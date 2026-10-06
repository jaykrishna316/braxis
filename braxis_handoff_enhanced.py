"""
Feature 8: Team Handoff & Onboarding (ENHANCED)
NOW CUSTOMIZES CHECKLISTS based on ACTUAL PROJECT ANALYSIS instead of static lists.
"""

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class ProjectComplexity(Enum):
    """Project complexity levels based on actual codebase analysis."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"


@dataclass
class OnboardingPlan:
    """Customized onboarding plan for a team member."""
    role: str
    duration_days: int
    complexity_level: ProjectComplexity
    phases: List[str]
    checklist: List[str]
    key_contacts: List[str]
    critical_docs: List[str]


class HandoffCoordinatorEnhanced:
    """Generates customized onboarding/offboarding based on ACTUAL project analysis."""

    def __init__(self):
        self.project_analysis: Dict = {}
        self.onboarding_plans: Dict[str, OnboardingPlan] = {}

    def analyze_project_complexity(self, repo_path: str) -> Dict:
        """REAL ANALYSIS: Determine project complexity from actual codebase."""
        analysis = {
            "file_count": 0,
            "py_files": 0,
            "test_files": 0,
            "doc_files": 0,
            "config_complexity": 0,
            "dependency_count": 0,
            "has_ci_cd": False,
            "has_monitoring": False,
            "has_database": False,
            "frameworks": [],
            "external_integrations": [],
            "team_size_suggestion": 1,
            "complexity_level": ProjectComplexity.SIMPLE
        }

        file_count = 0
        py_files = 0
        test_files = 0

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', '.git']]

            for file in files:
                file_count += 1
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, repo_path)

                if file.endswith('.py'):
                    py_files += 1
                    if 'test' in file:
                        test_files += 1

                if file.endswith(('.md', '.rst')):
                    analysis["doc_files"] += 1

                # CI/CD detection
                if file in ['github-workflow.yml', 'gitlab-ci.yml', 'Jenkinsfile', '.travis.yml']:
                    analysis["has_ci_cd"] = True

                # Database detection
                if 'migration' in file or 'schema' in file or 'database' in file:
                    analysis["has_database"] = True

                # Framework detection
                if file == 'requirements.txt' or file == 'setup.py':
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if 'fastapi' in content:
                                analysis["frameworks"].append("FastAPI")
                            if 'flask' in content:
                                analysis["frameworks"].append("Flask")
                            if 'django' in content:
                                analysis["frameworks"].append("Django")
                            if 'sqlalchemy' in content:
                                analysis["has_database"] = True
                            if 'pytest' in content:
                                analysis["dependency_count"] += 1
                    except:
                        pass

                # External integrations
                if 'integration' in rel_path or 'external' in rel_path or 'api' in file:
                    if 'api' in file and file.endswith('.py'):
                        analysis["external_integrations"].append("External APIs")

        analysis["file_count"] = file_count
        analysis["py_files"] = py_files
        analysis["test_files"] = test_files

        # Determine complexity level from actual metrics
        if py_files < 10 and file_count < 30:
            analysis["complexity_level"] = ProjectComplexity.SIMPLE
            analysis["team_size_suggestion"] = 1
        elif py_files < 50 and file_count < 100:
            analysis["complexity_level"] = ProjectComplexity.MODERATE
            analysis["team_size_suggestion"] = 2
        elif py_files < 200 and file_count < 300:
            analysis["complexity_level"] = ProjectComplexity.COMPLEX
            analysis["team_size_suggestion"] = 3
        else:
            analysis["complexity_level"] = ProjectComplexity.ENTERPRISE
            analysis["team_size_suggestion"] = 5

        # Add CI/CD and monitoring indicators to complexity
        if analysis["has_ci_cd"]:
            analysis["complexity_level"] = ProjectComplexity(
                min(ProjectComplexity.ENTERPRISE.value,
                    [c.value for c in ProjectComplexity if c.value <= analysis["complexity_level"].value][-1])
            )

        self.project_analysis = analysis
        return analysis

    def generate_onboarding_plan(self, role: str, repo_path: str) -> OnboardingPlan:
        """REAL GENERATION: Create customized onboarding from project analysis."""

        if not self.project_analysis:
            self.analyze_project_complexity(repo_path)

        analysis = self.project_analysis
        complexity = analysis["complexity_level"]

        # Duration based on actual complexity
        duration_map = {
            ProjectComplexity.SIMPLE: 3,
            ProjectComplexity.MODERATE: 7,
            ProjectComplexity.COMPLEX: 14,
            ProjectComplexity.ENTERPRISE: 21
        }
        duration = duration_map.get(complexity, 7)

        # Role-specific phases
        base_phases = ["Environment Setup", "Codebase Tour", "Development Workflow"]
        if analysis.get("has_ci_cd"):
            base_phases.append("CI/CD Pipeline Understanding")
        if analysis.get("has_database"):
            base_phases.append("Database Schema & Migrations")
        if analysis.get("external_integrations"):
            base_phases.append("Integration Points")
        base_phases.extend(["Testing & Quality", "First Contribution"])

        # Build role-specific checklist
        checklist = [
            "Complete development environment setup",
            "Clone repository and verify builds",
            "Run test suite successfully",
            "Review project README and architecture docs",
        ]

        if analysis.get("has_ci_cd"):
            checklist.extend([
                "Understand CI/CD pipeline structure",
                "Configure local pre-commit hooks if applicable",
            ])

        if analysis.get("has_database"):
            checklist.extend([
                "Set up local database",
                "Apply initial migrations",
                "Review data model documentation",
            ])

        if role.lower() in ["frontend", "ui"]:
            checklist.extend([
                "Review UI component library",
                "Set up development server",
                "Test UI locally",
            ])
        elif role.lower() in ["backend", "api"]:
            checklist.extend([
                "Review API documentation",
                "Test API endpoints locally",
                "Understand authentication patterns",
            ])

        checklist.extend([
            "Pair program with team member on first task",
            "Submit first contribution (documentation or minor fix)",
            "Shadow on-call rotation",
        ])

        # Critical docs based on project
        critical_docs = ["README.md", "CONTRIBUTING.md"]
        if analysis.get("has_database"):
            critical_docs.append("Database schema documentation")
        if analysis.get("has_ci_cd"):
            critical_docs.append("CI/CD pipeline documentation")
        if analysis.get("frameworks"):
            critical_docs.extend([f"{f} setup guide" for f in analysis["frameworks"]])

        return OnboardingPlan(
            role=role,
            duration_days=duration,
            complexity_level=complexity,
            phases=base_phases,
            checklist=checklist,
            key_contacts=["Tech Lead", "Mentor", "Engineering Manager"],
            critical_docs=critical_docs
        )

    def generate_offboarding_plan(self, role: str, repo_path: str) -> List[str]:
        """REAL GENERATION: Create customized offboarding from project analysis."""

        if not self.project_analysis:
            self.analyze_project_complexity(repo_path)

        analysis = self.project_analysis

        offboarding_checklist = [
            "Document ongoing work and tasks",
            "Transfer code ownership and documentation",
            "Hand off on-call responsibilities",
            "Remove access from development tools",
            "Archive email and communication channels",
        ]

        if analysis.get("has_database"):
            offboarding_checklist.insert(2, "Document database maintenance procedures")

        if analysis.get("external_integrations"):
            offboarding_checklist.insert(2, "Document external API integration status")

        if role.lower() in ["lead", "architect"]:
            offboarding_checklist.insert(0, "Transfer architectural decisions documentation")
            offboarding_checklist.insert(1, "Brief replacement on team structure and processes")

        return offboarding_checklist

    def format_onboarding_markdown(self, plan: OnboardingPlan) -> str:
        """Format onboarding plan as markdown."""
        md = f"""# Onboarding Plan: {plan.role}

**Complexity Level:** {plan.complexity_level.value.upper()}
**Estimated Duration:** {plan.duration_days} days

## Phases

"""
        for i, phase in enumerate(plan.phases, 1):
            md += f"{i}. {phase}\n"

        md += "\n## Checklist\n\n"
        for item in plan.checklist:
            md += f"- [ ] {item}\n"

        md += "\n## Key Contacts\n\n"
        for contact in plan.key_contacts:
            md += f"- {contact}\n"

        md += "\n## Critical Documentation\n\n"
        for doc in plan.critical_docs:
            md += f"- {doc}\n"

        return md

    def get_readiness_assessment(self, repo_path: str) -> str:
        """Get human-readable project readiness assessment."""
        analysis = self.analyze_project_complexity(repo_path)

        assessment = f"""
TEAM READINESS ASSESSMENT
{'='*60}

PROJECT METRICS:
- Total Files: {analysis['file_count']}
- Python Files: {analysis['py_files']}
- Test Files: {analysis['test_files']}
- Documentation Files: {analysis['doc_files']}

INFRASTRUCTURE:
- CI/CD Configured: {'Yes' if analysis['has_ci_cd'] else 'No'}
- Database Required: {'Yes' if analysis['has_database'] else 'No'}
- External Integrations: {len(analysis.get('external_integrations', []))}

FRAMEWORKS DETECTED:
{chr(10).join(f"  • {f}" for f in analysis.get('frameworks', [])) or "  None detected"}

COMPLEXITY ASSESSMENT:
- Level: {analysis['complexity_level'].value.upper()}
- Recommended Team Size: {analysis['team_size_suggestion']} people
- Onboarding Duration: {[v for k, v in {'simple': 3, 'moderate': 7, 'complex': 14, 'enterprise': 21}.items() if k == analysis['complexity_level'].value][0]} days

ONBOARDING REQUIREMENTS:
- Setup time required
- CI/CD pipeline understanding {'✓' if analysis['has_ci_cd'] else ''}
- Database knowledge {'✓' if analysis['has_database'] else ''}
- Framework-specific training {'✓' if analysis.get('frameworks') else ''}
"""
        return assessment
