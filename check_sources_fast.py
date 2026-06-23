import asyncio
import aiohttp
import sys

sys.path.insert(0, r'c:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy')
from fetch_proxy import SOURCES

async def check_url(session, url):
    try:
        async with session.get(url, timeout=10, allow_redirects=True) as resp:
            return resp.status
    except asyncio.TimeoutError:
        return 'Timeout'
    except Exception as e:
        return 'Error'

async def main():
    print(f"Checking {len(SOURCES)} sources...")
    
    # We will use a Semaphore to limit concurrency to avoid overwhelming the OS or network
    sem = asyncio.Semaphore(100)
    
    async def bound_check(url):
        async with sem:
            return await check_url(session, url)

    async with aiohttp.ClientSession() as session:
        tasks = [bound_check(url) for url, proto in SOURCES]
        results = await asyncio.gather(*tasks)

    status_counts = {}
    for r in results:
        status_counts[r] = status_counts.get(r, 0) + 1

    print("\n--- RESULTS ---")
    for status, count in sorted(status_counts.items(), key=lambda x: str(x[0])):
        print(f"Status {status}: {count}")

if __name__ == '__main__':
    # Fix for Windows asyncio
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
