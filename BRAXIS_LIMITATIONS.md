# Braxis 2.0: Limitations & Honest Assessment

## Overview

Braxis 2.0 is a powerful AI agent context and analysis platform, but it has clear boundaries and limitations. This document outlines what Braxis does well, what it cannot do, and where external tools may be better suited.

---

## Core Limitations

### 1. **Framework Detection is Pattern-Based, Not AST-Based**

**Limitation:** Braxis detects frameworks by scanning for imports and filenames, not by parsing the Abstract Syntax Tree (AST).

**Impact:**
- False positives: A project with `requirements.txt` mentioning `flask` in a comment might be flagged as using Flask
- False negatives: Custom framework wrappers that don't directly import the parent framework may be missed
- No detection of version-specific features (e.g., FastAPI 0.95 vs 0.100 behavior changes)

**When to use alternatives:**
- For precise AST-based analysis: Use `tree-sitter` or `ast` module directly
- For vendored/monorepo frameworks: Consider `LibCST` for deeper code inspection
- For version-specific linting: Use `ruff` or `pylint` with language server protocol (LSP)

**Example gap:** A project using an internal `my_fastapi_wrapper` module won't be detected as FastAPI even if it imports and extends FastAPI internally.

---

### 2. **Security Scanning is Heuristic-Based**

**Limitation:** Braxis security scanning relies on regex patterns and simple string matching, not semantic analysis.

**Current Coverage:**
- ✓ SQL injection via string concatenation (basic patterns)
- ✓ Hardcoded credentials (regex for common secret patterns)
- ✓ Pickle usage in untrusted contexts (import detection)
- ✓ Command injection via `os.system()` (direct calls)

**Gaps:**
- ✗ Context-aware SQL injection (doesn't understand SQLAlchemy parameterization, prepared statements)
- ✗ Encrypted credential detection (base64, ROT13, or other obfuscation)
- ✗ Transitive vulnerabilities (doesn't track dependency chains deeply)
- ✗ LDAP injection, XPath injection, template injection (not implemented)
- ✗ Second-order SQL injection (doesn't track data flow)

**When to use alternatives:**
- **Production security scanning:** Use Semgrep, CodeQL, or Bandit
  - Semgrep: 1000+ community rules, semantic analysis, faster iteration
  - CodeQL: GitHub-native, catches complex data-flow vulnerabilities
  - Bandit: Python-specific, well-maintained, industry standard
- **Compliance scanning:** Use OWASP Dependency-Check or Snyk for transitive deps
- **Container security:** Use Trivy or Grype for image vulnerability scanning

**Why Braxis doesn't replace them:** Security is too critical for heuristics; false negatives can be catastrophic. Braxis is a first-pass gate, not a security tool.

---

### 3. **Complexity Estimation Formula is Unvalidated**

**Limitation:** The complexity-based onboarding duration formula has not been empirically validated against real team data.

**Current Formula Logic:**
```
Simple:      < 10 py files, < 30 total files      → 3 days
Moderate:    < 50 py files, < 100 total files     → 7 days
Complex:     < 200 py files, < 300 total files    → 14 days
Enterprise:  ≥ 200 py files, ≥ 300 total files    → 21 days

Bump if CI/CD detected:  SIMPLE → MODERATE, MODERATE → COMPLEX
```

**Limitations:**
- No correlation study vs actual onboarding time
- Doesn't account for: team experience, documentation quality, test coverage, domain complexity
- File count is a proxy, not a direct cause (500 small files ≠ 500 large files)
- Domain-specific factors ignored (biotech onboarding >> typical CRUD app)
- Threshold values (10, 50, 200 py files) chosen arbitrarily

**Real-world variance:** A "MODERATE" complexity project might take 3 days for a senior engineer or 21 days for a junior contractor—formula averages over population.

**When to trust Braxis estimates:**
- ✓ Relative comparisons (Project A is "more complex" than Project B)
- ✓ Baseline scoping (order-of-magnitude estimates for project planning)
- ✓ Detection of CI/CD overhead (CI/CD does add onboarding time)

**When NOT to trust:**
- ✗ As a hiring timeline without human review
- ✗ As a bottleneck for sprint planning
- ✗ For domains where Braxis has no training data

**Next validation step:** See engineering backlog item #1 (collect data from 20+ real projects).

---

### 4. **Code Quality ROI Calculation is Gap-Based, Not Cost-Benefit Analyzed**

**Current Formula:**
```
ROI = (target_score - current_score) / 10
```

**Limitations:**
- Doesn't account for effort to reach target (refactoring 500 files != refactoring 50)
- Doesn't model financial benefit (does 10% code quality improvement = 10% fewer bugs?)
- Treats all code equally (test file quality ≠ production code quality)
- Doesn't track velocity trade-off (stopping feature work to refactor)
- No diminishing returns modeling (first 10% easier than last 10%)

**When to use Braxis ROI:**
- ✓ Identifying which areas have highest improvement potential
- ✓ Communicating improvement priorities to team
- ✓ Relative prioritization within a single codebase

**When NOT to use:**
- ✗ Justifying budget to executives (use CodeScene or industry benchmarks)
- ✗ Setting team SLAs (use actual failure data + cost modeling)
- ✗ Comparing ROI across different codebases (normalize factors first)

---

### 5. **Natural Language Code Queries Depend on Claude API**

**Limitation:** NLQ feature is a wrapper around Claude's code understanding, not a proprietary analysis engine.

**Current behavior:**
- Takes natural language question + code context
- Sends to Claude API (requires API key, incurs costs)
- Returns Claude's response

**Limitations:**
- API cost: ~$0.003 per query at Claude Haiku rates (scales with context size)
- Rate-limited by Anthropic's API quotas
- No local execution (requires internet connectivity)
- No built-in caching for repeated queries
- Latency: Typical 2-5 second response time (not real-time)

**Competitive gap:** Tools like GitHub Copilot integrate local code understanding without external APIs.

**When to use Braxis NLQ:**
- ✓ One-off exploratory queries
- ✓ Complex semantic questions (not keyword matching)
- ✓ When Claude's instruction-following matters

**When to use alternatives:**
- **Local semantic search:** Use `tree-sitter` + `tree-sitter-queries` for pure local indexing
- **Code graph RAG:** Use `Understand-Anything` or `Code-Graph-RAG` for local embedding + retrieval
- **IDE integration:** Use GitHub Copilot, Cursor, or Codeium for real-time understanding

---

### 6. **Organization Aggregator Assumes Consistent Repo Structure**

**Limitation:** The aggregator expects similar directory/file layouts across repositories.

**Limitations:**
- Doesn't normalize monorepo structures (can't compare `packages/web` vs `src/web` across repos)
- Assumes Python-first repos (Go/Rust/Node repos will undercount)
- Polyglot project metrics are imprecise (counts .py files but not .go, .ts)
- No multi-language weighting

**Example:** An organization with 50% Go, 50% Python codebases will show skewed metrics if all repos are measured by Python file count.

**When to use aggregator:**
- ✓ Trend-tracking within a single organization using consistent structure
- ✓ Relative ranking (which team's codebase is most complex)
- ✓ Portfolio analysis for Python-heavy organizations

**When NOT to use:**
- ✗ Comparing polyglot organizations
- ✗ Cross-organization benchmarking without normalization
- ✗ Making hiring/resource decisions based on raw counts

---

### 7. **Agent Performance Telemetry Measures Symptoms, Not Root Causes**

**Limitation:** Braxis tracks whether an agent succeeded, but not *why*.

**Current tracking:**
- Task completion rate (succeeded/failed)
- Time to first solution
- Context relevance score
- Token usage

**What's missing:**
- Why did the agent fail? (insufficient context, wrong framework detection, unclear requirements)
- What caused the delay? (large codebase, poor naming, missing tests)
- Did the agent's solution actually work in production? (can't observe downstream)
- Human intervention bias (did a human fix the agent's partial solution?)

**When to use Braxis telemetry:**
- ✓ Identifying high-variance tasks (tasks where agents sometimes struggle)
- ✓ Detecting framework-specific problems (all FastAPI tasks at 60% success)
- ✓ Monitoring for telemetry regression (is context relevance declining?)

**When NOT to use:**
- ✗ Optimizing agent prompts without root cause analysis
- ✗ Comparing agents across different task distributions
- ✗ Making go/no-go decisions on new features

---

### 8. **Real Analysis Still Misses Custom Patterns**

**Limitation:** Braxis detects common frameworks and patterns, but not custom architectures.

**Examples:**
- Custom ORM built on top of SQLAlchemy (won't be detected as ORM)
- Internal test framework mimicking pytest (won't be detected as test framework)
- Monorepo with internal package manager (will be counted as single project)
- Microservices with non-standard service discovery (won't be detected)

**When to use Braxis analysis:**
- ✓ First-pass understanding of standard Python projects
- ✓ Detecting framework/library presence
- ✓ Identifying code organization patterns

**When to do manual analysis:**
- ✗ Custom internal frameworks (no substitute for reading code)
- ✗ Complex monorepo structures (requires domain knowledge)
- ✗ Systems with unusual architectural patterns

---

## What Braxis Does **Not** Do

### By Design
- ✗ Replace code review (doesn't understand intent or context)
- ✗ Enforce security compliance (security should be gated separately)
- ✗ Generate tests automatically (requires understanding of requirements)
- ✗ Refactor code (requires careful testing and human judgment)
- ✗ Deploy code (that's CI/CD's job)

### Out of Scope
- ✗ Database schema analysis (would require connection/schema inspection)
- ✗ Runtime performance profiling (requires execution)
- ✗ Infrastructure cost analysis (requires cloud API access)
- ✗ Team velocity metrics (requires project management tool integration)
- ✗ User behavior analytics (requires analytics platform integration)

---

## Recommended Tool Combinations

### For Production Security Gate
```
Braxis (first pass) → Semgrep (depth) → CodeQL (complexity) → OWASP DC (dependencies)
```

### For Complete Code Quality View
```
Braxis (real analysis) + Codacy (persistence) + CodeScene (trends) + SonarQube (gates)
```

### For Agent-Ready Context
```
Braxis (analysis) + Claude API (semantic queries) + tree-sitter (AST navigation)
```

### For Organization Metrics
```
Braxis (per-repo) + Codacy/LinearB (aggregate + visualization) + custom dashboards
```

---

## Validation Status

| Feature | Status | Confidence |
|---------|--------|-----------|
| Framework detection | Implemented | 75% (heuristic-based) |
| CI/CD detection | Implemented | 85% (pattern-matched) |
| Complexity estimation | Implemented | 55% (unvalidated formula) |
| Security scanning | Implemented | 60% (heuristic-based) |
| Code quality ROI | Implemented | 50% (gap-based, unvalidated) |
| Natural language queries | Implemented | 80% (delegates to Claude) |
| Onboarding plans | Implemented | 45% (complexity-dependent) |
| ADR generation | Implemented | 65% (pattern-matched) |

---

## Contributing Validation Data

If you're using Braxis 2.0 in production, please contribute to:

1. **Complexity Formula Validation:** Report actual onboarding time vs predicted time
2. **Security Scanning Accuracy:** Report false positives/negatives found
3. **Context Relevance:** Measure whether Braxis context improves agent task success
4. **ROI Predictions:** Track whether recommended improvements actually reduced issues

---

## Summary

Braxis 2.0 is best used as:
- **A first-pass analyzer** (not a final authority)
- **A contextualizer for AI agents** (not a replacement for agents)
- **A trend detector** (not an anomaly detector)
- **A baseline scorer** (not a certification)

For critical decisions (security, compliance, architecture), always supplement Braxis analysis with domain-specific tools and human review.

---

*Last updated: 2026-10-09*
*Confidence levels reflect engineering assessment; actual validation ongoing per backlog item #1, #2, #3*
