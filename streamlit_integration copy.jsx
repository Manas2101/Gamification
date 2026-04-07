"""
Streamlit integration module for database-backed dashboard
Bridges app.py to the refactored src/ modules
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import logging

from src.data.database import Database
from src.utils.config import Config

# MongoDB support
try:
    from src.data.mongodb import MongoDatabase
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoDatabase = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardDataLoader:
    """Handles data loading for Streamlit dashboard"""
    
    def __init__(self):
        """Initialize database connection (MongoDB or SQLite)"""
        config = Config()
        
        # Use MongoDB if configured, otherwise SQLite
        if config.use_mongodb:
            if not MONGODB_AVAILABLE:
                logger.error("MongoDB configured but pymongo not installed!")
                st.error("❌ MongoDB configured but pymongo not installed. Install with: pip install pymongo")
                self.db = Database()  # Fallback to SQLite
            else:
                logger.info(f"Dashboard using MongoDB: {config.mongodb_database}")
                # Use URI if provided, otherwise use individual parameters
                if config.mongodb_uri:
                    self.db = MongoDatabase(
                        connection_string=config.mongodb_uri,
                        database_name=config.mongodb_database
                    )
                else:
                    self.db = MongoDatabase(
                        host=config.mongodb_host,
                        port=config.mongodb_port,
                        username=config.mongodb_username,
                        password=config.mongodb_password,
                        auth_source=config.mongodb_auth_source,
                        database_name=config.mongodb_database
                    )
        else:
            logger.info(f"Dashboard using SQLite: {config.db_path}")
            self.db = Database(config.db_path)
    
    def load_latest_data(self) -> pd.DataFrame:
        """Load latest metrics for all pods"""
        try:
            return self.db.get_latest_metrics()
        except Exception as e:
            logger.error(f"Error loading latest data: {e}")
            return pd.DataFrame()
    
    def load_pod_history(self, pod_id: str, weeks: int = 12) -> pd.DataFrame:
        """Load historical data for a specific pod"""
        try:
            return self.db.get_pod_history(pod_id, weeks)
        except Exception as e:
            logger.error(f"Error loading pod history: {e}")
            return pd.DataFrame()
    
    def load_leaderboard(self) -> pd.DataFrame:
        """Load leaderboard data"""
        try:
            return self.db.get_leaderboard()
        except Exception as e:
            logger.error(f"Error loading leaderboard: {e}")
            return pd.DataFrame()
    
    def load_all_history(self) -> pd.DataFrame:
        """Load all historical metrics for all pods"""
        try:
            return self.db.get_all_history()
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return pd.DataFrame()


def load_dashboard_data():
    """
    Load all dashboard data - main entry point for app.py
    
    Returns:
        Tuple of (latest_df, history_df):
            - latest_df: DataFrame with latest metrics for all pods
            - history_df: DataFrame with all historical metrics
    """
    loader = DashboardDataLoader()
    latest_df = loader.load_latest_data()
    history_df = loader.load_all_history()
    return latest_df, history_df


def show_data_refresh_section():
    """
    Show data refresh section in sidebar.
    Data refresh is now handled via main.py refresh command.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Data Refresh")
    st.sidebar.info(
        "To refresh data, run:\n"
        "```\npython main.py refresh\n```"
    )
