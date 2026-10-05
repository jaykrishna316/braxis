"""
Comprehensive regression tests for Braxis 2.0 - All 14 Features
Run with: python -m unittest tests.test_braxis_2_0_features
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from braxis_benchmarking import BenchmarkingEngine, RepoMetadata, BenchmarkCluster
from braxis_telemetry import TelemetryEngine, AgentType, TaskMetrics
from braxis_context_slicing import ContextSlicer, AgentContextStyle
from braxis_task_context import TaskContextGenerator, TaskType
from braxis_adr import ADRGenerator, ADR, DecisionStatus
from braxis_ci_monitoring import CIMonitor, BuildStatus, ScoreCheckResult
from braxis_security import SecurityAnalyzer, VulnerabilityPattern, SeverityLevel
from braxis_handoff import HandoffManager, TeamMemberRole
from braxis_visualization import VisualizationEngine, Package, DepGraph
from braxis_coverage_map import CoverageMapper, TestCase, CodeLocation
from braxis_nlq import NaturalLanguageQueryEngine, ContextSection, QueryType
from braxis_org_aggregator import OrgAggregator, OrgRepo
from braxis_suggestions import ImprovementSuggester, ImprovementArea


class TestBenchmarking(unittest.TestCase):
    """Test suite for benchmarking engine."""

    def test_cluster_creation(self):
        """Test creating benchmark clusters."""
        engine = BenchmarkingEngine()
        cluster = engine.create_cluster("python", "django", "large")

        self.assertEqual(cluster.language, "python")
        self.assertEqual(cluster.framework, "django")
        self.assertEqual(cluster.project_size, "large")

    def test_repo_registration(self):
        """Test registering repositories in clusters."""
        engine = BenchmarkingEngine()
        cluster = engine.create_cluster("python", "django", "medium")

        repo = RepoMetadata(
            repo_name="test-repo",
            owner="test-org",
            language="python",
            framework="django",
            project_size="medium",
            age_months=12,
            score=75,
            last_updated=datetime.now()
        )

        engine.register_repo(repo, cluster.cluster_id)
        self.assertIn("test-org/test-repo", engine.repos)

    def test_percentile_calculation(self):
        """Test percentile calculation."""
        engine = BenchmarkingEngine()
        cluster = engine.create_cluster("python")

        for i in range(5):
            repo = RepoMetadata(
                repo_name=f"repo-{i}",
                owner="org",
                language="python",
                framework=None,
                project_size="medium",
                age_months=12,
                score=50 + (i * 10),
                last_updated=datetime.now()
            )
            cluster.add_repo(repo)

        percentile = cluster.get_percentile(75)
        self.assertGreater(percentile, 0)
        self.assertLessEqual(percentile, 100)


class TestTelemetry(unittest.TestCase):
    """Test suite for telemetry engine."""

    def test_task_recording(self):
        """Test recording agent tasks."""
        engine = TelemetryEngine("test-repo")

        task = engine.record_task(
            "task-1",
            AgentType.CLAUDE_CODE,
            "Add new endpoint",
            success=True,
            time_to_solution=300.0,
            context_relevance=85.0
        )

        self.assertEqual(task.task_id, "task-1")
        self.assertTrue(task.success)
        self.assertIn("task-1", engine.tasks)

    def test_efficiency_score_calculation(self):
        """Test efficiency score calculation."""
        engine = TelemetryEngine("test-repo")

        for i in range(3):
            engine.record_task(
                f"task-{i}",
                AgentType.CLAUDE_CODE,
                f"Task {i}",
                success=(i < 2),
                time_to_solution=300.0,
                context_relevance=80.0
            )

        score = engine.get_efficiency_score(AgentType.CLAUDE_CODE)
        self.assertIsNotNone(score)
        self.assertGreaterEqual(score.efficiency_score, 0)
        self.assertLessEqual(score.efficiency_score, 100)


class TestContextSlicing(unittest.TestCase):
    """Test suite for context slicing."""

    def test_context_profile_retrieval(self):
        """Test retrieving agent context profiles."""
        slicer = ContextSlicer()

        claude_profile = slicer.get_profile(AgentContextStyle.CLAUDE_CODE)
        self.assertEqual(claude_profile.agent_type, AgentContextStyle.CLAUDE_CODE)
        self.assertGreater(len(claude_profile.emphasis_areas), 0)

    def test_context_slicing(self):
        """Test slicing context for agents."""
        slicer = ContextSlicer()

        full_context = "# Architecture\nThis is about architecture.\n\n# API\nThis is about the API."
        sliced = slicer.slice_context(full_context, AgentContextStyle.CLAUDE_CODE)
        self.assertGreater(len(sliced), 0)


class TestTaskContext(unittest.TestCase):
    """Test suite for task-specific context generation."""

    def test_task_profile_retrieval(self):
        """Test retrieving task profiles."""
        generator = TaskContextGenerator()

        profile = generator.get_task_profile(TaskType.ADD_ENDPOINT)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.task_type, TaskType.ADD_ENDPOINT)

    def test_context_generation(self):
        """Test generating task-specific context."""
        generator = TaskContextGenerator()

        full_context = "# Full Context\nComplete documentation here."
        context = generator.generate_context(TaskType.ADD_ENDPOINT, full_context)

        self.assertGreater(len(context), len(full_context))

    def test_file_suggestions(self):
        """Test file suggestions for tasks."""
        generator = TaskContextGenerator()

        files = generator.suggest_files(TaskType.ADD_ENDPOINT)
        self.assertGreater(len(files), 0)

    def test_task_checklist(self):
        """Test task checklist generation."""
        generator = TaskContextGenerator()

        checklist = generator.get_task_checklist(TaskType.ADD_ENDPOINT)
        self.assertGreater(len(checklist), 0)


class TestADRGeneration(unittest.TestCase):
    """Test suite for ADR generation."""

    def test_monorepo_decision_detection(self):
        """Test detecting monorepo decisions."""
        generator = ADRGenerator("test-repo")

        adr = generator.detect_monorepo_decision("pnpm")
        self.assertIsNotNone(adr)
        self.assertIn("pnpm", adr.title.lower())
        self.assertEqual(adr.status, DecisionStatus.ACCEPTED)

    def test_framework_decision_detection(self):
        """Test detecting framework decisions."""
        generator = ADRGenerator("test-repo")

        adr = generator.detect_framework_decision("Django", "Flask")
        self.assertIsNotNone(adr)
        self.assertIn("Django", adr.title)

    def test_adr_markdown_export(self):
        """Test exporting ADR to markdown."""
        generator = ADRGenerator("test-repo")
        generator.detect_monorepo_decision("yarn")

        export = generator.export_adr_directory()
        self.assertIn(1, export)
        self.assertIn("ADR 1", export[1])


class TestCIMonitoring(unittest.TestCase):
    """Test suite for CI/CD monitoring."""

    def test_score_change_detection(self):
        """Test detecting score changes."""
        monitor = CIMonitor(failure_threshold=5)

        result = monitor.check_score_change(80, 75)
        self.assertEqual(result.change, 5)
        self.assertEqual(result.status, BuildStatus.PASSED)

    def test_score_drop_detection(self):
        """Test detecting score drops."""
        monitor = CIMonitor(failure_threshold=5)

        result = monitor.check_score_change(70, 78)
        self.assertEqual(result.change, -8)
        self.assertEqual(result.status, BuildStatus.FAILED)

    def test_pr_comment_generation(self):
        """Test generating PR comments."""
        monitor = CIMonitor()
        monitor.record_build(123, "abc123", 85, 80)

        comment = monitor.generate_pr_comment(123)
        self.assertIn("Score", comment)
        self.assertIn("85", comment)

    def test_badge_generation(self):
        """Test generating score badges."""
        monitor = CIMonitor()

        url = monitor.get_badge_url(78)
        self.assertIn("shields.io", url)
        self.assertIn("78", url)


class TestSecurityAnalysis(unittest.TestCase):
    """Test suite for security analysis."""

    def test_vulnerability_pattern_registration(self):
        """Test registering vulnerability patterns."""
        analyzer = SecurityAnalyzer("python")

        self.assertGreater(len(analyzer.PATTERNS), 0)
        self.assertIn("hardcoded_secrets", analyzer.PATTERNS)

    def test_security_score_calculation(self):
        """Test calculating security score."""
        analyzer = SecurityAnalyzer("python")

        score = analyzer.get_security_score()
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_summary_generation(self):
        """Test generating security summary."""
        analyzer = SecurityAnalyzer("python")

        summary = analyzer.get_summary()
        self.assertIn("total_findings", summary)
        self.assertIn("security_score", summary)


class TestHandoffManagement(unittest.TestCase):
    """Test suite for team handoff management."""

    def test_onboarding_plan_generation(self):
        """Test generating onboarding plans."""
        manager = HandoffManager("test-repo")

        plan = manager.generate_onboarding_plan("alice", "backend")
        self.assertEqual(plan["developer"], "alice")
        self.assertEqual(plan["role"], "backend")
        self.assertGreater(len(plan["milestones"]), 0)

    def test_offboarding_plan_generation(self):
        """Test generating offboarding plans."""
        manager = HandoffManager("test-repo")

        plan = manager.generate_offboarding_plan("bob")
        self.assertEqual(plan["developer"], "bob")
        self.assertGreater(len(plan["milestones"]), 0)

    def test_role_guide_generation(self):
        """Test generating role guides."""
        manager = HandoffManager("test-repo")

        guide = manager.generate_role_guide("backend")
        self.assertIn("Backend Developer", guide)
        self.assertIn("Responsibilities", guide)


class TestVisualization(unittest.TestCase):
    """Test suite for dependency visualization."""

    def test_dependency_graph_creation(self):
        """Test creating dependency graphs."""
        engine = VisualizationEngine()

        graph = engine.create_dependency_graph("/monorepo")
        self.assertEqual(graph.root_path, "/monorepo")
        self.assertEqual(len(graph.packages), 0)

    def test_package_addition(self):
        """Test adding packages to graph."""
        engine = VisualizationEngine()
        graph = engine.create_dependency_graph("/monorepo")

        pkg = Package(name="api", path="packages/api", dependencies=["express"])
        engine.add_package(graph, pkg)

        self.assertIn("api", graph.packages)

    def test_svg_generation(self):
        """Test generating SVG visualization."""
        engine = VisualizationEngine()
        graph = engine.create_dependency_graph("/monorepo")

        pkg1 = Package(name="core", path="packages/core")
        engine.add_package(graph, pkg1)

        svg = engine.generate_svg(graph)
        self.assertIn("<svg", svg)


class TestCoverageMapping(unittest.TestCase):
    """Test suite for test-to-code mapping."""

    def test_test_registration(self):
        """Test registering tests."""
        mapper = CoverageMapper()

        test = TestCase(
            test_id="test_add",
            test_file="test_api.py",
            test_name="test_add_endpoint",
            code_locations=[CodeLocation("api.py", "add_endpoint")]
        )

        mapper.register_test(test)
        self.assertIn("test_add", mapper.tests)

    def test_feature_coverage(self):
        """Test getting feature coverage."""
        mapper = CoverageMapper()

        test = TestCase(
            test_id="test_1",
            test_file="tests.py",
            test_name="test_feature",
            code_locations=[CodeLocation("app.py", "feature_func")]
        )
        mapper.register_test(test)
        mapper.register_feature("Feature A", [CodeLocation("app.py", "feature_func")])

        report = mapper.get_feature_coverage("Feature A")
        self.assertEqual(report.coverage_percentage, 100)


class TestNLQ(unittest.TestCase):
    """Test suite for natural language query interface."""

    def test_query_type_classification(self):
        """Test classifying query types."""
        engine = NaturalLanguageQueryEngine()

        how_type = engine._classify_query("How do I set up the project?")
        self.assertEqual(how_type, QueryType.HOW_TO)

        where_type = engine._classify_query("Where is the API defined?")
        self.assertEqual(where_type, QueryType.WHERE_IS)

    def test_keyword_extraction(self):
        """Test extracting keywords from queries."""
        engine = NaturalLanguageQueryEngine()

        keywords = engine._extract_keywords("How do I add authentication?")
        self.assertGreater(len(keywords), 0)


class TestOrgAggregator(unittest.TestCase):
    """Test suite for organization-wide metrics."""

    def test_repo_registration(self):
        """Test registering repositories."""
        agg = OrgAggregator("test-org")

        repo = OrgRepo(
            repo_name="api",
            score=75,
            language="python",
            team_size=3,
            last_updated=datetime.now()
        )

        agg.register_repo(repo, "backend-team")
        self.assertIn("api", agg.repos)
        self.assertIn("backend-team", agg.teams)

    def test_org_metrics_calculation(self):
        """Test calculating organization metrics."""
        agg = OrgAggregator("test-org")

        for i in range(3):
            repo = OrgRepo(
                repo_name=f"repo-{i}",
                score=60 + (i * 10),
                language="python",
                team_size=2,
                last_updated=datetime.now()
            )
            agg.register_repo(repo)

        metrics = agg.get_org_metrics()
        self.assertEqual(metrics.total_repos, 3)
        self.assertGreater(metrics.avg_score, 0)


class TestImprovementSuggestions(unittest.TestCase):
    """Test suite for improvement suggestions."""

    def test_improvement_plan_generation(self):
        """Test generating improvement plans."""
        suggester = ImprovementSuggester()

        plan = suggester.suggest_improvements(50, 85)
        self.assertEqual(plan.current_score, 50)
        self.assertEqual(plan.target_score, 85)
        self.assertGreater(len(plan.improvements), 0)

    def test_quick_wins_identification(self):
        """Test identifying quick wins."""
        suggester = ImprovementSuggester()

        quick_wins = suggester.get_quick_wins(50, max_hours=8)
        for win in quick_wins:
            self.assertLessEqual(win.time_estimate_hours, 8)

    def test_score_estimation(self):
        """Test estimating final score."""
        suggester = ImprovementSuggester()

        plan = suggester.suggest_improvements(50)
        estimated = suggester.estimate_score(50, plan.improvements)

        self.assertGreater(estimated, 50)
        self.assertLessEqual(estimated, 100)


if __name__ == "__main__":
    unittest.main(verbosity=2)
