"""
Feature 5: Architecture Decision Record (ADR) Auto-Generation
Extracts architectural decisions from code patterns and generates ADRs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class DecisionStatus(Enum):
    """Status of an architecture decision."""
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


@dataclass
class ADR:
    """Architecture Decision Record."""
    id: int
    title: str
    status: DecisionStatus
    context: str
    decision: str
    consequences: List[str]
    alternatives: List[str] = field(default_factory=list)
    related_adr_ids: List[int] = field(default_factory=list)
    date: datetime = field(default_factory=datetime.now)

    def to_markdown(self) -> str:
        """Convert ADR to Markdown format."""
        output = f"# ADR {self.id}: {self.title}\n\n"
        output += f"**Status:** {self.status.value}\n"
        output += f"**Date:** {self.date.strftime('%Y-%m-%d')}\n\n"

        output += "## Context\n"
        output += f"{self.context}\n\n"

        output += "## Decision\n"
        output += f"{self.decision}\n\n"

        output += "## Consequences\n"
        for consequence in self.consequences:
            output += f"- {consequence}\n"
        output += "\n"

        if self.alternatives:
            output += "## Considered Alternatives\n"
            for alt in self.alternatives:
                output += f"- {alt}\n"
            output += "\n"

        if self.related_adr_ids:
            output += "## Related ADRs\n"
            for adr_id in self.related_adr_ids:
                output += f"- ADR {adr_id}\n"

        return output


class ADRGenerator:
    """Generates Architecture Decision Records from code patterns."""

    def __init__(self, repo_name: str):
        self.repo_name = repo_name
        self.adrs: Dict[int, ADR] = {}
        self.next_id = 1

    def detect_monorepo_decision(self, monorepo_type: str) -> ADR:
        """Detect and record monorepo decision."""
        decisions = {
            "pnpm": {
                "title": "Use pnpm workspaces for dependency management",
                "context": "Multi-package JavaScript/Node.js project requiring efficient dependency management",
                "decision": "Use pnpm workspaces for all package management",
                "consequences": [
                    "Faster install times through hard linking",
                    "Strict dependency isolation between packages",
                    "Requires pnpm v8+ in CI/CD",
                    "All contributors must use pnpm"
                ]
            },
            "yarn": {
                "title": "Use Yarn workspaces for monorepo management",
                "context": "Multi-package project requiring coordination between packages",
                "decision": "Use Yarn workspaces for package management",
                "consequences": [
                    "Unified dependency resolution across packages",
                    "Improved build performance with caching",
                    "Requires Yarn v3+ for best experience"
                ]
            },
            "npm": {
                "title": "Use npm workspaces for package management",
                "context": "Multi-package Node.js project with shared dependencies",
                "decision": "Use npm workspaces",
                "consequences": [
                    "Native npm support without additional tools",
                    "Good for smaller monorepos",
                    "Limited performance optimization"
                ]
            }
        }

        if monorepo_type not in decisions:
            return None

        config = decisions[monorepo_type]
        adr = ADR(
            id=self.next_id,
            title=config["title"],
            status=DecisionStatus.ACCEPTED,
            context=config["context"],
            decision=config["decision"],
            consequences=config["consequences"]
        )

        self._register_adr(adr)
        return adr

    def detect_framework_decision(self, framework_type: str,
                                 alternative: str) -> ADR:
        """Detect and record framework selection decision."""
        adr = ADR(
            id=self.next_id,
            title=f"Use {framework_type} as primary framework",
            status=DecisionStatus.ACCEPTED,
            context=f"Selecting primary framework for {self.repo_name}",
            decision=f"Selected {framework_type} as the primary framework",
            consequences=[
                f"All core functionality built on {framework_type}",
                f"Team expertise focuses on {framework_type}",
                f"Dependencies compatible with {framework_type}"
            ],
            alternatives=[f"Use {alternative} instead"]
        )

        self._register_adr(adr)
        return adr

    def detect_error_handling_pattern(self, pattern: str) -> ADR:
        """Detect and record error handling pattern decision."""
        patterns = {
            "result_type": {
                "title": "Use Result<T, E> pattern for error handling",
                "decision": "All fallible functions return Result types",
                "consequences": [
                    "Explicit error handling at call sites",
                    "Type-safe error propagation",
                    "Requires unwrap() calls (which can panic)"
                ]
            },
            "exceptions": {
                "title": "Use exceptions for error handling",
                "decision": "Errors represented as exceptions",
                "consequences": [
                    "Simpler code for happy paths",
                    "Implicit error propagation",
                    "Stack traces available in debuggers"
                ]
            }
        }

        if pattern not in patterns:
            return None

        config = patterns[pattern]
        adr = ADR(
            id=self.next_id,
            title=config["title"],
            status=DecisionStatus.ACCEPTED,
            context=f"Error handling strategy for {self.repo_name}",
            decision=config["decision"],
            consequences=config["consequences"]
        )

        self._register_adr(adr)
        return adr

    def detect_testing_strategy(self, strategy: str) -> ADR:
        """Detect and record testing strategy decision."""
        strategies = {
            "unit_focused": {
                "title": "Focus on unit testing with high coverage",
                "decision": "Maximize unit test coverage with minimal integration tests",
                "consequences": [
                    "Fast test execution",
                    "Early detection of bugs",
                    "May miss integration issues"
                ]
            },
            "integration_heavy": {
                "title": "Emphasize integration testing",
                "decision": "Balance unit and integration tests with full end-to-end scenarios",
                "consequences": [
                    "Better real-world bug detection",
                    "Slower test execution",
                    "More complex test setup"
                ]
            },
            "bdd": {
                "title": "Use BDD (Behavior-Driven Development) approach",
                "decision": "Write tests as behavior specifications",
                "consequences": [
                    "Improved communication with stakeholders",
                    "Test-driven development culture",
                    "Requires learning BDD frameworks"
                ]
            }
        }

        if strategy not in strategies:
            return None

        config = strategies[strategy]
        adr = ADR(
            id=self.next_id,
            title=config["title"],
            status=DecisionStatus.ACCEPTED,
            context=f"Testing strategy for {self.repo_name}",
            decision=config["decision"],
            consequences=config["consequences"]
        )

        self._register_adr(adr)
        return adr

    def _register_adr(self, adr: ADR) -> None:
        """Register and store an ADR."""
        self.adrs[adr.id] = adr
        self.next_id += 1

    def get_all_adrs(self) -> List[ADR]:
        """Get all recorded ADRs."""
        return sorted(self.adrs.values(), key=lambda x: x.id)

    def export_adr_directory(self) -> Dict[int, str]:
        """Export all ADRs as markdown files."""
        return {
            adr.id: adr.to_markdown()
            for adr in self.get_all_adrs()
        }
