"""
Braxis Smart Triggering Logic
Detects meaningful changes and decides when to regenerate context files.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set
import subprocess
from braxis_config import BraxisConfig, GenerationConfig


@dataclass
class ChangeMetrics:
    """Metrics about code changes."""
    total_lines_changed: int = 0
    files_changed: List[str] = None
    meaningful_files_changed: List[str] = None
    is_trivial_change: bool = False
    change_reason: str = ""

    def __post_init__(self):
        if self.files_changed is None:
            self.files_changed = []
        if self.meaningful_files_changed is None:
            self.meaningful_files_changed = []


class SmartTrigger:
    """Intelligently decides when context files should be regenerated."""

    MEANINGFUL_FILE_PATTERNS = [
        "src/",
        "tests/",
        "setup.py",
        "pyproject.toml",
        "package.json",
        "requirements.txt",
        "Makefile",
        ".py",
        ".ts",
        ".js",
        ".java",
        ".go",
        ".rs",
    ]

    TRIVIAL_CHANGE_PATTERNS = [
        ".md",  # Markdown files (except specific ones)
        ".txt",  # Text files
        ".json",  # Config files that aren't meaningful
        "comment",
        "TODO",
        "FIXME",
        "whitespace",
    ]

    def __init__(self, config: Optional[BraxisConfig] = None):
        self.config = config or BraxisConfig()
        self.gen_config = self.config.generation

    def should_regenerate(
        self,
        changed_files: List[str],
        repo_path: str = ".",
        git_base: str = "origin/main",
    ) -> tuple[bool, ChangeMetrics]:
        """
        Determine if context files should be regenerated.

        Args:
            changed_files: List of changed file paths
            repo_path: Repository root path
            git_base: Git base branch for comparison

        Returns:
            Tuple of (should_regenerate, metrics)
        """
        if not changed_files:
            return False, ChangeMetrics(
                is_trivial_change=True,
                change_reason="No files changed"
            )

        # Filter for meaningful changes
        meaningful_files = self._filter_meaningful_files(changed_files)

        if not meaningful_files:
            return False, ChangeMetrics(
                is_trivial_change=True,
                files_changed=changed_files,
                change_reason="Only trivial files changed (comments, docs, etc.)"
            )

        # Check lines changed if threshold enabled
        if self.gen_config.min_change_threshold > 0:
            lines_changed = self._count_lines_changed(meaningful_files, repo_path, git_base)

            if lines_changed < self.gen_config.min_change_threshold:
                return False, ChangeMetrics(
                    total_lines_changed=lines_changed,
                    files_changed=changed_files,
                    meaningful_files_changed=meaningful_files,
                    is_trivial_change=True,
                    change_reason=f"Below minimum threshold ({lines_changed} < {self.gen_config.min_change_threshold})"
                )

        return True, ChangeMetrics(
            total_lines_changed=self._count_lines_changed(meaningful_files, repo_path, git_base),
            files_changed=changed_files,
            meaningful_files_changed=meaningful_files,
            change_reason="Meaningful code changes detected"
        )

    def should_commit_changes(
        self,
        old_content: dict[str, str],
        new_content: dict[str, str],
    ) -> bool:
        """
        Check if generated content has actually changed.
        Avoids committing if outputs are identical.
        """
        if set(old_content.keys()) != set(new_content.keys()):
            return True

        for key in old_content:
            if old_content[key] != new_content[key]:
                return True

        return False

    def _filter_meaningful_files(self, files: List[str]) -> List[str]:
        """Filter files to only meaningful ones for code changes."""
        meaningful = []
        exclude_patterns = self.gen_config.exclude_patterns

        for file in files:
            # Check if file matches exclude patterns
            if any(pattern in file for pattern in exclude_patterns):
                continue

            # Check if file is meaningful
            if any(pattern in file for pattern in self.MEANINGFUL_FILE_PATTERNS):
                meaningful.append(file)

        return meaningful

    def _count_lines_changed(
        self,
        files: List[str],
        repo_path: str = ".",
        git_base: str = "origin/main",
    ) -> int:
        """Count total lines changed in meaningful files."""
        if not files:
            return 0

        try:
            result = subprocess.run(
                ["git", "diff", git_base, "HEAD", "--", *files],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return 0

            # Count added and removed lines
            lines_count = 0
            for line in result.stdout.split("\n"):
                if line.startswith("+") or line.startswith("-"):
                    if not line.startswith("+++") and not line.startswith("---"):
                        lines_count += 1

            return lines_count
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # If git diff fails, be conservative and say there are changes
            return max(1, self.gen_config.min_change_threshold)

    @staticmethod
    def get_changed_files(
        repo_path: str = ".",
        git_base: str = "origin/main",
    ) -> List[str]:
        """Get list of changed files between base and current."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", git_base, "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return []

            return [f for f in result.stdout.strip().split("\n") if f]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []


class ChangeDetector:
    """Detects meaningful vs trivial changes in code."""

    @staticmethod
    def is_whitespace_only(diff: str) -> bool:
        """Check if diff contains only whitespace changes."""
        for line in diff.split("\n"):
            if line.startswith("+") or line.startswith("-"):
                if not line.startswith("+++") and not line.startswith("---"):
                    content = line[1:].strip()
                    if content and not content.startswith("#"):
                        return False
        return True

    @staticmethod
    def extract_meaningful_changes(diff: str) -> List[str]:
        """Extract meaningful changes from a diff."""
        meaningful = []
        current_file = None

        for line in diff.split("\n"):
            if line.startswith("diff --git"):
                current_file = line.split()[-1]
            elif (line.startswith("+") or line.startswith("-")) and not line.startswith("+++") and not line.startswith("---"):
                content = line[1:].strip()
                if content and not content.startswith("#"):
                    if current_file:
                        meaningful.append(f"{current_file}: {content[:80]}")

        return meaningful[:5]  # Return top 5 meaningful changes
