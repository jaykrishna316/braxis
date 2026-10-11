# Campaign Automation Features - Integration Status

## ✅ What Was Added

Two new files were cherry-picked from `braxis/demo-scoring-breakdown`:

### 1. **campaign_pr_generator.py** (61 lines)
- Generates intelligent PR descriptions with Braxis context
- Shows AI readiness scores and tiers
- Detects existing AGENTS.md and recommends merge options (A/B/C)
- Suggests branch naming and commit messages

**Usage:**
```bash
python3 campaign_pr_generator.py ~/braxis_campaign/meteor
```

### 2. **braxis_campaign_with_pr_mac.sh** (137 lines)
- Enhanced version of braxis_campaign_mac.sh
- Generates AGENTS.md files for campaign repos
- Auto-generates and displays PR descriptions
- Reduces manual PR creation effort

**Usage:**
```bash
./braxis_campaign_with_pr_mac.sh elastic/kibana jaykrishna316
```

## ⚠️ Missing Dependencies

These tools need the following methods added to `BraxisAnalyzer` in `braxis.py`:

### Required Methods:
1. **`detect_existing_agents_md()`** 
   - Reads existing AGENTS.md if it exists
   - Returns dict with: exists, path, content, score, sections

2. **`_score_agents_md(content)`** (private helper)
   - Scores AGENTS.md on customization quality (0-100)
   - Checks for custom sections: Skills, Package Domain, Gotchas, etc.
   - Higher score = more hand-written content

3. **`_extract_sections(content)`** (private helper)
   - Extracts named sections from AGENTS.md
   - Returns dict of section_name → section_content

4. **`generate_pr_description()`**
   - Returns intelligent PR description text
   - Includes AI readiness breakdown
   - Provides merge recommendations based on existing AGENTS.md quality

## 📋 What These Features Do

### Smart Merge Logic
- Detects if a project already has custom AGENTS.md
- Scores it on quality/customization (0-100)
- Preserves high-quality custom sections (score ≥ 50)
- Recommends merge strategy (A: replace, B: hybrid, C: keep)

### PR Description Generator  
- **Before:** Generic "feat: Add/update AGENTS.md" message
- **After:** Intelligent PR description showing:
  - ✅ Project's AI readiness score
  - ✅ Auto-refresh opportunities detected
  - ✅ Recommended merge strategy
  - ✅ What was improved (scoring details)

### Campaign Automation
- One-command campaign workflow
- Auto-generates both AGENTS.md AND PR description
- Shows users exactly what to put in their PR
- Saves 10-15 minutes per campaign repo

## 🔄 Integration Difficulty

**Current Status:** Low-difficulty integration (needs 4 methods in braxis.py)

The methods are self-contained and don't modify existing logic. They sit alongside the current `generate_agents_md()` method.

## 🎯 Next Steps

To complete integration:
1. Add the 4 required methods to BraxisAnalyzer class in braxis.py
2. Test `campaign_pr_generator.py` against a test repo
3. Test `braxis_campaign_with_pr_mac.sh` with a real campaign repo
4. Commit with attribution

---

**Decision Required:** 
- Want to add the 4 methods to braxis.py and complete integration? 
- Or keep these as "preview" tools for future integration?
