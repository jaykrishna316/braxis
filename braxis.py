#!/usr/bin/env python3
"""
Braxis - Auto-generate AI agent context files.
Keep AGENTS.md, CLAUDE.md, .cursorrules, and .agentic-config.json in sync with your codebase.
"""
import os
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime


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
        self.project_path = Path(project_path)
        self.files = []
        self.languages = defaultdict(int)
        self.test_files = []
        self.config_files = []
        self.build_files = []
        self.conventions = defaultdict(int)
        self.critical_files = []
        self.score_breakdown = {}
        self.tier = "Not Ready"

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
        """Generate AGENTS.md file."""
        primary_lang = max(self.languages.items(), key=lambda x: x[1])[0] if self.languages else "Unknown"
        content = f"""# AGENTS.md
AI agents read this file to understand your project.
## Project Identity
This is a {primary_lang.capitalize()} project. It uses {self.build_system}.
## Tech Stack
- Language: {primary_lang.capitalize()}
- Build: {self.build_system}
- Testing: {', '.join(self.test_frameworks)}
- Total Files: {len(self.files)}
## Quick Start
"""
        return content

    def generate_claude_md(self):
        """Generate CLAUDE.md file."""
        primary_lang = max(self.languages.items(), key=lambda x: x[1])[0] if self.languages else "Unknown"
        content = f"""# CLAUDE.md
Quick context for Claude Code working in this project.
## Project
{primary_lang.capitalize()} project using {self.build_system}.
"""
        return content

    def generate_cursorrules(self):
        """Generate .cursorrules file."""
        primary_lang = max(self.languages.items(), key=lambda x: x[1])[0] if self.languages else "Unknown"
        rules = f"""# Cursor Rules
This is a {primary_lang.capitalize()} project using {self.build_system}.
"""
        return rules

    def generate_agentic_config(self):
        """Generate .agentic-config.json file."""
        primary_lang = max(self.languages.items(), key=lambda x: x[1])[0] if self.languages else "Unknown"
        config = {
            "name": self.project_path.name,
            "description": f"A {primary_lang.capitalize()} project",
            "language": primary_lang,
            "build_system": self.build_system,
            "agent_readiness_score": self.total_score,
            "tier": self.tier,
        }
        return json.dumps(config, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Braxis - AI agent context generator')
    parser.add_argument('command', choices=['generate', 'score', 'inspect', 'validate'],
                        help='Command to run')
    parser.add_argument('--path', default='.', help='Project path')
    args = parser.parse_args()

    analyzer = BraxisAnalyzer(args.path)
    analyzer.analyze()

    if args.command == 'score':
        analyzer.print_score()
    elif args.command == 'generate':
        print("Generating context files...")
        with open('AGENTS.md', 'w') as f:
            f.write(analyzer.generate_agents_md())
        print("* AGENTS.md")
        with open('CLAUDE.md', 'w') as f:
            f.write(analyzer.generate_claude_md())
        print("* CLAUDE.md")
        with open('.cursorrules', 'w') as f:
            f.write(analyzer.generate_cursorrules())
        print("* .cursorrules")
        with open('.agentic-config.json', 'w') as f:
            f.write(analyzer.generate_agentic_config())
        print("* .agentic-config.json")
        print(f"\nAgent Readiness: {analyzer.total_score}/100 ({analyzer.tier})")
        print("\nFiles created successfully!")
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
