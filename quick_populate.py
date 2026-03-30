#!/usr/bin/env python3
"""
Quick script to populate the database with sample data for testing.
Run this if you don't have API tokens configured.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data.database import Database
import random
from datetime import datetime, timedelta

def populate_sample_data():
    """Populate database with sample team data for testing."""
    db = Database()
    
    # Sample teams
    teams = [
        ("team_001", "Team Alpha", "Cloud Native", "BU A", "Tier 1"),
        ("team_002", "Team Beta", "Hybrid", "BU A", "Tier 2"),
        ("team_003", "Team Gamma", "Legacy", "BU B", "Tier 1"),
        ("team_004", "Team Delta", "Cloud Native", "BU B", "Tier 2"),
        ("team_005", "Team Epsilon", "Hybrid", "BU C", "Tier 1"),
        ("team_006", "Team Zeta", "Cloud Native", "BU A", "Tier 3"),
        ("team_007", "Team Eta", "Legacy", "BU C", "Tier 2"),
        ("team_008", "Team Theta", "Cloud Native", "BU B", "Tier 1"),
        ("team_009", "Team Iota", "Hybrid", "BU A", "Tier 2"),
        ("team_010", "Team Kappa", "Cloud Native", "BU C", "Tier 1"),
    ]
    
    # Insert pods
    for pod_id, pod_name, stack, bu, tier in teams:
        db.upsert_pod(pod_id, pod_name, stack, bu, tier)
    
    # Generate 5 weeks of historical data
    today = datetime.now()
    weeks = []
    for i in range(5):
        week_start = today - timedelta(weeks=i)
        week_date = week_start.strftime("%Y-%m-%d")
        weeks.append(week_date)
    
    for week_date in weeks:
        for pod_id, pod_name, stack, bu, tier in teams:
            # Generate random but realistic metrics
            rf = random.randint(50, 350)
            lttd = round(random.uniform(1.0, 15.0), 1)
            cfr = round(random.uniform(0.01, 0.25), 2)
            mttr = round(random.uniform(0.5, 4.0), 1)
            
            # Generate pillar scores (0-100)
            release_velocity = round(random.uniform(40, 95), 1)
            git_hygiene = round(random.uniform(50, 98), 1)
            pipeline_maturity = round(random.uniform(45, 90), 1)
            compliance = round(random.uniform(60, 100), 1)
            quality_security = round(random.uniform(55, 95), 1)
            adoption = round(random.uniform(30, 85), 1)
            
            # Calculate DPI (weighted average)
            dpi = round(
                release_velocity * 0.30 +
                git_hygiene * 0.20 +
                pipeline_maturity * 0.20 +
                compliance * 0.15 +
                quality_security * 0.10 +
                adoption * 0.05,
                1
            )
            
            db.insert_weekly_metrics({
                'pod_id': pod_id,
                'week_date': week_date,
                'mttr': mttr,
                'lttd': lttd,
                'rf': rf,
                'cfr': cfr,
                'git_hygiene_score': git_hygiene,
                'Release_Velocity_Score': release_velocity,
                'Git_Hygiene_Score': git_hygiene,
                'Pipeline_Maturity_Score': pipeline_maturity,
                'Compliance_Score': compliance,
                'Quality_Security_Score': quality_security,
                'Adoption_Score': adoption,
                'dpi': dpi
            })
    
    print(f"✅ Populated database with {len(teams)} teams and {len(weeks)} weeks of data")
    
    # Show stats
    stats = db.get_statistics()
    print(f"   Total pods: {stats['total_pods']}")
    print(f"   Total metrics records: {stats['total_metrics_records']}")
    print(f"   Date range: {stats['earliest_week']} to {stats['latest_week']}")
    print(f"   Average DPI: {stats['average_dpi']}")

if __name__ == "__main__":
    populate_sample_data()
