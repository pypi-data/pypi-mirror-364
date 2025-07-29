"""
Generate client libraries for all test fixtures.
"""
import shutil
from pathlib import Path

from openapi_to_httpx.generator import generate_client_project


def generate_all_fixtures() -> list[Path]:
    """Generate client libraries for all test fixtures."""
    # Get paths
    tests_dir = Path(__file__).parent
    fixtures_dir = tests_dir / "fixtures"
    libraries_dir = fixtures_dir / "libraries"
    
    # Clean and recreate libraries directory
    if libraries_dir.exists():
        shutil.rmtree(libraries_dir)
    libraries_dir.mkdir(parents=True)
    
    # Find all OpenAPI specs in fixtures
    spec_files = list(fixtures_dir.glob("*.yaml")) + list(fixtures_dir.glob("*.json"))
    
    if not spec_files:
        raise RuntimeError("No OpenAPI spec files found in fixtures directory")
    
    generated_paths = []
    
    # Generate client for each spec
    for spec_file in spec_files:
        # Use spec filename (without extension) as package name
        package_name = spec_file.stem
        
        # Generate sync version
        sync_output_dir = libraries_dir / package_name
        try:
            generate_client_project(
                str(spec_file),
                sync_output_dir,
                client_name="APIClient",
                mode="sync"
            )
            generated_paths.append(sync_output_dir)
        except Exception as e:
            print(f"Failed to generate sync client for {spec_file.name}: {e}")
        
        # Generate async version
        async_output_dir = libraries_dir / f"{package_name}_async"
        try:
            generate_client_project(
                str(spec_file),
                async_output_dir,
                client_name="APIClient",
                mode="async"
            )
            generated_paths.append(async_output_dir)
        except Exception as e:
            print(f"Failed to generate async client for {spec_file.name}: {e}")
    
    # Create __init__.py to make it a proper package
    (libraries_dir / "__init__.py").touch()
    
    return generated_paths

def main():
    """CLI entry point for updating test fixtures."""
    generate_all_fixtures()
    
if __name__ == "__main__":
    main()
