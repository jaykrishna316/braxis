#!/usr/bin/env python3
"""
Item #6: Template-Based Context System (Control Baseline)

Naive, hardcoded file patterns for A/B testing against real analysis.
"""

from enum import Enum
from typing import List


class TaskType(Enum):
    """Task types for template suggestions."""
    ADD_ENDPOINT = "add_endpoint"
    FIX_BUG = "fix_bug"
    ADD_TEST = "add_test"
    REFACTOR = "refactor"
    SECURITY = "security"


class TemplateContextGenerator:
    """
    Generates context using hardcoded template patterns.

    This is the NAIVE baseline for comparison:
    - No real analysis
    - Guesses based on task type only
    - Always suggests the same files for each task type
    """

    # Hardcoded templates: what a naive system would suggest
    TEMPLATE_PATTERNS = {
        TaskType.ADD_ENDPOINT: [
            "braxis.py",           # Main file (always)
            "AGENTS.md",           # For API docs
            "test_braxis.py"       # For tests
        ],
        TaskType.FIX_BUG: [
            "braxis.py",           # Main logic
            "test_braxis.py",      # Test to verify fix
        ],
        TaskType.ADD_TEST: [
            "test_braxis.py",      # Test file
            "tests/",              # Test directory
        ],
        TaskType.REFACTOR: [
            "braxis.py",           # Code to refactor
            "test_braxis.py",      # Tests to ensure no regression
        ],
        TaskType.SECURITY: [
            "braxis.py",           # Security fix location
            "test_braxis.py",      # Security tests
        ],
    }

    def generate_context(self, task_type: TaskType) -> List[str]:
        """
        Generate context for a task using ONLY the task type.

        No real analysis - just returns hardcoded patterns.
        """
        return self.TEMPLATE_PATTERNS.get(task_type, ["braxis.py"])

    def generate_for_task_dict(self, task: dict) -> List[str]:
        """Generate context from a task dictionary."""
        task_type_str = task.get("type", "ADD_ENDPOINT")
        try:
            task_type = TaskType[task_type_str]
        except KeyError:
            task_type = TaskType.ADD_ENDPOINT

        return self.generate_context(task_type)


def demonstrate_template_system():
    """Show how template system works vs real analysis."""

    generator = TemplateContextGenerator()

    print("=" * 70)
    print("TEMPLATE-BASED CONTEXT SYSTEM (Naive Baseline)")
    print("=" * 70)
    print("\nHow it works:")
    print("- No real codebase analysis")
    print("- Hardcoded patterns per task type")
    print("- Same suggestions for all projects")
    print("- Expected to be much less accurate than real analysis")

    print("\n" + "=" * 70)
    print("Template Patterns by Task Type")
    print("=" * 70)

    for task_type, patterns in generator.TEMPLATE_PATTERNS.items():
        print(f"\n{task_type.value.upper()}:")
        for pattern in patterns:
            print(f"  - {pattern}")

    print("\n" + "=" * 70)
    print("Example: ADD_ENDPOINT Task")
    print("=" * 70)

    task = {
        "id": "ADD_COMMAND_001",
        "type": "ADD_ENDPOINT",
        "title": "Add 'braxis score' command",
    }

    template_context = generator.generate_for_task_dict(task)

    print(f"\nTask: {task['title']}")
    print(f"\nTemplate System Suggests:")
    for f in template_context:
        print(f"  - {f}")

    # What was actually needed (from Item #4 validation)
    actual_needed = ["braxis.py", "AGENTS.md"]

    print(f"\nActually Needed:")
    for f in actual_needed:
        print(f"  - {f}")

    # Calculate metrics
    suggested_set = set(template_context)
    needed_set = set(actual_needed)
    intersection = suggested_set & needed_set

    precision = len(intersection) / len(suggested_set) if suggested_set else 0
    recall = len(intersection) / len(needed_set) if needed_set else 0

    print(f"\nTemplate Accuracy:")
    print(f"  Precision: {precision:.2f} ({len(intersection)}/{len(suggested_set)})")
    print(f"  Recall: {recall:.2f} ({len(intersection)}/{len(needed_set)})")
    print(f"  F1: {2*precision*recall/(precision+recall) if precision+recall > 0 else 0:.2f}")

    print("\n" + "=" * 70)
    print("Key Point")
    print("=" * 70)
    print("\nTemplate system ALWAYS suggests the same files for each task type,")
    print("regardless of the actual codebase or task requirements.")
    print("\nThis is the CONTROL group in the A/B test.")
    print("It represents what agents would do WITHOUT Braxis context generation.")


if __name__ == "__main__":
    demonstrate_template_system()
