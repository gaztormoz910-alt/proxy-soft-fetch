import json

with open('validated_new_sources.json', 'r', encoding='utf-8') as f:
    valid_sources = json.load(f)

with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

end_idx = -1
for i, line in enumerate(lines):
    if line.startswith(']'):
        end_idx = i
        break

if end_idx != -1:
    new_lines = []
    new_lines.append("    # --- NEW SOCKS5 SOURCES ADDED ---\n")
    for url, proto in valid_sources:
        new_lines.append(f"    ('{url}', '{proto}'),\n")
    
    lines.insert(end_idx, "".join(new_lines))
    
    with open('fetch_proxy.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"Appended {len(valid_sources)} new sources to fetch_proxy.py")
else:
    print("Could not find the end of the SOURCES list")
