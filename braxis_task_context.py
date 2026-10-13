"""
Feature 4: Task-Specific Context Generation
Automatically slices most relevant context based on task type.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from enum import Enum


class TaskType(Enum):
    """Types of development tasks."""
    ADD_ENDPOINT = "add_endpoint"
    FIX_BUG = "fix_bug"
    ADD_TEST = "add_test"
    REFACTOR = "refactor"
    UPDATE_DOCS = "update_docs"
    ADD_FEATURE = "add_feature"
    OPTIMIZE = "optimize"
    SECURITY = "security"


@dataclass
class TaskProfile:
    """Profile for a specific task type."""
    task_type: TaskType
    description: str
    relevant_file_patterns: List[str]
    relevant_sections: List[str]
    relevant_examples: int
    key_concepts: List[str]


class TaskContextGenerator:
    """Generates task-specific context slices."""

    TASK_PROFILES = {
        TaskType.ADD_ENDPOINT: TaskProfile(
            task_type=TaskType.ADD_ENDPOINT,
            description="Adding a new API endpoint",
            relevant_file_patterns=[
                "**/*route*.py", "**/*api*.py", "**/*handler*.py",
                "tests/**/*test*endpoint*.py"
            ],
            relevant_sections=[
                "API Structure", "Routing Patterns", "Request/Response",
                "Error Handling", "Testing Strategy"
            ],
            relevant_examples=5,
            key_concepts=["routing", "validation", "error handling", "testing"]
        ),
        TaskType.FIX_BUG: TaskProfile(
            task_type=TaskType.FIX_BUG,
            description="Fixing a bug in the codebase",
            relevant_file_patterns=[
                "**/*bug*.md", "tests/**/*.py", "**/*debug*.py"
            ],
            relevant_sections=[
                "Architecture", "Known Issues", "Testing",
                "Anti-patterns", "Error Handling"
            ],
            relevant_examples=3,
            key_concepts=["debugging", "testing", "root cause", "regression"]
        ),
        TaskType.ADD_TEST: TaskProfile(
            task_type=TaskType.ADD_TEST,
            description="Adding test coverage",
            relevant_file_patterns=[
                "tests/**/*.py", "**/*test*.py", "**/conftest.py"
            ],
            relevant_sections=[
                "Testing Strategy", "Test Examples", "Mock Patterns",
                "Coverage Goals", "CI/CD Testing"
            ],
            relevant_examples=10,
            key_concepts=["unit test", "integration test", "fixtures", "mocks"]
        ),
        TaskType.REFACTOR: TaskProfile(
            task_type=TaskType.REFACTOR,
            description="Refactoring code for better structure",
            relevant_file_patterns=[
                "**/*.py", "src/**/*", "docs/architecture/*.md"
            ],
            relevant_sections=[
                "Architecture", "Code Patterns", "Best Practices",
                "Naming Conventions", "Module Structure"
            ],
            relevant_examples=7,
            key_concepts=["modularity", "separation of concerns", "patterns"]
        ),
        TaskType.UPDATE_DOCS: TaskProfile(
            task_type=TaskType.UPDATE_DOCS,
            description="Updating documentation",
            relevant_file_patterns=[
                "docs/**/*.md", "README.md", "AGENTS.md"
            ],
            relevant_sections=[
                "Documentation Guidelines", "Examples", "API Reference",
                "Getting Started", "Best Practices"
            ],
            relevant_examples=5,
            key_concepts=["clarity", "completeness", "examples"]
        ),
        TaskType.ADD_FEATURE: TaskProfile(
            task_type=TaskType.ADD_FEATURE,
            description="Adding a new feature",
            relevant_file_patterns=[
                "src/**/*.py", "tests/**/*.py", "docs/**/*.md"
            ],
            relevant_sections=[
                "Architecture", "API Design", "Testing",
                "Documentation", "Examples", "Roadmap"
            ],
            relevant_examples=8,
            key_concepts=["design", "implementation", "testing", "documentation"]
        ),
        TaskType.OPTIMIZE: TaskProfile(
            task_type=TaskType.OPTIMIZE,
            description="Performance optimization",
            relevant_file_patterns=[
                "**/*.py", "benchmarks/**/*", "performance/**/*"
            ],
            relevant_sections=[
                "Performance Patterns", "Bottlenecks",
                "Benchmarking", "Optimization Strategies"
            ],
            relevant_examples=3,
            key_concepts=["performance", "benchmarking", "profiling"]
        ),
        TaskType.SECURITY: TaskProfile(
            task_type=TaskType.SECURITY,
            description="Security improvements",
            relevant_file_patterns=[
                "**/*auth*.py", "**/*security*.py", "**/*validation*.py"
            ],
            relevant_sections=[
                "Security Patterns", "Input Validation",
                "Authentication", "Error Handling"
            ],
            relevant_examples=4,
            key_concepts=["validation", "authentication", "sanitization"]
        )
    }

    def __init__(self):
        self.task_cache: Dict[TaskType, str] = {}

    def get_task_profile(self, task_type: TaskType) -> TaskProfile:
        """Get profile for a task type."""
        return self.TASK_PROFILES.get(task_type)

    def generate_context(self, task_type: TaskType, full_context: str) -> str:
        """Generate task-specific context."""
        profile = self.get_task_profile(task_type)
        if not profile:
            return full_context

        # Start with header
        result = f"# Context for: {profile.description}\n"
        result += f"**Key Concepts:** {', '.join(profile.key_concepts)}\n\n"

        # Extract relevant sections
        relevant_sections = []
        for line in full_context.split('\n'):
            for section in profile.relevant_sections:
                if section.lower() in line.lower():
                    relevant_sections.append(line)

        if relevant_sections:
            result += "## Relevant Sections\n"
            result += '\n'.join(relevant_sections) + '\n\n'

        result += full_context

        self.task_cache[task_type] = result
        return result

    def suggest_files(self, task_type: TaskType) -> List[str]:
        """Suggest files to review for a task."""
        profile = self.get_task_profile(task_type)
        if not profile:
            return []

        return profile.relevant_file_patterns

    def get_task_checklist(self, task_type: TaskType) -> List[str]:
        """Get checklist for completing a task."""
        checklists = {
            TaskType.ADD_ENDPOINT: [
                "Define route and method",
                "Add request/response validation",
                "Implement error handling",
                "Write unit tests",
                "Write integration tests",
                "Update API documentation",
                "Check for security issues"
            ],
            TaskType.FIX_BUG: [
                "Reproduce the bug",
                "Write failing test",
                "Identify root cause",
                "Implement fix",
                "Verify test passes",
                "Check for regressions",
                "Update documentation if needed"
            ],
            TaskType.ADD_TEST: [
                "Identify coverage gap",
                "Write test cases",
                "Ensure tests are isolated",
                "Run full test suite",
                "Check coverage improvement",
                "Review test quality"
            ],
            TaskType.REFACTOR: [
                "Identify refactoring target",
                "Write tests if missing",
                "Plan refactoring approach",
                "Implement changes",
                "Verify all tests pass",
                "Update documentation"
            ]
        }

        return checklists.get(task_type, [])
