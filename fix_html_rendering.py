"""
HTML Rendering Debug & Fix Tool
Diagnoses why Streamlit shows plain HTML instead of rendering it
"""

import streamlit as st
import sys

st.set_page_config(page_title="HTML Rendering Debug", layout="wide")

st.title("🔧 Streamlit HTML Rendering Diagnostics")

# Check 1: Streamlit Version
st.header("1️⃣ Streamlit Version Check")
st.write(f"**Streamlit Version:** {st.__version__}")
if st.__version__ < "1.0.0":
    st.error("⚠️ Streamlit version is too old. Upgrade to 1.0.0+")
else:
    st.success(f"✅ Streamlit {st.__version__} supports HTML rendering")

# Check 2: unsafe_allow_html parameter
st.header("2️⃣ Testing unsafe_allow_html Parameter")

st.subheader("Test A: With unsafe_allow_html=True")
st.markdown("""
<div style='background: linear-gradient(135deg, #06b6d4, #3b82f6); padding: 20px; border-radius: 10px;'>
    <h3 style='color: white; margin: 0;'>✅ This should be styled</h3>
</div>
""", unsafe_allow_html=True)

st.subheader("Test B: Without unsafe_allow_html (should show plain text)")
st.markdown("""
<div style='background: linear-gradient(135deg, #06b6d4, #3b82f6); padding: 20px; border-radius: 10px;'>
    <h3 style='color: white; margin: 0;'>❌ This should be plain text</h3>
</div>
""")

# Check 3: CSS Classes vs Inline Styles
st.header("3️⃣ CSS Classes vs Inline Styles")

st.subheader("Test C: Using CSS Classes (might fail)")
st.markdown("""
<style>
.test-card {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    padding: 20px;
    border-radius: 10px;
    color: white;
}
</style>
<div class='test-card'>
    <h3>CSS Class Test</h3>
    <p>If this is styled with orange gradient, CSS classes work</p>
</div>
""", unsafe_allow_html=True)

st.subheader("Test D: Using Inline Styles (should always work)")
st.markdown("""
<div style='background: linear-gradient(135deg, #10b981, #059669); padding: 20px; border-radius: 10px; color: white;'>
    <h3 style='margin: 0;'>Inline Style Test</h3>
    <p style='margin: 5px 0 0 0;'>If this is styled with green gradient, inline styles work</p>
</div>
""", unsafe_allow_html=True)

# Check 4: Browser Console Errors
st.header("4️⃣ Browser Developer Tools Check")
st.info("""
**Action Required:**
1. Open browser Developer Tools (F12 or Right-click → Inspect)
2. Go to the **Console** tab
3. Look for any errors (red text)
4. Check the **Network** tab for failed CSS/JS loads
5. Report any errors you see below
""")

# Check 5: Streamlit Cache Issues
st.header("5️⃣ Cache Clearing")
st.warning("""
**If you see plain HTML, try these steps:**

**In Browser:**
1. Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
2. Clear cached images and files
3. Hard refresh: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)

**In Streamlit:**
1. Stop the Streamlit server (Ctrl+C)
2. Run: `streamlit cache clear`
3. Delete `.streamlit` folder in your project
4. Restart Streamlit
""")

# Check 6: Special Characters & Encoding
st.header("6️⃣ Encoding & Special Characters Test")
test_html = """
<div style='background: #8b5cf6; padding: 15px; border-radius: 8px; color: white;'>
    <p>Testing special chars: 🚀 ⚡ 💨 🏆</p>
    <p>Testing quotes: "double" 'single'</p>
    <p>Testing symbols: &lt; &gt; &amp;</p>
</div>
"""
st.markdown(test_html, unsafe_allow_html=True)

# Check 7: Streamlit Components Conflict
st.header("7️⃣ Component Conflict Check")
st.write("**Installed Streamlit Components:**")
try:
    import pkg_resources
    streamlit_packages = [pkg for pkg in pkg_resources.working_set if 'streamlit' in pkg.key.lower()]
    for pkg in streamlit_packages:
        st.write(f"- {pkg.key}: {pkg.version}")
except:
    st.write("Could not detect installed packages")

# Check 8: Python Version
st.header("8️⃣ Python Version")
st.write(f"**Python Version:** {sys.version}")

# Diagnostic Summary
st.header("📋 Diagnostic Summary")
st.info("""
**If Tests A, D work but main app shows plain HTML:**
- Problem: CSS classes not loading properly
- **Solution:** Use inline styles everywhere (no CSS classes)

**If all tests show plain HTML:**
- Problem: `unsafe_allow_html=True` not working
- **Solution:** Check Streamlit version, reinstall Streamlit

**If tests work in this file but not in main app:**
- Problem: Specific code in main app interfering
- **Solution:** Check for st.cache decorators, component conflicts
""")

# Quick Fix Generator
st.header("🔧 Quick Fix: Convert CSS Class to Inline Style")
st.write("Paste your HTML with CSS classes, get inline-style version:")

css_class_html = st.text_area("HTML with CSS classes:", 
    value="<div class='metric-card'>\n  <div class='metric-value'>100</div>\n  <div class='metric-label'>Score</div>\n</div>",
    height=150)

if st.button("Convert to Inline Styles"):
    # Simple conversion for common patterns
    inline_html = css_class_html.replace(
        "class='metric-card'",
        "style='background: rgba(45,55,72,0.2); border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1);'"
    ).replace(
        "class='metric-value'",
        "style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'"
    ).replace(
        "class='metric-label'",
        "style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'"
    ).replace(
        "class='achievement-card'",
        "style='border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1);'"
    ).replace(
        'class="metric-card"',
        'style="background: rgba(45,55,72,0.2); border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1);"'
    ).replace(
        'class="achievement-card"',
        'style="border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1);"'
    )
    
    st.code(inline_html, language='html')
    
    st.subheader("Preview:")
    st.markdown(inline_html, unsafe_allow_html=True)

st.divider()
st.success("✅ Run this diagnostic, then report which tests pass/fail for targeted debugging!")
