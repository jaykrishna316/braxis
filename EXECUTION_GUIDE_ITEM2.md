# Item #2: Complexity-Based Onboarding Formula Validation
## Step-by-Step Execution Guide

**Timeline:** Q3 2026 (8 weeks) | **Effort:** 40h | **Status:** Ready to Execute

---

## Phase 1: Data Collection (Weeks 1-6, 20h)

### Step 1.1: Identify Target Projects (3h)
Create a spreadsheet with 20+ projects matching these criteria:

| Complexity Level | Target Count | Selection Criteria |
|------------------|--------------|-------------------|
| SIMPLE | 5 | <10 py files, <30 total files, no CI/CD |
| MODERATE | 5 | 10-50 py files, 30-100 total files, may have CI/CD |
| COMPLEX | 5 | 50-200 py files, 100-300 total files, active CI/CD |
| ENTERPRISE | 5 | ≥200 py files, ≥300 total files, complex infrastructure |

**Sources:**
- Internal company projects
- Open-source projects (GitHub search)
- Community partnerships
- Customer codebases (with permission)

### Step 1.2: Run Braxis Analysis (5h)
For each project, execute:

```bash
# Clone project
git clone <project_url>
cd <project>

# Run Braxis analysis
python -c "
from braxis_handoff_enhanced import HandoffCoordinatorEnhanced, ProjectComplexity

coordinator = HandoffCoordinatorEnhanced()
analysis = coordinator.analyze_project_complexity('.')
plan = coordinator.generate_onboarding_plan('Developer', '.')

print(f'Complexity: {analysis[\"complexity_level\"].value}')
print(f'Predicted Duration: {plan.duration_days} days')
print(f'Files: {analysis[\"file_count\"]} total, {analysis[\"py_files\"]} Python')
print(f'CI/CD: {analysis[\"has_ci_cd\"]}')
"
```

**Record in spreadsheet:**
- Project name
- Predicted duration (days)
- Complexity level
- File counts
- CI/CD detected

### Step 1.3: Survey Teams (12h)
Contact teams who worked on the project:

**Survey Template:**

```plaintext
Project: [Name]

1. How many days did it take your team to reach productivity?
   (productive = can make small changes independently)
   Answer: ___ days

2. Team experience level at start:
   □ Junior (< 2 years)
   □ Mid-level (2-5 years)  
   □ Senior (5+ years)

3. Primary domain:
   □ Web API (REST/GraphQL)
   □ CLI Tool
   □ Data/ML
   □ Infrastructure
   □ Other: ___

4. Any special factors that slowed onboarding?
   Text: ___________

5. Documentation quality:
   □ Excellent
   □ Good
   □ Average
   □ Poor
```

**Collection methods:**
- Email surveys
- Slack polls
- 1-on-1 interviews (15 min)
- Retrospective notes

### Step 1.4: Record Data (5h)

Use the validation framework:

```python
from tests.test_validation_framework import OnboardingValidationFramework

fw = OnboardingValidationFramework()

fw.record_actual(
    project_name="project_xyz",
    predicted_days=7,
    actual_days=9,
    team_experience="mid",
    domain="web_api",
    file_count=95,
    py_files=40,
    has_ci_cd=True,
    complexity_level=ProjectComplexity.MODERATE,
    notes="Team struggled with async patterns initially"
)

# After all 20+ projects:
summary = fw.get_summary()
fw.export_json("validation_results_complexity.json")
```

---

## Phase 2: Analysis (Weeks 6-7, 15h)

### Step 2.1: Statistical Analysis (8h)

Calculate key metrics:

```python
import json
from statistics import mean, stdev

with open("validation_results_complexity.json") as f:
    data = json.load(f)

# Overall variance
all_variances = [r["variance_percent"] for r in data["raw_data"]]
print(f"Average Variance: {mean(all_variances):.1f}%")
print(f"Std Dev: {stdev(all_variances):.1f}%")
print(f"Range: {min(all_variances):.1f}% to {max(all_variances):.1f}%")

# By Complexity Level
print("\nBy Complexity Level:")
for level, metrics in data["by_complexity"].items():
    print(f"  {level}: avg {metrics['avg_variance']:.1f}%, "
          f"max {metrics['max_variance']:.1f}%")

# By Experience
print("\nBy Team Experience:")
for exp, metrics in data["by_experience"].items():
    print(f"  {exp}: avg {metrics['avg_variance']:.1f}%")
```

**Success thresholds:**
- ✅ PASS: Average variance < 25%, no level > 40%
- ⚠️ PARTIAL: 25-35% variance, some levels > 40%
- ❌ FAIL: > 35% variance, multiple levels > 40%

### Step 2.2: Identify Outliers (4h)

Projects with > 50% variance need investigation:

```python
for result in data["raw_data"]:
    variance = result["variance_percent"]
    if abs(variance) > 50:
        print(f"\nOutlier: {result['project_name']}")
        print(f"  Predicted: {result['predicted_days']}d")
        print(f"  Actual: {result['actual_days']}d")
        print(f"  Notes: {result['validation_notes']}")
        print("  Action: Investigate if notes explain variance")
```

### Step 2.3: Create Summary Report (3h)

Document findings in `COMPLEXITY_FORMULA_VALIDATION.md`:

```markdown
# Complexity Formula Validation Results

## Executive Summary
- Tested: 20+ projects across all complexity levels
- Overall variance: X%
- Success rate: Y/Z projects within ±25%

## By Complexity Level
| Level | Count | Avg Variance | Max Variance |
|-------|-------|--------------|--------------|
| SIMPLE | 5 | X% | Y% |
| MODERATE | 5 | X% | Y% |
| COMPLEX | 5 | X% | Y% |
| ENTERPRISE | 5 | X% | Y% |

## Confidence Assessment
Current formula confidence: XX% (was 55%)

## Recommendations
- If passing: Formula is validated
- If partial: Add experience multipliers
- If failing: Recalibrate thresholds
```

---

## Phase 3: Formula Refinement (Weeks 7-8, 5h)

### Option A: Passing (variance < 25%)
No changes needed. Document validation result.

### Option B: Partial (25-35% variance)
Add experience multiplier:

```python
# Current formula gives 7 days for MODERATE
# If junior teams take 12 days, senior take 5:
def estimate_with_experience(complexity, team_experience):
    base = complexity_days[complexity]
    multiplier = {
        "junior": 1.8,
        "mid": 1.0,
        "senior": 0.7
    }[team_experience]
    return base * multiplier
```

### Option C: Failing (variance > 35%)
Schedule retrospective meeting:
- Review outlier projects
- Identify missing factors (domain, test coverage, documentation)
- Plan major formula revision for next quarter

---

## Deliverables

✅ **validation_results_complexity.json** - Raw data export
✅ **COMPLEXITY_FORMULA_VALIDATION.md** - Findings report
✅ **Updated BRAXIS_LIMITATIONS.md** - New confidence level (from 55%)
✅ **Formula refinement (if needed)** - Updated code with multipliers

---

## Success Criteria Checklist

- [ ] 20+ projects identified and permission obtained
- [ ] Braxis analysis run on all projects
- [ ] Team feedback collected (≥80% response rate)
- [ ] Data recorded in validation framework
- [ ] Statistical analysis completed
- [ ] Report written with recommendations
- [ ] Findings socialized with team
- [ ] Next actions documented

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Teams unavailable for survey | Use historical data from retrospectives, Jira time tracking |
| Variance > 40% on all levels | Expand to 30 projects, add domain as factor |
| Outlier projects explain failures | Document as special cases (e.g., "learning projects") |
| Formula still uncertain | Set lower confidence level, note as "order-of-magnitude" |

---

**Owner:** Engineering Team
**Start Date:** [Q3 2026 kickoff]
**Review Date:** [Week 8]
