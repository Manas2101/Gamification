"""
HSBC DevOps Gamification Dashboard
===================================
Enterprise-grade dashboard following HSBC design standards
"""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from streamlit_integration import DashboardDataLoader

# Page config
st.set_page_config(
    page_title="HSBC DevOps Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# HSBC Design System CSS
st.markdown("""
<style>
/* Import HSBC Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700&display=swap');

/* Global Styles */
* {
    font-family: 'Inter', 'Univers Next for HSBC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Remove Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main Container */
.main {
    background: white;
    padding: 0 !important;
}

.stApp {
    background: white;
}

/* HSBC Header */
.hsbc-header {
    background: #1D262C;
    height: 60px;
    padding: 0 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -1rem -1rem 0 -1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.hsbc-logo-container {
    display: flex;
    align-items: center;
    gap: 32px;
}

.hsbc-logo {
    display: flex;
    align-items: center;
    gap: 4px;
}

.hsbc-hexagon {
    width: 28px;
    height: 28px;
    background: white;
    position: relative;
}

.hsbc-hexagon::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 28px;
    height: 14px;
    background: #DB0011;
}

.hsbc-title {
    color: white;
    font-size: 20px;
    font-weight: 500;
    line-height: 28px;
    letter-spacing: 0.35px;
    margin: 0;
}

.hsbc-user {
    display: flex;
    align-items: center;
    gap: 8px;
    color: white;
}

.hsbc-avatar {
    width: 38px;
    height: 38px;
    background: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #1D262C;
    font-size: 16px;
    font-weight: 500;
}

.hsbc-username {
    color: white;
    font-size: 20px;
    font-weight: 500;
    letter-spacing: 0.35px;
}

/* Navigation Tabs */
.hsbc-nav {
    background: white;
    border-bottom: 2px solid #D7D8D6;
    padding: 0 16px;
    margin: 0 -1rem;
    display: flex;
    gap: 0;
}

.hsbc-nav-item {
    padding: 16px;
    font-size: 14px;
    font-weight: 500;
    color: #333333;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
}

.hsbc-nav-item:hover {
    background: #F3F3F3;
}

.hsbc-nav-item.active {
    border-bottom: 2px solid #DB0011;
    margin-bottom: -2px;
}

/* Content Area */
.hsbc-content {
    padding: 24px 16px;
    max-width: 1280px;
    margin: 0 auto;
}

/* Page Header */
.hsbc-page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.hsbc-welcome {
    font-size: 20px;
    color: #333333;
}

.hsbc-welcome-name {
    font-weight: 500;
}

/* Buttons */
.hsbc-btn {
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 500;
    border: none;
    cursor: pointer;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.hsbc-btn-primary {
    background: #DB0011;
    color: white;
}

.hsbc-btn-primary:hover {
    background: #A8000B;
}

.hsbc-btn-secondary {
    background: black;
    color: white;
}

.hsbc-btn-secondary:hover {
    background: #333333;
}

/* Tables */
.hsbc-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 16px;
}

.hsbc-table thead {
    background: #EDEDED;
}

.hsbc-table th {
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
    color: #333333;
    border: 1px solid #D7D8D6;
}

.hsbc-table td {
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 350;
    color: #333333;
    border: 1px solid #D7D8D6;
}

.hsbc-table tbody tr:hover {
    background: #F3F3F3;
}

/* Status Indicators */
.hsbc-status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.hsbc-status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

.hsbc-status-approved {
    background: #00847F;
}

.hsbc-status-progress {
    background: #FFBB33;
}

.hsbc-status-rejected {
    background: #A8000B;
}

.hsbc-status-draft {
    background: #9B9B9B;
}

/* Metric Cards */
.hsbc-metric-card {
    background: white;
    border: 1px solid #EDEDED;
    border-left: 4px solid #DB0011;
    border-radius: 4px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.hsbc-metric-title {
    font-size: 14px;
    font-weight: 500;
    color: #767676;
    margin-bottom: 8px;
}

.hsbc-metric-value {
    font-size: 32px;
    font-weight: 500;
    color: #333333;
}

.hsbc-metric-change {
    font-size: 14px;
    margin-top: 4px;
}

.hsbc-metric-change.positive {
    color: #00847F;
}

.hsbc-metric-change.negative {
    color: #A8000B;
}

/* Dropdown/Select */
.hsbc-select {
    width: 100%;
    padding: 12px 16px;
    font-size: 14px;
    color: #333333;
    background: white;
    border: 1px solid #EDEDED;
    outline: none;
    cursor: pointer;
}

.hsbc-select:focus {
    border-color: #DB0011;
}

/* Section Title */
.hsbc-section-title {
    font-size: 16px;
    font-weight: 500;
    color: #333333;
    margin-bottom: 16px;
}

/* Sub Tabs */
.hsbc-subtabs {
    display: flex;
    gap: 0;
    border-bottom: 2px solid #D7D8D6;
    margin-bottom: 24px;
}

.hsbc-subtab {
    padding: 16px;
    font-size: 14px;
    font-weight: 500;
    color: #333333;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    margin-bottom: -2px;
}

.hsbc-subtab.active {
    border-bottom: 2px solid #DB0011;
}

/* Footer */
.hsbc-footer {
    background: #1D262C;
    color: white;
    padding: 10px 20px;
    text-align: center;
    margin: 40px -1rem -1rem -1rem;
    font-size: 16px;
    font-weight: 400;
}

/* Streamlit Override */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: white;
    border-bottom: 2px solid #D7D8D6;
}

.stTabs [data-baseweb="tab"] {
    background: white;
    color: #333333;
    padding: 16px;
    font-size: 14px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
}

.stTabs [aria-selected="true"] {
    background: white;
    color: #333333;
    border-bottom: 2px solid #DB0011 !important;
}

/* Hide Streamlit elements */
.stDeployButton {display: none;}

/* Charts */
.vega-embed {
    background: white !important;
}

/* DataFrames */
.dataframe {
    font-size: 14px !important;
    font-family: 'Inter', sans-serif !important;
}

.dataframe thead th {
    background: #EDEDED !important;
    color: #333333 !important;
    font-weight: 500 !important;
    padding: 12px !important;
    border: 1px solid #D7D8D6 !important;
}

.dataframe tbody td {
    padding: 12px !important;
    border: 1px solid #D7D8D6 !important;
    color: #333333 !important;
}

.dataframe tbody tr:hover {
    background: #F3F3F3 !important;
}

</style>
""", unsafe_allow_html=True)

# HSBC Header
st.markdown("""
<div class="hsbc-header">
    <div class="hsbc-logo-container">
        <div class="hsbc-logo">
            <div class="hsbc-hexagon"></div>
            <span style="color: white; font-size: 24px; font-weight: 700; letter-spacing: 8px;">HSBC</span>
        </div>
        <div style="width: 1px; height: 28px; background: white;"></div>
        <div class="hsbc-title">DevOps Transformation Dashboard</div>
    </div>
    <div class="hsbc-user">
        <div class="hsbc-avatar">JD</div>
        <span class="hsbc-username">John Doe</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data(ttl=300)
def load_dashboard_data():
    loader = DashboardDataLoader()
    latest_df = loader.load_latest_data()
    history_df = loader.load_all_history()
    return latest_df, history_df

try:
    display_latest_df, display_history = load_dashboard_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Process data
if not display_latest_df.empty:
    display_latest_df = display_latest_df.sort_values('DPI', ascending=False).reset_index(drop=True)
    display_latest_df['Rank'] = range(1, len(display_latest_df) + 1)

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs(['🏁 Dashboard', '🏆 Leaderboard', '🎖️ Badges', '📊 Team Trends'])

# ==================== TAB 1: DASHBOARD ====================
with tab1:
    st.markdown('<div class="hsbc-content">', unsafe_allow_html=True)
    
    # Page Header
    st.markdown("""
    <div class="hsbc-page-header">
        <div class="hsbc-welcome">
            <span class="hsbc-welcome-name">Welcome back,</span> John Doe
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    st.markdown('<div class="hsbc-section-title">📈 Overall Performance</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_dpi = display_latest_df['DPI'].mean() if not display_latest_df.empty else 0
        st.markdown(f"""
        <div class="hsbc-metric-card">
            <div class="hsbc-metric-title">Average DPI</div>
            <div class="hsbc-metric-value">{avg_dpi:.1f}</div>
            <div class="hsbc-metric-change positive">↑ 5.2% from last week</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_teams = len(display_latest_df) if not display_latest_df.empty else 0
        st.markdown(f"""
        <div class="hsbc-metric-card">
            <div class="hsbc-metric-title">Total Teams</div>
            <div class="hsbc-metric-value">{total_teams}</div>
            <div class="hsbc-metric-change">Active teams tracked</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_rf = display_latest_df['RF'].mean() if not display_latest_df.empty else 0
        st.markdown(f"""
        <div class="hsbc-metric-card">
            <div class="hsbc-metric-title">Avg Release Frequency</div>
            <div class="hsbc-metric-value">{avg_rf:.1f}</div>
            <div class="hsbc-metric-change positive">↑ 12.3% from last week</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_lttd = display_latest_df['LTTD'].mean() if not display_latest_df.empty else 0
        st.markdown(f"""
        <div class="hsbc-metric-card">
            <div class="hsbc-metric-title">Avg Lead Time (days)</div>
            <div class="hsbc-metric-value">{avg_lttd:.1f}</div>
            <div class="hsbc-metric-change negative">↓ 8.5% from last week</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Top Performers
    st.markdown('<div class="hsbc-section-title" style="margin-top: 32px;">🏆 Top 5 Performers</div>', unsafe_allow_html=True)
    
    if not display_latest_df.empty:
        top_5 = display_latest_df.head(5)[['Rank', 'Team', 'DPI', 'Tier', 'Stack']]
        
        # Create HTML table
        table_html = '<table class="hsbc-table"><thead><tr>'
        table_html += '<th>Rank</th><th>Team</th><th>DPI Score</th><th>Tier</th><th>Stack</th>'
        table_html += '</tr></thead><tbody>'
        
        for _, row in top_5.iterrows():
            rank_badge = '🥇' if row['Rank'] == 1 else '🥈' if row['Rank'] == 2 else '🥉' if row['Rank'] == 3 else ''
            table_html += f'<tr>'
            table_html += f'<td>{rank_badge} {row["Rank"]}</td>'
            table_html += f'<td><strong>{row["Team"]}</strong></td>'
            table_html += f'<td><strong>{row["DPI"]:.1f}</strong></td>'
            table_html += f'<td>{row["Tier"]}</td>'
            table_html += f'<td>{row["Stack"]}</td>'
            table_html += f'</tr>'
        
        table_html += '</tbody></table>'
        st.markdown(table_html, unsafe_allow_html=True)

# ==================== TAB 2: LEADERBOARD ====================
with tab2:
    st.markdown('<div class="hsbc-content">', unsafe_allow_html=True)
    
    st.markdown('<div class="hsbc-section-title">🏆 Team Rankings</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        stacks = ['All'] + list(display_latest_df['Stack'].unique()) if not display_latest_df.empty else ['All']
        selected_stack = st.selectbox('Filter by Stack', stacks, key='stack_filter')
    
    with col2:
        tiers = ['All'] + list(display_latest_df['Tier'].unique()) if not display_latest_df.empty else ['All']
        selected_tier = st.selectbox('Filter by Tier', tiers, key='tier_filter')
    
    with col3:
        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
        if st.button('🔄 Refresh Data', key='refresh_lb'):
            st.cache_data.clear()
            st.rerun()
    
    # Apply filters
    filtered_df = display_latest_df.copy()
    if selected_stack != 'All':
        filtered_df = filtered_df[filtered_df['Stack'] == selected_stack]
    if selected_tier != 'All':
        filtered_df = filtered_df[filtered_df['Tier'] == selected_tier]
    
    # Display table
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[['Rank', 'Team', 'DPI', 'RF', 'LTTD', 'Tier', 'Stack']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info('No teams match the selected filters.')
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 3: BADGES ====================
with tab3:
    st.markdown('<div class="hsbc-content">', unsafe_allow_html=True)
    
    st.markdown('<div class="hsbc-section-title">🎖️ Achievement Badges</div>', unsafe_allow_html=True)
    
    if not display_latest_df.empty:
        # Badge criteria
        badge_groups = {
            '🚀 Release Champion': display_latest_df[display_latest_df['RF'] >= 20],
            '⚡ Speed Demon': display_latest_df[display_latest_df['LTTD'] <= 1.5],
            '🏆 Excellence Award': display_latest_df[display_latest_df['DPI'] >= 80],
            '📈 Rising Star': display_latest_df[display_latest_df['DPI'].between(60, 79)]
        }
        
        for badge_name, badge_df in badge_groups.items():
            if not badge_df.empty:
                st.markdown(f'### {badge_name}')
                st.markdown(f'**{len(badge_df)} teams** earned this badge')
                
                badge_teams = ', '.join(badge_df['Team'].tolist())
                st.markdown(f'<div style="padding: 12px; background: #F3F3F3; border-left: 4px solid #DB0011; margin-bottom: 16px;">{badge_teams}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 4: TEAM TRENDS ====================
with tab4:
    st.markdown('<div class="hsbc-content">', unsafe_allow_html=True)
    
    st.markdown('<div class="hsbc-section-title">📊 Team Performance Trends</div>', unsafe_allow_html=True)
    
    if not display_latest_df.empty:
        team_list = sorted(display_latest_df['Team'].unique())
        selected_team = st.selectbox('Select Team', team_list, key='team_select')
        
        if selected_team and not display_history.empty:
            team_history = display_history[display_history['Team'] == selected_team].sort_values('Week_Start')
            
            if not team_history.empty:
                # Team metrics
                latest_metrics = team_history.iloc[-1]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric('Current DPI', f"{latest_metrics['DPI']:.1f}")
                with col2:
                    st.metric('Release Frequency', f"{latest_metrics['RF']:.1f}")
                with col3:
                    st.metric('Lead Time', f"{latest_metrics['LTTD']:.1f} days")
                
                # Trend chart
                st.markdown('### DPI Trend Over Time')
                
                chart = alt.Chart(team_history).mark_line(point=True, color='#DB0011').encode(
                    x=alt.X('Week_Start:T', title='Week'),
                    y=alt.Y('DPI:Q', title='DPI Score', scale=alt.Scale(domain=[0, 100])),
                    tooltip=['Week_Start:T', 'DPI:Q', 'RF:Q', 'LTTD:Q']
                ).properties(height=400)
                
                st.altair_chart(chart, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="hsbc-footer">
    Support | © HSBC Bank plc 2026
</div>
""", unsafe_allow_html=True)
