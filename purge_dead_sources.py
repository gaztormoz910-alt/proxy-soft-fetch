import asyncio
import aiohttp
import sys
import re
import ast
from datetime import datetime, timezone

GH_REGEX = re.compile(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.*)')
TIME_REGEX = re.compile(r'<relative-time datetime=\"([^\"]+)\"')

async def check_url(session, url):
    # 1. If it's a Github raw url, check freshness
    match = GH_REGEX.match(url)
    if match:
        owner, repo, branch, filepath = match.groups()
        html_url = f'https://github.com/{owner}/{repo}/commits/{branch}/{filepath}'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        try:
            async with session.get(html_url, headers=headers, timeout=15) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    time_match = TIME_REGEX.search(html)
                    if time_match:
                        commit_date_str = time_match.group(1)
                        commit_date = datetime.strptime(commit_date_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                        now = datetime.now(timezone.utc)
                        days_old = (now - commit_date).days
                        if days_old > 30:
                            return url, 'STALE_GITHUB'
                        else:
                            return url, 'OK'
                    else:
                        # Sometimes Github pages don't have relative-time if there are no commits or repo is empty
                        return url, 'NO_COMMITS_FOUND'
                elif resp.status == 404:
                    return url, 'GITHUB_404'
                elif resp.status == 429:
                    # Rate limit. Let's assume it's OK to avoid accidentally deleting it
                    return url, 'OK'
                else:
                    return url, 'OK'
        except Exception as e:
            return url, 'OK' # Better safe than sorry

    # 2. Not github raw. Just check if it's 404
    try:
        async with session.get(url, timeout=15, allow_redirects=True) as resp:
            if resp.status == 404:
                return url, '404'
            return url, 'OK'
    except asyncio.TimeoutError:
        return url, 'TIMEOUT' # Timeout is fine, keep it
    except Exception as e:
        return url, 'OK' # Keep it if we are not sure

async def main():
    print("Extracting URLs from fetch_proxy.py...")
    with open('c:\\Users\\Bog_1\\OneDrive\\Desktop\\Fetch Free Proxy\\fetch_proxy.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    urls_to_check = []
    # Simple regex to find URLs in string literals inside the file
    url_re = re.compile(r"'(https?://[^']+)'|\"(https?://[^\"]+)\"")
    
    for line in lines:
        if line.strip().startswith('#'):
            continue # Already commented
        if 'SOURCES' in line or 'extend' in line or 'http' in line:
            matches = url_re.findall(line)
            for m in matches:
                url = m[0] if m[0] else m[1]
                # Filter out comprehensions parameters with curly braces e.g. {i}
                if '{' not in url and '}' not in url:
                    urls_to_check.append(url)
                    
    urls_to_check = list(set(urls_to_check))
    print(f"Found {len(urls_to_check)} static URLs to check.")

    print("Checking URLs...")
    sem = asyncio.Semaphore(15) # Keep concurrency low to not anger github HTML endpoints
    
    async def bound_check(url):
        async with sem:
            return await check_url(session, url)

    async with aiohttp.ClientSession() as session:
        tasks = [bound_check(url) for url in urls_to_check]
        results = await asyncio.gather(*tasks)

    dead_urls = set()
    stats = {}
    for url, status in results:
        stats[status] = stats.get(status, 0) + 1
        if status in ['404', 'GITHUB_404', 'STALE_GITHUB', 'NO_COMMITS_FOUND']:
            dead_urls.add(url)

    print("\n--- RESULTS ---")
    for st, c in stats.items():
        print(f"{st}: {c}")

    if not dead_urls:
        print("No dead URLs found.")
        return

    print(f"\nCommenting out {len(dead_urls)} dead URLs in fetch_proxy.py...")
    
    modified = 0
    with open('c:\\Users\\Bog_1\\OneDrive\\Desktop\\Fetch Free Proxy\\fetch_proxy.py', 'w', encoding='utf-8') as f:
        for line in lines:
            if line.strip().startswith('#'):
                f.write(line)
                continue
                
            has_dead_url = False
            for dead in dead_urls:
                if f"'{dead}'" in line or f'\"{dead}\"' in line:
                    has_dead_url = True
                    break
                    
            if has_dead_url:
                f.write('# [AUTO-PURGED] ' + line)
                modified += 1
            else:
                f.write(line)
                
    print(f"Successfully commented out {modified} lines!")

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
