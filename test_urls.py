import re
import requests
from concurrent.futures import ThreadPoolExecutor

SOURCES = [
    # ── ИЗ СТАРОГО СПИСКА (РАБОЧИЕ API И САЙТЫ) ───────────────
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all', 'http'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all', 'socks4'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all', 'socks5'),
    ('https://www.proxyscan.io/api/proxy?limit=5000&format=txt&type=http', 'http'),
    ('https://www.proxyscan.io/api/proxy?limit=5000&format=txt&type=socks5', 'socks5'),
    ('https://www.proxyscan.io/download?type=http', 'http'),
    ('https://www.proxyscan.io/download?type=socks4', 'socks4'),
    ('https://www.proxyscan.io/download?type=socks5', 'socks5'),
    ('https://www.proxy-list.download/api/v1/get?type=http', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=socks4', 'socks4'),
    ('https://www.proxy-list.download/api/v1/get?type=socks5', 'socks5'),
    ('https://api.openproxylist.xyz/http.txt', 'http'),
    ('https://api.openproxylist.xyz/socks4.txt', 'socks4'),
    ('https://api.openproxylist.xyz/socks5.txt', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc', 'http'),
    ('https://free-proxy-list.net/', 'http'),
    ('https://www.sslproxies.org/', 'http'),
    ('https://www.us-proxy.org/', 'http'),
    ('https://spys.one/en/free-proxy-list/', 'http'),
    ('https://hidemy.name/en/proxy-list/', 'http'),

    # ── НОВЫЕ И ЛУЧШИЕ RAW GITHUB-БОТЫ (Из Анализа) ───────────
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt', 'http'),
    ('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt', 'http'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP_RAW.txt', 'http'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt', 'socks4'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt', 'socks5'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt', 'http'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/almroot/proxylist/master/list.txt', 'http'),
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/socks5.txt', 'socks5'),
]

PROXY_RE  = re.compile(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})\b')
JSON_RE   = re.compile(r'"ip"\s*:\s*"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"[^}]*"port"\s*:\s*"?(\d{1,5})"?')
TABLE_RE  = re.compile(r'<td[^>]*>\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*</td>\s*<td[^>]*>\s*(\d{1,5})\s*</td>', re.IGNORECASE | re.DOTALL)

with open('results.txt', 'w', encoding='utf-8') as f:
    f.write("")

def fetch_and_test(url_info):
    url, proto = url_info
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        content = resp.text
        
        matches = {
            'proxy_re': PROXY_RE.findall(content),
            'json_re': JSON_RE.findall(content),
            'table_re': TABLE_RE.findall(content),
        }
        
        counts = [len(matches['proxy_re']), len(matches['json_re']), len(matches['table_re'])]
        total = sum(counts)
        res_str = f"OK   | {url[:80]:<80} | P:{counts[0]:<5} J:{counts[1]:<5} T:{counts[2]:<5} TOT:{total:<5} | Status: {resp.status_code}\n"
        
        # If total is 0 and status is 200, maybe we need to parse it differently
        if total == 0 and resp.status_code == 200:
            res_str += f"--- CONTENT PREVIEW (First 200 chars): {content[:200].replace(chr(10), ' ')}\n"
            
    except Exception as e:
        res_str = f"FAIL | {url[:80]:<80} | {str(e)}\n"

    with open('results.txt', 'a', encoding='utf-8') as f:
        f.write(res_str)

with ThreadPoolExecutor(max_workers=10) as ex:
    ex.map(fetch_and_test, SOURCES)
