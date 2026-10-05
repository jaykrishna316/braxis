"""
Feature 14: Readiness Improvement Suggestions
Analyzes current score and suggests highest-ROI improvements.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class ImprovementArea(Enum):
    """Areas that can be improved."""
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"
    CONVENTIONS = "conventions"
    SECURITY = "security"
    ENTRY_POINTS = "entry_points"
    DEPENDENCIES = "dependencies"
    BUILD = "build"


@dataclass
class Improvement:
    """A suggested improvement."""
    area: ImprovementArea
    current_score: int
    target_score: int
    effort_estimate: str  # "quick", "medium", "large"
    time_estimate_hours: int
    expected_roi_points: int
    description: str
    action_items: List[str]
    success_criteria: List[str]


@dataclass
class ImprovementPlan:
    """A plan to improve readiness."""
    current_score: int
    target_score: int
    total_estimated_hours: int
    improvements: List[Improvement]
    priority_order: List[ImprovementArea]


class ImprovementSuggester:
    """Suggests improvements to increase AI-readiness."""

    IMPROVEMENT_DB = {
        ImprovementArea.TESTING: [
            {
                "threshold": 30,
                "actions": [
                    "Set up pytest with basic fixtures",
                    "Write tests for main functions",
                    "Configure coverage tracking"
                ],
                "roi": 15,
                "hours": 8,
                "description": "Add basic unit test infrastructure"
            },
            {
                "threshold": 50,
                "actions": [
                    "Achieve 60%+ code coverage",
                    "Add integration tests",
                    "Set up CI test runs"
                ],
                "roi": 12,
                "hours": 16,
                "description": "Improve test coverage and automation"
            },
            {
                "threshold": 70,
                "actions": [
                    "Reach 80%+ code coverage",
                    "Add E2E tests for critical paths",
                    "Implement performance tests"
                ],
                "roi": 10,
                "hours": 24,
                "description": "Comprehensive test coverage"
            }
        ],
        ImprovementArea.DOCUMENTATION: [
            {
                "threshold": 20,
                "actions": [
                    "Create/update README.md",
                    "Add API documentation",
                    "Document main entry points"
                ],
                "roi": 12,
                "hours": 6,
                "description": "Basic documentation foundation"
            },
            {
                "threshold": 50,
                "actions": [
                    "Create AGENTS.md context file",
                    "Add architecture overview",
                    "Document code examples"
                ],
                "roi": 15,
                "hours": 12,
                "description": "Comprehensive AI-agent context"
            }
        ],
        ImprovementArea.ARCHITECTURE: [
            {
                "threshold": 40,
                "actions": [
                    "Map current architecture",
                    "Create architecture.md",
                    "Identify main components"
                ],
                "roi": 10,
                "hours": 8,
                "description": "Document existing architecture"
            },
            {
                "threshold": 70,
                "actions": [
                    "Refactor for modularity",
                    "Create component boundaries",
                    "Implement clear interfaces"
                ],
                "roi": 12,
                "hours": 32,
                "description": "Improve code modularity"
            }
        ],
        ImprovementArea.CONVENTIONS: [
            {
                "threshold": 30,
                "actions": [
                    "Define naming conventions",
                    "Set up linting (ruff/flake8)",
                    "Create style guide"
                ],
                "roi": 10,
                "hours": 6,
                "description": "Establish code style"
            },
            {
                "threshold": 60,
                "actions": [
                    "Enforce linting in CI",
                    "Document patterns",
                    "Run formatter on codebase"
                ],
                "roi": 8,
                "hours": 8,
                "description": "Automate style enforcement"
            }
        ],
        ImprovementArea.SECURITY: [
            {
                "threshold": 40,
                "actions": [
                    "Add input validation",
                    "Set up security scanning",
                    "Document security practices"
                ],
                "roi": 12,
                "hours": 12,
                "description": "Basic security hardening"
            },
            {
                "threshold": 70,
                "actions": [
                    "Add authentication/authorization",
                    "Implement error handling",
                    "Add security tests"
                ],
                "roi": 15,
                "hours": 20,
                "description": "Comprehensive security review"
            }
        ]
    }

    def __init__(self):
        self.history: List[ImprovementPlan] = []

    def suggest_improvements(self, current_score: int,
                            target_score: int = 85) -> ImprovementPlan:
        """Generate improvement plan."""
        improvements = []
        total_hours = 0

        # Always suggest improvements in priority order
        priority_order = [
            ImprovementArea.TESTING,
            ImprovementArea.DOCUMENTATION,
            ImprovementArea.SECURITY,
            ImprovementArea.ARCHITECTURE,
            ImprovementArea.CONVENTIONS,
            ImprovementArea.ENTRY_POINTS,
            ImprovementArea.DEPENDENCIES,
            ImprovementArea.BUILD
        ]

        for area in priority_order:
            if area not in self.IMPROVEMENT_DB:
                continue

            area_improvements = self.IMPROVEMENT_DB[area]

            # Find relevant improvements for current score
            for imp in area_improvements:
                if current_score < imp["threshold"]:
                    effort_map = {
                        1: "quick",
                        8: "medium",
                        24: "large"
                    }

                    hours = imp["hours"]
                    effort = effort_map.get(hours, "medium")

                    improvement = Improvement(
                        area=area,
                        current_score=current_score,
                        target_score=target_score,
                        effort_estimate=effort,
                        time_estimate_hours=hours,
                        expected_roi_points=imp["roi"],
                        description=imp["description"],
                        action_items=imp["actions"],
                        success_criteria=[
                            f"Score increases by {imp['roi']} points",
                            "All action items completed",
                            "CI passes with new requirements"
                        ]
                    )

                    improvements.append(improvement)
                    total_hours += hours

                    # Stop if we've suggested enough
                    if len(improvements) >= 3:
                        break

            if len(improvements) >= 3:
                break

        # Sort by ROI/effort ratio
        improvements.sort(
            key=lambda x: x.expected_roi_points / max(1, x.time_estimate_hours),
            reverse=True
        )

        plan = ImprovementPlan(
            current_score=current_score,
            target_score=target_score,
            total_estimated_hours=total_hours,
            improvements=improvements[:3],  # Top 3 suggestions
            priority_order=priority_order
        )

        self.history.append(plan)
        return plan

    def get_quick_wins(self, current_score: int, max_hours: int = 8) -> List[Improvement]:
        """Get improvements that can be done quickly."""
        plan = self.suggest_improvements(current_score)

        quick_wins = [
            imp for imp in plan.improvements
            if imp.time_estimate_hours <= max_hours
        ]

        return sorted(quick_wins, key=lambda x: x.expected_roi_points, reverse=True)

    def estimate_score(self, current_score: int,
                      improvements: List[Improvement]) -> int:
        """Estimate score after applying improvements."""
        estimated = current_score

        for imp in improvements:
            estimated += imp.expected_roi_points

        return min(100, estimated)

    def generate_improvement_report(self, current_score: int,
                                   target_score: int) -> str:
        """Generate readable improvement report."""
        plan = self.suggest_improvements(current_score, target_score)

        report = f"# AI-Readiness Improvement Plan\n\n"
        report += f"**Current Score:** {current_score}/100\n"
        report += f"**Target Score:** {target_score}/100\n"
        report += f"**Gap:** {target_score - current_score} points\n"
        report += f"**Estimated Time:** {plan.total_estimated_hours} hours\n\n"

        report += "## Top 3 High-ROI Improvements\n\n"

        for i, imp in enumerate(plan.improvements, 1):
            roi_ratio = imp.expected_roi_points / max(1, imp.time_estimate_hours)

            report += f"### {i}. {imp.area.value.upper()} ({imp.effort_estimate})\n"
            report += f"**ROI:** +{imp.expected_roi_points} points in {imp.time_estimate_hours} hours "
            report += f"({roi_ratio:.2f} pts/hr)\n"
            report += f"**Description:** {imp.description}\n\n"

            report += "**Action Items:**\n"
            for action in imp.action_items:
                report += f"- {action}\n"
            report += "\n"

            report += "**Success Criteria:**\n"
            for criteria in imp.success_criteria:
                report += f"- {criteria}\n"
            report += "\n"

        estimated_final = self.estimate_score(current_score, plan.improvements)
        report += f"## Estimated Result\n"
        report += f"After completing these improvements: **{estimated_final}/100** "
        report += f"(+{estimated_final - current_score} points)\n"

        return report
