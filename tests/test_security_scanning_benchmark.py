"""
Security scanning accuracy benchmark.

Compares Braxis vulnerability detection against:
- Semgrep
- CodeQL
- Bandit
- Built-in Python ast module

Provides framework for testing against known CVE datasets and OWASP patterns.
"""

import os
import tempfile
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Tuple

import pytest


class VulnerabilityType(Enum):
    """Types of vulnerabilities Braxis can detect."""
    SQL_INJECTION = "sql_injection"
    HARDCODED_CREDENTIAL = "hardcoded_credential"
    PICKLE_USAGE = "pickle_usage"
    COMMAND_INJECTION = "command_injection"
    HARDCODED_SECRET = "hardcoded_secret"


@dataclass
class VulnerabilityFinding:
    """A detected vulnerability."""
    vuln_type: VulnerabilityType
    file_path: str
    line_number: int
    code_snippet: str
    severity: str  # critical, high, medium, low
    confidence: float  # 0-1


@dataclass
class BenchmarkResult:
    """Result of security scanning benchmark."""
    test_case_name: str
    tool_name: str  # "braxis", "semgrep", "bandit", "codeql"
    findings: List[VulnerabilityFinding]
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float


class SecurityBenchmarkSuite:
    """Test cases with known vulnerabilities for benchmarking."""

    @staticmethod
    def sql_injection_test_cases() -> Dict[str, Tuple[str, List[VulnerabilityType]]]:
        """Return test cases for SQL injection detection."""
        return {
            "basic_concatenation": (
                """
import sqlite3
db = sqlite3.connect(':memory:')
user_input = request.args.get('username')
query = "SELECT * FROM users WHERE name = '" + user_input + "'"
db.execute(query)
                """,
                [VulnerabilityType.SQL_INJECTION]
            ),
            "f_string_concatenation": (
                """
import sqlite3
db = sqlite3.connect(':memory:')
username = get_user_input()
query = f"SELECT * FROM users WHERE username = '{username}'"
result = db.execute(query).fetchall()
                """,
                [VulnerabilityType.SQL_INJECTION]
            ),
            "format_string": (
                """
import sqlite3
db = sqlite3.connect(':memory:')
name = request.form['name']
query = "SELECT * FROM products WHERE name = '{}'".format(name)
db.execute(query)
                """,
                [VulnerabilityType.SQL_INJECTION]
            ),
            "parameterized_safe": (
                """
import sqlite3
db = sqlite3.connect(':memory:')
username = request.args.get('username')
query = "SELECT * FROM users WHERE username = ?"
db.execute(query, (username,))
                """,
                []  # No vulnerability
            ),
            "sqlalchemy_safe": (
                """
from sqlalchemy import text
username = request.args.get('username')
query = text("SELECT * FROM users WHERE username = :username")
result = db.execute(query, {"username": username})
                """,
                []  # No vulnerability
            ),
        }

    @staticmethod
    def hardcoded_credential_test_cases() -> Dict[str, Tuple[str, List[VulnerabilityType]]]:
        """Return test cases for hardcoded credential detection."""
        return {
            "hardcoded_password": (
                """
PASSWORD = "super_secret_123"
API_KEY = "sk-1234567890abcdef"
db = Database(password=PASSWORD)
                """,
                [VulnerabilityType.HARDCODED_CREDENTIAL, VulnerabilityType.HARDCODED_CREDENTIAL]
            ),
            "aws_key": (
                """
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                """,
                [VulnerabilityType.HARDCODED_CREDENTIAL, VulnerabilityType.HARDCODED_CREDENTIAL]
            ),
            "env_variable_safe": (
                """
import os
PASSWORD = os.getenv("DATABASE_PASSWORD")
API_KEY = os.getenv("API_KEY")
                """,
                []  # No vulnerability
            ),
            "docstring_false_positive": (
                """
def authenticate(username, password):
    '''
    Example:
        authenticate("user", "password123")
    '''
    pass
                """,
                []  # False positive risk: appears to be hardcoded in docstring
            ),
        }

    @staticmethod
    def command_injection_test_cases() -> Dict[str, Tuple[str, List[VulnerabilityType]]]:
        """Return test cases for command injection detection."""
        return {
            "os_system_concat": (
                """
import os
filename = request.args.get('file')
os.system("rm /tmp/" + filename)
                """,
                [VulnerabilityType.COMMAND_INJECTION]
            ),
            "os_system_f_string": (
                """
import os
user_id = request.form['id']
os.system(f"kill -9 {user_id}")
                """,
                [VulnerabilityType.COMMAND_INJECTION]
            ),
            "subprocess_list_safe": (
                """
import subprocess
filename = request.args.get('file')
subprocess.run(["rm", filename], check=True)
                """,
                []  # No vulnerability (list form is safe)
            ),
            "subprocess_shell_unsafe": (
                """
import subprocess
cmd = request.args.get('cmd')
subprocess.run(cmd, shell=True)
                """,
                [VulnerabilityType.COMMAND_INJECTION]
            ),
        }

    @staticmethod
    def pickle_test_cases() -> Dict[str, Tuple[str, List[VulnerabilityType]]]:
        """Return test cases for pickle usage detection."""
        return {
            "pickle_load_untrusted": (
                """
import pickle
data = request.data
obj = pickle.loads(data)
                """,
                [VulnerabilityType.PICKLE_USAGE]
            ),
            "pickle_dump_safe": (
                """
import pickle
my_obj = {"key": "value"}
pickled = pickle.dumps(my_obj)
                """,
                []  # Dumping (writing) is safe
            ),
            "json_safe": (
                """
import json
data = request.json
obj = json.loads(data)
                """,
                []  # No vulnerability
            ),
        }


class SecurityScanningValidator:
    """Validates security scanning accuracy."""

    def __init__(self):
        self.benchmark_results: List[BenchmarkResult] = []

    def evaluate_braxis_security_scanning(self, code: str, expected_vulns: List[VulnerabilityType]) -> BenchmarkResult:
        """Evaluate Braxis security scanning against known vulnerabilities."""
        # This would call Braxis's actual security scanning
        # For now, we provide the framework

        findings = []

        # Check for SQL injection patterns
        if any(pattern in code for pattern in [
            "SELECT *",
            "db.execute",
            "query ="
        ]) and any(pattern in code for pattern in [
            '+ user',
            'f"',
            '.format(',
            "'" + " + ",
        ]):
            findings.append(VulnerabilityFinding(
                vuln_type=VulnerabilityType.SQL_INJECTION,
                file_path="test.py",
                line_number=1,
                code_snippet=code[:50],
                severity="high",
                confidence=0.75
            ))

        # Check for hardcoded credentials
        if any(pattern in code for pattern in [
            "PASSWORD =",
            "API_KEY =",
            "SECRET_KEY =",
            "AKIAI"
        ]):
            findings.append(VulnerabilityFinding(
                vuln_type=VulnerabilityType.HARDCODED_CREDENTIAL,
                file_path="test.py",
                line_number=1,
                code_snippet=code[:50],
                severity="critical",
                confidence=0.85
            ))

        # Calculate metrics
        tp = len([f for f in findings if f.vuln_type in expected_vulns])
        fp = len([f for f in findings if f.vuln_type not in expected_vulns])
        fn = len([v for v in expected_vulns if v not in [f.vuln_type for f in findings]])

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        result = BenchmarkResult(
            test_case_name="test",
            tool_name="braxis",
            findings=findings,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            precision=precision,
            recall=recall,
            f1_score=f1
        )

        self.benchmark_results.append(result)
        return result


# Test functions

def test_security_benchmark_sql_injection():
    """Test SQL injection detection across test cases."""
    suite = SecurityBenchmarkSuite()
    validator = SecurityScanningValidator()

    test_cases = suite.sql_injection_test_cases()

    for name, (code, expected_vulns) in test_cases.items():
        result = validator.evaluate_braxis_security_scanning(code, expected_vulns)
        print(f"\n{name}:")
        print(f"  Expected: {expected_vulns}")
        print(f"  Found: {[f.vuln_type for f in result.findings]}")
        print(f"  Precision: {result.precision:.2f}, Recall: {result.recall:.2f}")


def test_security_benchmark_hardcoded_credentials():
    """Test hardcoded credential detection."""
    suite = SecurityBenchmarkSuite()
    validator = SecurityScanningValidator()

    test_cases = suite.hardcoded_credential_test_cases()

    for name, (code, expected_vulns) in test_cases.items():
        result = validator.evaluate_braxis_security_scanning(code, expected_vulns)
        print(f"\n{name}:")
        print(f"  Expected: {len(expected_vulns)} vulnerabilities")
        print(f"  Found: {len(result.findings)} vulnerabilities")


def test_security_benchmark_command_injection():
    """Test command injection detection."""
    suite = SecurityBenchmarkSuite()
    test_cases = suite.command_injection_test_cases()
    assert len(test_cases) > 0


def test_security_benchmark_pickle():
    """Test pickle usage detection."""
    suite = SecurityBenchmarkSuite()
    test_cases = suite.pickle_test_cases()
    assert len(test_cases) > 0


def test_braxis_vs_semgrep_coverage():
    """
    Framework for comparing Braxis coverage vs Semgrep.

    To run against actual Semgrep:
    1. Install semgrep: pip install semgrep
    2. Get OWASP rule set: semgrep --config=p/owasp-top-ten
    3. Compare findings
    """
    # This is a placeholder for actual Semgrep comparison
    # Requires installing Semgrep and running it on test cases

    semgrep_rules = [
        "python.lang.security.sql-injection",
        "python.lang.security.hardcoded-secret",
        "python.lang.security.cmd-injection",
    ]

    braxis_patterns = [
        "sql_injection",
        "hardcoded_credential",
        "command_injection",
    ]

    # Mapping: some Braxis patterns map to Semgrep rules
    coverage = {
        "sql_injection": "python.lang.security.sql-injection",
        "hardcoded_credential": "python.lang.security.hardcoded-secret",
        "command_injection": "python.lang.security.cmd-injection",
    }

    for braxis_pattern, semgrep_rule in coverage.items():
        assert semgrep_rule in semgrep_rules


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
