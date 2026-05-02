import re
import requests

SOURCES = [
    ('https://proxybros.com/free-proxy-list/', 'http'),
    ('https://smallseotools.co.uk/free-proxy-list/', 'http'),
    ('https://free-proxy.cz/en/', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt', 'http'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/all.txt', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/all.json', 'http'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/http.txt', 'http'),
]

PROXY_RE  = re.compile(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})\b')
JSON_RE   = re.compile(r'"ip"\s*:\s*"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"[^}]*"port"\s*:\s*"?(\d{1,5})"?')
TABLE_RE  = re.compile(r'<td[^>]*>\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*</td>\s*<td[^>]*>\s*(\d{1,5})\s*</td>', re.IGNORECASE | re.DOTALL)

def is_valid(ip: str, port: int) -> bool:
    parts = ip.split('.')
    return (len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
            and 1 <= port <= 65535 and ip not in ('0.0.0.0', '127.0.0.1', '255.255.255.255'))

def parse_proxies(content: str) -> list:
    found = set()
    for ip, port in JSON_RE.findall(content):
        if is_valid(ip, int(port)): found.add(f"{ip}:{port}")
    for ip, port in TABLE_RE.findall(content):
        ip = ip.strip()
        if is_valid(ip, int(port)): found.add(f"{ip}:{port}")
    for ip, port in PROXY_RE.findall(content):
        if is_valid(ip, int(port)): found.add(f"{ip}:{port}")
        
    import base64
    for b64_match in re.finditer(r'Base64\.decode\("([A-Za-z0-9+/=]+)"\)', content):
        try:
            ip = base64.b64decode(b64_match.group(1)).decode('utf-8')
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                snippet = content[b64_match.end():b64_match.end()+150]
                port_match = re.search(r'>\s*(\d{2,5})\s*<', snippet)
                if port_match:
                    port = int(port_match.group(1))
                    if is_valid(ip, port):
                        found.add(f"{ip}:{port}")
        except:
            pass
    return list(found)

print(f"{'SOURCE':<80} | {'STATUS':<10} | {'PROXIES':<10}")
print("-" * 110)
for url, _ in SOURCES:
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        status = r.status_code
        proxies = len(parse_proxies(r.text))
        print(f"{url[:80]:<80} | {status:<10} | {proxies:<10}")
    except Exception as e:
        print(f"{url[:80]:<80} | {'ERROR':<10} | {0:<10}")
