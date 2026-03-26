# Agentic Recommendation Workflow

**Automated DevOps Maturity Recommendations using AI Analysis**

---

## Table of Contents

1. [Overview](#overview)
2. [Workflow Architecture](#workflow-architecture)
3. [Prerequisites](#prerequisites)
4. [Workflow Steps](#workflow-steps)
5. [6 Pillar Skills](#6-pillar-skills)
6. [Usage Examples](#usage-examples)
7. [Output Structure](#output-structure)
8. [Integration Guide](#integration-guide)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This workflow automates the generation of DevOps maturity recommendations by:

- **Detecting** changes in application YAML configurations
- **Analyzing** apps against 6 DevOps maturity pillars
- **Generating** AI-ready prompts with context and guidelines
- **Automating** Windsurf chat interactions (optional)
- **Storing** structured recommendations for tracking

**Goal:** Provide agentic, context-aware recommendations that help teams improve their DevOps practices across all 6 pillars.

---

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENTIC WORKFLOW PIPELINE                     │
└─────────────────────────────────────────────────────────────────┘

Step 1: DETECT CHANGES
├─> Script: detect_app_changes.py
├─> Input: apps/ folder (git diff)
└─> Output: List of changed YAML files

        ↓

Step 2: ANALYZE APPS
├─> Script: analyze_app.py
├─> Input: Changed YAML files + 6 Pillar Skills
├─> Process: Extract fields, identify gaps per pillar
└─> Output: {app}_analysis.json

        ↓

Step 3: GENERATE AI PROMPT
├─> Script: generate_prompt.py
├─> Input: Analysis results + Skill guidelines
├─> Process: Create comprehensive prompt with context
└─> Output: {app}_prompt.txt

        ↓

Step 4: WINDSURF AUTOMATION (Optional)
├─> Script: automate_windsurf.sh
├─> Input: Generated prompt
├─> Process: Open Windsurf, paste prompt, trigger chat
└─> Output: AI generates recommendations

        ↓

Step 5: STORE RECOMMENDATIONS
├─> Format: Python dict + JSON
├─> Location: workflow/recommendations/
└─> Structure: Pillar-based with priorities and steps

        ↓

Step 6: INTEGRATE WITH DASHBOARD
├─> Load recommendations
├─> Display high-priority items
└─> Track implementation progress
```

---

## Prerequisites

### Required Tools
- Python 3.8+
- Git
- Windsurf IDE (for automation)
- PyYAML library

### Installation

```bash
# Install Python dependencies
pip install pyyaml

# Make scripts executable
chmod +x workflow/*.py workflow/*.sh

# Verify installation
python workflow/detect_app_changes.py --help
```

---

## Workflow Steps

### Step 1: Detect Changes in Apps Folder

**Purpose:** Identify which application YAML files have been modified or added.

**Script:** `detect_app_changes.py`

**How it works:**
1. Runs `git diff HEAD apps/` to find changes
2. Filters for `.yaml` and `.yml` files
3. Parses git status (Added, Modified, Deleted)
4. Returns structured list of changes

**Manual Execution:**
```bash
python workflow/detect_app_changes.py
```

**Expected Output:**
```json
[
  {
    "path": "apps/payment_service.yaml",
    "type": "modified",
    "status": "M",
    "app_name": "payment_service"
  }
]
```

**When to run:**
- After editing any app YAML file
- Before running the full workflow
- To check what will be analyzed

---

### Step 2: Analyze Apps Against 6 Pillars

**Purpose:** Evaluate each changed app against all 6 DevOps maturity pillars.

**Script:** `analyze_app.py`

**How it works:**
1. Loads the app YAML file
2. Loads all 6 pillar skill documents
3. For each pillar:
   - Extracts relevant fields from YAML
   - Identifies gaps (missing or poor configurations)
   - Records observations
4. Generates comprehensive analysis

**Manual Execution:**
```bash
python workflow/analyze_app.py apps/your_app.yaml
```

**Expected Output:**
- Console: Human-readable summary
- File: `{app}_analysis.json` with full details

**Analysis Structure:**
```json
{
  "app_name": "payment_service",
  "filepath": "apps/payment_service.yaml",
  "pillar_analyses": {
    "release_velocity": {
      "relevant_fields": {
        "repos": [...],
        "deployment_frequency": "weekly",
        "ci_cd_tools": "Not specified"
      },
      "gaps": [
        "No CI/CD tools specified",
        "Deployment frequency not optimal"
      ]
    },
    "git_hygiene": { ... },
    "pipeline_maturity": { ... },
    "compliance": { ... },
    "quality_security": { ... },
    "adoption": { ... }
  }
}
```

---

### Step 3: Generate AI Prompt

**Purpose:** Create a comprehensive, context-rich prompt for AI to generate recommendations.

**Script:** `generate_prompt.py`

**How it works:**
1. Takes analysis results from Step 2
2. Loads skill guidelines for context
3. Formats app configuration and gaps
4. Generates structured prompt with:
   - App context
   - Current state analysis
   - Identified gaps per pillar
   - Expected output format
   - Implementation guidelines

**Manual Execution:**
```bash
python workflow/generate_prompt.py apps/your_app.yaml
```

**Expected Output:**
- File: `workflow/recommendations/{app}_prompt.txt`

**Prompt Structure:**
```markdown
# DevOps Maturity Recommendations for {app_name}

## Application Context
**App Name:** payment_service
**Current Configuration:**
```yaml
[YAML content]
```

## Analysis Results
### Release Velocity
**Current State:**
- deployment_frequency: weekly
- ci_cd_tools: Not specified

**Gaps Identified:**
- ⚠️ No CI/CD tools specified
- ⚠️ Manual deployment process

[... other pillars ...]

## Your Task
Generate comprehensive recommendations with:
1. 2-3 specific actions per pillar
2. Priority levels (High/Medium/Low)
3. Implementation steps
4. Score impact estimates

## Output Format
```python
RECOMMENDATIONS = {
    'app_name': 'payment_service',
    'pillars': {
        'release_velocity': {
            'recommendations': [...]
        }
    }
}
```
```

---

### Step 4: Windsurf Automation (Optional)

**Purpose:** Automatically open Windsurf, start a chat, and paste the generated prompt.

**Script:** `automate_windsurf.sh`

**How it works (macOS):**
1. Opens new Windsurf window with project
2. Activates Windsurf application
3. Sends Cmd+L to open new chat
4. Copies prompt to clipboard
5. Pastes prompt into chat (Cmd+V)
6. Waits for user to review and submit

**Manual Execution:**
```bash
./workflow/automate_windsurf.sh workflow/recommendations/{app}_prompt.txt {app_name}
```

**Platform Support:**
- ✅ **macOS:** Full automation via AppleScript
- ⚠️ **Linux:** Manual steps (instructions provided)
- ⚠️ **Windows:** Manual steps (instructions provided)

**Manual Alternative (All Platforms):**
1. Open Windsurf
2. Press `Ctrl+L` (or `Cmd+L` on Mac) for new chat
3. Copy content from: `workflow/recommendations/{app}_prompt.txt`
4. Paste into chat
5. Review and press Enter

---

### Step 5: AI Generates Recommendations

**Purpose:** AI analyzes the prompt and generates structured, actionable recommendations.

**Process:**
1. AI reads the prompt with full context
2. Analyzes gaps and current state
3. Generates recommendations per pillar
4. Structures output as Python dict
5. Includes priorities, steps, and impact estimates

**Expected AI Output:**
```python
# recommendations.py - Auto-generated recommendations for payment_service

RECOMMENDATIONS = {
    'app_name': 'payment_service',
    'generated_date': '2024-03-26T23:00:00',
    'pillars': {
        'release_velocity': {
            'current_score': 45,
            'target_score': 75,
            'recommendations': [
                {
                    'title': 'Implement CI/CD Pipeline with GitHub Actions',
                    'priority': 'High',
                    'description': 'Set up automated build, test, and deploy pipeline',
                    'impact': 'Reduce deployment time from hours to minutes',
                    'implementation_steps': [
                        'Create .github/workflows/ci-cd.yml',
                        'Configure build and test stages',
                        'Add deployment automation',
                        'Set up environment-specific deployments'
                    ],
                    'estimated_score_gain': 20
                },
                {
                    'title': 'Increase Deployment Frequency',
                    'priority': 'Medium',
                    'description': 'Move from weekly to daily deployments',
                    'impact': 'Faster feature delivery, reduced batch size',
                    'implementation_steps': [
                        'Enable feature flags',
                        'Implement automated testing',
                        'Set up deployment monitoring',
                        'Train team on continuous deployment'
                    ],
                    'estimated_score_gain': 10
                }
            ]
        },
        'git_hygiene': { ... },
        'pipeline_maturity': { ... },
        'compliance': { ... },
        'quality_security': { ... },
        'adoption': { ... }
    },
    'summary': {
        'total_recommendations': 15,
        'high_priority_count': 6,
        'estimated_total_score_gain': 85,
        'implementation_timeline': '2-3 months'
    }
}
```

**Storage:**
- Python format: `workflow/recommendations/{app}_recommendations.py`
- JSON format: `workflow/recommendations/{app}_recommendations.json`

---

### Step 6: Store and Track Recommendations

**Purpose:** Save recommendations in structured format for tracking and integration.

**Storage Location:** `workflow/recommendations/`

**File Structure:**
```
workflow/recommendations/
├── payment_service_analysis.json          # Analysis results
├── payment_service_prompt.txt             # Generated prompt
├── payment_service_recommendations.py     # Python format
└── payment_service_recommendations.json   # JSON format
```

**Utilities:** `recommendations_template.py`

**Available Functions:**
```python
from workflow.recommendations_template import (
    save_recommendations,
    load_recommendations,
    get_high_priority_recommendations,
    generate_summary_report
)

# Load recommendations
recs = load_recommendations('payment_service')

# Get high-priority items
high_priority = get_high_priority_recommendations(recs)

# Generate report
report = generate_summary_report(recs)
```

---

## 6 Pillar Skills

Each pillar has a dedicated skill document that guides the AI analysis:

### 1. Release Velocity (30% weight)
**File:** `skills/release_velocity_skill.md`

**Focus Areas:**
- Deployment frequency (daily, weekly, monthly)
- Lead time for changes
- Release process automation
- Rollback capabilities

**Key Indicators:**
- ✅ Multiple deployments per day
- ✅ Automated deployment on merge
- ✅ Feature flags for gradual rollouts
- ✅ Zero-touch deployments

**Scoring:**
- **85-100:** Elite - Multiple daily deployments, full automation
- **70-84:** High - Daily/weekly deployments, mostly automated
- **50-69:** Medium - Weekly/bi-weekly, some automation
- **<50:** Low - Monthly or manual deployments

---

### 2. Git Hygiene (20% weight)
**File:** `skills/git_hygiene_skill.md`

**Focus Areas:**
- Branch management (stale branches)
- Pull request practices (size, reviews)
- Code review culture
- Branch protection policies

**Key Indicators:**
- ✅ No stale branches (auto-cleanup)
- ✅ Small PRs (<400 lines)
- ✅ Required reviews (1-2 reviewers)
- ✅ Fast review turnaround (<48 hours)

**Scoring:**
- **85-100:** Elite - No stale branches, small PRs, fast reviews
- **70-84:** High - Minimal stale branches, good PR practices
- **50-69:** Medium - Some stale branches, variable PR sizes
- **<50:** Low - Many stale branches, large PRs, slow reviews

---

### 3. Pipeline Maturity (20% weight)
**File:** `skills/pipeline_maturity_skill.md`

**Focus Areas:**
- CI/CD automation level
- Testing automation (unit, integration, E2E)
- Deployment automation
- Infrastructure as Code

**Key Indicators:**
- ✅ Fully automated CI/CD pipeline
- ✅ High test coverage (>80%)
- ✅ One-click deployments
- ✅ Automated rollback on failure

**Scoring:**
- **85-100:** Elite - Full automation, IaC, comprehensive testing
- **70-84:** High - Mostly automated, good testing
- **50-69:** Medium - Partial automation, basic testing
- **<50:** Low - Minimal automation, manual processes

---

### 4. Compliance (15% weight)
**File:** `skills/compliance_skill.md`

**Focus Areas:**
- Release documentation
- Access control and reviews
- Audit logging
- Compliance frameworks (SOX, GDPR, etc.)

**Key Indicators:**
- ✅ Automated release notes generation
- ✅ Quarterly access reviews
- ✅ Comprehensive audit logs
- ✅ Evidence collection for audits

**Scoring:**
- **85-100:** Elite - Full compliance automation, comprehensive docs
- **70-84:** High - Good documentation, regular reviews
- **50-69:** Medium - Basic documentation, some manual processes
- **<50:** Low - Minimal documentation, no regular reviews

---

### 5. Quality & Security (10% weight)
**File:** `skills/quality_security_skill.md`

**Focus Areas:**
- Security scanning (SAST, DAST)
- Code quality tools
- Privileged access management
- Secrets management

**Key Indicators:**
- ✅ Automated SAST/DAST in CI/CD
- ✅ No privileged access needed
- ✅ Secrets in vault/secrets manager
- ✅ Quality gates in pipeline

**Scoring:**
- **85-100:** Elite - Full security automation, no privileged access
- **70-84:** High - Good security practices, minimal privileged access
- **50-69:** Medium - Basic security, some privileged access
- **<50:** Low - Minimal security, high privileged access

---

### 6. Adoption (5% weight)
**File:** `skills/adoption_skill.md`

**Focus Areas:**
- AI/Copilot adoption
- API catalog presence
- Containerization
- Modern development practices

**Key Indicators:**
- ✅ GitHub Copilot enabled
- ✅ APIs in central catalog
- ✅ Containerized applications
- ✅ Cloud-native architecture

**Scoring:**
- **85-100:** Elite - Full AI adoption, comprehensive API catalog
- **70-84:** High - Good tool adoption, APIs documented
- **50-69:** Medium - Some modern tools, basic API docs
- **<50:** Low - Minimal modern tool adoption

---

## Usage Examples

### Example 1: Full Automated Workflow

```bash
# Step 1: Make changes to an app
vim apps/payment_service.yaml

# Step 2: Run complete workflow
python workflow/run_workflow.py

# Output:
# ============================================================
# 🚀 AGENTIC RECOMMENDATION WORKFLOW
# ============================================================
#
# 📋 Step 1: Detecting changes in apps folder...
# ✓ Found 1 changed file(s):
#   - apps/payment_service.yaml (modified)
#
# 🔍 Step 2: Analyzing changed apps against 6 pillar skills...
#   → Analyzing: payment_service
#     ✓ Analysis saved to: payment_service_analysis.json
#
# 💡 Step 3: Generating recommendation prompts...
#   → Generating prompt for: payment_service
#     ✓ Prompt saved to: payment_service_prompt.txt
#
# ⏭️  Step 4: Skipping Windsurf automation (use --auto flag)
#
# 📝 Manual steps:
#   For payment_service:
#   1. Run: ./workflow/automate_windsurf.sh workflow/recommendations/payment_service_prompt.txt payment_service
#   2. Or manually paste prompt from: workflow/recommendations/payment_service_prompt.txt

# Step 3: Trigger Windsurf (macOS)
./workflow/automate_windsurf.sh workflow/recommendations/payment_service_prompt.txt payment_service

# Step 4: Review and submit in Windsurf chat

# Step 5: Check generated recommendations
cat workflow/recommendations/payment_service_recommendations.py
```

---

### Example 2: Step-by-Step Manual Workflow

```bash
# Step 1: Detect changes
python workflow/detect_app_changes.py

# Step 2: Analyze specific app
python workflow/analyze_app.py apps/payment_service.yaml

# Step 3: Generate prompt
python workflow/generate_prompt.py apps/payment_service.yaml

# Step 4: Manually in Windsurf
# - Open Windsurf
# - Press Cmd+L (or Ctrl+L)
# - Paste content from: workflow/recommendations/payment_service_prompt.txt
# - Press Enter

# Step 5: Save AI output
# - Copy AI response
# - Save to: workflow/recommendations/payment_service_recommendations.py
```

---

### Example 3: Testing with Example App

```bash
# Quick test with provided example
./workflow/test_workflow.sh

# This will:
# 1. Copy example_app.yaml to apps/test_payment_app.yaml
# 2. Run detection
# 3. Run analysis
# 4. Generate prompt
# 5. Show next steps

# Clean up after testing
git reset HEAD apps/test_payment_app.yaml
rm apps/test_payment_app.yaml
rm -rf workflow/recommendations/
```

---

## Output Structure

### Analysis Output (`{app}_analysis.json`)

```json
{
  "app_name": "payment_service",
  "filepath": "apps/payment_service.yaml",
  "app_data": { ... },
  "pillar_analyses": {
    "release_velocity": {
      "pillar": "release_velocity",
      "observations": [],
      "gaps": [
        "No CI/CD tools specified",
        "Deployment frequency not documented"
      ],
      "relevant_fields": {
        "repos": [...],
        "deployment_frequency": "weekly",
        "ci_cd_tools": "Not specified"
      }
    },
    ...
  }
}
```

---

### Recommendations Output (`{app}_recommendations.py`)

```python
RECOMMENDATIONS = {
    'app_name': 'payment_service',
    'generated_date': '2024-03-26T23:00:00',
    'pillars': {
        'release_velocity': {
            'current_score': 45,
            'target_score': 75,
            'recommendations': [
                {
                    'title': 'Implement CI/CD Pipeline',
                    'priority': 'High',
                    'description': '...',
                    'impact': '...',
                    'implementation_steps': [...],
                    'estimated_score_gain': 20
                }
            ]
        }
    },
    'summary': {
        'total_recommendations': 15,
        'high_priority_count': 6,
        'estimated_total_score_gain': 85,
        'implementation_timeline': '2-3 months'
    }
}
```

---

## Integration Guide

### Integrate with Dashboard

```python
# In your dashboard code (app.py)
from workflow.recommendations_template import (
    load_recommendations,
    get_high_priority_recommendations
)

# Load recommendations for an app
app_name = "payment_service"
recs = load_recommendations(app_name)

if recs:
    # Display in Streamlit
    st.subheader(f"📋 Recommendations for {app_name}")
    
    # Get high-priority items
    high_priority = get_high_priority_recommendations(recs)
    
    for rec in high_priority:
        pillar = rec['pillar'].replace('_', ' ').title()
        
        with st.expander(f"🔴 {rec['title']} ({pillar})"):
            st.write(f"**Priority:** {rec['priority']}")
            st.write(f"**Description:** {rec['description']}")
            st.write(f"**Impact:** {rec['impact']}")
            st.write(f"**Score Gain:** +{rec['estimated_score_gain']} points")
            
            st.write("**Implementation Steps:**")
            for i, step in enumerate(rec['implementation_steps'], 1):
                st.write(f"{i}. {step}")
```

---

### Track Implementation Progress

```python
# Add tracking to recommendations
def mark_recommendation_complete(app_name, pillar, rec_title):
    recs = load_recommendations(app_name)
    
    for rec in recs['pillars'][pillar]['recommendations']:
        if rec['title'] == rec_title:
            rec['status'] = 'completed'
            rec['completed_date'] = datetime.now().isoformat()
    
    save_recommendations(app_name, recs)

# Display progress
def show_implementation_progress(app_name):
    recs = load_recommendations(app_name)
    
    total = recs['summary']['total_recommendations']
    completed = sum(
        1 for pillar in recs['pillars'].values()
        for rec in pillar['recommendations']
        if rec.get('status') == 'completed'
    )
    
    progress = (completed / total) * 100
    st.progress(progress / 100)
    st.write(f"Progress: {completed}/{total} ({progress:.1f}%)")
```

---

## Troubleshooting

### Issue: No changes detected

**Problem:** `detect_app_changes.py` returns empty list

**Solutions:**
```bash
# Check git status
git status

# Make sure you have uncommitted changes
echo "# test change" >> apps/test_app.yaml

# Or check staged changes
git add apps/your_app.yaml
```

---

### Issue: Windsurf automation not working

**Problem:** Script doesn't open Windsurf or paste prompt

**Solutions:**

**macOS:**
```bash
# Check if Windsurf is installed
which windsurf

# Manually trigger:
open -na "Windsurf" --args "$(pwd)"
```

**All Platforms:**
```bash
# Manual alternative:
# 1. Open Windsurf manually
# 2. Press Ctrl+L (Cmd+L on Mac)
# 3. Paste from: workflow/recommendations/{app}_prompt.txt
```

---

### Issue: Analysis errors

**Problem:** `analyze_app.py` fails with YAML error

**Solutions:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('apps/your_app.yaml'))"

# Check file exists
ls -la apps/your_app.yaml

# Check file permissions
chmod 644 apps/your_app.yaml
```

---

### Issue: Missing skill files

**Problem:** Skill documents not found

**Solutions:**
```bash
# Check skill files exist
ls -la workflow/skills/

# Should see:
# - release_velocity_skill.md
# - git_hygiene_skill.md
# - pipeline_maturity_skill.md
# - compliance_skill.md
# - quality_security_skill.md
# - adoption_skill.md

# If missing, they're in the workflow/skills/ directory
```

---

### Issue: Recommendations not saving

**Problem:** AI generates recommendations but they're not saved

**Solutions:**
```bash
# Create recommendations directory
mkdir -p workflow/recommendations

# Check write permissions
chmod 755 workflow/recommendations

# Manually save AI output:
# 1. Copy AI response from Windsurf
# 2. Save to: workflow/recommendations/{app}_recommendations.py
```

---

## Best Practices

### 1. Regular Workflow Runs

Run the workflow after significant changes:
- New app added
- Major configuration changes
- Quarterly reviews

### 2. Customize Skill Documents

Tailor skill files to your organization:
- Add company-specific requirements
- Adjust scoring thresholds
- Include internal tools and practices

### 3. Track Implementation

- Mark recommendations as completed
- Track score improvements
- Review progress quarterly

### 4. Integrate with CI/CD

```yaml
# .github/workflows/recommendations.yml
name: Generate Recommendations

on:
  push:
    paths:
      - 'apps/**/*.yaml'

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run workflow
        run: python workflow/run_workflow.py
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: recommendations
          path: workflow/recommendations/
```

---

## Summary

This agentic workflow provides:

✅ **Automated change detection** via git diff  
✅ **6-pillar analysis** with skill-based evaluation  
✅ **AI prompt generation** with full context  
✅ **Windsurf automation** for seamless workflow  
✅ **Structured recommendations** with priorities and steps  
✅ **Dashboard integration** for tracking progress  

**Next Steps:**
1. Test with `./workflow/test_workflow.sh`
2. Customize skill documents for your org
3. Run workflow on real apps
4. Integrate with dashboard
5. Track implementation progress

---

**For questions or issues, refer to the README.md or contact the DevOps team.**
