"""
Feature 3: Smart Context Slicing by Agent Type
Generates agent-specific context guidance (Claude Code, Cursor, Copilot).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class AgentContextStyle(Enum):
    """Context style preferences for different agents."""
    CLAUDE_CODE = "claude-code"
    CURSOR = "cursor"
    COPILOT = "copilot"
    GENERIC = "generic"


@dataclass
class AgentContextProfile:
    """Context generation profile for a specific agent type."""
    agent_type: AgentContextStyle
    emphasis_areas: List[str]
    style_guide: str
    max_context_tokens: int
    include_sections: List[str]
    exclude_sections: List[str]


class ContextSlicer:
    """Generates agent-specific context slices."""

    PROFILES = {
        AgentContextStyle.CLAUDE_CODE: AgentContextProfile(
            agent_type=AgentContextStyle.CLAUDE_CODE,
            emphasis_areas=[
                "Architecture", "Entry Points", "Full Workflow",
                "Development Commands", "Testing Strategy"
            ],
            style_guide="Comprehensive, structured, with clear sections",
            max_context_tokens=8000,
            include_sections=[
                "Architecture Overview", "Project Structure",
                "Development Workflow", "Testing Strategy",
                "Code Style & Conventions", "Common Patterns"
            ],
            exclude_sections=["IDE Shortcuts"]
        ),
        AgentContextStyle.CURSOR: AgentContextProfile(
            agent_type=AgentContextStyle.CURSOR,
            emphasis_areas=[
                "IDE Shortcuts", "Local File Patterns",
                "Quick Refactoring", "Code Navigation"
            ],
            style_guide="IDE-centric, fast navigation, local patterns",
            max_context_tokens=4000,
            include_sections=[
                "Project Structure", "Code Conventions",
                "Common Patterns", "Quick Start"
            ],
            exclude_sections=["Full Architecture", "Historical Context"]
        ),
        AgentContextStyle.COPILOT: AgentContextProfile(
            agent_type=AgentContextStyle.COPILOT,
            emphasis_areas=[
                "Naming Conventions", "Inline Examples",
                "Anti-patterns", "Quick Reference"
            ],
            style_guide="Concise, example-driven, naming-focused",
            max_context_tokens=2000,
            include_sections=[
                "Naming Conventions", "Common Patterns",
                "Code Examples", "Anti-patterns"
            ],
            exclude_sections=["Full Documentation", "Historical Decisions"]
        ),
        AgentContextStyle.GENERIC: AgentContextProfile(
            agent_type=AgentContextStyle.GENERIC,
            emphasis_areas=[
                "Architecture", "Conventions", "Examples"
            ],
            style_guide="Standard, balanced, comprehensive",
            max_context_tokens=6000,
            include_sections=[
                "Architecture Overview", "Project Structure",
                "Code Style", "Common Patterns", "Examples"
            ],
            exclude_sections=[]
        )
    }

    def __init__(self):
        self.generated_contexts: Dict[AgentContextStyle, str] = {}

    def get_profile(self, agent_type: AgentContextStyle) -> AgentContextProfile:
        """Get context profile for an agent type."""
        return self.PROFILES.get(agent_type, self.PROFILES[AgentContextStyle.GENERIC])

    def slice_context(self, full_context: str, agent_type: AgentContextStyle,
                     emphasis_areas: Optional[List[str]] = None) -> str:
        """Generate context slice for a specific agent."""
        profile = self.get_profile(agent_type)

        if emphasis_areas is None:
            emphasis_areas = profile.emphasis_areas

        # Filter sections based on profile
        context_lines = []
        current_section = None

        for line in full_context.split('\n'):
            # Track current section
            if line.startswith('#'):
                current_section = line.strip()

            # Include or exclude based on profile
            should_include = True

            if profile.exclude_sections:
                for excluded in profile.exclude_sections:
                    if excluded.lower() in line.lower():
                        should_include = False
                        break

            if should_include:
                context_lines.append(line)

        result = '\n'.join(context_lines)

        # Add agent-specific header
        result = self._add_agent_header(agent_type, profile) + result

        self.generated_contexts[agent_type] = result
        return result

    def _add_agent_header(self, agent_type: AgentContextStyle,
                         profile: AgentContextProfile) -> str:
        """Add agent-specific header to context."""
        headers = {
            AgentContextStyle.CLAUDE_CODE:
                "# Context for Claude Code\n"
                "This context is optimized for Claude Code with emphasis on "
                "architecture, workflows, and development commands.\n\n",
            AgentContextStyle.CURSOR:
                "# Context for Cursor IDE\n"
                "This context is optimized for Cursor with emphasis on "
                "local patterns and IDE shortcuts.\n\n",
            AgentContextStyle.COPILOT:
                "# Context for GitHub Copilot\n"
                "This context is optimized for inline suggestions with emphasis on "
                "naming conventions and examples.\n\n",
            AgentContextStyle.GENERIC:
                "# Context Guide\n"
                "Standard context with balanced coverage.\n\n"
        }
        return headers.get(agent_type, "")

    def generate_all_variants(self, full_context: str) -> Dict[str, str]:
        """Generate all agent-specific context variants."""
        variants = {}
        for agent_type in AgentContextStyle:
            variants[agent_type.value] = self.slice_context(full_context, agent_type)
        return variants

    def get_emphasis_summary(self, agent_type: AgentContextStyle) -> str:
        """Get summary of what this agent emphasizes."""
        profile = self.get_profile(agent_type)
        return f"{agent_type.value}: {', '.join(profile.emphasis_areas)}"
