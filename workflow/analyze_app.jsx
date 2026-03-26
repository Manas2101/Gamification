#!/usr/bin/env python3
"""
Analyze a YAML app file against all 6 pillar skills
Generate comprehensive recommendations
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List

class AppAnalyzer:
    def __init__(self, skills_dir: str = "workflow/skills"):
        self.skills_dir = Path(skills_dir)
        self.project_root = Path(__file__).parent.parent
        
        # Load all skill files
        self.skills = {
            'release_velocity': self._load_skill('release_velocity_skill.md'),
            'git_hygiene': self._load_skill('git_hygiene_skill.md'),
            'pipeline_maturity': self._load_skill('pipeline_maturity_skill.md'),
            'compliance': self._load_skill('compliance_skill.md'),
            'quality_security': self._load_skill('quality_security_skill.md'),
            'adoption': self._load_skill('adoption_skill.md')
        }
    
    def _load_skill(self, filename: str) -> str:
        """Load a skill markdown file"""
        skill_path = self.project_root / self.skills_dir / filename
        
        if not skill_path.exists():
            return ""
        
        with open(skill_path, 'r') as f:
            return f.read()
    
    def load_yaml_app(self, filepath: str) -> Dict:
        """Load and parse YAML app file"""
        full_path = self.project_root / filepath
        
        with open(full_path, 'r') as f:
            return yaml.safe_load(f)
    
    def analyze_app(self, filepath: str, app_data: Dict = None) -> Dict:
        """
        Analyze an app YAML file against all 6 pillars
        Returns analysis results for prompt generation
        """
        if app_data is None:
            app_data = self.load_yaml_app(filepath)
        
        app_name = app_data.get('app_name', Path(filepath).stem)
        
        analysis = {
            'app_name': app_name,
            'filepath': filepath,
            'app_data': app_data,
            'pillar_analyses': {}
        }
        
        # Analyze each pillar
        for pillar_name, skill_content in self.skills.items():
            pillar_analysis = self._analyze_pillar(
                pillar_name, 
                skill_content, 
                app_data
            )
            analysis['pillar_analyses'][pillar_name] = pillar_analysis
        
        return analysis
    
    def _analyze_pillar(self, pillar_name: str, skill_content: str, app_data: Dict) -> Dict:
        """
        Analyze app against a specific pillar
        Extract relevant fields and identify gaps
        """
        analysis = {
            'pillar': pillar_name,
            'observations': [],
            'gaps': [],
            'relevant_fields': {}
        }
        
        # Extract relevant fields based on pillar
        if pillar_name == 'release_velocity':
            analysis['relevant_fields'] = {
                'repos': app_data.get('repos', []),
                'deployment_frequency': app_data.get('deployment_frequency', 'Not specified'),
                'ci_cd_tools': app_data.get('ci_cd_tools', 'Not specified'),
                'release_strategy': app_data.get('release_strategy', 'Not specified')
            }
            
            # Identify gaps
            if not app_data.get('ci_cd_tools'):
                analysis['gaps'].append('No CI/CD tools specified')
            if not app_data.get('deployment_frequency'):
                analysis['gaps'].append('Deployment frequency not documented')
        
        elif pillar_name == 'git_hygiene':
            analysis['relevant_fields'] = {
                'repos': app_data.get('repos', []),
                'repo_count': len(app_data.get('repos', [])),
                'git_org': app_data.get('git_org', 'Not specified'),
                'branch_protection': app_data.get('branch_protection', 'Not specified')
            }
            
            if not app_data.get('branch_protection'):
                analysis['gaps'].append('No branch protection policy mentioned')
        
        elif pillar_name == 'pipeline_maturity':
            analysis['relevant_fields'] = {
                'ci_cd_pipeline': app_data.get('ci_cd_pipeline', 'Not specified'),
                'automation_tools': app_data.get('automation_tools', 'Not specified'),
                'testing_framework': app_data.get('testing_framework', 'Not specified'),
                'deployment_automation': app_data.get('deployment_automation', 'Not specified')
            }
            
            if not app_data.get('ci_cd_pipeline'):
                analysis['gaps'].append('No CI/CD pipeline configured')
            if not app_data.get('testing_framework'):
                analysis['gaps'].append('No automated testing framework')
        
        elif pillar_name == 'compliance':
            analysis['relevant_fields'] = {
                'compliance_framework': app_data.get('compliance_framework', 'Not specified'),
                'documentation_required': app_data.get('documentation_required', 'Not specified'),
                'access_control': app_data.get('access_control', 'Not specified'),
                'audit_logging': app_data.get('audit_logging', 'Not specified')
            }
            
            if not app_data.get('compliance_framework'):
                analysis['gaps'].append('No compliance framework specified')
            if not app_data.get('audit_logging'):
                analysis['gaps'].append('No audit logging configured')
        
        elif pillar_name == 'quality_security':
            analysis['relevant_fields'] = {
                'security_scanning': app_data.get('security_scanning', 'Not specified'),
                'code_quality_tools': app_data.get('code_quality_tools', 'Not specified'),
                'secrets_management': app_data.get('secrets_management', 'Not specified'),
                'privileged_access_required': app_data.get('privileged_access_required', 'Unknown')
            }
            
            if not app_data.get('security_scanning'):
                analysis['gaps'].append('No security scanning (SAST/DAST)')
            if app_data.get('privileged_access_required') == 'yes':
                analysis['gaps'].append('Privileged access required for deployments')
        
        elif pillar_name == 'adoption':
            analysis['relevant_fields'] = {
                'copilot_enabled': app_data.get('copilot_enabled', 'Not specified'),
                'api_catalog': app_data.get('api_catalog', 'Not specified'),
                'containerization': app_data.get('containerization', 'Not specified'),
                'cloud_platform': app_data.get('cloud_platform', 'Not specified')
            }
            
            if not app_data.get('copilot_enabled'):
                analysis['gaps'].append('GitHub Copilot not enabled')
            if not app_data.get('api_catalog'):
                analysis['gaps'].append('APIs not in central catalog')
        
        return analysis
    
    def generate_analysis_summary(self, analysis: Dict) -> str:
        """Generate a human-readable summary of the analysis"""
        summary = f"# Analysis Summary for {analysis['app_name']}\n\n"
        
        for pillar_name, pillar_data in analysis['pillar_analyses'].items():
            summary += f"## {pillar_name.replace('_', ' ').title()}\n\n"
            
            if pillar_data['relevant_fields']:
                summary += "**Relevant Fields:**\n"
                for field, value in pillar_data['relevant_fields'].items():
                    summary += f"- {field}: {value}\n"
                summary += "\n"
            
            if pillar_data['gaps']:
                summary += "**Gaps Identified:**\n"
                for gap in pillar_data['gaps']:
                    summary += f"- {gap}\n"
                summary += "\n"
            
            summary += "---\n\n"
        
        return summary


def main():
    """Test the analyzer"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_app.py <path_to_yaml>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    analyzer = AppAnalyzer()
    analysis = analyzer.analyze_app(filepath)
    
    # Print summary
    summary = analyzer.generate_analysis_summary(analysis)
    print(summary)
    
    # Save full analysis to JSON
    output_file = Path(filepath).stem + "_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"\nFull analysis saved to: {output_file}")


if __name__ == "__main__":
    main()
