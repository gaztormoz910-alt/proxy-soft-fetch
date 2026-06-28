import asyncio
import aiohttp
import json
import re
from datetime import datetime, timezone
import sys

GITHUB_TOKEN = "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"
GH_REGEX = re.compile(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.*)')
GH_API_REGEX = re.compile(r'https://api\.github\.com/repos/([^/]+)/([^/]+)/contents/(.*)')

MAX_AGE_DAYS = 365 # 1 year

async def check_url(session, url):
    # First check GitHub freshness if applicable
    is_github = False
    owner = repo = filepath = ""
    
    match = GH_REGEX.match(url)
    if match:
        is_github = True
        owner, repo, branch, filepath = match.groups()
    else:
        match2 = GH_API_REGEX.match(url)
        if match2:
            is_github = True
            owner, repo, filepath = match2.groups()
            
    if is_github:
        api_url = f'https://api.github.com/repos/{owner}/{repo}/commits?path={filepath}&page=1&per_page=1'
        headers = {'User-Agent': 'Mozilla/5.0'}
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'
            
        try:
            async with session.get(api_url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and len(data) > 0:
                        commit_date_str = data[0]['commit']['author']['date']
                        commit_date = datetime.strptime(commit_date_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                        now = datetime.now(timezone.utc)
                        days_old = (now - commit_date).days
                        if days_old > MAX_AGE_DAYS:
                            return url, False, f"Dead GitHub: {days_old} days old"
                    else:
                        return url, False, "Dead GitHub: No commit history"
                elif resp.status == 404:
                    return url, False, "Dead GitHub: 404 Not Found"
                elif resp.status == 403:
                    print(f"Rate limited on {url}")
        except Exception as e:
            return url, False, f"GitHub API Error: {str(e)}"
            
    # Then check actual reachability
    try:
        async with session.get(url, timeout=15) as resp:
            if resp.status == 200:
                text = await resp.text()
                # Basic validation: should contain some dots or colons for IPs
                if '.' in text and ':' in text:
                    return url, True, "OK"
                else:
                    return url, False, "No proxies found in content"
            else:
                return url, False, f"HTTP {resp.status}"
    except Exception as e:
        return url, False, f"Fetch Error: {str(e)}"

async def main():
    try:
        with open('extracted_from_dialog.json', 'r', encoding='utf-8') as f:
            urls = json.load(f)
    except FileNotFoundError:
        print("extracted_from_dialog.json not found")
        return

    print(f"Checking {len(urls)} URLs...")
    
    good_urls = []
    bad_urls = []
    
    sem = asyncio.Semaphore(15)
    
    async def bound_check(url):
        async with sem:
            return await check_url(session, url)

    async with aiohttp.ClientSession() as session:
        tasks = [bound_check(u) for u in urls]
        results = await asyncio.gather(*tasks)
        
    for res in results:
        url, is_good, reason = res
        if is_good:
            good_urls.append(url)
        else:
            bad_urls.append((url, reason))
            
    print(f"Good URLs: {len(good_urls)}")
    print(f"Bad URLs: {len(bad_urls)}")
    
    with open('good_dialog_sources.json', 'w', encoding='utf-8') as f:
        json.dump(good_urls, f, indent=4)
        
    with open('bad_dialog_sources.txt', 'w', encoding='utf-8') as f:
        for u, r in bad_urls:
            f.write(f"{u} -> {r}\n")

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
