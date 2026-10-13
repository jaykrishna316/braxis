from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="braxis",
    version="3.0.0",
    author="Jayakrishna Ichapurapu",
    author_email="jayichapurapu@example.com",
    description="AI Context Platform v3.0 - Extract Tier 1 & Tier 2 patterns + MCP Server for Claude integration.",
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
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "llm": ["anthropic>=0.24.0"],
        "mcp": [],
    },
    entry_points={
        "console_scripts": [
            "braxis=braxis:main",
            "braxis-mcp=braxis.mcp_stdio:run_server",
        ],
    },
)
