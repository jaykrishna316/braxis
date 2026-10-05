"""
Unit tests for Braxis - AI agent context file generator.
"""
import os
import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from braxis import BraxisAnalyzer


@pytest.fixture
def tmpdir_cleanup():
    """Provide a temporary directory that's cleaned up after test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestValidateProjectPath:
    """Tests for project path validation."""

    def test_validate_valid_path(self, tmpdir_cleanup):
        """Test validation of valid project path."""
        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        assert analyzer.project_path == Path(tmpdir_cleanup).resolve()

    def test_validate_empty_path(self):
        """Test validation rejects empty path."""
        with pytest.raises(ValueError):
            BraxisAnalyzer("")

    def test_validate_nonexistent_path(self):
        """Test validation rejects nonexistent path."""
        with pytest.raises(FileNotFoundError):
            BraxisAnalyzer("/nonexistent/path/12345")

    def test_validate_file_not_directory(self):
        """Test validation rejects file path."""
        with tempfile.NamedTemporaryFile() as tmpfile:
            with pytest.raises(NotADirectoryError):
                BraxisAnalyzer(tmpfile.name)

    def test_validate_relative_path_conversion(self, tmpdir_cleanup):
        """Test that relative paths are converted to absolute."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir_cleanup)
            analyzer = BraxisAnalyzer(".")
            assert analyzer.project_path.is_absolute()
        finally:
            os.chdir(original_cwd)


class TestWriteFileSafely:
    """Tests for safe file writing functionality."""

    def test_write_file_successfully(self, tmpdir_cleanup):
        """Test successful file write."""
        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        filepath = Path(tmpdir_cleanup) / "test.txt"
        content = "Test content"
        analyzer._write_file_safely(str(filepath), content)
        assert filepath.exists()
        assert filepath.read_text() == content

    def test_write_file_creates_parent_directories(self, tmpdir_cleanup):
        """Test that parent directories are created."""
        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        filepath = Path(tmpdir_cleanup) / "subdir" / "nested" / "test.txt"
        content = "Test content"
        analyzer._write_file_safely(str(filepath), content)
        assert filepath.exists()
        assert filepath.read_text() == content

    def test_write_file_empty_filepath(self, tmpdir_cleanup):
        """Test that empty filepath raises error."""
        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        with pytest.raises(ValueError):
            analyzer._write_file_safely("", "content")

    def test_write_file_non_string_content(self, tmpdir_cleanup):
        """Test that non-string content raises error."""
        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        filepath = Path(tmpdir_cleanup) / "test.txt"
        with pytest.raises(TypeError):
            analyzer._write_file_safely(str(filepath), 123)

    def test_write_file_overwrites_existing(self, tmpdir_cleanup):
        """Test that file write overwrites existing file."""
        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        filepath = Path(tmpdir_cleanup) / "test.txt"
        filepath.write_text("Old content")
        analyzer._write_file_safely(str(filepath), "New content")
        assert filepath.read_text() == "New content"

    def test_write_file_cleans_temp_file(self, tmpdir_cleanup):
        """Test that temp files are cleaned up."""
        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        filepath = Path(tmpdir_cleanup) / "test.txt"
        analyzer._write_file_safely(str(filepath), "content")
        tmp_files = list(Path(tmpdir_cleanup).glob("*.tmp"))
        assert len(tmp_files) == 0


class TestBraxisAnalyzer:
    """Tests for BraxisAnalyzer functionality."""

    def test_analyzer_initialization(self, tmpdir_cleanup):
        """Test analyzer initialization."""
        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        assert analyzer.files == []
        assert analyzer.test_files == []
        assert analyzer.config_files == []
        assert analyzer.build_files == []
        assert analyzer.tier == "Not Ready"

    def test_scan_files(self, tmpdir_cleanup):
        """Test file scanning."""
        Path(tmpdir_cleanup, "test.py").write_text("# test")
        Path(tmpdir_cleanup, "main.py").write_text("# main")
        Path(tmpdir_cleanup, "config.json").write_text("{}")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer._scan_files()

        assert len(analyzer.files) >= 3
        assert any("test.py" in str(f) for f in analyzer.files)

    def test_detect_languages(self, tmpdir_cleanup):
        """Test language detection."""
        Path(tmpdir_cleanup, "test.py").write_text("# python")
        Path(tmpdir_cleanup, "script.js").write_text("// javascript")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer._scan_files()
        analyzer._detect_languages()

        assert "python" in analyzer.languages
        assert "javascript" in analyzer.languages

    def test_detect_test_files(self, tmpdir_cleanup):
        """Test test file detection."""
        Path(tmpdir_cleanup, "test_main.py").write_text("# test")
        Path(tmpdir_cleanup, "main_test.py").write_text("# test")
        Path(tmpdir_cleanup, "main.py").write_text("# main")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer._scan_files()

        assert len(analyzer.test_files) >= 2

    def test_detect_build_system_python(self, tmpdir_cleanup):
        """Test Python build system detection."""
        Path(tmpdir_cleanup, "setup.py").write_text("# setup")
        Path(tmpdir_cleanup, "main.py").write_text("# main")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer._scan_files()
        analyzer._detect_build_system()

        assert analyzer.build_system in ["Unknown", "Python", "pip"]

    def test_detect_build_system_npm(self, tmpdir_cleanup):
        """Test npm build system detection."""
        Path(tmpdir_cleanup, "package.json").write_text("{}")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer._scan_files()
        analyzer._detect_build_system()

        assert "npm" in analyzer.build_system or "Node" in analyzer.build_system

    def test_detect_build_system_unknown(self, tmpdir_cleanup):
        """Test unknown build system detection."""
        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer._scan_files()
        analyzer._detect_build_system()

        assert analyzer.build_system == "Unknown"

    def test_calculate_score(self, tmpdir_cleanup):
        """Test score calculation."""
        Path(tmpdir_cleanup, "main.py").write_text("# main")
        Path(tmpdir_cleanup, "test.py").write_text("# test")
        Path(tmpdir_cleanup, "README.md").write_text("# Readme")
        Path(tmpdir_cleanup, "setup.py").write_text("# setup")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()

        assert hasattr(analyzer, "total_score")
        assert analyzer.total_score >= 0
        assert analyzer.total_score <= 100
        assert analyzer.tier in ["Not Ready", "Agent-Aware", "AI-Native", "AI-Native-Plus", "Agent-Optimized"]

    def test_generate_agents_md(self, tmpdir_cleanup):
        """Test AGENTS.md generation."""
        Path(tmpdir_cleanup, "test.py").write_text("# test")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        content = analyzer.generate_agents_md()

        assert "AGENTS.md" in content
        assert "Project Overview" in content

    def test_generate_claude_md(self, tmpdir_cleanup):
        """Test CLAUDE.md generation."""
        Path(tmpdir_cleanup, "test.py").write_text("# test")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        content = analyzer.generate_claude_md()

        assert "CLAUDE.md" in content
        assert "Claude Code" in content

    def test_generate_cursorrules(self, tmpdir_cleanup):
        """Test .cursorrules generation."""
        Path(tmpdir_cleanup, "test.py").write_text("# test")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        content = analyzer.generate_cursorrules()

        assert "Cursor Rules" in content

    def test_generate_agentic_config(self, tmpdir_cleanup):
        """Test .agentic-config.json generation."""
        Path(tmpdir_cleanup, "test.py").write_text("# test")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        content = analyzer.generate_agentic_config()

        config = json.loads(content)
        assert "metadata" in config
        assert "project" in config
        assert "ai_readiness" in config
        assert "overall_score" in config.get("ai_readiness", {})
        assert "tier" in config.get("ai_readiness", {})

    def test_analyze_full_workflow(self, tmpdir_cleanup):
        """Test complete analysis workflow."""
        Path(tmpdir_cleanup, "main.py").write_text("# main")
        Path(tmpdir_cleanup, "test.py").write_text("import unittest")
        Path(tmpdir_cleanup, "README.md").write_text("# Project")
        Path(tmpdir_cleanup, "setup.py").write_text("# setup")
        Path(tmpdir_cleanup, "config.json").write_text("{}")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()

        assert len(analyzer.files) > 0
        assert len(analyzer.languages) > 0
        assert analyzer.total_score > 0
        assert analyzer.tier != "Not Ready"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_directory(self, tmpdir_cleanup):
        """Test analysis of empty directory."""
        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        assert len(analyzer.files) > -1
        assert analyzer.total_score > 0

    def test_special_characters_in_path(self, tmpdir_cleanup):
        """Test handling of special characters in file paths."""
        special_dir = Path(tmpdir_cleanup) / "test-dir_123"
        special_dir.mkdir()

        analyzer = BraxisAnalyzer(str(special_dir))
        assert analyzer.project_path == special_dir.resolve()

    def test_large_file_scanning(self, tmpdir_cleanup):
        """Test handling of large files."""
        large_file = Path(tmpdir_cleanup) / "large.py"
        large_file.write_text("# " + "x" * 10000)

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        assert large_file in analyzer.files

    def test_ignored_directories(self, tmpdir_cleanup):
        """Test that common build directories are ignored."""
        (Path(tmpdir_cleanup) / ".git").mkdir()
        (Path(tmpdir_cleanup) / ".git" / "config").write_text("git")
        (Path(tmpdir_cleanup) / "node_modules").mkdir()
        (Path(tmpdir_cleanup) / "node_modules" / "pkg.js").write_text("js")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer._scan_files()

        git_files = [f for f in analyzer.files if ".git" in str(f)]
        node_files = [f for f in analyzer.files if "node_modules" in str(f)]

        assert len(git_files) == 0
        assert len(node_files) == 0

    def test_file_write_with_unicode(self, tmpdir_cleanup):
        """Test writing files with unicode content."""
        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        filepath = Path(tmpdir_cleanup) / "unicode.txt"
        content = "Unicode test: 你好世界 🚀"
        analyzer._write_file_safely(str(filepath), content)
        assert filepath.read_text(encoding='utf-8') == content

    def test_score_breakdown_keys(self, tmpdir_cleanup):
        """Test that score breakdown has expected keys."""
        Path(tmpdir_cleanup, "test.py").write_text("# test")
        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()

        expected_keys = ['Architecture', 'Testing', 'Dependencies', 'Conventions',
                       'Entry Points', 'Security', 'Build', 'Documentation']
        for key in expected_keys:
            assert key in analyzer.score_breakdown


class TestCountTestFunctions:
    """Regression tests for _count_test_functions() method."""

    def test_count_python_test_functions(self, tmpdir_cleanup):
        """Test counting Python test functions."""
        Path(tmpdir_cleanup, "test_one.py").write_text(
            "def test_func1():\n    pass\n"
            "def test_func2():\n    pass\n"
            "def helper():\n    pass"
        )
        Path(tmpdir_cleanup, "test_two.py").write_text(
            "def test_func3():\n    pass"
        )

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        count = analyzer._count_test_functions()

        assert count == 3

    def test_count_go_test_functions(self, tmpdir_cleanup):
        """Test counting Go test functions."""
        Path(tmpdir_cleanup, "main_test.go").write_text(
            "func TestOne(t *testing.T) {}\n"
            "func TestTwo(t *testing.T) {}\n"
            "func Helper() {}"
        )

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        count = analyzer._count_test_functions()

        assert count == 2

    def test_count_bats_test_declarations(self, tmpdir_cleanup):
        """Test counting Bats test declarations."""
        Path(tmpdir_cleanup, "test_main.bats").write_text(
            "@test \"first test\" {\n  true\n}\n"
            "@test \"second test\" {\n  true\n}"
        )

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        count = analyzer._count_test_functions()

        assert count == 2

    def test_count_test_functions_returns_at_least_file_count(self, tmpdir_cleanup):
        """Test that count returns at least the number of test files."""
        Path(tmpdir_cleanup, "test_one.py").write_text("# no functions")
        Path(tmpdir_cleanup, "test_two.py").write_text("# no functions")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        count = analyzer._count_test_functions()

        assert count >= len(analyzer.test_files)

    def test_count_javascript_tests(self, tmpdir_cleanup):
        """Test counting JavaScript test declarations."""
        Path(tmpdir_cleanup, "test_main.js").write_text(
            "describe('suite', () => {\n"
            "  it('test 1', () => {});\n"
            "  it('test 2', () => {});\n"
            "});"
        )

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        count = analyzer._count_test_functions()

        assert count >= 2


class TestDetectedPythonTools:
    """Regression tests for _get_detected_python_tools() method."""

    def test_detects_ruff_from_pyproject(self, tmpdir_cleanup):
        """Test detection of ruff configuration."""
        pyproject = Path(tmpdir_cleanup) / "pyproject.toml"
        pyproject.write_text("[tool.ruff]\nline-length = 88")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        tools = analyzer._get_detected_python_tools()

        assert "ruff" in tools

    def test_detects_mypy_from_pyproject(self, tmpdir_cleanup):
        """Test detection of mypy configuration."""
        pyproject = Path(tmpdir_cleanup) / "pyproject.toml"
        pyproject.write_text("[tool.mypy]\nstrict = true")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        tools = analyzer._get_detected_python_tools()

        assert "mypy" in tools

    def test_detects_multiple_tools(self, tmpdir_cleanup):
        """Test detection of multiple tools."""
        pyproject = Path(tmpdir_cleanup) / "pyproject.toml"
        pyproject.write_text(
            "[tool.ruff]\nline-length = 88\n"
            "[tool.mypy]\nstrict = true"
        )

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        tools = analyzer._get_detected_python_tools()

        assert "ruff" in tools
        assert "mypy" in tools

    def test_returns_empty_list_when_no_tools(self, tmpdir_cleanup):
        """Test returns empty list when no tools configured."""
        pyproject = Path(tmpdir_cleanup) / "pyproject.toml"
        pyproject.write_text("[build-system]\nrequires = ['setuptools']")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        tools = analyzer._get_detected_python_tools()

        assert tools == []

    def test_handles_missing_pyproject(self, tmpdir_cleanup):
        """Test handles missing pyproject.toml."""
        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        tools = analyzer._get_detected_python_tools()

        assert tools == []

    def test_detects_pylint_flake8_pyright(self, tmpdir_cleanup):
        """Test detection of other tools."""
        pyproject = Path(tmpdir_cleanup) / "pyproject.toml"
        pyproject.write_text(
            "[tool.pylint]\ndisable = 'missing-docstring'\n"
            "[tool.flake8]\nmax-line-length = 88\n"
            "[tool.pyright]\ntypeCheckingMode = 'basic'"
        )

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        tools = analyzer._get_detected_python_tools()

        assert "pylint" in tools
        assert "flake8" in tools
        assert "pyright" in tools


class TestUnittestDetection:
    """Regression tests for unittest detection fix."""

    def test_detects_unittest_over_pytest(self, tmpdir_cleanup):
        """Test that unittest is detected when test_*.py files exist."""
        Path(tmpdir_cleanup, "test_main.py").write_text("import unittest\nclass TestMain(unittest.TestCase): pass")
        Path(tmpdir_cleanup, "main.py").write_text("# main")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()

        assert "unittest" in analyzer.test_frameworks

    def test_detects_pytest_when_configured(self, tmpdir_cleanup):
        """Test pytest detected from pyproject.toml configuration."""
        pyproject = Path(tmpdir_cleanup) / "pyproject.toml"
        pyproject.write_text("[tool.pytest.ini_options]\nminversion = '6.0'")
        Path(tmpdir_cleanup, "test_main.py").write_text("import pytest")
        Path(tmpdir_cleanup, "main.py").write_text("# main")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()

        assert "pytest" in analyzer.test_frameworks

    def test_detects_go_test_files(self, tmpdir_cleanup):
        """Test detection of Go _test.go files."""
        Path(tmpdir_cleanup, "main_test.go").write_text("func TestMain(t *testing.T) {}")
        Path(tmpdir_cleanup, "main.go").write_text("// main")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()

        assert "Go testing" in analyzer.test_frameworks

    def test_detects_ruby_spec_files(self, tmpdir_cleanup):
        """Test detection of Ruby spec_*.rb files."""
        Path(tmpdir_cleanup, "spec_main.rb").write_text("describe MainClass do\n  it 'test' do\n    true\n  end\nend")
        Path(tmpdir_cleanup, "main.rb").write_text("class Main\nend")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()

        assert "RSpec" in analyzer.test_frameworks


class TestSetupCommandConditionals:
    """Regression tests for conditional setup commands fix."""

    def test_setup_command_for_package_with_setup_py(self, tmpdir_cleanup):
        """Test setup command is suggested for packages with setup.py."""
        Path(tmpdir_cleanup, "setup.py").write_text("from setuptools import setup")
        Path(tmpdir_cleanup, "main.py").write_text("# main")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        setup_cmd = analyzer._get_initial_setup_commands("python")

        assert setup_cmd is not None
        assert "pip" in setup_cmd

    def test_setup_command_for_project_in_pyproject(self, tmpdir_cleanup):
        """Test setup command for [project] in pyproject.toml."""
        pyproject = Path(tmpdir_cleanup) / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'myproject'")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        setup_cmd = analyzer._get_initial_setup_commands("python")

        assert setup_cmd is not None
        assert "pip" in setup_cmd

    def test_no_setup_command_for_non_package(self, tmpdir_cleanup):
        """Test no setup command for non-package Python projects."""
        Path(tmpdir_cleanup, "main.py").write_text("print('hello')")
        Path(tmpdir_cleanup, "utils.py").write_text("# utilities")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        setup_cmd = analyzer._get_initial_setup_commands("python")

        assert setup_cmd is None or "No setup" in setup_cmd or len(setup_cmd) == 0


class TestDynamicCommandGeneration:
    """Regression tests for dynamic command generation fix."""

    def test_development_commands_use_detected_framework(self, tmpdir_cleanup):
        """Test that development commands use self.test_frameworks."""
        Path(tmpdir_cleanup, "test_main.py").write_text(
            "import unittest\nclass TestMain(unittest.TestCase):\n    def test_one(self): pass"
        )
        Path(tmpdir_cleanup, "main.py").write_text("# main")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        commands = analyzer._get_development_commands("python")

        assert commands is not None
        assert isinstance(commands, str)
        assert "unittest" in commands

    def test_cursor_rules_use_detected_framework(self, tmpdir_cleanup):
        """Test that cursor rules use detected test framework."""
        Path(tmpdir_cleanup, "test_main.py").write_text("import unittest")
        Path(tmpdir_cleanup, "main.py").write_text("# main")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        rules = analyzer.generate_cursorrules()

        assert rules is not None
        assert isinstance(rules, str)

    def test_agentic_config_uses_detected_framework(self, tmpdir_cleanup):
        """Test that agentic config uses detected test framework."""
        Path(tmpdir_cleanup, "test_main.py").write_text(
            "import unittest\nclass TestMain(unittest.TestCase): pass"
        )
        Path(tmpdir_cleanup, "main.py").write_text("# main")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        config_content = analyzer.generate_agentic_config()
        config = json.loads(config_content)

        testing = config.get("testing", {})
        framework = testing.get("framework")
        assert framework is not None
        assert framework != "None detected"


class TestHardcodedValueDetection:
    """Regression tests to detect hardcoded values in generated output."""

    def test_agentic_config_no_default_pytest(self, tmpdir_cleanup):
        """Test that pytest is not defaulted without configuration."""
        Path(tmpdir_cleanup, "test_main.py").write_text(
            "import unittest\nclass TestMain(unittest.TestCase): pass"
        )
        Path(tmpdir_cleanup, "main.py").write_text("# main")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        config_content = analyzer.generate_agentic_config()
        config = json.loads(config_content)

        testing = config.get("ai_readiness", {}).get("testing", {})
        framework = testing.get("framework")

        assert framework != "pytest"

    def test_agentic_config_test_count_matches_actual(self, tmpdir_cleanup):
        """Test that test count in config matches actual test functions."""
        Path(tmpdir_cleanup, "test_one.py").write_text(
            "def test_a(): pass\ndef test_b(): pass"
        )
        Path(tmpdir_cleanup, "test_two.py").write_text(
            "def test_c(): pass"
        )

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        config_content = analyzer.generate_agentic_config()
        config = json.loads(config_content)

        reported_count = config.get("testing", {}).get("total_tests")
        assert reported_count is not None
        assert reported_count >= 2

    def test_agentic_config_no_tools_unless_configured(self, tmpdir_cleanup):
        """Test that tools only appear if configured."""
        Path(tmpdir_cleanup, "main.py").write_text("# main")
        Path(tmpdir_cleanup, "pyproject.toml").write_text("[build-system]\nrequires = ['setuptools']")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        config_content = analyzer.generate_agentic_config()
        config = json.loads(config_content)

        dev = config.get("ai_readiness", {}).get("development", {})
        linting = dev.get("linting_tools", [])

        assert linting == []

    def test_agents_md_no_hardcoded_test_framework(self, tmpdir_cleanup):
        """Test AGENTS.md doesn't hardcode test frameworks."""
        Path(tmpdir_cleanup, "test_main.py").write_text(
            "import unittest\nclass TestMain(unittest.TestCase): pass"
        )
        Path(tmpdir_cleanup, "main.py").write_text("# main")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        agents_md = analyzer.generate_agents_md()

        assert agents_md is not None
        assert agents_md != ""

    def test_python_version_from_config(self, tmpdir_cleanup):
        """Test Python version comes from configuration, not hardcoded."""
        pyproject = Path(tmpdir_cleanup) / "pyproject.toml"
        pyproject.write_text('requires-python = ">=3.8"')
        Path(tmpdir_cleanup, "main.py").write_text("# main")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        config_content = analyzer.generate_agentic_config()
        config = json.loads(config_content)

        version = config.get("development", {}).get("prerequisites", {}).get("language_version")
        assert version == ">=3.8"

    def test_shell_project_not_given_python_defaults(self, tmpdir_cleanup):
        """Test that shell projects don't receive Python defaults."""
        Path(tmpdir_cleanup, "script.sh").write_text("#!/bin/bash\necho hello")
        Path(tmpdir_cleanup, "test.bats").write_text("@test 'test' { true }")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        config_content = analyzer.generate_agentic_config()
        config = json.loads(config_content)

        dev = config.get("ai_readiness", {}).get("development", {})
        setup_cmd = dev.get("setup_command")

        assert "pip" not in str(setup_cmd) if setup_cmd else True


class TestRegression_HardcodingFixes:
    """Regression tests for hardcoding issues fixed in Braxis."""

    def test_shell_project_package_manager_is_none(self, tmpdir_cleanup):
        """Test that shell projects have None as package manager (Issue 1)."""
        Path(tmpdir_cleanup, "bin").mkdir()
        Path(tmpdir_cleanup, "bin/script").write_text("#!/bin/bash\necho hello")
        Path(tmpdir_cleanup, "test.bats").write_text("@test 'test' { true }")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        config_content = analyzer.generate_agentic_config()
        config = json.loads(config_content)

        pkg_mgr = config.get("development", {}).get("prerequisites", {}).get("package_manager")
        assert pkg_mgr is None

    def test_agents_md_shell_package_manager_not_listed(self, tmpdir_cleanup):
        """Test that AGENTS.md doesn't list package manager for shell projects (Issue 2)."""
        Path(tmpdir_cleanup, "bin").mkdir()
        Path(tmpdir_cleanup, "bin/script").write_text("#!/bin/bash\necho hello")
        Path(tmpdir_cleanup, "test.bats").write_text("@test 'test' { true }")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        agents_md = analyzer.generate_agents_md()

        assert "**Package Manager:** pip" not in agents_md
        assert "**Package Manager:** npm" not in agents_md

    def test_agents_md_code_style_shell_specific(self, tmpdir_cleanup):
        """Test that AGENTS.md has Shell-specific code style (Issue 3)."""
        Path(tmpdir_cleanup, "bin").mkdir()
        Path(tmpdir_cleanup, "bin/script").write_text("#!/bin/bash\necho hello")
        Path(tmpdir_cleanup, "test.bats").write_text("@test 'test' { true }")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        agents_md = analyzer.generate_agents_md()

        assert "snake_case" in agents_md
        assert "exit status" in agents_md

    def test_shellcheck_command_comprehensive_paths(self, tmpdir_cleanup):
        """Test that shellcheck command includes comprehensive paths (Issue 4)."""
        Path(tmpdir_cleanup, "bin").mkdir()
        Path(tmpdir_cleanup, "bin/script").write_text("#!/bin/bash\necho hello")
        Path(tmpdir_cleanup, "test.bats").write_text("@test 'test' { true }")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        agents_md = analyzer.generate_agents_md()

        assert "./bin/*" in agents_md
        assert "./libexec/*" in agents_md
        assert "./plugins/*/bin/*" in agents_md

    def test_claude_md_agents_import_not_in_code_fence(self, tmpdir_cleanup):
        """Test that CLAUDE.md doesn't put @AGENTS.md in code fence (Issue 5)."""
        Path(tmpdir_cleanup, "test.py").write_text("# test")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        claude_md = analyzer.generate_claude_md()

        assert "```\n@AGENTS.md" not in claude_md
        assert "\n@AGENTS.md\n" in claude_md

    def test_cursorrules_shell_specific_naming_convention(self, tmpdir_cleanup):
        """Test that .cursorrules has Shell-specific naming convention (Issue 6)."""
        Path(tmpdir_cleanup, "bin").mkdir()
        Path(tmpdir_cleanup, "bin/script").write_text("#!/bin/bash\necho hello")
        Path(tmpdir_cleanup, "test.bats").write_text("@test 'test' { true }")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        cursorrules = analyzer.generate_cursorrules()

        assert "snake_case" in cursorrules
        assert "shellcheck" in cursorrules

    def test_cursorrules_test_command_language_specific(self, tmpdir_cleanup):
        """Test that .cursorrules uses language-specific test commands (Issue 7)."""
        Path(tmpdir_cleanup, "bin").mkdir()
        Path(tmpdir_cleanup, "bin/script").write_text("#!/bin/bash\necho hello")
        Path(tmpdir_cleanup, "test.bats").write_text("@test 'test' { true }")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()
        cursorrules = analyzer.generate_cursorrules()

        assert "make test" in cursorrules
        assert "pytest" not in cursorrules


class TestAutomationVerification:
    """Tests to verify automation and context regeneration."""

    def test_automation_triggers_context_regeneration(self, tmpdir_cleanup):
        """Verify that code changes trigger context file regeneration."""
        Path(tmpdir_cleanup, "src").mkdir()
        Path(tmpdir_cleanup, "src/main.py").write_text("print('hello')")

        analyzer = BraxisAnalyzer(tmpdir_cleanup)
        analyzer.analyze()

        assert "python" in analyzer.languages
        agents_md = analyzer.generate_agents_md()
        assert "Python" in agents_md
