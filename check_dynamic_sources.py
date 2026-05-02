import re
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

with open(r'c:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy\fetch_proxy.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract from SOURCES list in the code
sources_match = re.search(r'SOURCES\s*=\s*\[(.*?)\]', content, re.DOTALL)
if sources_match:
    urls = re.findall(r"'(https?://[^']+)'", sources_match.group(1))
else:
    urls = []

urls = list(set(urls))

results = []

def check_url(url):
    try:
        start_time = time.time()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url, headers=headers, timeout=10)
        elapsed = time.time() - start_time
        
        status = resp.status_code
        content_len = len(resp.text)
        
        # Check for proxies roughly
        proxies_found = len(re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', resp.text))
        if proxies_found == 0:
            # Maybe it's json
            proxies_found = len(re.findall(r'"ip"\s*:', resp.text))
        
        return {
            'url': url,
            'status': status,
            'len': content_len,
            'proxies': proxies_found,
            'time': round(elapsed, 2)
        }
    except Exception as e:
        return {
            'url': url,
            'status': str(type(e).__name__),
            'len': 0,
            'proxies': 0,
            'time': 0
        }

print(f"Checking {len(urls)} URLs...")
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(check_url, u) for u in urls]
    for future in as_completed(futures):
        res = future.result()
        results.append(res)
        print(f"[{res['status']}] {res['proxies']} proxies - {res['url']}")

# Separate check for GitHub repos update time
github_repos = set()
for url in urls:
    if 'raw.githubusercontent.com' in url:
        parts = url.split('/')
        if len(parts) > 4:
            owner = parts[3]
            repo = parts[4]
            github_repos.add(f"{owner}/{repo}")

print("\nChecking GitHub repos last update time...")
for repo in github_repos:
    try:
        api_url = f"https://api.github.com/repos/{repo}/commits?per_page=1"
        resp = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            date = resp.json()[0]['commit']['committer']['date']
            print(f"{repo}: Last updated {date}")
        else:
            print(f"{repo}: Error {resp.status_code}")
    except Exception as e:
        print(f"{repo}: Error {e}")
