# Braxis

**The axis of agent knowledge. Keep your agents aligned as your codebase evolves.**

When you use AI agents in your workflow, they read from `AGENTS.md` on day 1. Then your codebase evolves. That file becomes stale. Agents hallucinate, miss patterns, violate conventions they no longer see.

Braxis solves this by auto-generating and keeping in sync four instruction files that AI agents read:

- **`AGENTS.md`** — Universal agent context (read by 20+ AI tools)
- **`CLAUDE.md`** — Claude Code optimized variant
- **`.cursorrules`** — Cursor IDE specific rules
- **`.agentic-config.json`** — Machine-readable metadata

Runs on CI/CD. Zero external dependencies. Your agents always work from current truth.

## The Problem

Imagine this workflow:

Day 1: Agent A reads AGENTS.md → Learns your codebase
Day 5: You refactor src/ directory → AGENTS.md becomes outdated
Day 6: Agent B starts → Reads stale AGENTS.md
Result: Agents disagree on conventions, miss patterns, coordination breaks

In multi-agent systems (like Neo), this gets exponentially worse. One agent's stale context breaks the coordination protocol another agent depends on.

## The Solution

Braxis runs on every code change and regenerates your context files automatically.

Every push: Braxis analyzes repo → Regenerates AGENTS.md, CLAUDE.md, .cursorrules
Result: All agents always see current truth

## Quick Start (5 minutes)
1. Install

pip install braxis

2. Run

braxis generate

3. Commit

git add AGENTS.md CLAUDE.md .cursorrules .agentic-config.json
git commit -m "chore: add agent context files"
git push


This creates four files that your AI tools will read automatically.

## Usage
Generate all context files

braxis generate

Score your repo's agent readiness (0-100)

braxis score

See what Braxis found about your repo

braxis inspect

Validate that AGENTS.md exists

braxis validate


## Auto-Regenerate on Every Push (Optional)

Copy this to `.github/workflows/braxis.yml` in your repo:

name: Regenerate Context Files

on:
push:
paths:
- 'src/**'
- 'package.json'
- 'pyproject.toml'

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
title: "chore: update AGENTS.md and related files"


Now on every code push, GitHub Actions will auto-regenerate your context files. Your agents always see current reality.

## What Gets Generated

AGENTS.md (Universal)
Universal instructions for any AI agent reading your repo.

CLAUDE.md (Claude Code Optimized)
Concise summary optimized for Claude's context budget.

.cursorrules (Cursor IDE)
Rules that guide Cursor's AI when editing your code.

.agentic-config.json (Machine Readable)
Metadata in JSON format for automated systems.

## Customize (Optional)

Create `.agentic-config.json` to override defaults:

{
"name": "My Project",
"description": "What it does",
"custom_conventions": {
"error_handling": "Use Result pattern",
"async_patterns": "asyncio preferred"
},
"critical_files": [
"src/main.py",
"src/core.py"
]
}


## Why This Matters

For Solo Developers: Your Claude Code / Cursor / Copilot sessions always see current context.

For Teams: All developers' AI assistants see the same ground truth about the codebase.

For Multi-Agent Systems: Agents can trust each other's context. Coordination protocols work reliably.

## Installation
From PyPI

pip install braxis

From source

git clone https://github.com/jaykrishna316/braxis
cd braxis
pip install -e .


## Requirements

- Python 3.8+
- Zero external dependencies

## FAQ

Q: Does Braxis run my code?
A: No. Static analysis only. Safe to run anywhere.

Q: Can I customize what gets generated?
A: Yes. Create `.agentic-config.json` in your repo root.

Q: Can I use this with Claude / Cursor / Copilot?
A: Yes. Braxis generates files for all of them.

Q: How do I keep files in sync?
A: Copy `.github/workflows/braxis.yml` to your repo. GitHub Actions will auto-regenerate on every code change.

## License

MIT - Use, modify, and ship it freely.

---

Braxis — The axis of agent knowledge. Keep your agents aligned.
