import streamlit as st

st.set_page_config(page_title="HTML Test", layout="wide")

# Test 1: Simple HTML with inline styles
st.markdown("""
<div style='background-color: #1e293b; padding: 20px; border-radius: 10px; color: white;'>
    <h2 style='color: #06b6d4;'>Test 1: Inline Styles</h2>
    <p>If you see this styled (blue heading, dark background), inline styles work.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Test 2: CSS in style block
st.markdown("""
<style>
.test-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    margin: 10px 0;
}
</style>

<div class='test-card'>
    <h2>Test 2: CSS Classes</h2>
    <p>If you see this with purple gradient background, CSS classes work.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Test 3: Native Streamlit components
st.metric("Test 3: Native Metric", "123", "45")
st.success("If you see this green box, native Streamlit components work.")

st.markdown("---")

# Test 4: Check what's actually being rendered
st.code("""
If Tests 1 and 2 show plain text instead of styled boxes:
- Your browser is blocking the HTML rendering
- Streamlit's unsafe_allow_html is not working
- Try a different browser or clear all browser cache

If only Test 2 fails but Test 1 works:
- CSS style blocks are not being processed
- Use inline styles instead of CSS classes
""")
