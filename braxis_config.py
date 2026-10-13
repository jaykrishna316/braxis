"""
Braxis Configuration File Handler
Loads and validates .braxis.yml configuration files.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class ContextConfig:
    """Configuration for context file generation."""
    output_format: str = "markdown"  # markdown, json, html
    code_block_style: str = "python-fenced"  # python-fenced, markdown, html
    include_architecture: bool = True
    include_testing: bool = True
    include_conventions: bool = True
    max_code_examples: int = 3
    code_snippet_max_lines: int = 20


@dataclass
class GenerationConfig:
    """Configuration for generation behavior."""
    include_test_metrics: bool = True
    min_change_threshold: int = 5  # lines changed
    skip_trivial_changes: bool = True
    auto_stage_changes: bool = True
    exclude_patterns: List[str] = field(default_factory=list)


@dataclass
class AutomationConfig:
    """Configuration for GitHub Actions and CI/CD."""
    github_paths: List[str] = field(default_factory=lambda: ["src/", "tests/", "setup.py", "pyproject.toml"])
    github_branches: List[str] = field(default_factory=lambda: ["main", "develop", "master"])
    exclude_patterns: List[str] = field(default_factory=lambda: ["__pycache__", ".venv", "node_modules"])
    auto_commit: bool = True
    auto_comment_prs: bool = True
    commit_message: str = "chore: regenerate context files"


@dataclass
class ScoringConfig:
    """Configuration for AI readiness scoring."""
    enable_scoring: bool = True
    weight_architecture: float = 1.0
    weight_testing: float = 1.0
    weight_dependencies: float = 1.0
    weight_conventions: float = 1.0
    weight_entry_points: float = 1.0
    weight_security: float = 1.0
    weight_build: float = 1.0
    weight_documentation: float = 1.0


@dataclass
class BraxisConfig:
    """Master configuration class for Braxis."""
    context: ContextConfig = field(default_factory=ContextConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    automation: AutomationConfig = field(default_factory=AutomationConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    version: str = "1.1"

    @classmethod
    def load(cls, config_path: str = ".braxis.yml") -> "BraxisConfig":
        """Load configuration from .braxis.yml file."""
        path = Path(config_path)

        if not path.exists():
            return cls()  # Return defaults

        try:
            if yaml is None:
                return cls._load_from_json(path)
            return cls._load_from_yaml(path)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            return cls()

    @classmethod
    def _load_from_yaml(cls, path: Path) -> "BraxisConfig":
        """Load configuration from YAML file."""
        if yaml is None:
            raise ImportError("PyYAML is required to load .braxis.yml files")

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        return cls._parse_config(data)

    @classmethod
    def _load_from_json(cls, path: Path) -> "BraxisConfig":
        """Load configuration from JSON file (fallback if YAML unavailable)."""
        with open(path) as f:
            data = json.load(f)

        return cls._parse_config(data)

    @classmethod
    def _parse_config(cls, data: Dict[str, Any]) -> "BraxisConfig":
        """Parse configuration dictionary."""
        context_data = data.get("context", {})
        generation_data = data.get("generation", {})
        automation_data = data.get("automation", {})
        scoring_data = data.get("scoring", {})

        return cls(
            context=ContextConfig(**{k: v for k, v in context_data.items() if hasattr(ContextConfig, k)}),
            generation=GenerationConfig(**{k: v for k, v in generation_data.items() if hasattr(GenerationConfig, k)}),
            automation=AutomationConfig(**{k: v for k, v in automation_data.items() if hasattr(AutomationConfig, k)}),
            scoring=ScoringConfig(**{k: v for k, v in scoring_data.items() if hasattr(ScoringConfig, k)}),
        )

    def save(self, config_path: str = ".braxis.yml") -> None:
        """Save configuration to file."""
        path = Path(config_path)

        data = {
            "context": self._dataclass_to_dict(self.context),
            "generation": self._dataclass_to_dict(self.generation),
            "automation": self._dataclass_to_dict(self.automation),
            "scoring": self._dataclass_to_dict(self.scoring),
            "version": self.version,
        }

        if yaml is not None:
            with open(path, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
        else:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)

    @staticmethod
    def _dataclass_to_dict(obj: Any) -> Dict[str, Any]:
        """Convert dataclass to dictionary."""
        from dataclasses import asdict
        return asdict(obj)
