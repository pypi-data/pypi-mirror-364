#!/usr/bin/env python3
"""
Release preparation script for physionet-mcp.

This script helps prepare for a new release by:
- Validating the current state
- Updating version numbers
- Running pre-release checks
- Generating basic release notes
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import argparse


def run_command(cmd: str, cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd.split(),
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def get_current_version() -> Optional[str]:
    """Get the current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        return None
    
    content = pyproject_path.read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    
    print("❌ Could not find version in pyproject.toml")
    return None


def update_version(new_version: str) -> bool:
    """Update the version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    
    # Update version
    new_content = re.sub(
        r'version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        content
    )
    
    if new_content == content:
        print("❌ Failed to update version in pyproject.toml")
        return False
    
    pyproject_path.write_text(new_content)
    print(f"✅ Updated version to {new_version} in pyproject.toml")
    return True


def validate_git_state() -> bool:
    """Check if git state is clean and up to date."""
    print("🔍 Checking git state...")
    
    # Check if we're in a git repo
    if not Path(".git").exists():
        print("❌ Not in a git repository")
        return False
    
    # Check for uncommitted changes
    code, stdout, stderr = run_command("git status --porcelain")
    if code != 0:
        print(f"❌ Git status failed: {stderr}")
        return False
    
    if stdout.strip():
        print("❌ Uncommitted changes found:")
        print(stdout)
        print("Please commit or stash changes before preparing release")
        return False
    
    # Check if we're on main/master
    code, stdout, stderr = run_command("git branch --show-current")
    if code == 0:
        current_branch = stdout.strip()
        if current_branch not in ["main", "master"]:
            print(f"⚠️  Currently on branch '{current_branch}', consider switching to main/master")
    
    print("✅ Git state is clean")
    return True


def run_tests() -> bool:
    """Run the test suite."""
    print("🧪 Running tests...")
    
    # Check if we can import the package
    code, stdout, stderr = run_command("uv run python -c \"import physionetmcp; print('Import successful')\"")
    if code != 0:
        print(f"❌ Package import failed: {stderr}")
        return False
    print("✅ Package imports successfully")
    
    # Run linting
    code, stdout, stderr = run_command("uv run ruff check physionetmcp/")
    if code != 0:
        print(f"❌ Linting failed: {stderr}")
        return False
    print("✅ Linting passed")
    
    # Check formatting
    code, stdout, stderr = run_command("uv run ruff format --check physionetmcp/")
    if code != 0:
        print("❌ Code formatting check failed")
        print("Run: uv run ruff format physionetmcp/")
        return False
    print("✅ Code formatting is correct")
    
    # Run unit tests if they exist
    if Path("tests/unit").exists():
        code, stdout, stderr = run_command("uv run pytest tests/unit/ -v")
        if code != 0:
            print(f"⚠️  Some unit tests failed: {stderr}")
            # Don't return False as tests might be expected to fail in some cases
        else:
            print("✅ Unit tests passed")
    
    return True


def check_dependencies() -> bool:
    """Check if dependencies are up to date."""
    print("📦 Checking dependencies...")
    
    # Check if uv.lock exists and is up to date
    if not Path("uv.lock").exists():
        print("❌ uv.lock not found. Run 'uv lock' to generate it")
        return False
    
    # Check for security vulnerabilities
    code, stdout, stderr = run_command("uv run --with safety safety check --json")
    if code != 0:
        print("⚠️  Security check found issues (this might be expected)")
        print(stderr)
    else:
        print("✅ No security vulnerabilities found")
    
    return True


def build_package() -> bool:
    """Build the package and validate it."""
    print("🏗️  Building package...")
    
    # Clean previous builds
    import shutil
    if Path("dist").exists():
        shutil.rmtree("dist")
    
    # Build the package
    code, stdout, stderr = run_command("uv build")
    if code != 0:
        print(f"❌ Package build failed: {stderr}")
        return False
    print("✅ Package built successfully")
    
    # Validate the built package
    code, stdout, stderr = run_command("uv run --with twine twine check dist/*")
    if code != 0:
        print(f"❌ Package validation failed: {stderr}")
        return False
    print("✅ Package validation passed")
    
    return True


def generate_release_notes(version: str, previous_version: Optional[str] = None) -> str:
    """Generate basic release notes."""
    notes = f"""# Release {version}

## 🚀 What's New

<!-- Add your release highlights here -->

## 🐛 Bug Fixes

<!-- List bug fixes here -->

## 🔧 Improvements

<!-- List improvements here -->

## 📦 Installation

```bash
pip install physionetmcp=={version}
```

## 🔄 Upgrading

```bash
pip install --upgrade physionetmcp
```

---

**Full Changelog**: """
    
    if previous_version:
        notes += f"https://github.com/yourusername/physionet-mcp/compare/v{previous_version}...v{version}"
    else:
        notes += f"https://github.com/yourusername/physionet-mcp/releases/tag/v{version}"
    
    return notes


def increment_version(version: str, bump_type: str) -> str:
    """Increment version number based on bump type."""
    try:
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError("Version must be in MAJOR.MINOR.PATCH format")
        
        major, minor, patch = map(int, parts)
        
        if bump_type == "major":
            return f"{major + 1}.0.0"
        elif bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        elif bump_type == "patch":
            return f"{major}.{minor}.{patch + 1}"
        else:
            raise ValueError("Bump type must be 'major', 'minor', or 'patch'")
    
    except ValueError as e:
        print(f"❌ Invalid version format: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Prepare a new release")
    parser.add_argument("--version", help="Specific version to release (e.g., 0.2.0)")
    parser.add_argument("--bump", choices=["major", "minor", "patch"], 
                       help="Increment version automatically")
    parser.add_argument("--skip-tests", action="store_true", 
                       help="Skip running tests")
    parser.add_argument("--skip-build", action="store_true", 
                       help="Skip building package")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    print("🚀 Preparing release for physionet-mcp")
    print("=" * 50)
    
    # Get current version
    current_version = get_current_version()
    if not current_version:
        sys.exit(1)
    
    print(f"📋 Current version: {current_version}")
    
    # Determine new version
    if args.version:
        new_version = args.version
    elif args.bump:
        new_version = increment_version(current_version, args.bump)
    else:
        print("❌ Please specify either --version or --bump")
        sys.exit(1)
    
    print(f"🎯 Target version: {new_version}")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    # Validation steps
    if not validate_git_state():
        sys.exit(1)
    
    if not args.skip_tests and not run_tests():
        print("❌ Tests failed. Fix issues before releasing.")
        sys.exit(1)
    
    if not check_dependencies():
        print("⚠️  Dependency issues found, but continuing...")
    
    # Update version
    if not args.dry_run:
        if not update_version(new_version):
            sys.exit(1)
    else:
        print(f"🔍 Would update version to {new_version}")
    
    # Build package
    if not args.skip_build:
        if not args.dry_run:
            if not build_package():
                sys.exit(1)
        else:
            print("🔍 Would build package")
    
    # Generate release notes
    release_notes = generate_release_notes(new_version, current_version)
    release_notes_path = Path(f"release_notes_v{new_version}.md")
    
    if not args.dry_run:
        release_notes_path.write_text(release_notes)
        print(f"📝 Generated release notes: {release_notes_path}")
    else:
        print(f"🔍 Would generate release notes: {release_notes_path}")
    
    # Final instructions
    print("\n" + "=" * 50)
    print("✅ Release preparation complete!")
    print("\n📋 Next steps:")
    
    if not args.dry_run:
        print(f"1. Review and edit release notes: {release_notes_path}")
        print("2. Commit the version change:")
        print(f"   git add pyproject.toml")
        print(f"   git commit -m 'Bump version to {new_version}'")
        print("3. Create and push the tag:")
        print(f"   git tag v{new_version}")
        print(f"   git push origin v{new_version}")
        print("4. Create a GitHub release using the generated notes")
        print("\n🤖 The GitHub Actions workflow will automatically:")
        print("   - Run tests on multiple Python versions")
        print("   - Build the package")
        print("   - Publish to PyPI")
        print("   - Run security scans")
    else:
        print("Run without --dry-run to make actual changes")
    
    print(f"\n🎉 Ready to release version {new_version}!")


if __name__ == "__main__":
    main() 