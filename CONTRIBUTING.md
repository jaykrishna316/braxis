# Contributing to Braxis

Thank you for your interest in contributing to Braxis! We welcome all contributions, from bug reports to new features.

## Getting Started

### Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/braxis.git
cd braxis
```

### Set Up Development Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
pip install pytest
```

### Run Tests
```bash
python3 -m unittest test_braxis -v
```

### Check Score
```bash
python3 braxis.py score
```

---

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/bug-description
```

### 2. Make Changes
- Write clean, well-documented code
- Add tests for new features
- Follow PEP 8 style guide

### 3. Test Your Changes
```bash
# Run all tests
python3 -m unittest test_braxis -v

# Test specific module
python3 -m unittest test_braxis.TestValidateProjectPath -v

# Check code quality
python3 braxis.py inspect
```

### 4. Commit
```bash
git add .
git commit -m "feat: describe your changes

- Detail 1
- Detail 2"
```

Use conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for code refactoring
- `chore:` for maintenance

### 5. Push & Create PR
```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub with clear description.

---

## Code Style

- Follow PEP 8
- Use type hints where possible
- Keep functions focused and single-purpose
- Add docstrings to public functions
- No external dependencies (except setuptools)

---

## Testing Guidelines

- Add tests for new features
- Add tests for bug fixes
- Test edge cases and error conditions
- All tests must pass before PR merge

---

## Scoring & Quality

Your contribution should maintain or improve Braxis's own agent readiness score:

```bash
python3 braxis.py score
```

Target: **71/100 (AI-Native)** or higher

---

## Questions?

- Open an issue for bugs
- Start a discussion for questions
- Check existing issues/PRs first

Thank you for contributing! 🎉
