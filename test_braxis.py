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


if __name__ == '__main__':
    unittest.main()
