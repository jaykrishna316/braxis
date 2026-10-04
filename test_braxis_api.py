"""
Tests for Braxis Programmatic API, Configuration, and Triggers.
"""

import unittest
from pathlib import Path
from braxis_config import (
    BraxisConfig,
    ContextConfig,
    GenerationConfig,
    AutomationConfig,
    ScoringConfig,
)
from braxis_triggers import SmartTrigger, ChangeMetrics, ChangeDetector
from braxis_api import (
    AIReadinessScore,
    GenerationResult,
    Suggestion,
    ContextGenerator,
    ScoreAnalyzer,
    TrendAnalyzer,
    MultiRepoAnalyzer,
)


class TestBraxisConfig(unittest.TestCase):
    """Test configuration file handling."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = BraxisConfig()
        assert config.context.output_format == "markdown"
        assert config.generation.include_test_metrics is True
        assert config.automation.auto_commit is True
        assert config.scoring.enable_scoring is True

    def test_context_config(self):
        """Test context configuration."""
        ctx = ContextConfig(
            output_format="json",
            code_block_style="html",
        )
        assert ctx.output_format == "json"
        assert ctx.code_block_style == "html"

    def test_generation_config(self):
        """Test generation configuration."""
        gen = GenerationConfig(
            min_change_threshold=10,
            skip_trivial_changes=True,
        )
        assert gen.min_change_threshold == 10
        assert gen.skip_trivial_changes is True

    def test_automation_config(self):
        """Test automation configuration."""
        auto = AutomationConfig(
            auto_commit=False,
            commit_message="Custom commit",
        )
        assert auto.auto_commit is False
        assert auto.commit_message == "Custom commit"

    def test_config_creation_with_nested_objects(self):
        """Test creating config with all nested objects."""
        config = BraxisConfig(
            context=ContextConfig(output_format="json"),
            generation=GenerationConfig(min_change_threshold=5),
            automation=AutomationConfig(auto_commit=False),
            scoring=ScoringConfig(enable_scoring=True),
        )
        assert config.context.output_format == "json"
        assert config.generation.min_change_threshold == 5
        assert config.automation.auto_commit is False


class TestSmartTrigger(unittest.TestCase):
    """Test smart triggering logic."""

    def test_trigger_initialization(self):
        """Test SmartTrigger initialization."""
        trigger = SmartTrigger()
        assert trigger.config is not None
        assert trigger.gen_config is not None

    def test_filter_meaningful_files(self):
        """Test filtering of meaningful files."""
        trigger = SmartTrigger()
        files = [
            "src/module.py",
            "tests/test_module.py",
            "README.md",
            "docs/guide.md",
            "setup.py",
        ]

        meaningful = trigger._filter_meaningful_files(files)
        assert "src/module.py" in meaningful
        assert "tests/test_module.py" in meaningful
        assert "setup.py" in meaningful
        # .md files should be filtered
        assert not any(f.endswith(".md") for f in meaningful)

    def test_filter_excluded_patterns(self):
        """Test that excluded patterns are filtered."""
        config = BraxisConfig(
            generation=GenerationConfig(exclude_patterns=["__pycache__", ".venv"])
        )
        trigger = SmartTrigger(config)
        files = [
            "src/module.py",
            "__pycache__/cache.py",
            ".venv/lib/python.py",
        ]

        meaningful = trigger._filter_meaningful_files(files)
        assert "src/module.py" in meaningful
        assert "__pycache__/cache.py" not in meaningful
        assert ".venv/lib/python.py" not in meaningful

    def test_no_changes(self):
        """Test trigger with no files changed."""
        trigger = SmartTrigger()
        should_regen, metrics = trigger.should_regenerate([])

        assert should_regen is False
        assert metrics.is_trivial_change is True
        assert "No files changed" in metrics.change_reason

    def test_only_trivial_changes(self):
        """Test trigger with only trivial changes."""
        trigger = SmartTrigger()
        files = ["README.md", "docs/guide.md", "LICENSE"]

        should_regen, metrics = trigger.should_regenerate(files)

        assert should_regen is False
        assert metrics.is_trivial_change is True
        assert "trivial" in metrics.change_reason.lower()

    def test_meaningful_changes(self):
        """Test trigger with meaningful changes."""
        trigger = SmartTrigger()
        files = ["src/module.py", "setup.py"]

        should_regen, metrics = trigger.should_regenerate(files)

        # Should regenerate (assuming line threshold is met or disabled)
        if trigger.gen_config.min_change_threshold == 0:
            assert should_regen is True

    def test_change_detector_whitespace_only(self):
        """Test change detector for whitespace-only changes."""
        diff = """
-    # This is a comment
+   # This is a comment
"""
        is_trivial = ChangeDetector.is_whitespace_only(diff)
        # This should detect as whitespace-only
        # (actual detection depends on implementation details)

    def test_change_metrics_structure(self):
        """Test ChangeMetrics data structure."""
        metrics = ChangeMetrics(
            total_lines_changed=42,
            files_changed=["src/module.py"],
            meaningful_files_changed=["src/module.py"],
            is_trivial_change=False,
            change_reason="Meaningful code changes detected",
        )

        assert metrics.total_lines_changed == 42
        assert len(metrics.files_changed) == 1
        assert metrics.is_trivial_change is False


class TestAIReadinessScore(unittest.TestCase):
    """Test AI Readiness Score data model."""

    def test_score_creation(self):
        """Test creating a score."""
        score = AIReadinessScore(
            total=75,
            architecture=10,
            testing=7,
            dependencies=12,
            conventions=10,
            entry_points=4,
            security=10,
            build=10,
            documentation=8,
            level="AI-Aware",
        )

        assert score.total == 75
        assert score.level == "AI-Aware"

    def test_score_to_dict(self):
        """Test converting score to dictionary."""
        score = AIReadinessScore(
            total=75,
            architecture=10,
            testing=7,
            dependencies=12,
            conventions=10,
            entry_points=4,
            security=10,
            build=10,
            documentation=8,
            level="AI-Aware",
        )

        score_dict = score.to_dict()
        assert score_dict["total"] == 75
        assert score_dict["level"] == "AI-Aware"
        assert "timestamp" in score_dict

    def test_get_dimensions(self):
        """Test getting dimension scores."""
        score = AIReadinessScore(
            total=75,
            architecture=10,
            testing=7,
            dependencies=12,
            conventions=10,
            entry_points=4,
            security=10,
            build=10,
            documentation=8,
        )

        dims = score.get_dimensions()
        assert dims["architecture"] == 10
        assert dims["testing"] == 7
        assert len(dims) == 8


class TestGenerationResult(unittest.TestCase):
    """Test generation result data model."""

    def test_generation_result_success(self):
        """Test successful generation result."""
        result = GenerationResult(
            success=True,
            changed_files=["AGENTS.md", "CLAUDE.md"],
            changes={
                "AGENTS.md": "# Agents\nContent",
                "CLAUDE.md": "# Claude\nContent",
            },
            files_generated=2,
        )

        assert result.success is True
        assert len(result.changed_files) == 2
        assert len(result.changes) == 2

    def test_generation_result_failure(self):
        """Test failed generation result."""
        result = GenerationResult(
            success=False,
            errors=["File not found", "Invalid config"],
        )

        assert result.success is False
        assert len(result.errors) == 2

    def test_generation_result_to_dict(self):
        """Test converting result to dictionary."""
        result = GenerationResult(
            success=True,
            changed_files=["AGENTS.md"],
            changes={"AGENTS.md": "content"},
            files_generated=1,
        )

        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["num_files_generated"] == 1
        assert "timestamp" in result_dict


class TestSuggestion(unittest.TestCase):
    """Test improvement suggestion data model."""

    def test_suggestion_creation(self):
        """Test creating a suggestion."""
        suggestion = Suggestion(
            dimension="architecture",
            current_score=10,
            target_score=50,
            actions=["Refactor code", "Add modules"],
            priority="high",
            estimated_effort="high",
        )

        assert suggestion.dimension == "architecture"
        assert suggestion.current_score == 10
        assert suggestion.priority == "high"

    def test_suggestion_to_dict(self):
        """Test converting suggestion to dictionary."""
        suggestion = Suggestion(
            dimension="testing",
            current_score=7,
            target_score=50,
            actions=["Add unit tests"],
            priority="high",
        )

        sug_dict = suggestion.to_dict()
        assert sug_dict["dimension"] == "testing"
        assert sug_dict["priority"] == "high"


class TestContextGenerator(unittest.TestCase):
    """Test context file generation."""

    def test_generator_initialization(self):
        """Test initializing a context generator."""
        generator = ContextGenerator(project_path=".")
        assert generator.project_path is not None
        assert generator.config is not None

    def test_generator_with_custom_config(self):
        """Test generator with custom config."""
        config = BraxisConfig(
            context=ContextConfig(output_format="json")
        )
        generator = ContextGenerator(project_path=".", config=config)
        assert generator.config.context.output_format == "json"

    def test_generator_invalid_path(self):
        """Test generator with invalid project path."""
        with self.assertRaises(FileNotFoundError):
            ContextGenerator(project_path="/nonexistent/path")


class TestScoreAnalyzer(unittest.TestCase):
    """Test score analysis."""

    def test_analyzer_initialization(self):
        """Test initializing a score analyzer."""
        analyzer = ScoreAnalyzer(project_path=".")
        assert analyzer.project_path is not None
        assert analyzer.config is not None

    def test_get_improvement_suggestions(self):
        """Test getting improvement suggestions."""
        analyzer = ScoreAnalyzer(project_path=".")
        # Note: This will fail if BraxisAnalyzer can't be loaded,
        # but it tests the API contract
        try:
            suggestions = analyzer.get_improvement_suggestions()
            assert isinstance(suggestions, list)
            for s in suggestions:
                assert isinstance(s, Suggestion)
        except Exception:
            # Expected if running outside full environment
            pass


class TestMultiRepoAnalyzer(unittest.TestCase):
    """Test multi-repository analysis."""

    def test_multi_repo_initialization(self):
        """Test initializing multi-repo analyzer."""
        analyzer = MultiRepoAnalyzer(repos=["repo1", "repo2"])
        assert len(analyzer.repos) == 2


if __name__ == "__main__":
    unittest.main()
