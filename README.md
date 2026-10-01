# Braxis

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

## Make It Auto-Update (Optional)

Create `.github/workflows/braxis.yml`:

```yaml
name: Auto-Regenerate Context Files

on:
  push:
    paths:
      - 'src/**'
      - 'lib/**'
      - 'package.json'
      - 'pyproject.toml'
      - 'setup.py'

jobs:
  regenerate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install braxis
      - run: braxis generate
      - uses: peter-evans/create-pull-request@v5
        with:
          commit-message: "chore: regenerate context files"
          title: "chore: update AGENTS.md and context files"
          branch: braxis/auto-update
```

Now every time you push code, GitHub Actions automatically regenerates all context files.

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

## Commands

```bash
braxis score                          # Score agent readiness (0-100)
braxis score --path /path/to/project  # Score a specific project
braxis generate                       # Generate context files
braxis inspect                        # See what Braxis found
braxis validate                       # Verify AGENTS.md exists
```

---

## Safety & Reliability

Braxis includes robust error handling and data safety features:

- **Input Validation** - Validates project paths and file inputs with clear error messages
- **Atomic File Writing** - Uses temporary files and atomic operations to prevent partial writes
- **Error Handling** - Comprehensive error handling with informative feedback
- **Tested** - 30+ unit tests covering all major functionality

---

## Requirements

- Python 3.8+
- Zero external dependencies

---

## License

MIT

---

**Braxis** — Keep your agents aligned. Keep your code context current.