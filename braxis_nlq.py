"""
Feature 11: Natural Language Query Interface
Allows agents to query context using natural language.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class QueryType(Enum):
    """Types of natural language queries."""
    HOW_TO = "how_to"
    WHAT_IS = "what_is"
    WHERE_IS = "where_is"
    WHY = "why"
    EXAMPLE = "example"
    PATTERN = "pattern"


@dataclass
class ContextSection:
    """A section of context documentation."""
    title: str
    content: str
    keywords: List[str]
    relevance_score: float = 0.0


@dataclass
class QueryResult:
    """Result of a natural language query."""
    query: str
    query_type: QueryType
    matching_sections: List[ContextSection]
    direct_answer: Optional[str] = None
    relevance_score: float = 0.0


class NaturalLanguageQueryEngine:
    """Processes natural language queries on context."""

    def __init__(self):
        self.sections: Dict[str, ContextSection] = {}
        self.query_history: List[QueryResult] = []

    def register_section(self, section: ContextSection) -> None:
        """Register a context section."""
        self.sections[section.title] = section

    def query(self, question: str) -> QueryResult:
        """Process a natural language query."""
        query_type = self._classify_query(question)
        keywords = self._extract_keywords(question)

        matching_sections = self._find_matching_sections(keywords, query_type)
        answer = self._generate_answer(question, matching_sections, query_type)

        result = QueryResult(
            query=question,
            query_type=query_type,
            matching_sections=matching_sections,
            direct_answer=answer,
            relevance_score=self._calculate_relevance(matching_sections)
        )

        self.query_history.append(result)
        return result

    def _classify_query(self, question: str) -> QueryType:
        """Classify query type."""
        question_lower = question.lower()

        if any(word in question_lower for word in ["where", "find", "location", "file", "path", "defined"]):
            return QueryType.WHERE_IS
        elif any(word in question_lower for word in ["how", "setup", "install", "run", "execute"]):
            return QueryType.HOW_TO
        elif any(word in question_lower for word in ["why", "reason", "decision", "because"]):
            return QueryType.WHY
        elif any(word in question_lower for word in ["example", "instance", "demo", "show"]):
            return QueryType.EXAMPLE
        elif any(word in question_lower for word in ["pattern", "approach", "method", "practice"]):
            return QueryType.PATTERN
        elif any(word in question_lower for word in ["what", "is", "define", "mean"]):
            return QueryType.WHAT_IS

        return QueryType.WHAT_IS

    def _extract_keywords(self, question: str) -> List[str]:
        """Extract keywords from question."""
        stop_words = {"how", "what", "where", "why", "is", "are", "the", "a", "an", "to", "do", "should"}

        words = question.lower().split()
        keywords = [w.strip("?,.:!") for w in words
                   if w.strip("?,.:!") not in stop_words and len(w) > 2]

        return keywords

    def _find_matching_sections(self, keywords: List[str],
                               query_type: QueryType) -> List[ContextSection]:
        """Find matching sections based on keywords."""
        matches = []

        for section in self.sections.values():
            score = 0

            # Check keyword matches
            for keyword in keywords:
                if keyword in section.title.lower():
                    score += 2
                if keyword in section.content.lower():
                    score += 1
                for sec_keyword in section.keywords:
                    if keyword in sec_keyword.lower():
                        score += 1.5

            if score > 0:
                section.relevance_score = score
                matches.append(section)

        # Sort by relevance
        matches.sort(key=lambda x: x.relevance_score, reverse=True)
        return matches[:5]  # Return top 5

    def _generate_answer(self, question: str, sections: List[ContextSection],
                        query_type: QueryType) -> Optional[str]:
        """Generate direct answer to query."""
        if not sections:
            return None

        if query_type == QueryType.HOW_TO:
            answer = "Based on the documentation:\n\n"
            for section in sections[:2]:
                answer += f"**{section.title}:**\n{section.content[:200]}...\n\n"
            answer += "See the full documentation for detailed steps."

        elif query_type == QueryType.WHERE_IS:
            answer = "You can find this in:\n"
            for section in sections[:3]:
                answer += f"- {section.title}\n"

        elif query_type == QueryType.EXAMPLE:
            answer = "Examples found in:\n"
            for section in sections[:2]:
                answer += f"- {section.title}\n"
                # Extract code blocks if present
                if "```" in section.content:
                    start = section.content.find("```")
                    end = section.content.find("```", start + 3)
                    if end > start:
                        answer += section.content[start:end+3] + "\n"
        else:
            # Default answer
            if sections:
                answer = f"Based on '{sections[0].title}': {sections[0].content[:300]}"

        return answer

    def _calculate_relevance(self, sections: List[ContextSection]) -> float:
        """Calculate overall relevance score."""
        if not sections:
            return 0.0

        scores = [s.relevance_score for s in sections]
        avg_score = sum(scores) / len(scores)

        # Normalize to 0-100
        return min(100, (avg_score / 5) * 100)

    def get_query_suggestions(self, partial_query: str) -> List[str]:
        """Suggest complete queries based on partial input."""
        suggestions = []

        for section in self.sections.values():
            # Create suggestion based on section
            if partial_query.lower() in section.title.lower():
                suggestions.append(f"Tell me about {section.title}")

            for keyword in section.keywords:
                if partial_query.lower() in keyword.lower():
                    suggestions.append(f"How do I use {keyword}?")

        return suggestions[:5]
