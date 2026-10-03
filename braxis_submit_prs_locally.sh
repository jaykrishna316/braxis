#!/bin/bash
# Braxis PR Campaign - Local Submission Script
# Run this on your machine with gh CLI authenticated as jaykrishna316
#
# Usage: bash braxis_submit_prs_locally.sh /path/to/generated/AGENTS.md/files

set -e

WORK_DIR="${1:-.}"
TEMP_DIR="/tmp/braxis_pr_work_$$"
RESULTS_FILE="braxis_pr_results_$(date +%Y%m%d_%H%M%S).md"

mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

# Initialize results file
cat > "$RESULTS_FILE" << 'HEADER'
# Braxis PR Campaign Results

**Date:** '$(date)'  
**Submitter:** jaykrishna316  

## PR Submission Status

| Repository | Status | PR URL | Submitted |
|-----------|--------|--------|-----------|
HEADER

# Array of repos with their local folder names
declare -A REPO_MAP=(
  ["optuna"]="optuna/optuna"
  ["ray"]="ray-project/ray"
  ["mlflow"]="mlflow/mlflow"
  ["wandb"]="wandb/wandb"
  ["kedro"]="kedro-org/kedro"
  ["flask"]="pallets/flask"
  ["starlette"]="encode/starlette"
  ["fastapi"]="tiangolo/fastapi"
  ["ClickHouse"]="ClickHouse/ClickHouse"
  ["airflow"]="apache/airflow"
  ["remix"]="remix-run/remix"
  ["svelte"]="sveltejs/svelte"
  ["nest"]="nestjs/nest"
  ["turbo"]="vercel/turbo"
  ["docusaurus"]="facebook/docusaurus"
  ["terraform"]="hashicorp/terraform"
  ["cargo"]="rust-lang/cargo"
  ["tokio"]="tokio-rs/tokio"
  ["pack"]="buildpacks/pack"
  ["grpc"]="grpc/grpc"
)

echo "Braxis PR Campaign - Local Submission"
echo "======================================"
echo "Workspace: $TEMP_DIR"
echo "Results will be saved to: $RESULTS_FILE"
echo ""

SUCCESS=0
FAILED=0

for local_name in "${!REPO_MAP[@]}"; do
  repo_path="${REPO_MAP[$local_name]}"
  owner="${repo_path%/*}"
  repo="${repo_path##*/}"
  agents_file="$WORK_DIR/$local_name/AGENTS.md"
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Processing: $repo_path"
  
  if [ ! -f "$agents_file" ]; then
    echo "✗ AGENTS.md not found at: $agents_file"
    echo "| $repo_path | ✗ Missing File | - | $(date) |" >> "$RESULTS_FILE"
    FAILED=$((FAILED+1))
    continue
  fi
  
  echo "✓ AGENTS.md found ($(wc -l < "$agents_file") lines)"
  
  # Step 1: Fork the repository
  echo "Step 1/5: Forking $repo_path..."
  fork_cmd="gh repo fork $owner/$repo --clone=false --remote=false"
  if $fork_cmd 2>&1 | grep -q "already forked"; then
    echo "  ✓ Fork already exists"
  else
    echo "  ✓ Fork created or already present"
  fi
  sleep 2
  
  # Step 2: Clone the fork
  echo "Step 2/5: Cloning fork..."
  clone_dir="$TEMP_DIR/${repo}_work"
  rm -rf "$clone_dir"
  
  if ! gh repo clone "jaykrishna316/$repo" "$clone_dir" 2>&1 | head -3; then
    echo "✗ Clone failed"
    echo "| $repo_path | ✗ Clone Failed | - | $(date) |" >> "$RESULTS_FILE"
    FAILED=$((FAILED+1))
    continue
  fi
  
  cd "$clone_dir"
  git config user.name "jaykrishna316"
  git config user.email "jaykrishna.i13@gmail.com"
  
  # Step 3: Create feature branch
  echo "Step 3/5: Creating feature branch..."
  default_branch=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@.*/@@')
  branch_name="add/agents-md"
  
  git checkout -b "$branch_name" "origin/$default_branch" 2>/dev/null || true
  
  # Step 4: Add AGENTS.md and commit
  echo "Step 4/5: Committing AGENTS.md..."
  cp "$agents_file" AGENTS.md
  git add AGENTS.md
  
  git commit -m "Add AGENTS.md: AI agent context and development guide" \
    -m "" \
    -m "- Comprehensive project context for AI code assistants" \
    -m "- AI Readiness Score included" \
    -m "- Development workflows, testing patterns, and conventions" \
    -m "- Helps agents understand architecture and best practices" \
    -m "- Non-intrusive: single documentation file" \
    -m "" \
    -m "Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>" \
    -m "Claude-Session: https://claude.ai/code/session_016Dbj2nKz4X4HY87wV3fQsv" 2>&1 | tail -2
  
  # Step 5: Push and create PR
  echo "Step 5/5: Pushing and creating PR..."
  git push origin "$branch_name" 2>&1 | tail -2
  
  # Create PR body
  pr_body="## What is AGENTS.md?

AGENTS.md is a standardized context file that helps AI code assistants understand your project. It includes:

- Project structure and architecture
- Development workflows and commands  
- Testing patterns and frameworks
- Code style conventions
- Common patterns and anti-patterns
- AI readiness assessment

## Why Add This?

✅ **Better AI Collaboration** - AI assistants provide more accurate, contextual code suggestions  
✅ **Faster Onboarding** - New contributors (human and AI) understand the project faster  
✅ **Quality Consistency** - Clear guidelines reduce context switching and mistakes  
✅ **Zero Overhead** - Single documentation file with no impact on existing code  
✅ **Framework Agnostic** - Works with Claude, ChatGPT, or any AI tool

## Learn More

See the AGENTS.md file for complete project context. For background on this standard, visit: https://github.com/jaykrishna316/braxis

---

Generated with [Braxis](https://github.com/jaykrishna316/braxis) - AI Agent Context Generator"
  
  # Create the PR
  if gh pr create \
    --title "Add AGENTS.md: AI agent context and development guide" \
    --body "$pr_body" \
    --repo "$owner/$repo" \
    2>&1 | tee /tmp/pr_output.txt | grep -q "https://github.com"; then
    
    pr_url=$(grep "https://github.com" /tmp/pr_output.txt | head -1 | tr -d ' ')
    echo "✓ PR Created: $pr_url"
    echo "| $repo_path | ✓ Created | [$pr_url](​$pr_url) | $(date) |" >> "$RESULTS_FILE"
    SUCCESS=$((SUCCESS+1))
  else
    echo "✗ PR Creation failed - check fork at: https://github.com/jaykrishna316/$repo"
    echo "| $repo_path | ⚠ Manual Review | [Fork](https://github.com/jaykrishna316/$repo) | $(date) |" >> "$RESULTS_FILE"
    FAILED=$((FAILED+1))
  fi
  
  cd "$TEMP_DIR"
  
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Campaign Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Successful PRs: $SUCCESS"
echo "⚠ Manual Review Needed: $FAILED"
echo "Total: $(($SUCCESS + $FAILED)) / 20"
echo ""
echo "Results saved to: $RESULTS_FILE"
echo "Workspace: $TEMP_DIR"

