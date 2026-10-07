#!/usr/bin/env python3
"""
Detect if code changes are significant enough to regenerate context files.
Returns 0 (significant changes) or 1 (no significant changes).

Used by GitHub Actions to conditionally run Braxis.
"""
import sys
import subprocess
from pathlib import Path

def get_changed_files(base_branch="origin/main"):
    """Get list of changed files compared to base branch."""
    try:
        # Get diff between base and current
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_branch}...HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        # If diff fails (e.g., first push), assume significant
        return ["unknown"]

def is_significant_change(files):
    """
    Determine if changed files represent significant code changes.

    Significant = architecture/logic changes that affect context
    Not significant = docs, comments, styles
    """
    if not files or files == ["unknown"]:
        return True  # Assume significant if we can't determine

    # File patterns for significant changes
    significant_patterns = [
        # Source code
        '*.py', '*.js', '*.ts', '*.tsx', '*.java', '*.go', '*.rs',
        '*.rb', '*.php', '*.cs', '*.kt', '*.scala', '*.cpp', '*.c',

        # Build & dependencies
        'package.json', 'package-lock.json', 'yarn.lock',
        'pyproject.toml', 'setup.py', 'requirements.txt',
        'pom.xml', 'build.gradle', 'build.gradle.kts',
        'Gemfile', 'Gemfile.lock', 'Cargo.toml', 'Cargo.lock',
        'composer.json', 'composer.lock', 'go.mod', 'go.sum',
        'pubspec.yaml', 'pubspec.lock',
        'Makefile', 'CMakeLists.txt',

        # Project structure
        '.github/workflows/**', 'src/**', 'lib/**', 'app/**',
        'packages/**', 'modules/**', 'services/**', 'components/**',

        # Test files
        'test/**', 'tests/**', 'spec/**', '__tests__/**',
        '*_test.py', '*_test.go', '*_test.js', '*_test.ts',
        '*_spec.py', '*_spec.rb', '*_spec.js',

        # Config that affects architecture
        '.env*', 'config/**', 'conf/**',
        'tsconfig.json', '.eslintrc*', '.prettierrc*',
        'babel.config.*', 'jest.config.*',

        # Entry points & main files
        'main.py', 'index.js', 'index.ts', 'app.js', 'server.js',
        'cli.py', 'bin/**',
    ]

    # Non-significant patterns (should NOT trigger regeneration)
    non_significant_patterns = [
        'README.md', '*.md', 'docs/**',
        '.gitignore', '.editorconfig', 'LICENSE',
        '*.txt', '*.json',  # Most JSON files (except those above)
        '.github/ISSUE_TEMPLATE/**', '.github/pull_request_template.md',
        'CHANGELOG.md', 'CONTRIBUTING.md', 'GOVERNANCE.md',
        '.github/CODEOWNERS',
    ]

    def matches_pattern(filepath, patterns):
        """Check if filepath matches any pattern."""
        p = Path(filepath)
        for pattern in patterns:
            if '**' in pattern:
                # Glob pattern
                if p.match(pattern.replace('**/', '*/')):
                    return True
            elif '/' in pattern:
                # Directory pattern
                if filepath.startswith(pattern):
                    return True
            else:
                # Filename pattern
                if p.name == pattern or p.name.endswith(pattern.lstrip('*')):
                    return True
        return False

    # Check each file
    for file in files:
        if not file or file.strip() == '':
            continue

        # Skip non-significant files
        if matches_pattern(file, non_significant_patterns):
            continue

        # Check if it's a significant file
        if matches_pattern(file, significant_patterns):
            return True

        # If it's a source file we don't recognize, assume significant
        source_extensions = {'.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.cs', '.kt'}
        if Path(file).suffix in source_extensions:
            return True

    return False

def main():
    """Main entry point."""
    # Get changed files
    changed_files = get_changed_files()

    print(f"Changed files: {len(changed_files)}")
    for f in changed_files[:10]:  # Show first 10
        print(f"  - {f}")
    if len(changed_files) > 10:
        print(f"  ... and {len(changed_files) - 10} more")

    # Check if significant
    if is_significant_change(changed_files):
        print("\n✅ Significant changes detected - regenerating context files")
        sys.exit(0)  # 0 = True = significant
    else:
        print("\n⏭️ No significant changes - skipping Braxis regeneration")
        sys.exit(1)  # 1 = False = not significant

if __name__ == '__main__':
    main()
