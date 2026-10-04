# Top 10 Repositories - AGENTS.md Quality Analysis

**Date**: October 4, 2026  
**Standard**: AGENTS_GRADING_STANDARD.md (v1.0)  
**Methodology**: 10-dimension rubric, 0-100 scoring scale

---

## ⚠️ Methodology Note: Fair vs. Unfair Comparisons

**Important**: This analysis has a **methodological flaw** we're now addressing through Phase 1 bias reduction.

### The Problem
- **7 of 10 repositories DO NOT have formal AGENTS.md files**
- Django, Airflow, Kubernetes, TensorFlow, React scored 65-78 not because guidance is bad, but because it's *scattered across existing docs*
- Comparing "repos with AGENTS.md" vs "repos without AGENTS.md" is like grading essay quality when some submissions aren't essays

### Fair Comparison (Only Repos with AGENTS.md)
These 3 projects have formal AGENTS.md or equivalent guidance files:

| Rank | Repository | Score | Fair to Compare? |
|------|------------|-------|------------------|
| 1 | **Braxis** | 93/100 | ✅ Yes - AGENTS.md pioneer |
| 2 | **Sentry** | 83/100 | ✅ Yes - formal agent guidance |
| 3 | **FastAPI** | 81/100 | ✅ Yes - clear agent patterns |

*This is the only fair comparison. Braxis scores highest among repos with formal AGENTS.md files.*

### "AI Readiness Score" (All 10 Repos)
These 7 projects have excellent agent guidance **but scattered across existing docs**:

| Rank | Repository | Score | Why Scored Lower |
|------|------------|-------|------------------|
| 4 | **Django** | 78/100 | No consolidated AGENTS.md (guidance in CONTRIBUTING.md, etc.) |
| 5 | **Next.js** | 75/100 | Setup docs embedded in Next.js site |
| 6 | **Vue.js** | 72/100 | Contributing guide but no agent boundaries |
| 5 | **Airflow** | 72/100 | Complex guidance (Breeze, architecture docs scattered) |
| 8 | **Kubernetes** | 70/100 | Multiple docs (API conventions, extension model) |
| 9 | **TensorFlow** | 68/100 | Contribution docs + API patterns |
| 10 | **React** | 65/100 | Minimal formal agent guidance |

*These scores reflect "AI readiness" (likelihood someone finds agent guidance), not actual quality.*

### v1.1 Will Propose
- Separate scoring: Track A (AGENTS.md quality) vs. Track B (AI readiness)
- Reweight dimensions for language fairness
- Fair comparison results once methodology is validated by external experts

See [EXPERT_REVIEW_FRAMEWORK.md](../EXPERT_REVIEW_FRAMEWORK.md) for how to provide feedback.

---

## 📊 Current Rankings (v1.0 - Pre-Review)

| Rank | Repository | Score | Tier | Strengths | Gaps |
|------|------------|-------|------|-----------|------|
| 🥇 1 | **Braxis** | **93/100** | 🟢 Agent-Optimized | Agent boundaries (10/10), Anti-patterns (10/10), Examples (10/10) | Architecture diagrams |
| 🥈 2 | **Sentry** | **83/100** | 🟢 Enterprise-Ready | Architecture (diagrammed), Multi-tenant patterns, CI/CD | Agent boundaries less explicit |
| 🥉 3 | **FastAPI** | **81/100** | 🟢 Enterprise-Ready | Type-checking strict, Clear commands, Examples | Less explicit agent boundaries |
| 4 | **Django** | **78/100** | 🟡 AI-Native | Mature docs, Testing patterns, Comprehensive | Anti-patterns scattered |
| 5 | **Airflow** | **72/100** | 🟡 AI-Native | Architecture clarity, CI/CD integration | Complex, fragmented guidance |
| 6 | **Next.js** | **75/100** | 🟡 AI-Native | Command clarity, Modern setup, Examples | Limited agent boundaries |
| 7 | **Vue.js** | **72/100** | 🟡 AI-Native | Type hints, Testing docs, Clear structure | Could expand anti-patterns |
| 8 | **Kubernetes** | **70/100** | 🟡 AI-Native | Architecture (detailed), Extensibility docs | Agent boundaries missing |
| 9 | **TensorFlow** | **68/100** | 🟡 AI-Native | Setup instructions, Examples, Type-checking | Scattered guidance, unclear boundaries |
| 10 | **React** | **65/100** | 🟡 AI-Native | Examples (React-specific), Type support | No explicit AGENTS.md, minimal guidance |

---

## 🎯 Detailed Scores by Dimension

### Dimension 1: Command Execution & Clarity

| Repo | Score | Why |
|------|-------|-----|
| **Braxis** | 9/10 | Make targets (test, lint, format, check) |
| **FastAPI** | 9/10 | `uv run pytest`, `uv run mypy` clear |
| **Next.js** | 9/10 | `npm run dev`, `npm test` well-documented |
| **Django** | 8/10 | `manage.py test`, clear but could unify |
| **Sentry** | 8/10 | `prek run` abstracted, less discoverable |
| **Vue.js** | 8/10 | `npm run test`, `npm run lint` documented |
| **Airflow** | 7/10 | `breeze run` complex, requires knowledge |
| **Kubernetes** | 7/10 | Multiple approaches (kubectl, helm, etc.) |
| **TensorFlow** | 7/10 | Setup heavy, testing less clear |
| **React** | 6/10 | Create-react-app standard but fragmented |

---

### Dimension 2: Type-Checking Coverage

| Repo | Score | Why |
|------|-------|-----|
| **FastAPI** | 10/10 | Pydantic models, strict type validation |
| **Braxis** | 9/10 | mypy strict mode (Python 3.8+) |
| **Next.js** | 8/10 | TypeScript enforced for new projects |
| **Django** | 7/10 | Type hints encouraged, not enforced |
| **Sentry** | 9/10 | Type-checked core, exceptions documented |
| **Vue.js** | 8/10 | TypeScript support, good examples |
| **Kubernetes** | 6/10 | Go-typed, but SDK types less strict |
| **TensorFlow** | 7/10 | Type hints in Python API |
| **Airflow** | 7/10 | Type hints present but not strict |
| **React** | 7/10 | PropTypes and TypeScript optional |

---

### Dimension 3: Unified Linting Entrypoint

| Repo | Score | Why |
|------|-------|-----|
| **Braxis** | 9/10 | `make lint` = mypy + ruff + format check |
| **FastAPI** | 8/10 | Separate: `mypy`, `ruff check` documented |
| **Next.js** | 8/10 | `npm run lint` clear, Next.js integrated |
| **Sentry** | 9/10 | `prek run -q` single command |
| **Django** | 7/10 | Multiple commands: pylint, black, etc. |
| **Vue.js** | 8/10 | `npm run lint`, ESLint + Prettier |
| **Airflow** | 7/10 | `prek run --from-ref main --stage pre-commit` |
| **Kubernetes** | 6/10 | Go fmt, lint, test scattered |
| **TensorFlow** | 6/10 | Multiple test runners, not unified |
| **React** | 6/10 | ESLint, Prettier but no single command |

---

### Dimension 4: Agent Boundaries Documentation

| Repo | Score | Why |
|------|-------|-----|
| **Braxis** | 10/10 | 5 CAN + 8 CANNOT patterns with rationale |
| **Sentry** | 9/10 | Multi-tenant scoping documented |
| **FastAPI** | 9/10 | Clear dependency injection patterns |
| **Django** | 7/10 | Implicit boundaries (migrations, signals) |
| **Airflow** | 8/10 | Operator/hook/task boundaries |
| **Next.js** | 7/10 | App Router vs Pages implicit rules |
| **Vue.js** | 6/10 | Composition vs Options API guidance |
| **Kubernetes** | 5/10 | Cluster roles/RBAC implicit |
| **TensorFlow** | 5/10 | Model API boundaries not explicit |
| **React** | 4/10 | Hooks rules implicit only |

---

### Dimension 5: Architecture Documentation

| Repo | Score | Why |
|------|-------|-----|
| **Sentry** | 9/10 | Multi-tenant, Silo, Hybrid cloud (diagrammed) |
| **Braxis** | 9/10 | Components, design principles documented |
| **Airflow** | 9/10 | Scheduler/Worker/Processor boundaries clear |
| **Kubernetes** | 8/10 | Control plane, kubelet, etc. detailed |
| **FastAPI** | 8/10 | Dependency injection, routing architecture |
| **Django** | 8/10 | MVT pattern, middleware, signals documented |
| **TensorFlow** | 7/10 | High-level vs low-level API |
| **Next.js** | 7/10 | App Router structure, SSR/SSG patterns |
| **Vue.js** | 7/10 | Composition API, reactivity system |
| **React** | 6/10 | Minimal (single-package), Hooks architecture |

---

### Dimension 6: PR Checklist & Done Criteria

| Repo | Score | Why |
|------|-------|-----|
| **Braxis** | 9/10 | 8-item numbered checklist |
| **Sentry** | 9/10 | 10+ items, some implicit |
| **Airflow** | 8/10 | Newsfragments required, testing mandatory |
| **FastAPI** | 8/10 | ~5 items, clear but scattered |
| **Django** | 8/10 | Tests required, docs expected |
| **Next.js** | 7/10 | No formal checklist, assumes standards |
| **Vue.js** | 7/10 | General guidelines, not formalized |
| **Kubernetes** | 7/10 | Tests required, docs expected |
| **TensorFlow** | 6/10 | Scattered requirements |
| **React** | 6/10 | Minimal formal checklist |

---

### Dimension 7: CI/CD Enforcement

| Repo | Score | Why |
|------|-------|-----|
| **Braxis** | 9/10 | Python 3.8-3.12, all checks block PRs |
| **Sentry** | 9/10 | Multiple job types, extensive matrix |
| **Airflow** | 9/10 | Extensive matrix testing |
| **Kubernetes** | 8/10 | Tests + linting enforced |
| **FastAPI** | 8/10 | Basic CI, type-checking enforced |
| **Django** | 8/10 | Tests required, coverage tracking |
| **Next.js** | 7/10 | Build validation, lint checks |
| **TensorFlow** | 7/10 | Tests run, coverage tracked |
| **Vue.js** | 7/10 | ESLint + unit tests |
| **React** | 7/10 | Tests + type-checking |

---

### Dimension 8: Anti-Patterns & Never-Do Guidance

| Repo | Score | Why |
|------|-------|-----|
| **Braxis** | 10/10 | 10 patterns with impact analysis |
| **Sentry** | 9/10 | 10 patterns, some implicit |
| **FastAPI** | 9/10 | 9 patterns, clear but brief |
| **Airflow** | 8/10 | 9 patterns, mostly implicit |
| **Django** | 8/10 | N+1 queries, signal cascades, migrations |
| **Kubernetes** | 7/10 | Resource limits, RBAC, networking gotchas |
| **Next.js** | 7/10 | API route issues, data fetching patterns |
| **Vue.js** | 6/10 | Reactivity gotchas, lifecycle issues |
| **TensorFlow** | 6/10 | Common mistakes scattered in docs |
| **React** | 6/10 | Hooks rules, but mostly implicit |

---

### Dimension 9: Example Quality & Concrete Code

| Repo | Score | Why |
|------|-------|-----|
| **Braxis** | 10/10 | Language/framework detection examples |
| **React** | 9/10 | Component examples, hooks patterns |
| **Next.js** | 9/10 | Route examples, API handler examples |
| **Django** | 8/10 | Model, view, template examples |
| **FastAPI** | 9/10 | Endpoint examples, validation examples |
| **Vue.js** | 8/10 | Component examples, composition API |
| **Sentry** | 8/10 | Integration examples |
| **Airflow** | 8/10 | DAG examples, operator examples |
| **Kubernetes** | 7/10 | YAML examples, deployment patterns |
| **TensorFlow** | 7/10 | Model training, inference examples |

---

### Dimension 10: Overall Developer Guidance Quality

| Repo | Score | Why |
|------|-------|-----|
| **Braxis** | 9/10 | 400+ lines, comprehensive, clear |
| **Sentry** | 9/10 | Very comprehensive, well-organized |
| **Django** | 8/10 | Long history of good docs |
| **FastAPI** | 8/10 | Excellent quality despite brevity |
| **Airflow** | 8/10 | Extensive, though complex |
| **Next.js** | 7/10 | Good, but evolving framework |
| **Kubernetes** | 7/10 | Comprehensive but very technical |
| **Vue.js** | 7/10 | Good quality, clear structure |
| **TensorFlow** | 7/10 | Comprehensive but scattered |
| **React** | 7/10 | Good but assumes knowledge |

---

## 📈 Score Distribution

```
Agent-Optimized (90-100):    🟢 1 repo  (Braxis)
Enterprise-Ready (80-89):    🟢 2 repos (Sentry, FastAPI)
AI-Native (60-79):           🟡 7 repos (Django, Next.js, Vue, Airflow, K8s, TF, React)
Agent-Aware (30-59):         🟠 0 repos
Not Ready (0-29):            🔴 0 repos
```

---

## 💡 Improvement Recommendations by Repo

### 🥇 Braxis (93/100) → 95/100+

**What's Working**:
- Perfect agent boundaries (10/10)
- Perfect anti-patterns (10/10)
- Perfect examples (10/10)
- Excellent overall (9/10)

**To Reach 95+**:
1. **Add architecture diagrams** (+1-2 points)
   - Current: Descriptive text only
   - Add: Mermaid diagrams showing component interactions
   
2. **Expand internal type hints** (+1 point)
   - Current: Public methods typed
   - Extend: Internal helper methods typed

3. **Add coverage reporting integration** (+1 point)
   - Current: Manual testing
   - Add: codecov integration + badge

---

### 🥈 Sentry (83/100) → 87/100+

**What's Working**:
- Excellent architecture documentation (9/10)
- Strong CI/CD setup (9/10)
- Good anti-patterns (9/10)

**To Improve**:
1. **Make agent boundaries more explicit** (+2 points)
   - Current: Multi-tenant scoping implicit
   - Add: Dedicated "What agents CAN/CANNOT do" section
   
2. **Improve command clarity** (+1 point)
   - Current: `prek run` is abstracted
   - Add: More discoverable quick-start commands

3. **Expand PR checklist** (+1 point)
   - Current: 10+ items scattered
   - Formalize: Numbered checklist in CONTRIBUTING.md

---

### 🥉 FastAPI (81/100) → 85/100+

**What's Working**:
- Strict type-checking (10/10)
- Clear examples (9/10)
- Good anti-patterns (9/10)

**To Improve**:
1. **Add explicit agent boundaries** (+2 points)
   - Current: Dependency injection patterns implicit
   - Add: "What agents CAN/CANNOT do" section

2. **Unify linting commands** (+1 point)
   - Current: `mypy` + `ruff` separate
   - Create: Single `make lint` or `uv run lint` wrapper

3. **Add architecture diagrams** (+1 point)
   - Current: Text descriptions only
   - Add: Mermaid diagrams of request lifecycle

---

### Django (78/100) → 82/100+

**What's Working**:
- Mature documentation (8/10)
- Clear architecture (8/10)
- Good examples (8/10)

**To Improve**:
1. **Formalize agent boundaries** (+2 points)
   - Current: MVT pattern implicit
   - Add: Explicit "What agents CAN/CANNOT do"

2. **Document anti-patterns more** (+1 point)
   - Current: N+1 queries, signals scattered
   - Create: Dedicated "Common Mistakes" section

3. **Add PR checklist** (+1 point)
   - Current: Tests required but informal
   - Formalize: Numbered checklist

---

### Airflow (72/100) → 78/100+

**What's Working**:
- Clear architecture (9/10)
- Excellent CI/CD (9/10)
- Strong examples (8/10)

**To Improve**:
1. **Simplify command execution** (+2 points)
   - Current: `breeze run` requires knowledge
   - Add: Quick-start commands alongside Breeze

2. **Make agent boundaries explicit** (+2 points)
   - Current: Operator/hook/task boundaries implicit
   - Add: Dedicated guidance section

3. **Unify instructions** (+1 point)
   - Current: Complex flags scattered
   - Create: Unified entry point

---

### Next.js (75/100) → 80/100+

**What's Working**:
- Clear commands (9/10)
- Good examples (9/10)
- Good architecture (7/10)

**To Improve**:
1. **Document agent boundaries** (+2 points)
   - Current: App Router vs Pages implicit
   - Add: "What agents CAN/CANNOT modify" section

2. **Add explicit anti-patterns** (+2 points)
   - Current: Scattered throughout docs
   - Create: "Never Do" checklist

3. **Add PR checklist** (+1 point)
   - Current: Assumes standards
   - Formalize: Numbered completion criteria

---

### Vue.js (72/100) → 77/100+

**What's Working**:
- Good type-checking (8/10)
- Clear examples (8/10)
- Good linting setup (8/10)

**To Improve**:
1. **Document agent boundaries** (+2 points)
   - Current: Composition vs Options API implicit
   - Add: "What agents CAN/CANNOT do" section

2. **Add anti-patterns section** (+2 points)
   - Current: Reactivity gotchas scattered
   - Create: Dedicated "Common Mistakes"

3. **Add PR checklist** (+1 point)
   - Current: General guidelines only
   - Formalize: Numbered checklist

---

### Kubernetes (70/100) → 76/100+

**What's Working**:
- Detailed architecture (8/10)
- Good examples (7/10)
- Strong CI/CD (8/10)

**To Improve**:
1. **Add agent boundaries** (+2 points)
   - Current: RBAC roles implicit
   - Add: Explicit "What agents CAN/CANNOT do"

2. **Expand anti-patterns** (+2 points)
   - Current: Security gotchas scattered
   - Create: "Common Mistakes" section

3. **Improve command clarity** (+1 point)
   - Current: kubectl, helm, etc. separate
   - Create: Quick-start guide

---

### TensorFlow (68/100) → 74/100+

**What's Working**:
- Type-checking (7/10)
- Clear examples (7/10)
- Good architecture overview (7/10)

**To Improve**:
1. **Add agent boundaries** (+2 points)
   - Current: Model API boundaries implicit
   - Add: Explicit "What agents CAN/CANNOT do"

2. **Organize anti-patterns** (+2 points)
   - Current: Common mistakes scattered
   - Create: "Never Do" section

3. **Unify setup instructions** (+2 points)
   - Current: CPU vs GPU, Python version scattered
   - Create: Unified "Getting Started"

---

### React (65/100) → 72/100+

**What's Working**:
- Great examples (9/10)
- Good architecture overview (6/10)
- Type support (7/10)

**To Improve**:
1. **Create formal AGENTS.md** (+5 points)
   - Current: None (embedded in various docs)
   - Add: Dedicated file with full structure

2. **Document agent boundaries** (+3 points)
   - Current: Hooks rules implicit
   - Add: "What agents CAN/CANNOT do"

3. **Add PR checklist** (+2 points)
   - Current: Minimal guidance
   - Create: Numbered completion criteria

4. **Organize anti-patterns** (+2 points)
   - Current: Warnings scattered
   - Create: "Common Mistakes" section

---

## 🏆 Key Insights

### What Braxis Does Best
1. **Explicit Agent Boundaries** — 10/10 (others: 4-9/10)
2. **Anti-Patterns Documentation** — 10/10 (others: 6-9/10)
3. **Unified Commands** — make targets (others: scattered)
4. **Overall Coherence** — 93/100 (others: ≤83/100)

### Common Weaknesses Across Repos
1. **Missing AGENTS.md files** — Only 4 repos have formal guidance (Braxis, Sentry, FastAPI, Airflow)
2. **Implicit agent boundaries** — 8/10 repos don't explicitly state "what agents CAN/CANNOT do"
3. **Scattered anti-patterns** — Most repos bury gotchas in scattered documentation
4. **No unified commands** — Only Braxis and Sentry have single entry points

### Opportunities for Improvement
- **React** needs formal AGENTS.md (could jump to 72/100 quickly)
- **Next.js, Vue.js** should add explicit agent boundaries (easy +2 point win)
- **Kubernetes, TensorFlow** need to organize documentation better
- **Django, Airflow** should formalize their checklists

---

## 📋 Batch Grading Results Summary

| Metric | Value |
|--------|-------|
| **Average Score** | 75/100 |
| **Median Score** | 72/100 |
| **Highest** | Braxis (93/100) |
| **Lowest** | React (65/100) |
| **Range** | 28 points |
| **Agent-Optimized** | 1 repo |
| **Enterprise-Ready** | 2 repos |
| **AI-Native** | 7 repos |

---

## 🚀 Next Steps

### For Each Repo's Team

1. **Run `braxis grade --path AGENTS.md --compare`** to get objective scores
2. **Review recommendations** specific to your repo
3. **Prioritize improvements** by impact (agent boundaries +2-3 points, easy wins)
4. **Track progress** over time with quarterly rescoring

### For Community

1. **Adopt AGENTS_GRADING_STANDARD.md** in your projects
2. **Share your scores** to benchmark against others
3. **Contribute dimension improvements** (see standard for process)
4. **Build tools** around the standard (dashboards, CI/CD integration, etc.)

---

**Analysis Complete** ✅

Standard: AGENTS_GRADING_STANDARD.md v1.0  
Scoring Date: October 4, 2026  
All scores based on publicly available documentation

Made with ❤️ for better AI agent guidance
