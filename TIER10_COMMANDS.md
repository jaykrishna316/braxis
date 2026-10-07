# Tier 10 Campaign - Individual Repo Commands

Each command below will:
1. Clone/pull the repo
2. Run braxis generate
3. Create a branch, commit with proper attribution
4. Auto-create PR on GitHub with condensed description

**Prerequisites:**
- `gh` CLI configured (`gh auth login`)
- Script available: `bash tier10_campaign_condensed.sh <owner/repo> jaykrishna316`

---

## ✅ COMPLETED
- ✅ pantsbuild/pants (93/100)
- ✅ scons/scons (93/100)

---

## REMAINING (8 repos)

### 1️⃣ ninja-build/ninja (66/100 - AI-Native)
```bash
bash tier10_campaign_condensed.sh ninja-build/ninja jaykrishna316
```

### 2️⃣ bazelbuild/bazel (96/100 - Agent-Optimized)
```bash
bash tier10_campaign_condensed.sh bazelbuild/bazel jaykrishna316
```

### 3️⃣ facebook/buck2 (95/100 - Agent-Optimized)
```bash
bash tier10_campaign_condensed.sh facebook/buck2 jaykrishna316
```

### 4️⃣ mesonbuild/meson (98/100 - Agent-Optimized+)
```bash
bash tier10_campaign_condensed.sh mesonbuild/meson jaykrishna316
```

### 5️⃣ waf-project/waf (38/100 - Agent-Aware)
```bash
bash tier10_campaign_condensed.sh waf-project/waf jaykrishna316
```

### ⚠️ REQUIRE AUTH (may fail without SSH/PAT)
```bash
# These require authentication:
# bash tier10_campaign_condensed.sh tup/tup jaykrishna316
# bash tier10_campaign_condensed.sh premake/premake5 jaykrishna316
# bash tier10_campaign_condensed.sh cmake/cmake jaykrishna316
```

---

## Usage Notes

1. **Run each command sequentially** (or in parallel if you prefer):
   ```bash
   # Option A: Sequential (recommended for clean logs)
   bash tier10_campaign_condensed.sh ninja-build/ninja jaykrishna316
   bash tier10_campaign_condensed.sh bazelbuild/bazel jaykrishna316
   # ... etc
   
   # Option B: Parallel (faster, but mixed output)
   bash tier10_campaign_condensed.sh ninja-build/ninja jaykrishna316 &
   bash tier10_campaign_condensed.sh bazelbuild/bazel jaykrishna316 &
   wait
   ```

2. **What happens automatically:**
   - ✅ Clones repo (if first time) or pulls latest
   - ✅ Generates AGENTS.md, CLAUDE.md, .cursorrules, .agentic-config.json
   - ✅ Creates timestamped branch
   - ✅ Commits with attribution to you
   - ✅ Pushes to your fork
   - ✅ **Auto-creates PR on GitHub** (via `gh pr create`)
   - ✅ Shows PR URL

3. **No manual GitHub web UI needed** — everything is automated!

---

## After Campaign Complete

All 8 repos will have:
- ✅ PR created on original repo (from your fork)
- ✅ Condensed AI-focused PR description (~250 words)
- ✅ GitHub Actions workflow code for auto-updates
- ✅ All context files ready for repo maintainers

Then you can:
1. Compare readiness scores across all 10 Tier 10 repos
2. Identify patterns (e.g., language performance)
3. Move to Tier 11
4. Aggregate findings across all tiers (1-10)

---

**Script Location:** `tier10_campaign_condensed.sh` (in this repo)  
**PR Description:** Condensed + auto-created via `gh pr create`  
**Attribution:** Includes Jayakrishna Ichapurapu + session link
