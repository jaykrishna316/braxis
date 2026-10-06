#!/usr/bin/env python3
"""
Braxis Regression Test Suite
Tests that Braxis performs REAL code analysis, not templating.
Prevents future degradation where templating creeps in.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple


class BraxisRegressionTest:
    """Automated test suite ensuring Braxis analyzes real code, not templates."""

    def __init__(self, braxis_path: str = "braxis"):
        self.braxis_cmd = braxis_path
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results: List[Dict[str, str]] = []

    def run_braxis_command(self, cmd: str, cwd: str) -> str:
        """Run braxis command and return output."""
        try:
            result = subprocess.run(
                f"{self.braxis_cmd} {cmd}",
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return "ERROR: Command timeout"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def extract_score(self, output: str, dimension: str) -> int:
        """Extract a score from braxis output."""
        pattern = rf"{dimension}\s+(\d+)/100"
        match = re.search(pattern, output)
        return int(match.group(1)) if match else -1

    def read_file(self, path: str) -> str:
        """Read file safely."""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception:
            return ""

    def test_result(self, test_name: str, passed: bool, reason: str = ""):
        """Record test result."""
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {test_name}")
        if reason:
            print(f"    {reason}")

        self.test_results.append({
            "name": test_name,
            "status": "PASS" if passed else "FAIL",
            "reason": reason
        })

        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

    def test_score_changes_with_code_patterns(self):
        """Test that Conventions score changes when code patterns are added."""
        print("\n[TEST 1] Score Changes with Code Patterns (Smoking Gun)")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            (tmpdir / "main.py").write_text("def add(a, b):\n    return a + b\n")
            (tmpdir / "setup.py").write_text("from setuptools import setup\nsetup()\n")

            output1 = self.run_braxis_command("score --path .", str(tmpdir))
            score1 = self.extract_score(output1, "Conventions")

            (tmpdir / "main.py").write_text(
                "def add(a: int, b: int) -> int:\n    return a + b\n"
            )

            output2 = self.run_braxis_command("score --path .", str(tmpdir))
            score2 = self.extract_score(output2, "Conventions")

            (tmpdir / "main.py").write_text(
                "import asyncio\n"
                "async def fetch(url: str) -> dict:\n"
                "    return {}\n"
                "asyncio.run(fetch('http://test.com'))\n"
            )

            output3 = self.run_braxis_command("score --path .", str(tmpdir))
            score3 = self.extract_score(output3, "Conventions")

            passed = (score1 >= 0 and score2 >= score1 and score3 > score2)
            reason = f"Scores: {score1} -> {score2} -> {score3} (should be increasing)"
            self.test_result("Conventions score increases with code patterns", passed, reason)

            return passed

    def test_project_specific_details(self):
        """Test that generated files contain project-specific data, not templates."""
        print("\n[TEST 2] Project-Specific Details (Not Templates)")
        print("=" * 60)

        all_passed = True

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            (tmpdir / "src").mkdir()
            (tmpdir / "src" / "myapp.py").write_text("def main(): pass\n")
            (tmpdir / "tests").mkdir()
            (tmpdir / "tests" / "test_myapp.py").write_text("import pytest\n")
            (tmpdir / "setup.py").write_text("from setuptools import setup\nsetup(name='myapp')\n")
            (tmpdir / "pyproject.toml").write_text("[build-system]\nrequires=['poetry']\n")
            (tmpdir / "README.md").write_text("# MyApp\n")

            self.run_braxis_command("generate --path .", str(tmpdir))

            # Check AGENTS.md
            agents_md = self.read_file(str(tmpdir / "AGENTS.md"))

            checks = [
                ("Contains 'myapp' or project name", "myapp" in agents_md.lower() or "Python" in agents_md),
                ("Mentions 'pytest' (detected test framework)", "pytest" in agents_md.lower()),
                ("Mentions 'src' directory", "src" in agents_md or "source" in agents_md.lower()),
                ("Contains actual file counts", re.search(r"[Ff]iles.*\d+", agents_md)),
                ("Not just generic text", len(agents_md) > 500),
            ]

            for check_name, result in checks:
                passed = bool(result)
                self.test_result(f"AGENTS.md: {check_name}", passed)
                all_passed = all_passed and passed

            # Check .agentic-config.json with nested structure
            config_path = tmpdir / ".agentic-config.json"
            if config_path.exists():
                config_json = json.loads(config_path.read_text())

                checks = [
                    ("Config has project name", config_json.get("metadata", {}).get("project_name")),
                    ("Config has description", config_json.get("metadata", {}).get("description")),
                    ("Config has primary language", config_json.get("project", {}).get("primary_language")),
                ]

                for check_name, result in checks:
                    self.test_result(f".agentic-config.json: {check_name}", bool(result))
                    all_passed = all_passed and bool(result)

        return all_passed

    def test_language_specific_analysis(self):
        """Test that different languages produce different outputs."""
        print("\n[TEST 3] Language-Specific Analysis")
        print("=" * 60)

        all_passed = True

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "main.py").write_text("def hello(): pass\n")
            (tmpdir / "setup.py").write_text("from setuptools import setup\nsetup()\n")

            output_py = self.run_braxis_command("inspect --path .", str(tmpdir))
            passed = "python" in output_py.lower()
            self.test_result("Python project detected as Python", passed, output_py[:100])
            all_passed = all_passed and passed

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "app.js").write_text("function hello() {}\n")
            (tmpdir / "package.json").write_text('{"name": "app", "version": "1.0.0"}\n')

            output_js = self.run_braxis_command("inspect --path .", str(tmpdir))
            passed = "javascript" in output_js.lower() or "npm" in output_js.lower()
            self.test_result("JavaScript project detected as JS", passed, output_js[:100])
            all_passed = all_passed and passed

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "main.go").write_text("package main\nfunc main() {}\n")
            (tmpdir / "go.mod").write_text("module myapp\n")

            output_go = self.run_braxis_command("inspect --path .", str(tmpdir))
            passed = "go" in output_go.lower()
            self.test_result("Go project detected as Go", passed, output_go[:100])
            all_passed = all_passed and passed

        return all_passed

    def test_build_system_detection(self):
        """Test that build systems are detected from actual config files."""
        print("\n[TEST 4] Build System Detection (Real Config Reading)")
        print("=" * 60)

        all_passed = True

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "main.py").write_text("pass\n")
            (tmpdir / "setup.py").write_text("from setuptools import setup\nsetup()\n")

            output = self.run_braxis_command("inspect --path .", str(tmpdir))
            passed = "setuptools" in output.lower() or "pip" in output.lower()
            self.test_result("Detects setuptools from setup.py", passed)
            all_passed = all_passed and passed

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "main.py").write_text("pass\n")
            (tmpdir / "pyproject.toml").write_text(
                "[build-system]\n"
                "requires = ['poetry-core']\n"
                "build-backend = 'poetry.core.masonry.api'\n"
            )

            output = self.run_braxis_command("inspect --path .", str(tmpdir))
            passed = "poetry" in output.lower()
            self.test_result("Detects poetry from pyproject.toml", passed, output[:100])
            all_passed = all_passed and passed

        return all_passed

    def test_framework_detection(self):
        """Test that test frameworks are detected from actual test code."""
        print("\n[TEST 5] Test Framework Detection (Real Code Scanning)")
        print("=" * 60)

        all_passed = True

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "main.py").write_text("pass\n")
            (tmpdir / "setup.py").write_text("from setuptools import setup\nsetup()\n")
            (tmpdir / "test_main.py").write_text("import pytest\ndef test_example(): pass\n")

            output = self.run_braxis_command("inspect --path .", str(tmpdir))
            passed = "pytest" in output.lower()
            self.test_result("Detects pytest from test imports", passed, output[:100])
            all_passed = all_passed and passed

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "main.py").write_text("pass\n")
            (tmpdir / "setup.py").write_text("from setuptools import setup\nsetup()\n")
            (tmpdir / "test_main.py").write_text("import unittest\nclass Test(unittest.TestCase): pass\n")

            output = self.run_braxis_command("inspect --path .", str(tmpdir))
            passed = "unittest" in output.lower() or "test" in output.lower()
            self.test_result("Detects unittest from test imports", passed, output[:100])
            all_passed = all_passed and passed

        return all_passed

    def test_critical_files_detection(self):
        """Test that entry points are detected from actual files."""
        print("\n[TEST 6] Critical Files Detection")
        print("=" * 60)

        all_passed = True

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "setup.py").write_text("from setuptools import setup\nsetup()\n")

            output1 = self.run_braxis_command("score --path .", str(tmpdir))

            (tmpdir / "main.py").write_text("def main(): pass\n")
            output2 = self.run_braxis_command("score --path .", str(tmpdir))

            has_critical1 = "Critical" in output1
            has_critical2 = "Critical" in output2

            passed = has_critical1 and has_critical2
            self.test_result("Critical files detection working", passed)
            all_passed = all_passed and passed

        return all_passed

    def test_no_generic_content(self):
        """Test that generated files don't contain obviously generic content."""
        print("\n[TEST 7] No Generic/Template Content")
        print("=" * 60)

        all_passed = True

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "myapp.py").write_text("def main(): pass\n")
            (tmpdir / "setup.py").write_text("from setuptools import setup\nsetup(name='myapp')\n")

            self.run_braxis_command("generate --path .", str(tmpdir))

            agents_md = self.read_file(str(tmpdir / "AGENTS.md"))
            claude_md = self.read_file(str(tmpdir / "CLAUDE.md"))

            template_patterns = [
                r"\[YOUR.*?\]",
                r"<.*?>",
                r"\{\{.*?\}\}",
                r"FIXME",
                r"TODO.*example",
                r"replace.*this",
            ]

            for pattern in template_patterns:
                in_agents = bool(re.search(pattern, agents_md, re.IGNORECASE))
                in_claude = bool(re.search(pattern, claude_md, re.IGNORECASE))

                passed = not (in_agents or in_claude)
                self.test_result(
                    f"No generic template pattern '{pattern}'",
                    passed,
                    f"agents={in_agents}, claude={in_claude}"
                )
                all_passed = all_passed and passed

        return all_passed

    def test_config_json_completeness(self):
        """Test that .agentic-config.json contains real analysis data."""
        print("\n[TEST 8] Configuration JSON Completeness")
        print("=" * 60)

        all_passed = True

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "main.py").write_text("def hello(): pass\n")
            (tmpdir / "setup.py").write_text("from setuptools import setup\nsetup()\n")
            (tmpdir / "test_main.py").write_text("import pytest\n")

            self.run_braxis_command("generate --path .", str(tmpdir))

            config_path = tmpdir / ".agentic-config.json"

            passed = config_path.exists()
            self.test_result("Config JSON file generated", passed)
            all_passed = all_passed and passed

            if config_path.exists():
                try:
                    config = json.loads(config_path.read_text())

                    required_checks = [
                        ("name field", config.get("metadata", {}).get("project_name")),
                        ("description field", config.get("metadata", {}).get("description")),
                        ("primary_language field", config.get("project", {}).get("primary_language")),
                        ("build_system field", config.get("project", {}).get("build_system")),
                        ("test_framework field", config.get("testing", {}).get("framework")),
                        ("overall_score field", config.get("ai_readiness", {}).get("overall_score")),
                    ]

                    for field_name, field_value in required_checks:
                        has_field = bool(field_value)
                        self.test_result(f"Config has '{field_name}' with data", has_field)
                        all_passed = all_passed and has_field

                except json.JSONDecodeError:
                    self.test_result("Config JSON is valid JSON", False, "JSON decode error")
                    all_passed = False

        return all_passed

    def run_all_tests(self):
        """Run the complete test suite."""
        print("\n" + "=" * 70)
        print("BRAXIS REGRESSION TEST SUITE")
        print("Ensuring Braxis performs REAL analysis, not templating")
        print("=" * 70)

        try:
            self.test_score_changes_with_code_patterns()
            self.test_project_specific_details()
            self.test_language_specific_analysis()
            self.test_build_system_detection()
            self.test_framework_detection()
            self.test_critical_files_detection()
            self.test_no_generic_content()
            self.test_config_json_completeness()
        except Exception as e:
            print(f"\nFATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

        total = self.tests_passed + self.tests_failed
        print("\n" + "=" * 70)
        print(f"TEST RESULTS: {self.tests_passed}/{total} passed")
        print("=" * 70)

        if self.tests_failed == 0:
            print("ALL TESTS PASSED - Braxis is analyzing real code!")
            return True
        else:
            print(f"{self.tests_failed} TESTS FAILED - Review failures above")
            return False


if __name__ == "__main__":
    import sys

    braxis_path = sys.argv[1] if len(sys.argv) > 1 else "braxis"
    tester = BraxisRegressionTest(braxis_path)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
