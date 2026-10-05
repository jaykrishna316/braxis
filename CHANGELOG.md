# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-10-05

### Added
- Smart triggering to skip trivial changes and reduce CI noise
- Programmatic API via `braxis_api.py` for integration into other tools
- Configuration file support (`.braxis.yml`) for customizing behavior
- MCP (Model Context Protocol) server auto-detection
- Score history tracking with trend analysis (`braxis history --trends`)
- Support for 15+ programming languages (Python, JavaScript, TypeScript, Go, Rust, Java, etc.)
- Hierarchical AGENTS.md for monorepos (pnpm, uv, yarn, npm, lerna)
- Pre-commit hook support for automatic context regeneration

### Changed
- Improved scoring algorithm for more accurate AI readiness assessment
- Enhanced architecture detection for better monorepo support
- Better handling of edge cases in file analysis

### Fixed
- Corrected scoring calculations for type-checking dimension
- Fixed monorepo detection for edge cases
- Improved error messages for missing project files

## [1.2.0] - 2026-09-15

### Added
- Repository gotchas detection (identifies common anti-patterns)
- Subsystem ownership mapping for better project structure understanding
- Extended language support (Scala, R, SQL, Kotlin, Swift)
- GitHub Actions workflow template for automatic updates

### Changed
- Improved AGENTS.md generation quality
- Better documentation extraction from CONTRIBUTING.md files
- More accurate convention detection

### Fixed
- Fixed monorepo detection for Cargo workspaces
- Improved handling of nested project structures

## [1.1.0] - 2026-08-20

### Added
- **BREAKING**: Monorepo hierarchical support
  - Projects can now define AGENTS.md files at multiple levels
  - Each subsystem can have its own context file
- Programmatic Python API for using Braxis as a library
- Configuration file support (`.braxis.yml`)
- Score history tracking across runs
- MCP server detection and documentation
- `braxis inspect` command for detailed analysis output

### Changed
- **BREAKING**: Changed project structure expectations
  - Now supports hierarchical layouts with subsystem-specific AGENTS.md files
  - Single-file mode is still supported for backwards compatibility
- Enhanced scoring rubric with 8 dimensions (previously 5)

### Deprecated
- Direct file manipulation approach (use API instead for programmatic access)

### Fixed
- Fixed scoring calculation for large monorepos
- Improved handling of symbolic links
- Better error handling for permission issues

## [1.0.0] - 2026-07-10

### Added
- Initial release of Braxis
- Auto-generation of 4 context files:
  - AGENTS.md (universal format)
  - CLAUDE.md (Claude Code optimized)
  - .cursorrules (Cursor IDE rules)
  - .agentic-config.json (machine-readable config)
- AI readiness scoring (0-100 scale)
- Support for 10+ programming languages
- GitHub Actions workflow template
- Pre-commit hook setup
- Zero external dependencies

### Features
- ✅ One-command context file generation
- ✅ Automatic language detection
- ✅ Build system detection (package.json, pyproject.toml, Makefile, etc.)
- ✅ Test pattern detection
- ✅ Convention analysis
- ✅ Security pattern detection
- ✅ CI/CD integration ready

---

## How to Read This Changelog

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Fixed** - Bug fixes
- **Removed** - Removed features
- **Security** - Security fixes and updates
- **BREAKING** - Breaking changes that require migration

## Version Numbering

Braxis uses semantic versioning: **MAJOR.MINOR.PATCH**

- **MAJOR** - Incompatible API changes (breaking changes)
- **MINOR** - Backwards-compatible new features
- **PATCH** - Backwards-compatible bug fixes

### Stability Guarantees

- **v0.x.y** - Alpha/Beta (API may change without warning)
- **v1.0.0+** - Stable API (breaking changes only in MAJOR versions)

## Migration Guides

### Upgrading from v1.0 to v1.1

If you're using Braxis v1.0, upgrading to v1.1 is mostly automatic. However:

- ⚠️ **Monorepo layouts changed**: Projects with multiple subsystems should review the new hierarchical structure
- ✅ **Backwards compatible**: Single-file mode still works
- Review: See [PHASE_1_IMPLEMENTATION.md](./PHASE_1_IMPLEMENTATION.md) for details

### Upgrading from v1.1 to v1.2

No breaking changes. Safe to upgrade.

### Upgrading from v1.2 to v1.3

No breaking changes. Safe to upgrade.

## Future Roadmap

See [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) for planned features and release timeline.

## Support & Questions

- **Bugs**: [Report issues on GitHub](https://github.com/jaykrishna316/braxis/issues)
- **Questions**: [Start a discussion](https://github.com/jaykrishna316/braxis/discussions)
- **Contributing**: See [CONTRIBUTING.md](./CONTRIBUTING.md)
