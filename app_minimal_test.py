"""
Minimal test to isolate the HTML rendering issue in app.py
This loads data the same way as app.py but with minimal rendering
"""

import streamlit as st
import pandas as pd
from streamlit_integration import load_dashboard_data

st.set_page_config(layout="wide", page_title="Minimal Test")

st.title("🔬 Minimal App Test - Data Loading + HTML Rendering")

# Load data exactly like app.py does
st.write("**Step 1: Loading data...**")
latest_df, history_df = load_dashboard_data()

st.write(f"✅ Loaded {len(latest_df)} latest rows, {len(history_df)} history rows")

# Test 1: Simple HTML before data
st.markdown("---")
st.subheader("Test 1: HTML Before Data Load")
st.markdown("""
<div style='background: linear-gradient(135deg, #06b6d4, #3b82f6); padding: 20px; border-radius: 10px; color: white;'>
    <h3 style='margin: 0;'>✅ Test 1: This should be styled (rendered before data)</h3>
</div>
""", unsafe_allow_html=True)

# Test 2: HTML after data
st.markdown("---")
st.subheader("Test 2: HTML After Data Load")
st.markdown("""
<div style='background: linear-gradient(135deg, #10b981, #059669); padding: 20px; border-radius: 10px; color: white;'>
    <h3 style='margin: 0;'>✅ Test 2: This should be styled (rendered after data)</h3>
</div>
""", unsafe_allow_html=True)

# Test 3: HTML with data values
st.markdown("---")
st.subheader("Test 3: HTML With Dynamic Data")
if not latest_df.empty:
    first_team = latest_df.iloc[0]['Team']
    first_dpi = latest_df.iloc[0].get('DPI', 0)
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #f59e0b, #d97706); padding: 20px; border-radius: 10px; color: white;'>
        <h3 style='margin: 0;'>✅ Test 3: Dynamic Data</h3>
        <p style='margin: 10px 0 0 0;'>Team: {first_team} | DPI: {first_dpi}</p>
    </div>
    """, unsafe_allow_html=True)

# Test 4: Show actual data
st.markdown("---")
st.subheader("Test 4: Data Preview")
st.dataframe(latest_df.head())

# Test 5: HTML in columns (like app.py does)
st.markdown("---")
st.subheader("Test 5: HTML in Columns (Like App.py)")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background: rgba(45,55,72,0.2); border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1);'>
        <div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>100</div>
        <div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>Test Metric</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background: rgba(45,55,72,0.2); border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1);'>
        <div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>200</div>
        <div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>Another Metric</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background: rgba(45,55,72,0.2); border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1);'>
        <div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>300</div>
        <div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>Third Metric</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.success("""
**Results:**
- If ALL tests show styled HTML: Data loading is NOT the issue
- If tests 1-2 work but 3-5 fail: Dynamic data breaks HTML rendering
- If test 5 fails but others work: Column layout breaks HTML rendering
- If all tests show plain HTML: Same issue as main app (unlikely since diagnostic passed)
""")
