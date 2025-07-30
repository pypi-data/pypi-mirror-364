# Publishing Guide

This document explains how to publish the `physionet-mcp` package to PyPI using the automated GitHub Actions workflow.

## 🚀 Publishing Methods

### 1. Automatic Publishing on Every Push (New!) 🎯

**The easiest way!** Every time you push to the `main` branch, a new version is automatically published to PyPI.

**How it works:**
- **Auto-versioning**: Generates development versions like `0.1.0.dev123+abc1234`
- **Unique versions**: Uses commit count + git SHA for uniqueness
- **No conflicts**: Never overwrites existing PyPI versions
- **Instant publishing**: Available on PyPI within minutes of your push

**Example workflow:**
```bash
# Make your changes
git add .
git commit -m "Add new feature"
git push origin main

# 🎉 Automatically published as: 0.1.0.dev456+def5678
# Available at: pip install physionetmcp==0.1.0.dev456+def5678
```

**Version format:** `{base_version}.dev{commit_count}+{git_sha}`
- `0.1.0` - Base version from pyproject.toml
- `.dev456` - Development version with commit count
- `+def5678` - Git commit SHA for uniqueness

### 2. Automatic Publishing via Release (Recommended for Stable Versions)

The easiest way to publish is by creating a GitHub release:

1. **Prepare for release:**
   ```bash
   # Update version in pyproject.toml
   # Update CHANGELOG.md (if you have one)
   # Commit and push changes
   git add pyproject.toml
   git commit -m "Bump version to 0.2.0"
   git push origin main
   ```

2. **Create and push a tag:**
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

3. **Create a GitHub Release:**
   - Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Choose the tag you just created (v0.2.0)
   - Fill in the release title and description
   - Click "Publish release"

4. **Automatic publishing:**
   - The workflow will automatically trigger
   - Run tests across Python 3.10, 3.11, and 3.12
   - Build the package
   - Publish to PyPI
   - Run security scans

### 2. Publishing via Git Tags

You can also publish by just pushing a version tag:

```bash
# Tag the current commit
git tag v0.2.0
git push origin v0.2.0
```

**Tag naming conventions:**
- `v0.2.0` → Publishes to PyPI
- `v0.2.0-beta.1` → Publishes to Test PyPI (pre-release)
- `v0.2.0-alpha.1` → Publishes to Test PyPI (pre-release)

### 3. Manual Testing

To test the workflow without publishing:

1. Go to the "Actions" tab in your GitHub repository
2. Click on "Publish to PyPI" workflow
3. Click "Run workflow"
4. Check "Publish to Test PyPI instead of PyPI"
5. Click "Run workflow"

## 🔧 Setup Requirements

### 1. PyPI Trusted Publishing (Recommended)

The workflow uses PyPI's trusted publishing feature for secure authentication:

1. **Configure PyPI:**
   - Go to https://pypi.org/manage/account/publishing/
   - Add a new trusted publisher:
     - Owner: `yourusername`
     - Repository: `physionet-mcp`
     - Workflow: `publish.yaml`
     - Environment: `pypi`

2. **Configure Test PyPI (optional):**
   - Go to https://test.pypi.org/manage/account/publishing/
   - Add the same configuration with environment: `test-pypi`

### 2. GitHub Environments

Create GitHub environments for additional security:

1. Go to your repository → Settings → Environments
2. Create environment: `pypi`
3. Create environment: `test-pypi`
4. (Optional) Add protection rules like required reviewers

## 📋 Pre-Release Checklist

Before publishing a new release:

- [ ] Update version in `pyproject.toml`
- [ ] Update `README.md` if needed
- [ ] Run tests locally: `uv run pytest`
- [ ] Run linting: `uv run ruff check physionetmcp/`
- [ ] Test package import: `uv run python -c "import physionetmcp"`
- [ ] Update dependencies if needed
- [ ] Test with different Python versions if possible

## 🔍 Workflow Features

The publish workflow includes:

### ✅ Quality Checks
- **Multi-Python Testing:** Tests on Python 3.10, 3.11, and 3.12
- **Linting:** Uses `ruff` for code quality checks
- **Type Checking:** Uses `mypy` for type safety
- **Package Validation:** Validates built packages with `twine`

### 🛡️ Security
- **Trusted Publishing:** No need to manage PyPI tokens
- **Security Scanning:** Runs `bandit` and `safety` checks
- **Environment Protection:** Uses GitHub environments for access control

### 📦 Publishing Logic
- **Auto-publish (Development):** Every push to `main` → development version to PyPI
- **Production PyPI:** Triggered by releases or stable version tags (v1.0.0)
- **Test PyPI:** Triggered by pre-release tags (v1.0.0-beta.1) or manual dispatch
- **Smart Skipping:** Skips auto-publish for tagged commits (avoids duplicates)
- **Artifact Management:** Builds are cached and shared between jobs

## 🔧 Managing Auto-Published Versions

### Using Development Versions

```bash
# Install latest development version
pip install physionetmcp --pre

# Install specific development version
pip install physionetmcp==0.1.0.dev123+abc1234

# Find available versions
pip index versions physionetmcp
```

### Controlling Auto-Publishing

```bash
# Disable auto-publish for a specific push (commit to feature branch first)
git checkout -b feature-branch
git add .
git commit -m "Work in progress"
git push origin feature-branch
# Then merge via PR when ready

# Force a specific version (via manual workflow)
# Go to Actions → "Publish to PyPI" → "Run workflow"
# Set "Force specific version" to desired version
```

### Git Workflow Best Practices

```bash
# For development work
git checkout -b feature/new-feature
# ... make changes ...
git push origin feature/new-feature
# → No auto-publish (not main branch)

# When ready to publish
git checkout main
git merge feature/new-feature
git push origin main  
# → Auto-publishes development version

# For stable releases
git tag v0.2.0
git push origin v0.2.0
# → Publishes stable version, skips auto-publish
```

## 🐛 Troubleshooting

### Common Issues

1. **"Package already exists"**
   - You cannot overwrite existing versions on PyPI
   - Increment the version number in `pyproject.toml`

2. **"Trusted publishing not configured"**
   - Set up trusted publishing on PyPI (see setup section)
   - Or configure `PYPI_API_TOKEN` secret (legacy method)

3. **Tests failing**
   - Check the Actions logs for specific test failures
   - Fix issues and push new commits before tagging

4. **Permission denied**
   - Ensure GitHub environments are configured correctly
   - Check that the workflow has `id-token: write` permissions

5. **"Failed to spawn: ruff" or similar linting errors**
   - The workflow uses `uv run --with TOOL` to install tools on-demand
   - Ensure your code passes linting locally: `uv run --with ruff ruff check physionetmcp/`
   - Auto-fix issues: `uv run --with ruff ruff check physionetmcp/ --fix`
   - Format code: `uv run --with ruff ruff format physionetmcp/`

### Debugging

- Check the "Actions" tab for detailed logs
- Security scan reports are available as workflow artifacts
- Test locally before publishing: `uv build && uv run twine check dist/*`

## 📚 Version Management

### Semantic Versioning

Follow [semantic versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., 1.0.0)
- `MAJOR.MINOR.PATCH-PRE.NUMBER` (e.g., 1.0.0-beta.1)

### Version Bumping

```bash
# Patch release (bug fixes)
# 0.1.0 → 0.1.1

# Minor release (new features, backwards compatible)
# 0.1.1 → 0.2.0

# Major release (breaking changes)
# 0.2.0 → 1.0.0

# Pre-release
# 1.0.0 → 1.1.0-beta.1
```

## 🎯 Next Steps

After successful publishing:

1. **Verify the release:**
   - Check https://pypi.org/project/physionetmcp/
   - Test installation: `pip install physionetmcp`

2. **Update documentation:**
   - Update installation instructions
   - Create/update changelog

3. **Announce the release:**
   - Create release notes on GitHub
   - Update any relevant documentation

---

For questions or issues with publishing, check the [GitHub Issues](https://github.com/yourusername/physionet-mcp/issues) or refer to the [PyPI documentation](https://packaging.python.org/). 