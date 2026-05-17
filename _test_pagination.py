import urllib.request
import re

urls = [
    "https://proxy5.net/ru/free-proxy/usa",
    "https://ru.proxy-tools.com/proxy/us",
    "https://proxybros.com/ru/free-proxy-list/US/1/",
    "https://proxyhub.me/ru/gb-socks4-proxy-list.html",
    "https://www.freeproxy.world/?country=GB",
    "https://fineproxy.org/ru/free-proxies/oceania/australia/",
    "https://spys.one/ru/proxy-city/Sydney/"
]

for url in urls:
    print(f"Testing {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as response:
            text = response.read().decode('utf-8', errors='ignore')
            ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text)
            print(f"  Status: {response.status}, IPs found: {len(ips)}")
    except Exception as e:
        print(f"  Failed: {e}")
