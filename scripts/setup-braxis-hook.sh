#!/bin/bash
# Setup Braxis pre-commit hook for local development

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
HOOK_SOURCE="$REPO_ROOT/.githooks/pre-commit"
HOOK_DEST="$REPO_ROOT/.git/hooks/pre-commit"

echo "🔧 Setting up Braxis pre-commit hook..."

# Configure git to use .githooks directory
echo "⚙️  Configuring git hooks directory..."
git config core.hooksPath .githooks

# Make hook executable
chmod +x "$HOOK_SOURCE"

echo "✅ Braxis pre-commit hook installed!"
echo ""
echo "What this does:"
echo "  • Before each commit, braxis generate will run automatically"
echo "  • Context files (AGENTS.md, CLAUDE.md, .cursorrules, .agentic-config.json) will be updated"
echo "  • Updated files will be automatically staged"
echo "  • If changes are detected, they'll be included in your commit"
echo ""
echo "To skip the hook (not recommended):"
echo "  git commit --no-verify"
echo ""
echo "To uninstall the hook:"
echo "  git config --unset core.hooksPath"
