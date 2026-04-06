"""
Database Module
===============

SQLite database operations for storing and retrieving pod metrics.

Provides persistent storage with historical tracking for:
    - Pod information and metadata
    - Weekly metrics snapshots
    - Historical trends and comparisons

Example:
    >>> from src.data.database import Database
    >>> db = Database("metrics.db")
    >>> db.upsert_pod(pod_id="123", pod_name="MyPod", ...)

Author: DevOps Transformation Team
"""

import sqlite3
import os
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

# Configure module logger
logger = logging.getLogger(__name__)


class Database:
    """
    SQLite database handler for metrics storage.
    
    Manages all database operations including table creation,
    data insertion, updates, and queries.
    
    Attributes:
        db_path (str): Path to SQLite database file
        
    Example:
        >>> db = Database("metrics.db")
        >>> db.upsert_pod("123", "MyPod", "Java", "BU1", "Tier 1")
        >>> df = db.get_latest_metrics()
    """
    
    def __init__(self, db_path: str = "metrics.db"):
        """
        Initialize database connection and create tables.
        
        Args:
            db_path: Path to SQLite database file.
                    Will be created if it doesn't exist.
        
        Raises:
            PermissionError: If directory is not writable.
        """
        # Convert to absolute path
        self.db_path = os.path.abspath(db_path)
        logger.info(f"Database path: {self.db_path}")
        
        # Ensure parent directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            logger.info(f"Creating database directory: {db_dir}")
            os.makedirs(db_dir, exist_ok=True)
        
        # Check write permissions
        if db_dir and not os.access(db_dir, os.W_OK):
            raise PermissionError(f"No write permission for: {db_dir}")
        
        # Handle case where db_path is accidentally a directory
        if os.path.isdir(self.db_path):
            logger.warning(f"Removing directory at db path: {self.db_path}")
            shutil.rmtree(self.db_path)
        
        # Initialize database tables
        self._init_tables()
        logger.info("Database initialized successfully")
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get database connection.
        
        Returns:
            SQLite connection object.
        """
        return sqlite3.connect(self.db_path)
    
    def _init_tables(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Pods table - stores pod metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pods (
                pod_id TEXT PRIMARY KEY,
                pod_name TEXT NOT NULL,
                stack TEXT,
                business_unit TEXT,
                tier TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Weekly metrics table - stores weekly snapshots
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pod_id TEXT NOT NULL,
                week_date DATE NOT NULL,
                week_start DATE,
                
                -- Raw metrics
                mttr REAL,
                lttd REAL,
                rf INTEGER,
                cfr REAL,
                
                -- Git hygiene
                git_hygiene_score REAL,
                git_hygiene_violations_critical INTEGER DEFAULT 0,
                git_hygiene_violations_warnings INTEGER DEFAULT 0,
                
                -- Pillar scores
                release_velocity_score REAL,
                git_hygiene_pillar_score REAL,
                pipeline_maturity_score REAL,
                compliance_score REAL,
                quality_security_score REAL,
                adoption_score REAL,
                
                -- Overall DPI
                dpi REAL,
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (pod_id) REFERENCES pods(pod_id),
                UNIQUE(pod_id, week_date)
            )
        ''')
        
        # Create indexes for common queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_weekly_metrics_pod_date 
            ON weekly_metrics(pod_id, week_date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_weekly_metrics_week 
            ON weekly_metrics(week_date)
        ''')
        
        conn.commit()
        conn.close()
    
    def upsert_pod(
        self,
        pod_id: str,
        pod_name: str,
        stack: str = None,
        business_unit: str = None,
        tier: str = None
    ):
        """
        Insert or update pod information.
        
        Args:
            pod_id: Unique pod identifier.
            pod_name: Display name for the pod.
            stack: Technology stack (e.g., "Java", "Python").
            business_unit: Business unit name.
            tier: Service tier (e.g., "Tier 1", "Tier 2").
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pods (pod_id, pod_name, stack, business_unit, tier, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(pod_id) DO UPDATE SET
                pod_name = excluded.pod_name,
                stack = excluded.stack,
                business_unit = excluded.business_unit,
                tier = excluded.tier,
                updated_at = CURRENT_TIMESTAMP
        ''', (pod_id, pod_name, stack, business_unit, tier))
        
        conn.commit()
        conn.close()
        logger.debug(f"Upserted pod: {pod_name} ({pod_id})")
    
    def insert_weekly_metrics(self, metrics: Dict):
        """
        Insert weekly metrics snapshot.
        
        Args:
            metrics: Dictionary containing all metric values.
                    Required keys: pod_id, week_date
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Extract values with defaults
        pod_id = metrics.get('pod_id')
        week_date = metrics.get('week_date')
        
        if not pod_id or not week_date:
            logger.error("Missing required fields: pod_id or week_date")
            conn.close()
            return
        
        # Format week_date if it's a datetime object
        if isinstance(week_date, datetime):
            week_date = week_date.strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT OR REPLACE INTO weekly_metrics (
                pod_id, week_date, week_start,
                mttr, lttd, rf, cfr,
                git_hygiene_score, git_hygiene_violations_critical, 
                git_hygiene_violations_warnings,
                release_velocity_score, git_hygiene_pillar_score,
                pipeline_maturity_score, compliance_score,
                quality_security_score, adoption_score, dpi
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pod_id,
            week_date,
            metrics.get('week_start'),
            metrics.get('mttr'),
            metrics.get('lttd'),
            metrics.get('rf'),
            metrics.get('cfr'),
            metrics.get('git_hygiene_score'),
            metrics.get('git_hygiene_violations_critical', 0),
            metrics.get('git_hygiene_violations_warnings', 0),
            metrics.get('Release_Velocity_Score'),
            metrics.get('Git_Hygiene_Score'),
            metrics.get('Pipeline_Maturity_Score'),
            metrics.get('Compliance_Score'),
            metrics.get('Quality_Security_Score'),
            metrics.get('Adoption_Score'),
            metrics.get('dpi')
        ))
        
        conn.commit()
        conn.close()
        logger.debug(f"Inserted metrics for pod {pod_id}, week {week_date}")
    
    def get_latest_metrics(self) -> pd.DataFrame:
        """
        Get latest metrics for all pods.
        
        Returns:
            DataFrame with latest metrics per pod.
        """
        conn = self._get_connection()
        
        query = '''
            SELECT 
                p.pod_id,
                p.pod_name AS Team,
                p.stack AS Stack,
                p.business_unit AS "Business Unit",
                p.tier AS Tier,
                m.week_date AS Week,
                m.mttr AS MTTR,
                m.lttd AS LTTD,
                m.rf AS RF,
                m.cfr AS CFR,
                m.git_hygiene_score,
                m.release_velocity_score AS Release_Velocity_Score,
                m.git_hygiene_pillar_score AS Git_Hygiene_Score,
                m.pipeline_maturity_score AS Pipeline_Maturity_Score,
                m.compliance_score AS Compliance_Score,
                m.quality_security_score AS Quality_Security_Score,
                m.adoption_score AS Adoption_Score,
                m.dpi AS DPI
            FROM pods p
            JOIN weekly_metrics m ON p.pod_id = m.pod_id
            WHERE m.week_date = (
                SELECT MAX(week_date) FROM weekly_metrics
            )
            ORDER BY m.dpi DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        logger.debug(f"Retrieved latest metrics for {len(df)} pods")
        return df
    
    def get_pod_history(
        self, 
        pod_id: str, 
        weeks: int = 12
    ) -> pd.DataFrame:
        """
        Get historical metrics for a specific pod.
        
        Args:
            pod_id: Pod identifier.
            weeks: Number of weeks of history to retrieve.
            
        Returns:
            DataFrame with historical metrics.
        """
        conn = self._get_connection()
        
        query = '''
            SELECT 
                week_date,
                mttr, lttd, rf, cfr,
                git_hygiene_score,
                release_velocity_score AS Release_Velocity_Score,
                git_hygiene_pillar_score AS Git_Hygiene_Score,
                pipeline_maturity_score AS Pipeline_Maturity_Score,
                compliance_score AS Compliance_Score,
                quality_security_score AS Quality_Security_Score,
                adoption_score AS Adoption_Score,
                dpi
            FROM weekly_metrics
            WHERE pod_id = ?
            ORDER BY week_date DESC
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(pod_id, weeks))
        conn.close()
        
        return df
    
    def get_all_pods(self) -> pd.DataFrame:
        """
        Get all pod information.
        
        Returns:
            DataFrame with pod metadata.
        """
        conn = self._get_connection()
        df = pd.read_sql_query("SELECT * FROM pods", conn)
        conn.close()
        return df
    
    def get_leaderboard(self, week_date: str = None) -> pd.DataFrame:
        """
        Get leaderboard rankings for a specific week.
        
        Args:
            week_date: Week date string (YYYY-MM-DD). 
                      Defaults to latest week.
            
        Returns:
            DataFrame with ranked pods.
        """
        conn = self._get_connection()
        
        if week_date:
            date_filter = f"WHERE m.week_date = '{week_date}'"
        else:
            date_filter = "WHERE m.week_date = (SELECT MAX(week_date) FROM weekly_metrics)"
        
        query = f'''
            SELECT 
                ROW_NUMBER() OVER (ORDER BY m.dpi DESC) as rank,
                p.pod_name,
                p.stack,
                p.tier,
                m.dpi,
                m.release_velocity_score,
                m.git_hygiene_pillar_score,
                m.pipeline_maturity_score,
                m.compliance_score,
                m.quality_security_score,
                m.adoption_score
            FROM pods p
            JOIN weekly_metrics m ON p.pod_id = m.pod_id
            {date_filter}
            ORDER BY m.dpi DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def delete_pod(self, pod_id: str):
        """
        Delete a pod and its metrics.
        
        Args:
            pod_id: Pod identifier to delete.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM weekly_metrics WHERE pod_id = ?", (pod_id,))
        cursor.execute("DELETE FROM pods WHERE pod_id = ?", (pod_id,))
        
        conn.commit()
        conn.close()
        logger.info(f"Deleted pod: {pod_id}")
    
    def get_all_history(self) -> pd.DataFrame:
        """
        Get all historical metrics for all pods.
        
        Returns:
            DataFrame with all historical metrics.
        """
        conn = self._get_connection()
        
        query = '''
            SELECT 
                p.pod_id,
                p.pod_name AS Team,
                p.stack AS Stack,
                p.business_unit AS "Business Unit",
                p.tier AS Tier,
                m.week_date AS Week,
                m.mttr AS MTTR,
                m.lttd AS LTTD,
                m.rf AS RF,
                m.cfr AS CFR,
                m.git_hygiene_score,
                m.release_velocity_score AS Release_Velocity_Score,
                m.git_hygiene_pillar_score AS Git_Hygiene_Score,
                m.pipeline_maturity_score AS Pipeline_Maturity_Score,
                m.compliance_score AS Compliance_Score,
                m.quality_security_score AS Quality_Security_Score,
                m.adoption_score AS Adoption_Score,
                m.dpi AS DPI
            FROM pods p
            JOIN weekly_metrics m ON p.pod_id = m.pod_id
            ORDER BY m.week_date DESC, m.dpi DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Compute Week_Start from Week (start of ISO week)
        if 'Week' in df.columns and len(df) > 0:
            df['Week'] = pd.to_datetime(df['Week'])
            df['Week_Start'] = df['Week'].dt.to_period('W').apply(lambda r: r.start_time)
        else:
            df['Week_Start'] = pd.NaT
        
        logger.debug(f"Retrieved {len(df)} historical records")
        return df
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with counts and summary stats.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM pods")
        pod_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM weekly_metrics")
        metrics_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(week_date), MAX(week_date) FROM weekly_metrics")
        date_range = cursor.fetchone()
        
        cursor.execute("SELECT AVG(dpi) FROM weekly_metrics WHERE week_date = (SELECT MAX(week_date) FROM weekly_metrics)")
        avg_dpi = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_pods': pod_count,
            'total_metrics_records': metrics_count,
            'earliest_week': date_range[0],
            'latest_week': date_range[1],
            'average_dpi': round(avg_dpi, 2) if avg_dpi else 0
        }
