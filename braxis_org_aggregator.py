"""
Feature 12: Organization Readiness Aggregator
Provides org-wide dashboards and cross-repo comparisons.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class OrgRepo:
    """A repository in an organization."""
    repo_name: str
    score: int
    language: str
    team_size: int
    last_updated: datetime
    trend: Optional[str] = None  # "↑", "↓", "→"


@dataclass
class OrgMetrics:
    """Organization-wide metrics."""
    org_name: str
    total_repos: int
    avg_score: float
    highest_score: int
    lowest_score: int
    repos_at_risk: int  # Below 50/100
    top_performers: List[str]
    needs_improvement: List[str]


@dataclass
class TeamMetrics:
    """Metrics by team."""
    team_name: str
    repos: List[OrgRepo]
    avg_score: float
    velocity: float  # Score improvement per month


class OrgAggregator:
    """Aggregates metrics across organization."""

    def __init__(self, org_name: str):
        self.org_name = org_name
        self.repos: Dict[str, OrgRepo] = {}
        self.teams: Dict[str, List[str]] = {}  # team_name -> [repo_names]
        self.history: List[Dict] = []

    def register_repo(self, repo: OrgRepo, team: Optional[str] = None) -> None:
        """Register a repository in the organization."""
        self.repos[repo.repo_name] = repo

        if team:
            if team not in self.teams:
                self.teams[team] = []
            self.teams[team].append(repo.repo_name)

    def get_org_metrics(self) -> OrgMetrics:
        """Get organization-wide metrics."""
        if not self.repos:
            return None

        repos = list(self.repos.values())
        scores = [r.score for r in repos]

        at_risk = len([s for s in scores if s < 50])
        top = sorted(repos, key=lambda r: r.score, reverse=True)[:3]
        needs_improve = sorted(repos, key=lambda r: r.score)[:3]

        metrics = OrgMetrics(
            org_name=self.org_name,
            total_repos=len(repos),
            avg_score=sum(scores) / len(scores),
            highest_score=max(scores),
            lowest_score=min(scores),
            repos_at_risk=at_risk,
            top_performers=[r.repo_name for r in top],
            needs_improvement=[r.repo_name for r in needs_improve]
        )

        return metrics

    def get_team_metrics(self, team_name: str) -> Optional[TeamMetrics]:
        """Get metrics for a specific team."""
        if team_name not in self.teams:
            return None

        repo_names = self.teams[team_name]
        repos = [self.repos[name] for name in repo_names if name in self.repos]

        if not repos:
            return None

        scores = [r.score for r in repos]
        avg = sum(scores) / len(scores)

        # Calculate velocity (improvement over time)
        velocity = self._calculate_velocity(team_name)

        return TeamMetrics(
            team_name=team_name,
            repos=repos,
            avg_score=avg,
            velocity=velocity
        )

    def get_repo_comparison(self, repo_names: List[str]) -> Dict:
        """Compare multiple repositories."""
        comparison = {}

        for name in repo_names:
            if name in self.repos:
                repo = self.repos[name]
                comparison[name] = {
                    "score": repo.score,
                    "language": repo.language,
                    "team_size": repo.team_size,
                    "trend": repo.trend or "→"
                }

        return comparison

    def get_score_distribution(self) -> Dict[str, int]:
        """Get distribution of scores across org."""
        distribution = {
            "agent_optimized": 0,  # 90-100
            "enterprise_ready": 0,  # 80-89
            "ai_native": 0,  # 60-79
            "agent_aware": 0,  # 30-59
            "not_ready": 0  # <30
        }

        for repo in self.repos.values():
            if repo.score >= 90:
                distribution["agent_optimized"] += 1
            elif repo.score >= 80:
                distribution["enterprise_ready"] += 1
            elif repo.score >= 60:
                distribution["ai_native"] += 1
            elif repo.score >= 30:
                distribution["agent_aware"] += 1
            else:
                distribution["not_ready"] += 1

        return distribution

    def get_language_stats(self) -> Dict[str, Dict]:
        """Get statistics by programming language."""
        by_lang = {}

        for repo in self.repos.values():
            if repo.language not in by_lang:
                by_lang[repo.language] = {"repos": 0, "avg_score": 0, "scores": []}

            by_lang[repo.language]["repos"] += 1
            by_lang[repo.language]["scores"].append(repo.score)

        # Calculate averages
        for lang in by_lang:
            scores = by_lang[lang]["scores"]
            by_lang[lang]["avg_score"] = sum(scores) / len(scores)
            del by_lang[lang]["scores"]  # Remove raw scores

        return by_lang

    def identify_at_risk_repos(self, threshold: int = 50) -> List[str]:
        """Identify repos below a score threshold."""
        return [
            name for name, repo in self.repos.items()
            if repo.score < threshold
        ]

    def generate_org_dashboard(self) -> str:
        """Generate organization dashboard as markdown."""
        metrics = self.get_org_metrics()
        if not metrics:
            return "No repository data available"

        dashboard = f"# {self.org_name} AI-Readiness Dashboard\n\n"

        dashboard += "## Organization Metrics\n"
        dashboard += f"- **Total Repositories:** {metrics.total_repos}\n"
        dashboard += f"- **Average Score:** {metrics.avg_score:.1f}/100\n"
        dashboard += f"- **Best:** {metrics.highest_score}/100\n"
        dashboard += f"- **Worst:** {metrics.lowest_score}/100\n"
        dashboard += f"- **At Risk (<50):** {metrics.repos_at_risk}\n\n"

        dashboard += "## Score Distribution\n"
        dist = self.get_score_distribution()
        for tier, count in dist.items():
            dashboard += f"- {tier}: {count} repos\n"
        dashboard += "\n"

        dashboard += "## Top Performers\n"
        for name in metrics.top_performers:
            score = self.repos[name].score
            dashboard += f"- ✓ {name} ({score}/100)\n"
        dashboard += "\n"

        dashboard += "## Needs Improvement\n"
        for name in metrics.needs_improvement:
            score = self.repos[name].score
            dashboard += f"- ⚠ {name} ({score}/100)\n"
        dashboard += "\n"

        dashboard += "## By Language\n"
        lang_stats = self.get_language_stats()
        for lang, stats in lang_stats.items():
            dashboard += f"- **{lang}:** {stats['repos']} repos, avg {stats['avg_score']:.1f}/100\n"

        return dashboard

    def _calculate_velocity(self, team_name: str) -> float:
        """Calculate team's improvement velocity."""
        # Simplified: return average of recent improvements
        team_repos = self.teams.get(team_name, [])
        velocities = []

        for repo_name in team_repos:
            if repo_name in self.repos:
                repo = self.repos[repo_name]
                # Simplified velocity calculation
                if repo.trend == "↑":
                    velocities.append(5.0)
                elif repo.trend == "↓":
                    velocities.append(-5.0)
                else:
                    velocities.append(0.0)

        return sum(velocities) / len(velocities) if velocities else 0.0
