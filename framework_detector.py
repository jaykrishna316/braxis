#!/usr/bin/env python3
"""
Framework Detection Module for Braxis
Provides AST-based framework detection with wrapper analysis and version extraction.
"""

import ast
import json
from pathlib import Path
from typing import Dict, Set, Tuple, Optional
from collections import defaultdict


class FrameworkDetector:
    """Deep AST-based framework detection for Python projects."""

    # Known framework import patterns
    FRAMEWORK_IMPORTS = {
        'fastapi': {'modules': ['fastapi'], 'classes': ['FastAPI']},
        'flask': {'modules': ['flask'], 'classes': ['Flask']},
        'django': {'modules': ['django'], 'classes': ['Django']},
        'starlette': {'modules': ['starlette'], 'classes': ['Starlette']},
        'pydantic': {'modules': ['pydantic'], 'classes': ['BaseModel']},
        'sqlalchemy': {'modules': ['sqlalchemy', 'sqlalchemy.orm'], 'classes': ['Column']},
        'pytest': {'modules': ['pytest', '_pytest'], 'classes': []},
        'unittest': {'modules': ['unittest'], 'classes': []},
        'requests': {'modules': ['requests'], 'classes': ['Session']},
        'numpy': {'modules': ['numpy'], 'classes': []},
        'pandas': {'modules': ['pandas'], 'classes': ['DataFrame']},
        'torch': {'modules': ['torch'], 'classes': ['Tensor']},
        'tensorflow': {'modules': ['tensorflow', 'tf'], 'classes': []},
    }

    def __init__(self, project_path: str):
        """Initialize framework detector."""
        self.project_path = Path(project_path).resolve()
        if not self.project_path.exists():
            raise ValueError(f"Project path not found: {project_path}")
        self.frameworks_found = {}

    def detect_frameworks(self, scan_depth: int = 1) -> Dict[str, Dict]:
        """
        Detect frameworks in the project.

        Args:
            scan_depth:
                0 = Pattern-based detection only (fastest)
                1 = AST-based direct imports (balanced)
                2 = Full deep detection with wrappers (slowest, most accurate)

        Returns:
            Dictionary mapping framework names to detection info
            {
                'fastapi': {
                    'version': '0.95.0',
                    'files': ['app.py'],
                    'direct': True,
                    'wrapped_by': []
                }
            }
        """
        frameworks = {}

        if scan_depth >= 1:
            frameworks.update(self._ast_based_detection())

        if scan_depth >= 2:
            frameworks.update(self._deep_wrapper_detection())

        # Extract versions for all found frameworks
        for framework in frameworks:
            version = self._extract_version(framework)
            frameworks[framework]['version'] = version

        return frameworks

    def _ast_based_detection(self) -> Dict[str, Dict]:
        """Parse imports from Python source files using AST."""
        frameworks = defaultdict(lambda: {'files': [], 'direct': True, 'wrapped_by': []})

        python_files = list(self.project_path.rglob('*.py'))

        for py_file in python_files:
            if self._should_skip(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                imports = self._extract_imports(tree)

                for module_name in imports:
                    framework = self._match_framework(module_name)
                    if framework:
                        relative_path = str(py_file.relative_to(self.project_path))
                        if relative_path not in frameworks[framework]['files']:
                            frameworks[framework]['files'].append(relative_path)

            except (SyntaxError, UnicodeDecodeError):
                # Skip files with encoding or syntax errors
                continue

        return dict(frameworks)

    def _deep_wrapper_detection(self) -> Dict[str, Dict]:
        """Detect frameworks imported within wrapper or extension modules."""
        frameworks = defaultdict(lambda: {'files': [], 'direct': False, 'wrapped_by': []})

        wrapper_patterns = [
            'wrapper', 'extension', 'custom', 'enhanced',
            '_internal', 'compat', 'shim', 'compat', 'adapter'
        ]

        python_files = list(self.project_path.rglob('*.py'))

        for py_file in python_files:
            if self._should_skip(py_file):
                continue

            # Check if filename suggests it's a wrapper
            is_wrapper = any(p in py_file.stem.lower() for p in wrapper_patterns)

            if not is_wrapper:
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                imports = self._extract_imports(tree)

                for module_name in imports:
                    framework = self._match_framework(module_name)
                    if framework:
                        relative_path = str(py_file.relative_to(self.project_path))
                        if relative_path not in frameworks[framework]['wrapped_by']:
                            frameworks[framework]['wrapped_by'].append(relative_path)
                        # Mark as potentially used via wrapper
                        frameworks[framework]['direct'] = False

            except (SyntaxError, UnicodeDecodeError):
                continue

        return dict(frameworks)

    def _extract_imports(self, tree: ast.AST) -> Set[str]:
        """Extract all imported module names from AST tree."""
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Get top-level module name (before first dot)
                    module = alias.name.split('.')[0]
                    imports.add(module)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Get top-level module name
                    module = node.module.split('.')[0]
                    imports.add(module)

        return imports

    def _extract_version(self, framework: str) -> str:
        """Extract framework version from requirements files."""
        # Try requirements.txt
        req_file = self.project_path / 'requirements.txt'
        if req_file.exists():
            version = self._parse_requirements_file(req_file, framework)
            if version:
                return version

        # Try pyproject.toml
        pyproject = self.project_path / 'pyproject.toml'
        if pyproject.exists():
            version = self._parse_pyproject_toml(pyproject, framework)
            if version:
                return version

        # Try setup.py
        setup_py = self.project_path / 'setup.py'
        if setup_py.exists():
            version = self._parse_setup_py(setup_py, framework)
            if version:
                return version

        return 'unknown'

    def _parse_requirements_file(self, req_file: Path, framework: str) -> Optional[str]:
        """Parse version from requirements.txt."""
        try:
            content = req_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Match framework name (case-insensitive, handle underscores/hyphens)
                parts = line.split('[')[0].split('#')[0]  # Remove extras and comments
                pkg_name = parts.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('!=')[0].strip()

                if pkg_name.lower().replace('-', '_') == framework.lower().replace('-', '_'):
                    return self._extract_version_from_spec(parts)

        except Exception:
            pass

        return None

    def _parse_pyproject_toml(self, pyproject: Path, framework: str) -> Optional[str]:
        """Parse version from pyproject.toml."""
        try:
            # Try tomllib (Python 3.11+)
            try:
                import tomllib
                data = tomllib.loads(pyproject.read_text(encoding='utf-8'))
            except ImportError:
                # Fallback: simple TOML parsing (basic implementation)
                content = pyproject.read_text(encoding='utf-8')
                data = self._parse_simple_toml(content)

            # Check dependencies
            dependencies = data.get('project', {}).get('dependencies', [])
            for dep in dependencies:
                if self._match_package_name(dep, framework):
                    return self._extract_version_from_spec(dep)

            # Check optional dependencies
            optional = data.get('project', {}).get('optional-dependencies', {})
            for deps_list in optional.values():
                for dep in deps_list:
                    if self._match_package_name(dep, framework):
                        return self._extract_version_from_spec(dep)

        except Exception:
            pass

        return None

    def _parse_setup_py(self, setup_py: Path, framework: str) -> Optional[str]:
        """Parse version from setup.py (basic implementation)."""
        try:
            content = setup_py.read_text(encoding='utf-8')
            # Look for install_requires = [...framework...]
            if 'install_requires' in content:
                start = content.find('install_requires')
                section = content[start:start+2000]
                # Simple regex-free search
                for line in section.split('\n'):
                    if self._match_package_name(line, framework):
                        return self._extract_version_from_spec(line)

        except Exception:
            pass

        return None

    def _parse_simple_toml(self, content: str) -> Dict:
        """Simple TOML parser for basic use cases (not full TOML spec)."""
        data = {'project': {}}
        in_project = False
        in_dependencies = False
        deps = []

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('[project]'):
                in_project = True
                in_dependencies = False
            elif line.startswith('dependencies'):
                in_dependencies = True
                deps = []
            elif in_dependencies:
                if line.startswith(']'):
                    data['project']['dependencies'] = deps
                    in_dependencies = False
                elif line.startswith('"') or line.startswith("'"):
                    # Extract dependency string
                    dep = line.strip('",[]').strip()
                    if dep:
                        deps.append(dep)

        return data

    def _match_package_name(self, spec: str, framework: str) -> bool:
        """Check if a requirement spec matches a framework name."""
        # Extract package name from spec (before version markers)
        pkg_name = spec.split('[')[0].split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('!=')[0].split(';')[0].strip()

        # Normalize: handle underscores and hyphens as equivalent
        return pkg_name.lower().replace('-', '_') == framework.lower().replace('-', '_')

    def _extract_version_from_spec(self, spec: str) -> str:
        """Extract version string from requirement specification."""
        spec = spec.strip()

        if '==' in spec:
            # Exact version: "fastapi==0.95.0"
            version = spec.split('==')[1].split(';')[0].strip()
            return version.split(']')[0].strip()

        elif '>=' in spec or '<=' in spec:
            # Range: "fastapi>=0.90,<1.0"
            parts = spec.split(',')
            versions = []
            for part in parts:
                if '>=' in part:
                    versions.append(part.split('>=')[1].strip())
                elif '<' in part:
                    versions.append(part.split('<')[1].strip())
            return '-'.join(versions) if versions else 'unknown'

        else:
            # No version spec
            return 'latest'

    def _match_framework(self, module_name: str) -> Optional[str]:
        """Match a module name to a known framework."""
        module_lower = module_name.lower()

        for framework, patterns in self.FRAMEWORK_IMPORTS.items():
            if module_lower in [m.lower() for m in patterns['modules']]:
                return framework

        return None

    def _should_skip(self, file_path: Path) -> bool:
        """Determine if a file should be skipped during scanning."""
        skip_dirs = {
            '.venv', 'venv', '.env', 'env',
            'dist', 'build', '__pycache__', '.git',
            '.pytest_cache', '.mypy_cache', 'node_modules',
            'site-packages', '.tox'
        }

        # Check if any part of path is in skip list
        for part in file_path.parts:
            if part in skip_dirs:
                return True

        return False


class JavaScriptFrameworkDetector:
    """Framework detection for JavaScript/TypeScript projects."""

    def __init__(self, project_path: str):
        """Initialize JS framework detector."""
        self.project_path = Path(project_path).resolve()
        self.frameworks_found = {}

    def detect_frameworks(self) -> Dict[str, Dict]:
        """Detect frameworks from package.json dependencies."""
        frameworks = {}

        pkg_json = self.project_path / 'package.json'
        if not pkg_json.exists():
            return frameworks

        try:
            data = json.loads(pkg_json.read_text(encoding='utf-8'))

            # Combine all dependencies
            all_deps = {}
            all_deps.update(data.get('dependencies', {}))
            all_deps.update(data.get('devDependencies', {}))

            # Known framework mappings
            known_frameworks = {
                'react': 'React',
                'react-dom': 'React',
                'vue': 'Vue',
                '@angular/core': 'Angular',
                'next': 'Next.js',
                'nuxt': 'Nuxt.js',
                'express': 'Express',
                'fastify': 'Fastify',
                'koa': 'Koa',
                'nest': 'NestJS',
                '@nestjs/core': 'NestJS',
                'jest': 'Jest',
                'mocha': 'Mocha',
                'vitest': 'Vitest',
                'webpack': 'Webpack',
                'vite': 'Vite',
                'esbuild': 'esbuild',
                'typescript': 'TypeScript',
            }

            for dep, version in all_deps.items():
                if dep in known_frameworks:
                    framework_name = known_frameworks[dep]
                    if framework_name not in frameworks:
                        frameworks[framework_name] = {
                            'version': version,
                            'source': 'package.json',
                            'packages': []
                        }
                    frameworks[framework_name]['packages'].append(dep)

        except Exception:
            pass

        return frameworks


# Example usage and testing
if __name__ == '__main__':
    # Test Python framework detection
    print("Testing Python Framework Detection:")
    print("=" * 60)

    detector = FrameworkDetector('/home/user/braxis')

    print("\n1. Direct imports (scan_depth=1):")
    frameworks_direct = detector.detect_frameworks(scan_depth=1)
    for framework, info in sorted(frameworks_direct.items()):
        print(f"  {framework}: {info['version']}")
        if info['files']:
            for f in info['files'][:2]:
                print(f"    - {f}")

    print("\n2. With wrapper detection (scan_depth=2):")
    frameworks_deep = detector.detect_frameworks(scan_depth=2)
    for framework, info in sorted(frameworks_deep.items()):
        print(f"  {framework}: {info['version']}")
        if info['wrapped_by']:
            print(f"    Wrapped by: {info['wrapped_by']}")

    # Test JavaScript detection
    print("\n" + "=" * 60)
    print("Testing JavaScript Framework Detection:")
    print("=" * 60)

    js_detector = JavaScriptFrameworkDetector('/home/user/braxis')
    js_frameworks = js_detector.detect_frameworks()
    if js_frameworks:
        for framework, info in sorted(js_frameworks.items()):
            print(f"  {framework}: {info['version']}")
    else:
        print("  No JavaScript frameworks detected")
