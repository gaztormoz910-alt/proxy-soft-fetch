import re
import urllib.request
import json
from concurrent.futures import ThreadPoolExecutor

with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find('SOURCES = [')
end_idx = content.find(']', start_idx)
sources_block = content[start_idx:end_idx]

urls = re.findall(r"(https?://[^\'\"]+)", sources_block)

print(f"Total extracted URLs: {len(urls)}")
unique_urls = set(urls)
print(f"Unique URLs: {len(unique_urls)}")
duplicates = len(urls) - len(unique_urls)
if duplicates > 0:
    print(f"Found {duplicates} duplicates!")

repos = set()
for url in unique_urls:
    if 'raw.githubusercontent.com' in url:
        parts = url.split('/')
        if len(parts) >= 5:
            owner = parts[3]
            repo = parts[4]
            repos.add((owner, repo))

print(f"Found {len(repos)} unique GitHub repositories.")

def check_repo(repo_info):
    owner, repo = repo_info
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode('utf-8'))
            return f"{owner}/{repo}", data.get('pushed_at')
    except Exception as e:
        return f"{owner}/{repo}", f"Error: {e}"

stale_repos = []
active_repos = []
with ThreadPoolExecutor(max_workers=5) as ex:
    for name, pushed_at in ex.map(check_repo, repos):
        if pushed_at and not pushed_at.startswith('Error'):
            # simple check if pushed in 2026 or 2024 (we are in 2026 now)
            # wait, pushed_at format is "2024-05-16T...Z"
            if "2026" in pushed_at or "2025" in pushed_at or "2024" in pushed_at: 
                # If they are very old, let's capture them. 
                pass
            active_repos.append((name, pushed_at))
        else:
            stale_repos.append((name, pushed_at))

active_repos.sort(key=lambda x: x[1] if x[1] else "", reverse=True)
print("\n--- Top 5 recently updated repos ---")
for r in active_repos[:5]:
    print(r)

print("\n--- Bottom 5 oldest updated repos ---")
for r in active_repos[-5:]:
    print(r)

print("\n--- Repos with errors ---")
for r in stale_repos:
    print(r)

