"""
Comprehensive Audit of all sources in fetch_proxy.py
Audits:
1. GitHub Repositories freshness via GitHub REST API (last push date, archived, deleted)
2. All 1686 Sources accessibility, response status, proxy yield, and error reasons
3. Dynamicity analysis: fresh updating vs stale vs dead/empty
"""

import sys
import os
import re
import json
import time
from datetime import datetime, timezone
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# Add workspace to path
sys.path.insert(0, os.path.abspath('.'))
import fetch_proxy
from fetch_proxy import ProxyUtils, SOURCES

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,text/plain,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
}

# 1. Load GitHub token from settings.json if available
github_token = None
try:
    with open('settings.json', 'r', encoding='utf-8') as f:
        cfg = json.load(f)
        github_token = cfg.get('github_token')
except Exception:
    pass

gh_headers = {'User-Agent': 'ProxyPulse-Auditor'}
if github_token:
    gh_headers['Authorization'] = f'token {github_token}'


def extract_repo_name(url):
    m = re.match(r'https?://raw\.githubusercontent\.com/([^/]+)/([^/]+)/', url)
    if m: return f"{m.group(1)}/{m.group(2)}"
    m2 = re.match(r'https?://cdn\.jsdelivr\.net/gh/([^/@]+)/([^/@]+)', url)
    if m2: return f"{m2.group(1)}/{m2.group(2)}"
    m3 = re.match(r'https?://([^.]+)\.github\.io/([^/]+)/', url)
    if m3: return f"{m3.group(1)}/{m3.group(2)}"
    return None


def audit_github_repo(repo):
    url = f"https://api.github.com/repos/{repo}"
    try:
        r = requests.get(url, headers=gh_headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            pushed_at = data.get('pushed_at')
            updated_at = data.get('updated_at')
            archived = data.get('archived', False)
            default_branch = data.get('default_branch', 'main')
            
            days_ago = -1
            if pushed_at:
                dt = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
                days_ago = (datetime.now(timezone.utc) - dt).days

            return {
                'repo': repo,
                'status': 'OK',
                'pushed_at': pushed_at,
                'days_ago': days_ago,
                'archived': archived,
                'default_branch': default_branch,
                'stars': data.get('stargazers_count', 0),
            }
        elif r.status_code == 404:
            return {'repo': repo, 'status': 'NOT_FOUND_404', 'days_ago': 99999, 'archived': False}
        elif r.status_code == 403:
            return {'repo': repo, 'status': 'RATE_LIMITED_403', 'days_ago': -1, 'archived': False}
        else:
            return {'repo': repo, 'status': f'HTTP_{r.status_code}', 'days_ago': -1, 'archived': False}
    except Exception as e:
        return {'repo': repo, 'status': f'ERROR_{type(e).__name__}', 'days_ago': -1, 'archived': False}


def check_single_source(idx, item):
    url = item[0] if isinstance(item, (tuple, list)) else item
    proto = item[1] if isinstance(item, (tuple, list)) and len(item) > 1 else 'http'
    
    repo = extract_repo_name(url)
    domain = url.split('/')[2] if '://' in url else 'unknown'
    
    result = {
        'id': idx,
        'url': url,
        'domain': domain,
        'protocol': proto,
        'repo': repo,
        'status_code': None,
        'proxies_found': 0,
        'content_length': 0,
        'response_time_ms': 0,
        'last_modified': None,
        'error': None,
    }
    
    t0 = time.time()
    try:
        # Use streaming to avoid downloading multi-megabyte files
        resp = requests.get(url, headers=HEADERS, timeout=12, stream=True, allow_redirects=True)
        result['response_time_ms'] = round((time.time() - t0) * 1000)
        result['status_code'] = resp.status_code
        result['last_modified'] = resp.headers.get('Last-Modified') or resp.headers.get('date')
        
        if resp.status_code == 200:
            chunks = []
            size = 0
            for chunk in resp.iter_content(chunk_size=16384):
                chunks.append(chunk.decode('utf-8', errors='ignore'))
                size += len(chunk)
                if size > 1024 * 1024: # max 1MB
                    break
            content = ''.join(chunks)
            result['content_length'] = len(content)
            
            # Parse proxies using official ProxyUtils
            parsed = ProxyUtils.parse_proxies(content)
            result['proxies_found'] = len(parsed)
        else:
            result['error'] = f"HTTP_{resp.status_code}"
    except requests.exceptions.Timeout:
        result['response_time_ms'] = round((time.time() - t0) * 1000)
        result['error'] = 'TIMEOUT'
    except requests.exceptions.SSLError:
        result['response_time_ms'] = round((time.time() - t0) * 1000)
        result['error'] = 'SSL_ERROR'
    except requests.exceptions.ConnectionError:
        result['response_time_ms'] = round((time.time() - t0) * 1000)
        result['error'] = 'CONN_ERROR'
    except Exception as e:
        result['response_time_ms'] = round((time.time() - t0) * 1000)
        result['error'] = f"ERR_{type(e).__name__}"
        
    return result


def main():
    print("=" * 80)
    print("STARTING FULL AUDIT OF ALL SOURCES IN fetch_proxy.py")
    print(f"Total sources in SOURCES: {len(SOURCES)}")
    print("=" * 80)
    
    # Extract unique repos
    all_repos = set()
    for item in SOURCES:
        u = item[0] if isinstance(item, (tuple, list)) else item
        r = extract_repo_name(u)
        if r: all_repos.add(r)
        
    print(f"\n[PHASE 1] Checking {len(all_repos)} unique GitHub repositories via API...")
    repo_audit = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        fmap = {ex.submit(audit_github_repo, r): r for r in all_repos}
        done = 0
        for fut in as_completed(fmap):
            done += 1
            res = fut.result()
            repo_audit[res['repo']] = res
            if done % 20 == 0 or done == len(all_repos):
                print(f"  GitHub Repos checked: {done}/{len(all_repos)}")

    # Classify repos by freshness:
    # Highly active: updated within 7 days
    # Active: updated within 30 days
    # Stale: updated 31 - 90 days
    # Dead / Abandoned: > 90 days, or 404, or archived
    repo_categories = {
        'FRESH_7D': [],
        'ACTIVE_30D': [],
        'STALE_90D': [],
        'ABANDONED_OLD': [],
        'ARCHIVED': [],
        'NOT_FOUND_404': [],
        'ERROR': []
    }
    
    for r, info in repo_audit.items():
        st = info['status']
        if st == 'NOT_FOUND_404':
            repo_categories['NOT_FOUND_404'].append(info)
        elif info.get('archived'):
            repo_categories['ARCHIVED'].append(info)
        elif st == 'OK':
            d = info['days_ago']
            if 0 <= d <= 7:
                repo_categories['FRESH_7D'].append(info)
            elif 7 < d <= 30:
                repo_categories['ACTIVE_30D'].append(info)
            elif 30 < d <= 90:
                repo_categories['STALE_90D'].append(info)
            else:
                repo_categories['ABANDONED_OLD'].append(info)
        else:
            repo_categories['ERROR'].append(info)

    print("\n--- GITHUB REPOSITORIES AUDIT RESULTS ---")
    print(f"  Fresh (< 7 days):        {len(repo_categories['FRESH_7D'])}")
    print(f"  Active (7-30 days):      {len(repo_categories['ACTIVE_30D'])}")
    print(f"  Stale (30-90 days):      {len(repo_categories['STALE_90D'])}")
    print(f"  Abandoned (> 90 days):   {len(repo_categories['ABANDONED_OLD'])}")
    print(f"  Archived:                {len(repo_categories['ARCHIVED'])}")
    print(f"  Deleted (404):           {len(repo_categories['NOT_FOUND_404'])}")

    print(f"\n[PHASE 2] Checking all {len(SOURCES)} URLs for network availability & proxy yield...")
    print("Testing with 25 concurrent threads...")
    
    url_results = []
    t_start = time.time()
    with ThreadPoolExecutor(max_workers=25) as ex:
        fmap = {ex.submit(check_single_source, idx, item): idx for idx, item in enumerate(SOURCES)}
        done = 0
        for fut in as_completed(fmap):
            done += 1
            res = fut.result()
            url_results.append(res)
            if done % 100 == 0 or done == len(SOURCES):
                elapsed = time.time() - t_start
                rate = done / elapsed if elapsed > 0 else 0
                print(f"  Checked: {done}/{len(SOURCES)} ({rate:.1f} urls/sec)")

    # Sort results by ID
    url_results.sort(key=lambda x: x['id'])
    
    # Domain breakdown & URL classifications
    alive_with_proxies = []
    empty_accessible = []
    dead_unreachable = []
    
    domain_stats = defaultdict(lambda: {'total': 0, 'alive': 0, 'empty': 0, 'dead': 0, 'total_proxies': 0})

    for r in url_results:
        dom = r['domain']
        domain_stats[dom]['total'] += 1
        
        # Attach repo freshness info if applicable
        if r['repo'] and r['repo'] in repo_audit:
            r['repo_info'] = repo_audit[r['repo']]
        else:
            r['repo_info'] = None
            
        if r['status_code'] == 200 and r['proxies_found'] > 0:
            alive_with_proxies.append(r)
            domain_stats[dom]['alive'] += 1
            domain_stats[dom]['total_proxies'] += r['proxies_found']
        elif r['status_code'] == 200 and r['proxies_found'] == 0:
            empty_accessible.append(r)
            domain_stats[dom]['empty'] += 1
        else:
            dead_unreachable.append(r)
            domain_stats[dom]['dead'] += 1

    print("\n" + "=" * 80)
    print("OVERALL SUMMARY OF SOURCES HEALTH")
    print("=" * 80)
    print(f"Total sources audited:            {len(url_results)}")
    print(f"1. ALIVE WITH PROXIES (WORKING):   {len(alive_with_proxies)} ({len(alive_with_proxies)/len(url_results)*100:.1f}%)")
    print(f"2. ACCESSIBLE BUT EMPTY (0 PROX): {len(empty_accessible)} ({len(empty_accessible)/len(url_results)*100:.1f}%)")
    print(f"3. DEAD / UNREACHABLE (ERRORS):   {len(dead_unreachable)} ({len(dead_unreachable)/len(url_results)*100:.1f}%)")
    
    # Save full audit JSON
    audit_data = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total_sources': len(url_results),
        'summary': {
            'alive_with_proxies': len(alive_with_proxies),
            'accessible_but_empty': len(empty_accessible),
            'dead_unreachable': len(dead_unreachable),
            'github_fresh_7d': len(repo_categories['FRESH_7D']),
            'github_active_30d': len(repo_categories['ACTIVE_30D']),
            'github_stale_90d': len(repo_categories['STALE_90D']),
            'github_abandoned': len(repo_categories['ABANDONED_OLD']),
            'github_archived': len(repo_categories['ARCHIVED']),
            'github_deleted_404': len(repo_categories['NOT_FOUND_404']),
        },
        'repo_categories': repo_categories,
        'domain_stats': dict(domain_stats),
        'alive_with_proxies': alive_with_proxies,
        'empty_accessible': empty_accessible,
        'dead_unreachable': dead_unreachable,
    }
    
    with open('full_source_audit_2026.json', 'w', encoding='utf-8') as f:
        json.dump(audit_data, f, ensure_ascii=False, indent=2)
        
    print(f"\nSaved full results to full_source_audit_2026.json")
    
    print("\nTop Domains by Proxy Yield:")
    sorted_domains = sorted(domain_stats.items(), key=lambda x: x[1]['total_proxies'], reverse=True)
    for dom, st in sorted_domains[:15]:
        print(f"  {dom:30s} | Total: {st['total']:3d} | Alive: {st['alive']:3d} | Empty: {st['empty']:3d} | Dead: {st['dead']:3d} | Proxies: {st['total_proxies']:6d}")

    print("\nWorst Performing Domains (High Failure/Empty):")
    problem_domains = sorted(domain_stats.items(), key=lambda x: (x[1]['dead'] + x[1]['empty']), reverse=True)
    for dom, st in problem_domains[:15]:
        if st['dead'] + st['empty'] > 0:
            print(f"  {dom:30s} | Total: {st['total']:3d} | Empty: {st['empty']:3d} | Dead: {st['dead']:3d} | Working: {st['alive']:3d}")

if __name__ == '__main__':
    main()
