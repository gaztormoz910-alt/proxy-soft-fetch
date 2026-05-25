"""
Check GitHub repo freshness via commits API with delay to avoid rate-limiting.
Uses conditional requests and sleep between each to stay under limits.
"""
import re
import time
import json
import requests
from datetime import datetime, timezone

# Extract unique GitHub repos from SOURCES
import sys
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
print(f"Checking {len(repos)} GitHub repos...")

results = []
for i, repo in enumerate(repos):
    time.sleep(1.5)  # Rate limit
    try:
        # Use commits endpoint with per_page=1 to get last commit
        resp = requests.get(
            f"https://api.github.com/repos/{repo}/commits?per_page=1",
            headers={'User-Agent': 'ProxyChecker/1.0', 'Accept': 'application/vnd.github.v3+json'},
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            if data:
                commit_date = data[0]['commit']['committer']['date']
                dt = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
                days = (datetime.now(timezone.utc) - dt).days
                results.append({'repo': repo, 'days_ago': days, 'last_commit': commit_date, 'status': 'ok'})
                status_icon = "OK" if days <= 30 else ("WARN" if days <= 180 else "DEAD")
                print(f"  [{i+1}/{len(repos)}] [{status_icon}] {repo}: {days} days ago ({commit_date})")
            else:
                results.append({'repo': repo, 'days_ago': 99999, 'last_commit': '', 'status': 'empty'})
                print(f"  [{i+1}/{len(repos)}] [EMPTY] {repo}: No commits found")
        elif resp.status_code == 404:
            results.append({'repo': repo, 'days_ago': 99999, 'last_commit': '', 'status': '404'})
            print(f"  [{i+1}/{len(repos)}] [404] {repo}: Repository not found!")
        elif resp.status_code == 403:
            remaining = resp.headers.get('X-RateLimit-Remaining', '?')
            reset = resp.headers.get('X-RateLimit-Reset', '?')
            print(f"  [{i+1}/{len(repos)}] [RATE_LIMITED] {repo}: remaining={remaining}, reset={reset}")
            results.append({'repo': repo, 'days_ago': -1, 'last_commit': '', 'status': 'rate_limited'})
            # Wait longer if rate limited
            time.sleep(10)
        else:
            results.append({'repo': repo, 'days_ago': -1, 'last_commit': '', 'status': f'http_{resp.status_code}'})
            print(f"  [{i+1}/{len(repos)}] [ERR] {repo}: HTTP {resp.status_code}")
    except Exception as e:
        results.append({'repo': repo, 'days_ago': -1, 'last_commit': '', 'status': f'error: {str(e)[:50]}'})
        print(f"  [{i+1}/{len(repos)}] [ERR] {repo}: {e}")

# Summary
print("\n" + "=" * 80)
print("GITHUB FRESHNESS SUMMARY")
print("=" * 80)

active = [r for r in results if r['status'] == 'ok' and r['days_ago'] <= 30]
moderate = [r for r in results if r['status'] == 'ok' and 30 < r['days_ago'] <= 180]
stale = [r for r in results if r['status'] == 'ok' and 180 < r['days_ago'] <= 365]
dead = [r for r in results if r['status'] == 'ok' and r['days_ago'] > 365]
not_found = [r for r in results if r['status'] == '404']
errors = [r for r in results if r['status'] not in ('ok', '404')]

print(f"\n  Active (<= 30 days): {len(active)}")
print(f"  Moderate (30-180 days): {len(moderate)}")
print(f"  Stale (180-365 days): {len(stale)}")
print(f"  Dead (> 365 days / > 1 year): {len(dead)}")
print(f"  404 Not Found: {len(not_found)}")
print(f"  Errors/Rate-limited: {len(errors)}")

if dead:
    print(f"\nDEAD REPOS (> 1 year without update):")
    for r in sorted(dead, key=lambda x: -x['days_ago']):
        print(f"  https://github.com/{r['repo']} - {r['days_ago']} days ago")

if stale:
    print(f"\nSTALE REPOS (6-12 months without update):")
    for r in sorted(stale, key=lambda x: -x['days_ago']):
        print(f"  https://github.com/{r['repo']} - {r['days_ago']} days ago")

if not_found:
    print(f"\n404 NOT FOUND REPOS:")
    for r in not_found:
        print(f"  https://github.com/{r['repo']}")

if moderate:
    print(f"\nMODERATE REPOS (1-6 months):")
    for r in sorted(moderate, key=lambda x: -x['days_ago']):
        print(f"  https://github.com/{r['repo']} - {r['days_ago']} days ago")

if active:
    print(f"\nACTIVE REPOS (<= 30 days):")
    for r in sorted(active, key=lambda x: x['days_ago']):
        print(f"  https://github.com/{r['repo']} - {r['days_ago']} days ago")

# Save results
with open(r'c:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy\github_freshness_report.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nReport saved to github_freshness_report.json")
