"""
Braxis Programmatic API
Expose Braxis functionality as a Python library for integration into custom tools.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
from braxis_config import BraxisConfig
from braxis_triggers import SmartTrigger, ChangeMetrics


@dataclass
class AIReadinessScore:
    """AI Readiness Score data model."""
    total: int
    architecture: int
    testing: int
    dependencies: int
    conventions: int
    entry_points: int
    security: int
    build: int
    documentation: int
    timestamp: datetime = field(default_factory=datetime.now)
    level: str = ""  # "AI-Hostile", "AI-Aware", "AI-Native"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total": self.total,
            "architecture": self.architecture,
            "testing": self.testing,
            "dependencies": self.dependencies,
            "conventions": self.conventions,
            "entry_points": self.entry_points,
            "security": self.security,
            "build": self.build,
            "documentation": self.documentation,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
        }

    def get_dimensions(self) -> Dict[str, int]:
        """Get all dimension scores."""
        return {
            "architecture": self.architecture,
            "testing": self.testing,
            "dependencies": self.dependencies,
            "conventions": self.conventions,
            "entry_points": self.entry_points,
            "security": self.security,
            "build": self.build,
            "documentation": self.documentation,
        }


@dataclass
class GenerationResult:
    """Result of context file generation."""
    success: bool
    changed_files: List[str] = field(default_factory=list)
    changes: Dict[str, str] = field(default_factory=dict)  # filename -> content
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    files_generated: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "changed_files": self.changed_files,
            "num_changes": len(self.changes),
            "num_files_generated": self.files_generated,
            "errors": self.errors,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Suggestion:
    """Suggestion for improving AI readiness."""
    dimension: str
    current_score: int
    target_score: int
    actions: List[str]
    priority: str  # "high", "medium", "low"
    estimated_effort: str = "medium"  # "low", "medium", "high"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "dimension": self.dimension,
            "current_score": self.current_score,
            "target_score": self.target_score,
            "actions": self.actions,
            "priority": self.priority,
            "estimated_effort": self.estimated_effort,
        }


class ContextGenerator:
    """Generate context files from a codebase."""

    def __init__(self, project_path: str = ".", config: Optional[BraxisConfig] = None):
        self.project_path = Path(project_path).resolve()
        self.config = config or BraxisConfig.load()
        self._validate_project()

    def _validate_project(self) -> None:
        """Validate project path exists."""
        if not self.project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {self.project_path}")
        if not self.project_path.is_dir():
            raise NotADirectoryError(f"Project path is not a directory: {self.project_path}")

    def generate(self) -> GenerationResult:
        """
        Generate context files for the project.

        Returns:
            GenerationResult with changes made
        """
        try:
            # Import here to avoid circular imports
            import sys
            sys.path.insert(0, str(self.project_path.parent))

            from braxis import BraxisAnalyzer

            analyzer = BraxisAnalyzer(str(self.project_path))
            analyzer.analyze()

            changes = {
                "AGENTS.md": analyzer.generate_agents_md(),
                "CLAUDE.md": analyzer.generate_claude_md(),
                ".cursorrules": analyzer.generate_cursorrules(),
                ".agentic-config.json": analyzer.generate_agentic_config(),
            }

            return GenerationResult(
                success=True,
                changes=changes,
                files_generated=len(changes),
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                errors=[str(e)],
            )

    def generate_specific(self, files: List[str]) -> GenerationResult:
        """Generate specific context files."""
        try:
            from braxis import BraxisAnalyzer

            analyzer = BraxisAnalyzer(str(self.project_path))
            analyzer.analyze()

            changes = {}
            for file in files:
                if file == "AGENTS.md":
                    changes["AGENTS.md"] = analyzer.generate_agents_md()
                elif file == "CLAUDE.md":
                    changes["CLAUDE.md"] = analyzer.generate_claude_md()
                elif file == ".cursorrules":
                    changes[".cursorrules"] = analyzer.generate_cursorrules()
                elif file == ".agentic-config.json":
                    changes[".agentic-config.json"] = analyzer.generate_agentic_config()

            return GenerationResult(
                success=True,
                changes=changes,
                files_generated=len(changes),
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                errors=[str(e)],
            )


class ScoreAnalyzer:
    """Analyze AI readiness score."""

    def __init__(self, project_path: str = ".", config: Optional[BraxisConfig] = None):
        self.project_path = Path(project_path).resolve()
        self.config = config or BraxisConfig.load()
        self._analyzer = None

    def _get_analyzer(self):
        """Lazy load BraxisAnalyzer."""
        if self._analyzer is None:
            from braxis import BraxisAnalyzer
            self._analyzer = BraxisAnalyzer(str(self.project_path))
            self._analyzer.analyze()
        return self._analyzer

    def calculate(self) -> AIReadinessScore:
        """Calculate AI readiness score."""
        analyzer = self._get_analyzer()
        score = analyzer.get_overall_score()
        tier = analyzer.get_tier(score)

        # Map score_breakdown to individual scores
        breakdown = analyzer.score_breakdown
        return AIReadinessScore(
            total=score,
            architecture=breakdown.get("Architecture", 10),
            testing=breakdown.get("Testing", 7),
            dependencies=breakdown.get("Dependencies", 12),
            conventions=breakdown.get("Conventions", 10),
            entry_points=breakdown.get("Entry Points", 4),
            security=breakdown.get("Security", 10),
            build=breakdown.get("Build", 10),
            documentation=breakdown.get("Documentation", 8),
            level=tier,
        )

    def get_dimension_scores(self) -> Dict[str, int]:
        """Get scores for each dimension."""
        return self.calculate().get_dimensions()

    def get_improvement_suggestions(self) -> List[Suggestion]:
        """Get suggestions for improving AI readiness."""
        score = self.calculate()
        suggestions = []

        # Suggest improvements for low-scoring dimensions
        for dimension, dim_score in score.get_dimensions().items():
            if dim_score < 25:
                priority = "high"
            elif dim_score < 50:
                priority = "medium"
            else:
                priority = "low"

            if dim_score < 75:  # Only suggest for dimensions below 75
                suggestion = self._get_dimension_suggestion(dimension, dim_score)
                if suggestion:
                    suggestions.append(suggestion)

        return sorted(suggestions, key=lambda s: s.priority == "high", reverse=True)

    @staticmethod
    def _get_dimension_suggestion(dimension: str, current_score: int) -> Optional[Suggestion]:
        """Get improvement suggestion for a dimension."""
        suggestions_map = {
            "architecture": Suggestion(
                dimension="architecture",
                current_score=current_score,
                target_score=50,
                actions=[
                    "Organize code into clear modules",
                    "Separate concerns (business logic, I/O, presentation)",
                    "Create clear package structure",
                    "Document architecture decisions",
                ],
                priority="high",
            ),
            "testing": Suggestion(
                dimension="testing",
                current_score=current_score,
                target_score=50,
                actions=[
                    "Add unit tests for core functionality",
                    "Implement integration tests",
                    "Aim for 70%+ code coverage",
                    "Document test strategy",
                ],
                priority="high",
            ),
            "entry_points": Suggestion(
                dimension="entry_points",
                current_score=current_score,
                target_score=50,
                actions=[
                    "Create clear main entry point",
                    "Document command-line interface",
                    "Add CLI help documentation",
                    "Define initialization procedures",
                ],
                priority="high",
            ),
            "documentation": Suggestion(
                dimension="documentation",
                current_score=current_score,
                target_score=50,
                actions=[
                    "Write comprehensive README",
                    "Add code comments for complex sections",
                    "Document API interfaces",
                    "Create architecture documentation",
                ],
                priority="medium",
            ),
            "conventions": Suggestion(
                dimension="conventions",
                current_score=current_score,
                target_score=50,
                actions=[
                    "Follow language naming conventions",
                    "Use consistent code style",
                    "Implement linting (ruff, pylint)",
                    "Set up code formatting (black, prettier)",
                ],
                priority="medium",
            ),
        }

        return suggestions_map.get(dimension)


class TrendAnalyzer:
    """Analyze score trends over time."""

    def __init__(self, project_path: str = ".", history_file: Optional[str] = None):
        self.project_path = Path(project_path).resolve()
        self.history_file = Path(history_file) if history_file else None

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get score history."""
        try:
            from braxis import BraxisAnalyzer
            analyzer = BraxisAnalyzer(str(self.project_path))
            history = analyzer.get_score_history(limit)
            return history
        except Exception:
            return []

    def get_trend(self, dimension: str) -> Optional[Dict[str, Any]]:
        """Get trend for a specific dimension."""
        history = self.get_history(limit=10)
        if not history:
            return None

        scores = [h.get("score_breakdown", {}).get(dimension) for h in history]
        scores = [s for s in scores if s is not None]

        if not scores:
            return None

        return {
            "dimension": dimension,
            "scores": scores,
            "average": sum(scores) / len(scores),
            "trend": "improving" if scores[-1] > scores[0] else "declining",
        }

    def predict_score(self, days_ahead: int) -> Optional[int]:
        """Predict future score based on trend."""
        history = self.get_history(limit=30)
        if len(history) < 2:
            return None

        # Simple linear regression
        scores = [h.get("total_score", 0) for h in history]
        if not scores:
            return None

        avg_change = (scores[-1] - scores[0]) / max(1, len(scores) - 1)
        predicted = scores[-1] + (avg_change * days_ahead)

        return max(0, min(100, int(predicted)))


class MultiRepoAnalyzer:
    """Analyze multiple repositories."""

    def __init__(self, repos: List[str], config: Optional[BraxisConfig] = None):
        self.repos = repos
        self.config = config or BraxisConfig.load()

    def analyze_all(self) -> Dict[str, AIReadinessScore]:
        """Analyze all repositories."""
        results = {}

        for repo in self.repos:
            try:
                analyzer = ScoreAnalyzer(repo, self.config)
                results[repo] = analyzer.calculate()
            except Exception as e:
                print(f"Warning: Could not analyze {repo}: {e}")

        return results

    def get_org_summary(self) -> Dict[str, Any]:
        """Get organization-wide summary."""
        results = self.analyze_all()

        if not results:
            return {"error": "No repositories analyzed"}

        scores = list(results.values())
        avg_score = sum(s.total for s in scores) / len(scores)

        dimension_avgs = {}
        for dim in scores[0].get_dimensions().keys():
            dimension_avgs[dim] = sum(s.get_dimensions()[dim] for s in scores) / len(scores)

        return {
            "num_repos": len(results),
            "average_score": int(avg_score),
            "dimension_averages": dimension_avgs,
            "repos": {name: score.to_dict() for name, score in results.items()},
        }
