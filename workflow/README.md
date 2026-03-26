# Agentic Recommendation Workflow

Automated workflow for generating DevOps maturity recommendations using AI analysis of application configurations.

## Overview

This workflow automates the process of:
1. Detecting changes in application YAML files
2. Analyzing apps against 6 DevOps maturity pillars
3. Generating AI prompts for recommendations
4. Automating Windsurf chat interactions (optional)
5. Storing recommendations for tracking

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Workflow Components                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. detect_app_changes.py                                   │
│     └─> Detects changed YAML files using git diff           │
│                                                              │
│  2. analyze_app.py                                           │
│     └─> Analyzes apps against 6 pillar skills               │
│                                                              │
│  3. generate_prompt.py                                       │
│     └─> Creates AI prompts for recommendations              │
│                                                              │
│  4. automate_windsurf.sh                                     │
│     └─> Opens Windsurf and pastes prompt                    │
│                                                              │
│  5. run_workflow.py                                          │
│     └─> Orchestrates entire workflow                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 6 Pillar Skills

Each pillar has a dedicated skill document that guides the analysis:

1. **Release Velocity (30%)** - `skills/release_velocity_skill.md`
   - Deployment frequency, lead time, release automation

2. **Git Hygiene (20%)** - `skills/git_hygiene_skill.md`
   - Branch management, PR practices, code reviews

3. **Pipeline Maturity (20%)** - `skills/pipeline_maturity_skill.md`
   - CI/CD automation, testing, deployment automation

4. **Compliance (15%)** - `skills/compliance_skill.md`
   - Documentation, access control, audit trails

5. **Quality & Security (10%)** - `skills/quality_security_skill.md`
   - Security scanning, code quality, privileged access

6. **Adoption (5%)** - `skills/adoption_skill.md`
   - AI tools, API catalog, modern practices

## Installation

```bash
# Make scripts executable
chmod +x workflow/run_workflow.py
chmod +x workflow/automate_windsurf.sh
chmod +x workflow/detect_app_changes.py
chmod +x workflow/analyze_app.py
chmod +x workflow/generate_prompt.py

# Install dependencies (if needed)
pip install pyyaml
```

## Usage

### Quick Start - Full Automated Workflow

```bash
# Run complete workflow (manual Windsurf step)
python workflow/run_workflow.py

# Run with automatic Windsurf triggering
python workflow/run_workflow.py --auto
```

### Step-by-Step Manual Workflow

#### Step 1: Detect Changes

```bash
python workflow/detect_app_changes.py
```

This will show all changed YAML files in the `apps/` folder.

#### Step 2: Analyze a Specific App

```bash
python workflow/analyze_app.py apps/your_app.yaml
```

This generates:
- Console output with analysis summary
- `your_app_analysis.json` with full analysis

#### Step 3: Generate Recommendation Prompt

```bash
python workflow/generate_prompt.py apps/your_app.yaml
```

This generates:
- `workflow/generated_prompt.txt` with AI prompt

#### Step 4: Trigger Windsurf (macOS)

```bash
./workflow/automate_windsurf.sh workflow/generated_prompt.txt your_app
```

This will:
- Open new Windsurf window
- Open chat (Cmd+L)
- Paste the prompt
- Wait for you to review and submit

#### Step 5: Review Recommendations

After AI generates recommendations, they'll be in:
- `workflow/recommendations/your_app_recommendations.py`
- `workflow/recommendations/your_app_recommendations.json`

## Workflow Outputs

All outputs are stored in `workflow/recommendations/`:

```
workflow/recommendations/
├── app1_analysis.json          # Analysis results
├── app1_prompt.txt             # Generated AI prompt
├── app1_recommendations.py     # Python format recommendations
└── app1_recommendations.json   # JSON format recommendations
```

## Example: Complete Workflow

```bash
# 1. Make a change to an app YAML file
vim apps/my_app.yaml

# 2. Run the workflow
python workflow/run_workflow.py

# Output:
# ============================================================
# 🚀 AGENTIC RECOMMENDATION WORKFLOW
# ============================================================
#
# 📋 Step 1: Detecting changes in apps folder...
# ✓ Found 1 changed file(s):
#   - apps/my_app.yaml (modified)
#
# 🔍 Step 2: Analyzing changed apps against 6 pillar skills...
#   → Analyzing: my_app
#     ✓ Analysis saved to: my_app_analysis.json
#
# 💡 Step 3: Generating recommendation prompts...
#   → Generating prompt for: my_app
#     ✓ Prompt saved to: my_app_prompt.txt
#
# ⏭️  Step 4: Skipping Windsurf automation (use --auto flag)
#
# 📝 Manual steps:
#   For my_app:
#   1. Run: ./workflow/automate_windsurf.sh workflow/recommendations/my_app_prompt.txt my_app
#   2. Or manually paste prompt from: workflow/recommendations/my_app_prompt.txt
#
# ============================================================
# 📊 WORKFLOW SUMMARY
# ============================================================
# Changed files: 1
# Analyzed apps: 1
# Prompts generated: 1
#
# 📁 Recommendations directory: workflow/recommendations
#
# ✅ Workflow complete!

# 3. Trigger Windsurf automation
./workflow/automate_windsurf.sh workflow/recommendations/my_app_prompt.txt my_app

# 4. Review and submit in Windsurf chat

# 5. Check generated recommendations
cat workflow/recommendations/my_app_recommendations.py
```

## Customization

### Adding Custom Analysis Logic

Edit `workflow/analyze_app.py` to add custom analysis logic for each pillar:

```python
def _analyze_pillar(self, pillar_name: str, skill_content: str, app_data: Dict) -> Dict:
    # Add your custom logic here
    pass
```

### Modifying Skill Documents

Edit the skill markdown files in `workflow/skills/` to adjust:
- Analysis criteria
- Scoring guidelines
- Recommendation templates
- Red flags to watch for

### Customizing Prompts

Edit `workflow/generate_prompt.py` to customize the AI prompt structure:

```python
def generate_recommendation_prompt(self, filepath: str, analysis: Dict = None) -> str:
    # Customize prompt generation here
    pass
```

## Platform-Specific Notes

### macOS
- Full automation supported
- Uses AppleScript for Windsurf control
- Clipboard integration for prompt pasting

### Linux
- Manual Windsurf steps required
- Automation script provides instructions

### Windows
- Manual Windsurf steps required
- Use Git Bash or WSL for running scripts

## Troubleshooting

### No changes detected
```bash
# Make sure you have uncommitted changes
git status

# Or make a test change
echo "# test" >> apps/test_app.yaml
```

### Windsurf automation not working
```bash
# Check if Windsurf is installed
which windsurf

# Manually paste prompt from:
cat workflow/recommendations/your_app_prompt.txt
```

### Analysis errors
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('apps/your_app.yaml'))"
```

## Integration with Dashboard

Recommendations can be integrated into the main dashboard:

```python
from workflow.recommendations_template import load_recommendations

# Load recommendations for an app
recs = load_recommendations('my_app')

# Get high-priority items
high_priority = get_high_priority_recommendations(recs)

# Display in dashboard
for rec in high_priority:
    print(f"{rec['pillar']}: {rec['title']}")
```

## Future Enhancements

- [ ] Automatic recommendation tracking
- [ ] Integration with metrics database
- [ ] Progress tracking for implemented recommendations
- [ ] Scheduled workflow runs (cron/GitHub Actions)
- [ ] Slack/Teams notifications
- [ ] Web UI for viewing recommendations

## Contributing

To add new analysis capabilities:

1. Update skill documents in `workflow/skills/`
2. Add analysis logic in `workflow/analyze_app.py`
3. Update prompt template in `workflow/generate_prompt.py`
4. Test with sample YAML files

## License

Internal use only - Part of DevOps Gamification Dashboard
