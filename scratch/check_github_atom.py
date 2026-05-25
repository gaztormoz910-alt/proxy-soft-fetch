import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import sys
import re
import time

sys.path.insert(0, r'c:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy')
from fetch_proxy import SOURCES

def extract_github_repo(url):
    m = re.match(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/', url)
    if m: return f"{m.group(1)}/{m.group(2)}"
    m = re.match(r'https://cdn\.jsdelivr\.net/gh/([^/]+)/([^/@]+)', url)
    if m: return f"{m.group(1)}/{m.group(2)}"
    m = re.match(r'https://([^.]+)\.github\.io/([^/]+)/', url)
    if m: return f"{m.group(1)}/{m.group(2)}"
    return None

repos = set()
for url, _ in SOURCES:
    r = extract_github_repo(url)
    if r: repos.add(r)

repos = sorted(repos)
print(f"Checking {len(repos)} GitHub repos via ATOM feed...")

stale_repos = []
dead_repos = []

headers = {'User-Agent': 'Mozilla/5.0'}

for i, repo in enumerate(repos):
    try:
        # Try main branch first, then master
        for branch in ['main', 'master']:
            feed_url = f"https://github.com/{repo}/commits/{branch}.atom"
            resp = requests.get(feed_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                # Find the first entry's updated field
                updated = root.find('{http://www.w3.org/2005/Atom}updated')
                if updated is not None:
                    dt = datetime.fromisoformat(updated.text.replace('Z', '+00:00'))
                    days = (datetime.now(timezone.utc) - dt).days
                    print(f"  [{i+1}/{len(repos)}] [OK] {repo}: {days} days ago ({branch})")
                    if days > 90:
                        stale_repos.append((repo, days))
                    break
        else:
            if resp.status_code == 404:
                print(f"  [{i+1}/{len(repos)}] [404] {repo}: Not found")
                dead_repos.append(repo)
            else:
                print(f"  [{i+1}/{len(repos)}] [ERR] {repo}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"  [{i+1}/{len(repos)}] [ERR] {repo}: {e}")
    time.sleep(0.5)

print("\n--- RESULTS ---")
print("Dead / 404 Repos:")
for r in dead_repos: print("  " + r)

print("\nStale Repos (> 90 days):")
for r, d in sorted(stale_repos, key=lambda x: -x[1]):
    print(f"  {r}: {d} days ago")

with open(r'c:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy\stale_repos.txt', 'w') as f:
    f.write("DEAD\n")
    for r in dead_repos: f.write(f"{r}\n")
    f.write("\nSTALE\n")
    for r, d in stale_repos: f.write(f"{r}\n")
