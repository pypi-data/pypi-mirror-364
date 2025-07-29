"""
CLI interface for openapi-to-httpx.
"""
import sys
from pathlib import Path

import click

from .generator import generate_client_project


@click.command()
@click.argument('schema', type=str, required=True)
@click.option(
    '-o', '--output',
    type=click.Path(path_type=Path),
    default='./generated_client',
    help='Output directory for generated client'
)
@click.option(
    '-n', '--name',
    default='APIClient',
    help='Name for the generated client class'
)
@click.option(
    '--mode',
    type=click.Choice(['sync', 'async']),
    default='async',
    help='Generate sync or async client (default: async)'
)
def main(schema: str, output: Path, name: str, mode: str) -> None:
    """
    Generate a Python HTTP client from an OpenAPI schema.
    
    SCHEMA can be a file path or URL to an OpenAPI schema.
    
    Examples:
        
        # Generate from a local file
        openapi-to-httpx ./api-schema.yaml
        
        # Generate from a URL
        openapi-to-httpx https://api.example.com/openapi.json
        
        # Specify output directory and client name
        openapi-to-httpx schema.yaml -o ./my_client -n MyAPIClient
    """
    try:
        # Generate from provided schema
        click.echo(f"📥 Loading schema from {schema}...")
        generate_client_project(schema, output, name, mode)
            
        # Show next steps
        click.echo("\n🚀 Next steps:")
        click.echo(f"   cd {output}")
        click.echo("   pip install httpx pydantic")
        click.echo("   # Start using your generated client!")
        
    except FileNotFoundError as e:
        click.echo(f"❌ Error: Schema file not found: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"❌ Error: Invalid schema: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()