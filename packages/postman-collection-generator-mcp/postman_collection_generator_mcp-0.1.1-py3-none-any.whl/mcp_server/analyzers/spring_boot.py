"""
Spring Boot framework analyzer using pattern matching and simple parsing.
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..models.api import ApiCollection, ApiEndpoint, ApiParameter, HttpMethod, ParameterLocation
from .base import BaseAnalyzer
from rich.console import Console

console = Console(stderr=True)


class SpringBootAnalyzer(BaseAnalyzer):
    """Analyzer for Spring Boot applications."""
    
    def can_analyze(self) -> bool:
        """Check if this is a Spring Boot project."""
        # Check for Spring Boot indicators
        indicators = [
            "pom.xml",
            "build.gradle",
            "src/main/java/**/*Application.java",
            "src/main/java/**/*Controller.java",
            "**/controller/*.java",
            "**/controllers/*.java"
        ]
        
        for pattern in indicators:
            if self.find_files(pattern):
                return True
                
        # Check for Spring Boot content in files
        for file in self.find_files("**/*.java"):
            content = self.read_file(file)
            if any(annotation in content for annotation in [
                "@SpringBootApplication", "@RestController", "@Controller",
                "@RequestMapping", "@GetMapping", "@PostMapping"
            ]):
                return True
        
        return False
    
    def analyze(self) -> ApiCollection:
        """Extract endpoints from Spring Boot application."""
        collection = ApiCollection(
            name=self.repo_path.name,
            description="Spring Boot Application"
        )
        
        # Find all Java controller files
        controller_patterns = [
            "**/controller/*.java",
            "**/controllers/*.java", 
            "**/*Controller.java"
        ]
        
        controller_files = []
        for pattern in controller_patterns:
            controller_files.extend(self.find_files(pattern))
        
        # Remove duplicates
        controller_files = list(set(controller_files))
        
        for controller_file in controller_files:
            try:
                endpoints = self._analyze_controller(controller_file)
                collection.endpoints.extend(endpoints)
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to analyze {controller_file}: {e}[/yellow]")
        
        console.print(f"[green]Extracted {len(collection.endpoints)} endpoints from Spring Boot app[/green]")
        return collection
    
    def _analyze_controller(self, file_path: Path) -> List[ApiEndpoint]:
        """Analyze a single Java controller file."""
        content = self.read_file(file_path)
        if not content:
            return []
        
        endpoints = []
        
        # Extract class-level RequestMapping
        class_path = ""
        class_mapping_match = re.search(r'@RequestMapping\s*\(\s*["\']([^"\']*)["\']', content)
        if class_mapping_match:
            class_path = class_mapping_match.group(1)
        
        # Find all method mappings - improved patterns
        method_patterns = [
            # Mappings with paths in quotes
            (r'@GetMapping\s*\(\s*["\']([^"\']*)["\'].*?\)\s*\n\s*public\s+.*?\s+(\w+)\s*\(', 'GET'),
            (r'@PostMapping\s*\(\s*["\']([^"\']*)["\'].*?\)\s*\n\s*public\s+.*?\s+(\w+)\s*\(', 'POST'),
            (r'@PutMapping\s*\(\s*["\']([^"\']*)["\'].*?\)\s*\n\s*public\s+.*?\s+(\w+)\s*\(', 'PUT'),
            (r'@DeleteMapping\s*\(\s*["\']([^"\']*)["\'].*?\)\s*\n\s*public\s+.*?\s+(\w+)\s*\(', 'DELETE'),
            (r'@PatchMapping\s*\(\s*["\']([^"\']*)["\'].*?\)\s*\n\s*public\s+.*?\s+(\w+)\s*\(', 'PATCH'),
            # Mappings without parentheses (empty path)
            (r'@GetMapping\s*\n\s*public\s+.*?\s+(\w+)\s*\(', 'GET'),
            (r'@PostMapping\s*\n\s*public\s+.*?\s+(\w+)\s*\(', 'POST'),
            (r'@PutMapping\s*\n\s*public\s+.*?\s+(\w+)\s*\(', 'PUT'),
            (r'@DeleteMapping\s*\n\s*public\s+.*?\s+(\w+)\s*\(', 'DELETE'),
            (r'@PatchMapping\s*\n\s*public\s+.*?\s+(\w+)\s*\(', 'PATCH'),
        ]
        
        for pattern, http_method in method_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                # Determine if pattern has path or not
                if len(match.groups()) == 2:
                    # Pattern with path: @GetMapping("/path") 
                    path = match.group(1)
                    method_name = match.group(2)
                else:
                    # Pattern without path: @GetMapping
                    path = ""
                    method_name = match.group(1)
                
                method = http_method
                
                # Combine class path and method path
                if path:
                    full_path = (class_path.rstrip('/') + '/' + path.lstrip('/')).replace('//', '/')
                else:
                    full_path = class_path or "/"
                
                if not full_path.startswith('/'):
                    full_path = '/' + full_path
                
                endpoint = ApiEndpoint(
                    path=full_path,
                    method=HttpMethod(method),
                    name=method_name or f"{method} {full_path}",
                    source_file=str(file_path.relative_to(self.repo_path)),
                    line_number=content[:match.start()].count('\n') + 1
                )
                
                # Extract parameters
                self._extract_parameters(content, match, endpoint)
                
                endpoints.append(endpoint)
        
        # Also handle simple @RequestMapping without explicit method
        simple_mapping_pattern = r'@RequestMapping\s*\(\s*["\']([^"\']*)["\'][\s\S]*?public\s+\w+\s+(\w+)\s*\([^)]*\)'
        for match in re.finditer(simple_mapping_pattern, content, re.MULTILINE | re.DOTALL):
            path = match.group(1)
            method_name = match.group(2)
            
            full_path = (class_path.rstrip('/') + '/' + path.lstrip('/')).replace('//', '/')
            if not full_path.startswith('/'):
                full_path = '/' + full_path
            
            endpoint = ApiEndpoint(
                path=full_path,
                method=HttpMethod.GET,  # Default to GET
                name=method_name,
                source_file=str(file_path.relative_to(self.repo_path)),
                line_number=content[:match.start()].count('\n') + 1
            )
            
            self._extract_parameters(content, match, endpoint)
            endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_method_name_from_context(self, content: str, position: int) -> Optional[str]:
        """Extract method name from the context around a match."""
        # Look for method declaration after the annotation
        after_match = content[position:]
        method_match = re.search(r'public\s+\w+\s+(\w+)\s*\(', after_match)
        return method_match.group(1) if method_match else None
    
    def _extract_parameters(self, content: str, match: re.Match, endpoint: ApiEndpoint):
        """Extract parameters from method signature and annotations."""
        # Get the full method signature - look for more content
        method_start = match.start()
        method_end = self._find_method_end(content, match.end())
        method_content = content[method_start:method_end]
        
        # Debug output (commenting out to avoid MCP protocol interference)
        # console.print(f"[blue]Analyzing method: {endpoint.name}[/blue]")
        # console.print(f"[blue]Method content preview: {method_content[:200]}...[/blue]")
        
        # Extract path variables from URL and add them as parameters
        path_vars = re.findall(r'\{(\w+)\}', endpoint.path)
        for var in path_vars:
            param = ApiParameter(
                name=var,
                location=ParameterLocation.PATH,
                required=True,
                type="integer" if var == "id" else "string",
                example="1" if var == "id" else f"example_{var}"
            )
            endpoint.parameters.append(param)
            # console.print(f"[green]Found path variable: {var}[/green]")
        
        # More flexible parameter extraction patterns
        param_patterns = [
            # @RequestParam patterns (look for any parameters after @RequestParam)
            r'@RequestParam\s*(?:\([^)]*\))?\s+(?:\w+\s+)*?(\w+)\s+(\w+)',
            # @PathVariable patterns  
            r'@PathVariable\s*(?:\([^)]*\))?\s+(?:\w+\s+)*?(\w+)\s+(\w+)',
            # @RequestBody patterns (including @Valid @RequestBody)
            r'@(?:Valid\s+)?@?RequestBody\s*(?:\([^)]*\))?\s+(?:\w+\s+)*?(\w+)\s+(\w+)',
            # @RequestHeader patterns
            r'@RequestHeader\s*(?:\([^)]*\))?\s+(?:\w+\s+)*?(\w+)\s+(\w+)',
        ]
        
        # Look for @RequestBody with various validation patterns
        request_body_patterns = [
            # @RequestBody @Valid Type name
            r'@RequestBody\s+@Valid\s+(\w+)\s+(\w+)',
            # @RequestBody @Validated Type name  
            r'@RequestBody\s+@Validated\s+(\w+)\s+(\w+)',
            # @Valid @RequestBody Type name
            r'@Valid\s+@RequestBody\s*(?:\([^)]*\))?\s+(\w+)\s+(\w+)',
            # @Validated @RequestBody Type name
            r'@Validated\s+@RequestBody\s*(?:\([^)]*\))?\s+(\w+)\s+(\w+)',
            # @RequestBody Type name (no validation)
            r'@RequestBody\s*(?:\([^)]*\))?\s+(\w+)\s+(\w+)'
        ]
        
        request_body_matches = []
        for pattern in request_body_patterns:
            matches = list(re.finditer(pattern, method_content, re.IGNORECASE))
            request_body_matches.extend(matches)
            if matches:  # Stop at first successful pattern
                break
        
        for match in request_body_matches:
            param_type_raw = match.group(1)
            param_name = match.group(2)
            # console.print(f"[green]Found request body: {param_type_raw} {param_name}[/green]")
            
            # Create request body schema
            endpoint.request_body = {
                "type": param_type_raw,
                "example": self._generate_example_for_type(param_type_raw)
            }
        
        # Look for @RequestParam
        query_param_pattern = r'@RequestParam\s*(?:\([^)]*\))?\s+(?:\w+\s+)*?(\w+)\s+(\w+)'
        query_matches = list(re.finditer(query_param_pattern, method_content, re.IGNORECASE))
        
        for match in query_matches:
            param_type_raw = match.group(1)
            param_name = match.group(2)
            # console.print(f"[green]Found query param: {param_type_raw} {param_name}[/green]")
            
            param_type = self._convert_java_type(param_type_raw)
            param = ApiParameter(
                name=param_name,
                location=ParameterLocation.QUERY,
                required=False,
                type=param_type,
                example=self._generate_simple_example(param_type)
            )
            endpoint.parameters.append(param)
    
    def _find_method_end(self, content: str, start_pos: int) -> int:
        """Find the end of a method by counting braces."""
        brace_count = 0
        pos = start_pos
        in_method_body = False
        
        while pos < len(content):
            char = content[pos]
            if char == '{':
                brace_count += 1
                in_method_body = True
            elif char == '}':
                brace_count -= 1
                if in_method_body and brace_count == 0:
                    return pos + 1
            pos += 1
        
        # Fallback to a reasonable limit
        return min(start_pos + 2000, len(content))
    
    def _convert_java_type(self, java_type: str) -> str:
        """Convert Java types to standard parameter types."""
        type_mapping = {
            "String": "string",
            "Integer": "integer", 
            "int": "integer",
            "Long": "integer",
            "long": "integer", 
            "Boolean": "boolean",
            "boolean": "boolean",
            "Double": "number",
            "double": "number",
            "Float": "number", 
            "float": "number",
            "List": "array",
            "ArrayList": "array",
            "Set": "array",
            "Map": "object"
        }
        
        # Handle generic types like List<String>
        base_type = java_type.split('<')[0].split('.')[-1]  # Get last part after dot
        return type_mapping.get(base_type, "string")
    
    def _generate_example_for_type(self, java_type: str) -> dict:
        """Generate example request body based on Java type."""
        # This is a simplified example generator
        # In a real implementation, you might want to parse the actual DTO classes
        
        type_name = java_type.split('.')[-1]  # Get class name
        
        # Common DTO patterns
        if "Request" in type_name or "Create" in type_name or "Update" in type_name:
            if "Login" in type_name:
                return {
                    "username": "example@email.com",
                    "password": "password123"
                }
            elif "User" in type_name:
                example = {
                    "name": "John Doe",
                    "email": "john@example.com"
                }
                if "Create" in type_name:
                    example["password"] = "password123"
                return example
            elif "Game" in type_name:
                return {
                    "name": "Poker Game",
                    "buyIn": 100.0,
                    "gameType": "CASH"
                }
            elif "CreditTransfer" in type_name:
                return {
                    "amount": 1000.00,
                    "payeeName": "John Doe",
                    "payeeAccountNumber": "1234567890",
                    "narrative": "Payment description"
                }
            elif "ProxyResolution" in type_name:
                return {
                    "proxyId": "example@email.com",
                    "proxyType": "EMAIL",
                    "bankCode": "001"
                }
            elif "Token" in type_name:
                return {
                    "tokenType": "OTP",
                    "purpose": "transaction_verification"
                }
            elif "Transaction" in type_name:
                return {
                    "profileId": "12345",
                    "startDate": "2024-01-01",
                    "endDate": "2024-01-31"
                }
            else:
                return {
                    "example": f"Replace with actual {type_name} structure"
                }
        
        return {"data": f"Example {type_name}"}
    
    def _generate_simple_example(self, param_type: str) -> str:
        """Generate simple examples for parameters."""
        examples = {
            "string": "example",
            "integer": "1",
            "number": "1.0", 
            "boolean": "true",
            "array": "value1,value2"
        }
        return examples.get(param_type, "example")