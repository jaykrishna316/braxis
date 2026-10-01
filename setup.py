from setuptools import setup
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="braxis",
    version="1.0.0",
    author="Jayakrishna Ichapurapu",
    author_email="jayichapurapu@example.com",
    description="Auto-generate AI agent context files. Keep AGENTS.md, CLAUDE.md, .cursorrules, and .agentic-config.json in sync with your codebase.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaykrishna316/braxis",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.8",
    py_modules=["braxis"],
    install_requires=[],
    extras_require={
        "llm": ["anthropic>=0.24.0"],
    },
    entry_points={
        "console_scripts": [
            "braxis=braxis:main",
        ],
    },
)
