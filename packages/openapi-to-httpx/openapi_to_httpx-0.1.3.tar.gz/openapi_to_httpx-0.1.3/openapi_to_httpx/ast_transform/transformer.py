"""
AST transformer that injects OpenAPI-specific details into the ideal client template.
"""
import ast
from typing import Any

import inflection

from openapi_to_httpx.naming_strategy import MethodNamingStrategy


class OpenAPITransformer(ast.NodeTransformer):
    """
    Transforms the ideal client AST to inject OpenAPI-specific endpoints and models.
    """
    
    def __init__(self, openapi_spec: dict[str, Any], client_name: str = "APIClient", mode: str = "sync"):
        self.spec = openapi_spec
        self.client_name = client_name
        self.mode = mode  # 'sync' or 'async'
        self.base_url = self._extract_base_url()
        self.paths = self.spec.get('paths', {})
        self.components = self.spec.get('components', {})
        self.schemas = self.components.get('schemas', {})
        
        # Track generated methods and models
        self.generated_methods = []
        self.generated_models = {}
        self.generated_enums = set()  # Track which models are enums
        self.imports_to_add = set()
        
        # Initialize naming strategy
        self.naming_strategy = MethodNamingStrategy()
        
        # Reserved class names from base_client.py to avoid conflicts
        self.base_client_classes = {
            'Response', 'File', 'ApiError', 'ValidationError', 
            'AuthenticationError', 'NotFoundError', 'BaseClient'
        }
        
    def _extract_base_url(self) -> str:
        """Extract base URL from OpenAPI spec."""
        servers = self.spec.get('servers', [])
        if servers:
            return servers[0].get('url', '')
        return ''
    
    def _snake_case(self, name: str) -> str:
        """Convert camelCase or PascalCase to snake_case."""
        return inflection.underscore(name)
    
    def _pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        # Special handling for all-uppercase names
        if name.isupper() and len(name) > 1:
            # Try to intelligently split all-caps names
            # For example: FILEUPLOADRESPONSE -> FileUploadResponse
            # First, convert to lowercase and add underscores before common words
            import re
            result = name
            
            # Common word patterns to split on
            common_words = [
                'FILE', 'UPLOAD', 'DOWNLOAD', 'RESPONSE', 'REQUEST',
                'ERROR', 'SUCCESS', 'CREATE', 'UPDATE', 'DELETE',
                'GET', 'POST', 'PUT', 'PATCH', 'STATUS', 'TYPE',
                'USER', 'ADMIN', 'API', 'URL', 'ID', 'UUID',
                'JSON', 'XML', 'HTML', 'HTTP', 'HTTPS'
            ]
            
            # Sort by length descending to match longer words first
            common_words.sort(key=len, reverse=True)
            
            # Replace common words with underscored versions
            for word in common_words:
                if word in result:
                    # Add underscores around the word
                    result = result.replace(word, f'_{word}_')
            
            # Clean up multiple underscores and edge underscores
            result = re.sub(r'_+', '_', result)
            result = result.strip('_')
            
            # Now convert to PascalCase using inflection
            return inflection.camelize(result.lower())
        
        return inflection.camelize(name)
    
    def _python_safe_name(self, name: str) -> str:
        """Make a name Python-safe."""
        # Replace non-alphanumeric characters with underscores
        import keyword
        import re
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure it doesn't start with a number
        if name and name[0].isdigit():
            name = f'_{name}'
        # Handle Python keywords
        if keyword.iskeyword(name):
            name = f'{name}_'
        return name
    
    def _parse_type_annotation(self, type_str: str) -> ast.AST:
        """Parse a type string into an AST annotation."""
        parsed = ast.parse(type_str).body[0]
        if isinstance(parsed, ast.Expr):
            return parsed.value
        return parsed
    
    def _generate_response_parser(self, response_type: str, response_content_type: str = 'application/json') -> ast.Assign:
        """Generate code to parse response based on type."""
        if response_type == 'bytes':
            # For binary responses, use response.content
            return ast.Assign(
                targets=[ast.Name(id='data', ctx=ast.Store())],
                value=ast.Attribute(
                    value=ast.Name(id='response', ctx=ast.Load()),
                    attr='content',
                    ctx=ast.Load()
                )
            )
        elif response_type == 'str' and response_content_type.startswith('text/'):
            # For text responses, use response.text
            return ast.Assign(
                targets=[ast.Name(id='data', ctx=ast.Store())],
                value=ast.Attribute(
                    value=ast.Name(id='response', ctx=ast.Load()),
                    attr='text',
                    ctx=ast.Load()
                )
            )
        elif response_type == 'Any':
            # Just return the JSON
            return ast.Assign(
                targets=[ast.Name(id='data', ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id='response', ctx=ast.Load()),
                        attr='json',
                        ctx=ast.Load()
                    ),
                    args=[],
                    keywords=[]
                )
            )
        elif response_type.startswith('list['):
            # Extract the item type
            item_type = response_type[5:-1]  # Extract Pet from list[Pet]
            # Remove quotes if present (for forward references)
            item_type_unquoted = item_type.strip("'\"")
            return ast.Assign(
                targets=[ast.Name(id='data', ctx=ast.Store())],
                value=ast.ListComp(
                    elt=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=item_type_unquoted, ctx=ast.Load()),
                            attr='model_validate',
                            ctx=ast.Load()
                        ),
                        args=[ast.Name(id='item', ctx=ast.Load())],
                        keywords=[]
                    ),
                    generators=[
                        ast.comprehension(
                            target=ast.Name(id='item', ctx=ast.Store()),
                            iter=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id='response', ctx=ast.Load()),
                                    attr='json',
                                    ctx=ast.Load()
                                ),
                                args=[],
                                keywords=[]
                            ),
                            ifs=[],
                            is_async=0
                        )
                    ]
                )
            )
        else:
            # Check if it's a primitive type or dict
            if response_type in ['str', 'int', 'float', 'bool', 'dict[str, Any]']:
                # For primitives and dicts, just return the JSON
                return ast.Assign(
                    targets=[ast.Name(id='data', ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='response', ctx=ast.Load()),
                            attr='json',
                            ctx=ast.Load()
                        ),
                        args=[],
                        keywords=[]
                    )
                )
            else:
                # Single model response
                # Remove quotes if present (for forward references)
                response_type_unquoted = response_type.strip("'\"")
                return ast.Assign(
                    targets=[ast.Name(id='data', ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=response_type_unquoted, ctx=ast.Load()),
                            attr='model_validate',
                            ctx=ast.Load()
                        ),
                        args=[ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id='response', ctx=ast.Load()),
                                attr='json',
                                ctx=ast.Load()
                            ),
                            args=[],
                            keywords=[]
                        )],
                        keywords=[]
                    )
                )
    
    def _resolve_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Resolve a schema that might contain a $ref."""
        if '$ref' in schema:
            ref_name = schema['$ref'].split('/')[-1]
            if ref_name in self.schemas:
                return self.schemas[ref_name]
        return schema
    
    def _get_python_type(self, schema: dict[str, Any], for_model: str | None = None) -> str:
        """Convert OpenAPI schema to Python type hint.
        
        Args:
            schema: The schema to convert
            for_model: The model this type is being generated for (for cycle detection)
        """
        if '$ref' in schema:
            ref_name = schema['$ref'].split('/')[-1]
            
            # Check if the referenced schema is a polymorphic type (anyOf/oneOf/allOf)
            if ref_name in self.schemas:
                ref_schema = self.schemas[ref_name]
                if 'anyOf' in ref_schema or 'oneOf' in ref_schema or 'allOf' in ref_schema:
                    # For now, return Any for polymorphic types
                    return 'Any'
            
            # Use sanitized model name if we have a mapping
            if hasattr(self, 'model_name_map') and ref_name in self.model_name_map:
                safe_ref = self.model_name_map[ref_name]
            else:
                # Otherwise sanitize it directly
                safe_ref = self._sanitize_model_name(ref_name)
            
            # Track that we need to import this model
            self.imports_to_add.add(safe_ref)
            
            # Always return the direct reference without quotes
            # The AST will handle forward references properly
            return safe_ref
        
        type_mapping = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'list',
            'object': 'dict[str, Any]',
            'null': 'None'
        }
        
        # Handle anyOf/oneOf
        if 'anyOf' in schema:
            types = []
            for subschema in schema['anyOf']:
                subtype = self._get_python_type(subschema, for_model)
                if subtype not in types:  # Avoid duplicates
                    types.append(subtype)
            
            # Special case: if we have [type, null], simplify to type | None
            if len(types) == 2 and 'None' in types:
                other_type = next(t for t in types if t != 'None')
                return f'{other_type} | None'
            
            # If we already have type | None, don't add another | None
            if any('| None' in t for t in types):
                # Remove standalone None if we already have type | None
                types = [t for t in types if t != 'None']
            
            return ' | '.join(types) if types else 'Any'
        
        if 'oneOf' in schema:
            types = []
            for subschema in schema['oneOf']:
                subtype = self._get_python_type(subschema, for_model)
                if subtype not in types:  # Avoid duplicates
                    types.append(subtype)
            return ' | '.join(types) if types else 'Any'
        
        if 'allOf' in schema:
            # For allOf, we would need intersection types which Python doesn't support
            # For now, return Any
            return 'Any'
        
        schema_type = schema.get('type')
        if not schema_type:
            # No type specified, default to Any
            return 'Any'
        
        # Handle inline enums (not referenced, but defined inline)
        if schema_type == 'string' and 'enum' in schema:
            # For inline enums, we use Literal type (still need typing for this)
            enum_values = schema.get('enum', [])
            if enum_values:
                # Create a Literal type with all enum values
                literal_values = ', '.join(f'"{v}"' for v in enum_values)
                return f'Literal[{literal_values}]'
        
        if schema_type == 'array':
            items = schema.get('items', {})
            item_type = self._get_python_type(items, for_model)
            return f'list[{item_type}]'
        
        return type_mapping.get(schema_type, 'Any')
    
    def _sanitize_model_name(self, name: str) -> str:
        """Sanitize model name to be a valid Python identifier and convert to PascalCase."""
        # Replace dots with underscores
        name = name.replace('.', '_')
        # Replace other invalid characters
        name = name.replace('-', '_')
        # Convert to PascalCase
        name = self._pascal_case(name)
        # Ensure it starts with a letter or underscore
        if name and name[0].isdigit():
            name = f'Model{name}'
        
        # Check for conflicts with base_client classes
        if name in self.base_client_classes:
            name = f'{name}Schema'
            
        return name
    
    def _generate_model_class(self, name: str, schema: dict[str, Any]) -> ast.ClassDef:
        """Generate a Pydantic model class from OpenAPI schema."""
        # Sanitize the model name
        safe_name = self._sanitize_model_name(name)
        properties = schema.get('properties', {})
        required = set(schema.get('required', []))
        
        # Create class body
        body = []
        
        # Add docstring if description exists
        if 'description' in schema:
            body.append(ast.Expr(value=ast.Constant(value=schema['description'])))
        
        # Add fields
        for prop_name, prop_schema in properties.items():
            field_name = self._python_safe_name(prop_name)
            
            # Special handling for file fields
            field_format = prop_schema.get('format')
            if field_format == 'binary':
                # File upload field
                field_type = 'File'
                self.imports_to_add.add('File')
            elif prop_schema.get('type') == 'array' and prop_schema.get('items', {}).get('format') == 'binary':
                # Array of files
                field_type = 'list[File]'
                self.imports_to_add.add('File')
            else:
                field_type = self._get_python_type(prop_schema, safe_name)
            
            # Handle nullable/optional fields
            if prop_name not in required:
                # Don't add | None if the type already includes None
                if not field_type.endswith('| None'):
                    field_type = f'{field_type} | None'
                is_required = False
            else:
                is_required = True
            
            # Create the annotation
            annotation = self._parse_type_annotation(field_type)
            
            # Create the field assignment
            if 'description' in prop_schema:
                # Use Field with description
                if is_required:
                    # Required field with description
                    field_assign = ast.AnnAssign(
                        target=ast.Name(id=field_name, ctx=ast.Store()),
                        annotation=annotation,
                        value=ast.Call(
                            func=ast.Name(id='Field', ctx=ast.Load()),
                            args=[],
                            keywords=[
                                ast.keyword(
                                    arg='description',
                                    value=ast.Constant(value=prop_schema['description'])
                                )
                            ]
                        ),
                        simple=1
                    )
                else:
                    # Optional field with description
                    field_assign = ast.AnnAssign(
                        target=ast.Name(id=field_name, ctx=ast.Store()),
                        annotation=annotation,
                        value=ast.Call(
                            func=ast.Name(id='Field', ctx=ast.Load()),
                            args=[ast.Constant(value=None)],
                            keywords=[
                                ast.keyword(
                                    arg='description',
                                    value=ast.Constant(value=prop_schema['description'])
                                )
                            ]
                        ),
                        simple=1
                    )
            else:
                # No description
                if is_required:
                    # Required field without description - just annotation
                    field_assign = ast.AnnAssign(
                        target=ast.Name(id=field_name, ctx=ast.Store()),
                        annotation=annotation,
                        value=None,  # No default value for required fields
                        simple=1
                    )
                else:
                    # Optional field without description
                    field_assign = ast.AnnAssign(
                        target=ast.Name(id=field_name, ctx=ast.Store()),
                        annotation=annotation,
                        value=ast.Constant(value=None),
                        simple=1
                    )
            
            body.append(field_assign)
        
        # If no fields, add pass
        if not body:
            body.append(ast.Pass())
        
        # Create the class with sanitized name
        return ast.ClassDef(
            name=safe_name,
            bases=[ast.Name(id='BaseModel', ctx=ast.Load())],
            keywords=[],
            body=body,
            decorator_list=[]
        )
    
    def _generate_enum_class(self, name: str, schema: dict[str, Any]) -> ast.ClassDef:
        """Generate a Python Enum class from OpenAPI enum schema."""
        safe_name = self._sanitize_model_name(name)
        enum_values = schema.get('enum', [])
        
        # Create class body
        body = []
        
        # Add docstring if description exists
        if 'description' in schema:
            body.append(ast.Expr(value=ast.Constant(value=schema['description'])))
        
        # Add enum values
        for value in enum_values:
            # Create safe attribute name from the value
            attr_name = value.upper().replace('-', '_').replace(' ', '_')
            # Make sure it's a valid Python identifier
            if not attr_name[0].isalpha() and attr_name[0] != '_':
                attr_name = f'VALUE_{attr_name}'
            
            body.append(ast.Assign(
                targets=[ast.Name(id=attr_name, ctx=ast.Store())],
                value=ast.Constant(value=value)
            ))
        
        # If no values, add pass
        if not enum_values:
            body.append(ast.Pass())
        
        # Create the enum class
        return ast.ClassDef(
            name=safe_name,
            bases=[ast.Attribute(
                value=ast.Name(id='enum', ctx=ast.Load()),
                attr='Enum',
                ctx=ast.Load()
            )],
            keywords=[],
            body=body,
            decorator_list=[]
        )
    
    def _generate_method(self, path: str, method: str, operation: dict[str, Any]) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
        """Generate a method from an OpenAPI operation."""
        operation_id = operation.get('operationId')
        
        # Use the naming strategy to generate a clean method name
        method_name = self.naming_strategy.generate_method_name(path, method, operation_id)
        method_name = self._python_safe_name(method_name)
        
        # Parse parameters
        parameters = operation.get('parameters', [])
        path_params = []
        query_params = []
        header_params = []
        
        for param in parameters:
            param_name = self._snake_case(param['name'])
            param_name = self._python_safe_name(param_name)
            param_in = param.get('in')
            param_schema = param.get('schema', {})
            param_type = self._get_python_type(param_schema)
            required = param.get('required', False)
            
            if not required and '| None' not in param_type:
                param_type = f'{param_type} | None'
            
            param_info = {
                'name': param_name,
                'original_name': param['name'],
                'type': param_type,
                'required': required,
                'description': param.get('description', '')
            }
            
            if param_in == 'path':
                path_params.append(param_info)
            elif param_in == 'query':
                query_params.append(param_info)
            elif param_in == 'header':
                header_params.append(param_info)
        
        # Parse request body
        request_body = None
        request_body_type = None
        multipart_fields = None
        if 'requestBody' in operation:
            content = operation['requestBody'].get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                request_body_type = self._get_python_type(schema)
                request_body = {
                    'type': request_body_type,
                    'required': operation['requestBody'].get('required', True),
                    'content_type': 'application/json'
                }
            elif 'multipart/form-data' in content:
                schema = content['multipart/form-data'].get('schema', {})
                
                # Get or generate model name
                if '$ref' in schema:
                    # Schema is already defined in components
                    request_body_type = self._get_python_type(schema)
                else:
                    # Generate a model name from the operation ID
                    operation_id = operation.get('operationId', f'{method}_{path.replace("/", "_").replace("{", "").replace("}", "")}')
                    model_name = self._pascal_case(operation_id) + 'Form'
                    
                    # Ensure the model is generated
                    if model_name not in self.generated_models:
                        model_class = self._generate_model_class(model_name, schema)
                        self.generated_models[model_name] = model_class
                    
                    request_body_type = self._sanitize_model_name(model_name)
                
                # Resolve schema reference if present to get field details
                resolved_schema = self._resolve_schema(schema)
                properties = resolved_schema.get('properties', {})
                required_fields = set(resolved_schema.get('required', []))
                
                # Parse multipart form fields for request building
                multipart_fields = []
                for field_name, field_schema in properties.items():
                    field_type = field_schema.get('type')
                    field_format = field_schema.get('format')
                    
                    # Determine if this is a file field
                    is_file = field_format == 'binary' or field_type == 'string' and field_format == 'binary'
                    
                    # Determine if it's an array of files
                    is_file_array = field_type == 'array' and field_schema.get('items', {}).get('format') == 'binary'
                    
                    field_info = {
                        'name': field_name,
                        'python_name': self._python_safe_name(self._snake_case(field_name)),
                        'type': self._get_python_type(field_schema),
                        'required': field_name in required_fields,
                        'is_file': is_file,
                        'is_file_array': is_file_array,
                        'description': field_schema.get('description', ''),
                        'enum': field_schema.get('enum'),
                        'default': field_schema.get('default')
                    }
                    multipart_fields.append(field_info)
                
                request_body = {
                    'type': request_body_type,
                    'required': operation['requestBody'].get('required', True),
                    'content_type': 'multipart/form-data',
                    'fields': multipart_fields
                }
        
        # Parse response
        responses = operation.get('responses', {})
        success_response = responses.get('200') or responses.get('201') or responses.get('204')
        response_type = 'Any'
        response_content_type = 'application/json'  # default
        is_sse_endpoint = False
        
        if success_response:
            content = success_response.get('content', {})
            if 'text/event-stream' in content:
                # SSE response
                response_type = 'str'  # Each event is a string
                response_content_type = 'text/event-stream'
                is_sse_endpoint = True
            elif 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                response_type = self._get_python_type(schema)
                response_content_type = 'application/json'
            elif 'application/octet-stream' in content or 'application/zip' in content:
                # Binary response
                response_type = 'bytes'
                response_content_type = 'application/octet-stream'
            elif 'text/plain' in content or 'text/html' in content:
                # Text response
                response_type = 'str'
                response_content_type = 'text/plain'
            elif content:
                # Check if any content type is binary
                for content_type in content:
                    if ('octet-stream' in content_type or 'zip' in content_type or 
                        'pdf' in content_type or 'image/' in content_type or
                        content_type.startswith('application/') and 'json' not in content_type and 'xml' not in content_type):
                        response_type = 'bytes'
                        response_content_type = content_type
                        break
        
        # Build function arguments
        args = [ast.arg(arg='self', annotation=None)]
        kwonlyargs = []
        kw_defaults = []
        defaults = []
        
        # Add path parameters (always required)
        for param in path_params:
            args.append(ast.arg(
                arg=param['name'],
                annotation=self._parse_type_annotation(param['type'])
            ))
        
        # Add request body parameter
        if request_body:
            # Both JSON and multipart now use a data parameter with the model type
            if request_body['required']:
                args.append(ast.arg(
                    arg='data',
                    annotation=self._parse_type_annotation(request_body['type'])
                ))
            else:
                # Optional body - make it keyword-only
                kwonlyargs.append(ast.arg(
                    arg='data',
                    annotation=self._parse_type_annotation(f"{request_body['type']} | None")
                ))
                kw_defaults.append(ast.Constant(value=None))
        # Add query parameters as keyword-only
        for param in query_params:
            kwonlyargs.append(ast.arg(
                arg=param['name'],
                annotation=self._parse_type_annotation(param['type'])
            ))
            if not param['required']:
                kw_defaults.append(ast.Constant(value=None))
            else:
                kw_defaults.append(None)
        
        # Add header parameters as keyword-only
        for param in header_params:
            kwonlyargs.append(ast.arg(
                arg=param['name'],
                annotation=self._parse_type_annotation(param['type'])
            ))
            if not param['required']:
                kw_defaults.append(ast.Constant(value=None))
            else:
                kw_defaults.append(None)
        
        # Build function body
        body = []
        
        # Add docstring
        summary = operation.get('summary', '')
        description = operation.get('description', '')
        docstring = summary
        if description and description != summary:
            docstring = f"{summary}\n\n{description}" if summary else description
        
        if docstring:
            body.append(ast.Expr(value=ast.Constant(value=docstring)))
        
        # Build URL with path parameters
        url_parts = []
        current_part = ""
        i = 0
        while i < len(path):
            if path[i] == '{':
                # Found parameter
                if current_part:
                    url_parts.append(ast.Constant(value=current_part))
                    current_part = ""
                
                # Find closing brace
                j = path.find('}', i)
                if j != -1:
                    param_name = path[i+1:j]
                    param_name_safe = self._snake_case(param_name)
                    param_name_safe = self._python_safe_name(param_name_safe)
                    url_parts.append(ast.Name(id=param_name_safe, ctx=ast.Load()))
                    i = j + 1
                else:
                    current_part += path[i]
                    i += 1
            else:
                current_part += path[i]
                i += 1
        
        if current_part:
            url_parts.append(ast.Constant(value=current_part))
        
        # Create URL
        if len(url_parts) == 1:
            url_expr = url_parts[0]
        else:
            # Use f-string for URL construction
            url_expr = ast.JoinedStr(values=[
                ast.FormattedValue(value=part, conversion=-1) if isinstance(part, ast.Name) else ast.Constant(value=part.value)
                for part in url_parts
            ])
        
        # Build request parameters
        request_kwargs = []
        
        # Add query parameters
        if query_params:
            params_dict = []
            for param in query_params:
                params_dict.append(ast.keyword(
                    arg=param['original_name'],
                    value=ast.Name(id=param['name'], ctx=ast.Load())
                ))
            
            request_kwargs.append(ast.keyword(
                arg='params',
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id='self', ctx=ast.Load()),
                        attr='_filter_none_values',
                        ctx=ast.Load()
                    ),
                    args=[ast.Dict(
                        keys=[ast.Constant(value=kw.arg) for kw in params_dict],
                        values=[kw.value for kw in params_dict]
                    )],
                    keywords=[]
                )
            ))
        
        # Add headers
        if header_params:
            headers_dict = []
            for param in header_params:
                headers_dict.append(ast.keyword(
                    arg=param['original_name'],
                    value=ast.Name(id=param['name'], ctx=ast.Load())
                ))
            
            request_kwargs.append(ast.keyword(
                arg='headers',
                value=ast.Dict(
                    keys=[ast.Constant(value=kw.arg) for kw in headers_dict],
                    values=[kw.value for kw in headers_dict]
                )
            ))
        
        # Add request body
        if request_body:
            if request_body['content_type'] == 'multipart/form-data':
                # Extract files and data from the model
                files_list = []
                data_dict_items = []
                
                for field in multipart_fields:
                    # Access field from data model
                    field_access = ast.Attribute(
                        value=ast.Name(id='data', ctx=ast.Load()),
                        attr=field['python_name'],
                        ctx=ast.Load()
                    )
                    
                    if field['is_file']:
                        # Single file field - wrap in list if not None
                        # Call .to_tuple() on the File object
                        file_tuple = ast.Tuple(
                            elts=[
                                ast.Constant(value=field['name']),
                                ast.Call(
                                    func=ast.Attribute(
                                        value=field_access,
                                        attr='to_tuple',
                                        ctx=ast.Load()
                                    ),
                                    args=[],
                                    keywords=[]
                                )
                            ],
                            ctx=ast.Load()
                        )
                        
                        if not field['required']:
                            # Only include if not None
                            files_list.append(
                                ast.IfExp(
                                    test=ast.Compare(
                                        left=field_access,
                                        ops=[ast.IsNot()],
                                        comparators=[ast.Constant(value=None)]
                                    ),
                                    body=ast.List(elts=[file_tuple], ctx=ast.Load()),
                                    orelse=ast.List(elts=[], ctx=ast.Load())
                                )
                            )
                        else:
                            files_list.append(ast.List(elts=[file_tuple], ctx=ast.Load()))
                    elif field['is_file_array']:
                        # Multiple files - create list comprehension
                        # [(field_name, f.to_tuple()) for f in data.field]
                        list_comp = ast.ListComp(
                            elt=ast.Tuple(
                                elts=[
                                    ast.Constant(value=field['name']),
                                    ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Name(id='f', ctx=ast.Load()),
                                            attr='to_tuple',
                                            ctx=ast.Load()
                                        ),
                                        args=[],
                                        keywords=[]
                                    )
                                ],
                                ctx=ast.Load()
                            ),
                            generators=[
                                ast.comprehension(
                                    target=ast.Name(id='f', ctx=ast.Store()),
                                    iter=field_access,
                                    ifs=[],
                                    is_async=0
                                )
                            ]
                        )
                        files_list.append(list_comp)
                    else:
                        # Regular form field
                        # Convert value to string for form data
                        if field['type'] == 'bool':
                            # Convert boolean to lowercase string
                            field_value = ast.Call(
                                func=ast.Attribute(
                                    value=ast.Call(
                                        func=ast.Name(id='str', ctx=ast.Load()),
                                        args=[field_access],
                                        keywords=[]
                                    ),
                                    attr='lower',
                                    ctx=ast.Load()
                                ),
                                args=[],
                                keywords=[]
                            )
                        elif field['type'] not in ['str', 'Any'] and not field['type'].endswith('| None'):
                            # Convert non-string types to strings
                            field_value = ast.Call(
                                func=ast.Name(id='str', ctx=ast.Load()),
                                args=[field_access],
                                keywords=[]
                            )
                        else:
                            field_value = field_access
                        
                        # Add to data dict only if not None
                        if not field['required']:
                            data_dict_items.append(
                                ast.IfExp(
                                    test=ast.Compare(
                                        left=field_access,
                                        ops=[ast.IsNot()],
                                        comparators=[ast.Constant(value=None)]
                                    ),
                                    body=ast.Tuple(
                                        elts=[
                                            ast.Constant(value=field['name']),
                                            field_value
                                        ],
                                        ctx=ast.Load()
                                    ),
                                    orelse=ast.Constant(value=None)
                                )
                            )
                        else:
                            data_dict_items.append(
                                ast.Tuple(
                                    elts=[
                                        ast.Constant(value=field['name']),
                                        field_value
                                    ],
                                    ctx=ast.Load()
                                )
                            )
                
                # Build files parameter
                # For now, we'll keep it simple and concatenate file lists
                if files_list:
                    # If we have multiple file lists (from array fields), we need to concatenate them
                    if len(files_list) == 1:
                        files_value = files_list[0]
                    else:
                        # Concatenate multiple lists
                        files_value = files_list[0]
                        for file_item in files_list[1:]:
                            files_value = ast.BinOp(
                                left=files_value,
                                op=ast.Add(),
                                right=file_item
                            )
                    
                    request_kwargs.append(ast.keyword(
                        arg='files',
                        value=files_value
                    ))
                
                # Build data parameter for non-file fields
                if data_dict_items:
                    # Filter out None values from the list
                    filtered_items = ast.ListComp(
                        elt=ast.Name(id='item', ctx=ast.Load()),
                        generators=[
                            ast.comprehension(
                                target=ast.Name(id='item', ctx=ast.Store()),
                                iter=ast.List(elts=data_dict_items, ctx=ast.Load()),
                                ifs=[ast.Compare(
                                    left=ast.Name(id='item', ctx=ast.Load()),
                                    ops=[ast.IsNot()],
                                    comparators=[ast.Constant(value=None)]
                                )],
                                is_async=0
                            )
                        ]
                    )
                    
                    request_kwargs.append(ast.keyword(
                        arg='data',
                        value=ast.Call(
                            func=ast.Name(id='dict', ctx=ast.Load()),
                            args=[filtered_items],
                            keywords=[]
                        )
                    ))
            else:
                # JSON request body (existing code)
                request_body_schema = operation.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {})
                if '$ref' in request_body_schema:
                    # It's a model, use model_dump
                    request_kwargs.append(ast.keyword(
                        arg='json',
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id='data', ctx=ast.Load()),
                                attr='model_dump',
                                ctx=ast.Load()
                            ),
                            args=[],
                            keywords=[ast.keyword(arg='exclude_unset', value=ast.Constant(value=True))]
                        )
                    ))
                elif request_body_type.startswith('list[') and request_body_schema.get('type') == 'array' and '$ref' in request_body_schema.get('items', {}):
                    # It's a list of models, use list comprehension with model_dump
                    request_kwargs.append(ast.keyword(
                        arg='json',
                        value=ast.ListComp(
                            elt=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id='item', ctx=ast.Load()),
                                    attr='model_dump',
                                    ctx=ast.Load()
                                ),
                                args=[],
                                keywords=[ast.keyword(arg='exclude_unset', value=ast.Constant(value=True))]
                            ),
                            generators=[
                                ast.comprehension(
                                    target=ast.Name(id='item', ctx=ast.Store()),
                                    iter=ast.Name(id='data', ctx=ast.Load()),
                                    ifs=[],
                                    is_async=0
                                )
                            ]
                        )
                    ))
                else:
                    # It's a dict or primitive
                    request_kwargs.append(ast.keyword(
                        arg='json',
                        value=ast.Name(id='data', ctx=ast.Load())
                    ))
        
        # Get client directly
        body.append(ast.Assign(
            targets=[ast.Name(id='client', ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='self', ctx=ast.Load()),
                    attr='_get_client',
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[]
            )
        ))
        
        # Handle SSE endpoints differently - only for async mode
        if is_sse_endpoint and self.mode == 'async':
            # For SSE, use async context manager and stream
            # async with client.stream(...) as response:
            #     self._handle_response(response)
            #     async for line in response.aiter_lines():
            #         if line:
            #             yield line
            
            # Create the stream context manager
            stream_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='client', ctx=ast.Load()),
                    attr='stream',
                    ctx=ast.Load()
                ),
                args=[ast.Constant(value=method.upper()), url_expr],
                keywords=request_kwargs
            )
            
            # Create the async for loop body
            for_body = [
                ast.If(
                    test=ast.Name(id='line', ctx=ast.Load()),
                    body=[
                        ast.Expr(value=ast.Yield(value=ast.Name(id='line', ctx=ast.Load())))
                    ],
                    orelse=[]
                )
            ]
            
            # Create the async with body
            with_body = [
                # Handle streaming response errors (don't read response body)
                ast.Expr(value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id='self', ctx=ast.Load()),
                        attr='_handle_streaming_response',
                        ctx=ast.Load()
                    ),
                    args=[ast.Name(id='response', ctx=ast.Load())],
                    keywords=[]
                )),
                # Async for loop
                ast.AsyncFor(
                    target=ast.Name(id='line', ctx=ast.Store()),
                    iter=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='response', ctx=ast.Load()),
                            attr='aiter_lines',
                            ctx=ast.Load()
                        ),
                        args=[],
                        keywords=[]
                    ),
                    body=for_body,
                    orelse=[]
                )
            ]
            
            # Create the async with statement
            body.append(
                ast.AsyncWith(
                    items=[
                        ast.withitem(
                            context_expr=stream_call,
                            optional_vars=ast.Name(id='response', ctx=ast.Store())
                        )
                    ],
                    body=with_body
                )
            )
        else:
            # Regular request handling
            # Make the request
            if self.mode == 'async':
                body.append(ast.Assign(
                    targets=[ast.Name(id='response', ctx=ast.Store())],
                    value=ast.Await(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id='client', ctx=ast.Load()),
                                attr=method.lower(),
                                ctx=ast.Load()
                            ),
                            args=[url_expr],
                            keywords=request_kwargs
                        )
                    )
                ))
            else:
                body.append(ast.Assign(
                    targets=[ast.Name(id='response', ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='client', ctx=ast.Load()),
                            attr=method.lower(),
                            ctx=ast.Load()
                        ),
                        args=[url_expr],
                        keywords=request_kwargs
                    )
                ))
            
            # Handle response
            body.append(ast.Expr(value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='self', ctx=ast.Load()),
                    attr='_handle_response',
                    ctx=ast.Load()
                ),
                args=[ast.Name(id='response', ctx=ast.Load())],
                keywords=[]
            )))
            
            # Parse response
            body.append(ast.If(
                test=ast.Compare(
                    left=ast.Attribute(
                        value=ast.Name(id='response', ctx=ast.Load()),
                        attr='status_code',
                        ctx=ast.Load()
                    ),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=204)]
                ),
                body=[
                    ast.Return(value=ast.Call(
                        func=ast.Name(id='Response', ctx=ast.Load()),
                        args=[],
                        keywords=[
                            ast.keyword(arg='data', value=ast.Constant(value=None)),
                            ast.keyword(arg='status_code', value=ast.Attribute(
                                value=ast.Name(id='response', ctx=ast.Load()),
                                attr='status_code',
                                ctx=ast.Load()
                            )),
                            ast.keyword(arg='headers', value=ast.Call(
                                func=ast.Name(id='dict', ctx=ast.Load()),
                                args=[ast.Attribute(
                                    value=ast.Name(id='response', ctx=ast.Load()),
                                    attr='headers',
                                    ctx=ast.Load()
                                )],
                                keywords=[]
                            )),
                            ast.keyword(arg='response_time', value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Attribute(
                                        value=ast.Name(id='response', ctx=ast.Load()),
                                        attr='elapsed',
                                        ctx=ast.Load()
                                    ),
                                    attr='total_seconds',
                                    ctx=ast.Load()
                                ),
                                args=[],
                                keywords=[]
                            ))
                        ]
                    ))
                ],
                orelse=[
                    # Parse response based on type
                    self._generate_response_parser(response_type, response_content_type),
                    ast.Return(value=ast.Call(
                        func=ast.Name(id='Response', ctx=ast.Load()),
                        args=[],
                        keywords=[
                            ast.keyword(arg='data', value=ast.Name(id='data', ctx=ast.Load())),
                            ast.keyword(arg='status_code', value=ast.Attribute(
                                value=ast.Name(id='response', ctx=ast.Load()),
                                attr='status_code',
                                ctx=ast.Load()
                            )),
                            ast.keyword(arg='headers', value=ast.Call(
                                func=ast.Name(id='dict', ctx=ast.Load()),
                                args=[ast.Attribute(
                                    value=ast.Name(id='response', ctx=ast.Load()),
                                    attr='headers',
                                    ctx=ast.Load()
                                )],
                                keywords=[]
                            )),
                            ast.keyword(arg='response_time', value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Attribute(
                                        value=ast.Name(id='response', ctx=ast.Load()),
                                        attr='elapsed',
                                        ctx=ast.Load()
                                    ),
                                    attr='total_seconds',
                                    ctx=ast.Load()
                                ),
                                args=[],
                                keywords=[]
                            ))
                        ]
                    ))
                ]
            ))
        
        # Create the function
        if self.mode == 'async':
            # Determine return type based on whether it's SSE
            if is_sse_endpoint:
                return_type = 'AsyncIterator[str]'
                self.imports_to_add.add('AsyncIterator')
            else:
                return_type = f'Response[{response_type}]'
            
            return ast.AsyncFunctionDef(
                name=method_name,
                args=ast.arguments(
                    posonlyargs=[],
                    args=args,
                    kwonlyargs=kwonlyargs,
                    kw_defaults=kw_defaults,
                    defaults=defaults,
                    kwarg=None,
                    vararg=None
                ),
                body=body,
                decorator_list=[],
                returns=self._parse_type_annotation(return_type)
            )
        else:
            return ast.FunctionDef(
                name=method_name,
                args=ast.arguments(
                    posonlyargs=[],
                    args=args,
                    kwonlyargs=kwonlyargs,
                    kw_defaults=kw_defaults,
                    defaults=defaults,
                    kwarg=None,
                    vararg=None
                ),
                body=body,
                decorator_list=[],
                returns=self._parse_type_annotation(f'Response[{response_type}]')
            )
    
    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Transform the client class."""
        if node.name in ['BaseClient', 'SyncClient', 'AsyncClient']:
            # Rename to the desired client name
            node.name = self.client_name
            
            # Update class docstring with API info
            api_title = self.spec.get('info', {}).get('title', 'API')
            api_description = self.spec.get('info', {}).get('description', '')
            if api_description:
                new_docstring = f"{api_title} client.\n\n{api_description}"
            else:
                new_docstring = f"{api_title} client."
            
            # Replace the docstring if it exists, or add one
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                node.body[0].value = ast.Constant(value=new_docstring)
            else:
                # Insert docstring at the beginning
                docstring_node = ast.Expr(value=ast.Constant(value=new_docstring))
                node.body.insert(0, docstring_node)
            
            # Remove example methods (get_resource, list_resources, etc.)
            example_methods = {
                'get_resource', 'aget_resource', 'list_resources',
                'create_resource', 'update_resource', 'delete_resource',
                'batch_create', 'upload_file', 'upload_file_multipart', 
                'upload_multiple_files'
            }
            
            node.body = [
                item for item in node.body
                if not (isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name in example_methods)
            ]
            
            # Add generated methods from OpenAPI paths
            for path, path_item in self.paths.items():
                for method, operation in path_item.items():
                    if method in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
                        generated_method = self._generate_method(path, method, operation)
                        if generated_method:
                            node.body.append(generated_method)
                            self.generated_methods.append(generated_method.name)
        
        return node
    
    def _extract_model_dependencies(self, schema: dict[str, Any]) -> set[str]:
        """Extract dependencies from a model schema."""
        deps = set()
        
        def find_refs(obj: Any):
            if isinstance(obj, dict):
                if '$ref' in obj:
                    ref_path = obj['$ref']
                    if ref_path.startswith('#/components/schemas/'):
                        model_name = ref_path.split('/')[-1]
                        deps.add(model_name)
                else:
                    for value in obj.values():
                        find_refs(value)
            elif isinstance(obj, list):
                for item in obj:
                    find_refs(item)
        
        find_refs(schema)
        return deps
    
    def _topologically_sort_models(self) -> list[str]:
        """Sort models by dependencies using topological sort."""
        # Build dependency graph
        dep_graph = {}
        for schema_name, schema in self.schemas.items():
            if schema.get('type') == 'object' or 'properties' in schema:
                deps = self._extract_model_dependencies(schema)
                # Filter to only include deps that are actual schemas
                valid_deps = {d for d in deps if d in self.schemas}
                dep_graph[schema_name] = valid_deps
        
        # Use iterative approach to handle cycles
        # Start with all nodes
        remaining_nodes = set(dep_graph.keys())
        sorted_nodes = []
        
        # Keep removing nodes with no dependencies or only dependencies on already processed nodes
        while remaining_nodes:
            # Find nodes that can be processed now
            processable = []
            for node in remaining_nodes:
                deps = dep_graph.get(node, set())
                # Can process if all dependencies are already processed or not in our set
                if all(dep not in remaining_nodes or dep == node for dep in deps):
                    processable.append(node)
            
            if not processable:
                # We have a cycle - break it by choosing a node
                # Choose the node with the most dependencies (likely to be a "leaf" in the cycle)
                node = max(remaining_nodes, key=lambda n: len(dep_graph.get(n, set())))
                processable = [node]
            
            # Process these nodes
            for node in processable:
                sorted_nodes.append(node)
                remaining_nodes.remove(node)
        
        return sorted_nodes
    
    def transform(self, tree: ast.Module) -> ast.Module:
        """Transform the AST and generate models."""
        # Keep a mapping of original names to sanitized names
        self.model_name_map = {}
        
        # First, create the name mapping for all models and enums
        for schema_name in self.schemas:
            schema = self.schemas[schema_name]
            # Check if it's a model (object with properties) or an enum
            if (schema.get('type') == 'object' or 'properties' in schema or 
                (schema.get('type') == 'string' and 'enum' in schema)):
                safe_name = self._sanitize_model_name(schema_name)
                self.model_name_map[schema_name] = safe_name
        
        # Initialize forward refs as empty - we'll use quotes for all model references
        # to handle forward references properly
        self.forward_refs = {}
        
        # Get topologically sorted model names
        sorted_model_names = self._topologically_sort_models()
        
        # Generate enum classes first (they have no dependencies)
        enum_classes = []
        for schema_name, schema in self.schemas.items():
            if schema.get('type') == 'string' and 'enum' in schema:
                enum_class = self._generate_enum_class(schema_name, schema)
                enum_classes.append(enum_class)
                safe_name = self.model_name_map[schema_name]
                self.generated_models[safe_name] = enum_class
                self.generated_enums.add(safe_name)  # Mark as enum
        
        # Generate model classes in dependency order
        model_classes = []
        for schema_name in sorted_model_names:
            schema = self.schemas[schema_name]
            model_class = self._generate_model_class(schema_name, schema)
            model_classes.append(model_class)
            # Store with sanitized name for reference
            safe_name = self.model_name_map[schema_name]
            self.generated_models[safe_name] = model_class
        
        # Transform the tree
        transformed = self.visit(tree)
        
        # Insert model classes after imports
        import_end = 0
        for i, node in enumerate(transformed.body):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_end = i + 1
            else:
                break
        
        # Insert enums first, then models after imports
        for enum in enum_classes:
            transformed.body.insert(import_end, enum)
            import_end += 1
        
        for model in model_classes:
            transformed.body.insert(import_end, model)
            import_end += 1
        
        # Fix any missing imports
        ast.fix_missing_locations(transformed)
        
        return transformed