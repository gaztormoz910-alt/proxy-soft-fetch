import re
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SOURCES = [
    'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all',
    'https://api.openproxylist.xyz/http.txt',
    'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc',
    'https://free-proxy-list.net/',
    'https://www.sslproxies.org/',
    'https://www.us-proxy.org/',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json',
    'https://www.socks-proxy.net/',
    'https://proxyroller.com/api/proxies?protocol=http&anonymity=elite&limit=100'
]

PROXY_RE  = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3}):(\d{1,5})\b')
JSON_IP_FIRST = re.compile(r'(?:"ip"|"host"|"proxy")\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"[^}]*?(?:"port")\s*:\s*"?(\d{1,5})"?', re.IGNORECASE)
JSON_PORT_FIRST = re.compile(r'(?:"port")\s*:\s*"?(\d{1,5})"?[^}]*?(?:"ip"|"host"|"proxy")\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"', re.IGNORECASE)
TABLE_RE  = re.compile(r'<td[^>]*>\s*(\d{1,3}(?:\.\d{1,3}){3})\s*</td>\s*<td[^>]*>\s*(\d{1,5})\s*</td>', re.IGNORECASE | re.DOTALL)

def is_valid(ip, port):
    parts = ip.split('.')
    return (len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
            and 1 <= int(port) <= 65535 and ip not in ('0.0.0.0', '127.0.0.1', '255.255.255.255'))

def parse_proxies(content):
    found = set()
    for ip, port in JSON_IP_FIRST.findall(content):
        if is_valid(ip, port): found.add(f"{ip}:{port}")
    for port, ip in JSON_PORT_FIRST.findall(content):
        if is_valid(ip, port): found.add(f"{ip}:{port}")
    for ip, port in TABLE_RE.findall(content):
        if is_valid(ip.strip(), port): found.add(f"{ip.strip()}:{port}")
    for ip, port in PROXY_RE.findall(content):
        if is_valid(ip, port): found.add(f"{ip}:{port}")
    return list(found)

for url in SOURCES:
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, verify=False)
        found = parse_proxies(r.text)
        print(f"[{len(found):>4} proxies] {url[:50]}...")
    except Exception as e:
        print(f"[ ERROR ] {url[:50]}... -> {e}")
