"""
Streamlit integration module for database-backed dashboard
Bridges app.py to the refactored src/ modules
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import logging

from src.data.database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardDataLoader:
    """Handles data loading for Streamlit dashboard"""
    
    def __init__(self):
        self.db = Database()
    
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


def load_dashboard_data():
    """
    Load all dashboard data - main entry point for app.py
    
    Returns:
        DataFrame with latest metrics for all pods
    """
    loader = DashboardDataLoader()
    return loader.load_latest_data()


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
