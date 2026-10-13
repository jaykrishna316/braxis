"""Feature 5: Agent-Specific Policy Extraction

Extracts explicit agent contribution policies and warnings that should
influence how agents approach the project.
"""

import re
from typing import Dict, List, Optional


class AgentPolicyExtractor:
    """Extract agent-specific policies and warnings."""

    # Policy keywords
    POLICY_KEYWORDS = [
        r"agent",
        r"code\s+agent",
        r"ai.?contributed",
        r"ai.?agent",
        r"autonomous",
        r"llm",
        r"machine\s+learning.*model",
    ]

    # Warning indicators
    WARNING_KEYWORDS = [
        r"do\s+not.*agent",
        r"agent.*rejected",
        r"agent.*warning",
        r"pure\s+agent",
        r"agent.only",
        r"do\s+not\s+submit.*agent",
    ]

    def __init__(self):
        """Initialize extractor."""
        self.policy_patterns = [re.compile(p, re.IGNORECASE) for p in self.POLICY_KEYWORDS]
        self.warning_patterns = [re.compile(p, re.IGNORECASE) for p in self.WARNING_KEYWORDS]

    def extract(self, content: str) -> Dict[str, any]:
        """Extract agent policies from documentation."""
        if not content:
            return {
                "found": False,
                "policies": [],
                "warnings": [],
                "restrictions": [],
                "sentiment": "neutral",
            }

        policies = self._extract_policies(content)
        warnings = self._extract_warnings(content)

        return {
            "found": len(policies) > 0 or len(warnings) > 0,
            "policies": policies,
            "warnings": warnings,
            "restrictions": self._classify_restrictions(policies + warnings),
            "sentiment": self._determine_sentiment(warnings),
        }

    def _extract_policies(self, content: str) -> List[Dict[str, str]]:
        """Extract agent policies."""
        policies = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            # Check if line mentions agents
            if any(p.search(line) for p in self.policy_patterns):
                # Extract section
                section = self._extract_policy_section(lines, i)
                if section and not self._is_duplicate(policies, section):
                    policies.append(section)

        return policies

    def _extract_warnings(self, content: str) -> List[Dict[str, str]]:
        """Extract agent-specific warnings."""
        warnings = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if any(p.search(line) for p in self.warning_patterns):
                section = self._extract_policy_section(lines, i)
                if section:
                    section["is_warning"] = True
                    warnings.append(section)

        return warnings

    def _extract_policy_section(self, lines: List[str], idx: int) -> Optional[Dict[str, str]]:
        """Extract a coherent policy section."""
        start = max(0, idx - 1)
        end = min(len(lines), idx + 5)

        section_lines = []
        for i in range(start, end):
            line = lines[i]
            if line.strip():
                section_lines.append(line)

        text = "\n".join(section_lines).strip()

        if len(text) < 20:
            return None

        return {
            "text": text,
            "line_number": idx,
            "type": self._classify_policy(text),
            "is_warning": False,
        }

    def _classify_policy(self, text: str) -> str:
        """Classify the type of policy."""
        text_lower = text.lower()

        if "do not submit" in text_lower or "pure agent" in text_lower:
            return "contribution_policy"
        elif "pr" in text_lower or "pull request" in text_lower:
            return "pr_policy"
        elif "agent" in text_lower and "contribute" in text_lower:
            return "contribution_policy"
        elif "agent" in text_lower and ("avoid" in text_lower or "do not" in text_lower):
            return "restriction"
        else:
            return "general_policy"

    def _classify_restrictions(self, all_items: List[Dict[str, str]]) -> List[str]:
        """Classify what restrictions apply to agents."""
        restrictions = []

        for item in all_items:
            text_lower = item["text"].lower()

            if "do not submit" in text_lower or "pure agent" in text_lower:
                restrictions.append("No pure AI-generated PRs")

            if "must review" in text_lower or "human review" in text_lower:
                restrictions.append("Requires human review before submission")

            if "coordinate" in text_lower or "discuss" in text_lower:
                restrictions.append("Coordination required before work")

            if "one.off" in text_lower or "busywork" in text_lower:
                restrictions.append("No low-value busywork PRs")

        return list(set(restrictions))  # Unique

    def _determine_sentiment(self, warnings: List[Dict[str, str]]) -> str:
        """Determine project's sentiment toward agents."""
        if not warnings:
            return "agent_friendly"

        negative_keywords = ["rejected", "closed", "not", "forbidden", "do not"]
        warning_text = " ".join(w["text"].lower() for w in warnings)

        negative_count = sum(1 for kw in negative_keywords if kw in warning_text)

        if negative_count > 3:
            return "agent_cautious"
        elif negative_count > 0:
            return "agent_restricted"
        else:
            return "agent_friendly"

    def _is_duplicate(self, policies: List[Dict[str, str]], new_policy: Dict[str, str]) -> bool:
        """Check if policy already exists."""
        new_text = new_policy["text"].lower()
        return any(p["text"].lower() == new_text for p in policies)


def format_agent_policy_section(extraction: Dict[str, any]) -> str:
    """Format agent policies for AGENTS.md."""
    if not extraction["found"]:
        return ""

    sentiment = extraction["sentiment"]

    if sentiment == "agent_friendly":
        header = "## ✅ Agent-Friendly Project\n\nThis project welcomes AI agent contributions.\n"
    elif sentiment == "agent_restricted":
        header = "## ⚠️ Agent Contribution Guidelines\n\nRead these guidelines before working on this project:\n"
    else:
        header = "## 🤖 Agent Policy\n\nAgent contributions require careful attention to:\n"

    lines = [header]

    if extraction["warnings"]:
        lines.append("### Critical Policies\n")
        for warning in extraction["warnings"][:3]:
            lines.append(f"**⚠️ {warning['type'].replace('_', ' ').title()}**\n")
            lines.append(f"{warning['text']}\n\n")

    if extraction["restrictions"]:
        lines.append("### Restrictions\n")
        for restriction in extraction["restrictions"]:
            lines.append(f"• {restriction}\n")

    if extraction["policies"] and not extraction["warnings"]:
        lines.append("### Policies\n")
        for policy in extraction["policies"][:3]:
            lines.append(f"• {policy['text'][:100]}...\n")

    return "\n".join(lines)
