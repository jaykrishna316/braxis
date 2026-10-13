"""
Feature 2: Agent Performance Feedback Loop & Feature 13: Agent Interaction Recording
Tracks agent performance metrics and stores interaction history for feedback loops.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import json


class AgentType(Enum):
    """Types of AI agents that can interact with projects."""
    CLAUDE_CODE = "claude-code"
    CURSOR = "cursor"
    COPILOT = "copilot"
    GENERIC = "generic"


@dataclass
class TaskMetrics:
    """Metrics for an agent task."""
    task_id: str
    agent_type: AgentType
    task_description: str
    start_time: datetime
    end_time: Optional[datetime]
    success: bool
    time_to_first_solution: Optional[float]  # seconds
    task_success_rate: float  # 0-100
    context_relevance: float  # 0-100
    tokens_used: int
    sections_referenced: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class AgentEfficiencyScore:
    """Overall agent efficiency metric for a repo."""
    repo_name: str
    agent_type: AgentType
    tasks_completed: int
    avg_time_to_solution: float
    success_rate: float
    context_relevance: float
    efficiency_score: float  # 0-100
    trend: Optional[float] = None  # percent improvement


class TelemetryEngine:
    """Manages agent performance tracking and telemetry."""

    def __init__(self, repo_name: str):
        self.repo_name = repo_name
        self.tasks: Dict[str, TaskMetrics] = {}
        self.interactions: List[Dict] = []
        self.efficiency_scores: Dict[AgentType, AgentEfficiencyScore] = {}

    def record_task(self, task_id: str, agent_type: AgentType,
                   description: str, success: bool,
                   time_to_solution: Optional[float] = None,
                   context_relevance: float = 0.0) -> TaskMetrics:
        """Record a completed agent task."""
        now = datetime.now()
        task = TaskMetrics(
            task_id=task_id,
            agent_type=agent_type,
            task_description=description,
            start_time=now,
            end_time=now,
            success=success,
            time_to_first_solution=time_to_solution,
            task_success_rate=100.0 if success else 0.0,
            context_relevance=context_relevance,
            tokens_used=0
        )
        self.tasks[task_id] = task
        self._update_efficiency_scores(agent_type)
        return task

    def record_interaction(self, agent_type: AgentType, action: str,
                          context_size: int, response_tokens: int,
                          sections_accessed: List[str]) -> None:
        """Record an agent interaction with the codebase."""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "agent_type": agent_type.value,
            "action": action,
            "context_size": context_size,
            "response_tokens": response_tokens,
            "sections_accessed": sections_accessed
        }
        self.interactions.append(interaction)

    def get_efficiency_score(self, agent_type: AgentType) -> Optional[AgentEfficiencyScore]:
        """Get efficiency score for an agent type."""
        return self.efficiency_scores.get(agent_type)

    def _update_efficiency_scores(self, agent_type: AgentType) -> None:
        """Update efficiency scores after recording a task."""
        agent_tasks = [
            t for t in self.tasks.values()
            if t.agent_type == agent_type
        ]

        if not agent_tasks:
            return

        completed = len([t for t in agent_tasks if t.success])
        avg_time = sum(t.time_to_first_solution or 0 for t in agent_tasks) / len(agent_tasks)
        success_rate = (completed / len(agent_tasks)) * 100
        avg_relevance = sum(t.context_relevance for t in agent_tasks) / len(agent_tasks)

        efficiency = (success_rate * 0.4 + avg_relevance * 0.4 +
                     max(0, 100 - avg_time / 10) * 0.2)

        score = AgentEfficiencyScore(
            repo_name=self.repo_name,
            agent_type=agent_type,
            tasks_completed=len(agent_tasks),
            avg_time_to_solution=avg_time,
            success_rate=success_rate,
            context_relevance=avg_relevance,
            efficiency_score=min(100, max(0, efficiency))
        )

        self.efficiency_scores[agent_type] = score

    def get_performance_improvement(self, agent_type: AgentType,
                                   baseline_score: float) -> Optional[float]:
        """Calculate performance improvement vs baseline."""
        current = self.get_efficiency_score(agent_type)
        if not current:
            return None

        improvement = ((current.efficiency_score - baseline_score) / baseline_score) * 100
        return improvement

    def get_interaction_summary(self) -> Dict:
        """Get summary of all interactions."""
        if not self.interactions:
            return {"total": 0, "by_agent": {}}

        by_agent = {}
        total_context = 0
        total_tokens = 0

        for interaction in self.interactions:
            agent = interaction["agent_type"]
            if agent not in by_agent:
                by_agent[agent] = {
                    "count": 0,
                    "total_context": 0,
                    "total_tokens": 0
                }

            by_agent[agent]["count"] += 1
            by_agent[agent]["total_context"] += interaction["context_size"]
            by_agent[agent]["total_tokens"] += interaction["response_tokens"]
            total_context += interaction["context_size"]
            total_tokens += interaction["response_tokens"]

        return {
            "total": len(self.interactions),
            "by_agent": by_agent,
            "total_context_kb": total_context / 1024,
            "total_tokens": total_tokens
        }

    def export_telemetry(self) -> Dict:
        """Export telemetry data for analysis."""
        return {
            "repo": self.repo_name,
            "timestamp": datetime.now().isoformat(),
            "tasks": {
                k: {
                    "agent": v.agent_type.value,
                    "success": v.success,
                    "time_to_solution": v.time_to_first_solution,
                    "context_relevance": v.context_relevance
                }
                for k, v in self.tasks.items()
            },
            "efficiency_scores": {
                k.value: {
                    "score": v.efficiency_score,
                    "success_rate": v.success_rate,
                    "tasks_completed": v.tasks_completed
                }
                for k, v in self.efficiency_scores.items()
            },
            "interactions": self.interactions
        }
