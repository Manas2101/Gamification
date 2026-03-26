#!/usr/bin/env python3
"""
Generate AI prompt for recommendations based on app analysis
This prompt will be passed to Windsurf chat for generating recommendations
"""

import json
from pathlib import Path
from typing import Dict
from analyze_app import AppAnalyzer

class PromptGenerator:
    def __init__(self):
        self.analyzer = AppAnalyzer()
    
    def generate_recommendation_prompt(self, filepath: str, analysis: Dict = None) -> str:
        """
        Generate a comprehensive prompt for AI to create recommendations
        """
        if analysis is None:
            analysis = self.analyzer.analyze_app(filepath)
        
        app_name = analysis['app_name']
        app_data = analysis['app_data']
        
        prompt = f"""# DevOps Maturity Recommendations for {app_name}

You are a DevOps expert analyzing an application's configuration to provide actionable recommendations across 6 pillars of DevOps maturity.

## Application Context

**App Name:** {app_name}
**File:** {filepath}

**Current Configuration:**
```yaml
{self._format_yaml_snippet(app_data)}
```

## Analysis Results

{self._format_pillar_analyses(analysis['pillar_analyses'])}

## Your Task

Based on the analysis above, generate comprehensive, actionable recommendations for this application across all 6 pillars. For each pillar where gaps were identified:

1. **Provide 2-3 specific, actionable recommendations**
2. **Prioritize recommendations** (High/Medium/Low)
3. **Include implementation steps** that are practical and specific
4. **Estimate the impact** on the pillar score
5. **Consider dependencies** between recommendations

## Output Format

Please structure your response as follows:

```python
# recommendations.py - Auto-generated recommendations for {app_name}

RECOMMENDATIONS = {{
    'app_name': '{app_name}',
    'generated_date': '<current_date>',
    'pillars': {{
        'release_velocity': {{
            'current_score': <estimated_score>,
            'target_score': <target_score>,
            'recommendations': [
                {{
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
                }},
                # ... more recommendations
            ]
        }},
        'git_hygiene': {{
            # ... similar structure
        }},
        'pipeline_maturity': {{
            # ... similar structure
        }},
        'compliance': {{
            # ... similar structure
        }},
        'quality_security': {{
            # ... similar structure
        }},
        'adoption': {{
            # ... similar structure
        }}
    }},
    'summary': {{
        'total_recommendations': <count>,
        'high_priority_count': <count>,
        'estimated_total_score_gain': <points>,
        'implementation_timeline': '<estimated_timeline>'
    }}
}}
```

## Important Guidelines

1. **Be specific**: Don't just say "improve CI/CD" - specify which tools, which steps, which configurations
2. **Be realistic**: Recommendations should be achievable within 1-3 months
3. **Consider the current state**: Build on what exists, don't recommend starting from scratch unless necessary
4. **Prioritize impact**: Focus on high-impact, low-effort wins first
5. **Think holistically**: Consider how recommendations in one pillar affect others

## Reference Skills

Use the following skill documents as reference for best practices:

{self._include_skill_summaries()}

---

Please generate the comprehensive recommendations now.
"""
        
        return prompt
    
    def _format_yaml_snippet(self, app_data: Dict) -> str:
        """Format YAML data for display in prompt"""
        import yaml
        return yaml.dump(app_data, default_flow_style=False, sort_keys=False)
    
    def _format_pillar_analyses(self, pillar_analyses: Dict) -> str:
        """Format pillar analyses for prompt"""
        output = ""
        
        for pillar_name, analysis in pillar_analyses.items():
            output += f"### {pillar_name.replace('_', ' ').title()}\n\n"
            
            if analysis['relevant_fields']:
                output += "**Current State:**\n"
                for field, value in analysis['relevant_fields'].items():
                    output += f"- {field}: `{value}`\n"
                output += "\n"
            
            if analysis['gaps']:
                output += "**Gaps Identified:**\n"
                for gap in analysis['gaps']:
                    output += f"- ⚠️ {gap}\n"
                output += "\n"
            else:
                output += "**Gaps:** None identified (configuration looks good)\n\n"
            
            output += "---\n\n"
        
        return output
    
    def _include_skill_summaries(self) -> str:
        """Include brief summaries of skill documents"""
        summaries = """
**Release Velocity (30%):** Focus on deployment frequency, lead time, and release automation
**Git Hygiene (20%):** Focus on branch management, PR practices, and code review culture
**Pipeline Maturity (20%):** Focus on CI/CD automation, testing, and deployment automation
**Compliance (15%):** Focus on documentation, access control, and audit trails
**Quality & Security (10%):** Focus on security scanning, code quality, and privileged access
**Adoption (5%):** Focus on AI tools, API catalog, and modern practices
"""
        return summaries
    
    def save_prompt(self, prompt: str, output_file: str = None) -> str:
        """Save generated prompt to file"""
        if output_file is None:
            output_file = "workflow/generated_prompt.txt"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(prompt)
        
        return str(output_path)


def main():
    """Test prompt generation"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_prompt.py <path_to_yaml>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    generator = PromptGenerator()
    prompt = generator.generate_recommendation_prompt(filepath)
    
    # Save prompt
    output_file = generator.save_prompt(prompt)
    
    print(f"Prompt generated and saved to: {output_file}")
    print("\n" + "="*60)
    print("GENERATED PROMPT:")
    print("="*60)
    print(prompt)


if __name__ == "__main__":
    main()
