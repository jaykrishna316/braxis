# Braxis — Auto-Generated AI Agent Context Files

[![PyPI - Version](https://img.shields.io/pypi/v/braxis.svg)](https://pypi.org/project/braxis/)
[![Python - Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Tests - Status](https://img.shields.io/badge/tests-57%2F57%20passing-brightgreen.svg)](https://github.com/jaykrishna316/braxis/blob/main/test_braxis.py)
[![License - MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/jaykrishna316/braxis/blob/main/LICENSE)

> **Keep your AI agents in sync with your code. One command. Always current. Production-grade.**

## The Problem

Your AI agents (Claude Code, Cursor, Copilot) read `AGENTS.md` to understand your project. But when your code evolves:
- 📉 Context becomes stale within days
- 🤔 Agents make outdated suggestions 
- ❌ They violate conventions they don't know about
- 🔄 Updating manually is tedious and error-prone

Without fresh context, AI agents are less effective than they should be.

## The Solution

**Braxis automatically generates and keeps your AI context files in sync with your codebase.**

One command. Your agents always see current reality:

```bash
pip install braxis
cd /path/to/your/project
braxis generate
```

That's it. Braxis creates:
- **AGENTS.md** - Universal format for any AI agent
- **CLAUDE.md** - Optimized for Claude Code
- **.cursorrules** - Rules for Cursor IDE
- **.agentic-config.json** - Machine-readable config

Commit them to your repo. Your agents get automatic, always-current guidance.

---

## Core Features

✅ **One Command** - Generate all context files with `braxis generate`
✅ **Zero Config** - Works out of the box, no setup needed
✅ **Programmatic API** - Use Braxis as a Python library in your tools (NEW in v1.1)
✅ **Configuration Files** - Customize behavior with `.braxis.yml` (NEW in v1.1)
✅ **Smart Triggering** - Skip trivial changes, reduce CI noise (NEW in v1.1)
✅ **Auto-Score** - Measure your project's AI agent readiness (0-100)
✅ **Score History** - Track improvements over time with trends
✅ **Multi-Language** - Python, JavaScript, TypeScript, Go, Rust, Java, and more
✅ **Monorepo Ready** - Hierarchical AGENTS.md for pnpm, uv, yarn, npm, lerna
✅ **CI/CD Integration** - GitHub Actions workflow included, auto-updates on push
✅ **Pre-commit Hooks** - Validate before every commit
✅ **LLM Recommendations** - Claude AI suggests improvements (optional)
✅ **MCP Detection** - Auto-documents MCP servers
✅ **Safe & Reliable** - Input validation, atomic writes, zero external dependencies
✅ **Production-Tested** - Used by real teams, actively maintained

---

## Why Developers Love Braxis

### Fast Results
- ⚡ One command generates all context files
- 📊 Auto-scores your project's AI readiness (0-100)
- 🔄 Works out of the box, zero config needed

### Production-Grade Quality
- ✅ 30+ unit tests, 100% pass rate
- 🔒 Strict type-checking and error handling
- 🏗️ Deep pattern detection and architecture analysis
- 🚀 Tested on projects from 27 to 22,679 files

### Stays in Sync Automatically
- 📅 GitHub Actions workflow included
- 🔍 Detects code changes instantly
- 📈 Tracks improvements over time with trends
- 💡 AI-powered recommendations via Claude API

---

## Quick Start (2 Minutes)

```bash
# 1. Install
pip install braxis

# 2. Generate
cd /your/project
braxis generate

# 3. Commit
git add AGENTS.md CLAUDE.md .cursorrules .agentic-config.json
git commit -m "chore: add AI agent context files"
git push
```

Your agents now read current, accurate context. That's all.

---

## What You Get

### For Claude Code Users
Claude Code automatically reads your `CLAUDE.md`. Instantly understands:
- Project structure and conventions
- Testing patterns and requirements
- Architecture decisions and gotchas
- Agent contribution boundaries

### For Cursor IDE Users
Copy `.cursorrules` into your Cursor settings. Cursor respects your project's rules automatically.

### For Any AI Agent
Share `AGENTS.md` with any agent (Copilot, custom agents, etc.). Universal format, no vendor lock-in.

---

## 🔄 Hybrid Automation: Keep Context Files Always Fresh

The Problem: Context files get stale the moment your code changes. Manual regeneration is forgotten. Agents read yesterday's documentation.

**The Solution:** Braxis uses two-layer automation to ensure context files are never out of sync:

### Layer 1: Local Pre-commit Hook (Immediate Feedback)

```bash
./scripts/setup-braxis-hook.sh
```

- ✅ Runs `braxis generate` before every commit
- ✅ Auto-stages context file updates
- ✅ Catches stale files before they're committed
- ✅ Zero external dependencies (pure bash)

**Example:**
```
$ git commit -m "add new feature"
🤖 Braxis Context Generator (pre-commit hook)
📝 Regenerating context files...
📌 Context files updated
   Staging changes...
✅ Updated files staged for commit
```

### Layer 2: Remote GitHub Actions (Safety Net)

Triggers automatically on every push to `main/develop/master`:
- ✅ Only on meaningful code changes (src/, tests/, setup.py)
- ✅ Auto-commits context updates if local hook was skipped
- ✅ Posts confirmation comment on PRs
- ✅ Ensures remote is always in sync

**Result:** Context files are always fresh, whether commits come from:
- 💻 Local development (hook catches it immediately)
- 🔄 Direct pushes to main (workflow auto-updates)
- 📤 Pull requests (workflow auto-commits before merge)

### Why This Matters

| Scenario | Without Automation | With Hybrid Approach |
|----------|-------------------|----------------------|
| Developer adds new feature | ❌ AGENTS.md stale in seconds | ✅ Auto-regenerated on commit |
| Team member reads code | ❌ Context files 5+ commits behind | ✅ Always current & accurate |
| AI agent analyzes code | ❌ Reads outdated architecture docs | ✅ Gets real-time project insight |
| New contributor joins | ❌ Reads stale patterns & conventions | ✅ Sees latest project standards |
| PR review happens | ❌ Comments miss recent changes | ✅ Context reflects actual code |

**One command. Two layers. Zero manual work. ✨**

---

## Real-World Impact

### Before Braxis
```
Day 1: Agent reads AGENTS.md from 2 weeks ago
Day 3: New error handling pattern added, agent doesn't know
Day 5: Agent violates outdated convention
Day 7: Agent suggests based on old architecture
```

### With Braxis
```
Every push: Braxis analyzes current codebase
Every merge: Context files auto-regenerate
Result: Agents always see the latest reality
```

---

## Advanced Features

### AGENTS.md Grading System (NEW in v1.4)
Evaluate your AGENTS.md quality against industry standards:
```bash
braxis grade --path AGENTS.md --compare
```
Get a 0-100 score with 10-dimension rubric and benchmarks against FastAPI, Sentry, Airflow.

### Dual-Format Context Files (v1.4)
- **Category A: Operations Manual** - Automatically extracted from CONTRIBUTING.md (AI policies, procedures, workarounds)
- **Category B: Architecture Guide** - Auto-generated from your codebase (structure, patterns, conventions)

### Repository Gotchas Detection (v1.2)
Automatically identifies common pitfalls:
- I/O in transactions
- Missing error handling
- Anti-patterns with before/after examples

### Subsystem Ownership Mapping (v1.2)
Visualize which subsystem owns what, prevent scope creep and conflicts.

---

## Score Your Project

See how AI-ready your codebase is:

```bash
braxis score
```

**Example output:**
```
Agent Readiness Score: 78/100 (AI-Native-Plus)

Breakdown:
 Architecture          10/100 [██░░░░░░░░░░░░░░░░░░]
 Testing                7/100 [█░░░░░░░░░░░░░░░░░░]
 Conventions           10/100 [██░░░░░░░░░░░░░░░░░░]
 Security              10/100 [██░░░░░░░░░░░░░░░░░░]
 Build                 10/100 [██░░░░░░░░░░░░░░░░░░]
 [... 3 more dimensions]
```

**Score Tiers:**
- **90-100** — Agent-Optimized (production-ready)
- **80-89** — AI-Native-Plus (excellent)
- **60-79** — AI-Native (good)
- **30-59** — Agent-Aware (basic)
- **0-29** — Not Ready

---

## Auto-Update with GitHub Actions

Enable automatic context regeneration on every push:

```bash
mkdir -p .github/workflows
cat > .github/workflows/braxis-auto-update.yml << 'EOF'
name: Braxis Auto-Update

on:
  push:
    branches: [ main ]
    paths:
      - '**.py'
      - 'package.json'
      - 'pyproject.toml'
      - 'setup.py'

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install braxis
      - run: braxis generate
      - name: Create PR with updates
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'chore: regenerate braxis context files'
          title: 'chore: update agent context files'
          branch: braxis/auto-update
EOF
```

Done. Context files regenerate automatically on every push.

---

## Why Braxis Stands Out

| Feature | Braxis | CursorRules | Other Tools |
|---------|--------|-------------|-------------|
| Auto-generates context | ✅ Four formats | ❌ Manual | ❌ Manual |
| Scores readiness | ✅ 0-100 | ❌ No | ❌ Limited |
| Tracks history | ✅ Yes | ❌ No | ❌ No |
| AI recommendations | ✅ Claude | ❌ No | ❌ No |
| Multi-language | ✅ 15+ | ❌ Limited | Varies |
| Monorepo support | ✅ Hierarchical | ⚠️ Limited | ⚠️ Limited |
| Production-tested | ✅ 30+ tests | ⚠️ Limited | Varies |
| Zero dependencies | ✅ Yes | ✅ Yes | Varies |

**The difference:** Braxis continuously analyzes your codebase, scores your readiness, tracks progress, and provides AI-driven guidance—all automatically.

---

## All Commands

```bash
# Generate context files
braxis generate                     # Current project
braxis generate --path /your/proj   # Specific project

# Score your project
braxis score                        # See readiness score
braxis score --path /your/proj

# Inspect analysis
braxis inspect                      # View detailed analysis

# Track progress
braxis history                      # All scores over time
braxis history --trends             # With trend indicators

# Grade AGENTS.md quality
braxis grade                        # Current project
braxis grade --compare              # With benchmarks

# Get recommendations
braxis recommendations              # Needs ANTHROPIC_API_KEY

# Validate context files
braxis validate                     # Check files exist
braxis --version                    # Check version
```

---

## 🔧 Programmatic API (NEW in v1.1)

Use Braxis as a Python library in your own tools and workflows:

### Generate Context Files Programmatically

```python
from braxis_api import ContextGenerator

generator = ContextGenerator(project_path=".")
result = generator.generate()

if result.success:
    for filename, content in result.changes.items():
        print(f"✅ Generated: {filename}")
```

### Analyze AI Readiness Scores

```python
from braxis_api import ScoreAnalyzer

analyzer = ScoreAnalyzer(project_path=".")
score = analyzer.calculate()

print(f"AI Readiness: {score.total}/100 ({score.level})")
print(f"Testing: {score.testing}/100")
print(f"Architecture: {score.architecture}/100")

# Get improvement suggestions
suggestions = analyzer.get_improvement_suggestions()
for s in suggestions:
    print(f"{s.dimension}: {s.current_score} → {s.target_score}")
```

### Track Score Trends Over Time

```python
from braxis_api import TrendAnalyzer

analyzer = TrendAnalyzer(project_path=".")
history = analyzer.get_history(limit=10)

trend = analyzer.get_trend("testing")
if trend:
    print(f"Testing trend: {trend['trend']}")
    print(f"Average: {trend['average']:.0f}/100")

predicted = analyzer.predict_score(days_ahead=30)
print(f"Predicted score in 30 days: {predicted}/100")
```

### Analyze Multiple Repositories

```python
from braxis_api import MultiRepoAnalyzer

analyzer = MultiRepoAnalyzer(repos=[
    "/path/to/repo1",
    "/path/to/repo2",
    "/path/to/repo3",
])

org_summary = analyzer.get_org_summary()
print(f"Organization Average: {org_summary['average_score']}/100")
print(f"Analyzed {org_summary['num_repos']} repositories")
```

### Smart Triggering (Skip Trivial Changes)

```python
from braxis_triggers import SmartTrigger

trigger = SmartTrigger()
should_regen, metrics = trigger.should_regenerate(
    changed_files=["src/module.py", "tests/test.py"],
    repo_path=".",
    git_base="origin/main"
)

if should_regen:
    print(f"Regenerating context... ({metrics.total_lines_changed} lines changed)")
else:
    print(f"Skipping (reason: {metrics.change_reason})")
```

### Use Case: IDE Plugins

```python
# Show real-time AI readiness in your editor
from braxis_api import ScoreAnalyzer

def get_project_health():
    analyzer = ScoreAnalyzer(project_path=".")
    score = analyzer.calculate()
    return {
        "score": score.total,
        "level": score.level,
        "status": "🟢" if score.total >= 70 else "🟡" if score.total >= 40 else "🔴"
    }
```

### Use Case: Organization Dashboard

```python
# Track scores across all your repos
from braxis_api import MultiRepoAnalyzer
import json

analyzer = MultiRepoAnalyzer(repos=["repo1", "repo2", "repo3"])
summary = analyzer.get_org_summary()

# Export to JSON for dashboard
with open("org-metrics.json", "w") as f:
    json.dump(summary, f, indent=2)
```

**See [API_GUIDE.md](API_GUIDE.md) for complete documentation.**

---

## ⚙️ Configuration File Support (NEW in v1.1)

Customize Braxis behavior per project using `.braxis.yml`:

```yaml
# Control context file generation
context:
  output_format: markdown
  code_block_style: python-fenced
  include_test_metrics: true

# Set change thresholds and patterns
generation:
  min_change_threshold: 5  # Lines changed to trigger regeneration
  skip_trivial_changes: true  # Skip whitespace/comments only
  exclude_patterns:
    - __pycache__
    - .venv
    - node_modules

# Configure GitHub Actions automation
automation:
  github_paths: [src/, tests/, setup.py, pyproject.toml]
  github_branches: [main, develop, master]
  auto_commit: true
  auto_comment_prs: true
  commit_message: "chore: regenerate context files"

# Customize scoring weights
scoring:
  enable_scoring: true
  weight_testing: 1.2  # Weight testing 20% higher
  weight_documentation: 0.8  # Weight docs 20% lower
```

Load configuration in your code:

```python
from braxis_config import BraxisConfig
from braxis_api import ContextGenerator

config = BraxisConfig.load(".braxis.yml")
generator = ContextGenerator(project_path=".", config=config)
result = generator.generate()
```

**See [.braxis.yml.example](.braxis.yml.example) for all options.**

---

## 🎯 Smart Triggering Logic (NEW in v1.1)

Automatically skip regenerating context files for trivial changes:

- ✅ Filters documentation-only changes (.md, .txt)
- ✅ Skips whitespace-only modifications
- ✅ Checks minimum line-change threshold
- ✅ Excludes configured patterns
- ✅ Detects meaningful changes vs noise

**Result:** Fewer CI runs, faster feedback, cleaner git history.

---

## Real-World Examples

### Onboarding New Team Members
```bash
$ braxis score
Agent Readiness: 78/100 (AI-Native-Plus)

# New dev immediately understands project quality baseline, conventions, and architecture
# Opens AGENTS.md in Claude Code → instant context
```

### Tracking Quality Improvements
```bash
$ braxis score
Score: 45/100

# After 2 weeks of improvements...
$ braxis history --trends
📈 +28 points (AI-Native)

# Team celebrates measurable progress
```

### Before Starting Major Refactor
```bash
$ braxis recommendations
# Get Claude AI's actionable suggestions
# Prioritize high-impact changes
# Measure progress with braxis history
```

---

## Requirements

- **Python** 3.8+ (works on macOS, Linux, Windows)
- **Zero dependencies** - Core features require nothing extra
- **Optional** - Install `braxis[llm]` for Claude recommendations

---

## Production Quality

Braxis enforces enterprise standards:

### Testing & Quality
- ✅ 57 unit tests covering all features (30 core + 27 API tests)
- ✅ 100% pass rate across Python 3.8-3.12
- ✅ Strict mypy type-checking (`disallow_untyped_defs`)
- ✅ ruff linting with E, W, F, I, UP, B, A, C4 rules
- ✅ GitHub Actions CI/CD on every push

### Safety & Reliability
- ✅ Input validation on all paths
- ✅ Atomic file writes (temporary files, no partial updates)
- ✅ Comprehensive error handling
- ✅ Path normalization
- ✅ Type-safe interface

### Code Quality
```bash
# Run all checks locally
make check

# Run individually:
make test           # Unit tests
make lint           # Type-check + lint
make format         # Auto-format
```

---

## Contributing

Braxis welcomes contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) for:

- Setup instructions
- Development workflow
- Testing guidelines
- Code style guide
- PR process
- Agent contribution boundaries

**Quick start:**
```bash
git clone https://github.com/jaykrishna316/braxis.git
cd braxis
pip install -e .
make check       # Verify setup
make test        # Run tests
```

---

## Community & Support

- **Issues** - [Report bugs or request features](https://github.com/jaykrishna316/braxis/issues)
- **Discussions** - [Ask questions, share ideas](https://github.com/jaykrishna316/braxis/discussions)
- **Contributing** - [Help improve Braxis](CONTRIBUTING.md)

---

## Customize For Your Project

Create `.agentic-config.json` in your repo root:

```json
{
  "name": "MyApp",
  "description": "Your app description",
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
    "src/api/routes.py"
  ]
}
```

---

## Roadmap

### Released: v1.4.0 ✅
- ✅ Dual-format AGENTS.md (Operations + Architecture)
- ✅ Auto-extract from CONTRIBUTING.md
- ✅ Production-tested on 27 to 22,679 file projects

### Released: v1.2.0 ✅
- ✅ Repository gotchas detection
- ✅ Subsystem ownership mapping
- ✅ Common mistakes identification

### Released: v1.1.0 ✅
- ✅ Hierarchical AGENTS.md for monorepos
- ✅ MCP server detection
- ✅ Project scale analysis

### Coming v1.5 (Q1 2027)
- 🚧 Preserve existing AGENTS.md
- 🚧 Multi-file strategies
- 🚧 Architecture Decision Records (ADRs)
- 🚧 Dependency graph visualization

[Have a feature request? Open an issue](https://github.com/jaykrishna316/braxis/issues/new)

---

## License

MIT - Free for personal and commercial use. [See LICENSE](LICENSE)

---

## The Bottom Line

AI agents need current context to work effectively. Braxis keeps your context automatically in sync with your code.

**One command. Always current. Production-grade. ✨**

---

Made with ❤️ by developers, for developers who use AI agents.

**Keep your agents aligned. Keep your code context current.**
