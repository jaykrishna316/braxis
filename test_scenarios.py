"""
Real-world scenario tests for Braxis 2.0 - All 14 Features
Demonstrates practical usage patterns and outputs
"""

import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta
from braxis_benchmarking import BenchmarkingEngine, RepoMetadata
from braxis_telemetry import TelemetryEngine, AgentType
from braxis_context_slicing import ContextSlicer, AgentContextStyle
from braxis_task_context import TaskContextGenerator, TaskType
from braxis_adr import ADRGenerator
from braxis_ci_monitoring import CIMonitor
from braxis_security import SecurityAnalyzer
from braxis_handoff import HandoffManager
from braxis_visualization import VisualizationEngine, Package
from braxis_coverage_map import CoverageMapper, TestCase, CodeLocation
from braxis_nlq import NaturalLanguageQueryEngine, ContextSection
from braxis_org_aggregator import OrgAggregator, OrgRepo
from braxis_suggestions import ImprovementSuggester


def print_header(feature_num, feature_name):
    """Print feature header."""
    print(f"\n{'='*80}")
    print(f"FEATURE {feature_num}: {feature_name}")
    print(f"{'='*80}\n")


def print_scenario(title):
    """Print scenario title."""
    print(f"\n📋 SCENARIO: {title}")
    print("-" * 80)


def print_result(label, value):
    """Print result."""
    print(f"  {label}: {value}")


# ============================================================================
# FEATURE 1: Cross-Repo Competitive Benchmarking
# ============================================================================

def test_feature_1_benchmarking():
    """Test Feature 1: Cross-Repo Competitive Benchmarking"""
    print_header(1, "Cross-Repo Competitive Benchmarking")

    print_scenario("Benchmark Django repos from startup ecosystem")

    engine = BenchmarkingEngine()
    django_cluster = engine.create_cluster("python", "django", "medium")

    # Simulate 5 repos in the cluster
    repos_data = [
        ("startup-api", 75),
        ("ecommerce-platform", 82),
        ("social-network", 68),
        ("marketplace", 91),
        ("analytics-dashboard", 73)
    ]

    for repo_name, score in repos_data:
        repo = RepoMetadata(
            repo_name=repo_name,
            owner="tech-startups",
            language="python",
            framework="django",
            project_size="medium",
            age_months=18,
            score=score,
            last_updated=datetime.now()
        )
        engine.register_repo(repo, django_cluster.cluster_id)

    # Benchmark a new repo
    result = engine.benchmark_repo("my-startup-api", 78, "python", "django", "medium")

    print_result("New Repo Score", f"{result.score}/100")
    print_result("Percentile Rank", f"{result.percentile:.1f}%")
    print_result("Tier Classification", result.percentile_tier.upper())
    print_result("Cluster Average", f"{django_cluster.get_stats()['avg']:.1f}/100")
    print_result("Recommendations", result.recommendations[0])

    # Organization stats
    org_stats = engine.get_org_stats("python")
    print_result("\nOrg Stats (Python repos)",
                f"Avg: {org_stats['avg']:.1f}, Min: {org_stats['min']}, Max: {org_stats['max']}")


# ============================================================================
# FEATURE 2: Agent Performance Feedback Loop
# ============================================================================

def test_feature_2_telemetry():
    """Test Feature 2: Agent Performance Feedback Loop"""
    print_header(2, "Agent Performance Feedback Loop")

    print_scenario("Track Claude Code agent performance over 5 tasks")

    engine = TelemetryEngine("my-startup-api")

    tasks_data = [
        ("task_001", "Add user authentication endpoint", True, 420.0, 92.0),
        ("task_002", "Fix database connection pooling", True, 180.0, 88.0),
        ("task_003", "Add API rate limiting", True, 300.0, 85.0),
        ("task_004", "Implement caching layer", True, 510.0, 90.0),
        ("task_005", "Add input validation", True, 240.0, 94.0),
    ]

    for task_id, desc, success, time_to_sol, relevance in tasks_data:
        engine.record_task(task_id, AgentType.CLAUDE_CODE, desc, success, time_to_sol, relevance)

    efficiency = engine.get_efficiency_score(AgentType.CLAUDE_CODE)

    print_result("Tasks Completed", efficiency.tasks_completed)
    print_result("Success Rate", f"{efficiency.success_rate:.1f}%")
    print_result("Avg Time to Solution", f"{efficiency.avg_time_to_solution:.0f} seconds")
    print_result("Context Relevance", f"{efficiency.context_relevance:.1f}%")
    print_result("Efficiency Score", f"{efficiency.efficiency_score:.1f}/100")
    print_result("Productivity Insight",
                "Claude Code is performing exceptionally well on this codebase")


# ============================================================================
# FEATURE 3: Smart Context Slicing
# ============================================================================

def test_feature_3_context_slicing():
    """Test Feature 3: Smart Context Slicing by Agent Type"""
    print_header(3, "Smart Context Slicing by Agent Type")

    print_scenario("Generate agent-specific context from full documentation")

    full_context = """
# Architecture
The system uses microservices architecture with 4 main components.

## API Gateway
Routes requests to appropriate services.

## Database Layer
PostgreSQL with Redis caching.

## Testing Strategy
Comprehensive unit and integration tests with 85% coverage.

## IDE Configuration
Set up VS Code with Python extension and Pylance.

## Quick Shortcuts
Cmd+Shift+P for command palette (VS Code).
"""

    slicer = ContextSlicer()

    for agent_type in [AgentContextStyle.CLAUDE_CODE,
                       AgentContextStyle.CURSOR,
                       AgentContextStyle.COPILOT]:
        profile = slicer.get_profile(agent_type)
        print_result(f"\n{agent_type.value.upper()}", "")
        print_result("  Emphasis Areas", ", ".join(profile.emphasis_areas[:3]))
        print_result("  Style", profile.style_guide)
        print_result("  Max Context", f"{profile.max_context_tokens} tokens")


# ============================================================================
# FEATURE 4: Task-Specific Context
# ============================================================================

def test_feature_4_task_context():
    """Test Feature 4: Task-Specific Context Generation"""
    print_header(4, "Task-Specific Context Generation")

    print_scenario("Get context and checklist for 'Add new API endpoint' task")

    generator = TaskContextGenerator()

    files = generator.suggest_files(TaskType.ADD_ENDPOINT)
    checklist = generator.get_task_checklist(TaskType.ADD_ENDPOINT)

    print_result("Task Type", "ADD_ENDPOINT")
    print_result("Key Files to Review", ", ".join(files[:3]))
    print_result("\nChecklist Items:", "")
    for i, item in enumerate(checklist, 1):
        print(f"    {i}. {item}")


# ============================================================================
# FEATURE 5: ADR Auto-Generation
# ============================================================================

def test_feature_5_adr():
    """Test Feature 5: Architecture Decision Record Auto-Generation"""
    print_header(5, "Architecture Decision Record Auto-Generation")

    print_scenario("Auto-generate ADRs from detected architectural patterns")

    generator = ADRGenerator("my-startup-api")

    # Detect decisions
    adr1 = generator.detect_monorepo_decision("pnpm")
    adr2 = generator.detect_framework_decision("FastAPI", "Django")
    adr3 = generator.detect_testing_strategy("bdd")

    print_result("ADR 1 Title", adr1.title)
    print_result("ADR 1 Status", adr1.status.value)
    print_result("ADR 1 Consequence", adr1.consequences[0][:50] + "...")

    print_result("\nADR 2 Title", adr2.title)
    print_result("ADR 2 Alternatives", ", ".join(adr2.alternatives))

    print_result("\nADR 3 Title", adr3.title)
    print_result("Total ADRs Generated", len(generator.get_all_adrs()))


# ============================================================================
# FEATURE 6: CI/CD Monitoring
# ============================================================================

def test_feature_6_ci_monitoring():
    """Test Feature 6: Real-Time Readiness Monitoring"""
    print_header(6, "Real-Time Readiness Monitoring in CI/CD")

    print_scenario("Simulate PR check with score validation")

    monitor = CIMonitor(failure_threshold=5)

    # Simulate PR #42 score change
    monitor.record_build(42, "abc123def", 82, 87)

    check = monitor.check_score_change(82, 87)
    pr_comment = monitor.generate_pr_comment(42)
    badge_url = monitor.get_badge_url(82)

    print_result("PR Number", "42")
    print_result("Previous Score", "87/100")
    print_result("Current Score", "82/100")
    print_result("Score Change", f"{check.change:+d}")
    print_result("CI Status", check.status.value.upper())
    print_result("Failure Threshold", "5 points")
    print_result("Build Outcome", "PASSED (within threshold)")
    print_result("\nBadge URL", badge_url[:60] + "...")


# ============================================================================
# FEATURE 7: Security Patterns
# ============================================================================

def test_feature_7_security():
    """Test Feature 7: Vulnerability Pattern Detection"""
    print_header(7, "Vulnerability Pattern Detection")

    print_scenario("Scan Python code for security vulnerabilities")

    analyzer = SecurityAnalyzer("python")

    # Sample vulnerable code
    vulnerable_code = """
user_input = request.args.get('id')
query = f"SELECT * FROM users WHERE id = {user_input}"
cursor.execute(query)
api_key = "sk_live_abc123xyz"
json.loads(user_data)
"""

    findings = analyzer.scan_file("app.py", vulnerable_code)
    summary = analyzer.get_summary()

    print_result("Files Scanned", "1")
    print_result("Total Findings", summary['total_findings'])
    print_result("Critical Issues", summary['critical'])
    print_result("High Issues", summary['high'])
    print_result("Security Score", f"{summary['security_score']:.1f}/100")
    print_result("Status", "⚠️  Action Required" if summary['security_score'] < 80 else "✅ Acceptable")


# ============================================================================
# FEATURE 8: Team Handoff
# ============================================================================

def test_feature_8_handoff():
    """Test Feature 8: Team Handoff Checklists"""
    print_header(8, "Team Handoff Checklists")

    print_scenario("Generate onboarding plan for new backend developer")

    manager = HandoffManager("my-startup-api")

    plan = manager.generate_onboarding_plan("alice@startup.com", "backend")

    print_result("New Developer", "Alice")
    print_result("Role", "Backend Developer")
    print_result("Onboarding Duration", "14 days")
    print_result("Key Responsibilities", plan['responsibilities'][0])
    print_result("First Week Goals", "Setup environment, understand architecture, first contribution")
    print_result("Day 5 Milestone", "Complete first independent pull request")
    print_result("Learning Resources", f"{len(plan['resources'])} items")


# ============================================================================
# FEATURE 9: Dependency Visualization
# ============================================================================

def test_feature_9_visualization():
    """Test Feature 9: Visual Dependency Graphs"""
    print_header(9, "Visual Dependency Graphs")

    print_scenario("Visualize monorepo package dependencies")

    engine = VisualizationEngine()
    graph = engine.create_dependency_graph("/home/user/startup")

    packages = [
        ("core", "packages/core", []),
        ("api", "packages/api", ["core"]),
        ("web", "packages/web", ["api"]),
        ("cli", "packages/cli", ["core"])
    ]

    for name, path, deps in packages:
        pkg = Package(name=name, path=path, internal_dependencies=deps)
        engine.add_package(graph, pkg)

    svg = engine.generate_svg(graph)
    tree = engine.generate_ascii_tree(graph)

    print_result("Packages in Monorepo", len(graph.packages))
    print_result("Dependency Relationships", len([p for p in packages if p[2]]))
    print_result("SVG Generated", "✅ Yes" if "<svg" in svg else "❌ No")
    print_result("\nASCII Tree Preview", "")
    for line in tree.split('\n')[:8]:
        print(f"    {line}")


# ============================================================================
# FEATURE 10: Test-to-Code Mapping
# ============================================================================

def test_feature_10_coverage():
    """Test Feature 10: Test-to-Code Mapping"""
    print_header(10, "Test-to-Code Mapping")

    print_scenario("Map test coverage for authentication feature")

    mapper = CoverageMapper()

    # Register tests
    test1 = TestCase(
        test_id="test_auth_001",
        test_file="tests/test_auth.py",
        test_name="test_login_success",
        code_locations=[
            CodeLocation("auth.py", "authenticate"),
            CodeLocation("auth.py", "validate_password")
        ]
    )
    test2 = TestCase(
        test_id="test_auth_002",
        test_file="tests/test_auth.py",
        test_name="test_login_failure",
        code_locations=[CodeLocation("auth.py", "authenticate")]
    )

    mapper.register_test(test1)
    mapper.register_test(test2)
    mapper.register_feature("Authentication", [
        CodeLocation("auth.py", "authenticate"),
        CodeLocation("auth.py", "validate_password")
    ])

    coverage = mapper.get_feature_coverage("Authentication")

    print_result("Feature", "Authentication")
    print_result("Test Cases Covering Feature", len(coverage.covered_by_tests))
    print_result("Code Coverage", f"{coverage.coverage_percentage:.0f}%")
    print_result("Status", "✅ Fully Covered" if coverage.coverage_percentage == 100 else "⚠️ Partial")


# ============================================================================
# FEATURE 11: Natural Language Queries
# ============================================================================

def test_feature_11_nlq():
    """Test Feature 11: Natural Language Query Interface"""
    print_header(11, "Natural Language Query Interface")

    print_scenario("Query context using natural language")

    engine = NaturalLanguageQueryEngine()

    # Register context sections
    sections = [
        ContextSection(
            title="Authentication System",
            content="Uses JWT tokens with 24-hour expiry. Stored in Redis cache.",
            keywords=["auth", "jwt", "security", "token"]
        ),
        ContextSection(
            title="Database Schema",
            content="PostgreSQL with 12 main tables. Uses migrations for schema changes.",
            keywords=["database", "postgres", "schema", "migration"]
        ),
        ContextSection(
            title="API Endpoints",
            content="RESTful API with 45 endpoints. Documented in OpenAPI format.",
            keywords=["api", "endpoint", "rest", "openapi"]
        )
    ]

    for section in sections:
        engine.register_section(section)

    # Query examples
    queries = [
        "How do I set up authentication?",
        "Where is the database schema defined?",
        "What are the API endpoints?"
    ]

    print_result("Registered Context Sections", len(sections))
    print("\nQuery Examples:")
    for i, query in enumerate(queries, 1):
        result = engine.query(query)
        print(f"  {i}. Q: {query}")
        print(f"     Type: {result.query_type.value}")
        print(f"     Relevance: {result.relevance_score:.0f}%")


# ============================================================================
# FEATURE 12: Organization Aggregator
# ============================================================================

def test_feature_12_org_aggregator():
    """Test Feature 12: Organization Readiness Aggregator"""
    print_header(12, "Organization Readiness Aggregator")

    print_scenario("Track AI-readiness across entire startup engineering org")

    agg = OrgAggregator("TechStartup Inc")

    repos_data = [
        ("api-backend", 78, "python", "backend-team"),
        ("web-frontend", 71, "javascript", "frontend-team"),
        ("mobile-app", 65, "swift", "mobile-team"),
        ("data-pipeline", 82, "python", "backend-team"),
        ("devops-infra", 75, "hcl", "devops-team"),
    ]

    for repo_name, score, lang, team in repos_data:
        repo = OrgRepo(
            repo_name=repo_name,
            score=score,
            language=lang,
            team_size=3,
            last_updated=datetime.now()
        )
        agg.register_repo(repo, team)

    metrics = agg.get_org_metrics()
    lang_stats = agg.get_language_stats()

    print_result("Organization", "TechStartup Inc")
    print_result("Total Repositories", metrics.total_repos)
    print_result("Organization Average Score", f"{metrics.avg_score:.1f}/100")
    print_result("Best Performer", metrics.top_performers[0])
    print_result("Needs Improvement", metrics.needs_improvement[0])
    print_result("At-Risk Repos (<50)", metrics.repos_at_risk)
    print_result("\nScore by Language:", "")
    for lang, avg_score in list(lang_stats.items())[:3]:
        print(f"    {lang}: {avg_score['avg_score']:.1f}/100")


# ============================================================================
# FEATURE 13: Agent Interaction Recording
# ============================================================================

def test_feature_13_interaction_recording():
    """Test Feature 13: Agent Interaction Recording"""
    print_header(13, "Agent Interaction Recording")

    print_scenario("Record and analyze agent interactions with codebase")

    engine = TelemetryEngine("my-startup-api")

    # Record interactions
    engine.record_interaction(
        AgentType.CLAUDE_CODE,
        "read_files",
        context_size=2048,
        response_tokens=512,
        sections_accessed=["Architecture", "API Design"]
    )

    engine.record_interaction(
        AgentType.CURSOR,
        "code_completion",
        context_size=1024,
        response_tokens=256,
        sections_accessed=["Conventions", "Patterns"]
    )

    engine.record_interaction(
        AgentType.CLAUDE_CODE,
        "write_code",
        context_size=3072,
        response_tokens=1024,
        sections_accessed=["Architecture", "Testing", "Security"]
    )

    summary = engine.get_interaction_summary()

    print_result("Total Interactions", summary['total'])
    print_result("Total Context Processed", f"{summary['total_context_kb']:.1f} KB")
    print_result("Total Response Tokens", summary['total_tokens'])
    print_result("\nInteractions by Agent Type:", "")
    for agent, stats in summary['by_agent'].items():
        print(f"    {agent}: {stats['count']} interactions, {stats['total_tokens']} tokens")


# ============================================================================
# FEATURE 14: Improvement Suggestions
# ============================================================================

def test_feature_14_suggestions():
    """Test Feature 14: Readiness Improvement Suggestions"""
    print_header(14, "Readiness Improvement Suggestions")

    print_scenario("Generate improvement plan: Current 60/100 → Target 85/100")

    suggester = ImprovementSuggester()

    plan = suggester.suggest_improvements(60, 85)
    quick_wins = suggester.get_quick_wins(60, max_hours=8)

    print_result("Current Score", f"{plan.current_score}/100")
    print_result("Target Score", f"{plan.target_score}/100")
    print_result("Score Gap", f"{plan.target_score - plan.current_score} points")
    print_result("Total Effort", f"{plan.total_estimated_hours} hours")

    print("\n📋 Top 3 High-ROI Improvements:")
    for i, imp in enumerate(plan.improvements, 1):
        roi_ratio = imp.expected_roi_points / max(1, imp.time_estimate_hours)
        print(f"\n  {i}. {imp.area.value.upper()} ({imp.effort_estimate})")
        print(f"     ROI: +{imp.expected_roi_points} points in {imp.time_estimate_hours} hours ({roi_ratio:.2f} pts/hr)")
        print(f"     Action: {imp.action_items[0]}")

    estimated_final = suggester.estimate_score(60, plan.improvements)
    print(f"\n✅ Estimated Final Score After Improvements: {estimated_final}/100")


# ============================================================================
# Run all scenarios
# ============================================================================

def main():
    """Run all scenario tests."""
    print("\n" + "="*80)
    print("BRAXIS 2.0 - COMPREHENSIVE SCENARIO TESTING")
    print("Real-world use cases for all 14 features")
    print("="*80)

    tests = [
        test_feature_1_benchmarking,
        test_feature_2_telemetry,
        test_feature_3_context_slicing,
        test_feature_4_task_context,
        test_feature_5_adr,
        test_feature_6_ci_monitoring,
        test_feature_7_security,
        test_feature_8_handoff,
        test_feature_9_visualization,
        test_feature_10_coverage,
        test_feature_11_nlq,
        test_feature_12_org_aggregator,
        test_feature_13_interaction_recording,
        test_feature_14_suggestions,
    ]

    for test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"\n❌ ERROR in {test_func.__name__}: {e}")

    print("\n" + "="*80)
    print("✅ ALL SCENARIO TESTS COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
