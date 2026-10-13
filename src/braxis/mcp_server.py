"""Braxis MCP Server - Context Protocol integration for Claude.

Exposes Braxis extractors as MCP tools that Claude can use directly.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from src.braxis.extractors.product_authority import ProductAuthorityExtractor
from src.braxis.extractors.architectural_constraints import ArchitecturalConstraintsExtractor
from src.braxis.extractors.code_generation import CodeGenerationExtractor
from src.braxis.extractors.multi_variant import MultiVariantExtractor
from src.braxis.extractors.agent_policy import AgentPolicyExtractor
from src.braxis.extractors.monorepo_subsystem import MonorepoSubsystemExtractor


class BraxisServer:
    """MCP Server wrapping all 6 Braxis extractors.

    Provides Claude with tools to analyze repositories and extract patterns.
    """

    def __init__(self):
        """Initialize all extractors."""
        self.extractors = {
            "product_authority": ProductAuthorityExtractor(),
            "architectural_constraints": ArchitecturalConstraintsExtractor(),
            "code_generation": CodeGenerationExtractor(),
            "multi_variant": MultiVariantExtractor(),
            "agent_policy": AgentPolicyExtractor(),
            "monorepo_subsystem": MonorepoSubsystemExtractor(),
        }

    def get_tools(self) -> list[Dict[str, Any]]:
        """Get tool definitions for MCP."""
        return [
            {
                "name": "analyze_repository",
                "description": "Analyze a repository and extract AI context patterns",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "repo_path": {
                            "type": "string",
                            "description": "Path to the repository to analyze",
                        }
                    },
                    "required": ["repo_path"],
                },
            },
            {
                "name": "extract_patterns",
                "description": "Extract specific patterns from a repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "repo_path": {
                            "type": "string",
                            "description": "Path to the repository",
                        },
                        "pattern_type": {
                            "type": "string",
                            "enum": [
                                "product_authority",
                                "architectural_constraints",
                                "code_generation",
                                "multi_variant",
                                "agent_policy",
                                "monorepo_subsystem",
                            ],
                            "description": "Type of pattern to extract",
                        },
                    },
                    "required": ["repo_path", "pattern_type"],
                },
            },
            {
                "name": "generate_agents_md",
                "description": "Generate AGENTS.md context file for a repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "repo_path": {
                            "type": "string",
                            "description": "Path to the repository",
                        }
                    },
                    "required": ["repo_path"],
                },
            },
            {
                "name": "get_readiness_score",
                "description": "Get AI readiness score for a repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "repo_path": {
                            "type": "string",
                            "description": "Path to the repository",
                        }
                    },
                    "required": ["repo_path"],
                },
            },
        ]

    def process_tool_call(
        self, tool_name: str, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a tool call from Claude."""
        try:
            if tool_name == "analyze_repository":
                return self.analyze_repository(tool_input["repo_path"])
            elif tool_name == "extract_patterns":
                return self.extract_patterns(
                    tool_input["repo_path"], tool_input["pattern_type"]
                )
            elif tool_name == "generate_agents_md":
                return self.generate_agents_md(tool_input["repo_path"])
            elif tool_name == "get_readiness_score":
                return self.get_readiness_score(tool_input["repo_path"])
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Analyze a repository and return all extracted patterns."""
        repo_path = Path(repo_path)

        if not repo_path.exists():
            return {"error": f"Repository path does not exist: {repo_path}"}

        # Read documentation
        content = self._read_repo_docs(repo_path)
        if not content:
            return {"error": "No documentation found in repository"}

        # Extract all patterns
        results = {}
        for name, extractor in self.extractors.items():
            try:
                results[name] = extractor.extract(content)
            except Exception as e:
                results[name] = {"error": str(e)}

        return {
            "repo_path": str(repo_path),
            "patterns": results,
            "summary": self._generate_summary(results),
        }

    def extract_patterns(self, repo_path: str, pattern_type: str) -> Dict[str, Any]:
        """Extract specific pattern type from repository."""
        repo_path = Path(repo_path)

        if not repo_path.exists():
            return {"error": f"Repository path does not exist: {repo_path}"}

        if pattern_type not in self.extractors:
            return {"error": f"Unknown pattern type: {pattern_type}"}

        content = self._read_repo_docs(repo_path)
        if not content:
            return {"error": "No documentation found in repository"}

        extractor = self.extractors[pattern_type]
        result = extractor.extract(content)

        return {
            "pattern_type": pattern_type,
            "repo_path": str(repo_path),
            "extraction": result,
        }

    def generate_agents_md(self, repo_path: str) -> Dict[str, Any]:
        """Generate AGENTS.md context file."""
        repo_path = Path(repo_path)

        if not repo_path.exists():
            return {"error": f"Repository path does not exist: {repo_path}"}

        content = self._read_repo_docs(repo_path)
        if not content:
            return {"error": "No documentation found in repository"}

        # Extract all patterns
        patterns = {}
        for name, extractor in self.extractors.items():
            patterns[name] = extractor.extract(content)

        # Generate markdown
        md = self._generate_agents_md_content(repo_path.name, patterns)

        return {
            "repo_path": str(repo_path),
            "agents_md": md,
            "file_location": str(repo_path / "AGENTS.md"),
        }

    def get_readiness_score(self, repo_path: str) -> Dict[str, Any]:
        """Get AI readiness score for repository."""
        repo_path = Path(repo_path)

        if not repo_path.exists():
            return {"error": f"Repository path does not exist: {repo_path}"}

        content = self._read_repo_docs(repo_path)
        if not content:
            return {"error": "No documentation found in repository"}

        # Extract all patterns and calculate score
        score = 0
        findings = {}

        for name, extractor in self.extractors.items():
            result = extractor.extract(content)
            findings[name] = result.get("found", False)
            if result.get("found"):
                score += 10  # +10 per feature detected

        return {
            "repo_path": str(repo_path),
            "score": min(score, 100),
            "max_possible": 60,  # 6 features * 10 points
            "findings": findings,
            "ready_for_ai": score >= 40,
        }

    @staticmethod
    def _read_repo_docs(repo_path: Path) -> str:
        """Read documentation from repository."""
        docs = []

        # Priority order for doc files
        doc_patterns = [
            "README.md",
            "CONTRIBUTING.md",
            "ARCHITECTURE.md",
            "docs/README.md",
            "docs/ARCHITECTURE.md",
        ]

        for pattern in doc_patterns:
            doc_file = repo_path / pattern
            if doc_file.exists():
                try:
                    docs.append(doc_file.read_text())
                except:
                    pass

        return "\n".join(docs)

    @staticmethod
    def _generate_summary(results: Dict[str, Any]) -> str:
        """Generate summary of extraction results."""
        found_count = sum(1 for r in results.values() if r.get("found", False))
        return f"Extracted patterns from {found_count}/6 feature categories"

    @staticmethod
    def _generate_agents_md_content(repo_name: str, patterns: Dict[str, Any]) -> str:
        """Generate AGENTS.md content from extracted patterns."""
        lines = [
            f"# {repo_name} - AI Agent Context",
            "",
            "Generated by Braxis MCP Server",
            "",
            "## Extracted Patterns",
            "",
        ]

        # Product Authority
        if patterns.get("product_authority", {}).get("found"):
            lines.append("### 📋 Product Authority")
            lines.append(
                "This project has defined product guarantees and state contracts."
            )
            lines.append("")

        # Architectural Constraints
        if patterns.get("architectural_constraints", {}).get("found"):
            lines.append("### ⚙️ Architectural Constraints")
            constraints = patterns.get("architectural_constraints", {})
            if constraints.get("critical_count", 0) > 0:
                lines.append(f"⚠️ **{constraints['critical_count']} critical constraints**")
            lines.append("")

        # Code Generation
        if patterns.get("code_generation", {}).get("found"):
            lines.append("### 🔧 Code Generation")
            codegen = patterns.get("code_generation", {})
            providers = codegen.get("providers", [])
            if providers:
                lines.append(f"Providers: {', '.join(providers)}")
            lines.append("")

        # Multi-Variant
        if patterns.get("multi_variant", {}).get("found"):
            lines.append("### 👥 Multi-Variant Patterns")
            multi = patterns.get("multi_variant", {})
            twins = len(multi.get("twins", []))
            platforms = len(multi.get("platforms", []))
            if twins > 0 or platforms > 0:
                lines.append(
                    f"Sync/async twins: {twins}, Platform clients: {platforms}"
                )
            lines.append("")

        # Agent Policy
        if patterns.get("agent_policy", {}).get("found"):
            lines.append("### 🤖 Agent Policy")
            agent = patterns.get("agent_policy", {})
            sentiment = agent.get("sentiment", "unknown").replace("_", " ")
            lines.append(f"Sentiment: {sentiment.title()}")
            if agent.get("restrictions"):
                lines.append("Restrictions:")
                for restriction in agent["restrictions"][:3]:
                    lines.append(f"• {restriction}")
            lines.append("")

        # Monorepo
        if patterns.get("monorepo_subsystem", {}).get("is_monorepo"):
            lines.append("### 📦 Monorepo Structure")
            mono = patterns.get("monorepo_subsystem", {})
            mtype = mono.get("structure", {}).get("type", "unknown")
            lines.append(f"Type: {mtype.title()}")
            subsystems = len(mono.get("subsystems", []))
            if subsystems > 0:
                lines.append(f"Subsystems: {subsystems}")
            lines.append("")

        lines.append("---")
        lines.append("_Generated by [Braxis MCP Server](https://github.com/jaykrishna316/braxis)_")

        return "\n".join(lines)


def main():
    """Entry point for MCP server."""
    server = BraxisServer()

    # Print tools in MCP format for registration
    tools = server.get_tools()
    print(json.dumps({"tools": tools}, indent=2))


if __name__ == "__main__":
    main()
