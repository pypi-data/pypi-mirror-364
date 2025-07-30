#!/usr/bin/env python3
"""
Auto-publish management script for physionet-mcp.

This script helps manage the auto-publishing workflow by:
- Viewing recent published versions
- Controlling when auto-publishing happens
- Managing development vs stable versions
"""

import subprocess
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
import re


def run_command(cmd: str) -> tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def get_pypi_versions() -> List[str]:
    """Get available versions from PyPI."""
    print("🔍 Fetching versions from PyPI...")
    
    code, stdout, stderr = run_command("pip index versions physionetmcp")
    if code != 0:
        print(f"❌ Failed to get PyPI versions: {stderr}")
        return []
    
    # Parse versions from pip output
    versions = []
    for line in stdout.split('\n'):
        if 'Available versions:' in line:
            # Extract versions from line like "Available versions: 0.1.0, 0.1.0.dev123+abc1234"
            version_part = line.split('Available versions:')[1].strip()
            versions = [v.strip() for v in version_part.split(',') if v.strip()]
            break
    
    return versions


def get_git_info() -> Dict[str, Any]:
    """Get current git information."""
    info = {}
    
    # Get current branch
    code, stdout, _ = run_command("git branch --show-current")
    info['branch'] = stdout.strip() if code == 0 else 'unknown'
    
    # Get commit count
    code, stdout, _ = run_command("git rev-list --count HEAD")
    info['commit_count'] = int(stdout.strip()) if code == 0 else 0
    
    # Get short SHA
    code, stdout, _ = run_command("git rev-parse --short HEAD")
    info['short_sha'] = stdout.strip() if code == 0 else 'unknown'
    
    # Get current version from pyproject.toml
    try:
        pyproject_path = Path("pyproject.toml")
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            match = re.search(r'version\s*=\s*"([^"]+)",?$', content, re.MULTILINE)
            info['base_version'] = match.group(1) if match else 'unknown'
        else:
            info['base_version'] = 'unknown'
    except Exception:
        info['base_version'] = 'unknown'
    
    # Always use PEP 440-compliant version (no +sha)
    if info['base_version'] != 'unknown':
        info['next_auto_version'] = f"{info['base_version']}.dev{info['commit_count']}"
    else:
        info['next_auto_version'] = 'unknown'
    
    return info


def show_status():
    """Show current auto-publishing status."""
    print("📊 Auto-Publishing Status")
    print("=" * 50)
    
    # Git info
    git_info = get_git_info()
    print(f"🌿 Current branch: {git_info['branch']}")
    print(f"📝 Base version: {git_info['base_version']}")
    print(f"🔢 Commit count: {git_info['commit_count']}")
    print(f"🏷️  Short SHA: {git_info['short_sha']}")
    
    # Auto-publish prediction
    if git_info['branch'] in ['main', 'master']:
        print(f"🚀 Next auto-version: {git_info['next_auto_version']}")
        print(f"✅ Auto-publish: ENABLED (on push) [PyPI]" )
    else:
        print("❌ Auto-publish: DISABLED (not on main branch)")
    
    print()
    
    # PyPI versions
    versions = get_pypi_versions()
    if versions:
        print("📦 Recent PyPI versions:")
        dev_versions = [v for v in versions if '.dev' in v]
        stable_versions = [v for v in versions if '.dev' not in v]
        
        if stable_versions:
            print("  Stable versions:")
            for version in stable_versions[:5]:  # Show last 5
                print(f"    📌 {version}")
        
        if dev_versions:
            print("  Development versions:")
            for version in dev_versions[:3]:  # Show last 3
                print(f"    🧪 {version}")
    else:
        print("📦 No versions found on PyPI (or package not published yet)")


def simulate_version():
    """Simulate what version would be published."""
    print("🎯 Version Simulation")
    print("=" * 30)
    
    git_info = get_git_info()
    
    print(f"Current state:")
    print(f"  Branch: {git_info['branch']}")
    print(f"  Base version: {git_info['base_version']}")
    print(f"  Commits: {git_info['commit_count']}")
    print(f"  SHA: {git_info['short_sha']}")
    print()
    
    if git_info['branch'] in ['main', 'master']:
        print(f"🚀 Would publish: {git_info['next_auto_version']}")
        print(f"📥 Install command: pip install physionetmcp=={git_info['next_auto_version']}")
    else:
        print("❌ No auto-publish (not on main branch)")
        print("💡 Switch to main branch to enable auto-publishing")


def check_workflow_status():
    """Check if GitHub Actions workflow is enabled."""
    print("🔍 Checking GitHub Actions status...")
    
    workflow_file = Path(".github/workflows/publish.yaml")
    if not workflow_file.exists():
        print("❌ Workflow file not found: .github/workflows/publish.yaml")
        return
    
    print("✅ Workflow file exists")
    
    # Check if we're in a git repo with remote
    code, stdout, _ = run_command("git remote -v")
    if code != 0:
        print("❌ Not in a git repository")
        return
    
    if 'github.com' in stdout:
        print("✅ GitHub remote detected")
        print("💡 Push to main branch will trigger auto-publishing")
    else:
        print("⚠️  No GitHub remote found - workflow won't run")


def main():
    parser = argparse.ArgumentParser(description="Manage auto-publishing for physionet-mcp")
    subcommands = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subcommands.add_parser('status', help='Show current auto-publishing status')
    
    # Simulate command
    subcommands.add_parser('simulate', help='Simulate what version would be published')
    
    # Check command
    subcommands.add_parser('check', help='Check if workflow is properly configured')
    
    # Versions command
    subcommands.add_parser('versions', help='List available versions on PyPI')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🚀 PhysioNet MCP Auto-Publish Manager")
    print()
    
    if args.command == 'status':
        show_status()
    elif args.command == 'simulate':
        simulate_version()
    elif args.command == 'check':
        check_workflow_status()
    elif args.command == 'versions':
        versions = get_pypi_versions()
        if versions:
            print("📦 All available versions:")
            for version in versions:
                print(f"  {version}")
        else:
            print("No versions found")
    
    print()
    print("💡 Tips:")
    print("  - Push to main branch for auto-publishing")
    print("  - Use feature branches to avoid unwanted publishes")
    print("  - Tag commits for stable releases")


if __name__ == "__main__":
    main() 