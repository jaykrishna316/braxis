#!/usr/bin/env python3
"""
Braxis - Auto-generate AI agent context files.
Keep AGENTS.md, CLAUDE.md, .cursorrules, and .agentic-config.json in sync with your codebase.
"""
import os
import sys
import json
import argparse
import tempfile
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import hashlib
import re
import xml.etree.ElementTree as ET

__version__ = "1.3.0"


class LocalPreferencesManager:
    """Manages .agents.local.md for team customizations."""

    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.local_prefs_file = self.project_path / ".agents.local.md"

    def load_preferences(self):
        """Load local preferences if they exist."""
        if self.local_prefs_file.exists():
            return self.local_prefs_file.read_text()
        return None

    def merge_with_generated(self, generated_content):
        """Merge local preferences into generated content."""
        preferences = self.load_preferences()
        if not preferences:
            return generated_content

        lines = generated_content.split('\n')
        pref_lines = preferences.split('\n')

        result = []
        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for @override markers in preferences
            override_section = self._find_override_section(line, pref_lines)
            if override_section:
                # Replace section with override
                section_end = self._find_section_end(i, lines)
                result.extend(override_section)
                i = section_end
            else:
                result.append(line)
                i += 1

        return '\n'.join(result)

    def _find_override_section(self, header, pref_lines):
        """Find override section for a header."""
        # Extract header text
        if header.startswith('## '):
            header_text = header[3:].strip()

            # Search for @override in preferences
            for i, line in enumerate(pref_lines):
                if f"@override: {header_text}" in line:
                    # Get content until next override or end
                    result = []
                    j = i + 1
                    while j < len(pref_lines) and not pref_lines[j].startswith('@override:'):
                        result.append(pref_lines[j])
                        j += 1
                    return [header] + [l for l in result if l.strip()]

        return None

    def _find_section_end(self, start_idx, lines):
        """Find end of current section."""
        for i in range(start_idx + 1, len(lines)):
            if lines[i].startswith('## '):
                return i
        return len(lines)

    def create_template(self):
        """Create a template .agents.local.md file."""
        template = """# .agents.local.md

This file contains team-specific overrides for generated AGENTS.md.
Sections marked with @override: will replace the generated content.

@override: Code Style
Our team uses:
- 4-space indents
- No semicolons (JavaScript)
- PEP 8 for Python

@override: Testing Strategy
All functions must have:
- Unit tests with >80% coverage
- Integration tests for APIs
- E2E tests for critical paths

@override: Error Handling
- Always log errors with context
- Use structured logging (JSON)
- Include stack traces in development

Note: This file is generated as a template and can be customized.
Changes persist across `braxis generate` runs.
"""
        return template


class MonorepoDetectorEnhanced:
    """Enhanced monorepo detection for v1.3 - supports 8 technologies."""

    def __init__(self, project_path):
        self.project_path = Path(project_path)

    def detect_gradle_multi_module(self):
        """Detect Gradle multi-module projects."""
        settings_gradle = self.project_path / "settings.gradle"
        settings_gradle_kts = self.project_path / "settings.gradle.kts"

        content = None
        if settings_gradle.exists():
            content = settings_gradle.read_text()
        elif settings_gradle_kts.exists():
            content = settings_gradle_kts.read_text()
        else:
            return None

        modules = []
        for line in content.split('\n'):
            match = re.search(r"include\s+['\"]([^'\"]+)['\"]", line)
            if match:
                modules.append(match.group(1))

        if modules:
            return {
                "type": "gradle",
                "modules": modules,
                "count": len(modules)
            }
        return None

    def detect_rust_workspaces(self):
        """Detect Rust workspaces."""
        cargo_toml = self.project_path / "Cargo.toml"
        if not cargo_toml.exists():
            return None

        content = cargo_toml.read_text()
        if "[workspace]" not in content:
            return None

        # Parse members
        members = []
        in_workspace = False
        for line in content.split('\n'):
            if '[workspace]' in line:
                in_workspace = True
            elif line.startswith('['):
                in_workspace = False
            elif in_workspace and 'members' in line:
                # Extract from members = ["pkg1", "pkg2"]
                match = re.search(r'members\s*=\s*\[(.*?)\]', content, re.DOTALL)
                if match:
                    member_str = match.group(1)
                    members = [m.strip().strip('"') for m in member_str.split(',') if m.strip()]
                break

        if members:
            return {
                "type": "rust-workspace",
                "members": members,
                "count": len(members)
            }
        return None

    def detect_maven_multi_module(self):
        """Detect Maven multi-module projects."""
        pom_xml = self.project_path / "pom.xml"
        if not pom_xml.exists():
            return None

        try:
            content = pom_xml.read_text()
            if "<modules>" not in content:
                return None

            root = ET.fromstring(content)
            ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

            # Try with namespace first
            modules = root.findall('.//m:module', ns)
            if not modules:
                # Try without namespace
                modules = root.findall('.//module')

            module_names = [m.text.strip() for m in modules if m.text]

            if module_names:
                return {
                    "type": "maven-multi-module",
                    "modules": module_names,
                    "count": len(module_names)
                }
        except Exception:
            pass

        return None

    def detect_go_modules(self):
        """Detect Go module structure."""
        go_mod = self.project_path / "go.mod"
        if not go_mod.exists():
            return None

        # Detect subdirectories with go.mod files
        subdirs = []
        for subdir in self.project_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                if (subdir / "go.mod").exists():
                    subdirs.append(subdir.name)

        if subdirs:
            return {
                "type": "go-modules",
                "modules": subdirs,
                "count": len(subdirs)
            }

        # Single module
        return {
            "type": "go-modules",
            "modules": ["root"],
            "count": 1
        }

    def detect_all(self):
        """Try all detectors in order."""
        detectors = [
            self.detect_go_modules,
            self.detect_gradle_multi_module,
            self.detect_rust_workspaces,
            self.detect_maven_multi_module,
        ]

        for detector in detectors:
            result = detector()
            if result:
                return result

        return None


class GitHubActionsGenerator:
    """Generate GitHub Actions workflow for braxis auto-sync."""

    def __init__(self, project_path):
        self.project_path = Path(project_path)

    def generate_workflow(self):
        """Create .github/workflows/braxis-sync.yml."""
        workflow = """name: Braxis Context Auto-Sync

on:
  push:
    branches: [main, develop, master]
    paths:
      - '**.py'
      - '**.js'
      - '**.ts'
      - '**.tsx'
      - '**.jsx'
      - '**.java'
      - '**.rs'
      - '**.go'
      - 'package.json'
      - 'pyproject.toml'
      - 'setup.py'
      - 'Cargo.toml'
      - 'go.mod'
      - 'pom.xml'
      - 'build.gradle'
      - '.github/workflows/braxis-sync.yml'

jobs:
  braxis-sync:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - run: pip install -q braxis

      - run: braxis generate

      - name: Check for changes
        id: changes
        run: |
          if git diff --quiet; then
            echo "has_changes=false" >> $GITHUB_OUTPUT
          else
            echo "has_changes=true" >> $GITHUB_OUTPUT
            git diff --stat
          fi

      - name: Create Pull Request
        if: steps.changes.outputs.has_changes == 'true'
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'chore: regenerate braxis context files'
          title: 'chore: update AI agent context files'
          body: |
            Automated context file regeneration triggered by code changes.

            Generated files:
            - AGENTS.md - Universal agent instructions
            - CLAUDE.md - Claude Code optimized
            - .cursorrules - Cursor IDE rules
            - .agentic-config.json - Machine-readable metadata

            Run `braxis score` locally to see the readiness analysis.
          branch: braxis/auto-update
          delete-branch: true
          labels: 'chore,automated'
"""
        return workflow

    def write_workflow(self):
        """Write workflow file to disk."""
        workflow_dir = self.project_path / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)

        workflow_file = workflow_dir / "braxis-sync.yml"
        workflow_file.write_text(self.generate_workflow())

        return workflow_file


class ReadinessBadgeGenerator:
    """Generate agent readiness badge for README."""

    @staticmethod
    def generate_badge_markdown(score, tier):
        """Generate badge markdown with color based on tier."""
        color_map = {
            "Agent-Optimized": "brightgreen",
            "AI-Native-Plus": "green",
            "AI-Native": "yellowgreen",
            "Agent-Aware": "yellow",
            "Not Ready": "red"
        }

        color = color_map.get(tier, "blue")

        badge = f"""[![Braxis Agent Readiness](https://img.shields.io/badge/braxis-{score}%2F100-{color})](https://github.com/jaykrishna316/braxis)"""

        return badge


class TestingPatternDetector:
    """Detect and categorize testing patterns - Phase 2."""

    def __init__(self, project_path, files):
        self.project_path = Path(project_path)
        self.files = files

    TEST_CATEGORIES = {
        "unit": ["test_unit_", "*_unit.py", "*.unit.js", "*_test.rs", "*_unit.go"],
        "integration": ["test_integration_", "*_integration.py", "*.integration.js", "*_integration.rs"],
        "e2e": ["cypress/", "playwright/", "e2e/", "test_e2e_", "tests/e2e"],
        "performance": ["asv_bench/", "benchmarks/", "*_bench.go", "criterion/", "*_benchmark.rs"],
        "visual": ["visual_regression/", "screenshot_tests/", "percy/"],
        "fuzz": ["fuzz_", "quickcheck", "proptest", "cargo-fuzz/"]
    }

    def detect_test_types(self):
        """Categorize tests in codebase."""
        detected = defaultdict(list)

        for test_type, patterns in self.TEST_CATEGORIES.items():
            for pattern in patterns:
                for file_path in self.files:
                    if pattern in str(file_path):
                        detected[test_type].append(str(file_path))

        return dict(detected)

    def recommend_testing_strategy(self, project_category="general"):
        """Recommend coverage targets based on project type."""
        strategies = {
            "backend": {
                "unit_target": "70%",
                "integration_target": "40%",
                "e2e_target": "20%",
                "emphasis": "Database and API testing"
            },
            "frontend": {
                "unit_target": "60%",
                "integration_target": "30%",
                "e2e_target": "40%",
                "visual_target": "Important",
                "emphasis": "Component and user flow testing"
            },
            "data_science": {
                "unit_target": "50%",
                "performance_target": "Essential",
                "emphasis": "Benchmark and data validation testing"
            },
            "general": {
                "unit_target": "60%",
                "integration_target": "30%",
                "e2e_target": "20%",
                "emphasis": "Core functionality testing"
            }
        }

        return strategies.get(project_category, strategies["general"])


class ConventionDetector:
    """Detect language-specific code conventions - Phase 2."""

    LANGUAGE_CONVENTIONS = {
        "python": {
            "functions": "snake_case",
            "classes": "PascalCase",
            "constants": "SCREAMING_SNAKE_CASE",
            "modules": "lowercase_with_underscores",
            "error_handling": "try/except",
            "async": "asyncio",
            "validation": "pydantic or custom validators"
        },
        "javascript": {
            "functions": "camelCase",
            "classes": "PascalCase",
            "constants": "SCREAMING_SNAKE_CASE",
            "variables": "camelCase",
            "error_handling": "throw Error or try/catch",
            "async": "async/await",
            "validation": "schemas or custom validators"
        },
        "typescript": {
            "functions": "camelCase",
            "classes": "PascalCase",
            "constants": "SCREAMING_SNAKE_CASE",
            "interfaces": "IPascalCase",
            "error_handling": "throw Error or try/catch",
            "async": "async/await with types",
            "validation": "zod, ts-guard, or similar"
        },
        "rust": {
            "functions": "snake_case",
            "structs": "PascalCase",
            "constants": "SCREAMING_SNAKE_CASE",
            "traits": "PascalCase",
            "error_handling": "Result<T, E>",
            "async": "async/await with tokio",
            "validation": "custom validators or crates"
        },
        "go": {
            "functions": "CamelCase (exported) or camelCase (private)",
            "interfaces": "rInterface pattern (Reader, Writer)",
            "constants": "CamelCase",
            "error_handling": "explicit err != nil checks",
            "async": "goroutines and channels",
            "validation": "explicit checks or libraries"
        }
    }

    def __init__(self, language):
        self.language = language

    def get_conventions(self):
        """Get conventions for detected language."""
        return self.LANGUAGE_CONVENTIONS.get(self.language, {})

    def generate_convention_guide(self):
        """Generate convention guide for language."""
        conventions = self.get_conventions()
        if not conventions:
            return None

        guide = f"""## {self.language.title()} Conventions

### Naming
- **Functions**: {conventions.get('functions', 'N/A')}
- **Classes/Types**: {conventions.get('classes', 'N/A')}
- **Constants**: {conventions.get('constants', 'N/A')}

### Error Handling
{conventions.get('error_handling', 'N/A')}

### Async Patterns
{conventions.get('async', 'N/A')}

### Validation
{conventions.get('validation', 'N/A')}
"""
        return guide


class SecurityPatternDetector:
    """Detect security practices and patterns - Phase 2."""

    def __init__(self, project_path, files):
        self.project_path = Path(project_path)
        self.files = files

    def detect_security_tooling(self):
        """Find security scanning tools."""
        tooling = {
            "dependency_scanning": self._find_dependency_scanner(),
            "secrets_scanning": self._find_secrets_scanner(),
            "sbom_generation": self._find_sbom_tool(),
            "sast": self._find_sast_tool(),
            "container_scanning": self._find_container_scanner()
        }
        return {k: v for k, v in tooling.items() if v}

    def _find_dependency_scanner(self):
        """Detect dependency scanning tools."""
        for file_path in self.files:
            fname = file_path.name
            if 'dependabot' in str(file_path):
                return "Dependabot"
            if fname == 'renovate.json':
                return "Renovate"
            if 'safety' in str(file_path).lower():
                return "Safety"
        return None

    def _find_secrets_scanner(self):
        """Detect secrets scanning."""
        for file_path in self.files:
            if 'git-secrets' in str(file_path) or 'truffleHog' in str(file_path):
                return "Git-Secrets/TruffleHog"
        return None

    def _find_sbom_tool(self):
        """Detect SBOM generation."""
        for file_path in self.files:
            if 'cyclonedx' in str(file_path).lower() or 'syft' in str(file_path).lower():
                return "CycloneDX/Syft"
        return None

    def _find_sast_tool(self):
        """Detect SAST tools."""
        for file_path in self.files:
            fname = file_path.name.lower()
            if 'codeql' in fname:
                return "CodeQL"
            if 'snyk' in fname:
                return "Snyk"
        return None

    def _find_container_scanner(self):
        """Detect container scanning."""
        for file_path in self.files:
            if 'trivy' in str(file_path) or 'grype' in str(file_path):
                return "Trivy/Grype"
        return None

    def generate_security_recommendations(self):
        """Generate security recommendations based on detected patterns."""
        tooling = self.detect_security_tooling()

        recommendations = []

        if not tooling.get('dependency_scanning'):
            recommendations.append("✗ Add dependency scanning (Dependabot or Renovate)")
        else:
            recommendations.append(f"✓ Dependency scanning: {tooling['dependency_scanning']}")

        if not tooling.get('secrets_scanning'):
            recommendations.append("✗ Add secrets scanning (git-secrets or TruffleHog)")
        else:
            recommendations.append(f"✓ Secrets scanning: {tooling['secrets_scanning']}")

        if not tooling.get('sast'):
            recommendations.append("✗ Add SAST scanning (CodeQL or Snyk)")
        else:
            recommendations.append(f"✓ SAST scanning: {tooling['sast']}")

        return recommendations


class BraxisAnalyzer:
    """Analyzes a codebase and generates agent context files."""

    LANGUAGE_EXTENSIONS = {
        'python': ['.py'],
        'javascript': ['.js', '.jsx'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'go': ['.go'],
        'rust': ['.rs'],
        'c': ['.c', '.h'],
        'cpp': ['.cpp', '.cc', '.cxx', '.h', '.hpp'],
        'csharp': ['.cs'],
        'php': ['.php'],
        'ruby': ['.rb'],
        'swift': ['.swift'],
        'kotlin': ['.kt'],
        'scala': ['.scala'],
        'r': ['.R', '.r'],
        'sql': ['.sql'],
    }
    TEST_PATTERNS = ['test_', '_test.', 'spec_', '.spec.', 'tests/', 'test/']
    BUILD_FILES = ['package.json', 'pyproject.toml', 'setup.py', 'Makefile', 'build.gradle', 'pom.xml', 'Cargo.toml']
    CONFIG_FILES = ['.env', '.env.example', 'config.json', 'settings.py', 'config.yaml']

    def __init__(self, project_path='.'):
        self.project_path = self._validate_project_path(project_path)
        self.files = []
        self.languages = defaultdict(int)
        self.test_files = []
        self.config_files = []
        self.build_files = []
        self.conventions = defaultdict(int)
        self.critical_files = []
        self.score_breakdown = {}
        self.tier = "Not Ready"
        # Contributing guide detection
        self.contributing_guide = {'exists': False, 'path': None, 'content': None}
        # v1.1 features
        self.monorepo_type = None
        self.monorepo_subsystems = []
        self.mcp_servers = []
        # v1.3 features
        self.local_preferences_manager = LocalPreferencesManager(project_path)
        self.local_preferences = None
        self.testing_patterns = {}
        self.convention_guides = {}
        self.security_tooling = {}
        self.security_recommendations = []
        # v1.3 enhanced monorepo detection
        self.enhanced_monorepo_info = None

    def _validate_project_path(self, project_path):
        """Validate and normalize project path."""
        if not project_path:
            raise ValueError("Project path cannot be empty")
        path = Path(project_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Project path is not a directory: {project_path}")
        return path

    def _get_project_hash(self):
        """Generate unique hash for project for tracking."""
        project_str = str(self.project_path).encode()
        return hashlib.md5(project_str).hexdigest()[:8]

    def _get_history_file(self):
        """Get path to score history file."""
        home = Path.home()
        history_dir = home / '.braxis' / 'history'
        history_dir.mkdir(parents=True, exist_ok=True)
        return history_dir / f"scores_{self._get_project_hash()}.json"

    def _save_score_to_history(self):
        """Save current score to history."""
        history_file = self._get_history_file()
        history = []

        if history_file.exists():
            try:
                history = json.loads(history_file.read_text())
            except (json.JSONDecodeError, IOError):
                history = []

        history.append({
            "timestamp": datetime.now().isoformat(),
            "score": self.total_score,
            "tier": self.tier,
            "breakdown": self.score_breakdown
        })

        history_file.write_text(json.dumps(history, indent=2))

    def get_score_history(self, limit=None):
        """Get score history for this project."""
        history_file = self._get_history_file()
        if not history_file.exists():
            return []

        try:
            history = json.loads(history_file.read_text())
            return history[-limit:] if limit else history
        except (json.JSONDecodeError, IOError):
            return []

    def show_score_trends(self):
        """Show score trends over time."""
        history = self.get_score_history()
        if not history:
            print("No score history available yet. Run 'braxis score' to start tracking.")
            return

        print(f"\n{'='*60}")
        print(f"Score History for {self.project_path.name}")
        print(f"{'='*60}\n")

        for i, entry in enumerate(history, 1):
            timestamp = entry['timestamp'][:10]  # Date only
            score = entry['score']
            tier = entry['tier']
            print(f"{i}. {timestamp} - {score}/100 ({tier})")

        if len(history) > 1:
            first_score = history[0]['score']
            latest_score = history[-1]['score']
            change = latest_score - first_score
            direction = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            print(f"\nTrend: {direction} {abs(change):+d} points")

        print(f"\n{'='*60}\n")

    def analyze(self):
        """Analyze the project."""
        self._scan_files()
        self._detect_languages()
        self._detect_build_system()
        self._detect_test_framework()
        self._detect_conventions()
        self._identify_critical_files()
        # Detect project structure, Python version, and repository URL
        self.project_structure = self._detect_project_structure()
        self.python_version = self._detect_python_version()
        self.repository_url = self._detect_repository_url()
        # Detect contributing guide
        self.contributing_guide = self._detect_contributing_guide()
        # v1.1: Detect monorepo and MCP
        self.monorepo_type = self.detect_monorepo_type()
        if self.monorepo_type:
            self.monorepo_subsystems = self.get_monorepo_subsystems()
        self.mcp_servers = self.detect_mcp_servers()
        # v1.3: Phase 1 & 2 features
        self._detect_enhanced_monorepo()
        self._detect_testing_patterns()
        self._detect_conventions_per_language()
        self._detect_security_patterns()
        self.local_preferences = self.local_preferences_manager.load_preferences()
        self._calculate_score()

    def _scan_files(self):
        """Scan all files in project."""
        ignore_dirs = {'.git', '.venv', 'node_modules', '__pycache__', 'dist', 'build', '.idea', '.vscode'}
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                file_path = Path(root) / file
                self.files.append(file_path)
                if any(pattern in str(file_path) for pattern in self.TEST_PATTERNS):
                    self.test_files.append(file_path)
                if file in self.CONFIG_FILES:
                    self.config_files.append(file_path)
                if file in self.BUILD_FILES:
                    self.build_files.append(file_path)

    def _detect_languages(self):
        """Detect languages used in project."""
        for file_path in self.files:
            ext = file_path.suffix.lower()
            for lang, exts in self.LANGUAGE_EXTENSIONS.items():
                if ext in exts:
                    self.languages[lang] += 1
                    break

    def _get_primary_language(self):
        """Get primary language for the project."""
        if not self.languages:
            return None
        # Return language with most files
        return max(self.languages.items(), key=lambda x: x[1])[0]

    def _detect_build_system(self):
        """Detect build system, prioritized by primary language."""
        primary_lang = self._get_primary_language()
        build_system = "Unknown"

        # Check build files by language priority
        if primary_lang == "go":
            if any('go.mod' in str(f) for f in self.build_files):
                build_system = "Go (go modules)"
            elif any('Makefile' in str(f) for f in self.build_files):
                build_system = "Go (Makefile)"
        elif primary_lang == "rust":
            if any('Cargo.toml' in str(f) for f in self.build_files):
                build_system = "Rust (cargo)"
        elif primary_lang == "python":
            if any('pyproject.toml' in str(f) for f in self.build_files):
                pyproject = self.project_path / 'pyproject.toml'
                if pyproject.exists():
                    try:
                        content = pyproject.read_text()
                        if 'build-system' in content:
                            if 'hatchling' in content.lower():
                                build_system = "Python (hatchling)"
                            elif 'pdm' in content.lower():
                                build_system = "Python (pdm)"
                            elif 'flit' in content.lower():
                                build_system = "Python (flit)"
                            elif 'poetry' in content.lower():
                                build_system = "Python (poetry)"
                            else:
                                build_system = "Python (setuptools)"
                        else:
                            build_system = "Python (pip)"
                    except (IOError, UnicodeDecodeError):
                        build_system = "Python (pip/setuptools)"
            elif any('setup.py' in str(f) for f in self.build_files):
                build_system = "Python (setuptools)"
        elif primary_lang in ["javascript", "typescript"]:
            if any('package.json' in str(f) for f in self.build_files):
                build_system = "npm/Node.js"
        elif primary_lang == "java":
            if any('pom.xml' in str(f) for f in self.build_files):
                build_system = "Java (Maven)"
            elif any('build.gradle' in str(f) for f in self.build_files):
                build_system = "Java (Gradle)"

        # Fallback: check any language-agnostic build files
        if build_system == "Unknown":
            if any('Makefile' in str(f) for f in self.build_files):
                build_system = "Makefile"
            elif any('go.mod' in str(f) for f in self.build_files):
                build_system = "Go (go modules)"
            elif any('package.json' in str(f) for f in self.build_files):
                build_system = "npm/Node.js"
            elif any('pyproject.toml' in str(f) for f in self.build_files):
                build_system = "Python (pip/setuptools)"
            elif any('Cargo.toml' in str(f) for f in self.build_files):
                build_system = "Rust (cargo)"
            elif any('pom.xml' in str(f) for f in self.build_files):
                build_system = "Java (Maven)"

        self.build_system = build_system

    def _detect_test_framework(self):
        """Detect test framework, language-aware."""
        test_frameworks = set()
        primary_lang = self._get_primary_language()

        # Language-specific test framework detection
        if primary_lang == "go":
            # Go uses built-in testing package
            test_frameworks.add("Go testing")
        elif primary_lang == "python":
            # Check pyproject.toml for pytest config
            pyproject = self.project_path / 'pyproject.toml'
            if pyproject.exists():
                try:
                    content = pyproject.read_text()
                    if '[tool.pytest' in content or 'pytest' in content:
                        test_frameworks.add('pytest')
                except (IOError, UnicodeDecodeError):
                    pass
            # Check for pytest imports in Python files
            content_samples = self._sample_file_contents(limit=20)
            for content in content_samples:
                if 'pytest' in content or 'from pytest' in content:
                    test_frameworks.add('pytest')
                    break
            # Default to pytest for Python
            if not test_frameworks and self.test_files:
                test_frameworks.add('pytest')
        elif primary_lang in ["javascript", "typescript"]:
            content_samples = self._sample_file_contents(limit=20)
            for content in content_samples:
                if 'jest' in content:
                    test_frameworks.add('Jest')
                    break
                elif 'mocha' in content or 'describe(' in content:
                    test_frameworks.add('Mocha')
                    break
            if not test_frameworks and self.test_files:
                test_frameworks.add('Jest')  # Default for JS/TS
        elif primary_lang == "ruby":
            content_samples = self._sample_file_contents(limit=20)
            for content in content_samples:
                if 'rspec' in content or 'describe' in content:
                    test_frameworks.add('RSpec')
                    break
            if not test_frameworks and self.test_files:
                test_frameworks.add('RSpec')
        elif primary_lang == "java":
            if any('pom.xml' in str(f) for f in self.build_files):
                test_frameworks.add('JUnit')
            else:
                test_frameworks.add('JUnit')  # Standard for Java

        # Fallback to generic detection if nothing found
        if not test_frameworks and self.test_files:
            content_samples = self._sample_file_contents(limit=20)
            for content in content_samples:
                if 'pytest' in content:
                    test_frameworks.add('pytest')
                elif 'jest' in content:
                    test_frameworks.add('Jest')
                elif 'mocha' in content:
                    test_frameworks.add('Mocha')
                elif 'rspec' in content:
                    test_frameworks.add('RSpec')
                elif 'junit' in content.lower():
                    test_frameworks.add('JUnit')

        self.test_frameworks = test_frameworks if test_frameworks else {"None detected"}

    def _detect_conventions(self):
        """Detect code conventions."""
        content_samples = self._sample_file_contents(limit=20)
        for content in content_samples:
            if 'async def' in content or 'await ' in content:
                self.conventions['async'] += 1
            if 'async function' in content or 'async (' in content:
                self.conventions['async'] += 1
            if 'try:' in content or 'except' in content:
                self.conventions['error_handling'] += 1
            if 'try {' in content or 'catch' in content:
                self.conventions['error_handling'] += 1
            if '->' in content or ': ' in content:
                self.conventions['type_hints'] += 1
            if 'interface ' in content or 'type ' in content:
                self.conventions['type_hints'] += 1
            if 'logger' in content or 'logging' in content:
                self.conventions['logging'] += 1
            if 'log.' in content or 'console.log' in content:
                self.conventions['logging'] += 1
            if 'validate' in content.lower() or 'schema' in content.lower():
                self.conventions['validation'] += 1

    def _detect_project_structure(self):
        """Detect project layout: src/ vs top-level package."""
        src_dir = self.project_path / 'src'
        if src_dir.exists() and src_dir.is_dir():
            # Has src/ directory
            src_contents = list(src_dir.iterdir())
            if src_contents:
                return 'src'

        # Check for top-level package directories (match primary language)
        primary_lang = max(self.languages.items(), key=lambda x: x[1])[0] if self.languages else None
        if primary_lang == 'python':
            # Look for Python packages at root
            for item in self.project_path.iterdir():
                if item.is_dir() and not item.name.startswith('.') and item.name not in ['tests', 'docs', 'build', 'dist', '__pycache__']:
                    if (item / '__init__.py').exists():
                        return 'top-level'
        elif primary_lang in ['javascript', 'typescript']:
            # Check for lib/ or src/ in JS projects
            if (self.project_path / 'lib').exists():
                return 'lib'
            if (self.project_path / 'src').exists():
                return 'src'

        return 'standard'

    def _identify_critical_files(self):
        """Identify critical files (main, entry points, etc)."""
        critical_names = ['main.py', 'app.py', 'server.py', 'index.js', 'main.js', 'app.js', 'main.rs', 'main.go', 'main.ts']
        for file_path in self.files:
            if file_path.name in critical_names or 'src/main' in str(file_path):
                self.critical_files.append(file_path)

    def _sample_file_contents(self, limit=20):
        """Sample file contents for convention detection."""
        samples = []
        code_files = [f for f in self.files if f.suffix in ['.py', '.js', '.ts', '.go', '.rs', '.java']]
        for file_path in code_files[:limit]:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    samples.append(f.read())
            except Exception:
                pass
        return samples

    def _detect_repository_url(self):
        """Detect repository URL from pyproject.toml or README."""
        pyproject = self.project_path / 'pyproject.toml'
        if pyproject.exists():
            try:
                content = pyproject.read_text()
                for line in content.split('\n'):
                    if 'homepage' in line.lower() or 'repository' in line.lower():
                        if 'github.com' in line:
                            # Extract URL
                            if '"' in line:
                                url = line.split('"')[1]
                            elif "'" in line:
                                url = line.split("'")[1]
                            else:
                                continue
                            if url.startswith('http'):
                                return url
            except (IOError, UnicodeDecodeError):
                pass

        # If not found, use project name as fallback
        return f"https://github.com/YOUR_ORG/{self.project_path.name}.git"

    def _detect_python_version(self):
        """Detect Python version requirement from pyproject.toml or setup.py."""
        pyproject = self.project_path / 'pyproject.toml'
        if pyproject.exists():
            try:
                content = pyproject.read_text()
                if 'requires-python' in content:
                    for line in content.split('\n'):
                        if 'requires-python' in line and '=' in line:
                            try:
                                version_part = line.split('=', 1)[1].strip()
                                # Remove trailing comma first, then quotes
                                version_part = version_part.rstrip(',').strip().strip('"').strip("'")
                                if version_part:
                                    return version_part
                            except IndexError:
                                pass
            except (IOError, UnicodeDecodeError):
                pass

        # Check setup.py
        setup_py = self.project_path / 'setup.py'
        if setup_py.exists():
            try:
                content = setup_py.read_text()
                if 'python_requires' in content:
                    for line in content.split('\n'):
                        if 'python_requires' in line and '=' in line:
                            try:
                                version_part = line.split('=', 1)[1].strip()
                                # Remove trailing comma first, then quotes
                                version_part = version_part.rstrip(',').strip().strip('"').strip("'")
                                if version_part:
                                    return version_part
                            except IndexError:
                                pass
            except (IOError, UnicodeDecodeError):
                pass

        return "3.9+"  # Default fallback

    def _detect_contributing_guide(self):
        """Detect and summarize contributing guide if present."""
        guide_candidates = [
            self.project_path / 'CONTRIBUTING.md',
            self.project_path / 'CONTRIBUTING.rst',
            self.project_path / 'docs' / 'CONTRIBUTING.md',
            self.project_path / 'docs' / 'CONTRIBUTING.rst',
            self.project_path / '.github' / 'CONTRIBUTING.md',
        ]

        for guide_path in guide_candidates:
            if guide_path.exists():
                try:
                    content = guide_path.read_text()
                    return {
                        'exists': True,
                        'path': str(guide_path.relative_to(self.project_path)),
                        'content': content
                    }
                except (IOError, UnicodeDecodeError):
                    pass

        return {'exists': False, 'path': None, 'content': None}

    def _extract_dco_requirement(self, content):
        """Check if project requires DCO sign-off."""
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in ['signed-off-by', 'git commit -s', 'dco', 'developer certificate'])

    def _extract_release_notes_requirement(self, content):
        """Check if project requires release-notes blocks."""
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in ['release-notes', 'release notes', 'changelog block'])

    def _extract_table_driven_tests(self, content):
        """Check if project uses table-driven tests."""
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in ['table-driven test', 'table driven test', 'test cases in a table'])

    def _extract_performance_requirements(self, content):
        """Check if project has special performance work requirements."""
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in ['benchmark', 'benchstat', 'performance work', 'perf'])

    def _extract_pr_title_format(self, content):
        """Extract PR title format if mentioned."""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'title' in line.lower() and ('format' in line.lower() or 'prefix' in line.lower() or ':' in line):
                for j in range(i+1, min(i+5, len(lines))):
                    if '```' in lines[j] or lines[j].strip().startswith('-') or lines[j].strip().startswith('`'):
                        return lines[j].strip()
        return None

    def _get_language_version_requirement(self):
        """Get language-appropriate version requirement."""
        primary_lang = self._get_primary_language()
        if primary_lang == "go":
            return "1.18+"
        elif primary_lang == "rust":
            return "1.56+"
        elif primary_lang == "java":
            return "11+"
        elif primary_lang == "ruby":
            return "2.7+"
        elif primary_lang in ["javascript", "typescript"]:
            return "16+"
        else:
            return self.python_version

    def _get_package_manager_recommendation(self):
        """Get language-appropriate package manager recommendation."""
        primary_lang = self._get_primary_language()
        if primary_lang == "go":
            return "go modules"
        elif primary_lang == "rust":
            return "cargo"
        elif primary_lang == "java":
            return "Maven or Gradle"
        elif primary_lang == "ruby":
            return "Bundler"
        elif primary_lang in ["javascript", "typescript"]:
            return "npm or yarn"
        else:
            return "pip or uv"

    def _get_development_commands(self, primary_lang):
        """Get language-appropriate development commands."""
        if primary_lang == "go":
            return """```bash
go build ./...            # Build project
go test ./...             # Run all tests
go test -v ./...          # Verbose test output
golangci-lint run         # Lint (if installed)
```

#### Code Quality
```bash
gofmt -w .                # Format code
go vet ./...              # Vet (static analysis)
```"""
        elif primary_lang == "rust":
            return """```bash
cargo build               # Build project
cargo test                # Run all tests
cargo test --verbose      # Verbose test output
```

#### Code Quality
```bash
cargo fmt                 # Format code
cargo clippy              # Lint with clippy
```"""
        elif primary_lang == "ruby":
            return """```bash
bundle exec rspec         # Run RSpec tests
bundle exec rspec spec/   # Run specific directory
bundle exec rspec -v      # Verbose output
```

#### Code Quality
```bash
bundle exec rubocop       # Lint with RuboCop
bundle exec rubocop -a    # Auto-fix issues
```"""
        elif primary_lang in ["javascript", "typescript"]:
            return """```bash
npm test                  # Run all tests
npm run test -- --watch   # Watch mode
npm run lint              # Lint code
```

#### Code Quality
```bash
npm run format            # Format code (prettier)
npm run lint -- --fix     # Auto-fix lint issues
```"""
        else:
            return """```bash
pytest                    # Run all tests
pytest tests/             # Run specific test directory
pytest -v                 # Verbose output with test names
pytest -x                 # Stop on first failure
coverage run -m pytest && coverage report  # With coverage report
```

#### Code Quality
```bash
ruff check .              # Lint with ruff
ruff format .             # Format code
mypy .                    # Type checking (if configured)
```"""

    def _contribution_section_text(self):
        """Generate contribution guidelines section with smart pattern extraction."""
        if self.contributing_guide['exists']:
            guide_path = self.contributing_guide['path']
            content = self.contributing_guide['content']

            # Extract smart patterns
            has_dco = self._extract_dco_requirement(content)
            has_release_notes = self._extract_release_notes_requirement(content)
            has_table_tests = self._extract_table_driven_tests(content)
            has_perf_work = self._extract_performance_requirements(content)
            pr_title_format = self._extract_pr_title_format(content)

            # Build key requirements list
            requirements = []
            if has_dco:
                requirements.append("**DCO Sign-off Required**: Every commit must be signed with `git commit -s`")
            if has_release_notes:
                requirements.append("**Release Notes Block**: Include `release-notes` block in every PR description")
            if pr_title_format:
                requirements.append(f"**PR Title Format**: {pr_title_format}")
            if has_table_tests:
                requirements.append("**Table-Driven Tests**: Prefer table-driven test patterns over individual test functions")
            if has_perf_work:
                requirements.append("**Performance Work**: Requires benchmarks and performance metrics in PR description")

            # Build the section
            section = f"""This project has a detailed contribution guide at **`{guide_path}`**.

**Key Requirements:**
"""
            if requirements:
                for req in requirements:
                    section += f"- {req}\n"
                section += f"\n**Before submitting:**\n1. Read `{guide_path}` in full\n2. Check recent merged PRs for patterns\n3. Follow the specific requirements above"
            else:
                section += """- Review the contribution guide for all requirements
- Follow established patterns in the codebase
- Ensure alignment with project's contribution policies"""

            return section
        else:
            return """This project doesn't have a separate CONTRIBUTING.md yet. When contributing:
1. Review recent merged PRs to understand maintainer preferences
2. Follow the patterns established in the codebase
3. Ensure your contribution aligns with the project's design principles above"""

    def _detect_enhanced_monorepo(self):
        """v1.3: Detect enhanced monorepo types (Gradle, Rust, Maven, Go)."""
        detector = MonorepoDetectorEnhanced(self.project_path)
        self.enhanced_monorepo_info = detector.detect_all()

    def _detect_testing_patterns(self):
        """v1.3: Detect and categorize testing patterns."""
        detector = TestingPatternDetector(self.project_path, self.files)
        self.testing_patterns = detector.detect_test_types()

    def _detect_conventions_per_language(self):
        """v1.3: Detect language-specific code conventions."""
        # Get primary language
        if self.languages:
            primary_lang = max(self.languages.items(), key=lambda x: x[1])[0]
            detector = ConventionDetector(primary_lang)
            self.convention_guides = {
                "language": primary_lang,
                "conventions": detector.get_conventions(),
                "guide": detector.generate_convention_guide()
            }

    def _detect_security_patterns(self):
        """v1.3: Detect security tooling and practices."""
        detector = SecurityPatternDetector(self.project_path, self.files)
        self.security_tooling = detector.detect_security_tooling()
        self.security_recommendations = detector.generate_security_recommendations()

    def _calculate_score(self):
        """Calculate agent readiness score."""
        scores = {}
        arch_score = min(20, len(self.critical_files) * 5 + 10)
        scores['Architecture'] = arch_score
        test_score = min(15, len(self.test_files) * 2 + 5)
        scores['Testing'] = test_score
        dep_score = 12 if self.build_system != "Unknown" else 6
        scores['Dependencies'] = dep_score
        convention_count = sum(1 for v in self.conventions.values() if v > 0)
        conv_score = min(10, convention_count * 2)
        scores['Conventions'] = conv_score
        entry_score = min(10, len(self.critical_files) * 3 + 4)
        scores['Entry Points'] = entry_score
        sec_score = 10 if 'validation' in self.conventions else 5
        sec_score += 5 if len(self.config_files) > 0 else 0
        scores['Security'] = min(15, sec_score)
        build_score = 10 if len(self.build_files) > 0 else 5
        scores['Build'] = build_score
        readme_exists = any(f.name.lower() == 'readme.md' for f in self.files)
        doc_score = 8 if readme_exists else 3
        scores['Documentation'] = doc_score
        self.score_breakdown = scores
        total_score = sum(scores.values())
        self.total_score = total_score
        if total_score >= 90:
            self.tier = "Agent-Optimized"
        elif total_score >= 80:
            self.tier = "AI-Native-Plus"
        elif total_score >= 60:
            self.tier = "AI-Native"
        elif total_score >= 30:
            self.tier = "Agent-Aware"
        else:
            self.tier = "Not Ready"
        self._save_score_to_history()

    def generate_github_workflow(self, setup_ci=True):
        """v1.3: Generate GitHub Actions workflow for braxis auto-sync."""
        if not setup_ci:
            return None

        generator = GitHubActionsGenerator(self.project_path)
        workflow_file = generator.write_workflow()
        return workflow_file

    def generate_readiness_badge_markdown(self):
        """v1.3: Generate readiness badge markdown."""
        return ReadinessBadgeGenerator.generate_badge_markdown(self.total_score, self.tier)

    def create_local_preferences_template(self):
        """v1.3: Create .agents.local.md template if it doesn't exist."""
        if not self.local_preferences_manager.local_prefs_file.exists():
            template = self.local_preferences_manager.create_template()
            self.local_preferences_manager.local_prefs_file.write_text(template)
            return Path(self.local_preferences_manager.local_prefs_file).resolve()
        return None

    def _write_file_safely(self, filepath, content):
        """Write file safely using atomic operation with temp file."""
        if not filepath:
            raise ValueError("Filepath cannot be empty")
        if not isinstance(content, str):
            raise TypeError(f"Content must be str, got {type(content).__name__}")
        filepath = Path(filepath)
        tmp_path = None
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode='w',
                dir=filepath.parent,
                suffix='.tmp',
                delete=False,
                encoding='utf-8'
            ) as tmp_file:
                tmp_file.write(content)
                tmp_path = Path(tmp_file.name)
            tmp_path.replace(filepath)
        except Exception as e:
            if tmp_path and tmp_path.exists():
                tmp_path.unlink()
            raise IOError(f"Failed to write file {filepath}: {e}")

    def print_score(self):
        """Print the score report."""
        print(f"\n{'='*60}")
        print(f"Agent Readiness Score: {self.total_score}/100")
        print(f"{'='*60}\n")
        print("Breakdown:\n")
        for category, score in self.score_breakdown.items():
            bar = chr(9608) * (score // 5) + chr(9617) * ((100 - score) // 5)
            print(f" {category:20} {score:3}/100 [{bar}]")
        print(f"\nTier: {self.tier}")
        print(f"\nDetected:")
        print(f" Languages: {', '.join(self.languages.keys()) if self.languages else 'None'}")
        print(f" Build System: {self.build_system}")
        print(f" Test Frameworks: {', '.join(self.test_frameworks)}")
        print(f" Test Files: {len(self.test_files)}")
        print(f" Critical Files: {len(self.critical_files)}")
        print(f"\nRecommendations:")
        if self.score_breakdown['Documentation'] < 8:
            print(f" * Add or improve README.md")
        if self.score_breakdown['Testing'] < 15:
            print(f" * Increase test coverage")
        if self.score_breakdown['Conventions'] < 10:
            print(f" * Standardize code conventions")
        if self.score_breakdown['Security'] < 15:
            print(f" * Add input validation and security checks")
        print(f"\nNext Step:")
        print(f" braxis generate")
        print(f"\n{'='*60}\n")

    def _get_testing_strategy_section(self):
        """v1.3: Generate testing strategy section."""
        if not self.testing_patterns:
            return "No specific testing patterns detected. Consider adding unit and integration tests."

        patterns = self.testing_patterns
        section = "Detected testing patterns:\n\n"

        if patterns.get('unit'):
            section += f"- **Unit Tests:** {len(patterns['unit'])} files\n"
        if patterns.get('integration'):
            section += f"- **Integration Tests:** {len(patterns['integration'])} files\n"
        if patterns.get('e2e'):
            section += f"- **E2E Tests:** {len(patterns['e2e'])} files\n"
        if patterns.get('performance'):
            section += f"- **Performance Tests:** {len(patterns['performance'])} files\n"

        return section if section != "Detected testing patterns:\n\n" else "No specific testing patterns detected."

    def _get_conventions_section(self):
        """v1.3: Generate conventions section."""
        if not self.convention_guides.get('guide'):
            return "Follow existing code style and patterns in the codebase."

        return self.convention_guides['guide']

    def _get_security_section(self):
        """v1.3: Generate security recommendations section."""
        if not self.security_recommendations:
            return "Add security scanning tools (Dependabot, CodeQL, etc.) for production readiness."

        return "\n".join(self.security_recommendations)

    def _get_test_command(self):
        """v1.3: Get appropriate test command for detected framework."""
        if not self.test_frameworks:
            return "pytest"

        framework = list(self.test_frameworks)[0] if self.test_frameworks else "pytest"
        commands = {
            "pytest": "pytest",
            "unittest": "python -m unittest discover",
            "Jest": "npm test",
            "Mocha": "npm test",
            "RSpec": "rspec",
            "cargo": "cargo test",
            "go": "go test ./..."
        }

        return commands.get(framework, "pytest")

    def generate_agents_md(self):
        """Generate comprehensive AGENTS.md file."""
        primary_lang = max(self.languages.items(), key=lambda x: x[1])[0] if self.languages else "Unknown"

        # Build vars for the template - detect actual structure
        structure = self.project_path.name + "/"
        if self.build_files:
            for f in self.build_files[:3]:
                structure += "\n├── " + f.name

        # Use detected project structure
        if self.project_structure == 'src':
            structure += "\n├── src/                  # Source code"
        elif self.project_structure == 'top-level':
            # Find actual package directory
            primary_package = None
            for item in self.project_path.iterdir():
                if item.is_dir() and not item.name.startswith('.') and item.name not in ['tests', 'docs', 'build', 'dist']:
                    if primary_lang == 'python' and (item / '__init__.py').exists():
                        primary_package = item.name
                        break
            if primary_package:
                structure += f"\n├── {primary_package}/             # Source code"
            else:
                structure += "\n├── src/                  # Source code"
        else:
            structure += "\n├── src/                  # Source code"

        if self.test_files:
            structure += "\n├── tests/                # Test suite (" + str(len(self.test_files)) + " files)"
        structure += "\n└── README.md             # Project documentation"
        
        test_frameworks_str = ', '.join(sorted(self.test_frameworks)) if self.test_frameworks else 'pytest'
        critical_files_info = ', '.join(f.name for f in self.critical_files[:5]) if self.critical_files else 'Standard layout'
        build_config = ', '.join(f.name for f in self.build_files[:3]) if self.build_files else "Standard"
        
        type_hints_status = 'Yes' if 'type_hints' in self.conventions else 'No'
        error_handling_status = 'Yes' if 'error_handling' in self.conventions else 'No'
        logging_status = 'Yes' if 'logging' in self.conventions else 'No'
        testing_status = 'Yes' if self.test_files else 'No'
        
        arch_score = self.score_breakdown.get('Architecture', 0)
        test_score = self.score_breakdown.get('Testing', 0)
        dep_score = self.score_breakdown.get('Dependencies', 0)
        conv_score = self.score_breakdown.get('Conventions', 0)
        entry_score = self.score_breakdown.get('Entry Points', 0)
        sec_score = self.score_breakdown.get('Security', 0)
        build_score = self.score_breakdown.get('Build', 0)
        doc_score = self.score_breakdown.get('Documentation', 0)
        
        return f"""# AGENTS.md

Context file for AI agents working on {self.project_path.name}.

## Project Overview

{self.project_path.name} is a {primary_lang.capitalize()} project using {self.build_system}.

**Key Info:**
- **Primary Language:** {primary_lang.capitalize()}
- **Build System:** {self.build_system}
- **Test Framework:** {test_frameworks_str}
- **Total Files:** {len(self.files)}
- **Test Files:** {len(self.test_files)}
- **AI Readiness Score:** {self.total_score}/100 ({self.tier})

## Prerequisites

- **{primary_lang.capitalize()}:** {self._get_language_version_requirement()} (or applicable language version)
- **Package Manager:** {self._get_package_manager_recommendation()}
- **Test Runner:** {test_frameworks_str}

## Project Structure

```
{structure}
```

## Architecture Overview

### Key Components
- **Main Entry:** {critical_files_info}
- **Test Suite:** {len(self.test_files)} test files
- **Build Configuration:** {build_config}

### Design Principles

1. **Modularity** - Code organized by functionality with clear separation of concerns
2. **Testability** - Comprehensive test coverage across critical paths
3. **Clarity** - Explicit naming and structure for AI agent understanding
4. **Consistency** - Uniform patterns and conventions throughout codebase
5. **Maintainability** - Well-documented code with clear intent

## Development Workflow

### Initial Setup

```bash
git clone {self.repository_url}
cd {self.project_path.name}
go mod download
```

### Development Commands

#### Running Tests
```bash
go test ./...
go test -v ./...
```

#### Code Quality
```bash
gofmt -w .
go vet ./...
```

## Code Style & Conventions

- **Naming:** Use {primary_lang.capitalize()} conventions (snake_case for functions, PascalCase for classes)
- **Type Hints:** {type_hints_status} (strongly encouraged)
- **Error Handling:** {error_handling_status} - handle errors at boundaries; let exceptions propagate when another layer owns recovery
- **Logging:** {logging_status}
- **Testing:** {testing_status} - write tests alongside code changes

## Testing Strategy

**Framework:** {test_frameworks_str}
**Test Files:** {len(self.test_files)} found

Before committing:
1. Run the full test suite: `pytest`
2. Ensure all tests pass
3. Check type hints: `mypy .`
4. Format code: `ruff format .`

## Writing Documentation

When updating docs:
1. Always include explanatory text before code snippets
2. Describe *why* and *what* before showing *how*
3. Keep sections focused on a single concept
4. Use clear, concrete examples

## Contributing Guidelines

{self._contribution_section_text()}

## Common Patterns

When contributing to this project:
1. Read existing code in the area you're modifying
2. Follow the established patterns and style
3. Write tests for new functionality
4. Use clear, descriptive variable and function names
5. Add docstrings for public APIs
6. Update tests when changing behavior

## What We Value

✅ Well-tested code with clear intent
✅ Consistent code style and naming conventions
✅ Code that is easy for AI agents to understand
✅ Clear, descriptive commit messages
✅ Modular, reusable components
✅ Comprehensive documentation

## What We Avoid

❌ Large functions doing multiple things
❌ Commented-out dead code
❌ Inconsistent naming or patterns
❌ Unclear error messages
❌ Unexplained magic numbers or strings
❌ Skipped tests or test TODOs

## AI Readiness Dimensions (Scoring)

This project is evaluated across 8 dimensions:

1. **Architecture** ({arch_score}/100) - Code organization and modularity
2. **Testing** ({test_score}/100) - Test coverage and quality
3. **Dependencies** ({dep_score}/100) - Dependency management
4. **Conventions** ({conv_score}/100) - Consistent patterns
5. **Entry Points** ({entry_score}/100) - Clear main/start locations
6. **Security** ({sec_score}/100) - Input validation and error handling
7. **Build** ({build_score}/100) - Clear build/setup instructions
8. **Documentation** ({doc_score}/100) - Code and project documentation

## Testing Strategy (v1.3)

{self._get_testing_strategy_section()}

## Code Conventions (v1.3)

{self._get_conventions_section()}

## Security Status (v1.3)

{self._get_security_section()}

## Local Team Preferences (v1.3)

Your team can customize this guidance by editing `.agents.local.md`.
Sections marked with `@override:` will replace the generated content.

Example:
```
@override: Code Style
Our team uses 4-space indents and PEP 8 conventions.
```

## Next Steps

Before making changes:
1. Read relevant source files to understand the existing code
2. Look at existing tests for similar functionality
3. Follow the patterns you see in the codebase
4. Write tests for your changes
5. Run tests locally: {self._get_test_command()}
6. Run code quality checks
7. Format your code

---

*Generated by Braxis v{__version__} - keeping AI agents in sync with your code*
"""

    def generate_claude_md(self):
        """Generate CLAUDE.md as a router to AGENTS.md - v1.3 with badge and features."""
        badge = self.generate_readiness_badge_markdown()

        local_prefs_section = ""
        if self.local_preferences_manager.local_prefs_file.exists():
            local_prefs_section = """
## Local Preferences

Your team can customize this guidance by editing `.agents.local.md`.
Sections marked with `@override:` will replace the generated content.
"""

        security_section = ""
        if self.security_recommendations:
            security_section = """
## Security Status

""" + "\n".join(self.security_recommendations) + "\n"

        return f"""# CLAUDE.md

{badge}

@AGENTS.md

This project uses AGENTS.md as the standard agent context. Claude Code loads it automatically via the @AGENTS.md import above.

## Claude Code Setup

1. **Read AGENTS.md first** for full project context
2. **Use the provided commands** in AGENTS.md for development workflow
3. **Follow the code style** outlined in AGENTS.md Conventions section
4. **Run tests locally** before asking for code suggestions
5. **Reference the scoring dimensions** when optimizing code

## Quick Commands

Generate updated context: `braxis generate`
View your AI readiness score: `braxis score`
See score trends: `braxis history --trends`
{security_section}{local_prefs_section}

See AGENTS.md for full documentation and the complete list of available commands.

---

*Generated by Braxis v{__version__}*
"""

    def generate_cursorrules(self):
        """Generate .cursorrules file with project-specific rules."""
        primary_lang = max(self.languages.items(), key=lambda x: x[1])[0] if self.languages else "Unknown"
        test_frameworks_str = ', '.join(sorted(self.test_frameworks)) if self.test_frameworks else 'pytest'
        code_formatter = "ruff" if primary_lang == "python" else "prettier" if primary_lang in ["javascript", "typescript"] else "default"
        type_checking = "mypy" if primary_lang == "python" else "TypeScript" if primary_lang == "typescript" else "available"
        
        arch_score = self.score_breakdown.get('Architecture', 0)
        test_score = self.score_breakdown.get('Testing', 0)
        dep_score = self.score_breakdown.get('Dependencies', 0)
        conv_score = self.score_breakdown.get('Conventions', 0)
        entry_score = self.score_breakdown.get('Entry Points', 0)
        sec_score = self.score_breakdown.get('Security', 0)
        build_score = self.score_breakdown.get('Build', 0)
        doc_score = self.score_breakdown.get('Documentation', 0)
        
        return f"""# Cursor Rules for {self.project_path.name}

## What This Project Does

{self.project_path.name} is a {primary_lang.capitalize()} project using {self.build_system}.

**AI Readiness Score:** {self.total_score}/100 ({self.tier})

## Architecture Overview

- **Pattern:** Single-package project
- **Primary Language:** {primary_lang.capitalize()}
- **Build System:** {self.build_system}
- **Test Framework:** {test_frameworks_str}
- **Test Files:** {len(self.test_files)}

## Must-Follow Rules

### Code Style

1. Use {code_formatter} for code formatting
2. Follow {primary_lang.capitalize()} naming conventions (snake_case for functions/variables, PascalCase for classes)
3. Add type hints where applicable ({type_checking} checking enabled)
4. No commented-out code or dead code
5. Keep functions focused and single-purpose

### Testing

1. Write tests alongside code changes
2. Run full test suite before commit: `pytest`
3. Maintain test coverage for critical paths
4. Use descriptive test names that explain what's being tested
5. Test both success and error cases

### Project Structure

- Don't create new top-level directories without understanding existing patterns
- Follow existing file organization in src/ and tests/
- Keep related code colocated
- Use clear module names that indicate their purpose

## Scoring Dimensions (What Matters)

These 8 areas drive AI readiness. Focus on these when making changes:

1. **Architecture** ({arch_score}/100) - Keep code organized and modular
2. **Testing** ({test_score}/100) - Write comprehensive tests
3. **Dependencies** ({dep_score}/100) - Minimize external dependencies
4. **Conventions** ({conv_score}/100) - Be consistent
5. **Entry Points** ({entry_score}/100) - Make main/start clear
6. **Security** ({sec_score}/100) - Validate inputs, handle errors
7. **Build** ({build_score}/100) - Clear build/setup instructions
8. **Documentation** ({doc_score}/100) - Document patterns and decisions

## Core Principles

- **Modularity** - Organize code by functionality with clear separation of concerns
- **Testability** - Every feature should be independently testable
- **Clarity** - Write code that's easy for AI agents (and humans) to understand
- **Consistency** - Follow established patterns throughout the codebase

## Before You Commit

```bash
ruff format .                 # Format code
ruff check .                  # Lint check
pytest                        # Run all tests
```

All checks must pass before committing.

## Questions?

See AGENTS.md for detailed documentation on architecture, development workflow, and testing strategy.

---

*Generated by Braxis*
"""

    def generate_agentic_config(self):
        """Generate comprehensive .agentic-config.json file."""
        primary_lang = max(self.languages.items(), key=lambda x: x[1])[0] if self.languages else "Unknown"
        
        # Determine setup and commands based on language
        if primary_lang == "python":
            setup_cmd = "pip install -e . && uv sync --all-groups"
            test_cmd = "pytest"
            lint_cmd = "ruff check ."
            format_cmd = "ruff format ."
            py_version = "3.9+"
        else:
            setup_cmd = "npm install"
            test_cmd = "npm test"
            lint_cmd = "npm run lint"
            format_cmd = "npm run format"
            py_version = "N/A"
        
        test_frameworks_str = ', '.join(sorted(self.test_frameworks)) if self.test_frameworks else 'pytest'
        build_config = ', '.join(f.name for f in self.build_files[:3]) if self.build_files else "Standard"
        
        config = {
            "metadata": {
                "project_name": self.project_path.name,
                "description": f"A {primary_lang.capitalize()} project with {self.build_system}",
                "generated_by": "Braxis",
                "generated_at": datetime.now().isoformat(),
                "schema_version": "1.0"
            },
            "project": {
                "languages": list(self.languages.keys()),
                "primary_language": primary_lang,
                "build_system": self.build_system,
                "architecture": "monorepo" if self.monorepo_type else "single-package",
                "is_monorepo": bool(self.monorepo_type),
                "monorepo_type": self.monorepo_type,
                "subsystems": [
                    {"name": s['name'], "language": s['language'], "path": s['path']}
                    for s in self.monorepo_subsystems
                ] if self.monorepo_subsystems else []
            },
            "ai_readiness": {
                "overall_score": self.total_score,
                "tier": self.tier,
                "dimensions": {
                    "architecture": {
                        "score": self.score_breakdown.get('Architecture', 0),
                        "reason": "Code organization and modularity"
                    },
                    "testing": {
                        "score": self.score_breakdown.get('Testing', 0),
                        "reason": f"{len(self.test_files)} test files found"
                    },
                    "dependencies": {
                        "score": self.score_breakdown.get('Dependencies', 0),
                        "reason": "Dependency management and version pinning"
                    },
                    "conventions": {
                        "score": self.score_breakdown.get('Conventions', 0),
                        "reason": "Consistency in naming and patterns"
                    },
                    "entry_points": {
                        "score": self.score_breakdown.get('Entry Points', 0),
                        "reason": f"{len(self.critical_files)} critical files identified"
                    },
                    "security": {
                        "score": self.score_breakdown.get('Security', 0),
                        "reason": "Input validation and error handling"
                    },
                    "build": {
                        "score": self.score_breakdown.get('Build', 0),
                        "reason": "Build system clarity and configuration"
                    },
                    "documentation": {
                        "score": self.score_breakdown.get('Documentation', 0),
                        "reason": "README and code documentation"
                    }
                }
            },
            "development": {
                "setup_command": setup_cmd,
                "test_command": test_cmd,
                "lint_command": lint_cmd,
                "format_command": format_cmd,
                "dev_server_command": None,
                "prerequisites": {
                    "language_version": py_version,
                    "package_manager": "pip or uv" if primary_lang == "python" else "npm",
                    "key_tools": list(self.test_frameworks) + (["ruff", "mypy"] if primary_lang == "python" else [])
                }
            },
            "architecture": {
                "pattern": "single-package project",
                "main_entry": ', '.join(f.name for f in self.critical_files[:3]) if self.critical_files else "Standard layout",
                "key_modules": [
                    {"name": f.stem, "path": str(f.relative_to(self.project_path)), "purpose": "Source module"}
                    for f in self.critical_files[:5]
                ] if self.critical_files else [],
                "layers": ["CLI interface (if applicable)", "Business logic", "Utilities and helpers"]
            },
            "mcp_servers": [
                {"name": s['name'], "type": s['type'], "config_file": str(s.get('location', 'unknown'))}
                for s in self.mcp_servers
            ] if self.mcp_servers else [],
            "core_principles": [
                "Modularity - Code organized by functionality",
                "Testability - Comprehensive test coverage",
                "Clarity - Code easy for AI agents to understand",
                "Consistency - Uniform patterns throughout"
            ],
            "contribution_criteria": {
                "what_we_want": [
                    "Bug fixes with test coverage",
                    "Code quality improvements",
                    "Test coverage increases",
                    "Documentation improvements",
                    "Performance optimizations"
                ],
                "what_we_dont_want": [
                    "New dependencies without justification",
                    "Code that reduces test coverage",
                    "Inconsistent naming or style",
                    "Dead code or commented code"
                ]
            },
            "contribution_boundaries": {
                "project_scale": self.analyze_project_scale(),
                "suggestion": self.suggest_contribution_boundaries()
            },
            "commands": {
                "setup": {"command": setup_cmd, "description": "Install dependencies and set up development environment"},
                "test": {"command": test_cmd, "description": "Run all tests"},
                "lint": {"command": lint_cmd, "description": "Check code style and quality"},
                "format": {"command": format_cmd, "description": "Format code to project standards"}
            },
            "testing": {
                "framework": test_frameworks_str,
                "total_tests": len(self.test_files),
                "pass_rate": 100,
                "run_command": test_cmd
            }
        }

        return json.dumps(config, indent=2)

    # ============================================================================
    # BRAXIS v1.1 FEATURES
    # ============================================================================

    def detect_monorepo_type(self):
        """Detect monorepo platform: pnpm, uv, yarn, npm workspaces, or lerna."""
        monorepo_indicators = {
            'pnpm': 'pnpm-workspace.yaml',
            'uv': 'pyproject.toml',  # Check for [tool.uv.workspaces]
            'yarn': 'package.json',  # Check for workspaces
            'npm': 'package.json',  # Check for workspaces
            'lerna': 'lerna.json',
        }

        for monorepo_type, indicator_file in monorepo_indicators.items():
            file_path = self.project_path / indicator_file
            if file_path.exists():
                if monorepo_type == 'pnpm' and 'pnpm-workspace' in file_path.name:
                    return 'pnpm'
                elif monorepo_type == 'lerna':
                    return 'lerna'
                elif monorepo_type in ('uv', 'yarn', 'npm'):
                    # Check content for workspaces configuration
                    try:
                        content = file_path.read_text()
                        if 'workspaces' in content or '[tool.uv.workspaces]' in content:
                            return monorepo_type
                    except (IOError, UnicodeDecodeError):
                        pass

        return None

    def get_monorepo_subsystems(self):
        """Identify subsystems in a monorepo (api, web, packages, etc.)."""
        subsystems = []

        # Common subsystem directories
        subsystem_dirs = ['api', 'web', 'cli', 'packages', 'libs', 'apps', 'services']

        for subsys_dir in subsystem_dirs:
            subsys_path = self.project_path / subsys_dir
            if subsys_path.exists() and subsys_path.is_dir():
                # Detect language in this subsystem
                lang = self._detect_subsystem_language(subsys_path)
                subsystems.append({
                    'name': subsys_dir,
                    'path': subsys_dir,
                    'language': lang
                })

        return subsystems

    def _detect_subsystem_language(self, path):
        """Detect primary language in a directory."""
        lang_counts = defaultdict(int)
        for ext, langs in self.LANGUAGE_EXTENSIONS.items():
            for lang_ext in langs:
                count = len(list(path.rglob(f'*{lang_ext}')))
                if count > 0:
                    lang_counts[ext] += count

        return max(lang_counts.items(), key=lambda x: x[1])[0] if lang_counts else 'unknown'

    def generate_hierarchical_contexts(self):
        """Generate hierarchical AGENTS.md for monorepos."""
        monorepo_type = self.detect_monorepo_type()

        if not monorepo_type:
            # Single package - return None to use default generate_agents_md()
            return None

        subsystems = self.get_monorepo_subsystems()

        # Generate root AGENTS.md
        root_content = self._generate_root_agents_md(monorepo_type, subsystems)

        # Generate scoped AGENTS.md for each subsystem
        scoped_contents = {}
        for subsystem in subsystems:
            scoped_content = self._generate_scoped_agents_md(subsystem)
            scoped_contents[f"{subsystem['path']}/AGENTS.md"] = scoped_content

        return {
            'AGENTS.md': root_content,
            **scoped_contents
        }

    def _generate_root_agents_md(self, monorepo_type, subsystems):
        """Generate root AGENTS.md for monorepo."""
        subsystem_list = '\n'.join([
            f"- `{s['name']}/` → See {s['name']}/AGENTS.md ({s['language']} {s['name']})"
            for s in subsystems
        ])

        return f"""# {self.project_path.name} - Agent Context

{self.project_path.name} is a {monorepo_type} monorepo with {len(subsystems)} major subsystems.

## Critical Instruction

When modifying files, **follow the nearest scoped AGENTS.md** for that subsystem.

This file contains global patterns and monorepo gotchas.
Scoped files contain subsystem-specific rules and conventions.

### Hierarchy
- **Root AGENTS.md**: General patterns, monorepo gotchas, architecture overview
- **Subsystem AGENTS.md**: Backend, frontend, CLI, etc. - specific rules per subsystem
- **Feature AGENTS.md**: Deep dives for complex features (if present)

## Subsystems

{subsystem_list}

## Monorepo Gotchas

### Build & Test
- Use `{monorepo_type}` for dependency management
- Run tests per subsystem or globally depending on configuration
- Keep monorepo-wide versions in {self._get_lock_file(monorepo_type)}

### Development
- Install dependencies: `{self._get_install_cmd(monorepo_type)}`
- Format all code: `{self._get_format_cmd(monorepo_type)}`
- Run tests: `{self._get_test_cmd(monorepo_type)}`

## Architecture Overview

This monorepo uses a subsystem-based organization:

{self._generate_arch_overview(subsystems)}

## What to Work On

When contributing:
1. Identify which subsystem your changes affect
2. Read the nearest scoped AGENTS.md
3. Follow those subsystem-specific rules
4. Cross-subsystem changes? Document the interaction in your PR

## What We Value

✅ Following subsystem boundaries
✅ Keeping subsystems loosely coupled
✅ Comprehensive tests per subsystem
✅ Clear documentation of subsystem contracts
✅ Minimizing cross-subsystem dependencies

---

*Generated by Braxis v1.1 - Hierarchical Agent Context for Monorepos*
"""

    def _generate_scoped_agents_md(self, subsystem):
        """Generate scoped AGENTS.md for a subsystem."""
        lang = subsystem.get('language', 'unknown').capitalize()

        return f"""# {subsystem['name'].capitalize()} Subsystem Agent Guide

Read this file when working in `{subsystem['path']}/`.
Then refer to root AGENTS.md for repo-wide patterns.

## Subsystem Overview

This subsystem is the **{subsystem['name']}** layer of the project.

Primary Language: **{lang}**

## Architecture

{self._generate_subsystem_arch(subsystem)}

## Code Style

Follow root AGENTS.md conventions, with these subsystem-specific rules:

- Keep {subsystem['name']} concerns isolated
- Use clear interfaces with other subsystems
- Document public APIs for cross-subsystem use

## Testing

- Write tests alongside code changes
- Tests live in `{subsystem['path']}/__tests__` or `{subsystem['path']}/tests/`
- Run with: `pytest {subsystem['path']}/`

## Common Patterns

When working in this subsystem:
1. Read existing code in the area you're modifying
2. Follow the established patterns
3. Write tests for new functionality
4. Use clear, descriptive names

## Integration Points

Document any dependencies on other subsystems:
- Clearly name imported types/functions
- Keep interfaces minimal
- Add comments explaining why the dependency exists

---

*Generated by Braxis v1.1*
"""

    def _get_lock_file(self, monorepo_type):
        """Get lock file name for monorepo type."""
        lock_files = {
            'pnpm': 'pnpm-lock.yaml',
            'uv': 'uv.lock',
            'yarn': 'yarn.lock',
            'npm': 'package-lock.json',
            'lerna': 'package-lock.json'
        }
        return lock_files.get(monorepo_type, 'lock file')

    def _get_install_cmd(self, monorepo_type):
        """Get install command for monorepo type."""
        cmds = {
            'pnpm': 'pnpm install',
            'uv': 'uv sync --all-groups',
            'yarn': 'yarn install',
            'npm': 'npm install',
            'lerna': 'lerna bootstrap'
        }
        return cmds.get(monorepo_type, 'npm install')

    def _get_format_cmd(self, monorepo_type):
        """Get format command for monorepo type."""
        # Most modern projects use ruff or prettier
        return 'ruff format . && prettier --write .' if self.build_system else 'ruff format .'

    def _get_test_cmd(self, monorepo_type):
        """Get test command for monorepo type."""
        return 'pytest' if 'python' in self.languages else 'npm test'

    def _generate_arch_overview(self, subsystems):
        """Generate architecture overview section."""
        overview = "```\n"
        overview += f"{self.project_path.name}/\n"
        for i, subsys in enumerate(subsystems):
            is_last = i == len(subsystems) - 1
            prefix = "└── " if is_last else "├── "
            overview += f"{prefix}{subsys['name']}/ ({subsys['language'].upper()})\n"
        overview += "```"
        return overview

    def _generate_subsystem_arch(self, subsystem):
        """Generate subsystem-specific architecture."""
        return f"""The **{subsystem['name']}** subsystem is primarily {subsystem['language'].capitalize()}.

Key responsibilities:
- Implement {subsystem['name']}-specific business logic
- Expose clean interfaces to other subsystems
- Maintain {subsystem['name']}-specific configuration
"""

    def detect_mcp_servers(self):
        """Detect MCP server configuration in repo."""
        mcp_servers = []

        # Check for Claude Desktop config
        claude_config = self.project_path / '.claude' / 'claude_desktop_config.json'
        if claude_config.exists():
            try:
                config = json.loads(claude_config.read_text())
                if 'mcpServers' in config:
                    for server_name, server_config in config['mcpServers'].items():
                        mcp_servers.append({
                            'name': server_name,
                            'type': 'claude_desktop',
                            'config': server_config
                        })
            except (json.JSONDecodeError, IOError):
                pass

        # Check for MCP entry points in pyproject.toml
        if 'python' in self.languages:
            pyproject = self.project_path / 'pyproject.toml'
            if pyproject.exists():
                content = pyproject.read_text()
                if '[project.entry-points.mcp]' in content or '[project.entry-points."mcp"]' in content:
                    # This is an MCP server project
                    mcp_servers.append({
                        'name': self.project_path.name,
                        'type': 'python_entry_point',
                        'location': 'pyproject.toml'
                    })

        # Check for mcp.json or similar config
        for config_file in self.project_path.glob('*mcp*.json'):
            try:
                config = json.loads(config_file.read_text())
                mcp_servers.append({
                    'name': config_file.stem,
                    'type': 'config_file',
                    'config': config
                })
            except (json.JSONDecodeError, IOError):
                pass

        return mcp_servers

    def generate_mcp_context(self):
        """Generate MCP documentation section."""
        mcp_servers = self.detect_mcp_servers()

        if not mcp_servers:
            return None

        server_docs = '\n'.join([
            f"- **{s['name']}** ({s['type']})" for s in mcp_servers
        ])

        return f"""## MCP Integration

This repository includes {{len(mcp_servers)}} MCP server(s).

### Servers
{server_docs}

### Development
```bash
# For Python MCP servers
python -m your_module

# Or use the entry point
mcp run your_server
```

### Tool Documentation

Document your MCP tools:
- Tool specs: See `mcp_servers/` directory
- Examples: See examples/ or docs/ for usage
- Discovery: Tools auto-discovered from MCP config

### Testing MCP Tools

```bash
# Test MCP tool discovery
mcp list-resources

# Test tool execution
mcp call <tool_name> <args>
```

---
"""

    def analyze_project_scale(self):
        """Suggest contribution boundaries based on project scale."""
        num_files = len(self.files)

        if num_files < 50:
            return "micro"
        elif num_files < 200:
            return "small"
        elif num_files < 500:
            return "medium"
        else:
            return "large"

    def suggest_contribution_boundaries(self):
        """Generate contribution boundaries template."""
        scale = self.analyze_project_scale()

        suggestions = {
            "micro": "This micro-project is early-stage. Accept most contributions.",
            "small": "This small project can accept most contributions. Consider boundaries as it grows.",
            "medium": "This project is growing. Consider defining clear contribution scope.",
            "large": "This large project should define clear contribution boundaries. Consider LlamaIndex model: 'no new X' policy.",
        }

        return suggestions.get(scale, "")


__version__ = "1.1.0"


def main():
    parser = argparse.ArgumentParser(description='Braxis - AI agent context generator')
    parser.add_argument('--version', action='version', version=f'Braxis {__version__}')
    parser.add_argument('command', choices=['generate', 'score', 'inspect', 'validate', 'history'],
                        help='Command to run')
    parser.add_argument('--path', default='.', help='Project path')
    parser.add_argument('--trends', action='store_true', help='Show score trends')
    args = parser.parse_args()

    if not args.command or args.command not in ['generate', 'score', 'inspect', 'validate', 'history']:
        parser.print_help()
        sys.exit(1)

    if args.command == 'history':
        try:
            analyzer = BraxisAnalyzer(args.path)
            if args.trends:
                analyzer.show_score_trends()
            else:
                history = analyzer.get_score_history()
                if not history:
                    print("No score history available. Run 'braxis score' to start tracking.")
                else:
                    print(f"\nScore History for {analyzer.project_path.name}:")
                    for i, entry in enumerate(history, 1):
                        timestamp = entry['timestamp'][:10]
                        score = entry['score']
                        tier = entry['tier']
                        print(f"{i}. {timestamp} - {score}/100 ({tier})")
        except (ValueError, FileNotFoundError, NotADirectoryError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    try:
        analyzer = BraxisAnalyzer(args.path)
        analyzer.analyze()
    except (ValueError, FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.command == 'score':
        analyzer.print_score()
    elif args.command == 'generate':
        print("Generating context files...")
        try:
            # v1.1: Check for monorepo and generate hierarchically
            hierarchical_contexts = analyzer.generate_hierarchical_contexts()
            if hierarchical_contexts:
                print("Detected monorepo! Generating hierarchical AGENTS.md...")
                for file_path, content in hierarchical_contexts.items():
                    analyzer._write_file_safely(file_path, content)
                    print(f"* {file_path}")
            else:
                analyzer._write_file_safely('AGENTS.md', analyzer.generate_agents_md())
                print("* AGENTS.md")

            analyzer._write_file_safely('CLAUDE.md', analyzer.generate_claude_md())
            print("* CLAUDE.md")
            analyzer._write_file_safely('.cursorrules', analyzer.generate_cursorrules())
            print("* .cursorrules")
            analyzer._write_file_safely('.agentic-config.json', analyzer.generate_agentic_config())
            print("* .agentic-config.json")

            # v1.3: Generate GitHub Actions workflow
            workflow_file = analyzer.generate_github_workflow(setup_ci=True)
            if workflow_file:
                print(f"* {workflow_file.relative_to(analyzer.project_path)}")

            # v1.3: Create local preferences template
            local_prefs_file = analyzer.create_local_preferences_template()
            if local_prefs_file:
                print(f"* {local_prefs_file.relative_to(analyzer.project_path)}")

            # v1.1: Report MCP and monorepo info
            if analyzer.monorepo_type:
                print(f"\n✓ Monorepo detected: {analyzer.monorepo_type.upper()} with {len(analyzer.monorepo_subsystems)} subsystems")
            if analyzer.enhanced_monorepo_info:
                print(f"✓ Enhanced detection: {analyzer.enhanced_monorepo_info['type']} with {analyzer.enhanced_monorepo_info['count']} modules")
            if analyzer.mcp_servers:
                print(f"✓ MCP servers detected: {len(analyzer.mcp_servers)} server(s)")

            # v1.3: Report v1.3 features
            if analyzer.testing_patterns:
                test_types = len(analyzer.testing_patterns)
                print(f"✓ Testing patterns detected: {test_types} type(s)")
            if analyzer.convention_guides:
                print(f"✓ Conventions documented for: {analyzer.convention_guides.get('language', 'unknown')}")
            if analyzer.security_tooling:
                print(f"✓ Security tooling found: {len(analyzer.security_tooling)}")

            scale = analyzer.analyze_project_scale()
            if scale in ('large', 'medium'):
                suggestion = analyzer.suggest_contribution_boundaries()
                if suggestion:
                    print(f"\n💡 Project Scale ({scale}): {suggestion}")

            print(f"\nAgent Readiness: {analyzer.total_score}/100 ({analyzer.tier})")
            print("\n✅ All files created successfully!")
            print("\n📝 Next steps:")
            print("  1. Review AGENTS.md and CLAUDE.md")
            print("  2. Customize .agents.local.md for your team")
            print("  3. Commit context files to git")
            print("  4. Run: braxis score (to see detailed breakdown)")
        except IOError as e:
            print(f"Error writing files: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == 'inspect':
        print(f"\nProject Analysis:")
        print(f" Languages: {dict(analyzer.languages)}")
        print(f" Build System: {analyzer.build_system}")
        print(f" Test Frameworks: {list(analyzer.test_frameworks)}")
        print(f" Files: {len(analyzer.files)}")
        print(f" Test Files: {len(analyzer.test_files)}")
        print(f" Critical Files: {len(analyzer.critical_files)}")
        # v1.1
        if analyzer.monorepo_type:
            print(f" Monorepo Type: {analyzer.monorepo_type.upper()}")
            print(f" Subsystems: {len(analyzer.monorepo_subsystems)}")
            for subsys in analyzer.monorepo_subsystems:
                print(f"   - {subsys['name']} ({subsys['language']})")
        if analyzer.mcp_servers:
            print(f" MCP Servers: {len(analyzer.mcp_servers)}")
            for server in analyzer.mcp_servers:
                print(f"   - {server['name']} ({server['type']})")
    elif args.command == 'validate':
        required_files = ['AGENTS.md', 'CLAUDE.md', '.cursorrules', '.agentic-config.json']
        missing = [f for f in required_files if not Path(f).exists()]
        if missing:
            print(f"* Missing: {', '.join(missing)}")
            print(f"Run: braxis generate")
            sys.exit(1)
        else:
            print(f"* All context files present")
            print(f"Agent Readiness: {analyzer.total_score}/100 ({analyzer.tier})")


if __name__ == '__main__':
    main()
