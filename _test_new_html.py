import urllib.request
import re

urls = [
    "https://proxylister.com/ru/protocols/http/",
    "https://proxylister.com/ru/countries/north-america/united-states/",
    "https://advanced.name/ru/freeproxy?country=US",
    "https://free.geonix.com/ru/united_states/",
    "https://good-proxies.ru/proxy-list/free/us/"
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
            
            print(f"  P: {len(proxies_p)} | T: {len(proxies_t)}")
    except Exception as e:
        print(f"  Failed: {e}")
