import asyncio
import aiohttp
import sys
import re
from datetime import datetime, timezone

sys.path.insert(0, r'c:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy')
from fetch_proxy import SOURCES

# Regex to extract owner/repo/branch/filepath from raw.githubusercontent.com
GH_REGEX = re.compile(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.*)')

async def check_repo_freshness(session, url, idx):
    match = GH_REGEX.match(url)
    if not match:
        return idx, url, True # Not a github raw url, consider it 'fresh' or handle elsewhere

    owner, repo, branch, filepath = match.groups()
    api_url = f'https://api.github.com/repos/{owner}/{repo}/commits?path={filepath}&page=1&per_page=1'
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        async with session.get(api_url, headers=headers, timeout=10) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data and len(data) > 0:
                    commit_date_str = data[0]['commit']['author']['date']
                    commit_date = datetime.strptime(commit_date_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    days_old = (now - commit_date).days
                    return idx, url, days_old <= 30, days_old
                else:
                    # Repo exists but file not found in commit history
                    return idx, url, False, 9999
            elif resp.status == 404:
                return idx, url, False, 9999
            elif resp.status == 403:
                # Rate limit
                return idx, url, 'RateLimit', 0
            else:
                return idx, url, True, 0 # Default to keep if unknown error
    except Exception as e:
        return idx, url, True, 0

async def main():
    print("Checking GitHub sources freshness...")
    sem = asyncio.Semaphore(20) # Keep concurrency low for github API rate limits
    
    async def bound_check(url, idx):
        async with sem:
            return await check_repo_freshness(session, url, idx)

    async with aiohttp.ClientSession() as session:
        tasks = [bound_check(url, i) for i, (url, proto) in enumerate(SOURCES)]
        results = await asyncio.gather(*tasks)

    dead_count = 0
    ratelimit = 0
    
    dead_urls = []
    
    for idx, url, is_fresh, days_old in results:
        if is_fresh == 'RateLimit':
            ratelimit += 1
        elif not is_fresh:
            dead_count += 1
            dead_urls.append((url, days_old))

    print(f"\nFound {dead_count} DEAD github sources (older than 30 days or 404).")
    if ratelimit > 0:
        print(f"Hit rate limit on {ratelimit} requests. Note: GitHub unauthenticated API limit is 60 req/hr.")
        
    with open('dead_github_sources.txt', 'w') as f:
        for url, days in sorted(dead_urls, key=lambda x: x[1], reverse=True):
            f.write(f"{days} days old: {url}\n")
            
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
