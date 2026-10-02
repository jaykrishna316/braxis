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

    def get_llm_recommendations(self):
        """Get intelligent recommendations using Claude API."""
        try:
            import anthropic
        except ImportError:
            print("Claude API not available. Install with: pip install braxis[llm]")
            return None

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("ANTHROPIC_API_KEY not set. Skipping LLM recommendations.")
            print("Set your API key: export ANTHROPIC_API_KEY='sk-ant-...'")
            return None

        try:
            client = anthropic.Anthropic(api_key=api_key)

            # Build project analysis summary
            analysis_summary = f"""
Project: {self.project_path.name}
Agent Readiness Score: {self.total_score}/100 ({self.tier})

Score Breakdown:
{self._format_score_breakdown()}

Project Details:
- Languages: {', '.join(self.languages.keys()) if self.languages else 'None detected'}
- Build System: {self.build_system}
- Test Frameworks: {', '.join(self.test_frameworks)}
- Test Files: {len(self.test_files)}
- Total Files: {len(self.files)}
- Critical Files: {len(self.critical_files)}
- Config Files: {len(self.config_files)}

Detected Conventions:
- Error Handling: {'Yes' if 'error_handling' in self.conventions else 'No'}
- Type Hints: {'Yes' if 'type_hints' in self.conventions else 'No'}
- Logging: {'Yes' if 'logging' in self.conventions else 'No'}
- Validation: {'Yes' if 'validation' in self.conventions else 'No'}
- Async Patterns: {'Yes' if 'async' in self.conventions else 'No'}
"""

            prompt = f"""Based on this project analysis, provide 5-7 specific, actionable recommendations to improve AI agent readiness and code quality:

{analysis_summary}

Format your response as a numbered list with:
1. A clear title for each recommendation
2. Why it matters (1-2 sentences)
3. How to implement it (concrete steps)

Focus on high-impact improvements that would increase the Agent Readiness Score."""

            response = client.messages.create(
                model="claude-opus-5-5",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract text from response
            recommendations = ""
            for block in response.content:
                if block.type == "text":
                    recommendations += block.text

            return recommendations

        except anthropic.APIError as e:
            print(f"API Error: {e.message}")
            return None
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return None

    def _format_score_breakdown(self):
        """Format score breakdown for display."""
        lines = []
        for category, score in self.score_breakdown.items():
            lines.append(f"  {category}: {score}/100")
        return "\n".join(lines)

    def analyze(self):
        """Analyze the project."""
        self._scan_files()
        self._detect_languages()
        self._detect_build_system()
        self._detect_test_framework()
        self._detect_conventions()
        self._identify_critical_files()
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

    def _detect_build_system(self):
        """Detect build system."""
        build_system = "Unknown"
        if any('package.json' in str(f) for f in self.build_files):
            build_system = "npm/Node.js"
        elif any('pyproject.toml' in str(f) or 'setup.py' in str(f) for f in self.build_files):
            build_system = "Python (pip/setuptools)"
        elif any('Cargo.toml' in str(f) for f in self.build_files):
            build_system = "Rust (cargo)"
        elif any('go.mod' in str(f) for f in self.build_files):
            build_system = "Go (go modules)"
        elif any('pom.xml' in str(f) for f in self.build_files):
            build_system = "Java (Maven)"
        self.build_system = build_system

    def _detect_test_framework(self):
        """Detect test framework."""
        test_frameworks = set()
        content_samples = self._sample_file_contents(limit=20)
        for content in content_samples:
            if 'pytest' in content or 'from pytest' in content:
                test_frameworks.add('pytest')
            if 'unittest' in content or 'import unittest' in content:
                test_frameworks.add('unittest')
            if 'jest' in content or 'describe(' in content:
                test_frameworks.add('Jest')
            if 'mocha' in content or 'describe(' in content:
                test_frameworks.add('Mocha')
            if 'rspec' in content or 'describe' in content:
                test_frameworks.add('RSpec')
            if 'junit' in content.lower():
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

    def generate_agents_md(self):
        """Generate comprehensive AGENTS.md file."""
        primary_lang = max(self.languages.items(), key=lambda x: x[1])[0] if self.languages else "Unknown"
        
        # Build vars for the template
        structure = self.project_path.name + "/"
        if self.build_files:
            for f in self.build_files[:3]:
                structure += "\n├── " + f.name
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

- **{primary_lang.capitalize()}:** 3.9+ (or applicable language version)
- **Package Manager:** pip or uv (recommended)
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
git clone https://github.com/<owner>/{self.project_path.name}.git
cd {self.project_path.name}
pip install -e .              # Install in development mode
# or
uv sync --all-groups          # Using uv (recommended)
```

### Development Commands

#### Running Tests
```bash
pytest                        # Run all tests
pytest tests/                 # Run specific test directory
pytest -v                     # Verbose output with test names
pytest -x                     # Stop on first failure
pytest --cov                  # With coverage report
```

#### Code Quality
```bash
ruff check .                  # Lint with ruff
ruff format .                 # Format code
mypy .                        # Type checking (if configured)
```

## Code Style & Conventions

- **Naming:** Use {primary_lang.capitalize()} conventions (snake_case for functions, PascalCase for classes)
- **Type Hints:** {type_hints_status} (strongly encouraged)
- **Error Handling:** {error_handling_status}
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

## Next Steps

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

    def generate_claude_md(self):
        """Generate CLAUDE.md as a router to AGENTS.md."""
        return """# CLAUDE.md

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

See AGENTS.md for full documentation and the complete list of available commands.

---

*Generated by Braxis*
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
                "architecture": "single-package",
                "is_monorepo": False
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
            "mcp_servers": [],
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


__version__ = "1.0.0"


def main():
    parser = argparse.ArgumentParser(description='Braxis - AI agent context generator')
    parser.add_argument('--version', action='version', version=f'Braxis {__version__}')
    parser.add_argument('command', choices=['generate', 'score', 'inspect', 'validate', 'history', 'recommendations'],
                        help='Command to run')
    parser.add_argument('--path', default='.', help='Project path')
    parser.add_argument('--trends', action='store_true', help='Show score trends')
    args = parser.parse_args()

    if not args.command or args.command not in ['generate', 'score', 'inspect', 'validate', 'history', 'recommendations']:
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

    if args.command == 'recommendations':
        try:
            analyzer = BraxisAnalyzer(args.path)
            analyzer.analyze()
            print("\nGenerating AI-powered recommendations...")
            recommendations = analyzer.get_llm_recommendations()
            if recommendations:
                print(f"\n{'='*60}")
                print(f"LLM-Powered Recommendations for {analyzer.project_path.name}")
                print(f"{'='*60}\n")
                print(recommendations)
                print(f"\n{'='*60}\n")
            else:
                print("Could not generate recommendations.")
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
            analyzer._write_file_safely('AGENTS.md', analyzer.generate_agents_md())
            print("* AGENTS.md")
            analyzer._write_file_safely('CLAUDE.md', analyzer.generate_claude_md())
            print("* CLAUDE.md")
            analyzer._write_file_safely('.cursorrules', analyzer.generate_cursorrules())
            print("* .cursorrules")
            analyzer._write_file_safely('.agentic-config.json', analyzer.generate_agentic_config())
            print("* .agentic-config.json")
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
