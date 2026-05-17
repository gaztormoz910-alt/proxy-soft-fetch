import urllib.request
import re

urls = [
    "https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=1",
    "https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=2",
    "https://proxybros.com/free-proxy-list/1/",
    "https://proxybros.com/free-proxy-list/2/",
]

PROXY_RE = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3})[:\s,;|"\']+(\d{1,5})\b')
TABLE_RE = re.compile(r'<td[^>]*>\s*(\d{1,3}(?:\.\d{1,3}){3})\s*</td>(?:[\s\S]*?</td>\s*){0,3}?<td[^>]*>\s*(\d{1,5})\s*</td>', re.IGNORECASE | re.DOTALL)

for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as response:
            text = response.read().decode('utf-8', errors='ignore')
            clean_text = re.sub(r'<[^>]+>', ' ', text)
            
            proxies_p = PROXY_RE.findall(clean_text)
            proxies_t = TABLE_RE.findall(text)
            
            print(f"URL: {url}")
            print(f"  P: {len(proxies_p)} | T: {len(proxies_t)}")
    except Exception as e:
        print(f"URL: {url} -> Failed: {e}")
