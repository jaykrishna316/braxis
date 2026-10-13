"""
Feature 1: Cross-Repo Competitive Benchmarking
Clusters repos by language/framework and provides percentile ranking within clusters.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


@dataclass
class RepoMetadata:
    """Metadata for a repository in the benchmark."""
    repo_name: str
    owner: str
    language: str
    framework: Optional[str]
    project_size: str  # small, medium, large
    age_months: int
    score: int
    last_updated: datetime
    tags: List[str] = field(default_factory=list)


@dataclass
class BenchmarkCluster:
    """A cluster of similar repositories for benchmarking."""
    cluster_id: str
    language: str
    framework: Optional[str]
    project_size: str
    repos: List[RepoMetadata] = field(default_factory=list)

    def add_repo(self, repo: RepoMetadata) -> None:
        """Add a repository to this cluster."""
        self.repos.append(repo)
        self.repos.sort(key=lambda r: r.score, reverse=True)

    def get_percentile(self, score: int) -> float:
        """Get percentile rank for a score in this cluster."""
        if not self.repos:
            return 0.0

        scores = [r.score for r in self.repos]
        if score not in scores:
            scores.append(score)
            scores.sort(reverse=True)

        rank = scores.index(score) + 1
        return ((len(scores) - rank) / len(scores)) * 100

    def get_stats(self) -> Dict:
        """Get statistical summary of cluster."""
        if not self.repos:
            return {"count": 0, "avg": 0, "min": 0, "max": 0}

        scores = [r.score for r in self.repos]
        return {
            "count": len(scores),
            "avg": sum(scores) / len(scores),
            "min": min(scores),
            "max": max(scores),
            "median": sorted(scores)[len(scores) // 2]
        }


@dataclass
class BenchmarkResult:
    """Result of benchmarking a repo against clusters."""
    repo_name: str
    score: int
    cluster: BenchmarkCluster
    percentile: float
    percentile_tier: str  # top10, top25, top50, bottom50
    trend: Optional[Tuple[int, float]] = None  # (previous_score, trend_direction)
    recommendations: List[str] = field(default_factory=list)


class BenchmarkingEngine:
    """Manages repository clustering and competitive benchmarking."""

    def __init__(self):
        self.clusters: Dict[str, BenchmarkCluster] = {}
        self.repos: Dict[str, RepoMetadata] = {}
        self.history: Dict[str, List[Tuple[datetime, int]]] = {}

    def create_cluster(self, language: str, framework: Optional[str] = None,
                      project_size: str = "medium") -> BenchmarkCluster:
        """Create a new benchmark cluster."""
        cluster_id = f"{language}_{framework or 'generic'}_{project_size}".lower()
        cluster = BenchmarkCluster(
            cluster_id=cluster_id,
            language=language,
            framework=framework,
            project_size=project_size
        )
        self.clusters[cluster_id] = cluster
        return cluster

    def register_repo(self, repo: RepoMetadata, cluster_id: str) -> None:
        """Register a repository in a cluster."""
        if cluster_id not in self.clusters:
            raise ValueError(f"Cluster {cluster_id} not found")

        self.repos[f"{repo.owner}/{repo.repo_name}"] = repo
        self.clusters[cluster_id].add_repo(repo)

        # Initialize history
        repo_key = f"{repo.owner}/{repo.repo_name}"
        if repo_key not in self.history:
            self.history[repo_key] = []
        self.history[repo_key].append((repo.last_updated, repo.score))

    def benchmark_repo(self, repo_name: str, score: int, language: str,
                      framework: Optional[str] = None,
                      project_size: str = "medium") -> BenchmarkResult:
        """Benchmark a repository against its cluster."""
        cluster_id = f"{language}_{framework or 'generic'}_{project_size}".lower()

        if cluster_id not in self.clusters:
            self.create_cluster(language, framework, project_size)

        cluster = self.clusters[cluster_id]
        percentile = cluster.get_percentile(score)

        # Determine tier
        if percentile >= 90:
            tier = "top10"
        elif percentile >= 75:
            tier = "top25"
        elif percentile >= 50:
            tier = "top50"
        else:
            tier = "bottom50"

        result = BenchmarkResult(
            repo_name=repo_name,
            score=score,
            cluster=cluster,
            percentile=percentile,
            percentile_tier=tier
        )

        # Generate recommendations
        cluster_stats = cluster.get_stats()
        if score < cluster_stats["avg"]:
            gap = cluster_stats["avg"] - score
            result.recommendations.append(
                f"Your repo is {gap:.0f} points below cluster average. "
                f"Focus on: testing, documentation, architecture"
            )
        else:
            result.recommendations.append(
                f"Your repo is in top {100-percentile:.0f}% of similar projects"
            )

        return result

    def get_trend(self, repo_key: str) -> Optional[Tuple[float, str]]:
        """Get score trend for a repository."""
        if repo_key not in self.history or len(self.history[repo_key]) < 2:
            return None

        history = sorted(self.history[repo_key], key=lambda x: x[0])
        prev_score = history[-2][1]
        curr_score = history[-1][1]

        if curr_score > prev_score:
            direction = "↑ improving"
        elif curr_score < prev_score:
            direction = "↓ declining"
        else:
            direction = "→ stable"

        change = curr_score - prev_score
        return (change, direction)

    def get_org_stats(self, language: Optional[str] = None) -> Dict:
        """Get organization-wide statistics."""
        filtered_repos = [
            r for r in self.repos.values()
            if language is None or r.language == language
        ]

        if not filtered_repos:
            return {"count": 0, "avg": 0}

        scores = [r.score for r in filtered_repos]
        return {
            "count": len(filtered_repos),
            "avg": sum(scores) / len(scores),
            "min": min(scores),
            "max": max(scores),
            "by_language": self._group_by_language(filtered_repos)
        }

    def _group_by_language(self, repos: List[RepoMetadata]) -> Dict[str, float]:
        """Group repos by language and compute averages."""
        by_lang = {}
        for repo in repos:
            if repo.language not in by_lang:
                by_lang[repo.language] = []
            by_lang[repo.language].append(repo.score)

        return {
            lang: sum(scores) / len(scores)
            for lang, scores in by_lang.items()
        }

    def export_benchmark_report(self, repo_key: str) -> Dict:
        """Export a benchmark report for a repository."""
        if repo_key not in self.repos:
            raise ValueError(f"Repository {repo_key} not found")

        repo = self.repos[repo_key]
        cluster = self._find_cluster_for_repo(repo)
        result = self.benchmark_repo(
            repo.repo_name, repo.score, repo.language, repo.framework
        )

        trend = self.get_trend(repo_key)
        org_stats = self.get_org_stats(repo.language)

        return {
            "repo": repo_key,
            "score": repo.score,
            "percentile": result.percentile,
            "tier": result.percentile_tier,
            "cluster_stats": cluster.get_stats(),
            "trend": trend,
            "org_stats": org_stats,
            "recommendations": result.recommendations
        }

    def _find_cluster_for_repo(self, repo: RepoMetadata) -> Optional[BenchmarkCluster]:
        """Find the cluster a repo belongs to."""
        cluster_id = f"{repo.language}_{repo.framework or 'generic'}_{repo.project_size}".lower()
        return self.clusters.get(cluster_id)
