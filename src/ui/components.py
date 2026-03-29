"""
Dashboard Components
====================

Reusable UI components for the Streamlit dashboard.

Provides styled components for:
    - Metric cards and KPI displays
    - Leaderboard tables
    - Badge displays
    - Filter controls

Example:
    >>> from src.ui.components import DashboardComponents
    >>> components = DashboardComponents()
    >>> components.render_metric_card("DPI Score", 85.5, delta=5.2)

Author: DevOps Transformation Team
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any


class DashboardComponents:
    """
    Reusable dashboard UI components.
    
    Provides consistent styling and behavior for common
    dashboard elements.
    
    Example:
        >>> dc = DashboardComponents()
        >>> dc.render_header("My Dashboard")
        >>> dc.render_metric_card("Score", 85)
    """
    
    # Color scheme
    COLORS = {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'success': '#48bb78',
        'warning': '#ed8936',
        'danger': '#f56565',
        'info': '#4299e1',
        'dark': '#1a202c',
        'light': '#f7fafc'
    }
    
    # Badge tier colors
    TIER_COLORS = {
        'platinum': '#e5e4e2',
        'gold': '#ffd700',
        'silver': '#c0c0c0',
        'bronze': '#cd7f32'
    }
    
    def __init__(self):
        """Initialize dashboard components."""
        pass
    
    def apply_custom_css(self):
        """
        Apply custom CSS styling to the dashboard.
        
        Should be called once at the start of the app.
        """
        st.markdown("""
        <style>
        /* Dark theme base */
        .main { background: #1a202c; }
        .stApp { background: #1a202c; }
        
        /* Text colors */
        .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p {
            color: white !important;
        }
        
        /* Metric cards */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: white;
        }
        
        .metric-label {
            font-size: 1rem;
            color: rgba(255,255,255,0.8);
        }
        
        .metric-delta-positive {
            color: #48bb78;
            font-size: 0.9rem;
        }
        
        .metric-delta-negative {
            color: #f56565;
            font-size: 0.9rem;
        }
        
        /* Badge styling */
        .badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            margin: 5px;
            font-weight: 600;
        }
        
        .badge-platinum { background: linear-gradient(135deg, #e5e4e2, #b8b8b8); color: #333; }
        .badge-gold { background: linear-gradient(135deg, #ffd700, #ffb700); color: #333; }
        .badge-silver { background: linear-gradient(135deg, #c0c0c0, #a0a0a0); color: #333; }
        .badge-bronze { background: linear-gradient(135deg, #cd7f32, #b87333); color: white; }
        
        /* Leaderboard styling */
        .leaderboard-row {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            margin: 5px 0;
        }
        
        .leaderboard-rank {
            font-size: 1.5rem;
            font-weight: bold;
            color: #ffd700;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: #1a202c;
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self, title: str, subtitle: str = None):
        """
        Render page header with title and optional subtitle.
        
        Args:
            title: Main page title.
            subtitle: Optional subtitle text.
        """
        st.markdown(f"""
        <div style="
            background: rgba(45,55,72,0.3);
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        ">
            <h1 style="
                font-size: 2.5rem;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            ">{title}</h1>
            {f'<p style="color: rgba(255,255,255,0.7);">{subtitle}</p>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)
    
    def render_metric_card(
        self, 
        label: str, 
        value: Any, 
        delta: float = None,
        format_str: str = "{:.1f}"
    ):
        """
        Render a metric card with value and optional delta.
        
        Args:
            label: Metric label text.
            value: Metric value.
            delta: Optional change value (positive/negative).
            format_str: Format string for value display.
        """
        # Format value
        if isinstance(value, (int, float)):
            display_value = format_str.format(value)
        else:
            display_value = str(value)
        
        # Format delta
        delta_html = ""
        if delta is not None:
            delta_class = "metric-delta-positive" if delta >= 0 else "metric-delta-negative"
            delta_sign = "+" if delta >= 0 else ""
            delta_html = f'<div class="{delta_class}">{delta_sign}{delta:.1f}</div>'
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{display_value}</div>
            <div class="metric-label">{label}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
    
    def render_badge(self, name: str, tier: str, icon: str = "🏅"):
        """
        Render a badge with tier styling.
        
        Args:
            name: Badge name.
            tier: Badge tier (platinum, gold, silver, bronze).
            icon: Badge icon emoji.
        """
        tier_lower = tier.lower()
        st.markdown(f"""
        <span class="badge badge-{tier_lower}">
            {icon} {name}
        </span>
        """, unsafe_allow_html=True)
    
    def render_badges_row(self, badges: List[Dict]):
        """
        Render multiple badges in a row.
        
        Args:
            badges: List of badge dictionaries with name, tier, icon.
        """
        badges_html = ""
        for badge in badges:
            tier = badge.get('tier', 'bronze').lower()
            icon = badge.get('icon', '🏅')
            name = badge.get('name', 'Badge')
            badges_html += f'<span class="badge badge-{tier}">{icon} {name}</span>'
        
        st.markdown(f"""
        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
            {badges_html}
        </div>
        """, unsafe_allow_html=True)
    
    def render_leaderboard_entry(
        self, 
        rank: int, 
        name: str, 
        score: float,
        details: Dict = None
    ):
        """
        Render a single leaderboard entry.
        
        Args:
            rank: Position in leaderboard.
            name: Team/pod name.
            score: DPI score.
            details: Optional additional details.
        """
        # Rank styling
        if rank == 1:
            rank_icon = "🥇"
        elif rank == 2:
            rank_icon = "🥈"
        elif rank == 3:
            rank_icon = "🥉"
        else:
            rank_icon = f"#{rank}"
        
        details_html = ""
        if details:
            details_html = " | ".join([
                f"{k}: {v}" for k, v in details.items()
            ])
        
        st.markdown(f"""
        <div class="leaderboard-row">
            <span class="leaderboard-rank">{rank_icon}</span>
            <span style="font-size: 1.2rem; margin-left: 15px;">{name}</span>
            <span style="float: right; font-size: 1.5rem; font-weight: bold;">
                {score:.1f}
            </span>
            {f'<div style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">{details_html}</div>' if details_html else ''}
        </div>
        """, unsafe_allow_html=True)
    
    def render_progress_bar(
        self, 
        value: float, 
        max_value: float = 100,
        label: str = None,
        color: str = None
    ):
        """
        Render a progress bar.
        
        Args:
            value: Current value.
            max_value: Maximum value.
            label: Optional label text.
            color: Optional custom color.
        """
        percentage = min(100, (value / max_value) * 100)
        
        if color is None:
            if percentage >= 80:
                color = self.COLORS['success']
            elif percentage >= 60:
                color = self.COLORS['warning']
            else:
                color = self.COLORS['danger']
        
        st.markdown(f"""
        <div style="margin: 10px 0;">
            {f'<div style="color: white; margin-bottom: 5px;">{label}</div>' if label else ''}
            <div style="
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                height: 20px;
                overflow: hidden;
            ">
                <div style="
                    background: {color};
                    width: {percentage}%;
                    height: 100%;
                    border-radius: 10px;
                    transition: width 0.5s ease;
                "></div>
            </div>
            <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem; text-align: right;">
                {value:.1f} / {max_value}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_pillar_scores(self, scores: Dict):
        """
        Render all six pillar scores with progress bars.
        
        Args:
            scores: Dictionary with pillar scores.
        """
        pillars = [
            ('Release_Velocity_Score', 'Release Velocity', '🚀'),
            ('Git_Hygiene_Score', 'Git Hygiene', '✨'),
            ('Pipeline_Maturity_Score', 'Pipeline Maturity', '⚙️'),
            ('Compliance_Score', 'Compliance', '📋'),
            ('Quality_Security_Score', 'Quality & Security', '🛡️'),
            ('Adoption_Score', 'Adoption', '💡')
        ]
        
        for key, label, icon in pillars:
            score = scores.get(key, 0)
            self.render_progress_bar(score, 100, f"{icon} {label}")
    
    def render_filter_sidebar(
        self, 
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Render filter controls in sidebar.
        
        Args:
            df: DataFrame with data to filter.
            
        Returns:
            Dictionary with selected filter values.
        """
        st.sidebar.header("🔍 Filters")
        
        filters = {}
        
        # Stack filter
        if 'stack' in df.columns:
            stacks = ['All'] + sorted(df['stack'].dropna().unique().tolist())
            filters['stack'] = st.sidebar.selectbox("Stack", stacks)
        
        # Tier filter
        if 'tier' in df.columns:
            tiers = ['All'] + sorted(df['tier'].dropna().unique().tolist())
            filters['tier'] = st.sidebar.selectbox("Tier", tiers)
        
        # Business unit filter
        if 'business_unit' in df.columns:
            bus = ['All'] + sorted(df['business_unit'].dropna().unique().tolist())
            filters['business_unit'] = st.sidebar.selectbox("Business Unit", bus)
        
        # DPI range filter
        if 'dpi' in df.columns:
            min_dpi = float(df['dpi'].min()) if not df['dpi'].isna().all() else 0
            max_dpi = float(df['dpi'].max()) if not df['dpi'].isna().all() else 100
            filters['dpi_range'] = st.sidebar.slider(
                "DPI Range",
                min_value=0.0,
                max_value=100.0,
                value=(min_dpi, max_dpi)
            )
        
        return filters
    
    def apply_filters(self, df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
        """
        Apply filters to DataFrame.
        
        Args:
            df: DataFrame to filter.
            filters: Dictionary of filter values.
            
        Returns:
            Filtered DataFrame.
        """
        filtered = df.copy()
        
        if filters.get('stack') and filters['stack'] != 'All':
            filtered = filtered[filtered['stack'] == filters['stack']]
        
        if filters.get('tier') and filters['tier'] != 'All':
            filtered = filtered[filtered['tier'] == filters['tier']]
        
        if filters.get('business_unit') and filters['business_unit'] != 'All':
            filtered = filtered[filtered['business_unit'] == filters['business_unit']]
        
        if filters.get('dpi_range'):
            min_dpi, max_dpi = filters['dpi_range']
            filtered = filtered[
                (filtered['dpi'] >= min_dpi) & 
                (filtered['dpi'] <= max_dpi)
            ]
        
        return filtered
