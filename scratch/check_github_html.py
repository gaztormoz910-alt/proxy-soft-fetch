import requests
import re
from datetime import datetime, timezone
import time
import sys
import json

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
    if r:
        repos.add(r)

repos = sorted(repos)
print(f"Checking {len(repos)} GitHub repos via HTML scraping...")

results = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

for i, repo in enumerate(repos):
    url = f"https://github.com/{repo}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            # Look for <relative-time datetime="2024-05-18T..."
            m = re.search(r'<relative-time[^>]*datetime="([^"]+)"', resp.text)
            if m:
                commit_date = m.group(1)
                dt = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
                days = (datetime.now(timezone.utc) - dt).days
                results.append({'repo': repo, 'days_ago': days, 'last_commit': commit_date, 'status': 'ok'})
                print(f"  [{i+1}/{len(repos)}] [OK] {repo}: {days} days ago ({commit_date})")
            else:
                results.append({'repo': repo, 'days_ago': 99999, 'last_commit': '', 'status': 'no_date_found'})
                print(f"  [{i+1}/{len(repos)}] [WARN] {repo}: Could not parse date from HTML")
        elif resp.status_code == 404:
            results.append({'repo': repo, 'days_ago': 99999, 'last_commit': '', 'status': '404'})
            print(f"  [{i+1}/{len(repos)}] [404] {repo}: Not found")
        else:
            results.append({'repo': repo, 'days_ago': -1, 'last_commit': '', 'status': f'http_{resp.status_code}'})
            print(f"  [{i+1}/{len(repos)}] [ERR] {repo}: HTTP {resp.status_code}")
    except Exception as e:
         results.append({'repo': repo, 'days_ago': -1, 'last_commit': '', 'status': f'error: {str(e)[:50]}'})
         print(f"  [{i+1}/{len(repos)}] [ERR] {repo}: {e}")
    time.sleep(1)

with open(r'c:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy\scratch\github_html_freshness.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nDone. Results saved.")
