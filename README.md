# Braxis

[![PyPI - Version](https://img.shields.io/pypi/v/braxis.svg)](https://pypi.org/project/braxis/)
[![Python - Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Tests - Status](https://img.shields.io/badge/tests-30%2F30%20passing-brightgreen.svg)](https://github.com/jaykrishna316/braxis/blob/main/test_braxis.py)
[![License - MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/jaykrishna316/braxis/blob/main/LICENSE)
[![Agent Readiness - AI-Native](https://img.shields.io/badge/agent%20readiness-71%2F100%20%7C%20AI--Native-blue.svg)]()

**Auto-generate AI agent context files. Keep them in sync with your code.**

Your AI agents (Claude Code, Cursor, Copilot) read from `AGENTS.md` to understand your project. When your code changes, that file gets stale. Agents miss patterns, violate conventions, hallucinate.

Braxis solves this: **one command generates four context files that stay in sync with your codebase.**

---

## See It In Action

Before Braxis:

Day 1: Agent reads stale AGENTS.md from 2 weeks ago
Sees old directory structure
Doesn't know about new error handling pattern
Makes bad suggestions based on outdated info


After Braxis:

Every push: GitHub Actions runs Braxis
Analyzes current codebase
Regenerates AGENTS.md, CLAUDE.md, .cursorrules, .agentic-config.json
Creates PR with updates
Your agents always see current reality


---

## How To Use Braxis On Your Project (5 minutes)

### Step 1: Install

```bash
pip install braxis
```

### Step 2: Go to Your Project

```bash
cd /path/to/your/project
```

### Step 3: Generate Context Files

```bash
braxis generate
```

That's it. Braxis creates:

your-project/
├── AGENTS.md (Universal agent instructions)
├── CLAUDE.md (Claude Code optimized)
├── .cursorrules (Cursor IDE rules)
├── .agentic-config.json (Machine-readable metadata)
└── (your existing files)


### Step 4: See What It Generated

```bash
cat AGENTS.md
```

### Step 5: Commit to Your Repo

```bash
git add AGENTS.md CLAUDE.md .cursorrules .agentic-config.json
git commit -m "chore: add AI agent context files"
git push
```

### Step 6: Your Agents Now Use These Files

**In Claude Code:** Automatically reads `CLAUDE.md`
**In Cursor:** Copy `.cursorrules` into Cursor Settings → Rules
**In any agent:** Reads `AGENTS.md` (universal format)

---

---

## ✨ Key Features

- ✅ **One Command** - Generate all context files with `braxis generate`
- ✅ **Zero Config** - Works out of the box, no setup needed
- ✅ **Auto-Score** - Measure your project's AI agent readiness (0-100)
- ✅ **Multi-Language** - Supports Python, JavaScript, TypeScript, Go, Rust, Java, and more
- ✅ **CI/CD Ready** - GitHub Actions workflow included
- ✅ **Pre-commit Hooks** - Validate before every commit
- ✅ **Safe & Reliable** - Input validation, atomic writes, comprehensive error handling
- ✅ **Well-Tested** - 30+ unit tests with 100% pass rate
- ✅ **No Dependencies** - Pure Python, zero external packages
- ✅ **Production-Grade** - Used in real projects, actively maintained

---

## 🚀 Extended Features

### Auto-Update with GitHub Actions

Automatically regenerate context files on every push using GitHub Actions.

Braxis includes a ready-to-use workflow. Copy it to your repo:

```bash
mkdir -p .github/workflows
cp /path/to/braxis/.github/workflows/braxis-score.yml .github/workflows/
git add .github/workflows/braxis-score.yml
git commit -m "chore: add braxis auto-update workflow"
git push
```

Or manually create `.github/workflows/braxis-score.yml`:

```yaml
name: Braxis Score Check

on:
  push:
    branches: [ main, develop ]
    paths:
      - '**.py'
      - 'package.json'
      - 'pyproject.toml'
      - 'setup.py'

jobs:
  score:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install braxis
      - run: braxis score
      - run: braxis generate
      - name: Create Pull Request for updates
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'chore: regenerate braxis context files'
          title: 'chore: update agent context files'
          branch: braxis/auto-update
```

**Result:** Every push automatically regenerates context files and creates a PR if needed. ✨

### Pre-commit Hooks

Validate context files before every commit using pre-commit.

#### For Contributors to Braxis:

```bash
pip install pre-commit
pre-commit install
```

The hooks will run automatically on `git commit`.

#### For Your Projects Using Braxis:

Copy the example config to your project:

```bash
cp /path/to/braxis/.pre-commit-config.example.yaml .pre-commit-config.yaml
```

Then install:

```bash
pip install pre-commit
pre-commit install
```

Now braxis will validate your project before each commit! 🔐

---

## 📚 Contributing

Braxis welcomes contributions! Read [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Setup instructions
- Development workflow  
- Testing guidelines
- Code style guide
- PR process

**Quick start:**

```bash
git clone https://github.com/YOUR_USERNAME/braxis.git
cd braxis
python3 -m venv venv
source venv/bin/activate
pip install -e .
python3 -m unittest test_braxis -v
```

---

---

## Customize For Your Project (Optional)

Create `.agentic-config.json`:

```json
{
  "name": "MyApp",
  "description": "A production API service",
  "exclude_patterns": [
    "node_modules/**",
    ".venv/**",
    "build/**"
  ],
  "custom_conventions": {
    "error_handling": "Always use try/except and log",
    "async_patterns": "All I/O must be async",
    "validation": "Use Pydantic models for inputs"
  },
  "critical_files": [
    "src/main.py",
    "src/api/routes.py",
    "README.md"
  ]
}
```

---

## What Each File Does

**AGENTS.md** - Universal format read by any AI agent

**CLAUDE.md** - Optimized for Claude Code

**.cursorrules** - Rules for Cursor IDE

**.agentic-config.json** - Machine-readable metadata

---

## Score Your Project

### See Your Agent Readiness Score

Check how ready your codebase is for AI agents:

```bash
braxis score
```

**Example output:**

```
============================================================
Agent Readiness Score: 71/100
============================================================

Breakdown:

 Architecture          10/100 [██░░░░░░░░░░░░░░░░░░]
 Testing                7/100 [█░░░░░░░░░░░░░░░░░░]
 Dependencies          12/100 [██░░░░░░░░░░░░░░░░░]
 Conventions           10/100 [██░░░░░░░░░░░░░░░░░░]
 Entry Points           4/100 [░░░░░░░░░░░░░░░░░░░]
 Security              10/100 [██░░░░░░░░░░░░░░░░░░]
 Build                 10/100 [██░░░░░░░░░░░░░░░░░░]
 Documentation          8/100 [█░░░░░░░░░░░░░░░░░░]

Tier: AI-Native

Detected:
 Languages: python
 Build System: Python (pip/setuptools)
 Test Frameworks: pytest, unittest
 Test Files: 1
 Critical Files: 0

Recommendations:
 * Increase test coverage
 * Add input validation and security checks
```

### Understanding Your Score

| Score | Tier | Meaning |
|-------|------|---------|
| 90-100 | **Agent-Optimized** | Production-ready for AI agents |
| 80-89 | **AI-Native-Plus** | Excellent agent compatibility |
| 60-79 | **AI-Native** | Good agent support |
| 30-59 | **Agent-Aware** | Basic agent compatibility |
| 0-29 | **Not Ready** | Needs improvements |

### Score Categories Explained

- **Architecture** - Critical files, entry points, project structure
- **Testing** - Test coverage and test framework detection
- **Dependencies** - Build system and dependency management
- **Conventions** - Code patterns, error handling, type hints
- **Entry Points** - Main functions and executable files
- **Security** - Input validation, security checks, config management
- **Build** - Build files and dependency tracking
- **Documentation** - README and project documentation

### Test a Specific Project

```bash
python3 braxis.py score --path /path/to/project
```

---

## All Commands

```bash
# Check version
braxis --version

# Score your project's agent readiness
braxis score
braxis score --path /path/to/project  # Score a specific project

# Generate context files
braxis generate
braxis generate --path /path/to/project

# Inspect project analysis
braxis inspect
braxis inspect --path /path/to/project

# Validate context files exist
braxis validate
braxis validate --path /path/to/project
```

---

## Quality & Reliability

Braxis is production-grade with enterprise-level quality standards:

### Safety Features
- **Input Validation** - Validates project paths and file inputs with clear error messages
- **Atomic File Writing** - Uses temporary files and atomic operations to prevent partial writes
- **Error Handling** - Comprehensive error handling with informative feedback
- **Path Normalization** - Converts relative paths to absolute paths safely

### Testing & Quality
- **Comprehensive Tests** - 30+ unit tests covering all major functionality
- **Test Coverage** - 100% pass rate across all test suites
- **Automated Testing** - GitHub Actions runs tests on every commit
- **Pre-commit Hooks** - Validates before every commit
- **Code Style** - Follows PEP 8 standards
- **Zero Dependencies** - No external packages required

### Run Tests Locally

```bash
# Run all tests
python3 -m unittest test_braxis -v

# Run specific test class
python3 -m unittest test_braxis.TestValidateProjectPath -v

# Check test coverage
pip install coverage
coverage run -m unittest test_braxis
coverage report
```

**Status:** All 30 tests passing ✅

---

## Requirements

- Python 3.8+
- Zero external dependencies
- Works on macOS, Linux, Windows

---

## Getting Help

- **Report Issues** - [GitHub Issues](https://github.com/jaykrishna316/braxis/issues)
- **Discussions** - [GitHub Discussions](https://github.com/jaykrishna316/braxis/discussions)
- **Contributing** - See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## License

MIT - Free to use in personal and commercial projects

---

## Why Braxis?

AI agents need current context to work effectively. Without it, they:
- ❌ Miss recent code patterns
- ❌ Violate project conventions
- ❌ Make outdated suggestions
- ❌ Waste your time with hallucinations

Braxis solves this automatically. One command. Always in sync. ✨

---

**Braxis** — Keep your agents aligned. Keep your code context current.

Made with ❤️ for AI-native development.

