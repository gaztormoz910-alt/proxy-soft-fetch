import urllib.request
import re

urls = [
    "https://proxy5.net/ru/free-proxy/usa",
    "https://ru.proxy-tools.com/proxy/us",
    "https://spys.one/ru/proxy-city/Sydney/"
]

PROXY_RE = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3})[:\s,;|"\']+(\d{1,5})\b')
TABLE_RE = re.compile(r'<td[^>]*>\s*(\d{1,3}(?:\.\d{1,3}){3})\s*</td>(?:[\s\S]*?</td>\s*){0,3}?<td[^>]*>\s*(\d{1,5})\s*</td>', re.IGNORECASE | re.DOTALL)

for url in urls:
    print(f"Testing {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as response:
            text = response.read().decode('utf-8', errors='ignore')
            clean_text = re.sub(r'<[^>]+>', ' ', text)
            
            proxies_p = PROXY_RE.findall(clean_text)
            proxies_t = TABLE_RE.findall(text)
            
            print(f"  PROXY_RE extracted: {len(proxies_p)}")
            print(f"  TABLE_RE extracted: {len(proxies_t)}")
            
            # Print a snippet of the table to understand why it failed
            if len(proxies_p) == 0 and len(proxies_t) == 0:
                match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text)
                if match:
                    idx = match.start()
                    print(f"  Snippet: {text[idx:idx+150]}")
    except Exception as e:
        print(f"  Failed: {e}")
