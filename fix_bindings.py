import sys

with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if '<Control-м>' in line or '<Control-М>' in line:
        continue
    new_lines.append(line)

with open('gui.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
