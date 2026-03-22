"""
Database inspection script
Shows all tables, columns, and sample data
"""

import sqlite3
import pandas as pd
import os

# Get database path
db_path = os.path.join(os.path.dirname(__file__), 'metrics.db')

print(f"📊 Inspecting database: {db_path}")
print("=" * 80)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print(f"\n📋 Found {len(tables)} tables:\n")

for (table_name,) in tables:
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name}")
    print('='*80)
    
    # Get column info
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    
    print("\nColumns:")
    for col in columns:
        col_id, name, type_, notnull, default, pk = col
        pk_marker = " [PRIMARY KEY]" if pk else ""
        null_marker = " NOT NULL" if notnull else ""
        print(f"  - {name}: {type_}{pk_marker}{null_marker}")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    print(f"\nTotal rows: {count}")
    
    # Show sample data
    if count > 0:
        print(f"\nSample data (first 3 rows):")
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 3", conn)
        print(df.to_string())
        
        # For weekly_metrics, show all teams
        if table_name == 'weekly_metrics':
            print(f"\n\nAll teams in weekly_metrics:")
            cursor.execute("""
                SELECT DISTINCT p.pod_name, COUNT(*) as weeks
                FROM weekly_metrics wm
                JOIN pods p ON wm.pod_id = p.pod_id
                GROUP BY p.pod_name
            """)
            teams = cursor.fetchall()
            for team, weeks in teams:
                print(f"  - {team}: {weeks} week(s) of data")
            
            # Show pillar scores
            print(f"\n\nPillar scores for all teams (latest week):")
            df_pillars = pd.read_sql_query("""
                SELECT 
                    p.pod_name as Team,
                    wm.dpi as DPI,
                    wm.velocity as Velocity,
                    wm.flow as Flow,
                    wm.stability as Stability,
                    wm.automation as Automation,
                    wm.quality_security as Quality_Security,
                    wm.ai_adoption as AI_Adoption
                FROM weekly_metrics wm
                JOIN pods p ON wm.pod_id = p.pod_id
                WHERE wm.id IN (
                    SELECT wm2.id
                    FROM weekly_metrics wm2
                    WHERE wm2.pod_id = wm.pod_id
                    ORDER BY date(wm2.week_date) DESC
                    LIMIT 1
                )
                ORDER BY wm.dpi DESC
            """, conn)
            print(df_pillars.to_string())

conn.close()

print("\n" + "="*80)
print("✅ Database inspection complete!")
print("="*80)
