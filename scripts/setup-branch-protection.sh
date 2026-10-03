#!/bin/bash

# Setup branch protection for main branch
# This script uses GitHub CLI to configure branch protection rules

set -e

echo "🔒 Setting up branch protection for main branch..."

# Get repo owner and name from git remote
REPO_URL=$(git config --get remote.origin.url)
OWNER=$(echo $REPO_URL | sed -E 's|.*github.com[:/]([^/]+)/.*|\1|')
REPO=$(echo $REPO_URL | sed -E 's|.*github.com[:/].*/([^.]+).*|\1|')

echo "📦 Repository: $OWNER/$REPO"

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "📥 Install from: https://cli.github.com"
    exit 1
fi

# Create branch protection rule for main
echo "⚙️  Configuring branch protection rules..."

gh api repos/$OWNER/$REPO/branches/main/protection \
  --input - << 'EOF'
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true,
  "required_linear_history": false
}
EOF

echo "✅ Branch protection rules created successfully!"
echo ""
echo "📋 Rules applied:"
echo "  • Require pull request before merging"
echo "  • Required approvals: 1"
echo "  • Dismiss stale pull request approvals"
echo "  • Require conversation resolution before merging"
echo "  • Block force pushes"
echo "  • Prevent deletion"
echo ""
echo "🔐 Your main branch is now protected!"
