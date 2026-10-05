# Release Process Guide

This guide is for Braxis maintainers on how to cut and publish a new release.

## Prerequisites

- Push access to the GitHub repository
- PyPI account with maintainer access to the `braxis` package
- Git configured locally (`git config user.name` and `git config user.email` set)
- Python 3.8+ installed locally

## Release Checklist

### 1. Prepare the Release (Local Development)

```bash
# Update to latest main
git checkout main
git pull origin main

# Verify all checks pass
make check

# Run full test suite
pytest tests/ -v

# Verify no uncommitted changes
git status
```

### 2. Update Version & Changelog

#### Update `setup.py` version:
```python
# setup.py
setup(
    name="braxis",
    version="1.3.1",  # <- Update this (increment PATCH/MINOR/MAJOR)
    ...
)
```

#### Update `pyproject.toml` version:
```toml
# pyproject.toml
[project]
name = "braxis"
version = "1.3.1"  # <- Update this to match setup.py
```

#### Update `CHANGELOG.md`:

Add new section at top:
```markdown
## [1.3.1] - 2026-10-05

### Added
- Feature description

### Fixed
- Bug fix description

### Changed
- Change description
```

Move unreleased changes from bottom to version section. Example:

**Before:**
```markdown
## [Unreleased]
### Added
- New MCP detection

## [1.3.0] - 2026-10-05
...
```

**After:**
```markdown
## [1.3.1] - 2026-10-05
### Added
- New MCP detection

## [1.3.0] - 2026-10-05
...
```

### 3. Verify Version Consistency

```bash
# Check all version strings match
grep -r "1.3.1" setup.py pyproject.toml

# Verify setup.py parses correctly
python -c "from setuptools import setup; exec(open('setup.py').read())"

# Test installation from local changes
pip install -e .
braxis --version  # Should output: Braxis 1.3.1
```

### 4. Create Release Commit

```bash
# Stage changes
git add setup.py pyproject.toml CHANGELOG.md

# Commit with clear message
git commit -m "chore: release v1.3.1

- Update version in setup.py and pyproject.toml
- Add CHANGELOG entries for v1.3.1
- Includes [list major features/fixes]"

# Verify commit
git log --oneline -1
```

### 5. Create Git Tag

```bash
# Create annotated tag (includes metadata)
git tag -a v1.3.1 -m "Release version 1.3.1"

# List tags to verify
git tag -l | tail -5

# Show tag details
git show v1.3.1
```

### 6. Push to GitHub

```bash
# Push commits
git push origin main

# Push tags (triggers GitHub Actions)
git push origin v1.3.1

# Verify on GitHub
# Visit: https://github.com/jaykrishna316/braxis/releases
```

### 7. Verify CI/CD Pipeline

After pushing, GitHub Actions should:
- Run tests (`code-quality.yml`)
- Run regression tests (`regression-tests.yml`)
- Build distribution packages

Check status at: https://github.com/jaykrishna316/braxis/actions

Wait for all checks to ✅ pass before proceeding.

### 8. Build & Test Distribution Package

```bash
# Clean previous builds
rm -rf build dist *.egg-info

# Build source distribution and wheel
python -m build

# Verify builds were created
ls -lh dist/
# Should show:
# - braxis-1.3.1-py3-none-any.whl
# - braxis-1.3.1.tar.gz

# Test installation from built wheel
pip install dist/braxis-1.3.1-py3-none-any.whl --force-reinstall

# Verify installation
braxis --version  # Should output: Braxis 1.3.1
braxis generate --help  # Should work

# Test programmatic API
python -c "from braxis_api import BraxisAPI; print('✓ API imports successfully')"
```

### 9. Publish to PyPI

#### Option A: Manual Upload (Not Recommended)

```bash
# Install twine
pip install twine

# Upload to TestPyPI first (optional but recommended)
twine upload --repository testpypi dist/braxis-1.3.1*

# Verify on TestPyPI
# https://test.pypi.org/project/braxis/

# Upload to Production PyPI
twine upload dist/braxis-1.3.1*

# Enter PyPI credentials when prompted
```

#### Option B: Automated via GitHub Actions (Recommended)

1. Create `.github/workflows/publish.yml`:
```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/* --username __token__ --password ${{ secrets.PYPI_API_TOKEN }}
```

2. Add PYPI_API_TOKEN to GitHub Secrets:
   - Go to https://github.com/jaykrishna316/braxis/settings/secrets
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: [PyPI API token from https://pypi.org/manage/account/tokens/]

3. Tag and push (workflow handles the rest):
```bash
git tag v1.3.1
git push origin v1.3.1
# Wait for "Publish to PyPI" workflow to complete
```

### 10. Verify PyPI Publication

```bash
# Wait 1-2 minutes for PyPI to index
sleep 120

# Install from PyPI (in fresh virtual env)
pip install braxis==1.3.1

# Verify
braxis --version  # Should output: Braxis 1.3.1
```

Check on PyPI: https://pypi.org/project/braxis/1.3.1/

### 11. Create GitHub Release

```bash
# Manually create Release on GitHub, or use GitHub CLI:
gh release create v1.3.1 \
  --title "v1.3.1: Bug fixes and improvements" \
  --notes "See CHANGELOG.md for details"
```

Visit: https://github.com/jaykrishna316/braxis/releases/tag/v1.3.1

### 12. Announce Release

- [ ] Tweet/post on social media
- [ ] Update README if major feature
- [ ] Post in GitHub Discussions (if major release)
- [ ] Update any external docs/websites

## Version Bumping Strategy

### When to bump MAJOR (1.0 → 2.0)
- Breaking API changes
- Remove deprecated features
- Incompatible changes to context file formats

### When to bump MINOR (1.3 → 1.4)
- New features
- New scoring dimensions
- New language support
- Backwards compatible additions

### When to bump PATCH (1.3.0 → 1.3.1)
- Bug fixes
- Performance improvements
- Documentation updates
- Non-functional changes

## Common Issues & Solutions

### Issue: Version mismatch between setup.py and pyproject.toml

**Solution:**
```bash
# Update both to same version
sed -i 's/version="1.3.0"/version="1.3.1"/' setup.py
sed -i 's/version = "1.3.0"/version = "1.3.1"/' pyproject.toml
git diff  # Verify changes
```

### Issue: Forgot to push tag

**Solution:**
```bash
git push origin v1.3.1
```

### Issue: Need to yank a bad release from PyPI

**Solution:**
```bash
twine upload --skip-existing --skip-existing dist/* --skip-existing
# Then mark as yanked on PyPI website (https://pypi.org/manage/project/braxis/releases/)
```

### Issue: CI/CD pipeline failed

**Solution:**
```bash
# Check GitHub Actions logs
# Fix the issue
# Push the fix
git add .
git commit -m "fix: <description>"
git push origin main

# Re-tag if needed (force-push tag)
git tag -d v1.3.1
git tag -a v1.3.1 -m "Release version 1.3.1 (retry)"
git push origin v1.3.1 --force
```

## Post-Release

1. Update documentation if API changed
2. Close related GitHub issues
3. Thank contributors
4. Plan next release on Roadmap

## Release Cadence

- **Patch releases** - As needed (bug fixes, hotfixes)
- **Minor releases** - ~Monthly (new features, improvements)
- **Major releases** - ~Quarterly (breaking changes, architectural updates)

## Support

For questions about the release process:
- Check this guide first
- Ask in GitHub Discussions
- Open an issue if problems occur
