"""
Comprehensive rendering diagnostic
This will show us EXACTLY what's being rendered and why
"""

import streamlit as st
import sys

st.set_page_config(page_title="Rendering Diagnostic", layout="wide")

st.title("🔬 HTML Rendering Diagnostic")

# Show Streamlit version
st.write(f"**Streamlit Version:** {st.__version__}")
st.write(f"**Python Version:** {sys.version}")

st.divider()

# Test 1: Simplest possible HTML
st.header("Test 1: Simplest HTML")
st.code("""st.markdown("<p style='color: red;'>RED TEXT</p>", unsafe_allow_html=True)""")
st.markdown("<p style='color: red;'>RED TEXT</p>", unsafe_allow_html=True)
st.write("**Expected:** Red colored text")
st.write("**If you see:** `<p style='color: red;'>RED TEXT</p>` then HTML is being escaped")

st.divider()

# Test 2: Without unsafe_allow_html
st.header("Test 2: WITHOUT unsafe_allow_html (should show plain text)")
st.code("""st.markdown("<p style='color: blue;'>BLUE TEXT</p>")""")
st.markdown("<p style='color: blue;'>BLUE TEXT</p>")
st.write("**Expected:** Plain text showing the HTML tags")

st.divider()

# Test 3: Div with background
st.header("Test 3: Div with Background")
st.code("""
st.markdown('''
<div style='background: #10b981; padding: 20px; color: white;'>
    <h3>Green Box</h3>
</div>
''', unsafe_allow_html=True)
""")
st.markdown("""
<div style='background: #10b981; padding: 20px; color: white; border-radius: 10px;'>
    <h3 style='margin: 0;'>Green Box</h3>
</div>
""", unsafe_allow_html=True)
st.write("**Expected:** Green box with white text")

st.divider()

# Test 4: F-string
st.header("Test 4: F-string with Variable")
value = 100
st.code(f"""
value = {value}
st.markdown(f'<div style="color: orange;">Value: {{value}}</div>', unsafe_allow_html=True)
""")
st.markdown(f"<div style='color: orange; font-size: 24px; font-weight: bold;'>Value: {value}</div>", unsafe_allow_html=True)
st.write("**Expected:** Orange text showing 'Value: 100'")

st.divider()

# Test 5: Exact metric card from app.py
st.header("Test 5: Exact Metric Card from app.py")
avg_dpi_display = "85.5"
html_code = f"""
<div style='background: rgba(45,55,72,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
    <div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>{avg_dpi_display}</div>
    <div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>🎯 Avg DPI</div>
</div>
"""

st.code(html_code, language='html')
st.markdown(html_code, unsafe_allow_html=True)
st.write("**Expected:** Semi-transparent card with large gradient number '85.5' and label below")

st.divider()

# Test 6: In columns
st.header("Test 6: In Columns (like app.py)")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style='background: #3b82f6; padding: 20px; border-radius: 10px; color: white; text-align: center;'>
        <div style='font-size: 36px; font-weight: bold;'>100</div>
        <div>Metric 1</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background: #10b981; padding: 20px; border-radius: 10px; color: white; text-align: center;'>
        <div style='font-size: 36px; font-weight: bold;'>200</div>
        <div>Metric 2</div>
    </div>
    """, unsafe_allow_html=True)

st.write("**Expected:** Two colored boxes side by side")

st.divider()

# Results interpretation
st.header("📊 Results Interpretation")

st.info("""
**If Test 1 shows RED TEXT (colored):**
- ✅ HTML rendering works
- ✅ `unsafe_allow_html=True` works
- ✅ Inline styles work

**If Test 1 shows `<p style='color: red;'>RED TEXT</p>` (plain text):**
- ❌ HTML is being escaped
- ❌ Streamlit is not rendering HTML
- 🔧 **Fix:** Reinstall Streamlit or check browser

**If Tests 1-4 work but Test 5 fails:**
- ❌ Complex CSS (gradients, backdrop-filter) not supported
- 🔧 **Fix:** Simplify CSS, remove backdrop-filter

**If Tests 1-5 work but Test 6 fails:**
- ❌ Columns break HTML rendering
- 🔧 **Fix:** Issue with Streamlit columns + HTML

**If ALL tests show plain HTML:**
- ❌ Critical Streamlit issue
- 🔧 **Fix:** Check browser, reinstall Streamlit, try different browser
""")

st.divider()

# Action items
st.header("🎯 Next Steps")

st.success("""
**After reviewing the tests above:**

1. **Screenshot this page** showing which tests pass/fail
2. **Check browser console** (F12 → Console tab) for errors
3. **Try a different browser** (Chrome, Firefox, Safari)
4. **Report back:** Which specific test number fails?

This will tell us EXACTLY where the rendering breaks!
""")
