"""
Feature 8: Team Handoff Checklists
Generates context requirements when developers join or leave.
"""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime


@dataclass
class HandoffCheckpoint:
    """A milestone in the onboarding/offboarding process."""
    day: int
    title: str
    tasks: List[str]


@dataclass
class TeamMemberRole:
    """A role within the team."""
    role_name: str
    responsibilities: List[str]
    key_files: List[str]
    learning_resources: List[str]


class HandoffManager:
    """Manages team member onboarding and offboarding."""

    ONBOARDING_CHECKLIST = [
        HandoffCheckpoint(
            day=1,
            title="Day 1: Environment Setup",
            tasks=[
                "Clone repository",
                "Set up development environment",
                "Run tests locally",
                "Review AGENTS.md",
                "Complete setup validation"
            ]
        ),
        HandoffCheckpoint(
            day=3,
            title="Day 3: Architecture Understanding",
            tasks=[
                "Review AGENTS.md Architecture section",
                "Trace 2-3 feature flows",
                "Identify key entry points",
                "Document questions",
                "Meet with domain expert"
            ]
        ),
        HandoffCheckpoint(
            day=5,
            title="Day 5: First Contribution",
            tasks=[
                "Find a good-first-issue",
                "Implement fix/feature",
                "Write tests",
                "Submit PR",
                "Get code review"
            ]
        ),
        HandoffCheckpoint(
            day=14,
            title="Day 14: Ramp Complete",
            tasks=[
                "Complete 3+ PRs",
                "Become familiar with CI/CD",
                "Understand deployment process",
                "Document gotchas discovered",
                "Ready for independent work"
            ]
        )
    ]

    OFFBOARDING_CHECKLIST = [
        HandoffCheckpoint(
            day=0,
            title="Immediate: Knowledge Transfer",
            tasks=[
                "Document current work-in-progress",
                "Update AGENTS.md with recent changes",
                "Create handoff document",
                "Record architecture decisions",
                "List domain-specific gotchas"
            ]
        ),
        HandoffCheckpoint(
            day=3,
            title="Week 1: Code Knowledge Transfer",
            tasks=[
                "Pair with replacement on key areas",
                "Explain recent architectural changes",
                "Share troubleshooting tips",
                "Document custom workflows",
                "Transfer IDE setup configs"
            ]
        ),
        HandoffCheckpoint(
            day=7,
            title="Week 2: Complete Handoff",
            tasks=[
                "Ensure all PRs are merged/closed",
                "Clean up WIP branches",
                "Final Q&A session",
                "Verify replacement can run tests",
                "Archive personal documentation"
            ]
        )
    ]

    ROLE_TEMPLATES = {
        "backend": TeamMemberRole(
            role_name="Backend Developer",
            responsibilities=[
                "API implementation",
                "Database schema",
                "Performance optimization",
                "Server deployment"
            ],
            key_files=[
                "braxis.py",
                "braxis_api.py",
                "tests/test_braxis_api.py"
            ],
            learning_resources=[
                "AGENTS.md - Architecture",
                "API_GUIDE.md",
                "Recent PRs in core/",
                "Database setup guide"
            ]
        ),
        "frontend": TeamMemberRole(
            role_name="Frontend Developer",
            responsibilities=[
                "UI implementation",
                "Component development",
                "User experience",
                "Browser testing"
            ],
            key_files=[
                "src/components/",
                "src/pages/",
                "tests/component_tests/"
            ],
            learning_resources=[
                "AGENTS.md - Components",
                "Design system guide",
                "Recent component PRs"
            ]
        ),
        "devops": TeamMemberRole(
            role_name="DevOps Engineer",
            responsibilities=[
                "CI/CD pipeline",
                "Infrastructure",
                "Deployment",
                "Monitoring"
            ],
            key_files=[
                ".github/workflows/",
                "scripts/deploy.sh",
                "terraform/"
            ],
            learning_resources=[
                "Deployment guide",
                "CI/CD documentation",
                "Infrastructure as Code examples"
            ]
        )
    }

    def __init__(self, repo_name: str):
        self.repo_name = repo_name
        self.team_members: Dict[str, Dict] = {}

    def generate_onboarding_plan(self, developer_name: str,
                                role: str = "backend") -> Dict:
        """Generate onboarding plan for new developer."""
        role_template = self.ROLE_TEMPLATES.get(role)

        return {
            "developer": developer_name,
            "role": role,
            "start_date": datetime.now().isoformat(),
            "responsibilities": role_template.responsibilities if role_template else [],
            "key_files": role_template.key_files if role_template else [],
            "resources": role_template.learning_resources if role_template else [],
            "milestones": self.ONBOARDING_CHECKLIST,
            "expected_productivity": "Day 5-7 for first independent contribution"
        }

    def generate_offboarding_plan(self, developer_name: str) -> Dict:
        """Generate offboarding plan."""
        return {
            "developer": developer_name,
            "last_day": datetime.now().isoformat(),
            "milestones": self.OFFBOARDING_CHECKLIST,
            "knowledge_transfer_priority": [
                "Active PRs and issues",
                "Architecture decisions",
                "Gotchas and workarounds",
                "Custom scripts/configs"
            ]
        }

    def get_onboarding_milestone(self, day: int) -> HandoffCheckpoint:
        """Get milestone for specific day."""
        for checkpoint in self.ONBOARDING_CHECKLIST:
            if checkpoint.day == day:
                return checkpoint
        return None

    def generate_role_guide(self, role: str) -> str:
        """Generate markdown guide for a role."""
        role_template = self.ROLE_TEMPLATES.get(role)
        if not role_template:
            return f"No template found for role: {role}"

        guide = f"# {role_template.role_name} Guide for {self.repo_name}\n\n"

        guide += "## Responsibilities\n"
        for resp in role_template.responsibilities:
            guide += f"- {resp}\n"
        guide += "\n"

        guide += "## Key Files\n"
        for file in role_template.key_files:
            guide += f"- {file}\n"
        guide += "\n"

        guide += "## Learning Resources\n"
        for resource in role_template.learning_resources:
            guide += f"- {resource}\n"
        guide += "\n"

        guide += "## Onboarding Timeline\n"
        for checkpoint in self.ONBOARDING_CHECKLIST:
            guide += f"### Day {checkpoint.day}: {checkpoint.title}\n"
            for task in checkpoint.tasks:
                guide += f"- {task}\n"
            guide += "\n"

        return guide
