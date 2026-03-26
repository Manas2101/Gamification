# Agentic Recommendation Workflow

This workflow automates the generation of DevOps maturity recommendations by analyzing application YAML files against 6 pillars.

## Workflow Steps

### Step 1: Detect Changes in Apps Folder

Check for any changes or new apps added in the `apps/` folder using git diff.

**Action:**
```bash
cd /Users/kritikapandey/Desktop/Gamification
python3 workflow/detect_app_changes.py
```

**Expected Output:**
- List of changed YAML files (added, modified, deleted)
- If no changes found, stop the workflow

**Decision Point:**
- If changes found → Continue to Step 2
- If no changes → Stop workflow

---

### Step 2: Analyze Changed Apps Against 6 Pillar Skills

For each changed app, analyze it against all 6 DevOps maturity pillars:
1. Release Velocity (30%)
2. Git Hygiene (20%)
3. Pipeline Maturity (20%)
4. Compliance (15%)
5. Quality & Security (10%)
6. Adoption (5%)

**Action:**
For each changed app file found in Step 1:
```bash
python3 workflow/analyze_app.py apps/{app_name}.yaml
```

**Expected Output:**
- `workflow/recommendations/{app_name}_analysis.json` - Full analysis results
- Console output showing gaps identified per pillar

**Skills Reference:**
- `workflow/skills/release_velocity_skill.md`
- `workflow/skills/git_hygiene_skill.md`
- `workflow/skills/pipeline_maturity_skill.md`
- `workflow/skills/compliance_skill.md`
- `workflow/skills/quality_security_skill.md`
- `workflow/skills/adoption_skill.md`

---

### Step 3: Generate AI Recommendation Prompts

Create comprehensive prompts for AI to generate recommendations based on the analysis.

**Action:**
For each analyzed app:
```bash
python3 workflow/generate_prompt.py apps/{app_name}.yaml
```

**Expected Output:**
- `workflow/recommendations/{app_name}_prompt.txt` - AI-ready prompt with full context

**Prompt Structure:**
- Application context and current configuration
- Analysis results per pillar
- Identified gaps and observations
- Expected output format (Python dict)
- Implementation guidelines

---

### Step 4: Trigger Windsurf Chat with Prompt

Open a new Windsurf window and paste the generated prompt into a new chat session.

**Action (macOS):**
```bash
./workflow/automate_windsurf.sh workflow/recommendations/{app_name}_prompt.txt {app_name}
```

**Manual Alternative (All Platforms):**
1. Open Windsurf IDE
2. Press `Cmd+L` (macOS) or `Ctrl+L` (Windows/Linux) to open new chat
3. Copy content from: `workflow/recommendations/{app_name}_prompt.txt`
4. Paste into chat
5. Review the prompt
6. Press Enter to submit

**What Happens:**
- Windsurf AI analyzes the prompt
- Generates structured recommendations per pillar
- Provides implementation steps and priority levels
- Estimates score impact for each recommendation

---

### Step 5: Save AI-Generated Recommendations

The AI will generate recommendations in the following format:

```python
RECOMMENDATIONS = {
    'app_name': '{app_name}',
    'generated_date': '<timestamp>',
    'pillars': {
        'release_velocity': {
            'current_score': <score>,
            'target_score': <score>,
            'recommendations': [
                {
                    'title': '<recommendation_title>',
                    'priority': 'High/Medium/Low',
                    'description': '<what_to_do>',
                    'impact': '<expected_impact>',
                    'implementation_steps': [
                        '<step_1>',
                        '<step_2>',
                        '<step_3>'
                    ],
                    'estimated_score_gain': <points>
                }
            ]
        },
        # ... other pillars
    },
    'summary': {
        'total_recommendations': <count>,
        'high_priority_count': <count>,
        'estimated_total_score_gain': <points>,
        'implementation_timeline': '<timeline>'
    }
}
```

**Action:**
Save the AI output to:
- `workflow/recommendations/{app_name}_recommendations.py` (Python format)
- `workflow/recommendations/{app_name}_recommendations.json` (JSON format)

---

### Step 6: Review and Store Recommendations

Review the generated recommendations and store them for tracking.

**Action:**
```bash
# View recommendations
cat workflow/recommendations/{app_name}_recommendations.py

# Or view JSON format
cat workflow/recommendations/{app_name}_recommendations.json
```

**Next Steps:**
- Review high-priority recommendations
- Plan implementation timeline
- Track progress in dashboard
- Update app YAML as recommendations are implemented

---

## Quick Start Commands

### Run Full Workflow (Automated)
```bash
cd /Users/kritikapandey/Desktop/Gamification
python3 workflow/run_workflow.py
```

### Run Full Workflow with Windsurf Automation (macOS)
```bash
python3 workflow/run_workflow.py --auto
```

### Test Workflow with Example App
```bash
./workflow/test_workflow.sh
```

---

## Workflow Outputs

All outputs are stored in `workflow/recommendations/`:

```
workflow/recommendations/
├── {app}_analysis.json          # Analysis results per pillar
├── {app}_prompt.txt             # Generated AI prompt
├── {app}_recommendations.py     # Python format recommendations
└── {app}_recommendations.json   # JSON format recommendations
```

---

## Integration with Dashboard

Load and display recommendations in the dashboard:

```python
from workflow.recommendations_template import load_recommendations, get_high_priority_recommendations

# Load recommendations
app_name = "payment_service"
recs = load_recommendations(app_name)

# Get high-priority items
high_priority = get_high_priority_recommendations(recs)

# Display in Streamlit
for rec in high_priority:
    st.write(f"**{rec['pillar']}:** {rec['title']}")
    st.write(f"Priority: {rec['priority']}")
    st.write(f"Score Gain: +{rec['estimated_score_gain']} points")
```

---

## Troubleshooting

### No changes detected
```bash
# Check git status
git status

# Make a test change
echo "# test" >> apps/test_app.yaml
```

### Windsurf automation not working
```bash
# Manual steps:
# 1. Open Windsurf
# 2. Press Cmd+L (or Ctrl+L)
# 3. Paste from: workflow/recommendations/{app}_prompt.txt
```

### Analysis errors
```bash
# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('apps/your_app.yaml'))"
```

---

## Summary

This workflow provides automated, agentic recommendations for DevOps maturity improvements:

✅ Detects changes in app configurations  
✅ Analyzes against 6 DevOps pillars  
✅ Generates AI-ready prompts with context  
✅ Automates Windsurf chat interactions  
✅ Stores structured recommendations  
✅ Integrates with dashboard for tracking  

**Run the workflow whenever app configurations change to get fresh, context-aware recommendations.**
