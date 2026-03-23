"""
Database module for storing and retrieving pod metrics data
Uses SQLite for persistent storage with historical tracking
"""

 

import sqlite3

import pandas as pd

from datetime import datetime

from typing import List, Dict, Optional

import logging

import os

 

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

 

class MetricsDatabase:

    """Handles all database operations for pod metrics"""

   

    def __init__(self, db_path: str = "metrics.db"):

        """

        Initialize database connection and create tables

       

        Args:

            db_path: Path to SQLite database file

        """

        import os
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Convert to absolute path
        self.db_path = os.path.abspath(db_path)
        logger.info(f"Database path resolved to: {self.db_path}")
        
        # Ensure parent directory exists (not the db file itself)
        db_dir = os.path.dirname(self.db_path)
        logger.info(f"Database directory: {db_dir}")
        
        if db_dir:
            if not os.path.exists(db_dir):
                logger.info(f"Creating database directory: {db_dir}")
                try:
                    os.makedirs(db_dir, exist_ok=True)
                except Exception as e:
                    logger.error(f"Failed to create directory {db_dir}: {e}")
                    raise
            elif not os.access(db_dir, os.W_OK):
                logger.error(f"No write permission for directory: {db_dir}")
                raise PermissionError(f"No write permission for directory: {db_dir}")
        
        # If metrics.db exists as a directory (error case), remove it
        if os.path.isdir(self.db_path):
            logger.warning(f"Database path {self.db_path} is a directory, removing it")
            import shutil
            shutil.rmtree(self.db_path)

        self.init_database()

   

    def init_database(self):

        """Create database tables if they don't exist"""

        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()

       

        # Pods table

        cursor.execute('''

            CREATE TABLE IF NOT EXISTS pods (

                pod_id INTEGER PRIMARY KEY,

                pod_name TEXT NOT NULL,

                stack TEXT,

                business_unit TEXT,

                tier TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )

        ''')

       

        # Weekly metrics table

        cursor.execute('''

            CREATE TABLE IF NOT EXISTS weekly_metrics (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                pod_id INTEGER NOT NULL,

                week_date DATE NOT NULL,

                week_start DATE NOT NULL,

                rf INTEGER,

                lttd REAL,

                ltdd_measurable REAL,

                cfr REAL,

                mttr REAL,

                priv_access INTEGER DEFAULT 0,

                ci BOOLEAN DEFAULT 0,

                cd BOOLEAN DEFAULT 0,

                iac BOOLEAN DEFAULT 0,

                rollback BOOLEAN DEFAULT 0,

                self_service BOOLEAN DEFAULT 0,

                cfr_reported BOOLEAN DEFAULT 1,

                automation_audited BOOLEAN DEFAULT 1,

                critical_data_present BOOLEAN DEFAULT 1,

                rf_score INTEGER,

                flow_score INTEGER,

                cfr_score INTEGER,

                mttr_score INTEGER,

                priv_score INTEGER,

                automation_score INTEGER,

                stability_score INTEGER,

                dpi INTEGER,

                velocity REAL,

                flow REAL,

                stability REAL,

                automation REAL,

                quality_security REAL,

                ai_adoption REAL,

                tier_name TEXT,

                data_quality_flags TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (pod_id) REFERENCES pods (pod_id),

                UNIQUE(pod_id, week_date)

            )

        ''')

       

        # Create indexes for faster queries

        cursor.execute('''

            CREATE INDEX IF NOT EXISTS idx_weekly_metrics_pod_week

            ON weekly_metrics(pod_id, week_date)

        ''')

       

        cursor.execute('''

            CREATE INDEX IF NOT EXISTS idx_weekly_metrics_week

            ON weekly_metrics(week_date)

        ''')

       

        conn.commit()

        conn.close()

        logger.info("Database initialized successfully")

   

    def upsert_pod(self, pod_id: int, pod_name: str, stack: str = None,

                   business_unit: str = None, tier: str = None):

        """

        Insert or update pod information

       

        Args:

            pod_id: Pod ID

            pod_name: Pod name

            stack: Technology stack (Legacy, Cloud Native, Hybrid)

            business_unit: Business unit

            tier: Performance tier

        """

        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()

       

        cursor.execute('''

            INSERT INTO pods (pod_id, pod_name, stack, business_unit, tier, updated_at)

            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)

            ON CONFLICT(pod_id) DO UPDATE SET

                pod_name = excluded.pod_name,

                stack = COALESCE(excluded.stack, stack),

                business_unit = COALESCE(excluded.business_unit, business_unit),

                tier = COALESCE(excluded.tier, tier),

                updated_at = CURRENT_TIMESTAMP

        ''', (pod_id, pod_name, stack, business_unit, tier))

       

        conn.commit()

        conn.close()

   

    def insert_weekly_metrics(self, metrics: Dict):

        """

        Insert or update weekly metrics for a pod

       

        Args:

            metrics: Dictionary containing all metric values

        """

        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()

       

        cursor.execute('''

            INSERT INTO weekly_metrics (

                pod_id, week_date, week_start, rf, lttd, ltdd_measurable, cfr, mttr,

                priv_access, ci, cd, iac, rollback, self_service,

                cfr_reported, automation_audited, critical_data_present,

                rf_score, flow_score, cfr_score, mttr_score, priv_score,

                automation_score, stability_score, dpi,

                velocity, flow, stability, automation, quality_security, ai_adoption, tier_name,

                data_quality_flags,

                release_velocity_score, git_hygiene_score, pipeline_maturity_score,

                compliance_score, quality_security_score, adoption_score,

                release_velocity_weighted, git_hygiene_weighted, pipeline_maturity_weighted,

                compliance_weighted, quality_security_weighted, adoption_weighted,

                pipeline_standard, feature_flags_adopted, has_release_page,

                has_compliance_evidence, apis_published, copilot_enabled,

                git_hygiene_violations_critical, git_hygiene_violations_warnings

            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(pod_id, week_date) DO UPDATE SET

                rf = excluded.rf,

                lttd = excluded.lttd,

                ltdd_measurable = excluded.ltdd_measurable,

                cfr = excluded.cfr,

                mttr = excluded.mttr,

                priv_access = excluded.priv_access,

                ci = excluded.ci,

                cd = excluded.cd,

                iac = excluded.iac,

                rollback = excluded.rollback,

                self_service = excluded.self_service,

                cfr_reported = excluded.cfr_reported,

                automation_audited = excluded.automation_audited,

                critical_data_present = excluded.critical_data_present,

                rf_score = excluded.rf_score,

                flow_score = excluded.flow_score,

                cfr_score = excluded.cfr_score,

                mttr_score = excluded.mttr_score,

                priv_score = excluded.priv_score,

                automation_score = excluded.automation_score,

                stability_score = excluded.stability_score,

                dpi = excluded.dpi,

                velocity = excluded.velocity,

                flow = excluded.flow,

                stability = excluded.stability,

                automation = excluded.automation,

                quality_security = excluded.quality_security,

                ai_adoption = excluded.ai_adoption,

                tier_name = excluded.tier_name,

                data_quality_flags = excluded.data_quality_flags,

                release_velocity_score = excluded.release_velocity_score,

                git_hygiene_score = excluded.git_hygiene_score,

                pipeline_maturity_score = excluded.pipeline_maturity_score,

                compliance_score = excluded.compliance_score,

                quality_security_score = excluded.quality_security_score,

                adoption_score = excluded.adoption_score,

                release_velocity_weighted = excluded.release_velocity_weighted,

                git_hygiene_weighted = excluded.git_hygiene_weighted,

                pipeline_maturity_weighted = excluded.pipeline_maturity_weighted,

                compliance_weighted = excluded.compliance_weighted,

                quality_security_weighted = excluded.quality_security_weighted,

                adoption_weighted = excluded.adoption_weighted,

                pipeline_standard = excluded.pipeline_standard,

                feature_flags_adopted = excluded.feature_flags_adopted,

                has_release_page = excluded.has_release_page,

                has_compliance_evidence = excluded.has_compliance_evidence,

                apis_published = excluded.apis_published,

                copilot_enabled = excluded.copilot_enabled,

                git_hygiene_violations_critical = excluded.git_hygiene_violations_critical,

                git_hygiene_violations_warnings = excluded.git_hygiene_violations_warnings

        ''', (

            metrics.get('pod_id'),

            metrics.get('week_date'),

            metrics.get('week_start'),

            metrics.get('rf'),

            metrics.get('lttd'),

            metrics.get('ltdd_measurable'),

            metrics.get('cfr'),

            metrics.get('mttr'),

            metrics.get('priv_access', 0),

            metrics.get('ci', False),

            metrics.get('cd', False),

            metrics.get('iac', False),

            metrics.get('rollback', False),

            metrics.get('self_service', False),

            metrics.get('cfr_reported', True),

            metrics.get('automation_audited', True),

            metrics.get('critical_data_present', True),

            metrics.get('rf_score'),

            metrics.get('flow_score'),

            metrics.get('cfr_score'),

            metrics.get('mttr_score'),

            metrics.get('priv_score'),

            metrics.get('automation_score'),

            metrics.get('stability_score'),

            metrics.get('dpi'),

            metrics.get('velocity'),

            metrics.get('flow'),

            metrics.get('stability'),

            metrics.get('automation'),

            metrics.get('quality_security'),

            metrics.get('ai_adoption'),

            metrics.get('tier'),

            metrics.get('data_quality_flags', ''),

            metrics.get('release_velocity_score'),

            metrics.get('git_hygiene_score'),

            metrics.get('pipeline_maturity_score'),

            metrics.get('compliance_score'),

            metrics.get('quality_security_score'),

            metrics.get('adoption_score'),

            metrics.get('release_velocity_weighted'),

            metrics.get('git_hygiene_weighted'),

            metrics.get('pipeline_maturity_weighted'),

            metrics.get('compliance_weighted'),

            metrics.get('quality_security_weighted'),

            metrics.get('adoption_weighted'),

            metrics.get('pipeline_standard', 'v1'),

            metrics.get('feature_flags_adopted', False),

            metrics.get('has_release_page', False),

            metrics.get('has_compliance_evidence', False),

            metrics.get('apis_published', False),

            metrics.get('copilot_enabled', False),

            metrics.get('git_hygiene_violations_critical', 0),

            metrics.get('git_hygiene_violations_warnings', 0)

        ))

       

        conn.commit()

        conn.close()

   

    def get_latest_metrics(self) -> pd.DataFrame:

        """

        Get the latest metrics for all pods

       

        Returns:

            DataFrame with latest metrics for each pod

        """

        conn = sqlite3.connect(self.db_path)

       

        query = '''

            SELECT

                p.pod_name as Team,

                date(wm.week_date) as Week,

                wm.rf as RF,

                wm.lttd as LTDD,

                wm.ltdd_measurable as LTDD_Measurable,

                wm.cfr as CFR,

                wm.mttr as MTTR,

                wm.priv_access as Priv_Access,

                wm.ci as CI,

                wm.cd as CD,

                wm.iac as IaC,

                wm.rollback as Rollback,

                wm.self_service as Self_Service,

                wm.cfr_reported as CFR_Reported,

                wm.automation_audited as Automation_Audited,

                wm.critical_data_present as Critical_Data_Present,

                p.stack as Stack,

                p.business_unit as "Business Unit",

                date(wm.week_start) as Week_Start,

                wm.dpi as DPI,

                wm.tier_name as Tier,

                wm.velocity as Velocity,

                wm.flow as Flow,

                wm.stability as Stability,

                wm.automation as Automation,

                wm.quality_security as Quality_Security,

                wm.ai_adoption as AI_Adoption,

                wm.data_quality_flags as Data_Quality_Flags

            FROM weekly_metrics wm

            JOIN pods p ON wm.pod_id = p.pod_id

            WHERE wm.id = (

                SELECT wm2.id

                FROM weekly_metrics wm2

                WHERE wm2.pod_id = wm.pod_id

                ORDER BY date(wm2.week_date) DESC, wm2.created_at DESC, wm2.id DESC

                LIMIT 1

            )

            ORDER BY wm.dpi DESC

        '''

       

        df = pd.read_sql_query(query, conn)

        conn.close()

       

        return df

   

    def get_historical_metrics(self, pod_id: Optional[int] = None,

                               weeks: int = 12) -> pd.DataFrame:

        """

        Get historical metrics for trend analysis

       

        Args:

            pod_id: Optional pod ID to filter by

            weeks: Number of weeks to retrieve

           

        Returns:

            DataFrame with historical metrics

        """

        conn = sqlite3.connect(self.db_path)

       

        if pod_id:

            query = '''

                SELECT

                    p.pod_name as Team,

                    date(wm.week_date) as Week,

                    wm.rf as RF,

                    wm.lttd as LTDD,

                    wm.ltdd_measurable as LTDD_Measurable,

                    wm.cfr as CFR,

                    wm.mttr as MTTR,

                    wm.priv_access as Priv_Access,

                    wm.ci as CI,

                    wm.cd as CD,

                    wm.iac as IaC,

                    wm.rollback as Rollback,

                    wm.self_service as Self_Service,

                    wm.cfr_reported as CFR_Reported,

                    wm.automation_audited as Automation_Audited,

                    wm.critical_data_present as Critical_Data_Present,

                    p.stack as Stack,

                    p.business_unit as "Business Unit",

                    date(wm.week_start) as Week_Start,

                    wm.dpi as DPI,

                    wm.tier_name as Tier,

                    wm.velocity as Velocity,

                    wm.flow as Flow,

                    wm.stability as Stability,

                    wm.automation as Automation,

                    wm.quality_security as Quality_Security,

                    wm.ai_adoption as AI_Adoption,

                    wm.data_quality_flags as Data_Quality_Flags

                FROM weekly_metrics wm

                JOIN pods p ON wm.pod_id = p.pod_id

                WHERE wm.pod_id = ?

                ORDER BY date(wm.week_date) DESC

                LIMIT ?

            '''

            df = pd.read_sql_query(query, conn, params=(pod_id, weeks))

        else:

            query = '''

                SELECT

                    p.pod_name as Team,

                    date(wm.week_date) as Week,

                    wm.rf as RF,

                    wm.lttd as LTDD,

                    wm.ltdd_measurable as LTDD_Measurable,

                    wm.cfr as CFR,

                    wm.mttr as MTTR,

                    wm.priv_access as Priv_Access,

                    wm.ci as CI,

                    wm.cd as CD,

                    wm.iac as IaC,

                    wm.rollback as Rollback,

                    wm.self_service as Self_Service,

                    wm.cfr_reported as CFR_Reported,

                    wm.automation_audited as Automation_Audited,

                    wm.critical_data_present as Critical_Data_Present,

                    p.stack as Stack,

                    p.business_unit as "Business Unit",

                    date(wm.week_start) as Week_Start,

                    wm.dpi as DPI,

                    wm.tier_name as Tier,

                    wm.velocity as Velocity,

                    wm.flow as Flow,

                    wm.stability as Stability,

                    wm.automation as Automation,

                    wm.quality_security as Quality_Security,

                    wm.ai_adoption as AI_Adoption,

                    wm.data_quality_flags as Data_Quality_Flags

                FROM weekly_metrics wm

                JOIN pods p ON wm.pod_id = p.pod_id

                WHERE date(wm.week_date) >= date('now', '-' || ? || ' days')

                ORDER BY date(wm.week_date) DESC, wm.dpi DESC

            '''

            df = pd.read_sql_query(query, conn, params=(weeks * 7,))

       

        conn.close()

        return df

   

    def get_all_pods(self) -> pd.DataFrame:

        """

        Get all pods information

       

        Returns:

            DataFrame with all pods

        """

        conn = sqlite3.connect(self.db_path)

        df = pd.read_sql_query('SELECT * FROM pods ORDER BY pod_name', conn)

        conn.close()

        return df

   

    def delete_week_data(self, week_date: str):

        """

        Delete all metrics for a specific week

       

        Args:

            week_date: Week date to delete

        """

        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()

        cursor.execute('DELETE FROM weekly_metrics WHERE week_date = ?', (week_date,))

        conn.commit()

        conn.close()

        logger.info(f"Deleted metrics for week: {week_date}")