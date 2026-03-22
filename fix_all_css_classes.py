"""
Automated fix: Replace ALL CSS classes with inline styles in app.py
This will fix the plain HTML rendering issue
"""

import re
import shutil
from datetime import datetime

# Backup
backup_file = f"app.py.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy('app.py', backup_file)
print(f"✅ Backup created: {backup_file}")

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define all CSS class replacements
replacements = [
    # Team card
    (r"<div class='team-card'>", 
     "<div style='background: rgba(45,55,72,0.2); border-radius: 15px; padding: 20px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);'>"),
    
    (r"<div class='team-card' style='", 
     "<div style='background: rgba(45,55,72,0.2); border-radius: 15px; padding: 20px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1); "),
    
    # Team name
    (r"<h2 class='team-name'>", 
     "<h2 style='font-size: 24px; font-weight: 700; color: white; margin: 0;'>"),
    
    # Metric bar
    (r"<div class='metric-bar'>", 
     "<div style='width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;'>"),
    
    # Metric fill (keep existing style attribute)
    (r"<div class='metric-fill' style='", 
     "<div style='height: 100%; border-radius: 10px; transition: width 0.3s ease; "),
    
    # Metric card (already fixed in some places, but catch any remaining)
    (r"<div class='metric-card'>", 
     "<div style='background: rgba(45,55,72,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>"),
    
    # Metric value
    (r"<div class='metric-value'>", 
     "<div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>"),
    
    (r"<div class='metric-value' style='", 
     "<div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; "),
    
    # Metric label
    (r"<div class='metric-label'>", 
     "<div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>"),
    
    (r"<div class='metric-label' style='", 
     "<div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; "),
    
    # Achievement icon
    (r"<div class='achievement-icon'>", 
     "<div style='font-size: 48px; margin-bottom: 15px;'>"),
    
    # Badge
    (r"<span class='badge' title='", 
     "<span style='background: linear-gradient(135deg, #8b5cf6, #6366f1); padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin: 0 4px; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.2);' title='"),
    
    # Tier badge
    (r"<div class='tier-badge' style='background:", 
     "<div style='padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 700; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.2); background:"),
    
    # Rank table
    (r"<table class='rank-table'>", 
     "<table style='width: 100%; border-collapse: collapse; margin-top: 20px;'>"),
    
    (r"<th class='rank-table-header'", 
     "<th style='background: rgba(59,130,246,0.2); color: white; padding: 12px; text-align: left; font-weight: 700; border-bottom: 2px solid rgba(59,130,246,0.5);'"),
    
    (r"<tr class='rank-table-row'>", 
     "<tr style='border-bottom: 1px solid rgba(255,255,255,0.1); transition: background 0.2s;'>"),
    
    (r"<td class='rank-table-cell'", 
     "<td style='padding: 12px; color: rgba(255,255,255,0.9);'"),
]

# Apply all replacements
original_content = content
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Count changes
changes = sum(1 for p, _ in replacements if re.search(p, original_content))

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Applied {len(replacements)} replacement patterns")
print(f"✅ Fixed {changes} CSS class instances")
print(f"\n📋 Next steps:")
print(f"1. Restart Streamlit: streamlit run app.py")
print(f"2. Hard refresh browser: Cmd+Shift+R")
print(f"3. If issues, restore: cp {backup_file} app.py")
