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
        # Check latest metrics
        latest_query = """
        SELECT 
            p.pod_name as Team,
            wm.week_date,
            wm.rf as RF,
            wm.lttd as LTTD,
            wm.ltdd_measurable as LTDD_Measurable,
            wm.cfr as CFR,
            wm.mttr as MTTR,
            wm.dpi as DPI,
            wm.rf_score as RF_Score,
            wm.flow_score as Flow_Score,
            wm.cfr_score as CFR_Score,
            wm.stability_score as Stability_Score
        FROM weekly_metrics wm
        JOIN pods p ON wm.pod_id = p.pod_id
        WHERE wm.week_date = (SELECT MAX(week_date) FROM weekly_metrics)
        LIMIT 5
        """
        latest_df = pd.read_sql_query(latest_query, conn)
        print("\nLatest metrics (sample 5 teams):")
        print(latest_df.to_string())
        
        # Check for NULL values
        print("\n" + "-" * 80)
        print("3. NULL VALUE CHECK")
        print("-" * 80)
        null_check_query = """
        SELECT 
            COUNT(*) as total_records,
            SUM(CASE WHEN rf IS NULL THEN 1 ELSE 0 END) as rf_nulls,
            SUM(CASE WHEN lttd IS NULL THEN 1 ELSE 0 END) as lttd_nulls,
            SUM(CASE WHEN cfr IS NULL THEN 1 ELSE 0 END) as cfr_nulls,
            SUM(CASE WHEN mttr IS NULL THEN 1 ELSE 0 END) as mttr_nulls,
            SUM(CASE WHEN dpi IS NULL THEN 1 ELSE 0 END) as dpi_nulls,
            SUM(CASE WHEN rf_score IS NULL THEN 1 ELSE 0 END) as rf_score_nulls
        FROM weekly_metrics
        WHERE week_date = (SELECT MAX(week_date) FROM weekly_metrics)
        """
        null_df = pd.read_sql_query(null_check_query, conn)
        print(null_df.to_string())
        
        # Check data types and ranges
        print("\n" + "-" * 80)
        print("4. DATA RANGES (Latest Week)")
        print("-" * 80)
        range_query = """
        SELECT 
            MIN(rf) as min_rf, MAX(rf) as max_rf, AVG(rf) as avg_rf,
            MIN(lttd) as min_lttd, MAX(lttd) as max_lttd, AVG(lttd) as avg_lttd,
            MIN(cfr) as min_cfr, MAX(cfr) as max_cfr, AVG(cfr) as avg_cfr,
            MIN(mttr) as min_mttr, MAX(mttr) as max_mttr, AVG(mttr) as avg_mttr,
            MIN(dpi) as min_dpi, MAX(dpi) as max_dpi, AVG(dpi) as avg_dpi
        FROM weekly_metrics
        WHERE week_date = (SELECT MAX(week_date) FROM weekly_metrics)
        """
        range_df = pd.read_sql_query(range_query, conn)
        print(range_df.to_string())
        
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
