#!/usr/bin/env python3
"""
DevOps Transformation Platform - Dashboard
===========================================

Streamlit dashboard for visualizing DevOps metrics and gamification.

Features:
    - Overview with key metrics and trends
    - Leaderboard with filtering
    - Badge gallery and achievements
    - Team deep dive with pillar breakdown
    - AI-powered recommendations

Usage:
    streamlit run dashboard.py

Author: DevOps Transformation Team
"""

import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
from datetime import datetime

from src.utils.config import Config
from src.data.database import Database
from src.core.badges import BadgeEngine
from src.core.recommendations import RecommendationEngine
from src.ui.components import DashboardComponents
from src.ui.charts import ChartBuilder


# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    layout="wide",
    page_title="🚀 DevOps Gamification Dashboard",
    page_icon="🏆"
)


# =============================================================================
# Initialize Components
# =============================================================================

@st.cache_resource
def get_config():
    """Get cached configuration."""
    return Config()


@st.cache_resource
def get_database():
    """Get cached database connection."""
    config = get_config()
    return Database(config.db_path)


@st.cache_data(ttl=300)
def load_data():
    """Load dashboard data with caching."""
    db = get_database()
    return db.get_latest_metrics()


# Initialize UI components
components = DashboardComponents()
charts = ChartBuilder()
badge_engine = BadgeEngine()
rec_engine = RecommendationEngine()


# =============================================================================
# Custom CSS
# =============================================================================

components.apply_custom_css()


# =============================================================================
# Header
# =============================================================================

components.render_header(
    "🚀 DevOps Gamification Dashboard",
    "Track your team's DevOps maturity across 6 pillars"
)


# =============================================================================
# Load Data
# =============================================================================

try:
    df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please run `python main.py setup` and `python main.py refresh` first.")
    data_loaded = False
    df = pd.DataFrame()


# =============================================================================
# Sidebar Filters
# =============================================================================

if data_loaded and not df.empty:
    filters = components.render_filter_sidebar(df)
    filtered_df = components.apply_filters(df, filters)
else:
    filtered_df = df


# =============================================================================
# Main Content Tabs
# =============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🏆 Leaderboard", 
    "🎖️ Badges",
    "🔍 Team Deep Dive",
    "💡 Recommendations"
])


# =============================================================================
# Tab 1: Overview
# =============================================================================

with tab1:
    if not data_loaded or df.empty:
        st.warning("No data available. Please run the weekly refresh first.")
        st.code("python main.py refresh", language="bash")
    else:
        # Summary metrics
        charts.render_metrics_summary(filtered_df)
        
        st.markdown("---")
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            charts.render_top_performers(filtered_df, n=5)
        
        with col2:
            charts.render_dpi_distribution(filtered_df)
        
        st.markdown("---")
        
        # Stack and Tier comparison
        col3, col4 = st.columns(2)
        
        with col3:
            charts.render_stack_comparison(filtered_df)
        
        with col4:
            charts.render_tier_comparison(filtered_df)


# =============================================================================
# Tab 2: Leaderboard
# =============================================================================

with tab2:
    if not data_loaded or df.empty:
        st.warning("No data available for leaderboard.")
    else:
        st.subheader("🏆 Team Leaderboard")
        
        # Sort by DPI
        leaderboard = filtered_df.sort_values('dpi', ascending=False).reset_index(drop=True)
        
        # Display top teams
        for idx, row in leaderboard.head(20).iterrows():
            rank = idx + 1
            
            # Get badges for this team
            scores = {
                'dpi': row.get('dpi', 0),
                'Release_Velocity_Score': row.get('Release_Velocity_Score', 0),
                'Git_Hygiene_Score': row.get('Git_Hygiene_Score', 0),
                'Pipeline_Maturity_Score': row.get('Pipeline_Maturity_Score', 0),
                'Compliance_Score': row.get('Compliance_Score', 0),
                'Quality_Security_Score': row.get('Quality_Security_Score', 0),
                'Adoption_Score': row.get('Adoption_Score', 0)
            }
            
            badges = badge_engine.compute_badges(scores)
            
            # Render leaderboard entry
            components.render_leaderboard_entry(
                rank=rank,
                name=row.get('pod_name', 'Unknown'),
                score=row.get('dpi', 0),
                details={
                    'Stack': row.get('stack', 'N/A'),
                    'Tier': row.get('tier', 'N/A'),
                    'Badges': len(badges)
                }
            )


# =============================================================================
# Tab 3: Badges
# =============================================================================

with tab3:
    st.subheader("🎖️ Badge Gallery")
    
    # Badge tier explanations
    st.markdown("""
    ### Badge Tiers
    
    | Tier | Score Range | Description |
    |------|-------------|-------------|
    | 💎 Platinum | 95-100 | Elite performance |
    | 🥇 Gold | 85-94 | Excellent performance |
    | 🥈 Silver | 70-84 | Strong performance |
    | 🥉 Bronze | 50-69 | Good foundation |
    """)
    
    st.markdown("---")
    
    # Pillar badges
    st.markdown("### Pillar Badges")
    
    pillar_badges = [
        {"name": "Velocity Champion", "icon": "🚀", "tier": "Gold", "description": "Excellence in release frequency"},
        {"name": "Hygiene Hero", "icon": "✨", "tier": "Gold", "description": "Clean and healthy repositories"},
        {"name": "Pipeline Pro", "icon": "⚙️", "tier": "Gold", "description": "Advanced CI/CD automation"},
        {"name": "Compliance Champion", "icon": "📋", "tier": "Gold", "description": "Meeting all compliance requirements"},
        {"name": "Quality Guardian", "icon": "🛡️", "tier": "Gold", "description": "Strong quality and security"},
        {"name": "Innovation Leader", "icon": "💡", "tier": "Gold", "description": "Early adoption of modern tools"}
    ]
    
    cols = st.columns(3)
    for i, badge in enumerate(pillar_badges):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                margin: 10px 0;
            ">
                <div style="font-size: 3rem;">{badge['icon']}</div>
                <div style="font-weight: bold; color: white;">{badge['name']}</div>
                <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">{badge['description']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Achievement badges
    st.markdown("### Achievement Badges")
    
    achievement_badges = [
        {"name": "DevOps Elite", "icon": "💎", "description": "Top-tier maturity across all pillars"},
        {"name": "Rapid Improver", "icon": "📈", "description": "Improved DPI by 10+ points"},
        {"name": "Well Rounded", "icon": "🎯", "description": "Strong performance across all pillars"},
        {"name": "Excellence Achiever", "icon": "⭐", "description": "Excellence in 3+ pillars"}
    ]
    
    cols = st.columns(4)
    for i, badge in enumerate(achievement_badges):
        with cols[i]:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea, #764ba2);
                padding: 15px;
                border-radius: 15px;
                text-align: center;
            ">
                <div style="font-size: 2rem;">{badge['icon']}</div>
                <div style="font-weight: bold; color: white; font-size: 0.9rem;">{badge['name']}</div>
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# Tab 4: Team Deep Dive
# =============================================================================

with tab4:
    if not data_loaded or df.empty:
        st.warning("No data available for team analysis.")
    else:
        st.subheader("🔍 Team Deep Dive")
        
        # Team selector
        team_names = filtered_df['pod_name'].tolist()
        selected_team = st.selectbox("Select Team", team_names)
        
        if selected_team:
            team_data = filtered_df[filtered_df['pod_name'] == selected_team].iloc[0]
            
            # Team header
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"### {selected_team}")
                st.markdown(f"**Stack**: {team_data.get('stack', 'N/A')} | **Tier**: {team_data.get('tier', 'N/A')}")
            
            with col2:
                dpi = team_data.get('dpi', 0)
                st.metric("DPI Score", f"{dpi:.1f}")
            
            with col3:
                scores = {col: team_data.get(col, 0) for col in [
                    'dpi', 'Release_Velocity_Score', 'Git_Hygiene_Score',
                    'Pipeline_Maturity_Score', 'Compliance_Score',
                    'Quality_Security_Score', 'Adoption_Score'
                ]}
                badges = badge_engine.compute_badges(scores)
                st.metric("Badges Earned", len(badges))
            
            st.markdown("---")
            
            # Pillar scores
            st.markdown("### Pillar Breakdown")
            
            pillar_scores = {
                'Release_Velocity_Score': team_data.get('Release_Velocity_Score', 0),
                'Git_Hygiene_Score': team_data.get('Git_Hygiene_Score', 0),
                'Pipeline_Maturity_Score': team_data.get('Pipeline_Maturity_Score', 0),
                'Compliance_Score': team_data.get('Compliance_Score', 0),
                'Quality_Security_Score': team_data.get('Quality_Security_Score', 0),
                'Adoption_Score': team_data.get('Adoption_Score', 0)
            }
            
            components.render_pillar_scores(pillar_scores)
            
            st.markdown("---")
            
            # Pillar comparison chart
            charts.render_pillar_comparison(pillar_scores, "Pillar Score Comparison")
            
            # Badges earned
            st.markdown("### Badges Earned")
            if badges:
                components.render_badges_row(badges)
            else:
                st.info("No badges earned yet. Keep improving!")


# =============================================================================
# Tab 5: Recommendations
# =============================================================================

with tab5:
    if not data_loaded or df.empty:
        st.warning("No data available for recommendations.")
    else:
        st.subheader("💡 Improvement Recommendations")
        
        # Team selector
        team_names = filtered_df['pod_name'].tolist()
        selected_team = st.selectbox("Select Team for Recommendations", team_names, key="rec_team")
        
        if selected_team:
            team_data = filtered_df[filtered_df['pod_name'] == selected_team].iloc[0]
            
            scores = {
                'Release_Velocity_Score': team_data.get('Release_Velocity_Score', 0),
                'Git_Hygiene_Score': team_data.get('Git_Hygiene_Score', 0),
                'Pipeline_Maturity_Score': team_data.get('Pipeline_Maturity_Score', 0),
                'Compliance_Score': team_data.get('Compliance_Score', 0),
                'Quality_Security_Score': team_data.get('Quality_Security_Score', 0),
                'Adoption_Score': team_data.get('Adoption_Score', 0)
            }
            
            # Generate recommendations
            recommendations = rec_engine.generate_recommendations(scores)
            
            if recommendations:
                st.markdown(rec_engine.format_recommendations(recommendations))
            else:
                st.success("🎉 Great job! No critical improvements needed.")
            
            st.markdown("---")
            
            # Quick wins
            st.markdown("### ⚡ Quick Wins")
            quick_wins = rec_engine.get_quick_wins(scores)
            
            if quick_wins:
                for qw in quick_wins:
                    st.markdown(f"- **{qw['title']}**: {qw['description']}")
            else:
                st.info("No quick wins identified - you're doing great!")


# =============================================================================
# Footer
# =============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.5); padding: 20px;">
    DevOps Transformation Platform | Built with ❤️ by the DevOps Team
</div>
""", unsafe_allow_html=True)
