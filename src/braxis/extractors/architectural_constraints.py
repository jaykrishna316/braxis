"""Feature 2: Architectural Constraints Detection

Extracts "Do not" and "Never" rules that agents commonly break:
- Generated files editing
- Breaking API changes
- Synchronization requirements
- File ownership patterns
"""

import re
from typing import Dict, List, Optional


class ArchitecturalConstraintsExtractor:
    """Extract architectural constraint patterns."""

    # Constraint patterns that indicate architectural rules
    CONSTRAINT_PATTERNS = [
        # Breaking changes / API contracts
        (r"breaking\s+change", "breaking_change"),
        (r"public\s+api", "public_api"),
        (r"stable\s+interface", "public_api"),
        (r"do\s+not\s+break", "breaking_change"),
        (r"do\s+not\s+change.*signature", "api_contract"),

        # Generated files
        (r"do\s+not\s+edit\s+generated", "generated_file"),
        (r"generated\s+file", "generated_file"),
        (r"generator.*owned", "generated_file"),
        (r"auto.generated", "generated_file"),
        (r"do\s+not\s+modify.*generated", "generated_file"),

        # Synchronization
        (r"keep.*in\s+sync", "sync_requirement"),
        (r"sync.*async.*twin", "sync_requirement"),
        (r"must\s+modify.*both", "sync_requirement"),
        (r"both.*must\s+change", "sync_requirement"),
        (r"parallel\s+implementation", "sync_requirement"),

        # File ownership
        (r"hand.written", "ownership"),
        (r"owned\s+by", "ownership"),
        (r"custom\s+code", "ownership"),
        (r"not\s+generated", "ownership"),

        # Forbidden operations
        (r"do\s+not\s+submit\s+pure\s+agent", "agent_policy"),
        (r"agent.*pr.*rejected", "agent_policy"),
        (r"never\s+save.*database", "constraint"),
        (r"must\s+not\s+persist", "constraint"),
        (r"read.only", "constraint"),
    ]

    def __init__(self):
        """Initialize the extractor."""
        self.patterns = [
            (re.compile(pattern, re.IGNORECASE), category)
            for pattern, category in self.CONSTRAINT_PATTERNS
        ]

    def extract(self, content: str) -> Dict[str, any]:
        """
        Extract architectural constraints from documentation.

        Args:
            content: Full text of documentation

        Returns:
            Dictionary with found constraints, organized by category
        """
        if not content or not content.strip():
            return {
                "found": False,
                "constraints": {},
                "summary": "",
                "critical_count": 0,
            }

        constraints = self._extract_constraints(content)

        return {
            "found": len(constraints) > 0,
            "constraints": constraints,
            "summary": self._create_summary(constraints),
            "critical_count": sum(
                1 for c in constraints.values() for item in c if item.get("critical", False)
            ),
        }

    def _extract_constraints(self, content: str) -> Dict[str, List[Dict[str, str]]]:
        """Extract constraints organized by category."""
        constraints = {}
        lines = content.split("\n")

        for i, line in enumerate(lines):
            matched_categories = self._match_line(line)

            for category in matched_categories:
                if category not in constraints:
                    constraints[category] = []

                section = self._extract_constraint_section(lines, i, category)
                if section and not self._is_duplicate(constraints[category], section):
                    constraints[category].append(section)

        return constraints

    def _match_line(self, line: str) -> List[str]:
        """Find all categories this line matches."""
        matches = []
        for pattern, category in self.patterns:
            if pattern.search(line):
                matches.append(category)
        return list(set(matches))  # Remove duplicates

    def _extract_constraint_section(
        self, lines: List[str], start_idx: int, category: str
    ) -> Optional[Dict[str, str]]:
        """Extract a constraint section."""
        if start_idx >= len(lines):
            return None

        # Collect the constraint with context
        section_lines = []

        # Look back for heading
        heading_idx = start_idx
        if start_idx > 0 and lines[start_idx - 1].strip().startswith("#"):
            heading_idx = start_idx - 1

        # Collect lines
        for i in range(heading_idx, min(start_idx + 5, len(lines))):
            section_lines.append(lines[i])

        text = "\n".join(section_lines).strip()

        if len(text) < 15:
            return None

        return {
            "text": text,
            "category": category,
            "critical": self._is_critical(text, category),
            "line_number": heading_idx,
        }

    def _is_critical(self, text: str, category: str) -> bool:
        """Determine if this constraint is critical."""
        critical_categories = {"breaking_change", "generated_file", "sync_requirement"}
        critical_keywords = {"never", "forbidden", "must not", "critical"}

        is_critical_category = category in critical_categories
        is_critical_keyword = any(kw in text.lower() for kw in critical_keywords)

        return is_critical_category or is_critical_keyword

    def _is_duplicate(
        self, existing_constraints: List[Dict[str, str]], new_constraint: Dict[str, str]
    ) -> bool:
        """Check if constraint already exists."""
        new_text = new_constraint["text"].lower()
        return any(c["text"].lower() == new_text for c in existing_constraints)

    def _create_summary(self, constraints: Dict[str, List[Dict[str, str]]]) -> str:
        """Create summary of constraints."""
        if not constraints:
            return ""

        summary_lines = []

        # Group by priority
        critical = []
        for category, items in constraints.items():
            for item in items:
                if item.get("critical", False):
                    critical.append(f"{category}: {item['text'].split(chr(10))[0][:60]}")

        if critical:
            summary_lines.append("### 🚨 Critical Constraints")
            summary_lines.extend(f"• {c}" for c in critical[:3])

        return "\n".join(summary_lines)


def format_architectural_constraints_section(extraction: Dict[str, any]) -> str:
    """Format constraints for AGENTS.md."""
    if not extraction["found"]:
        return ""

    lines = ["## 🏗️ Architectural Constraints\n"]

    if extraction["critical_count"] > 0:
        lines.append(f"⚠️ **{extraction['critical_count']} critical constraints** — read before starting\n")

    for category, items in extraction["constraints"].items():
        category_name = category.replace("_", " ").title()
        lines.append(f"### {category_name}\n")

        for item in items[:3]:
            critical_marker = "🚨 " if item.get("critical", False) else "• "
            lines.append(f"{critical_marker} {item['text']}\n")

    return "\n".join(lines)
