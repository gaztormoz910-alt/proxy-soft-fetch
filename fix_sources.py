import re

with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')

for i in range(70, min(280, len(lines))):
    line = lines[i]
    if 'all.txt' in line or 'data.txt' in line or 'data.csv' in line or 'proxies.json' in line or 'proxies.txt' in line or 'all-proxies.txt' in line:
        lines[i] = line.replace("'http'", "'all'")

with open('fetch_proxy.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
