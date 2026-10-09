# Item #4: Context Relevance Metric Validation
## Step-by-Step Execution Guide

**Timeline:** Q3 2026 (8 weeks) | **Effort:** 60h | **Status:** Ready to Execute

---

## Overview

Validate that Braxis context relevance scores accurately predict agent task success across 50+ representative agent tasks.

**Hypothesis:** Context relevance score > 0.75 predicts agent success > 80% of the time.

---

## Phase 1: Task Design & Collection (Weeks 1-3, 15h)

### Step 1.1: Define Task Types (3h)

Select 5 representative task types, 10 tasks each:

```python
from enum import Enum

TASK_TYPES = {
    "ADD_ENDPOINT": {
        "description": "Add new API endpoint",
        "count": 10,
        "example": "Add POST /users endpoint with validation"
    },
    "FIX_BUG": {
        "description": "Debug and fix existing issue",
        "count": 10,
        "example": "Fix race condition in auth token refresh"
    },
    "ADD_TEST": {
        "description": "Write unit/integration tests",
        "count": 10,
        "example": "Add tests for payment webhook handler"
    },
    "REFACTOR": {
        "description": "Improve code quality/structure",
        "count": 10,
        "example": "Extract authentication into separate module"
    },
    "SECURITY": {
        "description": "Fix security vulnerability",
        "count": 10,
        "example": "Add input validation to prevent SQL injection"
    }
}

TOTAL_TASKS = sum(t["count"] for t in TASK_TYPES.values())  # 50
```

### Step 1.2: Task Selection Criteria (5h)

Create spreadsheet to track task selection:

```python
TASK_SELECTION_TEMPLATE = {
    "task_id": "ADD_ENDPOINT_001",
    "type": "ADD_ENDPOINT",
    "codebase": "project_x",
    "description": "Add POST /users endpoint",
    "difficulty": "medium",  # easy, medium, hard
    "clarity": "high",  # low, medium, high
    "expected_files": ["src/routes.py", "src/models.py", "tests/test_api.py"],
    "selection_reason": "Representative web API task, moderate complexity"
}
```

**Selection criteria:**
- Vary project domains (web, CLI, data, etc.)
- Mix difficulty levels (easy 40%, medium 40%, hard 20%)
- Ensure clarity of requirements (avoid ambiguous tasks)
- Document expected file dependencies

### Step 1.3: Create Task Specifications (7h)

For each of 50 tasks, write clear requirements:

```markdown
## Task: ADD_ENDPOINT_001

**Goal:** Add POST /users endpoint

**Requirements:**
1. Accept JSON with name, email, password
2. Validate input (non-empty, valid email format)
3. Hash password before storage
4. Return created user ID on success
5. Return 400 on validation error, 500 on server error

**Files You'll Likely Need:**
- src/routes.py (add endpoint handler)
- src/models.py (user model)
- src/validation.py (input validators)
- tests/test_api.py (API tests)

**Success Criteria:**
- Endpoint responds with 200 for valid input
- Password is hashed (not plaintext)
- Validation errors return 400
- Tests cover success and failure cases
```

Store as JSON for easy processing:

```python
TASK_SPEC_001 = {
    "task_id": "ADD_ENDPOINT_001",
    "goal": "Add POST /users endpoint",
    "requirements": ["requirement 1", "requirement 2", ...],
    "expected_files": ["src/routes.py", "src/models.py", ...],
    "success_criteria": ["criterion 1", "criterion 2", ...]
}
```

---

## Phase 2: Agent Execution (Weeks 4-6, 30h)

### Step 2.1: Set Up Test Infrastructure (5h)

```python
# context_relevance_validation/test_runner.py

import json
import time
from dataclasses import asdict
from tests.test_validation_framework import (
    TaskContextGeneratorEnhanced,
    ContextRelevanceValidationFramework
)
from braxis_task_context_enhanced import TaskType

class AgentTaskTestRunner:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.generator = TaskContextGeneratorEnhanced()
        self.framework = ContextRelevanceValidationFramework()
    
    def run_agent_task(self, task_spec, task_type):
        """Execute agent on task and record results."""
        
        # Generate Braxis context
        context_start = time.time()
        analysis = self.generator.analyze_repo_structure(self.repo_path)
        profile = self.generator.generate_profile_from_analysis(
            task_type, analysis
        )
        suggested_files = profile.relevant_file_patterns
        context_time = time.time() - context_start
        
        # Agent would use context here
        # For testing: simulate agent task execution
        agent_success = self.simulate_agent_execution(
            task_spec, suggested_files
        )
        
        # Compare with ground truth
        actual_files = set(task_spec["expected_files"])
        suggested_set = set(suggested_files[:5])  # Top 5
        
        # Record result
        result = self.framework.record_task_validation(
            task_type=task_type,
            query=task_spec["goal"],
            agent_response_success=agent_success,
            context_relevance_score=self.calculate_relevance(
                suggested_set, actual_files
            ),
            files_actually_needed=list(actual_files),
            files_suggested=list(suggested_set),
            notes=f"Context generation: {context_time:.2f}s"
        )
        
        return result
    
    def simulate_agent_execution(self, task_spec, suggested_files):
        """Simulate agent using provided files."""
        # In reality, this would:
        # 1. Call Claude with context
        # 2. Execute suggested code
        # 3. Verify against success criteria
        
        # For validation: assume agent succeeds if 
        # suggested files cover > 70% of needed files
        return True  # Placeholder
    
    def calculate_relevance(self, suggested, needed):
        """Calculate context relevance score."""
        if not suggested and not needed:
            return 1.0
        if not needed:
            return 0.0
        overlap = suggested & needed
        return len(overlap) / len(needed) if needed else 0.0
```

### Step 2.2: Execute Tasks (20h)

```python
def run_validation_study():
    results = []
    task_count = 0
    
    for task_type_name, task_type_enum in [
        ("ADD_ENDPOINT", TaskType.ADD_ENDPOINT),
        ("FIX_BUG", TaskType.FIX_BUG),
        ("ADD_TEST", TaskType.ADD_TEST),
        ("REFACTOR", TaskType.REFACTOR),
        ("SECURITY", TaskType.SECURITY),
    ]:
        # Load 10 tasks of this type
        tasks = load_tasks_by_type(task_type_name)
        
        for task_spec in tasks:
            task_count += 1
            print(f"\n[{task_count}/50] Running {task_spec['task_id']}...")
            
            runner = AgentTaskTestRunner(task_spec["repo"])
            result = runner.run_agent_task(task_spec, task_type_enum)
            
            results.append(asdict(result))
            
            # Print live results
            print(f"  Success: {result.agent_response_success}")
            print(f"  Relevance: {result.context_relevance_score:.2f}")
            print(f"  Precision: {result.precision:.2f}")
            print(f"  Recall: {result.recall:.2f}")
    
    return results
```

### Step 2.3: Record Execution (5h)

```python
def save_results(results):
    import json
    
    with open("context_relevance_validation/raw_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Create summary
    total = len(results)
    successful = sum(1 for r in results if r["agent_response_success"])
    avg_relevance = sum(r["context_relevance_score"] for r in results) / total
    avg_precision = sum(r["precision"] for r in results) / total
    avg_recall = sum(r["recall"] for r in results) / total
    
    summary = {
        "total_tasks": total,
        "successful_tasks": successful,
        "success_rate": successful / total,
        "average_relevance_score": avg_relevance,
        "average_precision": avg_precision,
        "average_recall": avg_recall
    }
    
    with open("context_relevance_validation/summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    return summary
```

---

## Phase 3: Analysis (Weeks 7-8, 15h)

### Step 3.1: Correlation Analysis (8h)

```python
# context_relevance_validation/analyze.py

import json
import numpy as np
from scipy import stats

def load_results():
    with open("raw_results.json") as f:
        return json.load(f)

def calculate_correlation():
    results = load_results()
    
    # Extract variables
    relevance_scores = np.array([r["context_relevance_score"] for r in results])
    success = np.array([int(r["agent_response_success"]) for r in results])
    precisions = np.array([r["precision"] for r in results])
    recalls = np.array([r["recall"] for r in results])
    
    # Correlation tests
    corr_relevance, p_relevance = stats.pearsonr(relevance_scores, success)
    corr_precision, p_precision = stats.pearsonr(precisions, success)
    corr_recall, p_recall = stats.pearsonr(recalls, success)
    
    print(f"Relevance Score → Success: r={corr_relevance:.3f}, p={p_relevance:.4f}")
    print(f"Precision → Success: r={corr_precision:.3f}, p={p_precision:.4f}")
    print(f"Recall → Success: r={corr_recall:.3f}, p={p_recall:.4f}")
    
    # Success threshold analysis
    print("\nContext Relevance vs Task Success:")
    print("Score Threshold | Success Rate")
    print("-----------------|---------------")
    
    for threshold in np.arange(0.5, 1.0, 0.1):
        high_relevance = [r for r in results 
                         if r["context_relevance_score"] >= threshold]
        if high_relevance:
            success_rate = sum(1 for r in high_relevance 
                             if r["agent_response_success"]) / len(high_relevance)
            print(f"    {threshold:.1f}    |    {success_rate:.1%}")
    
    return {
        "relevance_correlation": corr_relevance,
        "relevance_p_value": p_relevance,
        "precision_correlation": corr_precision,
        "recall_correlation": corr_recall
    }

def analyze_by_task_type():
    results = load_results()
    
    by_type = {}
    for r in results:
        task_type = r["task_type"]
        if task_type not in by_type:
            by_type[task_type] = []
        by_type[task_type].append(r)
    
    print("\nPerformance by Task Type:")
    print("Task Type | Count | Avg Relevance | Avg Precision | Avg Recall | Success %")
    print("-" * 85)
    
    for task_type, tasks in by_type.items():
        avg_rel = np.mean([t["context_relevance_score"] for t in tasks])
        avg_prec = np.mean([t["precision"] for t in tasks])
        avg_rec = np.mean([t["recall"] for t in tasks])
        success_rate = sum(1 for t in tasks if t["agent_response_success"]) / len(tasks)
        
        print(f"{task_type:<12} | {len(tasks):>5} | {avg_rel:>13.2f} | "
              f"{avg_prec:>13.2f} | {avg_rec:>10.2f} | {success_rate:>8.1%}")
```

### Step 3.2: Write Report (7h)

Create `CONTEXT_RELEVANCE_STUDY.md`:

```markdown
# Context Relevance Metric Validation

## Executive Summary
- Tested: 50 agent tasks across 5 types
- Success rate: X% (with Braxis context)
- Average context relevance score: Y (0-1 scale)
- Correlation(relevance → success): r=0.62, p<0.001

## Key Findings
1. Context relevance score predicts success (r > 0.6)
2. Tasks with relevance > 0.75 succeed 85% of time
3. Precision (suggested files needed) average: 0.76
4. Recall (found all needed files) average: 0.82

## By Task Type
| Type | Count | Avg Relevance | Success % |
|------|-------|---------------|-----------|
| ADD_ENDPOINT | 10 | 0.78 | 90% |
| FIX_BUG | 10 | 0.71 | 80% |
| ADD_TEST | 10 | 0.79 | 85% |
| REFACTOR | 10 | 0.68 | 75% |
| SECURITY | 10 | 0.80 | 90% |

## Recommendations
- Context relevance is predictive of success
- Aim for > 0.75 relevance score in production
- Focus on improving recall for REFACTOR tasks
```

---

## Deliverables

✅ **context_relevance_validation/raw_results.json** - All 50 task results
✅ **context_relevance_validation/summary.json** - Aggregated metrics
✅ **CONTEXT_RELEVANCE_STUDY.md** - Findings report
✅ **correlation_analysis.txt** - Statistical test results
✅ **Updated BRAXIS_LIMITATIONS.md** - Context relevance confidence (from 80%)

---

## Success Criteria Checklist

- [ ] 50 tasks designed and documented
- [ ] Tasks cover all 5 types (10 each)
- [ ] Context generated for each task
- [ ] Agent execution simulated/recorded
- [ ] Precision/recall calculated
- [ ] Correlation analysis completed
- [ ] Report written with visualizations
- [ ] Confidence level updated

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Correlation < 0.5 | Context may not be primary success factor; investigate other factors |
| High variance by task type | Document task-specific tuning needs |
| Low recall | Extend file search depth or add semantic search |
| High false positives | Filter by importance score |

---

**Owner:** Context & Analysis Team
**Start Date:** [Q3 2026 kickoff]
**Review Date:** [Week 8]
