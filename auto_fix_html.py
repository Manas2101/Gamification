"""
Automated HTML/CSS Fix Script
Converts all CSS classes to inline styles in app.py
"""

import re
import shutil
from datetime import datetime

# Backup original file
backup_file = f"app.py.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy('app.py', backup_file)
print(f"✅ Backup created: {backup_file}")

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# CSS class to inline style mappings
replacements = {
    # Metric card classes
    r"<div class='metric-card'>": "<div style='background: rgba(45,55,72,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>",
    r'<div class="metric-card">': '<div style="background: rgba(45,55,72,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">',
    
    # Metric value classes
    r"<div class='metric-value'>": "<div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>",
    r'<div class="metric-value">': '<div style="font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;">',
    
    # Metric label classes
    r"<div class='metric-label'>": "<div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>",
    r'<div class="metric-label">': '<div style="color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">',
    
    # Achievement icon classes
    r"<div class='achievement-icon'>": "<div style='font-size: 48px; margin-bottom: 15px;'>",
    r'<div class="achievement-icon">': '<div style="font-size: 48px; margin-bottom: 15px;">',
    
    # Hero header classes
    r"<div class='hero-header'>": "<div style='text-align: center; padding: 40px 20px; background: linear-gradient(135deg, rgba(6,182,212,0.1), rgba(139,92,246,0.1)); border-radius: 20px; margin-bottom: 30px; border: 1px solid rgba(255,255,255,0.1);'>",
    r'<div class="hero-header">': '<div style="text-align: center; padding: 40px 20px; background: linear-gradient(135deg, rgba(6,182,212,0.1), rgba(139,92,246,0.1)); border-radius: 20px; margin-bottom: 30px; border: 1px solid rgba(255,255,255,0.1);">',
    
    # Hero title classes
    r"<h1 class='hero-title'>": "<h1 style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>",
    r'<h1 class="hero-title">': '<h1 style="font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;">',
    
    # Hero subtitle classes
    r"<p class='hero-subtitle'>": "<p style='font-size: 18px; color: rgba(255,255,255,0.8); margin: 0;'>",
    r'<p class="hero-subtitle">': '<p style="font-size: 18px; color: rgba(255,255,255,0.8); margin: 0;">',
    
    # Metric bar classes
    r"<div class='metric-bar'>": "<div style='width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;'>",
    r'<div class="metric-bar">': '<div style="width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;">',
    
    # Metric fill classes
    r"<div class='metric-fill'": "<div style='height: 100%; border-radius: 10px; transition: width 0.3s ease;'",
    r'<div class="metric-fill"': '<div style="height: 100%; border-radius: 10px; transition: width 0.3s ease;"',
}

# Apply replacements
original_content = content
for pattern, replacement in replacements.items():
    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

# Count changes
changes_made = sum(1 for p in replacements.keys() if re.search(p, original_content, re.IGNORECASE))

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Fixed {changes_made} CSS class instances")
print(f"✅ Updated app.py")
print(f"\n📋 Next steps:")
print(f"1. Review changes: git diff app.py")
print(f"2. Test the app: streamlit run app.py")
print(f"3. If issues, restore backup: cp {backup_file} app.py")
