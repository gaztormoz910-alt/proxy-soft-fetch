import json
import re

log_path = r'C:\Users\Bog_1\.gemini\antigravity\brain\39f57b39-3a6d-498d-88a5-e57d62d9c823\.system_generated\logs\transcript_full.jsonl'
with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
last_msg = ''
for line in reversed(lines):
    data = json.loads(line)
    if data.get('type') == 'USER_INPUT' and 'NEW_SOURCES' in data.get('content', ''):
        last_msg = data.get('content')
        break

# Extract valid proxy source tuples
tuples = re.findall(r"\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)", last_msg)

valid = []
for u, p in tuples:
    if u.startswith('http'):
        valid.append(f"    ('{u}', '{p}'),\n")

# Check for comprehensions
comps = []
for line in last_msg.split('\n'):
    if 'extend([(' in line and 'for i in range' in line:
        comps.append(line.strip() + '\n')

with open('c:\\Users\\Bog_1\\OneDrive\\Desktop\\Fetch Free Proxy\\to_append.txt', 'w', encoding='utf-8') as f:
    f.writelines(valid)
    f.writelines(comps)

print(f"Extracted {len(valid)} static sources and {len(comps)} generators.")
