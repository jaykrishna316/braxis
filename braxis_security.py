"""
Feature 7: Vulnerability Pattern Detection
Scans codebase for security anti-patterns specific to language/framework.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from enum import Enum


class SeverityLevel(Enum):
    """Severity levels for security findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class VulnerabilityPattern:
    """A security vulnerability pattern to detect."""
    id: str
    title: str
    description: str
    severity: SeverityLevel
    language: str
    patterns: List[str]  # Regex patterns to match
    remediation: str
    examples: List[str] = field(default_factory=list)


@dataclass
class Finding:
    """A security finding in the code."""
    pattern_id: str
    file_path: str
    line_number: int
    code_snippet: str
    severity: SeverityLevel
    message: str
    remediation: str


class SecurityAnalyzer:
    """Analyzes code for security vulnerabilities."""

    PATTERNS = {
        "sql_injection_python": VulnerabilityPattern(
            id="sql_injection_python",
            title="SQL Injection Risk",
            description="User input directly concatenated into SQL query",
            severity=SeverityLevel.CRITICAL,
            language="python",
            patterns=[
                r'f".*{.*}.*SELECT',
                r"query.*\+.*input",
                r"execute\(.*\+.*\)"
            ],
            remediation="Use parameterized queries or ORM methods",
            examples=[
                'Bad: cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")',
                'Good: cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))'
            ]
        ),
        "hardcoded_secrets": VulnerabilityPattern(
            id="hardcoded_secrets",
            title="Hardcoded Secrets",
            description="API keys, passwords, or tokens in source code",
            severity=SeverityLevel.CRITICAL,
            language="any",
            patterns=[
                r'api_key\s*=\s*["\'].*["\']',
                r'password\s*=\s*["\'].*["\']',
                r'secret\s*=\s*["\'].*["\']'
            ],
            remediation="Use environment variables or secret management system"
        ),
        "insecure_deserialization": VulnerabilityPattern(
            id="insecure_deserialization",
            title="Insecure Deserialization",
            description="Unsafe deserialization of untrusted data",
            severity=SeverityLevel.HIGH,
            language="python",
            patterns=[
                r'pickle\.loads',
                r'yaml\.load\(.*Loader=',
                r'eval\('
            ],
            remediation="Use safe deserialization like json or yaml.safe_load"
        ),
        "unescaped_output": VulnerabilityPattern(
            id="unescaped_output",
            title="Unescaped Output (XSS)",
            description="User input rendered without escaping",
            severity=SeverityLevel.HIGH,
            language="javascript",
            patterns=[
                r'innerHTML\s*=',
                r'dangerouslySetInnerHTML',
                r'\.html\('
            ],
            remediation="Use textContent, innerText, or templating that auto-escapes"
        ),
        "weak_crypto": VulnerabilityPattern(
            id="weak_crypto",
            title="Weak Cryptography",
            description="Use of weak cryptographic algorithms",
            severity=SeverityLevel.HIGH,
            language="any",
            patterns=[
                r'md5\(',
                r'sha1\(',
                r'DES\(',
                r'RC4\('
            ],
            remediation="Use SHA-256 or stronger algorithms"
        ),
        "missing_validation": VulnerabilityPattern(
            id="missing_validation",
            title="Missing Input Validation",
            description="User input not validated before use",
            severity=SeverityLevel.MEDIUM,
            language="any",
            patterns=[
                r'def.*\(.*\):.*request\.',
                r'@app\.route.*\n.*def.*\(.*\):'
            ],
            remediation="Add input validation and sanitization"
        )
    }

    def __init__(self, language: str = "python"):
        self.language = language
        self.findings: List[Finding] = []
        self.scan_results: Dict[str, List[Finding]] = {}

    def register_pattern(self, pattern: VulnerabilityPattern) -> None:
        """Register a new vulnerability pattern."""
        self.PATTERNS[pattern.id] = pattern

    def scan_file(self, file_path: str, content: str) -> List[Finding]:
        """Scan a file for security vulnerabilities."""
        import re

        findings = []
        lines = content.split('\n')

        # Check patterns for this language
        for pattern_id, pattern in self.PATTERNS.items():
            if pattern.language != "any" and pattern.language != self.language:
                continue

            for line_num, line in enumerate(lines, 1):
                for regex in pattern.patterns:
                    if re.search(regex, line, re.IGNORECASE):
                        finding = Finding(
                            pattern_id=pattern_id,
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=line.strip(),
                            severity=pattern.severity,
                            message=f"{pattern.title}: {pattern.description}",
                            remediation=pattern.remediation
                        )
                        findings.append(finding)

        self.findings.extend(findings)
        self.scan_results[file_path] = findings
        return findings

    def get_findings_by_severity(self) -> Dict[SeverityLevel, List[Finding]]:
        """Get findings grouped by severity."""
        by_severity = {}
        for severity in SeverityLevel:
            by_severity[severity] = [
                f for f in self.findings if f.severity == severity
            ]
        return by_severity

    def get_security_score(self) -> float:
        """Calculate security score (0-100)."""
        if not self.findings:
            return 100.0

        critical = len([f for f in self.findings if f.severity == SeverityLevel.CRITICAL])
        high = len([f for f in self.findings if f.severity == SeverityLevel.HIGH])
        medium = len([f for f in self.findings if f.severity == SeverityLevel.MEDIUM])

        score = 100 - (critical * 20 + high * 10 + medium * 5)
        return max(0, min(100, score))

    def get_summary(self) -> Dict:
        """Get security audit summary."""
        by_severity = self.get_findings_by_severity()

        return {
            "total_findings": len(self.findings),
            "critical": len(by_severity[SeverityLevel.CRITICAL]),
            "high": len(by_severity[SeverityLevel.HIGH]),
            "medium": len(by_severity[SeverityLevel.MEDIUM]),
            "low": len(by_severity[SeverityLevel.LOW]),
            "security_score": self.get_security_score()
        }
