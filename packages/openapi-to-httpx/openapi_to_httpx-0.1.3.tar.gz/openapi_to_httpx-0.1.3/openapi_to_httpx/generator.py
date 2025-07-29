"""
Client code generator that combines AST transformation with OpenAPI schemas.
"""
import ast
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .ast_transform.transformer import OpenAPITransformer
from .schema_parser import SchemaParser
from .template_renderer import TemplateRenderer


class ClientGenerator:
    """Generate Python client code from OpenAPI schemas."""
    
    def __init__(self, schema: dict[str, Any], client_name: str = "APIClient", mode: str = "sync"):
        self.schema = schema
        self.client_name = client_name
        self.mode = mode
        self.transformer = OpenAPITransformer(schema, client_name, mode)
        self.template_renderer = TemplateRenderer()
    
    def _get_template_ast(self) -> ast.Module:
        """Load and parse the appropriate client template."""
        if self.mode == "async":
            template_name = "async_client.py"
        else:
            template_name = "sync_client.py"
        template_path = Path(__file__).parent / "templates" / template_name
        template_code = template_path.read_text()
        return ast.parse(template_code)
    
    def _generate_init_file(self, package_name: str) -> str:
        """Generate __init__.py content."""
        # Get all model names from the transformer
        model_names = sorted(self.transformer.generated_models.keys())
        
        context = {
            'api_title': self.schema.get("info", {}).get("title", "API"),
            'client_name': self.client_name,
            'model_names': model_names,
        }
        return self.template_renderer.render_init(context)
    
    def _format_code(self, code: str) -> str:
        """Format generated code with ruff."""
        try:
            # Write code to a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            # Run ruff format and fix to remove unused imports
            try:
                # First fix imports and linting issues
                subprocess.run(
                    ['ruff', 'check', '--fix', '--select', 'F401,I', temp_path],
                    capture_output=True,
                    text=True,
                    check=False  # Don't raise on non-zero exit
                )
                
                # Then format the code
                subprocess.run(
                    ['ruff', 'format', temp_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Read the formatted code
                with open(temp_path, 'r') as f:
                    formatted_code = f.read()
                
                return formatted_code
            finally:
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)
                
        except Exception:
            # If ruff fails, return unformatted code
            return code
    
    def generate(self, output_dir: Path) -> None:
        """Generate the complete client package."""
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get and transform the template AST
        template_ast = self._get_template_ast()
        
        # Transform AST (this populates the models)
        transformed_ast = self.transformer.transform(template_ast)
        
        # Remove model classes from client since they're in models.py
        # Keep only non-model classes and functions
        filtered_body = []
        model_names = set(self.transformer.generated_models.keys())
        
        for node in transformed_ast.body:
            if isinstance(node, ast.ClassDef) and node.name in model_names:
                continue  # Skip model classes
            filtered_body.append(node)
        
        # Collect all model names used in the client
        used_models = set()
        
        def collect_model_names(node):
            """Recursively collect model names from AST nodes, including from type annotations."""
            if isinstance(node, ast.Name) and node.id in model_names:
                used_models.add(node.id)
            elif isinstance(node, ast.Subscript):
                # Handle types like Response[Pet], List[Pet], Optional[Pet], etc.
                collect_model_names(node.value)
                if isinstance(node.slice, ast.Name):
                    collect_model_names(node.slice)
                elif isinstance(node.slice, (ast.Tuple, ast.List)):
                    # Handle Union[Model1, Model2] or similar
                    for elt in node.slice.elts:
                        collect_model_names(elt)
                else:
                    # For other slice types, recursively check
                    collect_model_names(node.slice)
            elif isinstance(node, ast.Attribute):
                # Handle qualified names if needed
                collect_model_names(node.value)
            
        for node in ast.walk(transformed_ast):
            collect_model_names(node)
        
        # No need to handle typing imports - they're in the templates and black will clean up unused ones
        
        # Add import for models at the beginning after other imports
        # Sort for consistent ordering
        sorted_models = sorted(used_models)
        
        # Check if we need to add File to base_client imports
        if 'File' in self.transformer.imports_to_add:
            # Find the existing base_client import and add File to it
            for i, node in enumerate(filtered_body):
                if (isinstance(node, ast.ImportFrom) and 
                    node.module == 'base_client' and 
                    node.level == 1):
                    # Add File to the existing import
                    existing_names = [alias.name for alias in node.names]
                    if 'File' not in existing_names:
                        node.names.append(ast.alias(name='File', asname=None))
                    break
        
        # Only add import if there are models to import
        if sorted_models:
            import_models = ast.ImportFrom(
                module='models',
                names=[ast.alias(name=model, asname=None) for model in sorted_models],
                level=1  # Relative import
            )
        
            # Find the right position for the import
            # We need to place it after the last regular import, but before any code
            last_import_pos = None
            
            for i, node in enumerate(filtered_body):
                if isinstance(node, ast.ImportFrom) or isinstance(node, ast.Import):
                    last_import_pos = i
            
            if last_import_pos is not None:
                # Insert after the last import
                filtered_body.insert(last_import_pos + 1, import_models)
            else:
                # No imports found, check for module docstring
                if filtered_body and isinstance(filtered_body[0], ast.Expr) and isinstance(filtered_body[0].value, ast.Constant):
                    # Insert after docstring
                    filtered_body.insert(1, import_models)
                else:
                    # Insert at beginning
                    filtered_body.insert(0, import_models)
        transformed_ast.body = filtered_body
        
        # Generate client code
        client_code = ast.unparse(transformed_ast)
        client_code = self._format_code(client_code)
        
        # Write client file
        client_file = output_dir / "client.py"
        client_file.write_text(client_code)
        
        # Copy base_client.py
        base_client_path = Path(__file__).parent / "templates" / "base_client.py"
        base_client_code = base_client_path.read_text()
        base_client_code = self._format_code(base_client_code)
        base_client_file = output_dir / "base_client.py"
        base_client_file.write_text(base_client_code)
        
        # Generate models file (after transformation so models are populated)
        models_code = self._generate_models_file()
        models_file = output_dir / "models.py"
        models_file.write_text(models_code)
        
        # Generate __init__.py
        init_code = self._generate_init_file(output_dir.name)
        init_code = self._format_code(init_code)
        init_file = output_dir / "__init__.py"
        init_file.write_text(init_code)
        
        # Generate README
        readme_file = output_dir / "README.md"
        readme_file.write_text(self._generate_readme(output_dir.name))
    
    def _generate_models_file(self) -> str:
        """Generate a separate models file for better organization."""
        # Generate model code strings
        models_dict = {}
        for model_name, model_ast_node in self.transformer.generated_models.items():
            model_code = ast.unparse(model_ast_node)
            models_dict[model_name] = model_code.strip()
        
        # Separate enums from regular models
        enum_names = self.transformer.generated_enums if hasattr(self.transformer, 'generated_enums') else set()
        pydantic_models = [name for name in models_dict.keys() if name not in enum_names]
        
        context = {
            'models': models_dict,
            'pydantic_models': pydantic_models,
            'imports_to_add': self.transformer.imports_to_add
        }
        
        # Render the template
        models_code = self.template_renderer.render_models(context)
        
        # Format the entire file
        return self._format_code(models_code)
    
    def _generate_readme(self, package_name: str) -> str:
        """Generate README for the client."""
        context = {
            'api_title': self.schema.get("info", {}).get("title", "API"),
            'api_description': self.schema.get("info", {}).get("description", ""),
            'api_version': self.schema.get("info", {}).get("version", ""),
            'client_name': self.client_name,
            'package_name': package_name,
            'methods': sorted(self.transformer.generated_methods),
        }
        return self.template_renderer.render_readme(context)


def generate_client_project(
    schema_source: str,
    output_dir: Path,
    client_name: str = "APIClient",
    mode: str = "sync"
) -> None:
    """
    Generate a complete client project from an OpenAPI schema.
    
    Args:
        schema_source: Path to schema file or URL
        output_dir: Directory to output the generated client
        client_name: Name for the generated client class
        mode: Generate sync or async client
    """
    # Parse schema
    if schema_source.startswith(('http://', 'https://')):
        schema = SchemaParser.load_from_url(schema_source)
    else:
        schema = SchemaParser.load_from_file(Path(schema_source))
    
    # Validate schema
    SchemaParser.validate_schema(schema)
    
    # Generate client
    generator = ClientGenerator(schema, client_name, mode)
    generator.generate(output_dir)
    
    print(f"✅ Client generated successfully in {output_dir}")
    print(f"📦 Client class: {client_name}")