# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-10-03

### Added
- **Dual-Format AGENTS.md**: New Category A (Operations Manual from CONTRIBUTING.md) + Category B (Context Guide)
- **Campaign Automation Scripts**: 
  - `braxis_campaign.sh` for multi-repository AGENTS.md generation and PR automation
  - `braxis_campaign_mac.sh` for single-repository AGENTS.md generation with macOS compatibility
- **Graceful File Handling**: AGENTS.md generation now works even if file already exists
- **Pre-commit Configuration**: Added `.pre-commit-config.example.yaml` and `.pre-commit-hooks.yaml`
- **GitHub Actions Workflows**:
  - `braxis-score.yml`: Automated scoring and metrics tracking
  - `braxis-sync.yml`: Automated AGENTS.md synchronization
- **Comprehensive Documentation**:
  - COMPETITIVE_ANALYSIS.md: Analysis of similar tools and market positioning
  - IMPLEMENTATION_ROADMAP.md: Detailed feature roadmap and milestones
  - RESEARCH_FINDINGS.md: Research on high-star repositories and patterns
  - RECOMMENDED_CHANGES.md: Prioritized list of improvements

### Changed
- Improved script robustness for edge cases in fork workflows
- Enhanced AGENTS.md regeneration to handle existing files gracefully
- Updated README with v1.4 feature documentation

### Fixed
- Corrected version numbering in braxis.py (1.1.0 → 1.3.0)
- Fixed language-aware detection for build systems and test frameworks
- Improved CONTRIBUTING.md pattern extraction with smart parsing

### Tested
- Production validation on projects from 4 to 22,679 files
- Full test coverage maintained at 30/30 passing tests
- Campaign automation tested on both single and multi-repository scenarios

## [1.3.2] - Previous Release

See previous releases for v1.3.2 and earlier changes.

---

## Release Notes

### v1.4.0 Highlights

Braxis v1.4 introduces **dual-format AGENTS.md generation**, allowing AI agents to access both operational procedures extracted from CONTRIBUTING.md (Category A) and comprehensive context guides (Category B). This release also includes powerful campaign automation scripts for managing AGENTS.md across multiple repositories.

**Key Benefits:**
- Keep AI agents synchronized with the latest project status
- Standardized operational procedures and context for consistency
- Automated campaign management for monorepo and multi-repo setups
- Production-tested on repositories ranging from 4 to 22,679 files

**Breaking Changes:** None - fully backward compatible with v1.1-v1.3

**Migration Guide:** Existing projects will automatically benefit from the new dual-format feature on the next `braxis generate` run.

---

For more information, visit [GitHub Repository](https://github.com/jaykrishna316/braxis)
