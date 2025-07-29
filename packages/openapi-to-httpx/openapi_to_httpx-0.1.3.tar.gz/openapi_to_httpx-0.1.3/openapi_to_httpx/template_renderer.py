"""
Template renderer for generated files.
"""
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


class TemplateRenderer:
    """Renders Jinja2 templates for generated output files."""
    
    def __init__(self):
        template_dir = Path(__file__).parent / "templates" / "output"
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )
    
    def render_readme(self, context: dict[str, Any]) -> str:
        """Render README.md template."""
        template = self.env.get_template("README.md.j2")
        return template.render(**context)
    
    def render_init(self, context: dict[str, Any]) -> str:
        """Render __init__.py template."""
        template = self.env.get_template("__init__.py.j2")
        return template.render(**context)
    
    def render_models(self, context: dict[str, Any]) -> str:
        """Render models.py template."""
        template = self.env.get_template("models.py.j2")
        return template.render(**context)