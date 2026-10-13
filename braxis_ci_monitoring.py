"""
Feature 6: Real-Time Readiness Monitoring in CI/CD
Integrates AI-readiness scoring with CI/CD to track changes and enforce standards.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class BuildStatus(Enum):
    """Status of a build/PR check."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    NEUTRAL = "neutral"


@dataclass
class ScoreCheckResult:
    """Result of an AI-readiness score check in CI/CD."""
    score: int
    previous_score: int
    change: int
    status: BuildStatus
    message: str
    recommendations: List[str] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)


class CIMonitor:
    """Monitors AI-readiness in CI/CD pipelines."""

    def __init__(self, failure_threshold: int = 5):
        self.failure_threshold = failure_threshold
        self.build_history: List[Dict] = []
        self.pr_checks: Dict[str, ScoreCheckResult] = {}

    def check_score_change(self, current_score: int,
                          previous_score: int) -> ScoreCheckResult:
        """Check if score change is acceptable."""
        change = current_score - previous_score

        if change < -self.failure_threshold:
            status = BuildStatus.FAILED
            message = f"Score dropped {abs(change)} points (threshold: {self.failure_threshold})"
        elif change < 0:
            status = BuildStatus.WARNING
            message = f"Score decreased by {abs(change)} points"
        elif change > 0:
            status = BuildStatus.PASSED
            message = f"Score improved by {change} points ✓"
        else:
            status = BuildStatus.NEUTRAL
            message = "Score unchanged"

        result = ScoreCheckResult(
            score=current_score,
            previous_score=previous_score,
            change=change,
            status=status,
            message=message
        )

        # Add recommendations
        if status in [BuildStatus.FAILED, BuildStatus.WARNING]:
            result.recommendations.extend([
                "Review recent commits for changes that may have degraded the score",
                "Focus on: testing coverage, documentation, architecture clarity",
                "Run `braxis score` locally to debug"
            ])

        return result

    def record_build(self, pr_number: int, commit_sha: str,
                    score: int, previous_score: int) -> ScoreCheckResult:
        """Record a build check in CI/CD."""
        result = self.check_score_change(score, previous_score)

        self.build_history.append({
            "pr": pr_number,
            "commit": commit_sha,
            "score": score,
            "status": result.status.value,
            "timestamp": datetime.now().isoformat()
        })

        self.pr_checks[f"pr-{pr_number}"] = result
        return result

    def generate_pr_comment(self, pr_number: int) -> str:
        """Generate a GitHub PR comment with score info."""
        key = f"pr-{pr_number}"
        if key not in self.pr_checks:
            return "No score check available"

        result = self.pr_checks[key]

        emoji = {
            BuildStatus.PASSED: "✅",
            BuildStatus.WARNING: "⚠️",
            BuildStatus.FAILED: "❌",
            BuildStatus.NEUTRAL: "ℹ️"
        }[result.status]

        comment = f"## {emoji} AI-Readiness Score Check\n\n"
        comment += f"**Score:** {result.score}/100 (was {result.previous_score}/100)\n"
        comment += f"**Change:** {result.change:+d} points\n"
        comment += f"**Status:** {result.status.value.upper()}\n\n"
        comment += f"{result.message}\n"

        if result.recommendations:
            comment += "\n### Suggestions\n"
            for rec in result.recommendations:
                comment += f"- {rec}\n"

        return comment

    def should_pass_check(self, check_result: ScoreCheckResult) -> bool:
        """Determine if check should pass."""
        return check_result.status not in [BuildStatus.FAILED]

    def get_badge_url(self, score: int) -> str:
        """Generate shield.io badge URL for README."""
        if score >= 90:
            color = "brightgreen"
            label = "Agent-Optimized"
        elif score >= 80:
            color = "green"
            label = "Enterprise-Ready"
        elif score >= 60:
            color = "yellowgreen"
            label = "AI-Native"
        elif score >= 30:
            color = "yellow"
            label = "Agent-Aware"
        else:
            color = "red"
            label = "Not Ready"

        return (
            f"https://img.shields.io/badge/AI--Readiness-{score}%2F100-{color}"
            f"?style=flat-square&label={label}"
        )

    def get_build_trend(self, last_n: int = 10) -> List[Dict]:
        """Get trend of recent builds."""
        recent = self.build_history[-last_n:]
        return recent

    def get_trend_summary(self) -> Dict:
        """Get summary of score trends."""
        if len(self.build_history) < 2:
            return {"trend": "insufficient_data"}

        scores = [b["score"] for b in self.build_history[-10:]]
        avg = sum(scores) / len(scores)
        latest = scores[-1]

        if latest > avg:
            direction = "📈 Improving"
        elif latest < avg:
            direction = "📉 Declining"
        else:
            direction = "→ Stable"

        return {
            "trend": direction,
            "recent_avg": avg,
            "latest": latest,
            "builds_checked": len(self.build_history)
        }
