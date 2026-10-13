"""Feature 1: Product Authority & Safety Extraction

Extracts sections documenting product guarantees, state contracts, mutation constraints,
and behavioral promises. Creates [PRODUCT_AUTHORITY] section for AGENTS.md.
"""

import re
from typing import Dict, List, Optional, Tuple


class ProductAuthorityExtractor:
    """Extract product authority patterns from documentation."""

    # Keywords indicating authority/safety constraints
    AUTHORITY_PATTERNS = [
        r"ephemeral",
        r"persistent",
        r"read.only",
        r"read-only",
        r"guarantee",
        r"guaranteed",
        r"promise",
        r"contract",
        r"contract.*semantics",
        r"state.*lifecycle",
        r"state.*management",
        r"mutation.*constraint",
        r"immutable",
        r"authority",
        r"permission",
        r"forbidden",
        r"not.*allowed",
        r"do\s+not",
        r"never\s+",
    ]

    def __init__(self):
        """Initialize the extractor."""
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.AUTHORITY_PATTERNS]

    def extract(self, content: str, filename: str = "AGENTS.md") -> Dict[str, any]:
        """
        Extract product authority patterns from documentation.

        Args:
            content: Full text content of documentation file
            filename: Name of the file being analyzed

        Returns:
            Dictionary with:
            - found: bool indicating if authority patterns were detected
            - sections: List of extracted authority sections
            - summary: Short summary of key authorities
        """
        if not content or not content.strip():
            return {
                "found": False,
                "sections": [],
                "summary": "",
                "confidence": 0.0,
            }

        sections = self._extract_authority_sections(content)

        return {
            "found": len(sections) > 0,
            "sections": sections,
            "summary": self._create_summary(sections),
            "confidence": self._calculate_confidence(sections),
        }

    def _extract_authority_sections(self, content: str) -> List[Dict[str, str]]:
        """Extract sections containing authority patterns."""
        sections = []
        lines = content.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this line matches any authority pattern
            if self._matches_patterns(line):
                # Extract the section around this line
                section = self._extract_section(lines, i)

                # Avoid duplicates
                if section and not any(s["text"] == section["text"] for s in sections):
                    sections.append(section)

                # Skip ahead to avoid re-processing
                i += len(section["text"].split("\n"))
            else:
                i += 1

        return sections

    def _matches_patterns(self, line: str) -> bool:
        """Check if line matches any authority pattern."""
        return any(pattern.search(line) for pattern in self.patterns)

    def _extract_section(self, lines: List[str], start_idx: int) -> Optional[Dict[str, str]]:
        """Extract a coherent section starting from the given line."""
        if start_idx >= len(lines):
            return None

        # Find section boundaries (heading, blank lines, etc.)
        section_lines = [lines[start_idx]]

        # Look backward for heading/context
        context_start = start_idx
        if start_idx > 0:
            # Go back up to 2 lines for context (heading, etc.)
            for j in range(max(0, start_idx - 2), start_idx):
                if lines[j].strip() and not self._is_list_continuation(lines[j]):
                    context_start = j

        # Look forward for continuation
        end_idx = start_idx + 1
        while end_idx < len(lines) and end_idx < start_idx + 10:
            line = lines[end_idx]

            # Stop at empty lines or major section breaks
            if not line.strip():
                break
            if line.startswith("#") and end_idx > start_idx:
                break
            if self._is_code_block_boundary(line):
                end_idx += 1
                continue

            section_lines.append(line)
            end_idx += 1

        text = "\n".join(section_lines).strip()

        if len(text) < 20:  # Skip very short sections
            return None

        return {
            "text": text,
            "start_line": context_start,
            "end_line": end_idx,
            "type": self._classify_authority(text),
        }

    def _is_list_continuation(self, line: str) -> bool:
        """Check if line is a list item or continuation."""
        return bool(re.match(r"^\s*[-*+]\s", line)) or bool(re.match(r"^\s+", line))

    def _is_code_block_boundary(self, line: str) -> bool:
        """Check if line is a code block marker."""
        return line.strip().startswith("```")

    def _classify_authority(self, text: str) -> str:
        """Classify the type of authority constraint."""
        text_lower = text.lower()

        if "ephemeral" in text_lower or "read.only" in text_lower:
            return "state_contract"
        elif "do not" in text_lower or "never" in text_lower or "forbidden" in text_lower:
            return "constraint"
        elif "guarantee" in text_lower or "promise" in text_lower:
            return "guarantee"
        elif "mutation" in text_lower or "immutable" in text_lower:
            return "mutation_rule"
        else:
            return "authority"

    def _create_summary(self, sections: List[Dict[str, str]]) -> str:
        """Create a brief summary of key authorities."""
        if not sections:
            return ""

        summaries = []
        for section in sections[:3]:  # Top 3 sections
            # Extract first line or first 100 chars
            text = section["text"].split("\n")[0]
            if len(text) > 80:
                text = text[:77] + "..."
            summaries.append(f"• {text}")

        return "\n".join(summaries)

    def _calculate_confidence(self, sections: List[Dict[str, str]]) -> float:
        """Calculate confidence score based on number and quality of sections."""
        if not sections:
            return 0.0

        # More sections = higher confidence, up to 1.0
        confidence = min(len(sections) / 3.0, 1.0)

        # Boost confidence for specific keywords
        keyword_boost = 0.0
        for section in sections:
            if section["type"] in ["state_contract", "constraint"]:
                keyword_boost += 0.15

        return min(confidence + keyword_boost, 1.0)


def format_product_authority_section(extraction: Dict[str, any]) -> str:
    """Format extraction results as AGENTS.md section."""
    if not extraction["found"]:
        return ""

    lines = ["## 🛡️ Product Authority & Guarantees\n"]
    lines.append("Documented product guarantees, state contracts, and constraints:\n")

    for section in extraction["sections"][:5]:  # Show top 5
        lines.append(f"### {section['type'].replace('_', ' ').title()}")
        lines.append(f"\n{section['text']}\n")

    return "\n".join(lines)
