import json
import re

with open('source_check_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

urls_to_remove = set()
# Add dead sources
for s in report.get('dead_sources', []):
    urls_to_remove.add(s['url'])
# Add empty sources
for s in report.get('empty_sources', []):
    urls_to_remove.add(s['url'])

# Add stale repos
with open('stale_repos.txt', 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

stale_repos = set()
for line in lines:
    line = line.strip()
    if line and line not in ('DEAD', 'STALE'):
        stale_repos.add(line)

# Also remove proxy-list.download as it returns 502/429
urls_to_remove.add("https://www.proxy-list.download/api/v1/get?type=http")
urls_to_remove.add("https://www.proxy-list.download/api/v1/get?type=https")
urls_to_remove.add("https://www.proxy-list.download/api/v1/get?type=socks4")
urls_to_remove.add("https://www.proxy-list.download/api/v1/get?type=socks5")

print(f"Total specific URLs to remove: {len(urls_to_remove)}")
print(f"Total stale repos to remove: {len(stale_repos)}")

with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to filter out lines that define sources that are in urls_to_remove or match stale_repos
new_lines = []
removed_count = 0

for line in content.splitlines():
    # Check if line contains a source definition
    m = re.search(r"'(https?://[^']+)'", line)
    if m:
        url = m.group(1)
        # Check specific URL
        if url in urls_to_remove:
            removed_count += 1
            print(f"Removed URL: {url}")
            continue
        
        # Check stale repo
        is_stale = False
        for repo in stale_repos:
            if repo in url:
                is_stale = True
                break
        
        if is_stale:
            removed_count += 1
            print(f"Removed Stale Repo URL: {url}")
            continue
            
    # Also check f-strings like f'https://www.freeproxy.world/...page={p}'
    m_fstr = re.search(r"f'(https?://[^']+)'", line)
    if m_fstr:
        base_url = m_fstr.group(1).replace('{p}', '1') # replace format var to check
        if base_url in urls_to_remove or "freeproxy.world" in base_url or "proxybros.com" in base_url or "proxyhub.me" in base_url or "proxylister.com" in base_url:
            removed_count += 1
            print(f"Removed F-String URL: {line.strip()}")
            continue

    new_lines.append(line)

print(f"\nTotal lines removed: {removed_count}")

with open('fetch_proxy.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines) + '\n')

print("Updated fetch_proxy.py successfully.")
