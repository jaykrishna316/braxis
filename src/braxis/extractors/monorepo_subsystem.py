"""Feature 6: Monorepo Subsystem Guidance

Generates per-package AGENTS.md guidance instead of single project-level,
with package-specific Python versions, commands, and constraints.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional


class MonorepoSubsystemExtractor:
    """Extract and organize monorepo subsystem guidance."""

    def __init__(self):
        """Initialize extractor."""
        self.subsystems = []

    def extract(self, content: str, project_path: Optional[str] = None) -> Dict[str, any]:
        """Extract monorepo subsystem information."""
        if not content:
            return {
                "found": False,
                "subsystems": [],
                "is_monorepo": False,
                "structure": {},
                "package_map": {},
            }

        return {
            "found": True,
            "subsystems": self._detect_subsystems(content),
            "is_monorepo": self._is_monorepo_structure(content),
            "structure": self._extract_structure(content),
            "package_map": self._build_package_map(content),
            "guidance": self._extract_per_package_guidance(content),
        }

    def _detect_subsystems(self, content: str) -> List[Dict[str, str]]:
        """Detect separate subsystems in monorepo."""
        subsystems = []

        # Look for package markers
        patterns = [
            (r"packages?[/\\]([\w_\-]+)", "directory"),
            (r"([\w_\-]+)[/\\]pyproject\.toml", "python_package"),
            (r"([\w_\-]+)[/\\]package\.json", "npm_package"),
            (r"^[\s-]*([\w_\-]+)[/\\]?$", "package"),
        ]

        found = set()
        for pattern, subsystem_type in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                subsystem_name = match.group(1)
                # Filter out common non-package words
                if subsystem_name not in found and subsystem_name.lower() not in [
                    "packages", "docs", "tests", "src", "lib", "dist", "build"
                ]:
                    found.add(subsystem_name)
                    subsystems.append({
                        "name": subsystem_name,
                        "type": subsystem_type,
                        "path": f"{subsystem_name}/",
                    })

        return subsystems

    def _is_monorepo_structure(self, content: str) -> bool:
        """Determine if this is a monorepo."""
        monorepo_indicators = [
            r"monorepo",
            r"workspace",
            r"lerna",
            r"turborepo",
            r"nx\s+monorepo",
            r"multiple\s+packages",
            r"packages/.*pyproject\.toml",
        ]

        indicators_found = sum(
            1 for indicator in monorepo_indicators if re.search(indicator, content, re.IGNORECASE)
        )

        return indicators_found > 0

    def _extract_structure(self, content: str) -> Dict[str, any]:
        """Extract monorepo structure information."""
        structure = {
            "type": "unknown",
            "layers": [],
            "tools": [],
        }

        # Detect type
        if "turborepo" in content.lower():
            structure["type"] = "turborepo"
        elif "lerna" in content.lower():
            structure["type"] = "lerna"
        elif "nx" in content.lower():
            structure["type"] = "nx"
        elif "workspace" in content.lower():
            structure["type"] = "workspace"

        # Detect layers
        if "core" in content.lower():
            structure["layers"].append("core")
        if "implementation" in content.lower():
            structure["layers"].append("implementation")
        if "integration" in content.lower():
            structure["layers"].append("integration")

        # Detect tools
        tools = ["uv", "pnpm", "yarn", "npm", "poetry", "cargo"]
        for tool in tools:
            if tool in content.lower():
                structure["tools"].append(tool)

        return structure

    def _build_package_map(self, content: str) -> Dict[str, Dict[str, str]]:
        """Build map of packages to their requirements."""
        packages = {}

        # Look for Python version requirements per package
        python_version_pattern = r"python\s*[><=]+\s*([0-9.]+)"
        requires_python_pattern = r"requires-python\s*=\s*[\"']([^\"']+)[\"']"

        for match in re.finditer(python_version_pattern, content):
            version = match.group(1)
            # Try to associate with package
            start = max(0, match.start() - 500)
            context = content[start : match.start()]
            package_match = re.search(r"(\w+)/pyproject\.toml", context)
            if package_match:
                pkg_name = package_match.group(1)
                if pkg_name not in packages:
                    packages[pkg_name] = {}
                packages[pkg_name]["python_version"] = version

        for match in re.finditer(requires_python_pattern, content):
            version = match.group(1)
            start = max(0, match.start() - 500)
            context = content[start : match.start()]
            package_match = re.search(r"(\w+)/pyproject\.toml", context)
            if package_match:
                pkg_name = package_match.group(1)
                if pkg_name not in packages:
                    packages[pkg_name] = {}
                packages[pkg_name]["python_version"] = version

        return packages

    def _extract_per_package_guidance(self, content: str) -> Dict[str, List[str]]:
        """Extract package-specific guidance."""
        guidance = {}

        # Look for "cd into" patterns
        cd_pattern = r"cd\s+(?:into\s+)?(?:the\s+)?(\w+)"
        for match in re.finditer(cd_pattern, content, re.IGNORECASE):
            package = match.group(1)
            if package not in guidance:
                guidance[package] = []

            # Extract surrounding context
            start = max(0, match.start() - 100)
            end = min(len(content), match.end() + 100)
            context = content[start:end]

            guidance[package].append(f"Always cd into {package} before running tests/commands")

        # Look for per-package commands
        for match in re.finditer(r"(?:^|\n)###?\s*(\w+)", content):
            package = match.group(1)
            start = match.start()
            end = min(len(content), start + 500)
            section = content[start:end]

            if "test" in section.lower() or "command" in section.lower():
                if package not in guidance:
                    guidance[package] = []

                # Extract test commands
                test_match = re.search(r"(pytest|npm\s+test|cargo\s+test|make\s+test)", section)
                if test_match:
                    guidance[package].append(f"Test command: {test_match.group(1)}")

        return guidance


def format_monorepo_section(extraction: Dict[str, any]) -> str:
    """Format monorepo guidance for AGENTS.md."""
    if not extraction["is_monorepo"]:
        return ""

    lines = ["## 📦 Monorepo Structure\n"]

    if extraction["structure"]["type"] != "unknown":
        lines.append(f"**Type:** {extraction['structure']['type'].title()} monorepo\n")

    if extraction["subsystems"]:
        lines.append("### Packages/Subsystems\n")
        for subsystem in extraction["subsystems"][:10]:
            lines.append(f"• `{subsystem['path']}` ({subsystem['type']})\n")

    if extraction["package_map"]:
        lines.append("### Per-Package Requirements\n")
        for package, requirements in extraction["package_map"].items():
            if "python_version" in requirements:
                lines.append(
                    f"• `{package}`: Python {requirements['python_version']}\n"
                )

    if extraction["guidance"]:
        lines.append("### Per-Package Guidance\n")
        for package, guidance_items in extraction["guidance"].items():
            lines.append(f"**{package}:**\n")
            for guidance in guidance_items[:2]:
                lines.append(f"• {guidance}\n")

    lines.append("\n**Important**: Always `cd` into the package directory before running commands.\n")

    return "\n".join(lines)
