# Item #3: Security Scanning Benchmark
## Step-by-Step Execution Guide

**Timeline:** Q3 2026 (8 weeks) | **Effort:** 80h | **Status:** Ready to Execute

---

## Overview

Benchmark Braxis security scanning against industry standards (Semgrep, CodeQL, Bandit) on 250+ test cases with ground truth annotations.

---

## Phase 1: Environment Setup (Week 1, 10h)

### Step 1.1: Install Tools (2h)

```bash
# Create virtual environment
python -m venv venv_security_benchmark
source venv_security_benchmark/bin/activate

# Install security tools
pip install semgrep bandit codeql

# Verify installations
semgrep --version
bandit --version
codeql --version

# For Braxis (already installed)
pip install -e .
```

### Step 1.2: Download Semgrep Rules (3h)

```bash
# OWASP top-10 rules
semgrep --config=p/owasp-top-ten --help

# Custom rule for this benchmark
mkdir -p semgrep_rules
# Download or write python-specific security rules
```

### Step 1.3: Create Test Environment (5h)

```bash
# Create directory structure
mkdir -p security_benchmark/{test_cases,results,fixtures}

# Create Python test harness
cat > security_benchmark/harness.py << 'EOF'
import tempfile
import json
import os
from pathlib import Path

class SecurityBenchmarkHarness:
    def __init__(self, test_cases_dir):
        self.test_cases_dir = test_cases_dir
        self.results = {}
    
    def run_all_tools(self, code_file):
        """Run all security tools on a single file."""
        results = {}
        
        # Run Braxis scanner
        results['braxis'] = self.run_braxis(code_file)
        
        # Run Semgrep
        results['semgrep'] = self.run_semgrep(code_file)
        
        # Run Bandit
        results['bandit'] = self.run_bandit(code_file)
        
        # Run CodeQL (if available)
        try:
            results['codeql'] = self.run_codeql(code_file)
        except:
            results['codeql'] = None
        
        return results
    
    def run_braxis(self, code_file):
        # Implement Braxis scanning
        pass
    
    def run_semgrep(self, code_file):
        import subprocess
        cmd = ['semgrep', '--json', '--config=p/owasp-top-ten', code_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
    
    def run_bandit(self, code_file):
        import subprocess
        cmd = ['bandit', '-f', 'json', code_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
    
    def run_codeql(self, code_file):
        # CodeQL requires database setup
        pass
EOF
```

---

## Phase 2: Test Case Collection (Weeks 2-3, 20h)

### Step 2.1: SQL Injection Test Cases (5h)

Create test file: `security_benchmark/test_cases/sql_injection.py`

```python
# sql_injection.py - Test cases with ground truth

TEST_CASES = {
    "sql_injection_concat_001": {
        "code": '''
import sqlite3
db = sqlite3.connect(':memory:')
user_input = request.args.get('username')
query = "SELECT * FROM users WHERE name = '" + user_input + "'"
db.execute(query)
''',
        "vulnerability": "SQL_INJECTION",
        "line": 5,
        "severity": "HIGH",
        "cve_reference": "CWE-89"
    },
    "sql_injection_fstring_001": {
        "code": '''
import sqlite3
db = sqlite3.connect(':memory:')
username = get_user_input()
query = f"SELECT * FROM users WHERE username = '{username}'"
result = db.execute(query).fetchall()
''',
        "vulnerability": "SQL_INJECTION",
        "line": 5,
        "severity": "HIGH",
        "cve_reference": "CWE-89"
    },
    "sql_injection_format_001": {
        "code": '''
import sqlite3
db = sqlite3.connect(':memory:')
name = request.form['name']
query = "SELECT * FROM products WHERE name = '{}'".format(name)
db.execute(query)
''',
        "vulnerability": "SQL_INJECTION",
        "line": 5,
        "severity": "HIGH",
        "cve_reference": "CWE-89"
    },
    "sql_injection_safe_parameterized": {
        "code": '''
import sqlite3
db = sqlite3.connect(':memory:')
username = request.args.get('username')
query = "SELECT * FROM users WHERE username = ?"
db.execute(query, (username,))
''',
        "vulnerability": None,  # No vulnerability
        "severity": None
    },
    "sql_injection_safe_sqlalchemy": {
        "code": '''
from sqlalchemy import text
username = request.args.get('username')
query = text("SELECT * FROM users WHERE username = :username")
result = db.execute(query, {"username": username})
''',
        "vulnerability": None,
        "severity": None
    },
}
```

Repeat for:
- Hardcoded Credentials (4 variants)
- Command Injection (4 variants)
- Pickle Usage (3 variants)

### Step 2.2: Create Ground Truth Annotations (10h)

```python
# Annotation format
ANNOTATED_DATASET = [
    {
        "id": "sql_001",
        "filename": "sql_injection_concat_001.py",
        "code": "...",
        "vulnerabilities": [
            {
                "type": "SQL_INJECTION",
                "line": 5,
                "severity": "HIGH",
                "confidence": 1.0,  # Ground truth = 100%
                "cve": "CWE-89",
                "explanation": "User input directly concatenated into SQL query"
            }
        ]
    },
    # ... 250+ more cases
]
```

### Step 2.3: Organize Test Suite (5h)

```bash
security_benchmark/test_cases/
├── sql_injection/
│   ├── concat_001.py
│   ├── fstring_001.py
│   ├── format_001.py
│   ├── safe_parameterized.py
│   └── safe_sqlalchemy.py
├── hardcoded_credentials/
├── command_injection/
├── pickle_usage/
└── annotations.json  # Ground truth for all
```

---

## Phase 3: Scanning Execution (Weeks 4-5, 25h)

### Step 3.1: Batch Scanning Script (10h)

```python
# security_benchmark/run_benchmark.py

import json
import os
from pathlib import Path
from harness import SecurityBenchmarkHarness
from tests.test_security_scanning_benchmark import SecurityBenchmarkSuite

def run_full_benchmark():
    harness = SecurityBenchmarkHarness("test_cases")
    results = {
        "timestamp": datetime.now().isoformat(),
        "tools": ["braxis", "semgrep", "bandit", "codeql"],
        "test_cases": []
    }
    
    test_dirs = [
        "sql_injection",
        "hardcoded_credentials", 
        "command_injection",
        "pickle_usage"
    ]
    
    for test_dir in test_dirs:
        test_path = Path(f"test_cases/{test_dir}")
        for test_file in test_path.glob("*.py"):
            print(f"Scanning {test_file}...")
            
            tool_results = harness.run_all_tools(str(test_file))
            
            results["test_cases"].append({
                "test_id": test_file.stem,
                "category": test_dir,
                "tool_results": tool_results
            })
    
    # Save results
    with open("results/benchmark_raw.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    run_full_benchmark()
```

### Step 3.2: Run Benchmark (12h - mostly automated)

```bash
cd security_benchmark
python run_benchmark.py > benchmark.log 2>&1

# Monitor progress
tail -f benchmark.log
```

### Step 3.3: Export Findings (3h)

Convert each tool's output to normalized format:

```python
# Normalize findings across tools
def normalize_findings(tool_name, tool_output):
    findings = []
    
    if tool_name == "braxis":
        findings = [
            {"type": f.vuln_type.value, "line": f.line_number, 
             "severity": f.severity, "confidence": f.confidence}
            for f in tool_output
        ]
    
    elif tool_name == "semgrep":
        findings = [
            {"type": semgrep_to_braxis(m["check_id"]), 
             "line": m["start"]["line"],
             "severity": "HIGH",  # Extract from check_id
             "confidence": 0.95}
            for m in tool_output["results"]
        ]
    
    elif tool_name == "bandit":
        findings = [
            {"type": bandit_to_braxis(issue["test_id"]),
             "line": issue["line_number"],
             "severity": issue["severity"],
             "confidence": 0.85}
            for issue in tool_output["results"]
        ]
    
    return findings
```

---

## Phase 4: Analysis (Weeks 6-7, 25h)

### Step 4.1: Calculate Metrics (12h)

```python
# security_benchmark/analyze_results.py

from tests.test_security_scanning_benchmark import BenchmarkResult

def calculate_metrics(tool_name, findings, ground_truth):
    """Calculate precision/recall/F1 for a tool."""
    
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    
    # Match findings to ground truth
    for finding in findings:
        if finding in ground_truth:
            true_positives += 1
        else:
            false_positives += 1
    
    for truth in ground_truth:
        if truth not in findings:
            false_negatives += 1
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "tool": tool_name,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }

def analyze_all_results():
    results = []
    
    for tool in ["braxis", "semgrep", "bandit", "codeql"]:
        for category in ["sql_injection", "hardcoded_credentials", 
                        "command_injection", "pickle_usage"]:
            metrics = calculate_metrics(tool, category)
            results.append(metrics)
    
    # Print comparison table
    print("\nBenchmark Results")
    print("=" * 80)
    print(f"{'Tool':<15} {'Category':<25} {'Precision':<12} {'Recall':<12} {'F1':<8}")
    print("-" * 80)
    
    for r in results:
        print(f"{r['tool']:<15} {r['category']:<25} "
              f"{r['precision']:.2f}       {r['recall']:.2f}       {r['f1_score']:.2f}")
    
    return results
```

### Step 4.2: Create Summary Table (8h)

Expected output:

```
Benchmark Results Summary
===========================

| Tool | SQL Injection | Hardcoded Creds | Command Injection | Pickle | Overall |
|------|--------------|-----------------|-------------------|--------|---------|
| Braxis | P:0.72 R:0.65 F1:0.68 | ... | ... | ... | P:0.72 R:0.65 F1:0.68 |
| Bandit | P:0.85 R:0.78 F1:0.81 | ... | ... | ... | P:0.85 R:0.78 F1:0.81 |
| Semgrep | P:0.92 R:0.89 F1:0.90 | ... | ... | ... | P:0.92 R:0.89 F1:0.90 |
| CodeQL | P:0.91 R:0.87 F1:0.89 | ... | ... | ... | P:0.91 R:0.87 F1:0.89 |
```

### Step 4.3: Write Report (5h)

Create `SECURITY_SCANNING_VALIDATION.md`:

```markdown
# Security Scanning Benchmark Results

## Executive Summary
- Tested: 250+ code samples across 4 vulnerability types
- Tools: Braxis, Semgrep, CodeQL, Bandit
- Braxis performance: P:0.72, R:0.65, F1:0.68
- Gap to Semgrep: ~20% (acceptable for pattern-based approach)

## By Vulnerability Type
[Table by type]

## False Positive Analysis
- Braxis false positive rate: 8%
- Semgrep false positive rate: 3%
- CodeQL false positive rate: 2%

## Recommendations
- Braxis is suitable as first-pass gate
- Use Semgrep/CodeQL for production compliance
- Implement Braxis → Semgrep pipeline
```

---

## Deliverables

✅ **security_benchmark/test_cases/** - 250+ annotated test cases
✅ **results/benchmark_raw.json** - Raw tool outputs
✅ **results/benchmark_metrics.json** - Calculated precision/recall/F1
✅ **SECURITY_SCANNING_VALIDATION.md** - Findings report
✅ **Updated BRAXIS_LIMITATIONS.md** - Security scanning confidence (from 60%)

---

## Success Criteria Checklist

- [ ] All tools installed and verified
- [ ] 250+ test cases created with ground truth
- [ ] 16 vulnerability type variants covered
- [ ] Benchmark script runs without errors
- [ ] All 4 tools complete scanning
- [ ] Metrics calculated for each tool/type
- [ ] Comparison table generated
- [ ] Report written with recommendations
- [ ] False positive analysis documented

---

**Owner:** Security Team
**Start Date:** [Q3 2026 kickoff]
**Review Date:** [Week 8]
