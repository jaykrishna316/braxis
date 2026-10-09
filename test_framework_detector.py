#!/usr/bin/env python3
"""
Test suite for framework detection module.
Validates AST-based detection, wrapper detection, and version extraction.
"""

import unittest
import tempfile
from pathlib import Path
from framework_detector import FrameworkDetector, JavaScriptFrameworkDetector


class TestFrameworkDetector(unittest.TestCase):
    """Test suite for Python framework detection."""

    def setUp(self):
        """Create temporary test project structure."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def _create_python_file(self, filename: str, content: str):
        """Helper to create Python files for testing."""
        file_path = self.project_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    def _create_requirements_file(self, filename: str, content: str):
        """Helper to create requirements files."""
        file_path = self.project_path / filename
        file_path.write_text(content)

    def test_direct_fastapi_import(self):
        """Test detection of FastAPI direct import."""
        self._create_python_file('app.py', 'from fastapi import FastAPI\napp = FastAPI()')
        self._create_requirements_file('requirements.txt', 'fastapi==0.95.0')

        detector = FrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks(scan_depth=1)

        self.assertIn('fastapi', frameworks)
        self.assertTrue(frameworks['fastapi']['direct'])
        self.assertIn('app.py', frameworks['fastapi']['files'][0])

    def test_version_extraction_from_requirements(self):
        """Test version extraction from requirements.txt."""
        self._create_python_file('app.py', 'from fastapi import FastAPI')
        self._create_requirements_file('requirements.txt', 'fastapi==0.95.0')

        detector = FrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks(scan_depth=1)

        self.assertEqual(frameworks['fastapi']['version'], '0.95.0')

    def test_version_extraction_range(self):
        """Test version extraction with version ranges."""
        self._create_python_file('app.py', 'from fastapi import FastAPI')
        self._create_requirements_file('requirements.txt', 'fastapi>=0.90,<1.0')

        detector = FrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks(scan_depth=1)

        self.assertIn('0.90', frameworks['fastapi']['version'])
        self.assertIn('1.0', frameworks['fastapi']['version'])

    def test_custom_wrapper_detection(self):
        """Test detection of frameworks imported within wrapper modules."""
        # Create wrapper module
        self._create_python_file(
            'custom_fastapi_wrapper.py',
            'from fastapi import FastAPI\n\nclass CustomFastAPI(FastAPI):\n    pass'
        )
        # Create app that uses wrapper
        self._create_python_file('app.py', 'from custom_fastapi_wrapper import CustomFastAPI')
        self._create_requirements_file('requirements.txt', 'fastapi==0.95.0')

        detector = FrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks(scan_depth=2)

        self.assertIn('fastapi', frameworks)
        self.assertFalse(frameworks['fastapi']['direct'])  # Not direct import
        self.assertIn('custom_fastapi_wrapper.py', frameworks['fastapi']['wrapped_by'][0])

    def test_false_positive_reduction_comments(self):
        """Verify comments about frameworks don't create false positives."""
        self._create_python_file(
            'notes.py',
            '# FastAPI is a great framework\n# We could use FastAPI instead of Flask\nprint("hello")'
        )
        self._create_requirements_file('requirements.txt', '')

        detector = FrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks(scan_depth=1)

        self.assertNotIn('fastapi', frameworks)

    def test_multiple_frameworks(self):
        """Test detection of multiple frameworks in one project."""
        self._create_python_file(
            'app.py',
            'from fastapi import FastAPI\nimport pytest\nfrom pydantic import BaseModel'
        )
        self._create_requirements_file(
            'requirements.txt',
            'fastapi==0.95.0\npytest==7.2.0\npydantic==1.10.2'
        )

        detector = FrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks(scan_depth=1)

        self.assertIn('fastapi', frameworks)
        self.assertIn('pytest', frameworks)
        self.assertIn('pydantic', frameworks)

    def test_skips_venv_directories(self):
        """Test that venv directories are skipped."""
        self._create_python_file('.venv/lib/python3.9/site-packages/module.py', 'import something')
        self._create_python_file('app.py', 'from fastapi import FastAPI')
        self._create_requirements_file('requirements.txt', 'fastapi==0.95.0')

        detector = FrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks(scan_depth=1)

        # Should only find fastapi from app.py, not from venv
        self.assertEqual(len(frameworks), 1)
        self.assertIn('fastapi', frameworks)

    def test_version_unknown_when_not_specified(self):
        """Test that version is 'unknown' when not found in requirements."""
        self._create_python_file('app.py', 'from fastapi import FastAPI')
        self._create_requirements_file('requirements.txt', '')  # Empty requirements

        detector = FrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks(scan_depth=1)

        self.assertEqual(frameworks['fastapi']['version'], 'unknown')

    def test_case_insensitive_framework_matching(self):
        """Test that framework matching is case-insensitive."""
        self._create_python_file('app.py', 'from FastAPI import FastAPI')
        self._create_requirements_file('requirements.txt', 'FastAPI==0.95.0')

        detector = FrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks(scan_depth=1)

        self.assertIn('fastapi', frameworks)

    def test_hyphen_underscore_normalization(self):
        """Test that hyphens and underscores are treated as equivalent."""
        self._create_python_file('app.py', 'from sqlalchemy import Column')
        self._create_requirements_file('requirements.txt', 'SQLAlchemy==2.0.0')

        detector = FrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks(scan_depth=1)

        self.assertIn('sqlalchemy', frameworks)
        self.assertEqual(frameworks['sqlalchemy']['version'], '2.0.0')

    def test_syntax_error_resilience(self):
        """Test that files with syntax errors don't crash detection."""
        self._create_python_file('broken.py', 'def broken syntax here :(')
        self._create_python_file('app.py', 'from fastapi import FastAPI')
        self._create_requirements_file('requirements.txt', 'fastapi==0.95.0')

        detector = FrameworkDetector(str(self.project_path))
        # Should not raise an exception
        frameworks = detector.detect_frameworks(scan_depth=1)

        self.assertIn('fastapi', frameworks)


class TestJavaScriptFrameworkDetector(unittest.TestCase):
    """Test suite for JavaScript framework detection."""

    def setUp(self):
        """Create temporary test project structure."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def _create_package_json(self, content: str):
        """Helper to create package.json."""
        file_path = self.project_path / 'package.json'
        file_path.write_text(content)

    def test_react_detection(self):
        """Test detection of React in package.json."""
        package_json = '''{
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            }
        }'''
        self._create_package_json(package_json)

        detector = JavaScriptFrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks()

        self.assertIn('React', frameworks)
        self.assertEqual(frameworks['React']['version'], '^18.2.0')

    def test_multiple_js_frameworks(self):
        """Test detection of multiple JS frameworks."""
        package_json = '''{
            "dependencies": {
                "react": "^18.2.0",
                "express": "^4.18.0"
            },
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }'''
        self._create_package_json(package_json)

        detector = JavaScriptFrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks()

        self.assertIn('React', frameworks)
        self.assertIn('Express', frameworks)
        self.assertIn('Jest', frameworks)

    def test_no_frameworks_when_package_json_missing(self):
        """Test that empty dict is returned when package.json doesn't exist."""
        detector = JavaScriptFrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks()

        self.assertEqual(frameworks, {})

    def test_angular_detection(self):
        """Test detection of Angular via @angular/core."""
        package_json = '''{
            "dependencies": {
                "@angular/core": "^15.0.0",
                "@angular/common": "^15.0.0"
            }
        }'''
        self._create_package_json(package_json)

        detector = JavaScriptFrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks()

        self.assertIn('Angular', frameworks)


class TestFrameworkDetectorIntegration(unittest.TestCase):
    """Integration tests for framework detection."""

    def setUp(self):
        """Create temporary test project structure."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_real_world_django_project(self):
        """Test detection on a Django-like project structure."""
        # Create Django project structure
        (self.project_path / 'manage.py').write_text('import django\nif __name__ == "__main__": pass')
        (self.project_path / 'myapp').mkdir(parents=True, exist_ok=True)
        (self.project_path / 'myapp' / '__init__.py').write_text('')
        (self.project_path / 'myapp' / 'models.py').write_text('from django.db import models')
        (self.project_path / 'myapp' / 'views.py').write_text('from django.http import HttpResponse')
        (self.project_path / 'requirements.txt').write_text('django==4.2.0\ndjango-rest-framework==3.14.0')

        detector = FrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks(scan_depth=1)

        self.assertIn('django', frameworks)
        self.assertEqual(frameworks['django']['version'], '4.2.0')

    def test_real_world_fastapi_project(self):
        """Test detection on a FastAPI-like project structure."""
        (self.project_path / 'main.py').write_text('from fastapi import FastAPI\napp = FastAPI()')
        (self.project_path / 'models.py').write_text('from pydantic import BaseModel')
        (self.project_path / 'requirements.txt').write_text('fastapi==0.95.0\npydantic==1.10.2\nuvicorn==0.21.0')

        detector = FrameworkDetector(str(self.project_path))
        frameworks = detector.detect_frameworks(scan_depth=1)

        self.assertIn('fastapi', frameworks)
        self.assertIn('pydantic', frameworks)
        self.assertEqual(frameworks['fastapi']['version'], '0.95.0')


if __name__ == '__main__':
    unittest.main()
