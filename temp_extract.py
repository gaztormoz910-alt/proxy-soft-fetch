SOURCES = [
    # ── ИЗ СТАРОГО СПИСКА (РАБОЧИЕ API И САЙТЫ) ───────────────
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all', 'http'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all', 'socks4'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all', 'socks5'),
    ('https://api.openproxylist.xyz/http.txt', 'http'),
    ('https://api.openproxylist.xyz/socks4.txt', 'socks4'),
    ('https://api.openproxylist.xyz/socks5.txt', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc', 'http'),
    ('https://free-proxy-list.net/', 'http'),
    ('https://www.sslproxies.org/', 'http'),
    ('https://www.us-proxy.org/', 'http'),

    # ── НОВЫЕ И ЛУЧШИЕ RAW GITHUB-БОТЫ (Из Анализа) ───────────
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt', 'http'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt', 'http'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt', 'socks4'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt', 'socks5'),
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/socks5.txt', 'socks5'),
    
    # ── ДОБАВЛЕННЫЕ ИЗ CHECK_LINKS.TXT ───────────
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt', 'socks5'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/all.txt', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/all.json', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/http.txt', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/https.txt', 'http'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/socks5.txt', 'socks5'),
    
    # ── НОВЫЕ ИСТОЧНИКИ ОТ DEEPSEEK (Проверено на динамичность) ──
    ('https://www.socks-proxy.net/', 'socks5'),
    ('https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/iplocate/free-proxy-list/main/all-proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt', 'socks5'),
    
    # ── НОВЫЕ ИСТОЧНИКИ ОТ DEEPSEEK (Партия 2 - Проверено на динамичность) ──
    ('https://raw.githubusercontent.com/Firmfox/Proxify/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Firmfox/Proxify/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt', 'http'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/noctiro/getproxy/main/file/http.txt', 'http'),
    ('https://raw.githubusercontent.com/noctiro/getproxy/main/file/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/noctiro/getproxy/main/file/socks5.txt', 'socks5'),
    ('https://proxyroller.com/api/proxies?protocol=http&anonymity=elite&limit=100', 'http'),
]

PROXY_RE  = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3}):(\d{1,5})\b')
JSON_IP_FIRST = re.compile(r'(?:"ip"|"host"|"proxy")\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"[^}]*?(?:"port")\s*:\s*"?(\d{1,5})"?', re.IGNORECASE)
JSON_PORT_FIRST = re.compile(r'(?:"port")\s*:\s*"?(\d{1,5})"?[^}]*?(?:"ip"|"host"|"proxy")\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"', re.IGNORECASE)
TABLE_RE  = re.compile(r'<td[^>]*>\s*(\d{1,3}(?:\.\d{1,3}){3})\s*</td>\s*<td[^>]*>\s*(\d{1,5})\s*</td>', re.IGNORECASE | re.DOTALL)

def is_valid(ip: str, port: int) -> bool:
import json
print(json.dumps(SOURCES))
