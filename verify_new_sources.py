import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
import base64

# Simple proxy regex
PROXY_RE = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3})[:\s,;|"\']+(\d{1,5})\b')

def parse_proxies(content: str):
    # Base64 proxy-list.org
    content = content.replace('\n', '').replace('\r', '').strip()
    if len(content) > 20 and re.match(r'^[A-Za-z0-9+/]+={0,2}$', content):
        try:
            decoded = base64.b64decode(content).decode('utf-8')
            if re.search(r'\d{1,3}\.\d{1,3}\.', decoded) or '://' in decoded:
                content = decoded
        except: pass

    found = set()
    try:
        data = json.loads(content)
        def ext_json(obj, depth=0):
            if depth > 5: return
            if isinstance(obj, dict):
                ip_val = obj.get('ip', obj.get('host', obj.get('exit_ip', '')))
                port_val = obj.get('port', '')
                if ip_val and port_val and str(port_val).isdigit():
                    found.add(f"{str(ip_val).strip()}:{port_val}")
                for k, v in obj.items():
                    if k not in ['geolocation', 'location', 'ip_data', 'asn'] and isinstance(v, (dict, list)):
                        ext_json(v, depth+1)
            elif isinstance(obj, list):
                for item in obj: ext_json(item, depth+1)
        ext_json(data)
        if found: return list(found)
    except: pass

    # Regex fallback
    for match in re.finditer(r'data-ip=["\']([A-Za-z0-9+/=]+)["\'].*?data-port=["\']([A-Za-z0-9+/=]+)["\']', content, re.DOTALL):
        try:
            ip = base64.b64decode(match.group(1)).decode('utf-8').strip()
            port = base64.b64decode(match.group(2)).decode('utf-8').strip()
            found.add(f"{ip}:{port}")
        except: pass
        
    for match in re.finditer(r"Proxy\(['\"]([A-Za-z0-9+/=]+)['\"]\)", content):
        try:
            decoded = base64.b64decode(match.group(1)).decode('utf-8').strip()
            if ':' in decoded:
                ip, port = decoded.split(':', 1)
                found.add(f"{ip}:{port}")
        except: pass

    for match in PROXY_RE.finditer(content):
        ip, port = match.groups()
        found.add(f"{ip}:{port}")
    return list(found)

with open('all_new_sources.json', 'r', encoding='utf-8') as f:
    SOURCES = json.load(f)

# Deduplicate
seen = set()
unique_sources = []
for url, proto in SOURCES:
    if url not in seen:
        seen.add(url)
        unique_sources.append((url, proto))

print(f"Loaded {len(unique_sources)} unique sources to check...")

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def check_source(url, proto):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            proxies = parse_proxies(resp.text)
            return url, proto, True, len(proxies), resp.status_code
        else:
            return url, proto, False, 0, resp.status_code
    except Exception as e:
        return url, proto, False, 0, str(e)

valid_sources = []
total = len(unique_sources)
checked = 0
found_proxies = 0

with ThreadPoolExecutor(max_workers=50) as ex:
    fmap = {ex.submit(check_source, u, p): (u, p) for u, p in unique_sources}
    for fut in as_completed(fmap):
        checked += 1
        u, p, ok, count, status = fut.result()
        if ok and count > 0:
            valid_sources.append((u, p))
            found_proxies += count
            print(f"[{checked}/{total}] [OK] {count} proxies from {u}".encode('utf-8', 'replace').decode('utf-8', 'ignore'))
        else:
            status_str = str(status).encode('utf-8', 'replace').decode('utf-8', 'ignore')
            u_str = str(u).encode('utf-8', 'replace').decode('utf-8', 'ignore')
            print(f"[{checked}/{total}] [FAIL] Status: {status_str} from {u_str}")

print(f"\nVerification complete! Found {len(valid_sources)} working sources yielding {found_proxies} total raw proxies.")
with open('validated_new_sources.json', 'w', encoding='utf-8') as f:
    json.dump(valid_sources, f, indent=2)
