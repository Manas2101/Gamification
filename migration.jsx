#!/usr/bin/env python3
"""
Database Migration: Add 6-Pillar Scoring Columns

This script:
1. Backs up the current database
2. Adds new columns for 6-pillar scoring
3. Migrates existing data to new schema
4. Keeps old columns for comparison (will remove after validation)

Run: python migrate_to_6_pillars.py
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "metrics.db"
BACKUP_SUFFIX = datetime.now().strftime("%Y%m%d_%H%M%S")

def backup_database():
    """Create a backup of the database before migration"""
    if not Path(DB_PATH).exists():
        logger.error(f"Database {DB_PATH} not found!")
        return False
    
    backup_path = f"{DB_PATH}.backup_{BACKUP_SUFFIX}"
    shutil.copy2(DB_PATH, backup_path)
    logger.info(f"✅ Database backed up to: {backup_path}")
    return True

def add_new_columns(conn):
    """Add new columns for 6-pillar scoring"""
    cursor = conn.cursor()
    
    new_columns = [
        # New pillar raw scores (0-100)
        ("release_velocity_score", "REAL"),
        ("git_hygiene_score", "REAL"),
        ("pipeline_maturity_score", "REAL"),
        ("compliance_score", "REAL"),
        ("quality_security_score", "REAL"),
        ("adoption_score", "REAL"),
        
        # Weighted contributions (for transparency)
        ("release_velocity_weighted", "REAL"),
        ("git_hygiene_weighted", "REAL"),
        ("pipeline_maturity_weighted", "REAL"),
        ("compliance_weighted", "REAL"),
        ("quality_security_weighted", "REAL"),
        ("adoption_weighted", "REAL"),
        
        # New metrics for scoring
        ("pipeline_standard", "TEXT"),
        ("feature_flags_adopted", "BOOLEAN DEFAULT 0"),
        ("has_release_page", "BOOLEAN DEFAULT 0"),
        ("has_compliance_evidence", "BOOLEAN DEFAULT 0"),
        ("priv_access_reviewed_date", "TEXT"),
        ("apis_published", "BOOLEAN DEFAULT 0"),
        ("ai_tools_declared", "TEXT"),
        ("copilot_enabled", "BOOLEAN DEFAULT 0"),
        ("sonarqube_project", "TEXT"),
        
        # Git hygiene metrics (from hygiene_checker.py)
        ("git_hygiene_violations_critical", "INTEGER DEFAULT 0"),
        ("git_hygiene_violations_warnings", "INTEGER DEFAULT 0"),
    ]
    
    logger.info("Adding new columns...")
    for col_name, col_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE weekly_metrics ADD COLUMN {col_name} {col_type}")
            logger.info(f"  ✅ Added: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                logger.info(f"  ⏭️  Column {col_name} already exists, skipping")
            else:
                logger.error(f"  ❌ Error adding {col_name}: {e}")
    
    conn.commit()
    logger.info("✅ New columns added successfully")

def migrate_existing_data(conn):
    """Migrate existing data to new pillar structure"""
    cursor = conn.cursor()
    
    logger.info("Migrating existing data to new pillar structure...")
    
    # Migrate old pillar scores to new structure (temporary mapping)
    # This gives us a baseline until we run the new scoring logic
    cursor.execute("""
        UPDATE weekly_metrics
        SET 
            release_velocity_score = COALESCE(velocity, 0),
            pipeline_maturity_score = COALESCE(automation, 0),
            compliance_score = COALESCE(stability * 0.5, 0),
            quality_security_score = COALESCE(quality_security, 50),
            adoption_score = COALESCE(ai_adoption, 0),
            git_hygiene_score = 50.0
        WHERE release_velocity_score IS NULL
    """)
    
    # Calculate weighted scores (temporary)
    cursor.execute("""
        UPDATE weekly_metrics
        SET 
            release_velocity_weighted = release_velocity_score * 0.30,
            git_hygiene_weighted = git_hygiene_score * 0.20,
            pipeline_maturity_weighted = pipeline_maturity_score * 0.20,
            compliance_weighted = compliance_score * 0.15,
            quality_security_weighted = quality_security_score * 0.10,
            adoption_weighted = adoption_score * 0.05
        WHERE release_velocity_weighted IS NULL
    """)
    
    # Migrate existing boolean flags
    cursor.execute("""
        UPDATE weekly_metrics
        SET 
            feature_flags_adopted = 0,
            has_release_page = 0,
            has_compliance_evidence = 0,
            apis_published = 0,
            copilot_enabled = 0
        WHERE feature_flags_adopted IS NULL
    """)
    
    conn.commit()
    rows_updated = cursor.rowcount
    logger.info(f"✅ Migrated {rows_updated} rows to new pillar structure")

def verify_migration(conn):
    """Verify the migration was successful"""
    cursor = conn.cursor()
    
    logger.info("Verifying migration...")
    
    # Check if new columns exist
    cursor.execute("PRAGMA table_info(weekly_metrics)")
    columns = [row[1] for row in cursor.fetchall()]
    
    required_columns = [
        "release_velocity_score",
        "git_hygiene_score",
        "pipeline_maturity_score",
        "compliance_score",
        "quality_security_score",
        "adoption_score",
    ]
    
    missing = [col for col in required_columns if col not in columns]
    if missing:
        logger.error(f"❌ Missing columns: {missing}")
        return False
    
    # Check if data was migrated
    cursor.execute("""
        SELECT COUNT(*) 
        FROM weekly_metrics 
        WHERE release_velocity_score IS NOT NULL
    """)
    migrated_count = cursor.fetchone()[0]
    
    logger.info(f"✅ Verification complete: {migrated_count} rows have new pillar scores")
    return True

def cleanup_old_columns(conn):
    """
    Remove deprecated columns after migration is verified
    
    WARNING: This is irreversible! Make sure you have a backup.
    """
    logger.info("=" * 60)
    logger.info("CLEANUP: Removing deprecated columns")
    logger.info("=" * 60)
    
    # Columns to remove
    deprecated_columns = [
        # Old individual scores (replaced by new pillar system)
        'rf_score',
        'flow_score',
        'cfr_score',
        'mttr_score',
        'priv_score',
        'automation_score',
        'stability_score',
        # Old pillar scores (replaced by new weighted system)
        'velocity',
        'flow',
        'stability',
        'automation',
        'quality_security',
        'ai_adoption',
        # Old flags (no longer needed)
        'cfr_reported',
        'automation_audited',
        'critical_data_present',
    ]
    
    logger.info(f"Columns to remove: {len(deprecated_columns)}")
    
    # SQLite doesn't support DROP COLUMN directly in older versions
    # We need to recreate the table without those columns
    cursor = conn.cursor()
    
    try:
        # Get current table schema
        cursor.execute("PRAGMA table_info(weekly_metrics)")
        all_columns = cursor.fetchall()
        
        # Filter out deprecated columns
        keep_columns = [
            col[1] for col in all_columns 
            if col[1] not in deprecated_columns
        ]
        
        logger.info(f"Keeping {len(keep_columns)} columns")
        
        # Create new table with only kept columns
        columns_str = ', '.join(keep_columns)
        
        cursor.execute(f'''
            CREATE TABLE weekly_metrics_new AS
            SELECT {columns_str}
            FROM weekly_metrics
        ''')
        
        # Drop old table
        cursor.execute('DROP TABLE weekly_metrics')
        
        # Rename new table
        cursor.execute('ALTER TABLE weekly_metrics_new RENAME TO weekly_metrics')
        
        # Recreate unique constraint
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_pod_week 
            ON weekly_metrics(pod_id, week_date)
        ''')
        
        conn.commit()
        
        logger.info("✅ Cleanup complete!")
        logger.info(f"Removed {len(deprecated_columns)} deprecated columns")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        conn.rollback()
        return False


def main():
    import sys
    
    logger.info("=" * 60)
    logger.info("DATABASE MIGRATION: 6-Pillar Scoring System")
    logger.info("=" * 60)
    
    # Check if cleanup mode
    cleanup_mode = '--cleanup' in sys.argv
    
    if cleanup_mode:
        logger.warning("⚠️  CLEANUP MODE: This will remove old columns!")
        logger.warning("⚠️  Make sure you have tested the new system first!")
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Cleanup cancelled.")
            return
    
    # Step 1: Backup
    if not backup_database():
        logger.error("Backup failed. Aborting.")
        return
    
    # Step 2: Connect to database
    conn = sqlite3.connect(DB_PATH)
    
    try:
        if cleanup_mode:
            # Run cleanup only
            if cleanup_old_columns(conn):
                logger.info("=" * 60)
                logger.info("✅ CLEANUP COMPLETE!")
                logger.info("=" * 60)
        else:
            # Run migration
            # Step 3: Add new columns
            add_new_columns(conn)
            
            # Step 4: Migrate existing data
            migrate_existing_data(conn)
            
            # Step 5: Verify
            if verify_migration(conn):
                logger.info("=" * 60)
                logger.info("✅ MIGRATION COMPLETE!")
                logger.info("=" * 60)
                logger.info("Next steps:")
                logger.info("1. Run weekly_refresh.py to populate new pillar scores")
                logger.info("2. Compare old DPI vs new DPI in dashboard")
                logger.info("3. After validation, run: python migrate_to_6_pillars.py --cleanup")
            else:
                logger.error("❌ Migration verification failed!")
    
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        conn.rollback()
    
    finally:
        conn.close()


if __name__ == "__main__":
    main()
