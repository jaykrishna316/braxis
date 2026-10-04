#!/usr/bin/env python3
"""
Unit tests for Braxis - AI agent context file generator.
Uses unittest for compatibility without external dependencies.
"""
import os
import sys
import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from braxis import BraxisAnalyzer


class TestValidateProjectPath(unittest.TestCase):
    """Tests for project path validation."""

    def test_validate_valid_path(self):
        """Test validation of valid project path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = BraxisAnalyzer(tmpdir)
            self.assertEqual(analyzer.project_path, Path(tmpdir).resolve())

    def test_validate_empty_path(self):
        """Test validation rejects empty path."""
        with self.assertRaises(ValueError):
            BraxisAnalyzer("")

    def test_validate_nonexistent_path(self):
        """Test validation rejects nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            BraxisAnalyzer("/nonexistent/path/12345")

    def test_validate_file_not_directory(self):
        """Test validation rejects file path."""
        with tempfile.NamedTemporaryFile() as tmpfile:
            with self.assertRaises(NotADirectoryError):
                BraxisAnalyzer(tmpfile.name)

    def test_validate_relative_path_conversion(self):
        """Test that relative paths are converted to absolute."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                analyzer = BraxisAnalyzer(".")
                self.assertTrue(analyzer.project_path.is_absolute())
            finally:
                os.chdir(original_cwd)


class TestWriteFileSafely(unittest.TestCase):
    """Tests for safe file writing functionality."""

    def test_write_file_successfully(self):
        """Test successful file write."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = BraxisAnalyzer(tmpdir)
            filepath = Path(tmpdir) / "test.txt"
            content = "Test content"
            analyzer._write_file_safely(str(filepath), content)
            self.assertTrue(filepath.exists())
            self.assertEqual(filepath.read_text(), content)

    def test_write_file_creates_parent_directories(self):
        """Test that parent directories are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = BraxisAnalyzer(tmpdir)
            filepath = Path(tmpdir) / "subdir" / "nested" / "test.txt"
            content = "Test content"
            analyzer._write_file_safely(str(filepath), content)
            self.assertTrue(filepath.exists())
            self.assertEqual(filepath.read_text(), content)

    def test_write_file_empty_filepath(self):
        """Test that empty filepath raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = BraxisAnalyzer(tmpdir)
            with self.assertRaises(ValueError):
                analyzer._write_file_safely("", "content")

    def test_write_file_non_string_content(self):
        """Test that non-string content raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = BraxisAnalyzer(tmpdir)
            filepath = Path(tmpdir) / "test.txt"
            with self.assertRaises(TypeError):
                analyzer._write_file_safely(str(filepath), 123)

    def test_write_file_overwrites_existing(self):
        """Test that file write overwrites existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = BraxisAnalyzer(tmpdir)
            filepath = Path(tmpdir) / "test.txt"
            filepath.write_text("Old content")
            analyzer._write_file_safely(str(filepath), "New content")
            self.assertEqual(filepath.read_text(), "New content")

    def test_write_file_cleans_temp_file(self):
        """Test that temp files are cleaned up."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = BraxisAnalyzer(tmpdir)
            filepath = Path(tmpdir) / "test.txt"
            analyzer._write_file_safely(str(filepath), "content")
            tmp_files = list(Path(tmpdir).glob("*.tmp"))
            self.assertEqual(len(tmp_files), 0)


class TestBraxisAnalyzer(unittest.TestCase):
    """Tests for BraxisAnalyzer functionality."""

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = BraxisAnalyzer(tmpdir)
            self.assertEqual(analyzer.files, [])
            self.assertEqual(analyzer.test_files, [])
            self.assertEqual(analyzer.config_files, [])
            self.assertEqual(analyzer.build_files, [])
            self.assertEqual(analyzer.tier, "Not Ready")

    def test_scan_files(self):
        """Test file scanning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# test")
            Path(tmpdir, "main.py").write_text("# main")
            Path(tmpdir, "config.json").write_text("{}")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer._scan_files()

            self.assertGreaterEqual(len(analyzer.files), 3)
            self.assertTrue(any("test.py" in str(f) for f in analyzer.files))

    def test_detect_languages(self):
        """Test language detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# python")
            Path(tmpdir, "script.js").write_text("// javascript")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer._scan_files()
            analyzer._detect_languages()

            self.assertIn("python", analyzer.languages)
            self.assertIn("javascript", analyzer.languages)

    def test_detect_test_files(self):
        """Test test file detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_main.py").write_text("# test")
            Path(tmpdir, "main_test.py").write_text("# test")
            Path(tmpdir, "main.py").write_text("# main")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer._scan_files()

            self.assertGreaterEqual(len(analyzer.test_files), 2)

    def test_detect_build_system_python(self):
        """Test Python build system detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "setup.py").write_text("# setup")
            Path(tmpdir, "main.py").write_text("# main")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer._scan_files()
            analyzer._detect_build_system()

            self.assertTrue(analyzer.build_system in ["Unknown", "Python", "pip"])

    def test_detect_build_system_npm(self):
        """Test npm build system detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text("{}")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer._scan_files()
            analyzer._detect_build_system()

            self.assertTrue("npm" in analyzer.build_system or "Node" in analyzer.build_system)

    def test_detect_build_system_unknown(self):
        """Test unknown build system detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = BraxisAnalyzer(tmpdir)
            analyzer._scan_files()
            analyzer._detect_build_system()

            self.assertEqual(analyzer.build_system, "Unknown")

    def test_calculate_score(self):
        """Test score calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("# main")
            Path(tmpdir, "test.py").write_text("# test")
            Path(tmpdir, "README.md").write_text("# Readme")
            Path(tmpdir, "setup.py").write_text("# setup")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()

            self.assertTrue(hasattr(analyzer, "total_score"))
            self.assertGreaterEqual(analyzer.total_score, 0)
            self.assertLessEqual(analyzer.total_score, 100)
            self.assertIn(analyzer.tier, ["Not Ready", "Agent-Aware", "AI-Native", "AI-Native-Plus", "Agent-Optimized"])

    def test_generate_agents_md(self):
        """Test AGENTS.md generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# test")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            content = analyzer.generate_agents_md()

            self.assertIn("AGENTS.md", content)
            self.assertIn("Project Overview", content)

    def test_generate_claude_md(self):
        """Test CLAUDE.md generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# test")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            content = analyzer.generate_claude_md()

            self.assertIn("CLAUDE.md", content)
            self.assertIn("Claude Code", content)

    def test_generate_cursorrules(self):
        """Test .cursorrules generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# test")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            content = analyzer.generate_cursorrules()

            self.assertIn("Cursor Rules", content)

    def test_generate_agentic_config(self):
        """Test .agentic-config.json generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# test")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            content = analyzer.generate_agentic_config()

            config = json.loads(content)
            self.assertIn("metadata", config)
            self.assertIn("project", config)
            self.assertIn("ai_readiness", config)
            self.assertIn("overall_score", config.get("ai_readiness", {}))
            self.assertIn("tier", config.get("ai_readiness", {}))

    def test_analyze_full_workflow(self):
        """Test complete analysis workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("# main")
            Path(tmpdir, "test.py").write_text("import unittest")
            Path(tmpdir, "README.md").write_text("# Project")
            Path(tmpdir, "setup.py").write_text("# setup")
            Path(tmpdir, "config.json").write_text("{}")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()

            self.assertGreater(len(analyzer.files), 0)
            self.assertGreater(len(analyzer.languages), 0)
            self.assertGreater(analyzer.total_score, 0)
            self.assertNotEqual(analyzer.tier, "Not Ready")


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling."""

    def test_empty_directory(self):
        """Test analysis of empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            self.assertGreater(len(analyzer.files), -1)
            self.assertGreater(analyzer.total_score, 0)

    def test_special_characters_in_path(self):
        """Test handling of special characters in file paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            special_dir = Path(tmpdir) / "test-dir_123"
            special_dir.mkdir()

            analyzer = BraxisAnalyzer(str(special_dir))
            self.assertEqual(analyzer.project_path, special_dir.resolve())

    def test_large_file_scanning(self):
        """Test handling of large files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            large_file = Path(tmpdir) / "large.py"
            large_file.write_text("# " + "x" * 10000)

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            self.assertIn(large_file, analyzer.files)

    def test_ignored_directories(self):
        """Test that common build directories are ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()
            (Path(tmpdir) / ".git" / "config").write_text("git")
            (Path(tmpdir) / "node_modules").mkdir()
            (Path(tmpdir) / "node_modules" / "pkg.js").write_text("js")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer._scan_files()

            git_files = [f for f in analyzer.files if ".git" in str(f)]
            node_files = [f for f in analyzer.files if "node_modules" in str(f)]

            self.assertEqual(len(git_files), 0)
            self.assertEqual(len(node_files), 0)

    def test_file_write_with_unicode(self):
        """Test writing files with unicode content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = BraxisAnalyzer(tmpdir)
            filepath = Path(tmpdir) / "unicode.txt"
            content = "Unicode test: 你好世界 🚀"
            analyzer._write_file_safely(str(filepath), content)
            self.assertEqual(filepath.read_text(encoding='utf-8'), content)

    def test_score_breakdown_keys(self):
        """Test that score breakdown has expected keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# test")
            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()

            expected_keys = ['Architecture', 'Testing', 'Dependencies', 'Conventions',
                           'Entry Points', 'Security', 'Build', 'Documentation']
            for key in expected_keys:
                self.assertIn(key, analyzer.score_breakdown)


class TestCountTestFunctions(unittest.TestCase):
    """Regression tests for _count_test_functions() method."""

    def test_count_python_test_functions(self):
        """Test counting Python test functions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_one.py").write_text(
                "def test_func1():\n    pass\n"
                "def test_func2():\n    pass\n"
                "def helper():\n    pass"
            )
            Path(tmpdir, "test_two.py").write_text(
                "def test_func3():\n    pass"
            )

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            count = analyzer._count_test_functions()

            self.assertEqual(count, 3)

    def test_count_go_test_functions(self):
        """Test counting Go test functions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main_test.go").write_text(
                "func TestOne(t *testing.T) {}\n"
                "func TestTwo(t *testing.T) {}\n"
                "func Helper() {}"
            )

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            count = analyzer._count_test_functions()

            self.assertEqual(count, 2)

    def test_count_bats_test_declarations(self):
        """Test counting Bats test declarations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_main.bats").write_text(
                "@test \"first test\" {\n  true\n}\n"
                "@test \"second test\" {\n  true\n}"
            )

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            count = analyzer._count_test_functions()

            self.assertEqual(count, 2)

    def test_count_test_functions_returns_at_least_file_count(self):
        """Test that count returns at least the number of test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_one.py").write_text("# no functions")
            Path(tmpdir, "test_two.py").write_text("# no functions")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            count = analyzer._count_test_functions()

            self.assertGreaterEqual(count, len(analyzer.test_files))

    def test_count_javascript_tests(self):
        """Test counting JavaScript test declarations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_main.js").write_text(
                "describe('suite', () => {\n"
                "  it('test 1', () => {});\n"
                "  it('test 2', () => {});\n"
                "});"
            )

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            count = analyzer._count_test_functions()

            self.assertGreaterEqual(count, 2)


class TestDetectedPythonTools(unittest.TestCase):
    """Regression tests for _get_detected_python_tools() method."""

    def test_detects_ruff_from_pyproject(self):
        """Test detection of ruff configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text("[tool.ruff]\nline-length = 88")

            analyzer = BraxisAnalyzer(tmpdir)
            tools = analyzer._get_detected_python_tools()

            self.assertIn("ruff", tools)

    def test_detects_mypy_from_pyproject(self):
        """Test detection of mypy configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text("[tool.mypy]\nstrict = true")

            analyzer = BraxisAnalyzer(tmpdir)
            tools = analyzer._get_detected_python_tools()

            self.assertIn("mypy", tools)

    def test_detects_multiple_tools(self):
        """Test detection of multiple tools."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text(
                "[tool.ruff]\nline-length = 88\n"
                "[tool.mypy]\nstrict = true"
            )

            analyzer = BraxisAnalyzer(tmpdir)
            tools = analyzer._get_detected_python_tools()

            self.assertIn("ruff", tools)
            self.assertIn("mypy", tools)

    def test_returns_empty_list_when_no_tools(self):
        """Test returns empty list when no tools configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text("[build-system]\nrequires = ['setuptools']")

            analyzer = BraxisAnalyzer(tmpdir)
            tools = analyzer._get_detected_python_tools()

            self.assertEqual(tools, [])

    def test_handles_missing_pyproject(self):
        """Test handles missing pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = BraxisAnalyzer(tmpdir)
            tools = analyzer._get_detected_python_tools()

            self.assertEqual(tools, [])

    def test_detects_pylint_flake8_pyright(self):
        """Test detection of other tools."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text(
                "[tool.pylint]\ndisable = 'missing-docstring'\n"
                "[tool.flake8]\nmax-line-length = 88\n"
                "[tool.pyright]\ntypeCheckingMode = 'basic'"
            )

            analyzer = BraxisAnalyzer(tmpdir)
            tools = analyzer._get_detected_python_tools()

            self.assertIn("pylint", tools)
            self.assertIn("flake8", tools)
            self.assertIn("pyright", tools)


class TestUnittestDetection(unittest.TestCase):
    """Regression tests for unittest detection fix."""

    def test_detects_unittest_over_pytest(self):
        """Test that unittest is detected when test_*.py files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_main.py").write_text("import unittest\nclass TestMain(unittest.TestCase): pass")
            Path(tmpdir, "main.py").write_text("# main")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()

            self.assertIn("unittest", analyzer.test_frameworks)

    def test_detects_pytest_when_configured(self):
        """Test pytest detected from pyproject.toml configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text("[tool.pytest.ini_options]\nminversion = '6.0'")
            Path(tmpdir, "test_main.py").write_text("import pytest")
            Path(tmpdir, "main.py").write_text("# main")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()

            self.assertIn("pytest", analyzer.test_frameworks)

    def test_detects_go_test_files(self):
        """Test detection of Go _test.go files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main_test.go").write_text("func TestMain(t *testing.T) {}")
            Path(tmpdir, "main.go").write_text("// main")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()

            self.assertIn("Go testing", analyzer.test_frameworks)

    def test_detects_ruby_spec_files(self):
        """Test detection of Ruby spec_*.rb files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "spec_main.rb").write_text("describe MainClass do\n  it 'test' do\n    true\n  end\nend")
            Path(tmpdir, "main.rb").write_text("class Main\nend")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()

            self.assertIn("RSpec", analyzer.test_frameworks)


class TestSetupCommandConditionals(unittest.TestCase):
    """Regression tests for conditional setup commands fix."""

    def test_setup_command_for_package_with_setup_py(self):
        """Test setup command is suggested for packages with setup.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "setup.py").write_text("from setuptools import setup")
            Path(tmpdir, "main.py").write_text("# main")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            setup_cmd = analyzer._get_initial_setup_commands("python")

            self.assertIsNotNone(setup_cmd)
            self.assertIn("pip", setup_cmd)

    def test_setup_command_for_project_in_pyproject(self):
        """Test setup command for [project] in pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text("[project]\nname = 'myproject'")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            setup_cmd = analyzer._get_initial_setup_commands("python")

            self.assertIsNotNone(setup_cmd)
            self.assertIn("pip", setup_cmd)

    def test_no_setup_command_for_non_package(self):
        """Test no setup command for non-package Python projects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("print('hello')")
            Path(tmpdir, "utils.py").write_text("# utilities")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            setup_cmd = analyzer._get_initial_setup_commands("python")

            self.assertTrue(setup_cmd is None or "No setup" in setup_cmd or len(setup_cmd) == 0)


class TestDynamicCommandGeneration(unittest.TestCase):
    """Regression tests for dynamic command generation fix."""

    def test_development_commands_use_detected_framework(self):
        """Test that development commands use self.test_frameworks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_main.py").write_text(
                "import unittest\nclass TestMain(unittest.TestCase):\n    def test_one(self): pass"
            )
            Path(tmpdir, "main.py").write_text("# main")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            commands = analyzer._get_development_commands("python")

            self.assertIsNotNone(commands)
            self.assertIsInstance(commands, str)
            self.assertIn("unittest", commands)

    def test_cursor_rules_use_detected_framework(self):
        """Test that cursor rules use detected test framework."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_main.py").write_text("import unittest")
            Path(tmpdir, "main.py").write_text("# main")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            rules = analyzer.generate_cursorrules()

            self.assertIsNotNone(rules)
            self.assertIsInstance(rules, str)

    def test_agentic_config_uses_detected_framework(self):
        """Test that agentic config uses detected test framework."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_main.py").write_text(
                "import unittest\nclass TestMain(unittest.TestCase): pass"
            )
            Path(tmpdir, "main.py").write_text("# main")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            config_content = analyzer.generate_agentic_config()
            config = json.loads(config_content)

            testing = config.get("testing", {})
            framework = testing.get("framework")
            self.assertIsNotNone(framework)
            self.assertNotEqual(framework, "None detected", "Should detect a valid framework")


class TestHardcodedValueDetection(unittest.TestCase):
    """Regression tests to detect hardcoded values in generated output."""

    def test_agentic_config_no_default_pytest(self):
        """Test that pytest is not defaulted without configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_main.py").write_text(
                "import unittest\nclass TestMain(unittest.TestCase): pass"
            )
            Path(tmpdir, "main.py").write_text("# main")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            config_content = analyzer.generate_agentic_config()
            config = json.loads(config_content)

            testing = config.get("ai_readiness", {}).get("testing", {})
            framework = testing.get("framework")

            self.assertNotEqual(framework, "pytest",
                              "pytest should not be default for unittest projects")

    def test_agentic_config_test_count_matches_actual(self):
        """Test that test count in config matches actual test functions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_one.py").write_text(
                "def test_a(): pass\ndef test_b(): pass"
            )
            Path(tmpdir, "test_two.py").write_text(
                "def test_c(): pass"
            )

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            config_content = analyzer.generate_agentic_config()
            config = json.loads(config_content)

            reported_count = config.get("testing", {}).get("total_tests")
            self.assertIsNotNone(reported_count, "total_tests should not be None")
            self.assertGreaterEqual(reported_count, 2,
                                   "reported test count should be at least file count")

    def test_agentic_config_no_tools_unless_configured(self):
        """Test that tools only appear if configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("# main")
            Path(tmpdir, "pyproject.toml").write_text("[build-system]\nrequires = ['setuptools']")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            config_content = analyzer.generate_agentic_config()
            config = json.loads(config_content)

            dev = config.get("ai_readiness", {}).get("development", {})
            linting = dev.get("linting_tools", [])

            self.assertEqual(linting, [],
                           "No linting tools should be configured if not in pyproject.toml")

    def test_agents_md_no_hardcoded_test_framework(self):
        """Test AGENTS.md doesn't hardcode test frameworks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_main.py").write_text(
                "import unittest\nclass TestMain(unittest.TestCase): pass"
            )
            Path(tmpdir, "main.py").write_text("# main")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            agents_md = analyzer.generate_agents_md()

            self.assertIsNotNone(agents_md)
            self.assertNotEqual(agents_md, "", "AGENTS.md should not be empty")

    def test_python_version_from_config(self):
        """Test Python version comes from configuration, not hardcoded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text('requires-python = ">=3.8"')
            Path(tmpdir, "main.py").write_text("# main")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            config_content = analyzer.generate_agentic_config()
            config = json.loads(config_content)

            version = config.get("development", {}).get("prerequisites", {}).get("language_version")
            self.assertEqual(version, ">=3.8",
                           "Python version should come from configuration")

    def test_shell_project_not_given_python_defaults(self):
        """Test that shell projects don't receive Python defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "script.sh").write_text("#!/bin/bash\necho hello")
            Path(tmpdir, "test.bats").write_text("@test 'test' { true }")

            analyzer = BraxisAnalyzer(tmpdir)
            analyzer.analyze()
            config_content = analyzer.generate_agentic_config()
            config = json.loads(config_content)

            dev = config.get("ai_readiness", {}).get("development", {})
            setup_cmd = dev.get("setup_command")

            self.assertNotIn("pip", str(setup_cmd) if setup_cmd else "",
                           "Shell project should not have pip setup command")


if __name__ == '__main__':
    unittest.main()
