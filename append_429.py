import json

with open('validated_new_sources.json', 'r', encoding='utf-8') as f:
    valid_sources = json.load(f)

with open('all_new_sources.json', 'r', encoding='utf-8') as f:
    all_s = json.load(f)

to_add = []
valid_urls = set(u for u, p in valid_sources)
for u, p in all_s:
    if u not in valid_urls and ('geonode.com' in u or 'proxyscrape.com' in u):
        to_add.append((u, p))
        valid_urls.add(u) # Prevent duplicates

with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

end_idx = -1
for i, line in enumerate(lines):
    if line.startswith(']'):
        end_idx = i
        break

if end_idx != -1:
    new_lines = []
    new_lines.append('    # --- RATE LIMITED BUT VALID (GEONODE/PROXYSCRAPE) ---\n')
    for url, proto in to_add:
        new_lines.append(f"    ('{url}', '{proto}'),\n")
    
    lines.insert(end_idx, "".join(new_lines))
    
    with open('fetch_proxy.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"Appended {len(to_add)} rate-limited sources to fetch_proxy.py")
else:
    print("Could not find the end of the SOURCES list")
