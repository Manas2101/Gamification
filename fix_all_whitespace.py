"""
Fix ALL leading whitespace in HTML strings in app.py
This is the root cause of plain HTML rendering
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

# Pattern to find st.markdown with HTML that has leading whitespace
# This matches: st.markdown(f"""\n        <div...
pattern = r'(st\.markdown\(f?""")\n\s+(<[^>]+>)'

def fix_whitespace(match):
    """Remove leading whitespace from HTML in st.markdown calls"""
    prefix = match.group(1)  # st.markdown(f"""
    html_start = match.group(2)  # <div...
    return f"{prefix}{html_start}"

# Apply fix
original_content = content
content = re.sub(pattern, fix_whitespace, content)

# Also fix multi-line HTML blocks with consistent indentation
# Find all st.markdown blocks and remove leading whitespace from HTML lines
lines = content.split('\n')
fixed_lines = []
in_markdown = False
markdown_indent = 0

for i, line in enumerate(lines):
    # Detect start of st.markdown with HTML
    if 'st.markdown(' in line and ('"""' in line or "'''" in line):
        in_markdown = True
        markdown_indent = len(line) - len(line.lstrip())
        fixed_lines.append(line)
        continue
    
    # Detect end of st.markdown
    if in_markdown and ('"""' in line or "'''" in line):
        in_markdown = False
        fixed_lines.append(line)
        continue
    
    # Fix HTML lines inside st.markdown
    if in_markdown and line.strip().startswith('<'):
        # Remove leading whitespace, keep the HTML
        fixed_lines.append(line.lstrip())
    else:
        fixed_lines.append(line)

content = '\n'.join(fixed_lines)

# Count changes
changes = len([i for i, (old, new) in enumerate(zip(original_content.split('\n'), content.split('\n'))) if old != new])

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Fixed {changes} lines with leading whitespace")
print(f"\n📋 Next steps:")
print(f"1. Streamlit will auto-reload")
print(f"2. Refresh browser: Cmd+R")
print(f"3. If issues, restore: cp {backup_file} app.py")
