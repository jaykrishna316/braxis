# Braxis Programmatic API Guide

Braxis now exposes a comprehensive Python API for integrating context file generation into your own tools and workflows.

## Installation

```bash
pip install braxis
```

## Quick Start

### Basic Score Analysis

```python
from braxis_api import ScoreAnalyzer

# Analyze a project
analyzer = ScoreAnalyzer(project_path="/path/to/repo")
score = analyzer.calculate()

print(f"AI Readiness Score: {score.total}/100")
print(f"Level: {score.level}")
print(f"Architecture: {score.architecture}/100")
print(f"Testing: {score.testing}/100")
```

### Generate Context Files

```python
from braxis_api import ContextGenerator

# Generate context files
generator = ContextGenerator(project_path="/path/to/repo")
result = generator.generate()

if result.success:
    print(f"Generated {result.files_generated} files")
    for filename, content in result.changes.items():
        print(f"\n{filename}:")
        print(content[:200] + "...")
else:
    print(f"Error: {result.errors}")
```

### Get Improvement Suggestions

```python
from braxis_api import ScoreAnalyzer

analyzer = ScoreAnalyzer(project_path="/path/to/repo")
suggestions = analyzer.get_improvement_suggestions()

for suggestion in suggestions:
    print(f"\n{suggestion.dimension.upper()}")
    print(f"Current: {suggestion.current_score}/100 → Target: {suggestion.target_score}/100")
    print(f"Priority: {suggestion.priority}")
    for action in suggestion.actions:
        print(f"  • {action}")
```

## Core API Classes

### ScoreAnalyzer

Analyze AI readiness scores for a project.

#### Methods

- **`calculate()`** → `AIReadinessScore`
  - Calculate the overall AI readiness score
  
- **`get_dimension_scores()`** → `Dict[str, int]`
  - Get individual dimension scores
  
- **`get_improvement_suggestions()`** → `List[Suggestion]`
  - Get actionable improvement suggestions

#### Example

```python
from braxis_api import ScoreAnalyzer

analyzer = ScoreAnalyzer(project_path=".")
score = analyzer.calculate()

# Get all dimensions
dims = score.get_dimensions()
for dimension, score_val in dims.items():
    print(f"{dimension}: {score_val}/100")
```

### ContextGenerator

Generate context files from a codebase.

#### Methods

- **`generate()`** → `GenerationResult`
  - Generate all context files (AGENTS.md, CLAUDE.md, .cursorrules, .agentic-config.json)
  
- **`generate_specific(files: List[str])`** → `GenerationResult`
  - Generate specific context files

#### Example

```python
from braxis_api import ContextGenerator

generator = ContextGenerator(project_path=".")
result = generator.generate()

if result.success:
    # Access generated content
    for filename, content in result.changes.items():
        with open(filename, 'w') as f:
            f.write(content)
        print(f"✅ Generated {filename}")
else:
    print(f"❌ Error: {', '.join(result.errors)}")
```

### TrendAnalyzer

Analyze score trends over time.

#### Methods

- **`get_history(limit: Optional[int])`** → `List[Dict]`
  - Get score history
  
- **`get_trend(dimension: str)`** → `Optional[Dict]`
  - Get trend for a specific dimension
  
- **`predict_score(days_ahead: int)`** → `Optional[int]`
  - Predict future score

#### Example

```python
from braxis_api import TrendAnalyzer

analyzer = TrendAnalyzer(project_path=".")

# Get historical scores
history = analyzer.get_history(limit=10)
for entry in history:
    print(f"{entry['timestamp']}: {entry['total_score']}/100")

# Get trend for a dimension
trend = analyzer.get_trend("testing")
if trend:
    print(f"Testing trend: {trend['trend']}")
    print(f"Average: {trend['average']:.0f}/100")

# Predict future score
predicted = analyzer.predict_score(days_ahead=30)
if predicted:
    print(f"Predicted score in 30 days: {predicted}/100")
```

### MultiRepoAnalyzer

Analyze multiple repositories at once.

#### Methods

- **`analyze_all()`** → `Dict[str, AIReadinessScore]`
  - Analyze all configured repositories
  
- **`get_org_summary()`** → `Dict[str, Any]`
  - Get organization-wide summary

#### Example

```python
from braxis_api import MultiRepoAnalyzer

analyzer = MultiRepoAnalyzer(repos=[
    "/path/to/repo1",
    "/path/to/repo2",
    "/path/to/repo3",
])

# Get scores for all repos
results = analyzer.analyze_all()
for repo, score in results.items():
    print(f"{repo}: {score.total}/100 ({score.level})")

# Get organization summary
summary = analyzer.get_org_summary()
print(f"Organization Average: {summary['average_score']}/100")
print(f"Analyzed {summary['num_repos']} repositories")
```

## Data Models

### AIReadinessScore

Represents an AI readiness score.

```python
@dataclass
class AIReadinessScore:
    total: int                    # Overall score (0-100)
    architecture: int             # Architecture dimension
    testing: int                  # Testing dimension
    dependencies: int             # Dependencies dimension
    conventions: int              # Conventions dimension
    entry_points: int             # Entry points dimension
    security: int                 # Security dimension
    build: int                    # Build dimension
    documentation: int            # Documentation dimension
    timestamp: datetime            # When this score was calculated
    level: str                     # "AI-Hostile", "AI-Aware", "AI-Native"
```

### GenerationResult

Result of context file generation.

```python
@dataclass
class GenerationResult:
    success: bool                  # Whether generation succeeded
    changed_files: List[str]       # Files that changed
    changes: Dict[str, str]        # filename → content mapping
    errors: List[str]              # Error messages if any
    timestamp: datetime            # When generation ran
    files_generated: int           # Number of files generated
```

### Suggestion

An improvement suggestion.

```python
@dataclass
class Suggestion:
    dimension: str                 # Which dimension to improve
    current_score: int             # Current score in dimension
    target_score: int              # Recommended target
    actions: List[str]             # Steps to take
    priority: str                  # "high", "medium", "low"
    estimated_effort: str          # "low", "medium", "high"
```

## Configuration

Braxis uses `.braxis.yml` for project-specific configuration.

### Example Configuration

```yaml
context:
  output_format: markdown
  code_block_style: python-fenced
  include_test_metrics: true

generation:
  min_change_threshold: 5
  skip_trivial_changes: true
  exclude_patterns:
    - __pycache__
    - .venv

automation:
  github_paths:
    - src/
    - tests/
    - setup.py
  auto_commit: true

scoring:
  enable_scoring: true
  weight_testing: 1.2  # Weight testing 20% higher
```

Load configuration in your code:

```python
from braxis_config import BraxisConfig
from braxis_api import ContextGenerator

config = BraxisConfig.load(".braxis.yml")
generator = ContextGenerator(project_path=".", config=config)
result = generator.generate()
```

## Smart Triggering

Detect meaningful changes automatically.

```python
from braxis_triggers import SmartTrigger

trigger = SmartTrigger()

# Check if changes are meaningful
should_regen, metrics = trigger.should_regenerate(
    changed_files=["src/module.py", "tests/test.py"],
    repo_path=".",
    git_base="origin/main"
)

if should_regen:
    print(f"Regenerating context files...")
    print(f"Changed files: {metrics.meaningful_files_changed}")
    print(f"Lines changed: {metrics.total_lines_changed}")
else:
    print(f"Skipping (reason: {metrics.change_reason})")
```

## Integration Examples

### GitHub Actions

```python
import os
from braxis_api import ContextGenerator
from braxis_triggers import SmartTrigger

# Get changed files from environment
changed_files = os.getenv("CHANGED_FILES", "").split(",")

# Check if regeneration is needed
trigger = SmartTrigger()
should_regen, metrics = trigger.should_regenerate(changed_files)

if should_regen:
    generator = ContextGenerator()
    result = generator.generate()
    
    if result.success:
        # Commit and push
        print(f"✅ Generated {len(result.changes)} files")
    else:
        print(f"❌ Error: {result.errors}")
```

### IDE Plugin

```python
from braxis_api import ScoreAnalyzer

def get_project_health():
    """Get AI readiness score for IDE display."""
    analyzer = ScoreAnalyzer(project_path=".")
    score = analyzer.calculate()
    
    return {
        "score": score.total,
        "level": score.level,
        "status": "🟢" if score.total >= 70 else "🟡" if score.total >= 40 else "🔴"
    }
```

### Organizational Dashboard

```python
from braxis_api import MultiRepoAnalyzer
import json

# Analyze all repos
analyzer = MultiRepoAnalyzer(repos=["repo1", "repo2", "repo3"])
summary = analyzer.get_org_summary()

# Save to JSON for dashboard
with open("org-metrics.json", "w") as f:
    json.dump(summary, f, indent=2)

# Slack notification
print(f"📊 Organization AI Readiness: {summary['average_score']}/100")
```

## Error Handling

```python
from braxis_api import ContextGenerator, GenerationResult

try:
    generator = ContextGenerator(project_path="/path/to/repo")
    result = generator.generate()
    
    if not result.success:
        print(f"Generation failed: {', '.join(result.errors)}")
    else:
        print(f"Successfully generated {result.files_generated} files")
        
except FileNotFoundError as e:
    print(f"Project path not found: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Considerations

- **Caching**: Scores are cached locally by project hash
- **Git Operations**: SmartTrigger uses git diff for line counting (can be slow on large repos)
- **Multi-repo Analysis**: Consider analyzing repos in parallel for large organizations

## API Compatibility

This API is stable as of Braxis v1.1. Breaking changes will increment the major version number.

## Contributing

To contribute to the Braxis API:
1. Add tests in `test_braxis_api.py`
2. Update documentation
3. Follow the existing code style
4. Ensure all tests pass

## Support

For issues or questions:
- Check the [README](README.md) for general information
- See [AGENTS.md](AGENTS.md) for project context
- Open an issue on GitHub

---

**Version**: 1.1  
**Last Updated**: October 2024
