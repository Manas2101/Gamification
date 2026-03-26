#!/usr/bin/env python3
"""
Main Workflow Runner - Orchestrates the entire agentic recommendation workflow

Steps:
1. Detect changes in apps folder
2. Analyze changed apps against 6 pillar skills
3. Generate recommendation prompts
4. Trigger Windsurf automation (optional)
5. Store recommendations
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from detect_app_changes import AppChangeDetector
from analyze_app import AppAnalyzer
from generate_prompt import PromptGenerator

class WorkflowRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.workflow_dir = self.project_root / "workflow"
        self.recommendations_dir = self.workflow_dir / "recommendations"
        self.recommendations_dir.mkdir(exist_ok=True)
        
        self.detector = AppChangeDetector()
        self.analyzer = AppAnalyzer()
        self.prompt_generator = PromptGenerator()
    
    def run(self, auto_windsurf: bool = False):
        """Run the complete workflow"""
        print("="*60)
        print("🚀 AGENTIC RECOMMENDATION WORKFLOW")
        print("="*60)
        print()
        
        # Step 1: Detect changes
        print("📋 Step 1: Detecting changes in apps folder...")
        changes = self.detector.get_changed_files()
        
        if not changes:
            print("✓ No changes detected. Workflow complete.")
            return
        
        print(f"✓ Found {len(changes)} changed file(s):")
        for change in changes:
            print(f"  - {change['path']} ({change['type']})")
        print()
        
        # Step 2: Analyze each changed app
        print("🔍 Step 2: Analyzing changed apps against 6 pillar skills...")
        analyses = []
        
        for change in changes:
            if change['type'] == 'deleted':
                print(f"  ⊘ Skipping deleted file: {change['path']}")
                continue
            
            print(f"  → Analyzing: {change['app_name']}")
            
            try:
                analysis = self.analyzer.analyze_app(change['path'])
                analyses.append({
                    'change': change,
                    'analysis': analysis
                })
                
                # Save analysis
                analysis_file = self.recommendations_dir / f"{change['app_name']}_analysis.json"
                with open(analysis_file, 'w') as f:
                    json.dump(analysis, f, indent=2, default=str)
                
                print(f"    ✓ Analysis saved to: {analysis_file.name}")
                
            except Exception as e:
                print(f"    ✗ Error analyzing {change['path']}: {e}")
                continue
        
        print()
        
        # Step 3: Generate prompts
        print("💡 Step 3: Generating recommendation prompts...")
        
        for item in analyses:
            app_name = item['change']['app_name']
            analysis = item['analysis']
            
            print(f"  → Generating prompt for: {app_name}")
            
            try:
                prompt = self.prompt_generator.generate_recommendation_prompt(
                    item['change']['path'],
                    analysis
                )
                
                # Save prompt
                prompt_file = self.recommendations_dir / f"{app_name}_prompt.txt"
                with open(prompt_file, 'w') as f:
                    f.write(prompt)
                
                print(f"    ✓ Prompt saved to: {prompt_file.name}")
                
                # Store prompt path for later use
                item['prompt_file'] = str(prompt_file)
                
            except Exception as e:
                print(f"    ✗ Error generating prompt for {app_name}: {e}")
                continue
        
        print()
        
        # Step 4: Windsurf automation (optional)
        if auto_windsurf and analyses:
            print("🤖 Step 4: Triggering Windsurf automation...")
            self._trigger_windsurf_automation(analyses)
        else:
            print("⏭️  Step 4: Skipping Windsurf automation (use --auto flag to enable)")
            print()
            print("📝 Manual steps:")
            for item in analyses:
                if 'prompt_file' in item:
                    app_name = item['change']['app_name']
                    print(f"\n  For {app_name}:")
                    print(f"  1. Run: ./workflow/automate_windsurf.sh {item['prompt_file']} {app_name}")
                    print(f"  2. Or manually paste prompt from: {item['prompt_file']}")
        
        print()
        
        # Step 5: Summary
        print("="*60)
        print("📊 WORKFLOW SUMMARY")
        print("="*60)
        print(f"Changed files: {len(changes)}")
        print(f"Analyzed apps: {len(analyses)}")
        print(f"Prompts generated: {len([a for a in analyses if 'prompt_file' in a])}")
        print()
        print(f"📁 Recommendations directory: {self.recommendations_dir}")
        print()
        print("✅ Workflow complete!")
        print()
    
    def _trigger_windsurf_automation(self, analyses: List[Dict]):
        """Trigger Windsurf automation for each app"""
        for item in analyses:
            if 'prompt_file' not in item:
                continue
            
            app_name = item['change']['app_name']
            prompt_file = item['prompt_file']
            
            print(f"  → Triggering Windsurf for: {app_name}")
            
            try:
                # Make script executable
                script_path = self.workflow_dir / "automate_windsurf.sh"
                script_path.chmod(0o755)
                
                # Run automation script
                result = subprocess.run(
                    [str(script_path), prompt_file, app_name],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"    ✓ Windsurf automation triggered")
                else:
                    print(f"    ✗ Error: {result.stderr}")
                
                # Wait between apps to avoid overwhelming
                import time
                time.sleep(5)
                
            except Exception as e:
                print(f"    ✗ Error triggering Windsurf: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run agentic recommendation workflow"
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Automatically trigger Windsurf automation'
    )
    
    args = parser.parse_args()
    
    runner = WorkflowRunner()
    runner.run(auto_windsurf=args.auto)


if __name__ == "__main__":
    main()
