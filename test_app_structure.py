"""
Test that matches app.py structure exactly
"""

import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Structure Test")

# Add CSS block like app.py
st.markdown("""
<style>
* {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.main {
    background: #1a202c;
}
</style>
""", unsafe_allow_html=True)

st.title("App Structure Test")

# Create tabs like app.py
tab1, tab2 = st.tabs(["📊 Overview", "🏆 Test"])

# Create sample data like app.py
data = pd.DataFrame({
    'Team': ['RDH'],
    'DPI': [85.5],
    'RF': [250],
    'LTDD': [1.5]
})

with tab1:
    st.markdown("<h2 style='color:white; text-align:center;'>📊 Overview</h2>", unsafe_allow_html=True)
    
    # Create columns like app.py
    col1, col2, col3 = st.columns(3)
    
    # Calculate values like app.py
    avg_dpi = data['DPI'].mean()
    avg_rf = data['RF'].mean()
    avg_ltdd = data['LTDD'].mean()
    
    with col1:
        avg_dpi_display = f"{avg_dpi:.1f}"
        st.markdown(f"""
        <div style='background: rgba(45,55,72,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>{avg_dpi_display}</div>
            <div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase;'>🎯 Avg DPI</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_rf_display = f"{avg_rf:.0f}"
        st.markdown(f"""
        <div style='background: rgba(45,55,72,0.2); border-radius: 15px; padding: 25px; text-align: center;'>
            <div style='font-size: 48px; font-weight: 800; color: #06b6d4;'>{avg_rf_display}</div>
            <div style='color: rgba(255,255,255,0.7); font-size: 14px;'>⚡ Avg RF</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_ltdd_display = f"{avg_ltdd:.1f}"
        st.markdown(f"""
        <div style='background: rgba(45,55,72,0.2); border-radius: 15px; padding: 25px; text-align: center;'>
            <div style='font-size: 48px; font-weight: 800; color: #10b981;'>{avg_ltdd_display}</div>
            <div style='color: rgba(255,255,255,0.7); font-size: 14px;'>⏱ Avg LTDD</div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("<h2 style='color:white;'>Test Tab</h2>", unsafe_allow_html=True)
    st.write("If Overview tab shows styled cards, structure is fine")
    st.write("If Overview tab shows plain HTML, tabs or CSS block breaks rendering")

st.success("Check the Overview tab - do you see styled metric cards or plain HTML?")
