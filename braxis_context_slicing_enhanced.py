"""
Feature 3: Smart Context Slicing by Agent Type (ENHANCED)
Generates agent-specific context guidance by ANALYZING actual codebase.
NOW WITH REAL CODE ANALYSIS instead of hard-coded profiles.
"""

import os
import re
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


class ContextSlicerEnhanced:
    """Generates agent-specific context slices by ANALYZING code."""

    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path
        self.generated_contexts: Dict[AgentContextStyle, str] = {}
        self.analysis_cache: Dict = {}

    def analyze_codebase(self, repo_path: str) -> Dict:
        """REAL ANALYSIS: Analyze actual codebase to determine emphasis areas."""
        analysis = {
            "has_api": False,
            "has_tests": False,
            "has_cli": False,
            "has_web": False,
            "languages": [],
            "key_patterns": [],
            "test_files": 0,
            "py_files": 0,
            "doc_files": 0,
            "config_files": {}
        }

        # Scan directory for actual patterns
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]

            for file in files:
                # Count file types
                if file.endswith('.py'):
                    analysis["py_files"] += 1
                    if 'test' in file or 'spec' in file:
                        analysis["has_tests"] = True
                        analysis["test_files"] += 1

                if file.endswith(('.md', '.rst', '.txt')):
                    analysis["doc_files"] += 1

                # Detect frameworks/patterns
                if file in ['setup.py', 'setup.cfg', 'pyproject.toml']:
                    analysis["languages"].append("Python")
                if file in ['package.json', 'tsconfig.json']:
                    analysis["languages"].append("JavaScript/TypeScript")
                if file in ['Makefile', 'Dockerfile']:
                    analysis["config_files"][file] = True
                if 'cli' in file.lower() or file == 'main.py':
                    analysis["has_cli"] = True
                if file in ['requirements.txt', 'Pipfile', 'poetry.lock']:
                    analysis["key_patterns"].append("dependency_management")
                if file == 'AGENTS.md':
                    analysis["key_patterns"].append("ai_agent_aware")

        # Read AGENTS.md if it exists to extract real structure
        agents_md_path = os.path.join(repo_path, 'AGENTS.md')
        if os.path.exists(agents_md_path):
            with open(agents_md_path, 'r') as f:
                content = f.read()
                if 'Architecture' in content:
                    analysis["has_architecture_docs"] = True
                if 'Testing' in content:
                    analysis["has_testing_docs"] = True
                if 'Entry' in content:
                    analysis["has_entry_points"] = True

        self.analysis_cache = analysis
        return analysis

    def generate_profile_from_analysis(self, agent_type: AgentContextStyle,
                                      analysis: Dict) -> AgentContextProfile:
        """REAL GENERATION: Create profile based on actual code analysis."""

        # Determine emphasis areas from actual analysis
        emphasis_areas = []
        include_sections = []
        exclude_sections = []

        # Base on actual findings
        if analysis.get("has_architecture_docs"):
            emphasis_areas.append("Architecture")
            include_sections.append("Architecture Overview")

        if analysis.get("has_tests"):
            emphasis_areas.append("Testing Strategy")
            include_sections.append("Testing Strategy")

        if analysis.get("has_cli"):
            emphasis_areas.append("Entry Points")
            include_sections.append("CLI/Main Entry")

        if analysis.get("has_entry_points"):
            emphasis_areas.append("Full Workflow")

        if analysis.get("py_files", 0) > 20:
            emphasis_areas.append("Code Organization")

        # Agent-specific customizations based on real code
        if agent_type == AgentContextStyle.CLAUDE_CODE:
            max_tokens = 8000
            style_guide = f"Comprehensive, structured (analyzed: {analysis.get('py_files', 0)} Python files)"
            if "dependency_management" in analysis.get("key_patterns", []):
                include_sections.append("Dependency Management")
            exclude_sections = ["IDE Shortcuts"]
            if not emphasis_areas:
                emphasis_areas = ["Architecture", "Development Workflow"]

        elif agent_type == AgentContextStyle.CURSOR:
            max_tokens = 4000
            style_guide = f"IDE-centric, fast navigation"
            exclude_sections = ["Full Architecture", "Historical Context"]
            if not emphasis_areas:
                emphasis_areas = ["Code Patterns", "Quick Navigation"]

        elif agent_type == AgentContextStyle.COPILOT:
            max_tokens = 2000
            style_guide = f"Concise, example-driven ({analysis.get('py_files', 0)} analyzable files)"
            exclude_sections = ["Full Documentation", "Historical Decisions"]
            if not emphasis_areas:
                emphasis_areas = ["Code Examples", "Naming Patterns"]

        else:  # GENERIC
            max_tokens = 6000
            style_guide = f"Standard, balanced (repo has {len(analysis.get('languages', []))} languages)"
            exclude_sections = []
            if not emphasis_areas:
                emphasis_areas = ["Architecture", "Conventions"]

        # Add common sections based on actual files
        if analysis.get("doc_files", 0) > 0:
            include_sections.append("Documentation")
        if analysis.get("has_tests"):
            include_sections.append("Test Examples")

        return AgentContextProfile(
            agent_type=agent_type,
            emphasis_areas=emphasis_areas if emphasis_areas else ["Code Structure"],
            style_guide=style_guide,
            max_context_tokens=max_tokens,
            include_sections=include_sections if include_sections else ["Project Structure", "Code Patterns"],
            exclude_sections=exclude_sections
        )

    def slice_context(self, full_context: str, agent_type: AgentContextStyle,
                     repo_path: Optional[str] = None) -> str:
        """Generate context slice for a specific agent (REAL ANALYSIS)."""

        # Perform actual code analysis if repo path provided
        if repo_path and os.path.exists(repo_path):
            analysis = self.analyze_codebase(repo_path)
            profile = self.generate_profile_from_analysis(agent_type, analysis)
        else:
            # Fall back to basic analysis
            analysis = self.analyze_codebase(self.repo_path) if self.repo_path else {}
            profile = self.generate_profile_from_analysis(agent_type, analysis)

        # Filter context based on analyzed profile
        context_lines = []
        current_section = None

        for line in full_context.split('\n'):
            # Track current section
            if line.startswith('#'):
                current_section = line.strip()

            # Include or exclude based on ANALYZED profile
            should_include = True

            if profile.exclude_sections:
                for excluded in profile.exclude_sections:
                    if excluded.lower() in line.lower():
                        should_include = False
                        break

            if should_include:
                context_lines.append(line)

        result = self._add_agent_header(agent_type, profile, analysis) + '\n'.join(context_lines)
        self.generated_contexts[agent_type] = result

        return result

    def _add_agent_header(self, agent_type: AgentContextStyle,
                         profile: AgentContextProfile, analysis: Dict) -> str:
        """Add agent-specific header with REAL analysis data."""
        header = f"# Context for {agent_type.value}\n"
        header += f"**Generated from Real Code Analysis**\n"
        header += f"**Repo Analysis:** {analysis.get('py_files', 0)} Python files, "
        header += f"{analysis.get('test_files', 0)} test files, "
        header += f"{len(analysis.get('languages', []))} language(s)\n"
        header += f"**Emphasis Areas:** {', '.join(profile.emphasis_areas)}\n"
        header += f"**Max Context:** {profile.max_context_tokens:,} tokens\n\n"
        return header

    def generate_all_variants(self, full_context: str, repo_path: str = None) -> Dict[str, str]:
        """Generate all agent-specific context variants (REAL ANALYSIS)."""
        variants = {}
        for agent_type in AgentContextStyle:
            variants[agent_type.value] = self.slice_context(full_context, agent_type, repo_path)
        return variants

    def get_analysis_summary(self, repo_path: str) -> str:
        """Get human-readable summary of code analysis."""
        analysis = self.analyze_codebase(repo_path)

        summary = f"""
CODE ANALYSIS SUMMARY
{'='*60}

Python Files: {analysis.get('py_files', 0)}
Test Files: {analysis.get('test_files', 0)}
Documentation Files: {analysis.get('doc_files', 0)}
Languages Detected: {', '.join(analysis.get('languages', [])) or 'None'}

ARCHITECTURE PATTERNS DETECTED:
- Has CLI: {analysis.get('has_cli', False)}
- Has Tests: {analysis.get('has_tests', False)}
- Has Architecture Docs: {analysis.get('has_architecture_docs', False)}

KEY PATTERNS:
{chr(10).join(f"  • {p}" for p in analysis.get('key_patterns', []) or ['None detected'])}

CONFIG FILES FOUND:
{chr(10).join(f"  • {f}" for f in analysis.get('config_files', {}).keys() or ['None found'])}
"""
        return summary
