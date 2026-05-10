import json
import ast

with open('scratch/valid_sources.json', 'r') as f:
    external_valid = json.load(f)['valid']

with open('scratch/valid_sources_internal.json', 'r') as f:
    internal_valid = json.load(f)['valid'] # these are lists of [url, proto]

# Build a master dict of {url: proto}
master = {}

for url, proto in internal_valid:
    master[url] = proto

for url in external_valid:
    if url not in master:
        # Determine protocol
        url_lower = url.lower()
        if 'socks5' in url_lower:
            proto = 'socks5'
        elif 'socks4' in url_lower:
            proto = 'socks4'
        else:
            proto = 'http'
        master[url] = proto

# Now format the SOURCES array
code_lines = ["SOURCES = ["]
for url, proto in master.items():
    code_lines.append(f"    ('{url}', '{proto}'),")
code_lines[-1] = code_lines[-1].rstrip(',') # remove last comma
code_lines.append("]")

with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
new_content = re.sub(r'SOURCES\s*=\s*\[.*?\]', '\n'.join(code_lines), content, flags=re.DOTALL)

with open('fetch_proxy.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Updated fetch_proxy.py with {len(master)} strictly valid, unique endpoints.")
