"""
Chart Builder
=============

Chart and visualization builders for the dashboard.

Provides methods to create:
    - DPI trend charts
    - Pillar comparison charts
    - Leaderboard visualizations
    - Distribution charts

Example:
    >>> from src.ui.charts import ChartBuilder
    >>> builder = ChartBuilder()
    >>> chart = builder.create_dpi_trend_chart(history_df)

Author: DevOps Transformation Team
"""

import pandas as pd
import streamlit as st
from typing import Dict, List, Optional


class ChartBuilder:
    """
    Builder for dashboard charts and visualizations.
    
    Uses Streamlit's native charting capabilities for
    consistent styling and interactivity.
    
    Example:
        >>> cb = ChartBuilder()
        >>> cb.render_dpi_trend(df, "pod_123")
    """
    
    # Chart color palette
    COLORS = {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'success': '#48bb78',
        'warning': '#ed8936',
        'danger': '#f56565',
        'pillars': [
            '#667eea',  # Release Velocity
            '#48bb78',  # Git Hygiene
            '#ed8936',  # Pipeline Maturity
            '#9f7aea',  # Compliance
            '#f56565',  # Quality & Security
            '#4299e1'   # Adoption
        ]
    }
    
    def __init__(self):
        """Initialize chart builder."""
        pass
    
    def render_dpi_trend(
        self, 
        df: pd.DataFrame, 
        title: str = "DPI Trend"
    ):
        """
        Render DPI trend line chart.
        
        Args:
            df: DataFrame with week_date and dpi columns.
            title: Chart title.
        """
        if df.empty or 'dpi' not in df.columns:
            st.warning("No DPI data available for trend chart")
            return
        
        st.subheader(title)
        
        # Prepare data
        chart_data = df[['week_date', 'dpi']].copy()
        chart_data = chart_data.sort_values('week_date')
        chart_data = chart_data.set_index('week_date')
        
        st.line_chart(chart_data, use_container_width=True)
    
    def render_pillar_comparison(
        self, 
        scores: Dict,
        title: str = "Pillar Scores"
    ):
        """
        Render pillar comparison bar chart.
        
        Args:
            scores: Dictionary with pillar scores.
            title: Chart title.
        """
        st.subheader(title)
        
        # Prepare data
        pillars = {
            'Release Velocity': scores.get('Release_Velocity_Score', 0),
            'Git Hygiene': scores.get('Git_Hygiene_Score', 0),
            'Pipeline Maturity': scores.get('Pipeline_Maturity_Score', 0),
            'Compliance': scores.get('Compliance_Score', 0),
            'Quality & Security': scores.get('Quality_Security_Score', 0),
            'Adoption': scores.get('Adoption_Score', 0)
        }
        
        chart_df = pd.DataFrame({
            'Pillar': list(pillars.keys()),
            'Score': list(pillars.values())
        })
        chart_df = chart_df.set_index('Pillar')
        
        st.bar_chart(chart_df, use_container_width=True)
    
    def render_dpi_distribution(
        self, 
        df: pd.DataFrame,
        title: str = "DPI Distribution"
    ):
        """
        Render DPI score distribution histogram.
        
        Args:
            df: DataFrame with dpi column.
            title: Chart title.
        """
        if df.empty or 'dpi' not in df.columns:
            st.warning("No DPI data available")
            return
        
        st.subheader(title)
        
        # Create bins for distribution
        bins = [0, 30, 50, 70, 85, 95, 100]
        labels = ['0-30', '30-50', '50-70', '70-85', '85-95', '95-100']
        
        df_copy = df.copy()
        df_copy['DPI Range'] = pd.cut(
            df_copy['dpi'], 
            bins=bins, 
            labels=labels,
            include_lowest=True
        )
        
        distribution = df_copy['DPI Range'].value_counts().sort_index()
        st.bar_chart(distribution, use_container_width=True)
    
    def render_stack_comparison(
        self, 
        df: pd.DataFrame,
        title: str = "Average DPI by Stack"
    ):
        """
        Render average DPI comparison by technology stack.
        
        Args:
            df: DataFrame with stack and dpi columns.
            title: Chart title.
        """
        if df.empty or 'stack' not in df.columns or 'dpi' not in df.columns:
            st.warning("No stack data available")
            return
        
        st.subheader(title)
        
        # Calculate average DPI per stack
        stack_avg = df.groupby('stack')['dpi'].mean().sort_values(ascending=False)
        st.bar_chart(stack_avg, use_container_width=True)
    
    def render_tier_comparison(
        self, 
        df: pd.DataFrame,
        title: str = "Average DPI by Tier"
    ):
        """
        Render average DPI comparison by service tier.
        
        Args:
            df: DataFrame with tier and dpi columns.
            title: Chart title.
        """
        if df.empty or 'tier' not in df.columns or 'dpi' not in df.columns:
            st.warning("No tier data available")
            return
        
        st.subheader(title)
        
        # Calculate average DPI per tier
        tier_avg = df.groupby('tier')['dpi'].mean().sort_values(ascending=False)
        st.bar_chart(tier_avg, use_container_width=True)
    
    def render_pillar_trends(
        self, 
        df: pd.DataFrame,
        title: str = "Pillar Score Trends"
    ):
        """
        Render multi-line chart showing all pillar trends.
        
        Args:
            df: DataFrame with week_date and pillar score columns.
            title: Chart title.
        """
        pillar_columns = [
            'Release_Velocity_Score',
            'Git_Hygiene_Score',
            'Pipeline_Maturity_Score',
            'Compliance_Score',
            'Quality_Security_Score',
            'Adoption_Score'
        ]
        
        available_cols = [c for c in pillar_columns if c in df.columns]
        
        if not available_cols or 'week_date' not in df.columns:
            st.warning("No pillar trend data available")
            return
        
        st.subheader(title)
        
        chart_data = df[['week_date'] + available_cols].copy()
        chart_data = chart_data.sort_values('week_date')
        chart_data = chart_data.set_index('week_date')
        
        # Rename columns for display
        rename_map = {
            'Release_Velocity_Score': 'Release Velocity',
            'Git_Hygiene_Score': 'Git Hygiene',
            'Pipeline_Maturity_Score': 'Pipeline Maturity',
            'Compliance_Score': 'Compliance',
            'Quality_Security_Score': 'Quality & Security',
            'Adoption_Score': 'Adoption'
        }
        chart_data = chart_data.rename(columns=rename_map)
        
        st.line_chart(chart_data, use_container_width=True)
    
    def render_top_performers(
        self, 
        df: pd.DataFrame, 
        n: int = 5,
        title: str = "Top Performers"
    ):
        """
        Render top N performers chart.
        
        Args:
            df: DataFrame with pod_name and dpi columns.
            n: Number of top performers to show.
            title: Chart title.
        """
        if df.empty or 'pod_name' not in df.columns or 'dpi' not in df.columns:
            st.warning("No performance data available")
            return
        
        st.subheader(title)
        
        top_n = df.nlargest(n, 'dpi')[['pod_name', 'dpi']]
        top_n = top_n.set_index('pod_name')
        
        st.bar_chart(top_n, use_container_width=True)
    
    def render_improvement_needed(
        self, 
        df: pd.DataFrame, 
        n: int = 5,
        title: str = "Needs Improvement"
    ):
        """
        Render bottom N performers chart.
        
        Args:
            df: DataFrame with pod_name and dpi columns.
            n: Number of bottom performers to show.
            title: Chart title.
        """
        if df.empty or 'pod_name' not in df.columns or 'dpi' not in df.columns:
            st.warning("No performance data available")
            return
        
        st.subheader(title)
        
        bottom_n = df.nsmallest(n, 'dpi')[['pod_name', 'dpi']]
        bottom_n = bottom_n.set_index('pod_name')
        
        st.bar_chart(bottom_n, use_container_width=True)
    
    def render_metrics_summary(self, df: pd.DataFrame):
        """
        Render summary metrics in columns.
        
        Args:
            df: DataFrame with metrics data.
        """
        if df.empty:
            st.warning("No data available")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_dpi = df['dpi'].mean() if 'dpi' in df.columns else 0
            st.metric("Average DPI", f"{avg_dpi:.1f}")
        
        with col2:
            total_pods = len(df)
            st.metric("Total Pods", total_pods)
        
        with col3:
            high_performers = len(df[df['dpi'] >= 80]) if 'dpi' in df.columns else 0
            st.metric("High Performers", high_performers)
        
        with col4:
            needs_attention = len(df[df['dpi'] < 50]) if 'dpi' in df.columns else 0
            st.metric("Needs Attention", needs_attention)
