"""Feature 4: Multi-Variant Pattern Extraction

Detects sync/async twins, platform clients, and patterns requiring
synchronized changes across variants.
"""

import re
from typing import Dict, List, Optional


class MultiVariantExtractor:
    """Extract multi-variant patterns (twins, platform clients, etc.)."""

    # Twin patterns
    TWIN_PATTERNS = [
        (r"async.*client|Async.*Client", "async_client"),
        (r"sync.*client|Sync.*Client", "sync_client"),
        (r"(\w+)\s+/\s+Async\1", "sync_async_pair"),
        (r"(Anthropic)\s+/\s+(AsyncAnthropic)", "client_twin"),
        (r"keep.*in\s+sync", "sync_requirement"),
        (r"both.*must\s+change", "sync_requirement"),
    ]

    # Platform patterns
    PLATFORM_PATTERNS = {
        "aws": r"aws|amazon|boto",
        "bedrock": r"bedrock|anthropic.*bedrock",
        "vertex": r"vertex|google.*vertex",
        "gcp": r"google\s+cloud|gcp",
        "azure": r"azure|microsoft",
    }

    def __init__(self):
        """Initialize extractor."""
        self.twin_patterns = [
            (re.compile(pattern, re.IGNORECASE), category) for pattern, category in self.TWIN_PATTERNS
        ]
        self.platform_patterns = {
            name: re.compile(pattern, re.IGNORECASE) for name, pattern in self.PLATFORM_PATTERNS.items()
        }

    def extract(self, content: str) -> Dict[str, any]:
        """Extract multi-variant patterns."""
        if not content:
            return {
                "found": False,
                "twins": [],
                "platforms": [],
                "sync_requirements": [],
                "auth_patterns": [],
            }

        return {
            "found": True,
            "twins": self._detect_twins(content),
            "platforms": self._detect_platforms(content),
            "sync_requirements": self._extract_sync_requirements(content),
            "auth_patterns": self._extract_auth_patterns(content),
        }

    def _detect_twins(self, content: str) -> List[Dict[str, str]]:
        """Detect sync/async twin patterns."""
        twins = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            for pattern, category in self.twin_patterns:
                if pattern.search(line):
                    if category == "sync_requirement":
                        continue  # Handle separately

                    twin_info = self._extract_twin_info(lines, i, category)
                    if twin_info and not self._is_duplicate_twin(twins, twin_info):
                        twins.append(twin_info)

        return twins

    def _extract_twin_info(self, lines: List[str], idx: int, category: str) -> Optional[Dict[str, str]]:
        """Extract information about a twin pattern."""
        start = max(0, idx - 1)
        end = min(len(lines), idx + 3)
        context = "\n".join(lines[start:end]).strip()

        # Try to extract class/method names
        match = re.search(r"(\w+)\s+/\s+(\w+)", context)
        if match:
            return {
                "type": "class_twin",
                "sync_name": match.group(1),
                "async_name": match.group(2),
                "context": context,
                "category": category,
            }

        return {
            "type": category,
            "context": context,
            "category": category,
        }

    def _is_duplicate_twin(self, twins: List[Dict[str, str]], new_twin: Dict[str, str]) -> bool:
        """Check if twin already in list."""
        if new_twin["type"] == "class_twin":
            return any(
                t["type"] == "class_twin"
                and t.get("sync_name") == new_twin.get("sync_name")
                for t in twins
            )
        return False

    def _detect_platforms(self, content: str) -> List[Dict[str, str]]:
        """Detect platform-specific clients."""
        platforms = []

        for platform_name, pattern in self.platform_patterns.items():
            if pattern.search(content):
                platform_info = self._extract_platform_info(content, platform_name)
                platforms.append(platform_info)

        return platforms

    def _extract_platform_info(self, content: str, platform_name: str) -> Dict[str, str]:
        """Extract platform-specific information."""
        lines = content.split("\n")

        auth_method = "standard"
        if "credential" in content.lower():
            auth_method = "credential_based"
        if "key" in content.lower() or "token" in content.lower():
            auth_method = "key_token"

        return {
            "name": platform_name.upper(),
            "detected": True,
            "auth_method": auth_method,
            "requires_setup": True,
        }

    def _extract_sync_requirements(self, content: str) -> List[Dict[str, str]]:
        """Extract patterns requiring synchronized changes."""
        requirements = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if "keep" in line.lower() and "sync" in line.lower():
                section = "\n".join(lines[max(0, i - 1) : min(len(lines), i + 3)])
                requirements.append({
                    "type": "keep_in_sync",
                    "requirement": section.strip(),
                    "line": i,
                })

            if "both" in line.lower() and "must" in line.lower() and "change" in line.lower():
                section = "\n".join(lines[max(0, i - 1) : min(len(lines), i + 3)])
                requirements.append({
                    "type": "dual_change",
                    "requirement": section.strip(),
                    "line": i,
                })

        return requirements

    def _extract_auth_patterns(self, content: str) -> List[Dict[str, str]]:
        """Extract authentication/credential patterns."""
        patterns = []

        auth_keywords = [
            ("api_key", r"api.?key|api_key"),
            ("bearer", r"bearer|token"),
            ("oauth", r"oauth|oauth2"),
            ("credentials", r"credentials|credential"),
            ("authentication", r"authentication|authenticate"),
        ]

        for auth_type, pattern in auth_keywords:
            if re.search(pattern, content, re.IGNORECASE):
                patterns.append({
                    "type": auth_type,
                    "found": True,
                })

        return patterns


def format_multi_variant_section(extraction: Dict[str, any]) -> str:
    """Format multi-variant extraction for AGENTS.md."""
    if not extraction["found"]:
        return ""

    lines = ["## 👥 Multi-Variant Patterns\n"]

    if extraction["twins"]:
        lines.append("### Sync/Async Twins\n")
        lines.append("Changes to one must be mirrored to the other:\n")
        for twin in extraction["twins"]:
            if twin["type"] == "class_twin":
                lines.append(
                    f"• `{twin['sync_name']}` (sync) ↔️ `{twin['async_name']}` (async)\n"
                )
            else:
                lines.append(f"• {twin['category']}\n")

    if extraction["platforms"]:
        lines.append("### Platform Clients\n")
        lines.append("This project supports multiple cloud platforms:\n")
        for platform in extraction["platforms"]:
            auth_info = f" — {platform['auth_method']}" if platform.get("auth_method") else ""
            lines.append(f"• {platform['name']}{auth_info}\n")

    if extraction["sync_requirements"]:
        lines.append("### Synchronization Requirements\n")
        for req in extraction["sync_requirements"][:3]:
            lines.append(f"• {req['requirement']}\n")

    if extraction["auth_patterns"]:
        lines.append("### Authentication Patterns\n")
        auth_types = [p["type"] for p in extraction["auth_patterns"]]
        lines.append(f"Supported: {', '.join(auth_types)}\n")

    return "\n".join(lines)
