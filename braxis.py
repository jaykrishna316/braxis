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
        """Detect test framework, language-aware with better edge case handling."""
        test_frameworks = set()
        primary_lang = self._get_primary_language()

        # Language-specific test framework detection with fallbacks
        if primary_lang == "go":
            test_frameworks.add("Go testing")
        elif primary_lang == "python":
            # Check multiple sources for pytest
            framework_found = False

            # 1. Check pyproject.toml
            pyproject = self.project_path / 'pyproject.toml'
            if pyproject.exists():
                try:
                    content = pyproject.read_text()
                    if 'pytest' in content.lower():
                        test_frameworks.add('pytest')
                        framework_found = True
                    elif 'unittest' in content.lower():
                        test_frameworks.add('unittest')
                        framework_found = True
                except (IOError, UnicodeDecodeError):
                    pass

            # 2. Check setup.cfg
            setup_cfg = self.project_path / 'setup.cfg'
            if setup_cfg.exists() and not framework_found:
                try:
                    content = setup_cfg.read_text()
                    if 'pytest' in content.lower():
                        test_frameworks.add('pytest')
                        framework_found = True
                except (IOError, UnicodeDecodeError):
                    pass

            # 3. Check test files for imports
            if not framework_found and self.test_files:
                for test_file in self.test_files[:10]:
                    try:
                        content = test_file.read_text()
                        if 'import pytest' in content or 'from pytest' in content:
                            test_frameworks.add('pytest')
                            framework_found = True
                            break
                        elif 'import unittest' in content:
                            test_frameworks.add('unittest')
                            framework_found = True
                            break
                    except (IOError, UnicodeDecodeError):
                        pass

            # 4. Default to pytest if Python has tests
            if not framework_found and self.test_files:
                test_frameworks.add('pytest')

        elif primary_lang in ["javascript", "typescript"]:
            # Check package.json first
            pkg_json = self.project_path / 'package.json'
            if pkg_json.exists():
                try:
                    content = pkg_json.read_text()
                    if 'jest' in content.lower():
                        test_frameworks.add('Jest')
                    elif 'mocha' in content.lower():
                        test_frameworks.add('Mocha')
                    elif 'vitest' in content.lower():
                        test_frameworks.add('Vitest')
                except (IOError, UnicodeDecodeError):
                    pass

            if not test_frameworks and self.test_files:
                test_frameworks.add('Jest')  # Default for JS/TS

        elif primary_lang == "ruby":
            content_samples = self._sample_file_contents(limit=20)
            found = False
            for content in content_samples:
                if 'rspec' in content.lower():
                    test_frameworks.add('RSpec')
                    found = True
                    break
            if not found and self.test_files:
                test_frameworks.add('RSpec')

        elif primary_lang == "java":
            # Check pom.xml for junit version to confirm it's a test framework
            test_frameworks.add('JUnit')
            if any('pom.xml' in str(f) for f in self.build_files):
                try:
                    pom = self.project_path / 'pom.xml'
                    if pom.exists():
                        content = pom.read_text()
                        if 'testng' in content.lower():
                            test_frameworks.add('TestNG')
                except (IOError, UnicodeDecodeError):
                    pass

        elif primary_lang == "cpp":
            # C++ doesn't use JUnit - check for C++ test frameworks
            content_samples = self._sample_file_contents(limit=10)
            for content in content_samples:
                if 'gtest' in content or 'google/test' in content:
                    test_frameworks.add('Google Test')
                    break
                elif 'catch' in content.lower() and 'include' in content.lower():
                    test_frameworks.add('Catch2')
                    break
            if not test_frameworks and self.test_files:
                test_frameworks.add('C++ Test Framework')

        elif primary_lang == "rust":
            test_frameworks.add('Rust cargo')  # Rust has built-in testing

        elif primary_lang == "c":
            content_samples = self._sample_file_contents(limit=10)
            for content in content_samples:
                if 'criterion' in content or 'unity' in content:
                    test_frameworks.add('C Test Framework')
                    break

        # If still nothing found, add placeholder (but prefer actual detection)
        if not test_frameworks:
            if self.test_files:
                test_frameworks.add(f"{primary_lang.capitalize()} tests")
            else:
                # Only add "None detected" if there are truly no test files
                test_frameworks.add("None detected")

        self.test_frameworks = test_frameworks

    def _detect_naming_patterns(self):
        """Detect actual naming conventions used in the codebase."""
        import re
        primary_lang = self._get_primary_language()
        patterns = {'snake_case': 0, 'camelCase': 0, 'PascalCase': 0, 'CONSTANT_CASE': 0}

        content_samples = self._sample_file_contents(limit=30)
        for content in content_samples:
            # Extract identifiers (variable names, function names)
            identifiers = re.findall(r'\b[a-zA-Z_]\w*\b', content)
            for identifier in identifiers:
                if identifier.isupper() and '_' in identifier:
                    patterns['CONSTANT_CASE'] += 1
                elif '_' in identifier and identifier.islower():
                    patterns['snake_case'] += 1
                elif identifier[0].isupper():
                    patterns['PascalCase'] += 1
                elif identifier[0].islower() and any(c.isupper() for c in identifier[1:]):
                    patterns['camelCase'] += 1

        # Return dominant pattern
        if patterns['snake_case'] > patterns['camelCase'] * 2:
            return "snake_case"
        elif patterns['camelCase'] > patterns['snake_case'] * 2:
            return "camelCase"
        elif patterns['PascalCase'] > sum(patterns.values()) * 0.3:
            return "PascalCase"
        else:
            return "mixed"

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

        # Store detected naming pattern
        self.naming_pattern = self._detect_naming_patterns()

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

    def _get_initial_setup_commands(self, primary_lang):
        """Get language-appropriate initial setup commands."""
        if primary_lang == "go":
            return "go mod download"
        elif primary_lang == "rust":
            return "cargo build"
        elif primary_lang == "ruby":
            return "bundle install"
        elif primary_lang in ["javascript", "typescript"]:
            return "npm install\n# or\nyarn install"
        else:  # Python and others
            return "pip install -e .\n# or\nuv sync --all-groups"

    def _get_testing_strategy_commands(self, primary_lang):
        """Get language-appropriate testing strategy commands."""
        if primary_lang == "go":
            return """Before committing:
1. Run the full test suite: `go test ./...`
2. Ensure all tests pass: `go test -v ./...`
3. Run linter: `golangci-lint run`
4. Format code: `gofmt -w .`"""
        elif primary_lang == "rust":
            return """Before committing:
1. Run the full test suite: `cargo test`
2. Run clippy: `cargo clippy --all-targets`
3. Format code: `cargo fmt`
4. Check documentation: `cargo doc --no-deps`"""
        elif primary_lang == "ruby":
            return """Before committing:
1. Run the full test suite: `bundle exec rspec`
2. Run specific test directory: `bundle exec rspec spec/`
3. Lint with RuboCop: `bundle exec rubocop`
4. Auto-fix issues: `bundle exec rubocop -a`"""
        elif primary_lang in ["javascript", "typescript"]:
            return """Before committing:
1. Run the full test suite: `npm test` or `yarn test`
2. Run linter: `npm run lint` or `yarn lint`
3. Format code: `npm run format` or `yarn format`
4. Type check (if TypeScript): `npm run type-check`"""
        else:  # Python and others
            return """Before committing:
1. Run the full test suite: `pytest`
2. Ensure all tests pass
3. Check type hints: `mypy .`
4. Format code: `ruff format .`"""

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

    def _calculate_score(self):
        """Calculate agent readiness score - normalized to be consistent across project types."""
        scores = {}

        # Architecture: Focus on quality of critical files, not quantity
        # Max 15 points: 5 for having any critical files, 10 for having multiple entry points
        arch_score = 5 if self.critical_files else 0
        arch_score += min(10, max(0, len(self.critical_files) - 1) * 3)
        scores['Architecture'] = arch_score

        # Testing: Has tests = 15, no tests = 0. Don't penalize small projects.
        # The presence of tests matters more than quantity
        test_score = 15 if self.test_files else 0
        scores['Testing'] = test_score

        # Dependencies: Has build system = 12, unknown = 0
        # This is binary - either the project is buildable or not
        dep_score = 12 if self.build_system != "Unknown" else 0
        scores['Dependencies'] = dep_score

        # Conventions: Count detected conventions (async, error_handling, type_hints, logging, validation)
        # Max 10 points for having multiple conventions detected
        convention_count = sum(1 for v in self.conventions.values() if v > 0)
        conv_score = min(10, convention_count * 2)
        scores['Conventions'] = conv_score

        # Entry Points: Has at least one clear entry point = 10, otherwise = 0
        # Don't penalize projects with fewer entry points
        entry_score = 10 if self.critical_files else 0
        scores['Entry Points'] = entry_score

        # Security: Has validation or input handling = 10, has config files = 5
        # Max 15 points
        sec_score = 0
        sec_score += 10 if 'validation' in self.conventions else 0
        sec_score += 5 if len(self.config_files) > 0 else 0
        scores['Security'] = min(15, sec_score)

        # Build: Has any build files = 10, otherwise = 0
        # Binary: buildable or not
        build_score = 10 if self.build_files else 0
        scores['Build'] = build_score

        # Documentation: Has README = 8, has docs directory = full 8
        # This is about presence, not volume
        doc_score = 0
        readme_exists = any(f.name.lower() in ['readme.md', 'readme.rst', 'readme.txt'] for f in self.files)
        if readme_exists:
            doc_score = 8
        docs_exist = (self.project_path / 'docs').exists() and len(list((self.project_path / 'docs').iterdir())) > 0
        if docs_exist:
            doc_score = max(doc_score, 8)
        scores['Documentation'] = doc_score

        self.score_breakdown = scores
        total_score = sum(scores.values())
        self.total_score = total_score

        # Tier assignment: More balanced distribution
        if total_score >= 85:
            self.tier = "Agent-Optimized"
        elif total_score >= 70:
            self.tier = "AI-Native-Plus"
        elif total_score >= 50:
            self.tier = "AI-Native"
        elif total_score >= 25:
            self.tier = "Agent-Aware"
        else:
            self.tier = "Not Ready"
        self._save_score_to_history()

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

    def _extract_gotchas_from_contributing(self):
        """v1.3.1: Extract warnings and gotchas from CONTRIBUTING.md."""
        if not self.contributing_guide['exists']:
            return []

        content = self.contributing_guide['content']
        gotchas = []
        warning_keywords = ['gotcha', 'warning:', 'caution:', 'note:', "don't", 'avoid', 'issue:', 'important:']

        lines = content.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(kw in line_lower for kw in warning_keywords):
                # Clean up markdown formatting
                clean_line = line.strip().lstrip('-').lstrip('*').lstrip('>').strip()
                if clean_line and len(clean_line) > 10:
                    gotchas.append(clean_line)

        return gotchas[:10]  # Limit to top 10 gotchas

    def _extract_category_a_content(self):
        """v1.4: Extract Category A (Operations Manual) content from CONTRIBUTING.md."""
        if not self.contributing_guide['exists']:
            return {}

        content = self.contributing_guide['content']
        category_a = {
            'procedures': [],
            'requirements': [],
            'workarounds': [],
            'policy_notes': []
        }

        lines = content.split('\n')

        # Extract procedures (lines with verbs like "must", "should", "run", "follow")
        procedure_keywords = ['must ', 'should ', 'run ', 'follow ', 'execute', 'install', 'build', 'test', 'commit']
        requirement_keywords = ['require', 'required', 'prerequisite', 'need', 'dependency']
        workaround_keywords = ['workaround', 'caveat', 'limitation', 'known issue', 'gotcha', 'exception']
        policy_keywords = ['policy', 'rule', 'guideline', 'standard', 'convention', 'forbidden', 'banned', 'cannot', 'must not', 'agent']

        for line in lines:
            # Skip markdown headers and empty lines
            if line.strip().startswith('#') or not line.strip():
                continue

            clean_line = line.strip().lstrip('-').lstrip('*').lstrip('>').strip()
            if not clean_line or len(clean_line) < 10:
                continue

            # Strip bold markdown
            if clean_line.startswith('**') and clean_line.endswith('**'):
                clean_line = clean_line.strip('**').strip()

            if not clean_line or len(clean_line) < 10:
                continue

            line_lower = clean_line.lower()

            # Classify based on keywords - check policy first
            if any(kw in line_lower for kw in policy_keywords):
                if clean_line not in category_a['policy_notes']:
                    category_a['policy_notes'].append(clean_line)
            elif any(kw in line_lower for kw in procedure_keywords):
                if clean_line not in category_a['procedures']:
                    category_a['procedures'].append(clean_line)
            elif any(kw in line_lower for kw in requirement_keywords):
                if clean_line not in category_a['requirements']:
                    category_a['requirements'].append(clean_line)
            elif any(kw in line_lower for kw in workaround_keywords):
                if clean_line not in category_a['workarounds']:
                    category_a['workarounds'].append(clean_line)

        return category_a

    def _format_category_a_section(self, category_a_content):
        """Format Category A content into markdown section."""
        if not any(category_a_content.values()):
            return ""

        section = "## 🚨 AI Policy & Operations\n\n"
        section += "Extracted from CONTRIBUTING.md - operational constraints and procedures.\n\n"

        if category_a_content['policy_notes']:
            section += "### AI Policy\n\n"
            for note in category_a_content['policy_notes'][:5]:
                section += f"- {note}\n"
            section += "\n"

        if category_a_content['requirements']:
            section += "### Key Requirements\n\n"
            for req in category_a_content['requirements'][:5]:
                section += f"- {req}\n"
            section += "\n"

        if category_a_content['procedures']:
            section += "### Development Procedures\n\n"
            for proc in category_a_content['procedures'][:5]:
                section += f"- {proc}\n"
            section += "\n"

        if category_a_content['workarounds']:
            section += "### Known Workarounds & Caveats\n\n"
            for wka in category_a_content['workarounds'][:3]:
                section += f"- {wka}\n"
            section += "\n"

        return section

    def _generate_architecture_tables(self):
        """v1.3.1: Auto-generate directory-to-purpose mapping tables."""
        primary_lang = self._get_primary_language()

        # For monorepos, reference subsystem-scoped AGENTS.md files
        if self.monorepo_type:
            subsystems = self.get_monorepo_subsystems()
            if subsystems:
                subsystem_refs = '\n'.join([
                    f"- `{s['name']}/AGENTS.md` — {s['name'].capitalize()} subsystem ({s['language']})"
                    for s in subsystems
                ])
                return f"""### Directory-Scoped Agent Files

Each subsystem has its own specialized AGENTS.md file:

{subsystem_refs}

Refer to the scoped file when working in that directory."""

        # For single-language projects, generate directory map
        arch_table = "### Directory Map\n\n| Directory | Purpose |\n|-----------|----------|\n"

        common_dirs = {
            'src': 'Source code',
            'lib': 'Library code',
            'tests': 'Test suite',
            'test': 'Test suite',
            'spec': 'Test specifications',
            'docs': 'Documentation',
            'examples': 'Usage examples',
            'scripts': 'Build and utility scripts',
            'pkg': 'Package definitions',
            'cmd': 'Command-line tools',
            'api': 'API handlers',
            'config': 'Configuration files',
            'migrations': 'Database migrations',
            'public': 'Public assets',
            'vendor': 'Dependencies',
        }

        found_dirs = set()
        for item in self.project_path.iterdir():
            if item.is_dir() and item.name in common_dirs and not item.name.startswith('.'):
                found_dirs.add(item.name)

        # Add found directories
        for dir_name in sorted(found_dirs):
            arch_table += f"| `{dir_name}/` | {common_dirs[dir_name]} |\n"

        # If no standard directories found, use basic structure
        if not found_dirs:
            arch_table += f"| `src/` or project root | Main source code |\n"
            arch_table += "| `tests/` or `test/` | Test suite |\n"

        return arch_table

    def _detect_environment_requirements(self):
        """v1.3.1: Extract environment setup requirements and gotchas."""
        env_info = {}
        env_section = "### Environment Requirements\n\n"

        # Check .nvmrc for Node.js version
        nvmrc = self.project_path / '.nvmrc'
        if nvmrc.exists():
            try:
                node_version = nvmrc.read_text().strip()
                env_info['node'] = node_version
                env_section += f"- **Node.js:** {node_version} (pinned in `.nvmrc`)\n"
                env_section += "  ⚠️ **PATH Gotcha:** Run `yarn`/`npm` via login shell (`tmux` or `bash -lc`) to use pinned version\n"
            except (IOError, UnicodeDecodeError):
                pass

        # Check go.mod for Go version
        go_mod = self.project_path / 'go.mod'
        if go_mod.exists():
            try:
                for line in go_mod.read_text().split('\n'):
                    if line.startswith('go '):
                        go_version = line.split()[1]
                        env_info['go'] = go_version
                        env_section += f"- **Go:** {go_version}+ (from `go.mod`)\n"
                        env_section += "  - GCC required for CGo/SQLite compilation\n"
                        break
            except (IOError, UnicodeDecodeError):
                pass

        # Check .ruby-version for Ruby
        ruby_version_file = self.project_path / '.ruby-version'
        if ruby_version_file.exists():
            try:
                ruby_version = ruby_version_file.read_text().strip()
                env_info['ruby'] = ruby_version
                env_section += f"- **Ruby:** {ruby_version} (from `.ruby-version`)\n"
            except (IOError, UnicodeDecodeError):
                pass

        # Check for Python requirements
        if 'python' in self.languages:
            version = self._get_language_version_requirement()
            env_section += f"- **Python:** {version}\n"

        # Add package manager info
        primary_lang = self._get_primary_language()
        if primary_lang in ["javascript", "typescript"]:
            env_section += "- **Package Manager:** npm or yarn\n"
        elif primary_lang == "go":
            env_section += "- **Package Manager:** go modules\n"

        return env_section if env_info else ""

    def detect_existing_file(self, filename):
        """Generic: Detect and score existing file for merge decisions."""
        file_path = self.project_path / filename
        if not file_path.exists():
            return None

        try:
            content = file_path.read_text()
            score = self._score_file_quality(content, filename)
            return {
                'exists': True,
                'path': file_path,
                'content': content,
                'score': score,
                'sections': self._extract_sections(content) if filename.endswith('.md') else {}
            }
        except (IOError, UnicodeDecodeError):
            return None

    def detect_existing_agents_md(self):
        """Detect and score existing AGENTS.md for merge decisions."""
        return self.detect_existing_file('AGENTS.md')

    def _score_file_quality(self, content, filename):
        """Score file quality for hand-written vs auto-generated content."""
        score = 0

        # Base score on file length (hand-written content tends to be longer)
        if len(content) > 500:
            score += 20
        if len(content) > 1500:
            score += 15
        if len(content) > 3000:
            score += 10

        # Check for custom/meaningful content patterns
        custom_indicators = [
            'Skills', 'Package Domain', 'Key Entry Point',
            'Gotcha', 'Governance', 'Notes', 'Contributing Guidelines',
            'API Reference', 'Architecture Diagram'
        ]

        for indicator in custom_indicators:
            if indicator.lower() in content.lower():
                score += 10

        # Bonus for code examples (indicates hand-written)
        if '```' in content:
            score += 15

        # Penalty for generic/template text
        generic_patterns = ['TODO', 'FIXME', '...', '[Your', 'Replace this']
        generic_count = sum(1 for p in generic_patterns if p in content)
        score -= generic_count * 5

        # Section count bonus
        section_count = content.count('##')
        score += min(section_count * 3, 15)

        return min(max(score, 0), 100)

    def _score_agents_md(self, content):
        """Score existing AGENTS.md on completeness and customization."""
        return self._score_file_quality(content, 'AGENTS.md')

    def _extract_sections(self, content):
        """Extract custom sections from AGENTS.md."""
        lines = content.split('\n')
        sections = {}
        current_section = None
        current_content = []

        for line in lines:
            if line.startswith('##') and not line.startswith('###'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.replace('##', '').strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def _format_score_breakdown(self):
        """Format the score breakdown for PR description."""
        if not self.score_breakdown:
            return ""

        breakdown_text = "\n### AI Readiness Score Breakdown\n\n"
        breakdown_text += "| Category | Score | Status |\n"
        breakdown_text += "|----------|-------|--------|\n"

        # Define max scores and emojis for each category
        max_scores = {
            'Architecture': 20,
            'Testing': 15,
            'Dependencies': 12,
            'Conventions': 10,
            'Entry Points': 10,
            'Security': 15,
            'Build': 10,
            'Documentation': 8,
        }

        for category, score in self.score_breakdown.items():
            max_score = max_scores.get(category, 100)
            percentage = (score / max_score * 100) if max_score > 0 else 0

            if percentage >= 80:
                status = "✅ Strong"
            elif percentage >= 60:
                status = "⚠️ Fair"
            elif percentage >= 40:
                status = "⚠️ Needs Work"
            else:
                status = "❌ Weak"

            breakdown_text += f"| {category} | {score}/{max_score} | {status} |\n"

        breakdown_text += f"\n**Total: {self.total_score}/100** ({self.tier})\n"
        return breakdown_text

    def generate_pr_description(self):
        """Generate PR description for Braxis context files - unified messaging for both cases.

        Case 1 (no existing files): "Here are fresh files + install Braxis to keep them auto-updated"
        Case 2 (existing files):    "Here are recommended sections from yours + install Braxis to keep everything auto-updated"

        Both cases end with the same value: Install Braxis for continuous auto-updates
        """
        existing = self.detect_existing_agents_md()
        ai_readiness = f"{self.total_score}/100 ({self.tier})"
        score_breakdown = self._format_score_breakdown()

        # ALWAYS start with: We generated these files
        summary = f"""# Braxis: AI Context Files + Continuous Auto-Update

We've analyzed {self.project_path.name} and generated AI-ready context files:

- **AGENTS.md** — AI agent guidance + architecture documentation
- **CLAUDE.md** — Quick reference router to AGENTS.md
- **.cursorrules** — IDE/Claude Code conventions
- **.agentic-config.json** — Agent configuration

**AI Readiness Score:** {ai_readiness}

{score_breakdown}
---
"""

        # CASE 1: No existing MD files
        if not existing:
            summary += f"""
## What You're Getting

Fresh, automatically-generated AI context files for {self.project_path.name}:

```
Project:         {self.project_path.name}
Languages:       {', '.join(self.languages.keys()) if self.languages else 'Unknown'}
Build System:    {self.build_system or 'Unknown'}
Test Frameworks: {', '.join(self.test_frameworks) if self.test_frameworks else 'Unknown'}
AI Readiness:    {ai_readiness}
Total Files:     {len(self.files)}
Test Files:      {len(self.test_files)}
"""
            if self.monorepo_type:
                summary += f"Monorepo Type:   {self.monorepo_type.upper()} with {len(self.monorepo_subsystems)} subsystems\n"
            summary += "```\n"

            summary += """
## How to Use These Files

1. **Review this PR** to see what we auto-discovered about your project
2. **Accept the PR** to add all 4 files to your repo
3. **Customize if needed** for your specific project requirements

## Keep Them Fresh: Install Braxis for Auto-Updates

These files are valuable today. But their **real power is staying in sync** with your code as it evolves.

Every time your codebase changes:
- New test frameworks get auto-detected
- Architecture documentation stays current
- AI readiness score tracks improvements automatically
- Entry points update as files move

### Setup Automatic Updates (Recommended)

Add this GitHub Actions workflow to keep your AI context files fresh:

```yaml
# .github/workflows/ai-context.yml
name: Auto-Update AI Context Files

on:
  push:
    branches: [main, master]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  update-context:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install braxis
      - run: braxis generate --smart-merge --path .
      - uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'chore: auto-update AI context files'
          title: 'Auto: Update AI context files'
          branch: braxis/auto-update
```

**Once installed, Braxis will:**
- ✅ Regenerate files on every code push (plus weekly safety check)
- ✅ Preserve any custom sections you add
- ✅ Create PRs for review - never commits directly
- ✅ Keep AI readiness score current
- ✅ Require zero manual maintenance

### 💡 Even If You Reject This PR

Not ready to add these files to your repo? **You can still benefit from Braxis:**

- ✅ Install just the GitHub Actions workflow (skip the file commit)
- ✅ Braxis will generate context files on your machine/CI system
- ✅ Use them for local AI agent guidance without repo changes
- ✅ When ready, the files are ready to merge - no wasted setup

**The workflow is flexible - use what helps you most.**

## Next Steps

1. **Short-term:** Merge this PR to add the 4 files (recommended) OR just use the workflow
2. **Long-term:** Install the GitHub Actions workflow above for auto-updates
3. **Ongoing:** Your AI agents will always have fresh context

**Note:** The workflow works with or without accepting these files.
"""

        # CASE 2: Existing high-quality MD files
        else:
            summary += f"""
## We Detected Your Existing Files (Quality Score: {existing['score']}/100)

You already have valuable custom content in your existing AGENTS.md:
"""
            # List what they have
            custom_sections = [s for s in existing['sections']
                             if s in ['Skills', 'Package Domain', 'Key Entry Point', 'Gotcha', 'Governance', 'API Reference']]
            if custom_sections:
                for section in custom_sections:
                    summary += f"- ✅ **{section}** — Hand-written expertise\n"
            else:
                summary += f"- ✅ Custom AGENTS.md with {len(existing['sections'])} sections\n"

            summary += f"""
We respect this expertise and recommend **keeping it**.

### ⭐ The Real Win: Auto-Update While Preserving Your Work

Even if you choose to keep your existing AGENTS.md now, **installing Braxis enables continuous auto-updates that respect your custom work**:

- **When:** On significant code changes (src files, architecture, dependencies) + weekly safety check
- **What happens:** Braxis regenerates all 4 files using `--smart-merge` (skips trivial changes like docs/comments)
- **Your sections:** Automatically preserved (Skills, Governance, Package Domains, API Reference, etc.)
- **New content:** Auto-discovered architecture, test frameworks, entry points stay current
- **How:** Creates a PR for review - you always see the changes before merging

**This is the real value:** Your custom expertise stays intact, but the auto-generated parts stay fresh with your code changes.

## What This PR Suggests

We've generated new context files based on current code analysis:

### Recommended Approach

**Option A (Recommended): Keep Your Files + Get Auto-Update Capability**
- ✅ Keep your existing, hand-maintained AGENTS.md
- ✅ Accept our CLAUDE.md + .cursorrules + .agentic-config.json
- ✅ Install Braxis so these files auto-update going forward

> **How Option A Works with Auto-Updates:**
>
> When you install Braxis (via the GitHub Actions workflow), it intelligently regenerates on significant changes:
> 1. **Detects** significant code changes (source files, architecture, dependencies)
> 2. **Skips** trivial changes (docs, comments, formatting) to avoid noise
> 3. **Regenerates** context files when it matters using `--smart-merge`
> 4. **Automatically preserves** your custom sections (Skills, Governance, Architecture notes, etc.)
> 5. **Adds new auto-discovered content** (updated entry points, test frameworks, etc.)
> 6. Creates a PR for you to review before merging
>
> **Your custom AGENTS.md sections stay yours.** Braxis just keeps the auto-discovered parts fresh when your code actually changes.

**Option B: Review New Sections**
- Look at our generated AGENTS.md
- Copy any sections you find valuable
- Merge them into your existing file manually
- Install Braxis for auto-updates

**Option C: Accept All Files**
- Use our generated versions
- Customize them after merge
- Install Braxis for auto-updates

## Keep Everything Auto-Updated: Install Braxis

The real value isn't these initial files—it's **keeping your AI context fresh automatically** as your codebase evolves.

Whether you choose Option A, B, or C, install this GitHub Actions workflow:

```yaml
# .github/workflows/ai-context.yml
name: Auto-Update AI Context Files

on:
  push:
    branches: [main, master, devel]
  schedule:
    - cron: '0 0 * * 0'  # Weekly fallback

jobs:
  detect-changes:
    name: Check for Significant Changes
    runs-on: ubuntu-latest
    outputs:
      significant: ${{ steps.check.outputs.significant }}
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - name: Detect Significant Changes
        id: check
        run: |
          python3 -c "
          import subprocess, os
          files = subprocess.run(['git', 'diff', '--name-only', 'origin/main...HEAD'],
                               capture_output=True, text=True).stdout.split()

          # Source code changes = regenerate
          src_changes = any(f.endswith(('.py', '.js', '.ts', '.java', '.go')) for f in files)
          build_changes = any('package.json' in f or 'setup.py' in f for f in files)
          struct_changes = any('src/' in f or 'lib/' in f or 'packages/' in f for f in files)

          significant = src_changes or build_changes or struct_changes
          with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
              f.write('significant=' + str(significant).lower())
          "

  update-context:
    name: Update AI Context Files
    runs-on: ubuntu-latest
    needs: detect-changes
    if: needs.detect-changes.outputs.significant == 'true' || github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v3
      - run: pip install braxis
      - run: braxis generate --smart-merge --path .
      - uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'chore: auto-update AI context files'
          title: 'Auto: Update AI context files'
          branch: braxis/auto-update
```

**Why this matters:**
- Detects significant code changes (source files, architecture, dependencies)
- Skips regeneration for trivial changes (docs, comments, formatting)
- Regenerates on every code push (when it matters) + weekly safety check
- Uses `--smart-merge` to preserve your hand-written sections
- Creates PRs for you to review and merge
- Keeps AI readiness score current without noise
- **Zero manual maintenance, minimal PR spam**

### 💡 Even If You Reject This PR

Choosing not to merge this PR? **Installing Braxis still helps:**

- ✅ Your existing AGENTS.md stays unchanged
- ✅ Braxis auto-detects your custom file using smart-merge
- ✅ Weekly auto-updates keep your context fresh (no noise, only significant changes)
- ✅ Your hand-written sections are always preserved
- ✅ New auto-discovered content integrates smoothly

**The decision is yours on the files, but the workflow benefit is always available.**

Even repo owners who prefer their own AGENTS.md can benefit from continuous updates that respect their choices.

## Next Steps

1. **Choose your option** (A, B, or C above)
2. **Merge this PR** with your choice (or decline it)
3. **Install the workflow** for automatic updates
4. Your AI context stays fresh going forward

**Note:** Installing the Braxis workflow works whether you merge this PR or not.
"""

        # ALWAYS end with the unified call to action
        summary += f"""

---

## Summary: The Value Braxis Provides

**Immediate:** Fresh AI context files (or validation of your existing ones)
**Ongoing:** Automatic updates keep context in sync with code changes

### To Keep Your AI Context Files Up-to-Date

✅ **Install Braxis** (add the GitHub Actions workflow above)

This ensures:
- Your AGENTS.md, CLAUDE.md, .cursorrules, and .agentic-config.json stay current
- AI agents always have accurate project information
- No manual updates needed - Braxis handles it automatically
- AI readiness score tracked over time

---

**Questions?**
- See [Braxis docs](https://github.com/jaykrishna316/braxis) for more info
- Check the AI readiness breakdown in the generated AGENTS.md

**Generated by [Braxis](https://github.com/jaykrishna316/braxis)** — Keeping AI agents in sync with your code
"""
        return summary

    def merge_file_content(self, filename, existing, new_content):
        """
        Intelligently merge existing custom content with new auto-generated content.
        Works for any text file: AGENTS.md, CLAUDE.md, .cursorrules, .agentic-config.json
        """
        if not existing or existing['score'] < 40:
            # Existing file is low quality, replace entirely
            return new_content

        # For Markdown files (.md), preserve custom sections
        if filename.endswith('.md'):
            preserved_sections = [
                'Skills', 'Package Domain', 'Key Entry Point',
                'Gotcha', 'Governance', 'Notes', 'Contributing Guidelines',
                'API Reference', 'Architecture Diagram'
            ]

            merged_lines = []
            new_lines = new_content.split('\n')
            existing_sections = existing['sections']

            # Preserve header
            if new_lines:
                merged_lines.append(new_lines[0])  # Title
                merged_lines.append('')

            # Insert preserved custom sections before auto-generated content
            for section_name in preserved_sections:
                if section_name in existing_sections:
                    merged_lines.append(f'## {section_name}')
                    merged_lines.append('')
                    merged_lines.append(existing_sections[section_name])
                    merged_lines.append('')
                    merged_lines.append('---')
                    merged_lines.append('')

            # Append new content
            merged_lines.extend(new_lines[1:] if len(new_lines) > 1 else [])

            # Add preservation note
            merged_content = '\n'.join(merged_lines)
            merged_content += '\n\n> **Note:** This file was regenerated while preserving custom sections from the previous version.\n'
            return merged_content

        # For config files (.cursorrules, .agentic-config.json), do simple preservation
        # If existing file is high quality, keep it as-is
        if existing['score'] >= 60:
            return existing['content']
        else:
            # Low-medium quality: return new generated content
            return new_content

    def merge_agents_md(self, existing, new_content):
        """Merge for AGENTS.md (delegates to generic merge_file_content)."""
        return self.merge_file_content('AGENTS.md', existing, new_content)

    def generate_agents_md(self):
        """v1.4: Generate dual-format AGENTS.md with Category A (Operations) + Category B (Context)."""
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

        # Get detected naming pattern, with language-specific default
        naming_pattern = getattr(self, 'naming_pattern', None) or self._detect_naming_patterns()
        if naming_pattern == "snake_case":
            naming_desc = "Use snake_case for functions and variables"
        elif naming_pattern == "camelCase":
            naming_desc = "Use camelCase for functions and variables"
        elif naming_pattern == "PascalCase":
            naming_desc = "Use PascalCase for classes and type names"
        else:
            naming_desc = f"Follow {primary_lang.capitalize()} conventions (observed: {naming_pattern})"

        arch_score = self.score_breakdown.get('Architecture', 0)
        test_score = self.score_breakdown.get('Testing', 0)
        dep_score = self.score_breakdown.get('Dependencies', 0)
        conv_score = self.score_breakdown.get('Conventions', 0)
        entry_score = self.score_breakdown.get('Entry Points', 0)
        sec_score = self.score_breakdown.get('Security', 0)
        build_score = self.score_breakdown.get('Build', 0)
        doc_score = self.score_breakdown.get('Documentation', 0)

        # v1.4: Extract both Category A and Category B content
        category_a_content = self._extract_category_a_content()
        category_a_section = self._format_category_a_section(category_a_content)

        # v1.3.1: Generate new sections for Category B
        arch_tables = self._generate_architecture_tables()
        env_requirements = self._detect_environment_requirements()
        gotchas = self._extract_gotchas_from_contributing()

        # v1.3.2: Language-specific commands
        dev_commands = self._get_development_commands(primary_lang)
        init_commands = self._get_initial_setup_commands(primary_lang)
        testing_strategy = self._get_testing_strategy_commands(primary_lang)

        gotchas_section = ""
        if gotchas:
            gotchas_list = '\n'.join([f"- {g}" for g in gotchas])
            gotchas_section = f"""## Known Gotchas & Warnings

{gotchas_list}

"""

        return f"""# AGENTS.md

Context file for AI agents working on {self.project_path.name}.

**Dual Format**: This file combines Category A (Operations Manual) and Category B (Context Guide) for comprehensive agent guidance.

## Project Overview

{self.project_path.name} is a {primary_lang.capitalize()} project using {self.build_system}.

**Key Info:**
- **Primary Language:** {primary_lang.capitalize()}
- **Build System:** {self.build_system}
- **Test Framework:** {test_frameworks_str}
- **Total Files:** {len(self.files)}
- **Test Files:** {len(self.test_files)}
- **AI Readiness Score:** {self.total_score}/100 ({self.tier})

---

{category_a_section}

## 🏗️ Architecture & Context Guide

This section provides architectural context and agent-understanding for the codebase.

### Prerequisites

- **{primary_lang.capitalize()}:** {self._get_language_version_requirement()} (or applicable language version)
- **Package Manager:** {self._get_package_manager_recommendation()}
- **Test Runner:** {test_frameworks_str}

{env_requirements}

### Project Structure

```
{structure}
```

### Architecture Overview

#### Key Components
- **Main Entry:** {critical_files_info}
- **Test Suite:** {len(self.test_files)} test files
- **Build Configuration:** {build_config}

#### Design Principles

1. **Modularity** - Code organized by functionality with clear separation of concerns
2. **Testability** - Comprehensive test coverage across critical paths
3. **Clarity** - Explicit naming and structure for AI agent understanding
4. **Consistency** - Uniform patterns and conventions throughout codebase
5. **Maintainability** - Well-documented code with clear intent

{arch_tables}

### Development Workflow

#### Initial Setup

```bash
git clone {self.repository_url}
cd {self.project_path.name}
{init_commands}
```

#### Development Commands

**Running Tests:**
{dev_commands}

### Code Style & Conventions

- **Naming:** {naming_desc}
- **Type Hints:** {type_hints_status} (strongly encouraged)
- **Error Handling:** {error_handling_status} - handle errors at boundaries; let exceptions propagate when another layer owns recovery
- **Logging:** {logging_status}
- **Testing:** {testing_status} - write tests alongside code changes

### Testing Strategy

**Framework:** {test_frameworks_str}
**Test Files:** {len(self.test_files)} found

{testing_strategy}

### Writing Documentation

When updating docs:
1. Always include explanatory text before code snippets
2. Describe *why* and *what* before showing *how*
3. Keep sections focused on a single concept
4. Use clear, concrete examples

{gotchas_section}### Contributing Guidelines

{self._contribution_section_text()}

### Common Patterns

When contributing to this project:
1. Read existing code in the area you're modifying
2. Follow the established patterns and style
3. Write tests for new functionality
4. Use clear, descriptive variable and function names
5. Add docstrings for public APIs
6. Update tests when changing behavior

### What We Value

✅ Well-tested code with clear intent
✅ Consistent code style and naming conventions
✅ Code that is easy for AI agents to understand
✅ Clear, descriptive commit messages
✅ Modular, reusable components
✅ Comprehensive documentation

### What We Avoid

❌ Large functions doing multiple things
❌ Commented-out dead code
❌ Inconsistent naming or patterns
❌ Unclear error messages
❌ Unexplained magic numbers or strings
❌ Skipped tests or test TODOs

### AI Readiness Dimensions (Scoring)

This project is evaluated across 8 dimensions:

1. **Architecture** ({arch_score}/100) - Code organization and modularity
2. **Testing** ({test_score}/100) - Test coverage and quality
3. **Dependencies** ({dep_score}/100) - Dependency management
4. **Conventions** ({conv_score}/100) - Consistent patterns
5. **Entry Points** ({entry_score}/100) - Clear main/start locations
6. **Security** ({sec_score}/100) - Input validation and error handling
7. **Build** ({build_score}/100) - Clear build/setup instructions
8. **Documentation** ({doc_score}/100) - Code and project documentation

### Next Steps

Before making changes:
1. Read relevant source files to understand the existing code
2. Look at existing tests for similar functionality
3. Follow the patterns you see in the codebase
4. Write tests for your changes
5. Run `pytest` to verify nothing breaks
6. Run code quality checks: `ruff check . && mypy .`
7. Format your code: `ruff format .`

---

*Generated by Braxis - keeping AI agents in sync with your code*
"""

    def _extract_project_caveats_for_claude_md(self):
        """Extract project-specific caveats and gotchas for CLAUDE.md."""
        caveats = []

        # Read README for gotchas
        readme_candidates = [self.project_path / 'README.md', self.project_path / 'README.rst']
        for readme in readme_candidates:
            if readme.exists():
                try:
                    content = readme.read_text()
                    lines = content.split('\n')
                    for line in lines:
                        line_lower = line.lower()
                        if any(kw in line_lower for kw in ['caveat', 'gotcha', 'warning', 'limitation', 'known issue', 'important:', 'note:']):
                            clean = line.strip().lstrip('-*>').strip()
                            if clean and len(clean) > 15 and clean not in caveats:
                                caveats.append(clean)
                except (IOError, UnicodeDecodeError):
                    pass

        # Read CONTRIBUTING.md for additional gotchas
        if self.contributing_guide['exists'] and self.contributing_guide['content']:
            content = self.contributing_guide['content']
            lines = content.split('\n')
            for line in lines:
                line_lower = line.lower()
                if any(kw in line_lower for kw in ['caveat', 'gotcha', 'warning', 'limitation', 'known issue', 'important:', 'note:']):
                    clean = line.strip().lstrip('-*>').strip()
                    if clean and len(clean) > 15 and clean not in caveats:
                        caveats.append(clean)

        return caveats[:8]  # Return top 8 caveats

    def _extract_api_quirks(self):
        """Extract API or architecture quirks from documentation."""
        quirks = []
        doc_files = [
            self.project_path / 'docs' / 'README.md',
            self.project_path / 'docs' / 'ARCHITECTURE.md',
            self.project_path / 'docs' / 'API.md',
            self.project_path / 'docs' / 'DESIGN.md'
        ]

        for doc_file in doc_files:
            if doc_file.exists():
                try:
                    content = doc_file.read_text()
                    if 'api' in doc_file.name.lower() or 'architecture' in doc_file.name.lower():
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if any(kw in line.lower() for kw in ['quirk', 'design decision', 'tradeoff', 'trade-off', 'different from', 'unlike']):
                                clean = line.strip().lstrip('-*>').strip()
                                if clean and len(clean) > 15:
                                    quirks.append(clean)
                except (IOError, UnicodeDecodeError):
                    pass

        return quirks[:5]

    def generate_claude_md(self):
        """Generate project-specific CLAUDE.md with real caveats and quirks."""
        primary_lang = max(self.languages.items(), key=lambda x: x[1])[0] if self.languages else "Unknown"
        caveats = self._extract_project_caveats_for_claude_md()
        quirks = self._extract_api_quirks()

        caveats_section = ""
        if caveats:
            caveats_text = '\n'.join([f"- {c}" for c in caveats])
            caveats_section = f"""## Project-Specific Caveats

{caveats_text}

"""

        quirks_section = ""
        if quirks:
            quirks_text = '\n'.join([f"- {q}" for q in quirks])
            quirks_section = f"""## Architecture & API Quirks

{quirks_text}

"""

        return f"""# CLAUDE.md

@AGENTS.md

This project uses AGENTS.md as the standard agent context. Claude Code loads it automatically via the @AGENTS.md import above.

## Project: {self.project_path.name}

**Language:** {primary_lang.capitalize()} | **Build:** {self.build_system} | **Score:** {self.total_score}/100

---

{caveats_section}{quirks_section}## Quick Reference for Claude

### Before You Start
1. **Read AGENTS.md first** for full project architecture and workflow
2. **Check the caveats above** — they're extracted from this project's docs
3. **Run tests locally** before suggesting code changes
4. **Follow AGENTS.md conventions** for code style

### Key Commands
```bash
# Regenerate AI context files
braxis generate

# View AI readiness score
braxis score

# See score trends
braxis history --trends
```

### Testing Workflow
```bash
{', '.join(sorted(self.test_frameworks)) if self.test_frameworks else 'pytest'}
```

### Code Quality
```bash
ruff check .          # Lint
ruff format .         # Format
mypy .               # Type check
```

---

See AGENTS.md for complete project documentation.

*Generated by Braxis - keeping AI agents in sync with {self.project_path.name}*
"""

    def _generate_language_specific_cursorrules(self, primary_lang, test_frameworks_str):
        """Generate language-specific cursor rules."""
        base_rules = """## Must-Follow Rules

### Code Style & Formatting"""

        if primary_lang == "python":
            return f"""{base_rules}

1. Use **ruff** for formatting: `ruff format .`
2. Use **ruff** for linting: `ruff check .`
3. Python conventions: **snake_case** for functions/variables, **PascalCase** for classes
4. Type hints: Required for all public functions using **mypy** for checking
5. Docstrings: Use triple-quoted strings for all public functions and classes
6. No commented-out code, no dead code
7. Max line length: 100 characters

### Testing
1. Framework: {test_frameworks_str}
2. Test file naming: `test_*.py` or `*_test.py`
3. Test discovery: `pytest` finds and runs all tests
4. Fixtures: Use pytest fixtures for setup/teardown
5. Coverage: Maintain 80%+ coverage for critical paths
6. Run before commit: `pytest -v`

### Imports & Dependencies
1. Use absolute imports, not relative imports (unless necessary)
2. Group imports: stdlib, third-party, local (isort style)
3. No wildcard imports (`from module import *`)
4. Pin versions in requirements.txt/pyproject.toml
5. Avoid circular dependencies

### Error Handling
1. Be specific with exception types (not bare `except:`)
2. Log errors before re-raising
3. Validate all function arguments at entry points
4. Use try/except at system boundaries (I/O, network, DB)
"""
        elif primary_lang in ["javascript", "typescript"]:
            return f"""{base_rules}

1. Use **Prettier** for formatting: `npm run format`
2. Use **ESLint** for linting: `npm run lint`
3. JavaScript/TypeScript conventions: **camelCase** for functions/variables, **PascalCase** for classes/components
4. Type hints: TypeScript or JSDoc for all public functions
5. No commented-out code, no dead code
6. Max line length: 100 characters
7. Use const/let, avoid var
8. Use arrow functions for callbacks, regular functions for methods

### Testing
1. Framework: Jest or Mocha
2. Test file naming: `*.test.js`, `*.spec.js`, or `__tests__/` directory
3. Test discovery: `npm test` runs all tests
4. Mocking: Use Jest mocks or sinon for dependencies
5. Async tests: Use async/await, not callbacks
6. Coverage: Maintain 80%+ coverage
7. Run before commit: `npm test`

### Imports & Dependencies
1. Use ES6 imports (`import ... from`)
2. Group imports: stdlib, third-party, local
3. No wildcard imports unless necessary
4. Pin versions in package.json (use ^, ~, or exact)
5. Avoid circular dependencies

### React/Component Rules (if applicable)
1. Functional components with hooks, not class components
2. Custom hooks for shared logic (prefix with `use`)
3. Props must be validated (PropTypes or TypeScript)
4. Separate presentational from container components
"""
        elif primary_lang == "go":
            return f"""{base_rules}

1. Use **gofmt** for formatting: `go fmt ./...`
2. Use **golint** for linting: `golangci-lint run ./...`
3. Go conventions: **camelCase** for local variables/functions, **PascalCase** for exported functions
4. No type comments needed (Go's type system is strict)
5. Error handling: Always check and handle errors explicitly
6. Max line length: 100 characters
7. Use interfaces for abstraction, not inheritance

### Testing
1. Framework: Go's built-in `testing` package
2. Test file naming: `*_test.go`
3. Benchmarks: `BenchmarkXxx` for performance tests
4. Coverage: `go test -cover ./...`
5. Table-driven tests: Use test case slices for multiple scenarios
6. Run before commit: `go test -v ./...`

### Imports & Dependencies
1. Use `go.mod` for dependency management
2. Organize imports: stdlib, external, local
3. Use `import` blocks, not individual imports
4. No vendoring unless required

### Error Handling
1. Use sentinel values or custom error types
2. Wrap errors: `fmt.Errorf("context: %w", err)`
3. No panic in libraries (only in main)
4. Check errors immediately after operation
"""
        elif primary_lang == "rust":
            return f"""{base_rules}

1. Use **rustfmt** for formatting: `cargo fmt`
2. Use **clippy** for linting: `cargo clippy`
3. Rust conventions: **snake_case** for functions/variables, **PascalCase** for types
4. Type hints: Required (Rust enforces at compile time)
5. No unsafe code without explicit justification in comments
6. Max line length: 100 characters
7. Use Result<T, E> for fallible operations, Option<T> for optional values

### Testing
1. Framework: Rust's built-in `#[cfg(test)]` module system
2. Test file naming: Tests live in `tests/` directory and alongside code as modules
3. Unit tests: `#[test]` attribute on functions
4. Integration tests: Separate `.rs` files in `tests/`
5. Coverage: Use `cargo tarpaulin` for coverage
6. Run before commit: `cargo test`

### Cargo & Dependencies
1. Keep `Cargo.toml` updated with all direct dependencies
2. Use workspace for monorepos: `[workspace]`
3. Specify versions explicitly (no `*`)
4. Minimize dependencies (Rust philosophy)

### Memory Safety (Critical)
1. Borrow checker: Understand ownership rules
2. Lifetimes: Explicit when multiple references exist
3. Mutability: Make intent clear (mut keyword)
4. No null pointer dereferences (Option/Result)
"""
        elif primary_lang == "cpp":
            return f"""{base_rules}

1. Use **clang-format** for formatting: `clang-format -i *.cpp`
2. Use **clang-tidy** for linting: `clang-tidy -fix *.cpp`
3. C++ conventions: **snake_case** for functions/variables, **PascalCase** for classes
4. Include guards or `#pragma once` for headers
5. Const correctness: Mark const methods, const references
6. Memory safety: Use smart pointers (unique_ptr, shared_ptr), not raw pointers
7. RAII: Resource Acquisition Is Initialization

### Testing
1. Framework: GoogleTest (gtest), Catch2, or Doctest
2. Test file naming: `*_test.cpp`, `test_*.cpp`
3. Fixtures: Use gtest TEST_F for setup/teardown
4. Mocking: Use gmock for complex dependencies
5. Coverage: Use gcov/lcov for coverage
6. Run before commit: `ctest`

### Compilation & Build
1. Use CMake: `mkdir build && cd build && cmake .. && make`
2. Compiler warnings: Treat warnings as errors (`-Werror`)
3. Enable optimizations: `-O2` or `-O3` for release builds
4. Sanitizers: Use `-fsanitize=address,undefined` for debug

### C++ Best Practices
1. No manual `new`/`delete` — use smart pointers
2. RAII pattern for all resources
3. Prefer standard library over manual implementation
4. Modern C++ (C++17+): Use structured bindings, auto, constexpr
5. No null pointers — use std::optional
"""
        else:
            # Generic fallback
            return f"""{base_rules}

1. Use language-appropriate formatter
2. Follow {primary_lang.capitalize()} naming conventions
3. Add type hints/signatures where supported
4. No commented-out code or dead code
5. Keep functions focused and single-purpose

### Testing
1. Framework: {test_frameworks_str}
2. Write tests for all new functionality
3. Coverage: Maintain high coverage for critical paths
4. Run before commit: `{test_frameworks_str if test_frameworks_str else 'test command'}`

### Project Structure
- Keep related code colocated
- Use clear, descriptive names
- Follow existing patterns in the codebase
"""

    def generate_cursorrules(self):
        """Generate language-specific .cursorrules file."""
        primary_lang = max(self.languages.items(), key=lambda x: x[1])[0] if self.languages else "Unknown"
        test_frameworks_str = ', '.join(sorted(self.test_frameworks)) if self.test_frameworks else 'pytest'

        arch_score = self.score_breakdown.get('Architecture', 0)
        test_score = self.score_breakdown.get('Testing', 0)
        dep_score = self.score_breakdown.get('Dependencies', 0)
        conv_score = self.score_breakdown.get('Conventions', 0)
        entry_score = self.score_breakdown.get('Entry Points', 0)
        sec_score = self.score_breakdown.get('Security', 0)
        build_score = self.score_breakdown.get('Build', 0)
        doc_score = self.score_breakdown.get('Documentation', 0)

        language_rules = self._generate_language_specific_cursorrules(primary_lang, test_frameworks_str)

        return f"""# Cursor Rules for {self.project_path.name}

## What This Project Does

**Language:** {primary_lang.capitalize()} | **Build:** {self.build_system}

**AI Readiness Score:** {self.total_score}/100 ({self.tier})

{language_rules}

## Scoring Dimensions (What Matters)

These 8 areas drive AI readiness. Focus on these when making changes:

1. **Architecture** ({arch_score}/15) - Code organization and modularity
2. **Testing** ({test_score}/15) - Test coverage and quality
3. **Dependencies** ({dep_score}/12) - Dependency management
4. **Conventions** ({conv_score}/10) - Consistent patterns
5. **Entry Points** ({entry_score}/10) - Clear main/start locations
6. **Security** ({sec_score}/15) - Input validation and error handling
7. **Build** ({build_score}/10) - Clear build/setup instructions
8. **Documentation** ({doc_score}/8) - Code and project documentation

## Before You Commit

```bash
# Format code
{self._get_format_command(primary_lang)}

# Lint check
{self._get_lint_command(primary_lang)}

# Run tests
{self._get_test_command(primary_lang)}
```

All checks must pass before committing.

## Questions?

See AGENTS.md for detailed documentation on architecture, development workflow, and testing strategy.

---

*Generated by Braxis - language-aware rules for {primary_lang.capitalize()} projects*
"""

    def _get_format_command(self, lang):
        """Get the format command for the language."""
        commands = {
            'python': 'ruff format .',
            'javascript': 'prettier --write .',
            'typescript': 'prettier --write .',
            'go': 'go fmt ./...',
            'rust': 'cargo fmt',
            'cpp': 'clang-format -i **/*.{cpp,h}',
            'java': 'google-java-format -i **/*.java',
            'csharp': 'dotnet format'
        }
        return commands.get(lang, 'Use language formatter')

    def _get_lint_command(self, lang):
        """Get the lint command for the language."""
        commands = {
            'python': 'ruff check .',
            'javascript': 'eslint .',
            'typescript': 'eslint .',
            'go': 'golangci-lint run ./...',
            'rust': 'cargo clippy',
            'cpp': 'clang-tidy **/*.cpp',
            'java': 'checkstyle src/**/*.java',
            'csharp': 'dotnet analyzers'
        }
        return commands.get(lang, 'Use language linter')

    def _get_test_command(self, lang):
        """Get the test command for the language."""
        commands = {
            'python': 'pytest',
            'javascript': 'npm test',
            'typescript': 'npm test',
            'go': 'go test ./...',
            'rust': 'cargo test',
            'cpp': 'ctest',
            'java': 'mvn test',
            'csharp': 'dotnet test'
        }
        return commands.get(lang, 'Use language test runner')

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


__version__ = "1.3.0"


def main():
    parser = argparse.ArgumentParser(description='Braxis - AI agent context generator')
    parser.add_argument('--version', action='version', version=f'Braxis {__version__}')
    parser.add_argument('command', choices=['generate', 'score', 'inspect', 'validate', 'history'],
                        help='Command to run')
    parser.add_argument('--path', default='.', help='Project path')
    parser.add_argument('--trends', action='store_true', help='Show score trends')
    parser.add_argument('--smart-merge', action='store_true',
                        help='Intelligently merge existing custom sections with new content (preserve hand-maintained sections)')
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
                # v1.5: Smart merge logic for AGENTS.md
                new_agents_md = analyzer.generate_agents_md()
                if args.smart_merge:
                    existing = analyzer.detect_existing_agents_md()
                    if existing and existing['score'] >= 40:
                        print(f"  Smart merge: Preserving {len(existing['sections'])} custom sections (quality score: {existing['score']}/100)")
                        agents_md_content = analyzer.merge_agents_md(existing, new_agents_md)
                    else:
                        agents_md_content = new_agents_md
                else:
                    # Check if existing file would be lost and warn user
                    existing = analyzer.detect_existing_agents_md()
                    if existing and existing['score'] >= 50:
                        print(f"  ℹ️  Existing AGENTS.md has custom content (quality: {existing['score']}/100)")
                        print(f"     Use --smart-merge to preserve custom sections")
                    agents_md_content = new_agents_md

                analyzer._write_file_safely('AGENTS.md', agents_md_content)
                print("* AGENTS.md")

            # Smart-merge for CLAUDE.md
            new_claude_md = analyzer.generate_claude_md()
            if args.smart_merge:
                existing_claude = analyzer.detect_existing_file('CLAUDE.md')
                if existing_claude and existing_claude['score'] >= 40:
                    print(f"  Smart merge: Preserving CLAUDE.md (quality score: {existing_claude['score']}/100)")
                    claude_md_content = analyzer.merge_file_content('CLAUDE.md', existing_claude, new_claude_md)
                else:
                    claude_md_content = new_claude_md
            else:
                existing_claude = analyzer.detect_existing_file('CLAUDE.md')
                if existing_claude and existing_claude['score'] >= 50:
                    print(f"  ℹ️  Existing CLAUDE.md has custom content (quality: {existing_claude['score']}/100)")
                    print(f"     Use --smart-merge to preserve it")
                claude_md_content = new_claude_md
            analyzer._write_file_safely('CLAUDE.md', claude_md_content)
            print("* CLAUDE.md")

            # Smart-merge for .cursorrules
            new_cursorrules = analyzer.generate_cursorrules()
            if args.smart_merge:
                existing_cursorrules = analyzer.detect_existing_file('.cursorrules')
                if existing_cursorrules and existing_cursorrules['score'] >= 40:
                    print(f"  Smart merge: Preserving .cursorrules (quality score: {existing_cursorrules['score']}/100)")
                    cursorrules_content = analyzer.merge_file_content('.cursorrules', existing_cursorrules, new_cursorrules)
                else:
                    cursorrules_content = new_cursorrules
            else:
                existing_cursorrules = analyzer.detect_existing_file('.cursorrules')
                if existing_cursorrules and existing_cursorrules['score'] >= 50:
                    print(f"  ℹ️  Existing .cursorrules has custom content (quality: {existing_cursorrules['score']}/100)")
                    print(f"     Use --smart-merge to preserve it")
                cursorrules_content = new_cursorrules
            analyzer._write_file_safely('.cursorrules', cursorrules_content)
            print("* .cursorrules")

            # Smart-merge for .agentic-config.json
            new_agentic_config = analyzer.generate_agentic_config()
            if args.smart_merge:
                existing_agentic = analyzer.detect_existing_file('.agentic-config.json')
                if existing_agentic and existing_agentic['score'] >= 40:
                    print(f"  Smart merge: Preserving .agentic-config.json (quality score: {existing_agentic['score']}/100)")
                    agentic_config_content = analyzer.merge_file_content('.agentic-config.json', existing_agentic, new_agentic_config)
                else:
                    agentic_config_content = new_agentic_config
            else:
                existing_agentic = analyzer.detect_existing_file('.agentic-config.json')
                if existing_agentic and existing_agentic['score'] >= 50:
                    print(f"  ℹ️  Existing .agentic-config.json has custom content (quality: {existing_agentic['score']}/100)")
                    print(f"     Use --smart-merge to preserve it")
                agentic_config_content = new_agentic_config
            analyzer._write_file_safely('.agentic-config.json', agentic_config_content)
            print("* .agentic-config.json")

            # v1.1: Report MCP and monorepo info
            if analyzer.monorepo_type:
                print(f"\n✓ Monorepo detected: {analyzer.monorepo_type.upper()} with {len(analyzer.monorepo_subsystems)} subsystems")
            if analyzer.mcp_servers:
                print(f"✓ MCP servers detected: {len(analyzer.mcp_servers)} server(s)")

            scale = analyzer.analyze_project_scale()
            if scale in ('large', 'medium'):
                suggestion = analyzer.suggest_contribution_boundaries()
                if suggestion:
                    print(f"\n💡 Project Scale ({scale}): {suggestion}")

            print(f"\nAgent Readiness: {analyzer.total_score}/100 ({analyzer.tier})")
            print("\nFiles created successfully!")
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
