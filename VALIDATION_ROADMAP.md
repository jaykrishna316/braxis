# Braxis 2.0: Validation Roadmap & Execution Timeline

**Status:** 🟢 Ready to Execute | **Updated:** 2026-10-09

---

## Executive Summary

Complete execution plan for validating all 10 engineering backlog items. Critical path focuses on 4 core validation studies (Items #2-4, #6) with parallel research and development streams.

**Total Effort:** 550 hours (12-14 weeks with team of 4-5)
**Critical Path:** Items #2, #6, #3, #4 → Item #1 (longitudinal study)
**Key Deliverables:** 
- Validation frameworks with real data
- Competitive benchmarks (Semgrep/CodeQL)
- Publishable research findings
- Updated confidence levels
- Refined formulas/algorithms

---

## Timeline Overview

```
Q3 2026                              Q4 2026 - Q1 2027
Sep    Oct    Nov    Dec             Jan    Feb
|------|------|------|------|--------|------|
  [#2,#3,#4,#6 READY]                 [#1 CRITICAL]
  Validation Studies                  Longitudinal Study
  
Parallel: #7,#8,#9 Development        #10 Roadmap
```

---

## Critical Path Items (Ready Now)

### Item #2: Complexity Formula Validation ✅
**Status:** READY | **Effort:** 40h | **Timeline:** 8 weeks (Q3)

**GitHub Issue:** #11
**Execution Guide:** EXECUTION_GUIDE_ITEM2.md

**What it does:**
- Tests whether Braxis complexity estimates correlate with actual team onboarding time
- Collects data from 20+ real projects
- Validates or refines the complexity formula

**Phases:**
1. Data Collection (20h) - Identify projects, run Braxis analysis, survey teams
2. Statistical Analysis (15h) - Calculate variance by complexity level
3. Formula Refinement (5h) - Update if variance > 25%

**Success Criteria:**
- ✅ 20+ projects with actual ramp-time data
- ✅ Average variance < 25%
- ✅ No complexity level > 40% variance
- ✅ Confidence level raised from 55% to 75%+

**Blockers:** None - can start immediately
**Next Step:** Item #1 (depends on this data)

**Deliverables:**
- validation_results_complexity.json
- COMPLEXITY_FORMULA_VALIDATION.md
- Updated confidence level

---

### Item #3: Security Scanning Benchmark ✅
**Status:** READY | **Effort:** 80h | **Timeline:** 8 weeks (Q3)

**GitHub Issue:** #12
**Execution Guide:** EXECUTION_GUIDE_ITEM3.md

**What it does:**
- Benchmarks Braxis security scanning against Semgrep, CodeQL, Bandit
- Tests 250+ code samples with known vulnerabilities
- Calculates precision/recall/F1 by vulnerability type

**Phases:**
1. Environment Setup (10h) - Install tools, create test harness
2. Test Case Collection (20h) - 250 annotated test cases
3. Scanning Execution (25h) - Run all 4 tools
4. Analysis (25h) - Calculate metrics and write report

**Success Criteria:**
- ✅ 250+ test cases with ground truth
- ✅ Precision/recall/F1 for 4+ vulnerability types
- ✅ Braxis within 10-15% of Semgrep
- ✅ False positive rate < 10%

**Blockers:** None - can start immediately
**Parallel with:** Item #2

**Deliverables:**
- security_benchmark_results.json
- SECURITY_SCANNING_VALIDATION.md
- Comparative accuracy matrix
- Updated confidence level

---

### Item #4: Context Relevance Metric Validation ✅
**Status:** READY | **Effort:** 60h | **Timeline:** 8 weeks (Q3)

**GitHub Issue:** #13
**Execution Guide:** EXECUTION_GUIDE_ITEM4.md

**What it does:**
- Validates that context relevance scores predict agent task success
- Executes 50 real agent tasks across 5 types
- Measures precision/recall of suggested files

**Phases:**
1. Task Design (15h) - Create 50 representative tasks
2. Agent Execution (30h) - Run tasks with Braxis context, record outcomes
3. Analysis (15h) - Correlation testing and report

**Success Criteria:**
- ✅ 50 tasks executed (10 per type)
- ✅ Precision > 0.75 (suggested files are relevant)
- ✅ Recall > 0.80 (agent gets needed files)
- ✅ Correlation(relevance_score → success) > 0.6
- ✅ Confidence level raised from 80% to 85%+

**Blockers:** None - can start immediately
**Parallel with:** Item #2, #3

**Deliverables:**
- context_relevance_validation.json
- CONTEXT_RELEVANCE_STUDY.md
- Correlation analysis
- Updated confidence level

---

### Item #6: Real-Analysis vs Template A/B Testing ✅
**Status:** READY | **Effort:** 120h | **Timeline:** 10 weeks (Q3-Q4)

**GitHub Issue:** #15
**Execution Guide:** EXECUTION_GUIDE_ITEM6.md

**What it does:**
- Proves real-analysis provides 10+ percentage point advantage over templates
- A/B tests 50 matched task pairs (control = template, treatment = real-analysis)
- Includes statistical significance testing

**Phases:**
1. Template System Build (30h) - Create naive baseline
2. A/B Test Design (30h) - Create 50 matched pairs, randomize/blind
3. Execution (60h) - Run 50 task pairs with outcome recording
4. Analysis (30h) - Statistical testing and report

**Success Criteria:**
- ✅ Real-analysis success > Template success by > 10 percentage points
- ✅ Statistically significant (p < 0.05)
- ✅ Holds across task types
- ✅ Publishable findings

**Blockers:** None - can start immediately
**Parallel with:** Item #2, #3, #4
**Required for:** Item #1 (validates hypothesis)

**Deliverables:**
- Template system module
- ab_test_results.json
- REAL_ANALYSIS_VALIDATION.md
- Statistical analysis
- Publishable findings

---

## Dependent Items (Wait for Critical Path)

### Item #1: Longitudinal Impact Validation Study 🔴
**Status:** PLANNED | **Effort:** 160h | **Timeline:** 16 weeks (Q4 2026 - Q1 2027)

**GitHub Issue:** #10
**Dependencies:** Items #2, #3, #4, #6 must complete first

**What it does:**
- RCT proving Braxis improves agent productivity and code quality
- Randomized: 50 control tasks (no Braxis), 50 treatment tasks (with Braxis)
- Measures: success rate, time-to-completion, token efficiency, code quality

**Status:** Waiting for critical path validation data
**Next Step:** Schedule kickoff after Item #6 completes (early Q4)

**Why it depends on critical path:**
- Needs validated complexity formula (Item #2)
- Needs proven security scanning capability (Item #3)
- Needs validated context relevance (Item #4)
- Needs demonstrated real-analysis advantage (Item #6)

---

## Parallel Development Items (Non-Critical Path)

### Item #5: Documentation of Limitations ✅ COMPLETED
**Status:** COMPLETED | **Completion Date:** 2026-10-09

**Deliverable:** BRAXIS_LIMITATIONS.md (1,254 lines)
**Published:** https://claude.ai/artifact/TKq8F23ziXpVQj5DnqD6KR

---

### Item #7: Harden Security Scanning with CodeQL Backend
**Status:** READY | **Effort:** 60h | **Timeline:** Q4 2026 (6-8 weeks)

**GitHub Issue:** #16
**Does NOT block:** Any other items (optional improvement)

**What it does:**
- Adds optional CodeQL backend for semantic security scanning
- Reduces false negatives on complex patterns
- Backward compatible with existing heuristic scanning

---

### Item #8: Close Cursor/Copilot Framework Detection Gap
**Status:** READY | **Effort:** 20h | **Timeline:** Q4 2026 (3-4 weeks)

**GitHub Issue:** #17
**Does NOT block:** Any other items (research/competitive analysis)

**What it does:**
- Investigates how Cursor and GitHub Copilot detect frameworks
- Documents gaps in Braxis approach
- Proposes improvements (import graph analysis, semantic detection)

---

### Item #9: OpenTelemetry Alignment
**Status:** READY | **Effort:** 40h | **Timeline:** Q4 2026 (5-6 weeks)

**GitHub Issue:** #18
**Does NOT block:** Any other items (infrastructure improvement)

**What it does:**
- Aligns Braxis telemetry with OpenTelemetry standards
- Integrates exporters (Datadog, New Relic, Jaeger)
- Creates monitoring dashboards

---

### Item #10: Factory.ai Outreach & Integration
**Status:** PLANNED | **Effort:** 30h | **Timeline:** Q4 2026-Q1 2027

**Does NOT block:** Any other items (partnership opportunity)

**What it does:**
- Contacts Factory.ai about potential partnership
- Proposes integration with their platform
- Scopes joint development effort

---

## Weekly Execution Schedule (Q3 2026)

### Week 1 (Oct 1-5): Kickoff
- [ ] Assign teams to items #2, #3, #4, #6
- [ ] Review execution guides (30 min per item)
- [ ] Set up tracking/repos
- [ ] Item #2 team: Identify 20 projects
- [ ] Item #3 team: Install tools and create harness
- [ ] Item #4 team: Design 50 tasks
- [ ] Item #6 team: Build template system

### Weeks 2-3: Setup Phase
- [ ] Item #2: Surveys sent to teams, Braxis running
- [ ] Item #3: Test cases written (SQL, creds, command, pickle)
- [ ] Item #4: Tasks documented and ready
- [ ] Item #6: Template system validated, A/B pairs created

### Weeks 4-6: Execution Phase
- [ ] Item #2: Data collection ongoing, variance analysis
- [ ] Item #3: Benchmark scanning in progress
- [ ] Item #4: Agent tasks executing, results logging
- [ ] Item #6: A/B test execution (pairs 1-50)

### Weeks 7-8: Analysis Phase
- [ ] Item #2: Statistical analysis, formula refinement
- [ ] Item #3: Metric calculation, report writing
- [ ] Item #4: Correlation analysis, report writing
- [ ] Item #6: Statistical testing, blind review, report

### Week 8+ (Late Oct-Nov): Q4 Planning
- [ ] Compile Item #1 (longitudinal study) plan
- [ ] Assign resources to parallel items (#7, #8, #9)
- [ ] Start Item #1 kickoff (early November)

---

## Resource Allocation Recommendation

**Minimum team:** 4 people for critical path

```
Team Structure:
- Project Manager (20% on roadmap coordination)
- Data Science (Item #2, #3, #4 analysis)
- Security Engineer (Item #3 security scanning)
- Agent/ML Engineer (Item #4, #6 agent execution)
- Research Lead (Item #6 statistical testing, Item #1 design)

Time allocation:
40h (Item #2)    +
80h (Item #3)    +
60h (Item #4)    +
120h (Item #6)   = 300 hours critical path
                    (8-10 weeks with 30-40h/week team capacity)

Parallel:
40h (Item #7)    +
20h (Item #8)    +
40h (Item #9)    +
30h (Item #10)   = 130 hours non-critical
                    (can overlap with critical path)
```

---

## Success Metrics & Milestones

| Milestone | Target Date | Criteria |
|-----------|------------|----------|
| **Phase 1 Complete** (Items #2-4, #6 execution) | 2026-11-15 | All 4 items have raw data collected |
| **Phase 2 Complete** (Analysis & reporting) | 2026-12-01 | All 4 reports written, findings socialized |
| **Phase 3 Start** (Item #1 RCT) | 2026-12-15 | Item #1 kickoff meeting held |
| **Phase 3 Execution** (Item #1 data collection) | 2027-01-31 | 100 tasks executed (50/50 split) |
| **Phase 3 Complete** (Item #1 analysis) | 2027-02-28 | RCT findings analyzed and reported |
| **Preprint Ready** (Publication) | 2027-03-15 | arXiv submission ready |

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Teams unavailable for Item #2 surveys | Medium | High | Use historical data from Jira/retrospectives |
| Item #3 tool installation issues | Low | Medium | Pre-test all tools on test VMs |
| Item #4 agent success < 50% | Low | High | Simplify task designs, use easier projects |
| Item #6 shows no difference | Low | High | Increase sample size to 100 pairs |
| Item #1 recruitment challenges | Medium | High | Secure partnerships early (Q3), start recruiting in Q4 |
| Timeline slippage | Medium | Medium | Weekly status checks, adjust scope if needed |

---

## Communication & Reporting

**Weekly sync:** Every Monday, 30 min
- Item status updates (G/Y/R)
- Blockers and risks
- Key metrics/progress

**Bi-weekly stakeholder update:** Every other Thursday
- High-level progress
- Major decisions made
- Q&A with leadership

**Final reports:**
- Item #2: Early November
- Item #3: Early November
- Item #4: Mid-November
- Item #6: Late November
- Item #1: Late February 2027

---

## How to Use This Roadmap

### For Team Leads:
1. Read the execution guide for your item
2. Create sprint plan (2-week sprints recommended)
3. Assign team members and set up tracking
4. Check weekly against timeline

### For Engineers:
1. Review your item's execution guide (1-2 hours)
2. Set up environment per guide instructions
3. Follow phase breakdowns and success criteria
4. Report blockers daily, results weekly

### For Product/Leadership:
1. Review this overview (20 min)
2. Attend weekly syncs (30 min)
3. Approve major decisions as needed
4. Plan Item #1 kickoff after Item #6 data available

---

## Appendix: Cross-Reference

| Item | GitHub Issue | Guide | Status | Effort | Timeline |
|------|---|---|---|---|---|
| #1 | #10 | ENGINEERING_BACKLOG.md | PLANNED | 160h | Q4-Q1 |
| #2 | #11 | EXECUTION_GUIDE_ITEM2.md | READY | 40h | Q3 |
| #3 | #12 | EXECUTION_GUIDE_ITEM3.md | READY | 80h | Q3 |
| #4 | #13 | EXECUTION_GUIDE_ITEM4.md | READY | 60h | Q3 |
| #5 | #14 | BRAXIS_LIMITATIONS.md | ✅ DONE | 80h | Done |
| #6 | #15 | EXECUTION_GUIDE_ITEM6.md | READY | 120h | Q3-Q4 |
| #7 | #16 | ENGINEERING_BACKLOG.md | READY | 60h | Q4 |
| #8 | #17 | ENGINEERING_BACKLOG.md | READY | 20h | Q4 |
| #9 | #18 | ENGINEERING_BACKLOG.md | READY | 40h | Q4 |
| #10 | — | ENGINEERING_BACKLOG.md | PLANNED | 30h | Q4-Q1 |

---

**Last Updated:** 2026-10-09
**Next Review:** 2026-10-16 (post-kickoff sync)
**Owner:** Engineering Leadership
**Questions?** See ENGINEERING_BACKLOG.md for full context
