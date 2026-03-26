"""
Recommendations Template
This file shows the structure for storing AI-generated recommendations
"""

from datetime import datetime
from typing import Dict, List

# Template structure for recommendations
RECOMMENDATIONS_TEMPLATE = {
    'app_name': 'example_app',
    'generated_date': datetime.now().isoformat(),
    'pillars': {
        'release_velocity': {
            'current_score': 0,
            'target_score': 0,
            'recommendations': [
                {
                    'title': 'Example Recommendation',
                    'priority': 'High',  # High, Medium, Low
                    'description': 'What needs to be done',
                    'impact': 'Expected impact on the pillar',
                    'implementation_steps': [
                        'Step 1',
                        'Step 2',
                        'Step 3'
                    ],
                    'estimated_score_gain': 10
                }
            ]
        },
        'git_hygiene': {
            'current_score': 0,
            'target_score': 0,
            'recommendations': []
        },
        'pipeline_maturity': {
            'current_score': 0,
            'target_score': 0,
            'recommendations': []
        },
        'compliance': {
            'current_score': 0,
            'target_score': 0,
            'recommendations': []
        },
        'quality_security': {
            'current_score': 0,
            'target_score': 0,
            'recommendations': []
        },
        'adoption': {
            'current_score': 0,
            'target_score': 0,
            'recommendations': []
        }
    },
    'summary': {
        'total_recommendations': 0,
        'high_priority_count': 0,
        'estimated_total_score_gain': 0,
        'implementation_timeline': '1-3 months'
    }
}


def save_recommendations(app_name: str, recommendations: Dict, output_dir: str = "workflow/recommendations"):
    """
    Save recommendations to a Python file
    
    Args:
        app_name: Name of the application
        recommendations: Dictionary containing recommendations
        output_dir: Directory to save recommendations
    """
    from pathlib import Path
    import json
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save as Python file
    py_file = output_path / f"{app_name}_recommendations.py"
    
    with open(py_file, 'w') as f:
        f.write(f'"""\nRecommendations for {app_name}\n')
        f.write(f'Generated: {recommendations.get("generated_date", "")}\n')
        f.write('"""\n\n')
        f.write('RECOMMENDATIONS = ')
        f.write(json.dumps(recommendations, indent=4))
        f.write('\n')
    
    # Also save as JSON for easy parsing
    json_file = output_path / f"{app_name}_recommendations.json"
    with open(json_file, 'w') as f:
        json.dump(recommendations, f, indent=2)
    
    return str(py_file), str(json_file)


def load_recommendations(app_name: str, recommendations_dir: str = "workflow/recommendations"):
    """
    Load recommendations from JSON file
    
    Args:
        app_name: Name of the application
        recommendations_dir: Directory containing recommendations
    
    Returns:
        Dictionary containing recommendations
    """
    from pathlib import Path
    import json
    
    json_file = Path(recommendations_dir) / f"{app_name}_recommendations.json"
    
    if not json_file.exists():
        return None
    
    with open(json_file, 'r') as f:
        return json.load(f)


def get_high_priority_recommendations(recommendations: Dict) -> List[Dict]:
    """
    Extract all high-priority recommendations across all pillars
    
    Args:
        recommendations: Dictionary containing recommendations
    
    Returns:
        List of high-priority recommendations
    """
    high_priority = []
    
    for pillar_name, pillar_data in recommendations.get('pillars', {}).items():
        for rec in pillar_data.get('recommendations', []):
            if rec.get('priority') == 'High':
                rec['pillar'] = pillar_name
                high_priority.append(rec)
    
    return high_priority


def generate_summary_report(recommendations: Dict) -> str:
    """
    Generate a human-readable summary report
    
    Args:
        recommendations: Dictionary containing recommendations
    
    Returns:
        Formatted summary report
    """
    app_name = recommendations.get('app_name', 'Unknown')
    summary = recommendations.get('summary', {})
    
    report = f"""
# Recommendations Summary for {app_name}

**Generated:** {recommendations.get('generated_date', 'N/A')}

## Overview
- Total Recommendations: {summary.get('total_recommendations', 0)}
- High Priority: {summary.get('high_priority_count', 0)}
- Estimated Score Gain: +{summary.get('estimated_total_score_gain', 0)} points
- Implementation Timeline: {summary.get('implementation_timeline', 'N/A')}

## Pillar Breakdown

"""
    
    for pillar_name, pillar_data in recommendations.get('pillars', {}).items():
        rec_count = len(pillar_data.get('recommendations', []))
        if rec_count == 0:
            continue
        
        report += f"### {pillar_name.replace('_', ' ').title()}\n"
        report += f"- Current Score: {pillar_data.get('current_score', 'N/A')}\n"
        report += f"- Target Score: {pillar_data.get('target_score', 'N/A')}\n"
        report += f"- Recommendations: {rec_count}\n\n"
        
        for rec in pillar_data.get('recommendations', []):
            report += f"**{rec.get('title', 'N/A')}** (Priority: {rec.get('priority', 'N/A')})\n"
            report += f"- {rec.get('description', 'N/A')}\n"
            report += f"- Score Gain: +{rec.get('estimated_score_gain', 0)} points\n\n"
    
    return report
