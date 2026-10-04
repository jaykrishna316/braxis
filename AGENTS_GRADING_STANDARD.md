# AGENTS.md Grading Standard

> **Community Standard for Evaluating AI Agent Guidance Quality**
>
> Version: 1.0 (October 2026)  
> Status: Open for Community Contribution  
> License: MIT (same as Braxis)

---

## Overview

AGENTS.md files are critical for AI agent effectiveness. This standard provides a **language-agnostic rubric** for evaluating AGENTS.md quality across 10 dimensions, each scored 0-10.

**Final Score = Average of all 10 dimensions** → 0-100 scale

### Score Tiers

| Score | Tier | Meaning | Emoji |
|-------|------|---------|-------|
| 90-100 | **Agent-Optimized** | Production-ready, comprehensive guidance | 🟢 |
| 80-89 | **Enterprise-Ready** | Excellent agent compatibility, minor gaps | 🟢 |
| 60-79 | **AI-Native** | Good agent support, some gaps | 🟡 |
| 30-59 | **Agent-Aware** | Basic agent compatibility | 🟠 |
| 0-29 | **Not Ready** | Needs significant improvements | 🔴 |

---

## Dimension 1: Command Execution & Clarity (0-10)

**What it measures**: How clear and easy are the development commands?

### Scoring Rubric

- **10/10** — Single-word make targets (e.g., `make test`, `make lint`) with help text
- **9/10** — Clear, standard commands (e.g., `pytest`, `npm test`) with unified entrypoint
- **8/10** — Mix of clear + complex commands (e.g., `uv run pytest` + `prek run`)
- **7/10** — Multiple approaches, some require explanation
- **5/10** — Commands documented but unclear or fragmented
- **2/10** — Minimal command guidance
- **0/10** — No command documentation

### Evaluation Checklist

- [ ] Testing command documented and clear
- [ ] Linting command documented and clear
- [ ] Type-checking command documented
- [ ] Code formatting command documented
- [ ] Single unified entrypoint exists (optional but scores higher)
- [ ] Help text explains each target/command
- [ ] No virtualenv complexity exposed to user

### Reference Benchmarks

| Repo | Score | Command | Notes |
|------|-------|---------|-------|
| **Braxis** | **9/10** | `make test`, `make lint` | Single-word, abstracts environment |
| FastAPI | 9/10 | `uv run pytest`, `uv run mypy` | Clear but requires uv knowledge |
| Sentry | 8/10 | `prek run`, `prek run -q` | Abstracted but less discoverable |
| Airflow | 7/10 | `breeze run pytest`, complex flags | Requires Breeze knowledge |

---

## Dimension 2: Type-Checking Coverage (0-10)

**What it measures**: Are type hints required and enforced?

### Scoring Rubric

- **10/10** — 100% of public methods typed + strict mypy mode enforced
- **9/10** — 90%+ of public API typed, strict mode, config documented
- **8/10** — 70%+ typed, strict mode optional or warnings allowed
- **7/10** — 50%+ typed, mypy configured but not strict
- **5/10** — Type hints present but not enforced
- **2/10** — Type hints partially documented
- **0/10** — No type hints or enforcement

### Evaluation Checklist

- [ ] All public method signatures have return types
- [ ] Instance variables typed
- [ ] mypy strict mode documented or enforced
- [ ] Type checking tool specified (mypy, pyright, etc.)
- [ ] Type checking integrated into CI/CD
- [ ] Python version compatibility documented (e.g., 3.8+)

### Reference Benchmarks

| Repo | Score | Coverage | Notes |
|------|-------|----------|-------|
| **Braxis** | **9/10** | 12+ public methods, 100% of public API | mypy.ini strict = true |
| FastAPI | 10/10 | Entire codebase, strict mode | Industry standard |
| Airflow | 8/10 | Per-distribution, some exemptions | Complex codebase |
| Sentry | 9/10 | Core + API layers | Partial coverage |

---

## Dimension 3: Unified Linting Entrypoint (0-10)

**What it measures**: Is there a single command to verify code quality?

### Scoring Rubric

- **10/10** — Single command runs mypy + linter + formatter check
- **9/10** — Single command combines 2+ quality tools
- **8/10** — Separate commands clear and well-documented
- **7/10** — Commands documented but not unified
- **5/10** — Linting mentioned but process unclear
- **2/10** — Minimal linting guidance
- **0/10** — No linting guidance

### Evaluation Checklist

- [ ] Unified linting command exists and documented
- [ ] Command includes: type-checking, linting, formatting
- [ ] Linting tool specified (ruff, pylint, eslint, etc.)
- [ ] Formatter specified (black, prettier, ruff, etc.)
- [ ] All checks documented with expected results
- [ ] "Is my code ready?" answerable with one command

### Reference Benchmarks

| Repo | Score | Command | Coverage |
|------|-------|---------|----------|
| **Braxis** | **9/10** | `make lint` | mypy + ruff check + ruff format |
| Sentry | 9/10 | `prek run -q` | Single command, wrapped |
| FastAPI | 8/10 | Separate: `uv run mypy`, `uv run ruff` | Clear but not unified |
| Airflow | 7/10 | `prek run --from-ref main` | Complex flags |

---

## Dimension 4: Agent Boundaries Documentation (0-10)

**What it measures**: How explicit are the limits of agent contributions?

### Scoring Rubric

- **10/10** — 5+ "CAN DO" categories + 8+ "MUST NOT" patterns, each with rationale
- **9/10** — 4-5 "CAN DO" + 6-7 "MUST NOT" with clear examples
- **8/10** — Clear boundaries stated, some implicit
- **7/10** — Boundaries mentioned but not comprehensive
- **5/10** — Some boundaries documented
- **2/10** — Implicit boundaries only
- **0/10** — No boundary documentation

### Evaluation Checklist

- [ ] "What agents CAN do" section exists with examples
- [ ] "What agents MUST NOT do" section exists with impact analysis
- [ ] Each boundary includes rationale (why it matters)
- [ ] Examples provided for safe and unsafe patterns
- [ ] Edge cases documented
- [ ] File paths and scope clearly defined

### Reference Benchmarks

| Repo | Score | CAN DO | MUST NOT | Quality |
|------|-------|--------|----------|---------|
| **Braxis** | **10/10** | 5 patterns | 8 patterns | With impact analysis |
| Sentry | 9/10 | 4 patterns | 6 patterns | Some implicit |
| FastAPI | 9/10 | 3 patterns | 5 patterns | Clear but brief |
| Airflow | 8/10 | Architectural boundaries | 4 patterns | Mostly implicit |

---

## Dimension 5: Architecture Documentation (0-10)

**What it measures**: How well is the codebase structure explained?

### Scoring Rubric

- **10/10** — Components documented + diagrams + data flow + principles
- **9/10** — Core components documented + design principles + structure
- **8/10** — Main components documented with basic structure
- **7/10** — Structure documented but missing component details
- **5/10** — Basic architecture explanation
- **2/10** — Minimal structure documentation
- **0/10** — No architecture documentation

### Evaluation Checklist

- [ ] Core components listed and described
- [ ] Design principles documented (e.g., zero-dependency, modularity)
- [ ] Directory structure explained
- [ ] Key design patterns noted
- [ ] Data flow explained (optional but scores higher)
- [ ] Architectural diagrams present (optional but scores higher)
- [ ] 16+ lines of substantive architecture content

### Reference Benchmarks

| Repo | Score | Sections | Notes |
|------|-------|----------|-------|
| **Braxis** | **8/10** | Components + Principles + Structure | No diagrams yet |
| Sentry | 9/10 | Multi-tenant, Silo, Hybrid cloud | With diagrams |
| Airflow | 9/10 | Scheduler/Worker/Processor | Clear boundaries |
| FastAPI | 8/10 | Minimal (single-package) | Still comprehensive |

---

## Dimension 6: PR Checklist & Done Criteria (0-10)

**What it measures**: Are "done" criteria clear and numbered?

### Scoring Rubric

- **10/10** — 8+ numbered checklist items with clear completion criteria
- **9/10** — 6-7 items, well-defined, some with automation hints
- **8/10** — 5-6 items, clear but could be more specific
- **7/10** — Checklist present but vague
- **5/10** — Done criteria mentioned but not formalized
- **2/10** — Minimal guidance
- **0/10** — No PR checklist

### Evaluation Checklist

- [ ] Numbered list (not bullets) of "done" criteria
- [ ] Tests mentioned with command
- [ ] Type-checking mentioned with command
- [ ] Linting mentioned with command
- [ ] Code formatting mentioned with command
- [ ] Backward compatibility mentioned
- [ ] No external dependencies mentioned (if applicable)
- [ ] Commit attribution/message format mentioned

### Reference Benchmarks

| Repo | Score | Items | Format |
|------|-------|-------|--------|
| **Braxis** | **9/10** | 8 items | Numbered checklist |
| Sentry | 9/10 | 10+ items | Some implicit |
| FastAPI | 8/10 | ~5 items | Scattered across docs |
| Airflow | 8/10 | 6 items | Newsfragments required |

---

## Dimension 7: CI/CD Enforcement (0-10)

**What it measures**: Are quality checks automatically enforced?

### Scoring Rubric

- **10/10** — All checks (tests, lint, type, format) enforced in CI; blocks PRs
- **9/10** — Most checks (3+ of 4) enforced; blocks PRs
- **8/10** — Multiple checks enforced; results visible in PR
- **7/10** — Some checks automated; not all blocking
- **5/10** — Checks documented but not automated
- **2/10** — Minimal CI/CD setup
- **0/10** — No CI/CD

### Evaluation Checklist

- [ ] GitHub Actions (or CI system) configured
- [ ] Tests run on every push/PR
- [ ] Type-checking runs in CI
- [ ] Linting runs in CI
- [ ] Code formatting checked in CI
- [ ] Multiple Python versions tested (if applicable)
- [ ] CI failures block PR merge
- [ ] CI config documented in AGENTS.md

### Reference Benchmarks

| Repo | Score | Coverage | Matrix |
|------|-------|----------|--------|
| **Braxis** | **8/10** | Python 3.8-3.12, all checks | 5 versions |
| Sentry | 9/10 | Multiple job types | Extensive |
| Airflow | 9/10 | Extensive matrix testing | Very comprehensive |
| FastAPI | 8/10 | Basic CI | Limited matrix |

---

## Dimension 8: Anti-Patterns & Never-Do Guidance (0-10)

**What it measures**: Are dangerous patterns explicitly documented?

### Scoring Rubric

- **10/10** — 10+ "Never Do" patterns with impact analysis
- **9/10** — 8-9 patterns with rationale and examples
- **8/10** — 6-7 patterns documented clearly
- **7/10** — 5-6 patterns with some explanation
- **5/10** — Anti-patterns mentioned but incomplete
- **2/10** — Few anti-patterns documented
- **0/10** — No anti-pattern guidance

### Evaluation Checklist

- [ ] "Never Do" section exists
- [ ] At least 8 patterns documented
- [ ] Each pattern includes: description, why it matters, impact
- [ ] Examples of correct vs incorrect approaches provided
- [ ] Pattern covers common pitfalls (dependencies, breaking changes, etc.)
- [ ] Rationale explains real-world consequences

### Reference Benchmarks

| Repo | Score | Count | Quality |
|------|-------|-------|---------|
| **Braxis** | **10/10** | 10 patterns | With impact analysis |
| Sentry | 9/10 | 10 patterns | Some implicit |
| FastAPI | 9/10 | 9 patterns | Clear but brief |
| Airflow | 8/10 | 9 patterns | Mostly implicit |

---

## Dimension 9: Example Quality & Concrete Code (0-10)

**What it measures**: Are real, runnable examples provided?

### Scoring Rubric

- **10/10** — 5+ real code examples with before/after patterns
- **9/10** — 4 concrete examples with test cases
- **8/10** — 3 substantive examples with explanations
- **7/10** — Some code examples, could be more detailed
- **5/10** — Basic examples, limited coverage
- **2/10** — Minimal examples
- **0/10** — No code examples

### Evaluation Checklist

- [ ] Language/framework detection examples
- [ ] Test patterns shown
- [ ] Before/after code examples
- [ ] Examples match actual project style
- [ ] Examples include command to run/test
- [ ] Common mistakes illustrated with correction

### Reference Benchmarks

| Repo | Score | Examples | Coverage |
|------|-------|----------|----------|
| **Braxis** | **8/10** | Language + framework detection | Good starter patterns |
| Sentry | 9/10 | API endpoints + Celery tasks | Production patterns |
| FastAPI | 9/10 | Dependency injection + validation | Framework-specific |
| Airflow | 8/10 | Custom operators + decorators | Distributed patterns |

---

## Dimension 10: Overall Developer Guidance Quality (0-10)

**What it measures**: Is the entire AGENTS.md coherent and actionable?

### Scoring Rubric

- **10/10** — Comprehensive, clear, actionable, well-organized
- **9/10** — Very good guidance with minor gaps
- **8/10** — Good guidance, some areas could expand
- **7/10** — Adequate guidance with notable gaps
- **5/10** — Basic guidance, significant gaps
- **2/10** — Incomplete or confusing
- **0/10** — Unhelpful or missing

### Evaluation Checklist

- [ ] File is 300+ lines (substantial content)
- [ ] Sections are clearly organized with headers
- [ ] Table of contents or navigation present
- [ ] Language is clear and unambiguous
- [ ] No contradictions between sections
- [ ] New developers can onboard using AGENTS.md alone
- [ ] Commands are copy-pasteable
- [ ] Links to relevant files/sections work

### Holistic Questions

1. **Could a new developer contribute effectively using just this AGENTS.md?**
2. **Are edge cases and gotchas covered?**
3. **Does it feel like a real operations manual vs. theoretical?**
4. **Are there obvious gaps or missing sections?**
5. **Would an AI agent find it helpful and clear?**

---

## How to Grade an AGENTS.md File

### Step 1: Read Thoroughly
Read the entire AGENTS.md file once to get the big picture.

### Step 2: Score Each Dimension
For each of the 10 dimensions:
- Review the scoring rubric
- Check the evaluation checklist
- Compare against reference benchmarks
- Assign a score (0-10)

### Step 3: Calculate Average
```
Overall Score = (Dim1 + Dim2 + ... + Dim10) / 10
```

### Step 4: Identify Gaps
Note which dimensions scored lowest and why:
- Missing content?
- Unclear presentation?
- Incomplete examples?

### Step 5: Generate Recommendations
For each dimension below 8/10, suggest concrete improvements.

---

## Using Braxis Grade Command

### Installation
```bash
pip install braxis[grade]  # Or: braxis upgrade
```

### Basic Usage
```bash
# Grade your project's AGENTS.md
braxis grade

# Grade specific file
braxis grade path/to/AGENTS.md

# Show comparison with benchmarks
braxis grade --compare

# Output as JSON
braxis grade --json

# Show detailed breakdown
braxis grade --verbose
```

### Example Output
```
═══════════════════════════════════════════════════════════════
AGENTS.md Grade Report: my-project
═══════════════════════════════════════════════════════════════

Overall Score: 78/100 🟢 Enterprise-Ready

Dimension Scores:
  1. Command Execution         [████████░░] 9/10 ⭐
  2. Type-Checking             [████████░░] 9/10 ⭐
  3. Unified Linting           [████████░░] 9/10 ⭐
  4. Agent Boundaries          [██████████] 10/10 ⭐⭐
  5. Architecture Docs         [████████░░] 8/10
  6. PR Checklist              [████████░░] 9/10 ⭐
  7. CI/CD Enforcement         [████████░░] 8/10
  8. Anti-Patterns             [██████████] 10/10 ⭐⭐
  9. Example Quality           [████████░░] 8/10
 10. Overall Guidance          [████████░░] 9/10 ⭐

Comparison:
  Sentry (83/100)     -5 points
  FastAPI (81/100)    -3 points
  Braxis (78/100)      =  (baseline)
  Airflow (72/100)    +6 points

Top Strengths:
  • Agent Boundaries (10/10) — Explicit "CAN DO" + "MUST NOT"
  • Anti-Patterns (10/10) — Clear "Never Do" with impact analysis
  • Command Clarity (9/10) — Make targets are excellent

Areas for Improvement:
  1. Add architecture diagrams (+2 points → 80/100)
  2. Expand internal method type hints (+1 point → 79/100)
  3. Add coverage reporting integration (+2 points → 80/100)

Next Steps:
  Read: AGENTS_GRADING_STANDARD.md for improvement details
  Run: braxis grade --recommendations for AI-powered suggestions
```

---

## Contributing to This Standard

### Proposing New Dimensions

Submit a GitHub issue with:
- **Dimension Name** (4-5 words)
- **Why It Matters** (paragraph explaining value)
- **Scoring Rubric** (0-10 scale with checkpoints)
- **Reference Examples** (at least 2 projects)
- **Evaluation Checklist** (4-8 items)

### Improving Existing Dimensions

Submit a pull request with:
- **Which Dimension** you're improving
- **What's changing** (clarity, scoring adjustments, etc.)
- **Why** (feedback from grading projects)
- **Before/After Examples** (show the improvement)

---

## Version History

### v1.0 (October 2026)
- Initial release with 10 dimensions
- Benchmarked against FastAPI, Airflow, Sentry
- Braxis achieves 78/100 on own standard

---

## FAQ

### Q: Can I use this to grade CONTRIBUTING.md or README.md?
**A:** This standard is specifically for AGENTS.md (AI agent guidance). Similar standards could be created for other documentation types.

### Q: What if my project has multiple AGENTS.md files (monorepo)?
**A:** Grade each file separately, then calculate root score as weighted average:
```
overall = (root_score * 0.4) + avg(subsystem_scores) * 0.6
```

### Q: How often should I re-grade my AGENTS.md?
**A:** After major changes, quarterly reviews recommended. Use `braxis history` to track scores over time.

### Q: Is this prescriptive or flexible?
**A:** This standard is **flexible by design**. Use the dimensions that fit your project type. A single-file CLI tool may not need "Monorepo Guidance," for example.

---

## License

This standard is published under MIT license, the same as Braxis.

Free to use, adapt, and extend in any project.

---

**Questions or feedback?** Open an issue: https://github.com/jaykrishna316/braxis/issues

Made with ❤️ for better AI agent guidance.
