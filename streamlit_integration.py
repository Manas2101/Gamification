"""
Streamlit integration module for database-backed dashboard
Provides data loading and refresh functionality
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import logging

from database import MetricsDatabase
from data_fetcher import DataFetcher
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardDataLoader:
    """Handles data loading for Streamlit dashboard"""
    
    def __init__(self):
        """Initialize database connection"""
        self.db = MetricsDatabase(config.DB_PATH)
    
    @st.cache_data(ttl=3600)
    def load_latest_metrics(_self) -> pd.DataFrame:
        """
        Load latest metrics for all pods
        
        Returns:
            DataFrame with latest metrics
        """
        try:
            df = _self.db.get_latest_metrics()
            
            if df.empty:
                logger.warning("No data found in database. Using sample data.")
                return _self._create_sample_data()
            
            return df
        except Exception as e:
            logger.error(f"Error loading latest metrics: {e}")
            return _self._create_sample_data()
    
    @st.cache_data(ttl=3600)
    def load_historical_metrics(_self, weeks: int = 12) -> pd.DataFrame:
        """
        Load historical metrics for trend analysis
        
        Args:
            weeks: Number of weeks to load
            
        Returns:
            DataFrame with historical data
        """
        try:
            df = _self.db.get_historical_metrics(weeks=weeks)
            
            if df.empty:
                logger.warning("No historical data found")
                return pd.DataFrame()
            
            return df
        except Exception as e:
            logger.error(f"Error loading historical metrics: {e}")
            return pd.DataFrame()
    
    def _create_sample_data(self) -> pd.DataFrame:
        """
        Create sample data for initial display
        
        Returns:
            Sample DataFrame
        """
        return pd.DataFrame({
            'Team': ['Sample Team 1', 'Sample Team 2'],
            'Week': [datetime.now(), datetime.now()],
            'RF': [150, 200],
            'LTDD': [10.5, 8.2],
            'LTDD_Measurable': [0.92, 0.95],
            'CFR': [0.15, 0.10],
            'MTTR': [1.5, 1.2],
            'Priv_Access': [1, 0],
            'CI': [True, True],
            'CD': [True, True],
            'IaC': [True, True],
            'Rollback': [True, True],
            'Self_Service': [True, True],
            'CFR_Reported': [True, True],
            'Automation_Audited': [True, True],
            'Critical_Data_Present': [True, True],
            'Stack': ['Cloud Native', 'Hybrid'],
            'Business Unit': ['BU A', 'BU B'],
            'Week_Start': [datetime.now(), datetime.now()],
            'DPI': [55, 62],
            'Tier': ['Emerging', 'Emerging'],
            'RF_Score': [18, 25],
            'Flow_Score': [10, 15],
            'CFR_Score': [4, 4],
            'MTTR_Score': [4, 4],
            'Priv_Score': [2, 0],
            'Automation_Score': [15, 15],
            'Stability_Score': [10, 12],
            'Data_Quality_Flags': ['[]', '[]']
        })
    
    
    def get_pods_list(self) -> pd.DataFrame:
        """
        Get list of all pods
        
        Returns:
            DataFrame with pod information
        """
        try:
            return self.db.get_all_pods()
        except Exception as e:
            logger.error(f"Error loading pods list: {e}")
            return pd.DataFrame()


def show_data_refresh_section():
    """Display data refresh controls in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Data Refresh")
    
    # Check if bearer tokens are configured
    teambook_configured = bool(config.TEAMBOOK_BEARER_TOKEN)
    datasight_configured = bool(config.DATASIGHT_BEARER_TOKEN)
    
    if not teambook_configured or not datasight_configured:
        st.sidebar.warning("⚠️ Bearer tokens not configured")
        
        missing = []
        if not teambook_configured:
            missing.append("TEAMBOOK_BEARER_TOKEN")
        if not datasight_configured:
            missing.append("DATASIGHT_BEARER_TOKEN")
        
        st.sidebar.caption(f"Missing: {', '.join(missing)}")
        
        with st.sidebar.expander("ℹ️ How to configure"):
            st.markdown("""
            1. Copy `.env.example` to `.env`
            2. Add your TeamBook bearer token
            3. Add your DataSight bearer token
            4. Restart the dashboard
            
            **Note:** TeamBook and DataSight require separate tokens.
            """)
        return
    
    # Show configured status
    st.sidebar.success("✅ Tokens configured")
    st.sidebar.caption("🔑 TeamBook & DataSight")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data Now", use_container_width=True):
        loader = DashboardDataLoader()
        # Pass both tokens
        with st.spinner('Fetching from TeamBook and DataSight APIs...'):
            try:
                fetcher = DataFetcher(
                    config.TEAMBOOK_BEARER_TOKEN,
                    config.DATASIGHT_BEARER_TOKEN,
                    config.DB_PATH
                )
                fetcher.refresh_current_week()
                fetcher.cleanup_old_data(max_weeks=config.MAX_WEEKS_TO_KEEP)
                st.cache_data.clear()
                st.success(f'✅ Data refreshed! Keeping last {config.MAX_WEEKS_TO_KEEP} weeks.')
            except Exception as e:
                st.error(f'❌ Error: {str(e)}')
    
    # Last refresh info
    st.sidebar.caption("💡 Data is cached for 1 hour")
    st.sidebar.caption("⏰ Set up cron for weekly auto-refresh")
    
    # Manual cache clear
    if st.sidebar.button("Clear Cache", use_container_width=True):
        st.cache_data.clear()
        st.sidebar.success("Cache cleared!")


def load_dashboard_data() -> tuple:
    """
    Load all data needed for dashboard
    
    Returns:
        Tuple of (latest_df, history_df)
    """
    loader = DashboardDataLoader()
    
    latest_df = loader.load_latest_metrics()
    history_df = loader.load_historical_metrics()
    
    # If history is empty, use latest as history
    if history_df.empty and not latest_df.empty:
        history_df = latest_df.copy()
    
    return latest_df, history_df
