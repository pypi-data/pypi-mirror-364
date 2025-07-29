#!/usr/bin/env python3
"""
Script to bump the version in pyproject.toml based on a git tag.
Usage: python scripts/bump_version.py <version>
"""

import re
import sys
from pathlib import Path


def update_version_in_pyproject(new_version: str, pyproject_path: Path = Path("pyproject.toml")) -> None:
    """Update the version field in pyproject.toml with the new version."""
    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")
    
    # Read the current content
    content = pyproject_path.read_text()
    
    # Pattern to match version = "..." line
    version_pattern = r'^version\s*=\s*"[^"]*"'
    replacement = f'version = "{new_version}"'
    
    # Replace the version line
    new_content = re.sub(version_pattern, replacement, content, flags=re.MULTILINE)
    
    if new_content == content:
        raise ValueError("Could not find version field in pyproject.toml")
    
    # Write back the updated content
    pyproject_path.write_text(new_content)
    print(f"✅ Updated version to {new_version} in {pyproject_path}")


def validate_version(version: str) -> str:
    """Validate and clean the version string."""
    # Remove 'v' prefix if present
    if version.startswith('v'):
        version = version[1:]
    
    # Basic semantic version validation
    if not re.match(r'^\d+\.\d+\.\d+(?:[.-].*)?$', version):
        raise ValueError(f"Invalid version format: {version}. Expected format: X.Y.Z")
    
    return version


def main() -> None:
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py <version>")
        print("Example: python scripts/bump_version.py v1.2.3")
        sys.exit(1)
    
    raw_version = sys.argv[1]
    
    try:
        clean_version = validate_version(raw_version)
        update_version_in_pyproject(clean_version)
        print(f"🎉 Successfully updated version to {clean_version}")
    except (ValueError, FileNotFoundError) as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 