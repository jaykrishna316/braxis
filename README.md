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

## ✨ Key Features

- ✅ **One Command** - Generate all context files with `braxis generate`
- ✅ **Zero Config** - Works out of the box, no setup needed
- ✅ **Auto-Score** - Measure your project's AI agent readiness (0-100)
- ✅ **Score History** - Track improvements over time with trends & analytics
- ✅ **LLM Recommendations** - AI-powered suggestions using Claude API (optional)
- ✅ **Multi-Language** - Supports Python, JavaScript, TypeScript, Go, Rust, Java, and more
- ✅ **CI/CD Ready** - GitHub Actions workflow included
- ✅ **Pre-commit Hooks** - Validate before every commit
- ✅ **Safe & Reliable** - Input validation, atomic writes, comprehensive error handling
- ✅ **Well-Tested** - 30+ unit tests with 100% pass rate
- ✅ **No Dependencies** - Pure Python, zero external packages (LLM features optional)
- ✅ **Production-Grade** - Used in real projects, actively maintained

---

## How To Use Braxis On Your Project (5 minutes)

### Step 1: Install

```bash
# Basic installation (core features)
pip install braxis

# With LLM support (for AI recommendations)
pip install braxis[llm]
```

### Step 2: (Optional) Set Up Claude API

For LLM-powered recommendations:

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

Get your API key: https://console.anthropic.com

### Step 3: Go to Your Project

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

### Score History & Trends

Track your project's AI agent readiness score over time.

```bash
# View all historical scores
braxis history

# View scores with trends and direction indicators
braxis history --trends
```

**Example output:**
```
============================================================
Score History for myproject
============================================================

1. 2026-10-01 - 65/100 (AI-Native)
2. 2026-10-05 - 72/100 (AI-Native)
3. 2026-10-10 - 78/100 (AI-Native-Plus)

Trend: 📈 +13 points

============================================================
```

**Features:**
- Automatic score persistence on every `braxis score` run
- Project-specific tracking (stored in `~/.braxis/history/`)
- Trend indicators: 📈 (improving) 📉 (declining) ➡️ (stable)
- Configurable history limits
- Timestamps and tier information included

### LLM-Powered Recommendations

Get intelligent, actionable recommendations from Claude AI.

**Setup:**
```bash
# Install with LLM support
pip install braxis[llm]

# Set your API key
export ANTHROPIC_API_KEY='sk-ant-...'
```

**Usage:**
```bash
braxis recommendations
```

**Example output:**
```
============================================================
LLM-Powered Recommendations for myproject
============================================================

1. Add Comprehensive Test Suite
   Why it matters: Testing is the foundation of reliable code.
   Current state: Only 7% testing coverage
   How to implement:
   - Start with pytest fixtures for common patterns
   - Aim for 80%+ coverage on core modules
   - Run: pytest --cov to measure progress

2. Implement Input Validation Framework
   Why it matters: Validation prevents bugs and security issues
   Current state: No systematic validation detected
   How to implement:
   - Use Pydantic for request validation
   - Add schema validation to all API endpoints
   - Example: from pydantic import BaseModel

[... more recommendations ...]
```

**Features:**
- Uses Claude Opus 5.5 for high-quality analysis
- 5-7 actionable recommendations per run
- Concrete implementation steps for each suggestion
- Focuses on improving Agent Readiness Score
- Gracefully handles missing API keys
- Optional dependency (braxis works without it)

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

# View score history
braxis history
braxis history --path /path/to/project
braxis history --trends                 # Show trends with emoji indicators
braxis history --path /path/to/project --trends

# Get LLM-powered recommendations (requires: export ANTHROPIC_API_KEY='sk-ant-...')
braxis recommendations
braxis recommendations --path /path/to/project
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

## Why Braxis Stands Out

| Feature | Braxis | CursorRules | .cursorrules | Other Tools |
|---------|--------|-------------|--------------|-------------|
| **Auto-generates context** | ✅ Four formats | ❌ Manual | ❌ Manual | Varies |
| **Scores readiness** | ✅ 0-100 with 5 tiers | ❌ No | ❌ No | ❌ Limited |
| **Tracks history** | ✅ Over time with trends | ❌ No | ❌ No | ❌ No |
| **AI recommendations** | ✅ Claude-powered | ❌ No | ❌ No | ❌ Limited |
| **Multi-language** | ✅ 15+ languages | ❌ Limited | ❌ Limited | Varies |
| **CI/CD integration** | ✅ GitHub Actions ready | ⚠️ Manual | ⚠️ Manual | Varies |
| **Zero dependencies** | ✅ Core only | ✅ Yes | ✅ Yes | Varies |
| **Production-tested** | ✅ 30+ tests | ⚠️ Limited | ⚠️ Limited | Varies |
| **Atomic file ops** | ✅ Safe writes | ❌ No | ❌ No | ❌ No |
| **Active updates** | ✅ Latest Claude models | ⚠️ Varies | ⚠️ Varies | Varies |

**The difference:** Braxis goes beyond rules files. It continuously analyzes your codebase, scores your readiness, tracks progress, and provides AI-driven guidance—all automatically.

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

## Real-World Usage Examples

### Scenario 1: Onboarding New Team Members
```bash
# New developer clones repo
$ braxis score
Agent Readiness: 78/100 (AI-Native-Plus)

# They immediately understand the project structure, conventions, and quality baseline
# Opens AGENTS.md in Claude Code - instant context
```

### Scenario 2: Tracking Quality Improvements
```bash
# Initial state
$ braxis score
Score: 45/100 (Agent-Aware)

# After 2 weeks of improvements
$ braxis history --trends
📈 +28 points

# Team celebrates progress with visual trend data
```

### Scenario 3: CI/CD Automated Updates
```bash
# Every commit triggers workflow
$ braxis score
$ braxis generate
# PR created with updated context files
# Agents always have latest project info
```

### Scenario 4: Before Starting Major Refactor
```bash
$ braxis recommendations
# Get AI-powered guidance on what to improve
# Prioritize high-impact changes
# Measure progress with `braxis history`
```

---

## Why Braxis?

AI agents need current context to work effectively. Without it, they:
- ❌ Miss recent code patterns
- ❌ Violate project conventions
- ❌ Make outdated suggestions
- ❌ Waste your time with hallucinations

Braxis solves this automatically:
1. **Generates** context files from real code analysis
2. **Scores** your readiness for AI agents (0-100)
3. **Tracks** improvements over time with trends
4. **Recommends** actionable next steps via Claude AI

One command. Always in sync. Always improving. ✨

---

## License

MIT - Free to use in personal and commercial projects

See [LICENSE](LICENSE) for details.

---

## Roadmap

Upcoming features in development:
- 🚧 Custom scoring rules engine
- 🚧 Project comparison & benchmarking
- 🚧 Web dashboard for visualization
- 🚧 Score forecasting & predictions
- 🚧 Integration with more IDE platforms

Have a feature request? [Open an issue](https://github.com/jaykrishna316/braxis/issues/new)

---

**Braxis** — Keep your agents aligned. Keep your code context current.

Continuously analyze. Automatically improve. Always sync. ✨

Made with ❤️ for AI-native development by developers, for developers.

