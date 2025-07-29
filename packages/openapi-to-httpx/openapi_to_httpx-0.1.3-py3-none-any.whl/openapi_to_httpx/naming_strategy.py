"""
Method naming strategy for generating clean, idiomatic Python method names from OpenAPI paths.
"""
import inflection


class MethodNamingStrategy:
    """
    Generates clean method names from OpenAPI paths and HTTP methods.
    
    Examples:
        POST /api/v1/sessions/ -> post_sessions
        GET /api/v1/sessions/ -> get_sessions  
        GET /api/v1/sessions/{id} -> get_sessions_id
        PUT /api/v1/sessions/{id} -> put_sessions_id
        DELETE /api/v1/sessions/{id} -> delete_sessions_id
    """
    
    def __init__(self):
        self.used_names: set[str] = set()
        self.path_to_name: dict[tuple[str, str], str] = {}
        
    def generate_method_name(self, path: str, http_method: str, operation_id: str | None = None) -> str:
        """
        Generate a method name for an endpoint.
        
        Args:
            path: The URL path (e.g., "/api/v1/sessions/{id}")
            http_method: The HTTP method (e.g., "post", "get")
            operation_id: Optional operationId from OpenAPI spec
            
        Returns:
            A clean, snake_case method name
        """
        # If we've already generated a name for this path/method combo, return it
        cache_key = (path, http_method.lower())
        if cache_key in self.path_to_name:
            return self.path_to_name[cache_key]
        
        # If operationId is provided, always use it
        if operation_id:
            name = inflection.underscore(operation_id)
            if name not in self.used_names:
                self._register_name(cache_key, name)
                return name
        
        # Otherwise, generate a simple name from method + path
        name = self._generate_simple_name(path, http_method)
        
        # Handle name conflicts with numeric suffixes
        original_name = name
        suffix = 2
        while name in self.used_names:
            name = f"{original_name}_{suffix}"
            suffix += 1
        
        self._register_name(cache_key, name)
        return name
    
    def _register_name(self, cache_key: tuple[str, str], name: str):
        """Register a name as used."""
        self.used_names.add(name)
        self.path_to_name[cache_key] = name
    
    
    def _generate_simple_name(self, path: str, http_method: str) -> str:
        """Generate a simple method name by concatenating method + path segments."""
        # Split path into segments, replace slashes with underscores
        clean_path = path.strip('/')
        
        # Split into segments and clean them up
        if clean_path:
            segments = []
            for segment in clean_path.split('/'):
                if segment.startswith('{') and segment.endswith('}'):
                    # Keep parameter names but remove braces
                    param_name = segment[1:-1]  # Remove { }
                    segments.append(param_name)
                elif segment:
                    segments.append(segment)
        else:
            segments = ['root']
        
        # Build name: method + all path segments
        parts = [http_method.lower()] + segments
        name = '_'.join(parts)
        
        return inflection.underscore(name)
