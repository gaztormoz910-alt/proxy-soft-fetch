"""
Comprehensive source checker: checks every proxy source for accessibility,
content quality, and freshness (GitHub last commit date).
"""
import re
import json
import time
import requests
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import sys
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
PROXY_RE = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3})[:\s,;|"\']+(\d{1,5})\b')
JSON_IP = re.compile(r'(?:"ip"|"host"|"proxy")\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"[^}]*?(?:"port")\s*:\s*"?(\d{1,5})"?', re.I)

def extract_github_repo(url):
    """Extract owner/repo from raw.githubusercontent.com or github.io URL"""
    m = re.match(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/', url)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    m = re.match(r'https://cdn\.jsdelivr\.net/gh/([^/]+)/([^/@]+)', url)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    m = re.match(r'https://([^.]+)\.github\.io/([^/]+)/', url)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    return None

def check_github_repo_freshness(repo):
    """Check the last commit/push date of a GitHub repo"""
    try:
        # First try the repo API
        resp = requests.get(f"https://api.github.com/repos/{repo}", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            pushed = data.get('pushed_at', '')
            updated = data.get('updated_at', '')
            archived = data.get('archived', False)
            # Parse the most recent date
            date_str = pushed or updated
            if date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                days_ago = (datetime.now(timezone.utc) - dt).days
                return {
                    'repo': repo,
                    'last_push': pushed,
                    'last_update': updated,
                    'days_ago': days_ago,
                    'archived': archived,
                    'exists': True,
                    'error': None
                }
        elif resp.status_code == 404:
            return {'repo': repo, 'exists': False, 'days_ago': 99999, 'error': '404 - Repo not found', 'archived': False}
        elif resp.status_code == 403:
            return {'repo': repo, 'exists': True, 'days_ago': -1, 'error': 'Rate limited', 'archived': False}
        else:
            return {'repo': repo, 'exists': True, 'days_ago': -1, 'error': f'HTTP {resp.status_code}', 'archived': False}
    except Exception as e:
        return {'repo': repo, 'exists': True, 'days_ago': -1, 'error': str(e), 'archived': False}

def count_proxies(content):
    """Count proxy-like patterns in content"""
    count = 0
    for ip, port in PROXY_RE.findall(content):
        parts = ip.split('.')
        if all(0 <= int(p) <= 255 for p in parts) and 1 <= int(port) <= 65535:
            if ip not in ('0.0.0.0', '127.0.0.1', '255.255.255.255'):
                count += 1
    for ip, port in JSON_IP.findall(content):
        parts = ip.split('.')
        if all(0 <= int(p) <= 255 for p in parts) and 1 <= int(port) <= 65535:
            count += 1
    return count

def check_source(url, proto):
    """Check a single source URL"""
    result = {
        'url': url,
        'protocol': proto,
        'status_code': None,
        'accessible': False,
        'proxy_count': 0,
        'content_length': 0,
        'error': None,
        'response_time_ms': 0,
    }
    try:
        start = time.time()
        resp = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        elapsed = (time.time() - start) * 1000
        result['response_time_ms'] = round(elapsed)
        result['status_code'] = resp.status_code
        
        if resp.status_code == 200:
            result['accessible'] = True
            chunks = []
            size = 0
            for chunk in resp.iter_content(chunk_size=8192):
                chunks.append(chunk.decode('utf-8', errors='ignore'))
                size += len(chunk)
                if size > 512 * 1024:
                    break
            content = ''.join(chunks)
            result['content_length'] = len(content)
            result['proxy_count'] = count_proxies(content)
        else:
            result['error'] = f'HTTP {resp.status_code}'
    except requests.exceptions.Timeout:
        result['error'] = 'Timeout'
    except requests.exceptions.ConnectionError:
        result['error'] = 'Connection Error'
    except Exception as e:
        result['error'] = str(e)[:100]
    return result


# =====================================================
# Import SOURCES from fetch_proxy.py
# =====================================================
sys.path.insert(0, '.')
from fetch_proxy import SOURCES

print(f"Total sources to check: {len(SOURCES)}")
print("=" * 80)

# =====================================================
# PHASE 1: Check all source URLs for accessibility
# =====================================================
print("\n[PHASE 1] Checking all source URLs for accessibility and content...")
print("-" * 80)

# Deduplicate by URL (keep first occurrence)
seen_urls = set()
unique_sources = []
for url, proto in SOURCES:
    if url not in seen_urls:
        seen_urls.add(url)
        unique_sources.append((url, proto))

print(f"Unique URLs to check: {len(unique_sources)}")

results = []
with ThreadPoolExecutor(max_workers=50) as ex:
    fmap = {ex.submit(check_source, url, proto): (url, proto) for url, proto in unique_sources}
    done = 0
    for fut in as_completed(fmap):
        done += 1
        res = fut.result()
        results.append(res)
        status = "OK" if res['accessible'] else "FAIL"
        proxy_info = f"proxies={res['proxy_count']}" if res['accessible'] else res['error']
        if done % 20 == 0 or done == len(unique_sources):
            print(f"  Progress: {done}/{len(unique_sources)}")

# =====================================================
# PHASE 2: Check GitHub repos for freshness
# =====================================================
print("\n[PHASE 2] Checking GitHub repository freshness...")
print("-" * 80)

github_repos = set()
for url, _ in unique_sources:
    repo = extract_github_repo(url)
    if repo:
        github_repos.add(repo)

print(f"Unique GitHub repos to check: {len(github_repos)}")

repo_results = {}
with ThreadPoolExecutor(max_workers=5) as ex:  # GitHub rate limit is strict
    fmap = {ex.submit(check_github_repo_freshness, repo): repo for repo in github_repos}
    done = 0
    for fut in as_completed(fmap):
        done += 1
        res = fut.result()
        repo_results[res['repo']] = res
        if done % 10 == 0 or done == len(github_repos):
            print(f"  Progress: {done}/{len(github_repos)}")
        time.sleep(0.8)  # Avoid GitHub rate limit

# =====================================================
# ANALYSIS & REPORT
# =====================================================
print("\n" + "=" * 80)
print("ANALYSIS REPORT")
print("=" * 80)

# Categorize results
dead_sources = []      # Can't connect at all
empty_sources = []     # Connect but 0 proxies
alive_sources = []     # Connect and have proxies

for r in results:
    if not r['accessible']:
        dead_sources.append(r)
    elif r['proxy_count'] == 0:
        empty_sources.append(r)
    else:
        alive_sources.append(r)

# GitHub repo analysis
dead_repos = []        # Deleted / 404
stale_repos = []       # Not updated in > 90 days
archived_repos = []    # Explicitly archived
active_repos = []      # Updated within 90 days

for repo, info in sorted(repo_results.items()):
    if not info['exists']:
        dead_repos.append(info)
    elif info['archived']:
        archived_repos.append(info)
    elif info['days_ago'] > 90:
        stale_repos.append(info)
    elif info['days_ago'] >= 0:
        active_repos.append(info)

print(f"\n--- URL Accessibility ---")
print(f"  ✅ Alive (with proxies): {len(alive_sources)}")
print(f"  ⚠️  Accessible but EMPTY (0 proxies): {len(empty_sources)}")
print(f"  ❌ Dead / Unreachable: {len(dead_sources)}")

print(f"\n--- GitHub Repo Freshness ---")
print(f"  ✅ Active (updated < 90 days): {len(active_repos)}")
print(f"  ⚠️  Stale (> 90 days no update): {len(stale_repos)}")
print(f"  📦 Archived: {len(archived_repos)}")
print(f"  ❌ Deleted / Not Found: {len(dead_repos)}")

# Detailed report
output = {
    'check_date': datetime.now(timezone.utc).isoformat(),
    'summary': {
        'total_urls': len(unique_sources),
        'alive_with_proxies': len(alive_sources),
        'accessible_but_empty': len(empty_sources),
        'dead_unreachable': len(dead_sources),
        'github_repos_total': len(github_repos),
        'github_active': len(active_repos),
        'github_stale': len(stale_repos),
        'github_archived': len(archived_repos),
        'github_deleted': len(dead_repos),
    },
    'dead_sources': sorted([{'url': r['url'], 'error': r['error'], 'protocol': r['protocol']} for r in dead_sources], key=lambda x: x['url']),
    'empty_sources': sorted([{'url': r['url'], 'protocol': r['protocol'], 'content_length': r['content_length']} for r in empty_sources], key=lambda x: x['url']),
    'stale_repos': sorted([{'repo': r['repo'], 'days_ago': r['days_ago'], 'last_push': r.get('last_push', '')} for r in stale_repos], key=lambda x: -x['days_ago']),
    'archived_repos': [{'repo': r['repo'], 'last_push': r.get('last_push', '')} for r in archived_repos],
    'deleted_repos': [{'repo': r['repo'], 'error': r['error']} for r in dead_repos],
    'active_repos': sorted([{'repo': r['repo'], 'days_ago': r['days_ago'], 'last_push': r.get('last_push', '')} for r in active_repos], key=lambda x: x['days_ago']),
    'alive_sources': sorted([{'url': r['url'], 'proxy_count': r['proxy_count'], 'protocol': r['protocol']} for r in alive_sources], key=lambda x: -x['proxy_count']),
}

# Save detailed report
with open('source_check_report.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 80)
print("DETAILED PROBLEMS")
print("=" * 80)

if dead_sources:
    print(f"\n❌ DEAD / UNREACHABLE SOURCES ({len(dead_sources)}):")
    for r in sorted(dead_sources, key=lambda x: x['url']):
        print(f"  {r['url']}")
        print(f"    Error: {r['error']}")

if empty_sources:
    print(f"\n⚠️  ACCESSIBLE BUT EMPTY SOURCES ({len(empty_sources)}):")
    for r in sorted(empty_sources, key=lambda x: x['url']):
        print(f"  {r['url']}")
        print(f"    Content length: {r['content_length']} bytes, but 0 proxies found")

if dead_repos:
    print(f"\n❌ DELETED GitHub REPOS ({len(dead_repos)}):")
    for r in dead_repos:
        print(f"  https://github.com/{r['repo']} - {r['error']}")

if archived_repos:
    print(f"\n📦 ARCHIVED GitHub REPOS ({len(archived_repos)}):")
    for r in archived_repos:
        print(f"  https://github.com/{r['repo']} - Last push: {r.get('last_push', 'N/A')}")

if stale_repos:
    print(f"\n⚠️  STALE GitHub REPOS (> 90 days) ({len(stale_repos)}):")
    for r in sorted(stale_repos, key=lambda x: -x['days_ago']):
        print(f"  https://github.com/{r['repo']} - {r['days_ago']} days ago (last: {r.get('last_push', 'N/A')})")

print(f"\n✅ ACTIVE GitHub REPOS ({len(active_repos)}):")
for r in sorted(active_repos, key=lambda x: x['days_ago']):
    print(f"  https://github.com/{r['repo']} - {r['days_ago']} days ago")

print(f"\n\nReport saved to: source_check_report.json")
