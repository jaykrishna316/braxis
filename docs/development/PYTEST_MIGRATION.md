# Pytest Migration Guide

## Overview

Braxis has migrated from unittest to pytest for its test framework. This document explains the changes, benefits, and how to use the new testing setup.

## What Changed

### Before (unittest)
```bash
python test_braxis.py
```

### After (pytest)
```bash
pytest
# or with coverage
coverage run -m pytest
```

## Migration Details

### Test File Structure

All test classes were converted from `unittest.TestCase` to pytest-style test classes:

**Before (unittest):**
```python
import unittest

class TestValidation(unittest.TestCase):
    def test_valid_input(self):
        self.assertEqual(result, expected)
        self.assertTrue(condition)
    
    def assertRaises(ValueError):
        function()
```

**After (pytest):**
```python
import pytest

class TestValidation:
    def test_valid_input(self):
        assert result == expected
        assert condition
    
    def test_raises_error():
        with pytest.raises(ValueError):
            function()
```

### Key Improvements

1. **Simpler Assertions**
   - Use plain `assert` statements instead of `self.assertEqual()`, `self.assertTrue()`, etc.
   - Better error messages and diffs automatically

2. **Built-in Fixtures**
   - Replaced `setUp()`/`tearDown()` with pytest fixtures
   - Example: `tmpdir` fixture for temporary directories

3. **Better Error Reporting**
   - More detailed failure information
   - Better formatting of assertion failures

4. **Plugin Ecosystem**
   - Integrated coverage reporting
   - Parametrized tests
   - Markers for organizing tests

5. **Configuration in One Place**
   - `pytest.ini` for test configuration
   - `pyproject.toml` for coverage settings

## Installation

### For Development

Install with test dependencies:

```bash
pip install -e ".[dev]"
```

This includes pytest and coverage tools.

### Test-Only Installation

For CI/CD or minimal setup:

```bash
pip install -e ".[test]"
```

## Running Tests

### Run All Tests

```bash
pytest
# or
make test
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest test_braxis.py
```

### Run Specific Test Class

```bash
pytest test_braxis.py::TestValidation
```

### Run Specific Test Function

```bash
pytest test_braxis.py::TestValidation::test_valid_input
```

### Run Tests Matching a Pattern

```bash
pytest -k "test_scan"
```

### Stop on First Failure

```bash
pytest -x
```

### Show Print Statements

```bash
pytest -s
```

## Coverage Reporting

### Generate Coverage Report

```bash
make coverage
```

This will:
1. Run all tests with coverage tracking
2. Display a summary report in the terminal
3. Generate an HTML report in `htmlcov/`

### View HTML Report

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Check Coverage Percentage

```bash
coverage report
```

### Combine with pytest

```bash
coverage run -m pytest -v
coverage report
coverage html
```

## Test Organization

Test files follow the naming convention:

- `test_*.py` - Test files (discovered by pytest automatically)
- `Test*` - Test classes (discovered by pytest)
- `test_*` - Test functions (discovered by pytest)

## Configuration Files

### pytest.ini

Located at repository root:

```ini
[pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### pyproject.toml

Test and coverage configuration:

```toml
[tool.pytest.ini_options]
testpaths = ["."]
python_files = ["test_*.py"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["."]
omit = ["*/tests/*", "*/test_*.py"]

[tool.coverage.report]
show_missing = true
```

## Development Workflow

### Recommended Workflow

```bash
# 1. Make changes
git checkout -b feature/my-change

# 2. Run tests to verify
make test

# 3. Check test coverage
make coverage

# 4. Run full checks (tests + lint)
make check

# 5. Commit and push
git add .
git commit -m "feat: implement feature"
git push
```

### Quick Test Iteration

During development, run specific tests:

```bash
# Test one function
pytest test_braxis.py::TestValidation::test_method -v

# Test one class
pytest test_braxis.py::TestValidation -v

# Stop on first failure
pytest -x

# Show print output
pytest -s
```

## CI/CD Integration

GitHub Actions workflow uses pytest:

```yaml
- name: Run tests
  run: |
    pip install -e ".[test]"
    pytest -v --tb=short
    
- name: Generate coverage
  run: |
    coverage run -m pytest
    coverage report
```

## Migration Checklist

If converting other test projects to pytest:

- [x] Convert `unittest.TestCase` classes to plain classes
- [x] Replace assertion methods with `assert` statements
- [x] Replace `self.assertRaises()` with `pytest.raises()`
- [x] Convert `setUp()`/`tearDown()` to fixtures
- [x] Update Makefile with pytest commands
- [x] Add pytest configuration (pytest.ini or pyproject.toml)
- [x] Add pytest and coverage to optional dependencies
- [x] Update CI/CD workflows
- [x] Test locally to ensure all tests pass

## Benefits of pytest

1. **Simpler Syntax** - Less boilerplate, more readable
2. **Better Error Messages** - Shows exact values that differ
3. **Fixtures** - Cleaner setup/teardown than unittest
4. **Parametrized Tests** - Run same test with different inputs
5. **Markers** - Tag and filter tests easily
6. **Plugins** - Rich ecosystem (coverage, mock, etc.)
7. **Faster Development** - Quick iteration with -x, -k, -s flags
8. **Better CI Integration** - Works naturally with most CI systems

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [How to use pytest with GitHub Actions](https://docs.github.com/en/actions/guides/building-and-testing-python)

## Troubleshooting

### Tests Not Found

```bash
# Check pytest configuration
pytest --collect-only

# Verify test file naming
ls test_*.py
```

### Import Errors

```bash
# Install in editable mode
pip install -e .

# Check sys.path
python -c "import sys; print('\n'.join(sys.path))"
```

### Coverage Not Reporting

```bash
# Install coverage
pip install -e ".[dev]"

# Run with explicit coverage
coverage run -m pytest -v
coverage report
```

## Notes

- Tests must be runnable from the repository root
- No external dependencies required for core braxis functionality
- pytest is an optional dev dependency to keep core zero-dependency
- Coverage reports are generated to `htmlcov/` directory
