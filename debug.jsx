#!/usr/bin/env python3
"""
Debug script to check database contents and DataSight data
"""
import sqlite3
import pandas as pd
from database import MetricsDatabase
import config

def check_database():
    """Check what's in the database"""
    db = MetricsDatabase()
    
    print("=" * 80)
    print("DATABASE DIAGNOSTICS")
    print("=" * 80)
    
    # Check if database file exists
    import os
    if not os.path.exists(db.db_path):
        print(f"❌ Database file does not exist: {db.db_path}")
        return
    
    print(f"✅ Database file exists: {db.db_path}\n")
    
    conn = sqlite3.connect(db.db_path)
    
    # 1. Check pods table
    print("-" * 80)
    print("1. PODS TABLE")
    print("-" * 80)
    pods_df = pd.read_sql_query("SELECT * FROM pods", conn)
    print(f"Total pods: {len(pods_df)}")
    if not pods_df.empty:
        print("\nSample pods:")
        print(pods_df[['pod_id', 'pod_name', 'tier']].head())
    else:
        print("⚠️ No pods found in database!")
    
    # 2. Check weekly_metrics table
    print("\n" + "-" * 80)
    print("2. WEEKLY METRICS TABLE")
    print("-" * 80)
    
    metrics_count = pd.read_sql_query("SELECT COUNT(*) as count FROM weekly_metrics", conn).iloc[0]['count']
    print(f"Total metric records: {metrics_count}")
    
    if metrics_count > 0:
        # Check latest metrics with NEW 6-PILLAR SYSTEM
        latest_query = """
        SELECT 
            p.pod_name as Team,
            wm.week_date,
            wm.rf as RF,
            wm.lttd as LTTD,
            wm.cfr as CFR,
            wm.mttr as MTTR,
            wm.dpi as DPI,
            wm.release_velocity_score as RV_Score,
            wm.git_hygiene_score as GH_Score,
            wm.pipeline_maturity_score as PM_Score,
            wm.compliance_score as Comp_Score,
            wm.quality_security_score as QS_Score,
            wm.adoption_score as Adopt_Score
        FROM weekly_metrics wm
        JOIN pods p ON wm.pod_id = p.pod_id
        WHERE wm.week_date = (SELECT MAX(week_date) FROM weekly_metrics)
        LIMIT 5
        """
        latest_df = pd.read_sql_query(latest_query, conn)
        print("\nLatest metrics (sample 5 teams) - NEW 6-PILLAR SYSTEM:")
        print(latest_df.to_string())
        
        # Show weighted contributions
        print("\n" + "-" * 80)
        print("2b. WEIGHTED PILLAR CONTRIBUTIONS (Latest Week)")
        print("-" * 80)
        weighted_query = """
        SELECT 
            p.pod_name as Team,
            wm.release_velocity_weighted as RV_30pct,
            wm.git_hygiene_weighted as GH_20pct,
            wm.pipeline_maturity_weighted as PM_20pct,
            wm.compliance_weighted as Comp_15pct,
            wm.quality_security_weighted as QS_10pct,
            wm.adoption_weighted as Adopt_5pct,
            wm.dpi as Total_DPI
        FROM weekly_metrics wm
        JOIN pods p ON wm.pod_id = p.pod_id
        WHERE wm.week_date = (SELECT MAX(week_date) FROM weekly_metrics)
        LIMIT 5
        """
        weighted_df = pd.read_sql_query(weighted_query, conn)
        print(weighted_df.to_string())
        
        # Show new metrics
        print("\n" + "-" * 80)
        print("2c. NEW METRICS & FLAGS (Latest Week)")
        print("-" * 80)
        flags_query = """
        SELECT 
            p.pod_name as Team,
            wm.pipeline_standard as Pipeline,
            wm.feature_flags_adopted as FF,
            wm.has_release_page as Release_Page,
            wm.has_compliance_evidence as Compliance,
            wm.apis_published as APIs,
            wm.copilot_enabled as Copilot,
            wm.git_hygiene_violations_critical as Crit_Viol,
            wm.git_hygiene_violations_warnings as Warn_Viol
        FROM weekly_metrics wm
        JOIN pods p ON wm.pod_id = p.pod_id
        WHERE wm.week_date = (SELECT MAX(week_date) FROM weekly_metrics)
        LIMIT 5
        """
        flags_df = pd.read_sql_query(flags_query, conn)
        print(flags_df.to_string())
        
        # Check for NULL values in NEW 6-PILLAR COLUMNS
        print("\n" + "-" * 80)
        print("3. NULL VALUE CHECK (6-Pillar System)")
        print("-" * 80)
        null_check_query = """
        SELECT 
            COUNT(*) as total_records,
            SUM(CASE WHEN rf IS NULL THEN 1 ELSE 0 END) as rf_nulls,
            SUM(CASE WHEN lttd IS NULL THEN 1 ELSE 0 END) as lttd_nulls,
            SUM(CASE WHEN dpi IS NULL THEN 1 ELSE 0 END) as dpi_nulls,
            SUM(CASE WHEN release_velocity_score IS NULL THEN 1 ELSE 0 END) as rv_score_nulls,
            SUM(CASE WHEN git_hygiene_score IS NULL THEN 1 ELSE 0 END) as gh_score_nulls,
            SUM(CASE WHEN pipeline_maturity_score IS NULL THEN 1 ELSE 0 END) as pm_score_nulls,
            SUM(CASE WHEN compliance_score IS NULL THEN 1 ELSE 0 END) as comp_score_nulls,
            SUM(CASE WHEN quality_security_score IS NULL THEN 1 ELSE 0 END) as qs_score_nulls,
            SUM(CASE WHEN adoption_score IS NULL THEN 1 ELSE 0 END) as adopt_score_nulls
        FROM weekly_metrics
        WHERE week_date = (SELECT MAX(week_date) FROM weekly_metrics)
        """
        null_df = pd.read_sql_query(null_check_query, conn)
        print(null_df.to_string())
        
        # Check data types and ranges for NEW 6-PILLAR SCORES
        print("\n" + "-" * 80)
        print("4. PILLAR SCORE RANGES (Latest Week, 0-100 scale)")
        print("-" * 80)
        range_query = """
        SELECT 
            MIN(release_velocity_score) as min_rv, MAX(release_velocity_score) as max_rv, AVG(release_velocity_score) as avg_rv,
            MIN(git_hygiene_score) as min_gh, MAX(git_hygiene_score) as max_gh, AVG(git_hygiene_score) as avg_gh,
            MIN(pipeline_maturity_score) as min_pm, MAX(pipeline_maturity_score) as max_pm, AVG(pipeline_maturity_score) as avg_pm,
            MIN(compliance_score) as min_comp, MAX(compliance_score) as max_comp, AVG(compliance_score) as avg_comp,
            MIN(quality_security_score) as min_qs, MAX(quality_security_score) as max_qs, AVG(quality_security_score) as avg_qs,
            MIN(adoption_score) as min_adopt, MAX(adoption_score) as max_adopt, AVG(adoption_score) as avg_adopt
        FROM weekly_metrics
        WHERE week_date = (SELECT MAX(week_date) FROM weekly_metrics)
        """
        range_df = pd.read_sql_query(range_query, conn)
        print(range_df.to_string())
        
        # Check DPI ranges
        print("\n" + "-" * 80)
        print("4b. DPI RANGES (Latest Week)")
        print("-" * 80)
        dpi_query = """
        SELECT 
            MIN(dpi) as min_dpi, 
            MAX(dpi) as max_dpi, 
            AVG(dpi) as avg_dpi,
            COUNT(*) as total_teams
        FROM weekly_metrics
        WHERE week_date = (SELECT MAX(week_date) FROM weekly_metrics)
        """
        dpi_df = pd.read_sql_query(dpi_query, conn)
        print(dpi_df.to_string())
        
        # Check weeks available
        print("\n" + "-" * 80)
        print("5. AVAILABLE WEEKS")
        print("-" * 80)
        weeks_query = "SELECT DISTINCT week_date FROM weekly_metrics ORDER BY week_date DESC"
        weeks_df = pd.read_sql_query(weeks_query, conn)
        print(f"Total weeks: {len(weeks_df)}")
        print(weeks_df.to_string())
        
    else:
        print("⚠️ No metrics found in database!")
        print("\nPossible issues:")
        print("1. Bearer tokens not configured in .env")
        print("2. API requests failing")
        print("3. setup_database.py not run with data fetch")
    
    conn.close()
    
    # 3. Check configuration
    print("\n" + "=" * 80)
    print("6. CONFIGURATION CHECK")
    print("=" * 80)
    print(f"TeamBook token configured: {bool(config.TEAMBOOK_BEARER_TOKEN)}")
    print(f"DataSight token configured: {bool(config.DATASIGHT_BEARER_TOKEN)}")
    print(f"Database path: {config.DB_PATH}")
    print(f"Max weeks to keep: {config.MAX_WEEKS_TO_KEEP}")
    print(f"Service line ID: {config.SERVICE_LINE_ID}")
    
    print("\n" + "=" * 80)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    check_database()
