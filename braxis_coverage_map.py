"""
Feature 10: Test-to-Code Mapping
Creates bidirectional mapping between tests and code they cover.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional


@dataclass
class CodeLocation:
    """A location in source code."""
    file_path: str
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    line_range: Optional[tuple] = None


@dataclass
class TestCase:
    """A test case."""
    test_id: str
    test_file: str
    test_name: str
    code_locations: List[CodeLocation] = field(default_factory=list)
    impact_area: str = ""  # e.g., "API", "Database", "Utils"


@dataclass
class CoverageReport:
    """Coverage analysis for a feature."""
    feature_name: str
    covered_by_tests: List[TestCase]
    uncovered_code: List[CodeLocation]
    coverage_percentage: float


class CoverageMapper:
    """Maps tests to code and vice versa."""

    def __init__(self):
        self.tests: Dict[str, TestCase] = {}
        self.code_to_tests: Dict[str, List[TestCase]] = {}
        self.features: Dict[str, List[CodeLocation]] = {}

    def register_test(self, test: TestCase) -> None:
        """Register a test case."""
        self.tests[test.test_id] = test

        # Index code-to-tests mapping
        for location in test.code_locations:
            key = f"{location.file_path}:{location.function_name}"
            if key not in self.code_to_tests:
                self.code_to_tests[key] = []
            self.code_to_tests[key].append(test)

    def register_feature(self, feature_name: str,
                        code_locations: List[CodeLocation]) -> None:
        """Register a feature and its code locations."""
        self.features[feature_name] = code_locations

    def get_tests_for_code(self, file_path: str,
                          function_name: Optional[str] = None) -> List[TestCase]:
        """Get all tests covering a piece of code."""
        key = f"{file_path}:{function_name or 'all'}"
        return self.code_to_tests.get(key, [])

    def get_code_impact(self, test_id: str) -> Dict:
        """Get impact of a test on codebase."""
        test = self.tests.get(test_id)
        if not test:
            return {}

        return {
            "test_name": test.test_name,
            "covers": len(test.code_locations),
            "files": list(set(loc.file_path for loc in test.code_locations)),
            "functions": [loc.function_name for loc in test.code_locations
                         if loc.function_name],
            "impact_area": test.impact_area
        }

    def get_feature_coverage(self, feature_name: str) -> CoverageReport:
        """Get coverage report for a feature."""
        if feature_name not in self.features:
            return None

        feature_code = self.features[feature_name]
        covered_tests = []
        uncovered_code = []

        for location in feature_code:
            tests = self.get_tests_for_code(location.file_path,
                                           location.function_name)
            if tests:
                covered_tests.extend(tests)
            else:
                uncovered_code.append(location)

        total = len(feature_code)
        covered = total - len(uncovered_code)
        coverage_pct = (covered / total * 100) if total > 0 else 0

        return CoverageReport(
            feature_name=feature_name,
            covered_by_tests=covered_tests,
            uncovered_code=uncovered_code,
            coverage_percentage=coverage_pct
        )

    def generate_coverage_matrix(self) -> Dict[str, Dict]:
        """Generate matrix of tests vs features."""
        matrix = {}

        for feature_name in self.features:
            report = self.get_feature_coverage(feature_name)
            if report:
                matrix[feature_name] = {
                    "coverage": report.coverage_percentage,
                    "test_count": len(report.covered_by_tests),
                    "uncovered": len(report.uncovered_code),
                    "status": "✓ Covered" if report.coverage_percentage == 100 else "⚠ Partial"
                }

        return matrix

    def get_untested_code(self) -> List[CodeLocation]:
        """Get all code that isn't tested."""
        untested = []

        for tests in self.code_to_tests.values():
            if not tests:
                # Find the location
                for test in self.tests.values():
                    if test not in tests:
                        untested.extend(test.code_locations)

        return untested

    def suggest_test_coverage(self, file_path: str) -> str:
        """Suggest what to test in a file."""
        suggestions = []

        tests = self.get_tests_for_code(file_path)
        if tests:
            suggestions.append(f"✓ This file has {len(tests)} test(s)")
        else:
            suggestions.append(f"⚠ No tests found for {file_path}")
            suggestions.append("Consider adding tests for:")
            suggestions.append("- Main functions")
            suggestions.append("- Error handling")
            suggestions.append("- Edge cases")

        return "\n".join(suggestions)

    def generate_impact_report(self) -> Dict:
        """Generate report showing test impact across codebase."""
        report = {
            "total_tests": len(self.tests),
            "total_features": len(self.features),
            "coverage_by_area": {},
            "high_impact_tests": [],
            "low_coverage_features": []
        }

        # Calculate coverage by area
        for feature in self.features:
            coverage_report = self.get_feature_coverage(feature)
            if coverage_report:
                area = feature.split('_')[0]
                if area not in report["coverage_by_area"]:
                    report["coverage_by_area"][area] = []
                report["coverage_by_area"][area].append(coverage_report.coverage_percentage)

        # Find high-impact tests
        for test_id, test in self.tests.items():
            impact = self.get_code_impact(test_id)
            if impact.get('covers', 0) > 5:
                report["high_impact_tests"].append({
                    "test": test.test_name,
                    "covers": impact['covers']
                })

        # Find low-coverage features
        for feature in self.features:
            report_data = self.get_feature_coverage(feature)
            if report_data and report_data.coverage_percentage < 50:
                report["low_coverage_features"].append({
                    "feature": feature,
                    "coverage": report_data.coverage_percentage
                })

        return report
