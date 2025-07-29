"""
OpenAPI schema parser and downloader.
"""
import json
from pathlib import Path
from typing import Any

import httpx
import yaml


class SchemaParser:
    """Parse and validate OpenAPI schemas."""
    
    @staticmethod
    def load_from_file(file_path: Path) -> dict[str, Any]:
        """Load OpenAPI schema from a file."""
        content = file_path.read_text()
        
        if file_path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(content)
        elif file_path.suffix == '.json':
            return json.loads(content)
        else:
            # Try to parse as JSON first, then YAML
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return yaml.safe_load(content)
    
    @staticmethod
    def load_from_url(url: str) -> dict[str, Any]:
        """Download and parse OpenAPI schema from URL."""
        response = httpx.get(url, follow_redirects=True)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '')
        
        if 'yaml' in content_type or url.endswith(('.yaml', '.yml')):
            return yaml.safe_load(response.text)
        else:
            return response.json()
    
    @staticmethod
    def validate_schema(schema: dict[str, Any]) -> bool:
        """Basic validation of OpenAPI schema."""
        # Check for required fields
        if 'openapi' not in schema:
            raise ValueError("Missing 'openapi' field in schema")
        
        if 'info' not in schema:
            raise ValueError("Missing 'info' field in schema")
        
        if 'paths' not in schema:
            raise ValueError("Missing 'paths' field in schema")
        
        return True