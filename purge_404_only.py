import asyncio
import aiohttp
import sys
import re

async def check_url(session, url):
    try:
        # Just do a simple HEAD or GET to see if it's 404
        async with session.get(url, timeout=15, allow_redirects=True) as resp:
            if resp.status == 404:
                return url, '404'
            return url, 'OK'
    except asyncio.TimeoutError:
        return url, 'TIMEOUT'
    except Exception as e:
        return url, 'OK'

async def main():
    with open('c:\\Users\\Bog_1\\OneDrive\\Desktop\\Fetch Free Proxy\\fetch_proxy.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    urls_to_check = []
    url_re = re.compile(r"'(https?://[^']+)'|\"(https?://[^\"]+)\"")
    
    for line in lines:
        if line.strip().startswith('#'):
            continue
        if 'SOURCES' in line or 'extend' in line or 'http' in line:
            matches = url_re.findall(line)
            for m in matches:
                url = m[0] if m[0] else m[1]
                if '{' not in url and '}' not in url:
                    urls_to_check.append(url)
                    
    urls_to_check = list(set(urls_to_check))

    sem = asyncio.Semaphore(50)
    
    async def bound_check(url):
        async with sem:
            return await check_url(session, url)

    async with aiohttp.ClientSession() as session:
        tasks = [bound_check(url) for url in urls_to_check]
        results = await asyncio.gather(*tasks)

    dead_urls = set()
    for url, status in results:
        if status == '404':
            dead_urls.add(url)

    if not dead_urls:
        print("No 404 URLs found.")
        return

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
                f.write('# [404-DEAD] ' + line)
                modified += 1
            else:
                f.write(line)
                
    print(f"Successfully commented out {modified} lines with 404s!")

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
