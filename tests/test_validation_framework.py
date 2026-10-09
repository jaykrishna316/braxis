"""
Validation framework for Braxis 2.0 claims.

This module provides test infrastructure for:
1. Complexity-based onboarding formula validation
2. Context relevance metric validation
3. Real-analysis vs template hypothesis testing
4. Security scanning accuracy validation
"""

import os
import json
import tempfile
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum

# Import Braxis modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from braxis_handoff_enhanced import (
    ProjectComplexity,
    HandoffCoordinatorEnhanced,
    OnboardingPlan
)
from braxis_task_context_enhanced import (
    TaskType,
    TaskContextGeneratorEnhanced
)

# pytest import is optional - used only when running as test suite
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False


class OnboardingValidationType(Enum):
    """Types of onboarding validation data."""
    PREDICTED = "predicted"
    ACTUAL = "actual"
    VARIANCE = "variance"


@dataclass
class OnboardingValidationResult:
    """Result of onboarding duration validation against real data."""
    project_name: str
    predicted_days: int
    actual_days: int
    variance_percent: float
    complexity_level: ProjectComplexity
    team_experience: str  # junior, mid, senior
    domain: str
    file_count: int
    py_files: int
    has_ci_cd: bool
    validation_notes: str


@dataclass
class ContextRelevanceResult:
    """Result of context relevance metric validation."""
    task_type: TaskType
    query: str
    agent_response_success: bool
    context_relevance_score: float
    files_actually_needed: List[str]
    files_suggested: List[str]
    precision: float  # suggested ∩ needed / suggested
    recall: float  # suggested ∩ needed / needed
    validation_notes: str


class OnboardingValidationFramework:
    """Framework for validating complexity-based onboarding formula."""

    def __init__(self):
        self.validation_data: List[OnboardingValidationResult] = []
        self.coordinator = HandoffCoordinatorEnhanced()

    def record_prediction(self, project_path: str, project_name: str) -> OnboardingPlan:
        """Record Braxis's predicted onboarding duration for a project."""
        analysis = self.coordinator.analyze_project_complexity(project_path)
        plan = self.coordinator.generate_onboarding_plan("Developer", project_path)

        print(f"[VALIDATION] Project: {project_name}")
        print(f"  Complexity: {analysis['complexity_level'].value}")
        print(f"  Predicted duration: {plan.duration_days} days")
        print(f"  Metrics: {analysis['py_files']} py files, {analysis['file_count']} total files")
        print(f"  CI/CD: {analysis['has_ci_cd']}")

        return plan

    def record_actual(
        self,
        project_name: str,
        predicted_days: int,
        actual_days: int,
        team_experience: str,
        domain: str,
        file_count: int,
        py_files: int,
        has_ci_cd: bool,
        complexity_level: ProjectComplexity,
        notes: str = ""
    ) -> OnboardingValidationResult:
        """Record actual onboarding duration from real team data."""
        variance = ((actual_days - predicted_days) / predicted_days) * 100 if predicted_days > 0 else 0

        result = OnboardingValidationResult(
            project_name=project_name,
            predicted_days=predicted_days,
            actual_days=actual_days,
            variance_percent=variance,
            complexity_level=complexity_level,
            team_experience=team_experience,
            domain=domain,
            file_count=file_count,
            py_files=py_files,
            has_ci_cd=has_ci_cd,
            validation_notes=notes
        )

        self.validation_data.append(result)
        return result

    def get_summary(self) -> Dict:
        """Get summary statistics of validation results."""
        if not self.validation_data:
            return {"message": "No validation data recorded"}

        variances = [r.variance_percent for r in self.validation_data]
        avg_variance = sum(variances) / len(variances)
        max_variance = max(variances)
        min_variance = min(variances)

        # Grouped by complexity
        by_complexity = {}
        for result in self.validation_data:
            level = result.complexity_level.value
            if level not in by_complexity:
                by_complexity[level] = []
            by_complexity[level].append(result.variance_percent)

        complexity_summary = {
            level: {
                "count": len(values),
                "avg_variance": sum(values) / len(values),
                "max_variance": max(values),
                "min_variance": min(values)
            }
            for level, values in by_complexity.items()
        }

        # Grouped by experience
        by_experience = {}
        for result in self.validation_data:
            exp = result.team_experience
            if exp not in by_experience:
                by_experience[exp] = []
            by_experience[exp].append(result.variance_percent)

        experience_summary = {
            exp: {
                "count": len(values),
                "avg_variance": sum(values) / len(values)
            }
            for exp, values in by_experience.items()
        }

        return {
            "total_projects": len(self.validation_data),
            "average_variance_percent": avg_variance,
            "max_variance_percent": max_variance,
            "min_variance_percent": min_variance,
            "by_complexity": complexity_summary,
            "by_experience": experience_summary,
            "raw_data": [asdict(r) for r in self.validation_data]
        }

    def export_json(self, filepath: str):
        """Export validation results to JSON for analysis."""
        with open(filepath, 'w') as f:
            json.dump(self.get_summary(), f, indent=2, default=str)


class ContextRelevanceValidationFramework:
    """Framework for validating context relevance metrics."""

    def __init__(self):
        self.validation_data: List[ContextRelevanceResult] = []
        self.generator = TaskContextGeneratorEnhanced()

    def record_task_validation(
        self,
        task_type: TaskType,
        query: str,
        agent_response_success: bool,
        context_relevance_score: float,
        files_actually_needed: List[str],
        files_suggested: List[str],
        notes: str = ""
    ) -> ContextRelevanceResult:
        """Record result of an agent task using Braxis context."""

        # Calculate precision and recall
        suggested_set = set(files_suggested)
        needed_set = set(files_actually_needed)
        intersection = suggested_set & needed_set

        precision = len(intersection) / len(suggested_set) if suggested_set else 0
        recall = len(intersection) / len(needed_set) if needed_set else 0

        result = ContextRelevanceResult(
            task_type=task_type,
            query=query,
            agent_response_success=agent_response_success,
            context_relevance_score=context_relevance_score,
            files_actually_needed=files_actually_needed,
            files_suggested=files_suggested,
            precision=precision,
            recall=recall,
            validation_notes=notes
        )

        self.validation_data.append(result)
        return result

    def get_summary(self) -> Dict:
        """Get summary of context relevance validation."""
        if not self.validation_data:
            return {"message": "No validation data recorded"}

        total = len(self.validation_data)
        successful = sum(1 for r in self.validation_data if r.agent_response_success)
        success_rate = (successful / total * 100) if total > 0 else 0

        avg_relevance = sum(r.context_relevance_score for r in self.validation_data) / total
        avg_precision = sum(r.precision for r in self.validation_data) / total
        avg_recall = sum(r.recall for r in self.validation_data) / total

        # By task type
        by_task = {}
        for result in self.validation_data:
            task = result.task_type.value
            if task not in by_task:
                by_task[task] = {"count": 0, "success": 0, "relevances": []}
            by_task[task]["count"] += 1
            by_task[task]["success"] += 1 if result.agent_response_success else 0
            by_task[task]["relevances"].append(result.context_relevance_score)

        task_summary = {
            task: {
                "count": data["count"],
                "success_rate": (data["success"] / data["count"] * 100),
                "avg_relevance": sum(data["relevances"]) / len(data["relevances"])
            }
            for task, data in by_task.items()
        }

        return {
            "total_tasks": total,
            "successful_tasks": successful,
            "success_rate_percent": success_rate,
            "average_context_relevance": avg_relevance,
            "average_precision": avg_precision,
            "average_recall": avg_recall,
            "by_task_type": task_summary,
            "raw_data": [asdict(r) for r in self.validation_data]
        }

    def export_json(self, filepath: str):
        """Export validation results to JSON."""
        with open(filepath, 'w') as f:
            json.dump(self.get_summary(), f, indent=2, default=str)


class RealVsTemplateValidation:
    """Framework for testing real-analysis vs template-based context hypothesis."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.generator = TaskContextGeneratorEnhanced()

    def test_framework_detection_real_vs_template(self) -> Dict:
        """Compare framework detection: real analysis vs static templates."""
        # Real analysis
        analysis = self.generator.analyze_repo_structure(self.repo_path)
        real_frameworks = set()
        if analysis.get("has_fastapi"):
            real_frameworks.add("FastAPI")
        if analysis.get("has_flask"):
            real_frameworks.add("Flask")
        if analysis.get("has_django"):
            real_frameworks.add("Django")

        # Template-based (naive approach)
        template_frameworks = set()
        # This would be hardcoded based on project structure assumptions
        # In reality, template approach would just guess based on repo name/size
        if "api" in self.repo_path.lower():
            template_frameworks.add("FastAPI")  # Wrong assumption
        if "web" in self.repo_path.lower():
            template_frameworks.add("Django")   # Wrong assumption

        return {
            "detected_by_real_analysis": list(real_frameworks),
            "guessed_by_template": list(template_frameworks),
            "accuracy_advantage": len(real_frameworks & template_frameworks) / max(len(real_frameworks), len(template_frameworks), 1)
        }

    def test_task_routing_real_vs_template(self, task_type: TaskType) -> Dict:
        """Compare task-specific context routing: real vs template."""
        # Real analysis uses actual file patterns
        analysis = self.generator.analyze_repo_structure(self.repo_path)
        profile = self.generator.generate_profile_from_analysis(task_type, analysis)
        real_files = profile.relevant_file_patterns

        # Template approach would hardcode file patterns
        template_patterns = {
            TaskType.ADD_ENDPOINT: ["src/routes.py", "src/api.py", "tests/**/*.py"],
            TaskType.FIX_BUG: ["tests/**/*.py", "src/**/*.py"],
            TaskType.ADD_TEST: ["tests/**/*.py", "conftest.py"],
            TaskType.REFACTOR: ["src/**/*.py"],
        }
        template_files = template_patterns.get(task_type, ["src/**/*.py"])

        return {
            "task_type": task_type.value,
            "real_analysis_files": real_files[:5],
            "template_files": template_files,
            "real_analysis_is_specific": len(real_files) > 0,
            "template_is_generic": all("**" in f or "/**" in f for f in template_files)
        }


# Test functions for pytest integration

if HAS_PYTEST:
    def test_validation_framework_instantiation():
        """Test that validation frameworks can be instantiated."""
        onboarding_fw = OnboardingValidationFramework()
        assert onboarding_fw is not None

        context_fw = ContextRelevanceValidationFramework()
        assert context_fw is not None


    def test_onboarding_validation_recording():
        """Test recording onboarding validation data."""
        fw = OnboardingValidationFramework()

        result = fw.record_actual(
            project_name="test_project",
            predicted_days=7,
            actual_days=9,
            team_experience="mid",
            domain="web_api",
            file_count=85,
            py_files=35,
            has_ci_cd=True,
            complexity_level=ProjectComplexity.MODERATE,
            notes="Team had to learn custom auth framework"
        )

        assert result.variance_percent == pytest.approx(28.57, abs=0.1)
        assert len(fw.validation_data) == 1


    def test_context_relevance_validation_recording():
        """Test recording context relevance validation data."""
        fw = ContextRelevanceValidationFramework()

        result = fw.record_task_validation(
            task_type=TaskType.ADD_ENDPOINT,
            query="Add POST /users endpoint",
            agent_response_success=True,
            context_relevance_score=0.85,
            files_actually_needed=["src/routes.py", "src/models.py", "tests/test_api.py"],
            files_suggested=["src/routes.py", "src/models.py", "src/auth.py", "tests/test_api.py"],
            notes="Agent suggested auth.py but didn't need it"
        )

        assert result.precision == 0.75  # 3 out of 4 suggested were needed
        assert result.recall == 1.0      # Got all 3 needed files
        assert len(fw.validation_data) == 1


    def test_real_vs_template_framework_detection(tmp_path):
        """Test real-analysis advantage over template-based detection."""
        # Create a test project structure
        repo = tmp_path / "test_repo"
        repo.mkdir()

        # Create a Flask app to detect
        (repo / "app.py").write_text("from flask import Flask\napp = Flask(__name__)")
        (repo / "requirements.txt").write_text("Flask==2.0.0")

        validator = RealVsTemplateValidation(str(repo))
        result = validator.test_framework_detection_real_vs_template()

        assert "Flask" in result["detected_by_real_analysis"]
        assert result["accuracy_advantage"] > 0


if __name__ == "__main__":
    # Example usage
    fw = OnboardingValidationFramework()

    # Simulate recording validation data for a few projects
    fw.record_actual(
        project_name="project_a",
        predicted_days=3,
        actual_days=2,
        team_experience="senior",
        domain="cli_tool",
        file_count=25,
        py_files=8,
        has_ci_cd=False,
        complexity_level=ProjectComplexity.SIMPLE
    )

    fw.record_actual(
        project_name="project_b",
        predicted_days=7,
        actual_days=11,
        team_experience="junior",
        domain="web_api",
        file_count=95,
        py_files=40,
        has_ci_cd=True,
        complexity_level=ProjectComplexity.MODERATE,
        notes="Team struggled with async patterns"
    )

    print("\n=== VALIDATION SUMMARY ===")
    print(json.dumps(fw.get_summary(), indent=2))

    # Export for analysis
    fw.export_json("/tmp/validation_results.json")
    print("\nResults exported to /tmp/validation_results.json")
