#!/usr/bin/env python3
"""
Version bump script for CalcsLive Plug for Inventor.

Usage:
    python scripts/bump_version.py [patch|minor|major]

Examples:
    python scripts/bump_version.py patch   # 1.1.1 -> 1.1.2
    python scripts/bump_version.py minor   # 1.1.1 -> 1.2.0
    python scripts/bump_version.py major   # 1.1.1 -> 2.0.0
"""

import sys
import toml
from pathlib import Path


def bump_version(version: str, bump_type: str) -> str:
    """
    Bump semantic version number.

    Args:
        version: Current version string (e.g., "1.1.1")
        bump_type: Type of bump ("major", "minor", or "patch")

    Returns:
        New version string
    """
    major, minor, patch = map(int, version.split('.'))

    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}. Use 'major', 'minor', or 'patch'.")

    return f"{major}.{minor}.{patch}"


def update_pyproject_version(new_version: str):
    """Update version in pyproject.toml"""
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    data = toml.load(pyproject_path)
    old_version = data["project"]["version"]
    data["project"]["version"] = new_version

    with open(pyproject_path, "w") as f:
        toml.dump(data, f)

    print(f"✓ Updated pyproject.toml: {old_version} -> {new_version}")
    return old_version


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py [patch|minor|major]")
        sys.exit(1)

    bump_type = sys.argv[1].lower()

    if bump_type not in ['patch', 'minor', 'major']:
        print(f"Error: Invalid bump type '{bump_type}'")
        print("Use: patch, minor, or major")
        sys.exit(1)

    try:
        # Read current version
        data = toml.load("pyproject.toml")
        current_version = data["project"]["version"]

        # Calculate new version
        new_version = bump_version(current_version, bump_type)

        # Update files
        old_version = update_pyproject_version(new_version)

        print(f"\n🎉 Version bumped successfully!")
        print(f"   {old_version} -> {new_version} ({bump_type})")
        print(f"\nNext steps:")
        print(f"   1. Review changes: git diff")
        print(f"   2. Commit: git add . && git commit -m 'chore: bump version to {new_version}'")
        print(f"   3. Push: git push origin main")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()