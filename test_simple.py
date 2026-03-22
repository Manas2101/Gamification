import streamlit as st

st.set_page_config(page_title="Simple Test")

st.title("Simple HTML Test")

# Test 1: Direct HTML
st.subheader("Test 1: Direct HTML String")
st.markdown("""
<div style='background: linear-gradient(135deg, #06b6d4, #3b82f6); padding: 20px; border-radius: 10px; color: white;'>
    <h3 style='margin: 0;'>Direct HTML - Should be styled</h3>
</div>
""", unsafe_allow_html=True)

# Test 2: F-string with variable
st.subheader("Test 2: F-string with Variable")
value = "100"
st.markdown(f"""
<div style='background: linear-gradient(135deg, #10b981, #059669); padding: 20px; border-radius: 10px; color: white;'>
    <h3 style='margin: 0;'>F-string: {value} - Should be styled</h3>
</div>
""", unsafe_allow_html=True)

# Test 3: Exactly like app.py metric card
st.subheader("Test 3: Exact App.py Style")
avg_dpi_display = "85.5"
st.markdown(f"""
<div style='background: rgba(45,55,72,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
    <div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>{avg_dpi_display}</div>
    <div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>🎯 Avg DPI</div>
</div>
""", unsafe_allow_html=True)

# Test 4: In columns like app.py
st.subheader("Test 4: In Columns")
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style='background: rgba(45,55,72,0.2); border-radius: 15px; padding: 25px; text-align: center;'>
        <div style='font-size: 48px; font-weight: 800; color: #06b6d4;'>100</div>
        <div style='color: rgba(255,255,255,0.7);'>Metric 1</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background: rgba(45,55,72,0.2); border-radius: 15px; padding: 25px; text-align: center;'>
        <div style='font-size: 48px; font-weight: 800; color: #10b981;'>200</div>
        <div style='color: rgba(255,255,255,0.7);'>Metric 2</div>
    </div>
    """, unsafe_allow_html=True)

st.success("If all 4 tests show styled HTML, the issue is elsewhere in app.py")
st.error("If any test shows plain HTML, that's where the problem is")
