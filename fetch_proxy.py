import re
import socket
import threading
import time
import requests
import argparse
import sys
import os
import csv
import json
import dns.resolver
import dns.reversename
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from typing import List, Set, Tuple, Optional, Dict
import random
import ipaddress
try:
    import maxminddb
except ImportError:
    pass

# ═══════════════════════════════════════════════════════════════
#  РАСШИРЕННЫЙ СПИСОК ИСТОЧНИКОВ (Объединенный)
# ═══════════════════════════════════════════════════════════════
SOURCES = [
    # === HTTP / HTTPS ===
    ('http://htmlweb.ru/analiz/proxy_list.php', 'http'),
    ('https://api.openproxylist.xyz/http.txt', 'http'),
    ('https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all', 'http'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all', 'http'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=json', 'http'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=text', 'http'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text', 'http'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text&protocol=http', 'http'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=json', 'http'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text', 'http'),
    ('https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list/http.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/countries/DE/data.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/countries/FR/data.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/countries/GB/data.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/countries/US/data.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/https/data.txt', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=csv', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=json', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=json&protocol=http', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=json&protocol=https', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&country=DE', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&country=GB', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&country=NL', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&country=RU', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&country=US', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=http', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=https', 'http'),
    ('https://free-proxy-list.net/', 'http'),
    ('https://free-proxy-list.net/anonymous-proxy.html', 'http'),
    ('https://free-proxy-list.net/uk-proxy.html', 'http'),
    ('https://hidemium.io/free-proxy', 'http'),
    ('https://litport.net/api/free-proxy', 'http'),
    ('https://proxy-spider.com/api/proxies.example.txt', 'http'),
    ('https://proxyfreeonly.com/ru/free-proxy-list', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc', 'http'),
    ('https://proxymania.su/free-proxy', 'http'),
    ('https://proxyspace.pro/http.txt', 'http'),
    ('https://proxyspace.pro/https.txt', 'http'),
    ('https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/BreakingTechFr/Proxy_Free/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/http/raw/all.txt', 'http'),
    ('https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt', 'http'),
    ('https://raw.githubusercontent.com/Firmfox/Proxify/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/MrMarble/proxy-list/main/all.txt', 'http'),
    ('https://raw.githubusercontent.com/Noctiro/getproxy/master/file/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Noctiro/getproxy/master/file/https.txt', 'http'),
    ('https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Skillter/ProxyGather/refs/heads/master/proxies/working-proxies-http.txt', 'http'),
    ('https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/https.txt', 'http'),
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/https.txt', 'http'),
    ('https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt', 'http'),
    ('https://raw.githubusercontent.com/berkay-digital/Proxy-Scraper/main/proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/http.txt', 'http'),
    ('https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/http.txt', 'http'),
    ('https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt', 'http'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies.json', 'http'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt', 'http'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.csv', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/BR/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/CA/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/DE/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/FR/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/GB/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/IN/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/JP/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/NL/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/RU/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/SG/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/US/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/https/data.txt', 'http'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt', 'http'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt', 'http'),
    ('https://raw.githubusercontent.com/stormsia/proxy-list/main/working_proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/themiralay/Proxy-List-World/master/data.txt', 'http'),
    ('https://raw.githubusercontent.com/trio666/proxy-checker/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/trio666/proxy-checker/main/https.txt', 'http'),
    ('https://raw.githubusercontent.com/tuanminpay/live-proxy/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt', 'http'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/proxylist.json', 'http'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/proxylist.txt', 'http'),
    ('https://raw.githubusercontent.com/yuceltoluyag/GoodProxy/main/raw.txt', 'http'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt', 'http'),
    ('https://spys.me/proxy.txt', 'http'),
    ('https://sunny9577.github.io/proxy-scraper/generated/http_proxies.txt', 'http'),
    ('https://toproxylab.com/ru/spisok-besplatnyh-proksi-serverov', 'http'),
    ('https://vakhov.github.io/fresh-proxy-list/http.txt', 'http'),
    ('https://vakhov.github.io/fresh-proxy-list/https.txt', 'http'),
    ('https://vakhov.github.io/fresh-proxy-list/proxylist.txt', 'http'),
    ('https://www.google-proxy.net/', 'http'),
    ('https://www.my-proxy.com/free-proxy-list.html', 'http'),
    ('https://www.sslproxies.org/', 'http'),
    ('https://www.us-proxy.org/', 'http'),
    # === SOCKS4 ===
    ('https://api.openproxylist.xyz/socks4.txt', 'socks4'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all', 'socks4'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=json&protocol=socks4', 'socks4'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text&protocol=socks4', 'socks4'),
    ('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.txt', 'socks4'),
    ('https://databay.com/api/v1/proxy-list?format=json&protocol=socks4', 'socks4'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=socks4', 'socks4'),
    ('https://proxyspace.pro/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks4_proxies.txt', 'socks4'),
    ('https://raw.githubusercontent.com/BreakingTechFr/Proxy_Free/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/socks4/raw/all.txt', 'socks4'),
    ('https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Firmfox/Proxify/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Noctiro/getproxy/master/file/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Skillter/ProxyGather/refs/heads/master/proxies/working-proxies-socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt', 'socks4'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt', 'socks4'),
    ('https://raw.githubusercontent.com/trio666/proxy-checker/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/tuanminpay/live-proxy/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks4.txt', 'socks4'),
    ('https://sunny9577.github.io/proxy-scraper/generated/socks4_proxies.txt', 'socks4'),
    ('https://vakhov.github.io/fresh-proxy-list/socks4.txt', 'socks4'),
    ('https://www.socks-proxy.net/', 'socks4'),
    # === SOCKS5 ===
    ('https://api.openproxylist.xyz/socks5.txt', 'socks5'),
    ('https://api.proxyscrape.com/?request=getproxies&proxytype=socks5&timeout=10000&country=all', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all', 'socks5'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=json&protocol=socks5', 'socks5'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text&protocol=socks5', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list/socks5.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt', 'socks5'),
    ('https://databay.com/api/v1/proxy-list?format=json&protocol=socks5', 'socks5'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=socks5', 'socks5'),
    ('https://proxyspace.pro/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies.txt', 'socks5'),
    ('https://raw.githubusercontent.com/BreakingTechFr/Proxy_Free/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/socks5/raw/all.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Noctiro/getproxy/master/file/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Skillter/ProxyGather/refs/heads/master/proxies/working-proxies-socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks5/global/socks5_checked.txt', 'socks5'),
    ('https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt', 'socks5'),
    ('https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt', 'socks5'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt', 'socks5'),
    ('https://raw.githubusercontent.com/trio666/proxy-checker/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/tuanminpay/live-proxy/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt', 'socks5'),
    ('https://spys.me/socks.txt', 'socks5'),
    ('https://sunny9577.github.io/proxy-scraper/generated/socks5_proxies.txt', 'socks5'),
    ('https://vakhov.github.io/fresh-proxy-list/socks5.txt', 'socks5'),
]

# === ПАГИНАЦИЯ (ДИНАМИЧЕСКИЕ ИСТОЧНИКИ) ===
SOURCES.extend([
])
SOURCES.extend([
])
SOURCES.extend([
])
SOURCES.extend([
])
SOURCES.extend([
])
SOURCES.extend([
])
SOURCES.append(('https://good-proxies.ru/proxy-list/free/us/', 'http'))

class ProxyUtils:
    """Утилиты для работы с сетью и парсинга прокси"""
    
    PROXY_RE  = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3})[:\s,;|"\']+(\d{1,5})\b')
    JSON_IP_FIRST = re.compile(r'(?:"ip"|"host"|"proxy")\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"[^}]*?(?:"port")\s*:\s*"?(\d{1,5})"?', re.IGNORECASE)
    JSON_PORT_FIRST = re.compile(r'(?:"port")\s*:\s*"?(\d{1,5})"?[^}]*?(?:"ip"|"host"|"proxy")\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"', re.IGNORECASE)
    TABLE_RE  = re.compile(r'<td[^>]*>\s*(\d{1,3}(?:\.\d{1,3}){3})\s*</td>\s*<td[^>]*>\s*(\d{1,5})\s*</td>', re.IGNORECASE | re.DOTALL)

    @staticmethod
    def is_valid(ip: str, port: int) -> bool:
        parts = ip.split('.')
        return (len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
                and 1 <= port <= 65535 and ip not in ('0.0.0.0', '127.0.0.1', '255.255.255.255'))

    @classmethod
    def parse_proxies(cls, content: str) -> List[str]:
        # Автоматический декод Base64, если весь ответ это зашифрованная строка (часто бывает на GitHub)
        stripped = content.replace('\\n', '').replace('\\r', '').strip()
        if len(stripped) > 20 and re.match(r'^[A-Za-z0-9+/]+={0,2}$', stripped):
            import base64
            try:
                decoded = base64.b64decode(stripped).decode('utf-8')
                content = content + "\\n" + decoded
            except Exception:
                pass

        found = set()
        for ip, port in cls.JSON_IP_FIRST.findall(content):
            if cls.is_valid(ip, int(port)): found.add(f"{ip}:{port}")
        for port, ip in cls.JSON_PORT_FIRST.findall(content):
            if cls.is_valid(ip, int(port)): found.add(f"{ip}:{port}")
        for ip, port in cls.TABLE_RE.findall(content):
            if cls.is_valid(ip.strip(), int(port)): found.add(f"{ip.strip()}:{port}")
        for ip, port in cls.PROXY_RE.findall(content):
            if cls.is_valid(ip, int(port)): found.add(f"{ip}:{port}")
            
        # Парсинг зашифрованных протоколов (VLESS, VMess, SS, Trojan, MTProto и др.)
        URI_RE = re.compile(r'((?:vless|vmess|ss|ssr|trojan|tuic|hysteria2|tg)://[^\s"\'<>]+|https://t\.me/proxy\?[^\s"\'<>]+)', re.IGNORECASE)
        IPV4_CHECK = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}$')
        for uri in URI_RE.findall(content):
            # Принимаем только конфиги с реальным IPv4-адресом (не домены)
            ext_ip, _ = cls.extract_ip_port(uri)
            if IPV4_CHECK.match(ext_ip) and cls.is_valid(ext_ip, 1):
                found.add(uri)
            
        return list(found)

    @staticmethod
    def extract_ip_port(uri: str) -> tuple[str, str]:
        import urllib.parse
        import base64
        import json
        try:
            if uri.startswith("vmess://"):
                b64 = uri[8:]
                pad = len(b64) % 4
                if pad: b64 += "=" * (4 - pad)
                data = json.loads(base64.b64decode(b64).decode('utf-8', errors='ignore'))
                return data.get('add', 'Config'), str(data.get('port', 'N/A'))
            elif uri.startswith("tg://proxy") or uri.startswith("https://t.me/proxy") or uri.startswith("mtproto://"):
                p = urllib.parse.urlparse(uri)
                q = urllib.parse.parse_qs(p.query)
                return q.get("server", ["Config"])[0], q.get("port", ["N/A"])[0]
            else:
                p = urllib.parse.urlparse(uri)
                return p.hostname or "Config", str(p.port) if p.port else "N/A"
        except Exception:
            return "Config", "N/A"

    @staticmethod
    def fetch_url(url: str, timeout: int = 10, via_proxy: Optional[str] = None) -> str:
        headers = {'User-Agent': 'Mozilla/5.0'}
        proxies = {'http': via_proxy, 'https': via_proxy} if via_proxy else None
        try:
            resp = requests.get(url, headers=headers, timeout=timeout, stream=True, proxies=proxies)
            resp.raise_for_status()
            chunks, size = [], 0
            for chunk in resp.iter_content(chunk_size=8192):
                chunks.append(chunk.decode('utf-8', errors='ignore'))
                size += len(chunk)
                if size > 512 * 1024: break
            return ''.join(chunks)
        except Exception: 
            return ''

    @staticmethod
    def _parse_proxy_uri(uri: str) -> tuple[str, str, int]:
        import urllib.parse
        p = urllib.parse.urlparse(uri)
        return p.scheme.lower(), p.hostname or '', p.port or 80

    @staticmethod
    def tcp_ping(ip: str, port: int, timeout: int, via_proxy: Optional[str] = None) -> bool:
        try:
            if via_proxy:
                import socks
                ptype_str, pip, pport = ProxyUtils._parse_proxy_uri(via_proxy)
                if ptype_str == 'http': ptype = socks.HTTP
                elif ptype_str == 'socks4': ptype = socks.SOCKS4
                elif ptype_str == 'socks5': ptype = socks.SOCKS5
                else: ptype = socks.SOCKS5
                with socks.socksocket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(timeout)
                    sock.set_proxy(ptype, pip, int(pport))
                    return sock.connect_ex((ip, port)) == 0
            else:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(timeout)
                    return sock.connect_ex((ip, port)) == 0
        except Exception: 
            return False

    @staticmethod
    def http_check(ip: str, port: int, proto: str, timeout: int, via_proxy: Optional[str] = None) -> bool:
        proxy_url = f"{proto}://{ip}:{port}"
        
        if via_proxy:
            # requests doesn't support connecting to a proxy THROUGH a proxy natively.
            # We must use socks.socksocket monkey patch or a custom Transport.
            # The easiest way is to use socks monkey patch for this check.
            import socks
            ptype_str, pip, pport = ProxyUtils._parse_proxy_uri(via_proxy)
            if ptype_str == 'http': ptype = socks.HTTP
            elif ptype_str == 'socks4': ptype = socks.SOCKS4
            elif ptype_str == 'socks5': ptype = socks.SOCKS5
            else: ptype = socks.SOCKS5
            
            old_socket = socket.socket
            try:
                socks.set_default_proxy(ptype, pip, int(pport))
                socket.socket = socks.socksocket
                resp = requests.get("http://gstatic.com/generate_204", proxies={'http': proxy_url, 'https': proxy_url}, timeout=timeout)
                if resp.status_code == 204: return True
            except Exception:
                pass
            finally:
                socket.socket = old_socket
                socks.set_default_proxy()
            return False
        else:
            proxies = {'http': proxy_url, 'https': proxy_url}
            try:
                resp = requests.get("http://gstatic.com/generate_204", proxies=proxies, timeout=timeout)
                if resp.status_code == 204: return True
            except Exception: 
                pass
            return False

    @classmethod
    def check_proxy(cls, ip: str, port: int, protos: Set[str], timeout: int, via_proxy: Optional[str] = None) -> Set[str]:
        if not cls.tcp_ping(ip, port, timeout, via_proxy=via_proxy): return set()
        working_protos = set()
        for proto in sorted(protos):
            if cls.http_check(ip, port, proto, timeout, via_proxy=via_proxy):
                working_protos.add(proto)
                break
        return working_protos


class RandomProxyGenerator:
    """Генератор рандомных IP:PORT для массовой проверки"""

    RESERVED_NETWORKS = [
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.168.0.0/16'),
        ipaddress.ip_network('127.0.0.0/8'),
        ipaddress.ip_network('224.0.0.0/4'),
        ipaddress.ip_network('240.0.0.0/4'),
        ipaddress.ip_network('0.0.0.0/8'),
        ipaddress.ip_network('100.64.0.0/10'),
        ipaddress.ip_network('169.254.0.0/16'),
        ipaddress.ip_network('198.18.0.0/15'),
        ipaddress.ip_network('192.0.0.0/24'),
        ipaddress.ip_network('192.0.2.0/24'),
        ipaddress.ip_network('198.51.100.0/24'),
        ipaddress.ip_network('203.0.113.0/24'),
        ipaddress.ip_network('233.252.0.0/24')
    ]

    POPULAR_PORTS = {
        'http': [80, 8080, 3128, 8888, 8000, 8443, 443, 8118, 9080, 8081, 8082, 8090, 1080, 3129, 8180, 9090, 8008, 8880, 8123, 8899],
        'socks4': [1080, 4145, 1081, 1085, 4153, 10808, 9050, 9051, 31337, 50000, 4480, 1088, 1180, 5000, 6969],
        'socks5': [1080, 1081, 9050, 9051, 7777, 10808, 1085, 4145, 5555, 50000, 8889, 1088, 4480, 1180, 6969]
    }

    @classmethod
    def _is_reserved(cls, ip_obj: ipaddress.IPv4Address) -> bool:
        for net in cls.RESERVED_NETWORKS:
            if ip_obj in net:
                return True
        return False

    @classmethod
    def generate(cls, count: int, protocol: str) -> Set[str]:
        proxies = set()
        pool = cls.POPULAR_PORTS.get(protocol.lower(), [80, 8080])
        
        while len(proxies) < count:
            ip_int = random.randint(1, 0xFFFFFFFF - 1)
            try:
                ip_obj = ipaddress.IPv4Address(ip_int)
                if cls._is_reserved(ip_obj):
                    continue
                
                # Микс портов: 50% из пула, 50% полностью рандомные
                if random.random() < 0.5:
                    port = random.choice(pool)
                else:
                    port = random.randint(1, 65535)
                    
                proxies.add(f"{ip_obj}:{port}")
            except Exception:
                pass
        return proxies

    @classmethod
    def generate_all(cls, counts: Dict[str, int]) -> Dict[str, Set[str]]:
        results = {}
        for proto, count in counts.items():
            if count > 0:
                results[proto] = cls.generate(count, proto)
        return results


class _ProxyRotator:
    """Потокобезопасная ротация прокси с автоудалением мёртвых"""
    def __init__(self, proxies: List[str], remove_dead: bool = False):
        self._proxies = list(proxies)
        self._index = 0
        self._lock = threading.Lock()
        self._dead = set()
        self._remove_dead = remove_dead

    def next(self) -> Optional[str]:
        with self._lock:
            alive_proxies = [p for p in self._proxies if p not in self._dead]
            if not alive_proxies:
                return None
            
            if self._index >= len(alive_proxies):
                self._index = 0
                
            proxy = alive_proxies[self._index]
            self._index = (self._index + 1) % len(alive_proxies)
            return proxy

    def mark_dead(self, proxy: str):
        if self._remove_dead:
            with self._lock:
                self._dead.add(proxy)

    @property
    def alive_count(self) -> int:
        with self._lock:
            return len([p for p in self._proxies if p not in self._dead])

class ProxyHunter:
    """Главный класс сборщика и валидатора прокси"""
    
    def __init__(self, threads: int = 300, timeout: int = 3, countries: Optional[List[str]] = None, 
                 max_ping: float = 700.0, min_speed: float = 1.0,
                 check_smtp: bool = True, residential_only: bool = False,
                 chain_proxies: Optional[List[str]] = None,
                 chain_auto_remove_dead: bool = False,
                 random_counts: Optional[Dict[str, int]] = None):
        
        self.threads = min(threads, 5000)
        self.timeout = timeout
        
        default_countries = ['US','CA','GB','AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE',
                             'GR','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE']
        self.countries = set(c.upper() for c in (countries or default_countries))
        
        self.max_ping = max_ping
        self.min_speed = min_speed
        self.check_smtp = check_smtp
        self.residential_only = residential_only
        self.chain_proxies = chain_proxies
        self.chain_auto_remove_dead = chain_auto_remove_dead
        self.random_counts = random_counts or {"http": 0, "socks4": 0, "socks5": 0}
        self._rotator = None

        self.proxy_protocols: Dict[str, Set[str]] = defaultdict(set)
        self.live_results: List[str] = []
        self.good_results: List[str] = []
        self._lock = threading.Lock()
        
        self.ip_cache: Dict[str, dict] = {}
        self.db_reader = None
        
        self._pause_event = threading.Event()
        self._cancel_event = threading.Event()

    def pause(self):
        self._pause_event.set()

    def resume(self):
        self._pause_event.clear()

    def cancel(self):
        self._cancel_event.set()
        self.resume()  # Unblock paused threads

    def _wait_if_paused(self) -> bool:
        """Returns True if cancelled, False if ready to continue"""
        while self._pause_event.is_set() and not self._cancel_event.is_set():
            time.sleep(0.5)
        return self._cancel_event.is_set()

    def _get_country(self, ip: str) -> str:
        if hasattr(self, 'db_reader') and self.db_reader:
            try:
                geo_info = self.db_reader.get(ip)
                if geo_info and 'country' in geo_info:
                    return geo_info['country']['iso_code']
            except Exception:
                pass
        return 'Unknown'

    def collect(self):
        print(f"\n[+] ШАГ 1: Сбор из {len(SOURCES)} источников...")
        total_raw, ok_sources = 0, 0
        try:
            from tqdm import tqdm
            pbar = tqdm(total=len(SOURCES), desc="Загрузка")
        except ImportError:
            pbar = None

        with ThreadPoolExecutor(max_workers=min(len(SOURCES), 30)) as ex:
            fmap = {}
            for url, proto in SOURCES:
                via = self._rotator.next() if self._rotator else None
                fmap[ex.submit(ProxyUtils.fetch_url, url, 12, via)] = (url, proto, via)
                
            for fut in as_completed(fmap):
                if self._wait_if_paused(): break
                if self._cancel_event.is_set(): break
                url, proto, via = fmap[fut]
                content = fut.result()
                if not content and via and self._rotator:
                    self._rotator.mark_dead(via)
                if content:
                    ok_sources += 1
                    proxies = ProxyUtils.parse_proxies(content)
                    total_raw += len(proxies)
                    with self._lock:
                        for p in proxies:
                            self.proxy_protocols[p].add(proto)
                if pbar: pbar.update(1)
        
        if pbar: pbar.close()
        print(f"    Ответило источников: {ok_sources}/{len(SOURCES)}")
        print(f"    Собрано (Уникальных IP:PORT): {len(self.proxy_protocols)}")

    def collect_random(self):
        total_random = sum(self.random_counts.values())
        if total_random == 0:
            return
            
        print(f"\n[+] ШАГ 1.5: Генерация рандомных прокси...")
        random_proxies = RandomProxyGenerator.generate_all(self.random_counts)
        count = 0
        with self._lock:
            for proto, proxies in random_proxies.items():
                for p in proxies:
                    self.proxy_protocols[p].add(proto)
                count += len(proxies)
        print(f"    Сгенерировано рандомных: {count}")

    def validate(self):
        if not self.proxy_protocols: return
        candidates = list(self.proxy_protocols.items())
        total = len(candidates)
        print(f"\n[+] ШАГ 2: Базовая проверка {total} прокси на живость...")

        def worker(item: Tuple[str, Set[str]]) -> Optional[Tuple[str, Set[str]]]:
            if self._wait_if_paused(): return None
            if self._cancel_event.is_set(): return None
            ip_port, protos = item
            
            # Пропускаем зашифрованные конфиги напрямую в результаты (они не чекаются обычным TCP-пингом)
            if '://' in ip_port:
                scheme = ip_port.split('://', 1)[0].lower()
                if scheme in ('tg', 'https'): scheme = 'mtproto'
                # Извлекаем IP и проверяем, что это реальный IPv4 (не домен)
                ext_ip, _ = ProxyUtils.extract_ip_port(ip_port)
                if not re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', ext_ip):
                    return None  # Пропускаем конфиги с доменами — нам нужны только реальные IP
                # Фильтр по странам для зашифрованных прокси
                if self.countries:
                    country = self._get_country(ext_ip)
                    if country.upper() not in self.countries:
                        return None
                return (ip_port, {scheme})
                
            ip, port_s = ip_port.split(':')
            via = self._rotator.next() if self._rotator else None
            working = ProxyUtils.check_proxy(ip, int(port_s), protos, self.timeout, via_proxy=via)
            if working: 
                if self._cancel_event.is_set(): return None
                
                # Фильтр по странам — сразу отсеиваем невыбранные страны
                country = self._get_country(ip)
                if self.countries and country.upper() not in self.countries:
                    return None
                
                if self._wait_if_paused(): return None
                
                # Перенесенные из расширенной фильтрации проверки (DNSBL и Ботнет-порты)
                net_info = self._check_rdns_and_bl(ip)
                if net_info.get('dnsbl') or net_info.get('bad_ports'):
                    return None
                return (ip_port, working)
            else:
                if via and self._rotator:
                    # In real scenario we might mark it dead, but many proxies just timeout. 
                    # Only mark dead if we want aggressive removal. We will rely on fetch_url failures for marking dead to be safer.
                    pass
            return None

        try:
            from tqdm import tqdm
            pbar = tqdm(total=total, desc="Проверка")
        except ImportError: 
            pbar = None

        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            futs = [ex.submit(worker, item) for item in candidates]
            for fut in as_completed(futs):
                if self._wait_if_paused(): break
                if self._cancel_event.is_set(): break
                res = fut.result()
                if res:
                    ip_port, working_protos = res
                    with self._lock:
                        for p in sorted(working_protos): 
                            if '://' in ip_port:
                                norm_uri = f"{p}://{ip_port.split('://', 1)[1]}"
                                self.live_results.append(norm_uri)
                                ext_ip, ext_port = ProxyUtils.extract_ip_port(norm_uri)
                                ext_country = self._get_country(ext_ip) if ext_ip != "Config" else "Unknown"
                                if ext_ip != "Config":
                                    if ext_ip not in self.ip_cache: self.ip_cache[ext_ip] = {}
                                    self.ip_cache[ext_ip]['country'] = ext_country
                                print(f"    [REALTIME_NEW_LIVE] {json.dumps({'ip': ext_ip, 'port': ext_port, 'protocol': p.upper(), 'country': ext_country})}")
                            else:
                                self.live_results.append(f"{p}://{ip_port}")
                                ip, port = ip_port.split(':')
                                country = self.ip_cache.get(ip, {}).get('country', '') or self._get_country(ip)
                                if ip not in self.ip_cache: self.ip_cache[ip] = {}
                                self.ip_cache[ip]['country'] = country
                                print(f"    [REALTIME_NEW_LIVE] {json.dumps({'ip': ip, 'port': port, 'protocol': p, 'country': country})}")
                        if len(self.live_results) % 5 == 0 or len(self.live_results) < 10:
                            print(f"    [REALTIME_LIVE] {len(self.live_results)}")
                if pbar: pbar.update(1)

        if pbar: pbar.close()
        self.live_results = sorted(set(self.live_results))
        print(f"    Живых прокси: {len(self.live_results)}")

    def _download_mmdb_if_needed(self):
        db_path = 'GeoLite2-Country.mmdb'
        needs_download = False
        
        if not os.path.exists(db_path):
            needs_download = True
            print(f"\n[!] Локальная база {db_path} не найдена. Скачиваю (около 5MB)...")
        else:
            # Обновляем базу, если она старше 7 дней (604800 секунд)
            if time.time() - os.path.getmtime(db_path) > 604800:
                needs_download = True
                print(f"\n[!] Локальная база {db_path} устарела (старше 7 дней). Обновляю...")
                
        if needs_download:
            url = 'https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb'
            try:
                r = requests.get(url, stream=True, timeout=30)
                r.raise_for_status()
                with open(db_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("[✓] Локальная база успешно скачана/обновлена!")
            except Exception as e:
                print(f"[x] Ошибка обновления базы: {e}")

    def _batch_ip_info(self, ips: Set[str]):
        """Пакетный запрос в ip-api.com для кэширования гео/ISP"""
        chunks = [list(ips)[i:i+100] for i in range(0, len(ips), 100)]
        for chunk in chunks:
            if self._wait_if_paused(): break
            if self._cancel_event.is_set(): break
            try:
                resp = requests.post("http://ip-api.com/batch?fields=query,isp,org,hosting,mobile,countryCode", json=chunk, timeout=10)
                if resp.status_code == 200:
                    for data in resp.json():
                        self.ip_cache[data['query']] = {
                            'country': data.get('countryCode', ''),
                            'datacenter': data.get('hosting', False),
                            'isp': data.get('isp', '').lower()
                        }
            except Exception:
                pass
            time.sleep(4)

    def _check_rdns_and_bl(self, ip: str) -> dict:
        """Кэшируемая проверка RDNS и DNSBL"""
        if ip in self.ip_cache and 'dnsbl' in self.ip_cache[ip]:
            return self.ip_cache[ip]

        fast_resolver = dns.resolver.Resolver()
        fast_resolver.timeout = 1.0
        fast_resolver.lifetime = 1.0

        rdns = ""
        try:
            rev_name = dns.reversename.from_address(ip)
            rdns = str(fast_resolver.resolve(rev_name, 'PTR')[0]).lower()
        except Exception: 
            pass

        dirty_rdns = any(x in rdns for x in ['amazonaws', 'googleusercontent', 'digitalocean', 'hetzner', 'ovh', 'linode'])

        rev_ip = '.'.join(reversed(ip.split('.')))
        bls = [
            'zen.spamhaus.org', 
            'b.barracudacentral.org', 
            'bl.spamcop.net', 
            'cbl.abuseat.org',
            'psbl.surriel.com',
            'dnsbl.sorbs.net'
        ]
        is_bl = False
        for bl in bls:
            if self._cancel_event.is_set(): break
            try:
                answers = fast_resolver.resolve(f'{rev_ip}.{bl}', 'A')
                for rdata in answers:
                    ip_str = rdata.to_text()
                    # Игнорируем ответы вида 127.255.255.X (ошибка Spamhaus: "Public DNS blocked")
                    # Настоящие попадания в блеклист всегда в диапазоне 127.0.0.X или 127.0.1.X
                    if ip_str.startswith('127.0.0.') or ip_str.startswith('127.0.1.'):
                        is_bl = True
                        break
                if is_bl: break
            except Exception: 
                pass

        bad_ports = [22, 23, 3389, 3128]
        has_bad_port = False
        for port in bad_ports:
            if ProxyUtils.tcp_ping(ip, port, timeout=1):
                has_bad_port = True
                break

        if ip not in self.ip_cache: self.ip_cache[ip] = {}
        self.ip_cache[ip].update({'rdns_dirty': dirty_rdns, 'dnsbl': is_bl, 'bad_ports': has_bad_port})
        return self.ip_cache[ip]

    def _run_single_filter(self, item: str) -> Optional[str]:
        """Логика расширенной проверки одного прокси"""
        if self._wait_if_paused(): return None
        if self._cancel_event.is_set(): return None
        proto, ipp = item.split('://', 1)
        
        # Зашифрованные прокси пропускаем как "элитные" без проверок (их нельзя проверить через httpbin)
        if proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
            return item
        
        if ':' not in ipp:
            return None
        ip, port_s = ipp.split(':', 1)
        port = int(port_s)

        ip_info = self.ip_cache.get(ip, {})
        if self.residential_only and ip_info.get('datacenter', True):
            return None

        net_info = self._check_rdns_and_bl(ip)
        if net_info.get('rdns_dirty'):
            return None

        proxy_url = f"{proto}://{ip}:{port}"
        proxies = {'http': proxy_url, 'https': proxy_url}

        try:
            resp = requests.get('http://httpbin.org/headers', proxies=proxies, timeout=self.timeout)
            if resp.status_code == 200:
                headers = str(resp.json().get('headers', {})).lower()
                if 'x-forwarded-for' in headers or 'via' in headers or 'proxy-connection' in headers:
                    return None
        except Exception: 
            return None

        if self._wait_if_paused(): return None

        # 1. Точный замер TCP-пинга до самого прокси (без учета HTTP-оверхеда)
        ping_start = time.time()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3.0)
                sock.connect((ip, port))
            ping_ms = (time.time() - ping_start) * 1000
        except Exception:
            return None
            
        if ping_ms > self.max_ping:
            return None

        # 2. Точный замер чистой пропускной способности (без учета времени подключения)
        try:
            resp = requests.get('https://speed.cloudflare.com/__down?bytes=200000', 
                                proxies=proxies, timeout=self.timeout, stream=True)
            if resp.status_code != 200: return None
            
            dl_start = time.time()
            downloaded = 0
            for chunk in resp.iter_content(chunk_size=32768):
                if chunk: downloaded += len(chunk)
                
            dl_time = time.time() - dl_start
            if dl_time <= 0: dl_time = 0.001
            
            # Перевод байт/с в Мбит/с
            speed_mbps = (downloaded * 8) / dl_time / 1000000
            
            if speed_mbps < self.min_speed:
                return None
        except Exception: 
            return None

        if self._wait_if_paused(): return None

        if self.check_smtp:
            smtp_ok = False
            try:
                if requests.get('http://portquiz.net:25', proxies=proxies, timeout=self.timeout).status_code == 200: 
                    smtp_ok = True
            except Exception: pass
            
            if not smtp_ok:
                try:
                    if requests.get('http://portquiz.net:587', proxies=proxies, timeout=self.timeout).status_code == 200: 
                        smtp_ok = True
                except Exception: pass
            if not smtp_ok: return None

        return item

    def advanced_filter(self):
        if not self.live_results: return
        print(f"\n[+] ШАГ 3: Расширенная фильтрация {len(self.live_results)} прокси...")
        print(f"    [Фильтрация по странам и DNSBL уже пройдена на Шаге 2]")
        
        if self.residential_only and self.live_results:
            residential_ips = set([r.split('://')[1].split(':')[0] for r in self.live_results])
            print(f"    Запрашиваю тип прокси (Residential) для {len(residential_ips)} IP через ip-api...")
            self._batch_ip_info(residential_ips)
        elif not self.residential_only:
            print("    Флаг --residential-only не установлен. Пропускаем долгий опрос ip-api.com!")

        try:
            from tqdm import tqdm
            pbar = tqdm(total=len(self.live_results), desc="Фильтрация")
        except ImportError: 
            pbar = None

        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            futs = [ex.submit(self._run_single_filter, item) for item in self.live_results]
            for fut in as_completed(futs):
                if self._wait_if_paused(): break
                if self._cancel_event.is_set(): break
                res = fut.result()
                if res:
                    with self._lock: 
                        self.good_results.append(res)
                        proto, ipp = res.split('://', 1)
                        if proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                            import json
                            ext_ip, ext_port = ProxyUtils.extract_ip_port(res)
                            ext_country = self.ip_cache.get(ext_ip, {}).get('country') or self._get_country(ext_ip) if ext_ip != "Config" else "Unknown"
                            print(f"    [REALTIME_NEW_ELITE] {json.dumps({'ip': ext_ip, 'port': ext_port, 'protocol': proto.upper(), 'country': ext_country})}")
                        else:
                            ip, port = ipp.split(':')
                            country = self.ip_cache.get(ip, {}).get('country') or self._get_country(ip)
                            import json
                            print(f"    [REALTIME_NEW_ELITE] {json.dumps({'ip': ip, 'port': port, 'protocol': proto, 'country': country})}")
                        if len(self.good_results) % 2 == 0 or len(self.good_results) < 5:
                            print(f"    [REALTIME_ELITE] {len(self.good_results)}")
                if pbar: pbar.update(1)

        if pbar: pbar.close()
        self.good_results = sorted(set(self.good_results))
        print(f"    Годных, прошедших все фильтры: {len(self.good_results)}")

    def _save_category(self, folder_name: str, results_list: List[str], description: str):
        os.makedirs(folder_name, exist_ok=True)
        
        by_proto = defaultdict(list)
        for p in results_list:
            proto, ipp = p.split('://', 1)
            by_proto[proto.lower()].append(p)
            
        with open(os.path.join(folder_name, 'all.txt'), 'w', encoding='utf-8') as f:
            f.write(f"# {description}: {len(results_list)}\n")
            for p in results_list: f.write(p + '\n')
            
        with open(os.path.join(folder_name, 'all.csv'), 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Протокол', 'IP/Config', 'Port', 'Страна'])
            for p in results_list:
                proto, ipp = p.split('://', 1)
                if proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                    ext_ip, ext_port = ProxyUtils.extract_ip_port(p)
                    ext_country = self.ip_cache.get(ext_ip, {}).get('country', 'Unknown') if ext_ip != "Config" else "Unknown"
                    writer.writerow([proto.upper(), ext_ip, ext_port, ext_country])
                else:
                    ip, port = ipp.split(':', 1)
                    country = self.ip_cache.get(ip, {}).get('country', 'Unknown') or 'Unknown'
                    writer.writerow([proto.upper(), ip, port, country])
                
        unique_ips = set()
        for p in results_list:
            proto, ipp = p.split('://', 1)
            if proto.lower() not in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                unique_ips.add(ipp.split(':', 1)[0])
        unique_ips = sorted(unique_ips)
        with open(os.path.join(folder_name, 'all_ips.txt'), 'w', encoding='utf-8') as f:
            f.write(f"# {description} (Только уникальные IP): {len(unique_ips)}\n")
            for ip in unique_ips: f.write(ip + '\n')
                
        for proto, items in by_proto.items():
            with open(os.path.join(folder_name, f'{proto}.txt'), 'w', encoding='utf-8') as f:
                f.write(f"# {description} ({proto.upper()}): {len(items)}\n")
                for p in items: f.write(p + '\n')
                
            with open(os.path.join(folder_name, f'{proto}.csv'), 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Протокол', 'IP/Config', 'Port', 'Страна'])
                for p in items:
                    _, ipp = p.split('://', 1)
                    if proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                        ext_ip, _ = ProxyUtils.extract_ip_port(p)
                        country = self.ip_cache.get(ext_ip, {}).get('country') or self._get_country(ext_ip) if ext_ip != "Config" else "Unknown"
                        writer.writerow([proto.upper(), ipp, 'N/A', country])
                    else:
                        ip, port = ipp.split(':', 1)
                        country = self.ip_cache.get(ip, {}).get('country') or self._get_country(ip)
                        writer.writerow([proto.upper(), ip, port, country])
                    
            proto_ips = set()
            for p in items:
                _, ipp = p.split('://', 1)
                if proto.lower() not in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                    proto_ips.add(ipp.split(':', 1)[0])
            proto_ips = sorted(proto_ips)
            with open(os.path.join(folder_name, f'{proto}_ips.txt'), 'w', encoding='utf-8') as f:
                f.write(f"# {description} ({proto.upper()} - Только уникальные IP): {len(proto_ips)}\n")
                for ip in proto_ips: f.write(ip + '\n')

    def save(self):
        if self.live_results:
            self._save_category('results_live', self.live_results, 'Живые прокси')
            print("[✓] Базовые списки по категориям сохранены в папку 'results_live/'")
            
        if hasattr(self, 'good_results') and self.good_results:
            self._save_category('results_elite', self.good_results, 'Элитные прокси (Elite/NoDNSBL/Fast)')
            print("[✓] Элитные списки по категориям сохранены в папку 'results_elite/'")

    def run(self):
        t0 = time.time()
        print("\n🚀 ULTIMATE PROXY HUNTER v4.0 (ADVANCED FILTERS)")
        
        if self.chain_proxies:
            self._rotator = _ProxyRotator(self.chain_proxies, remove_dead=self.chain_auto_remove_dead)
            print(f"[+] Прокси-цепочка: {self._rotator.alive_count} прокси для маскировки")
            
        for attempt in range(2):
            self._download_mmdb_if_needed()
            try:
                if os.path.exists('GeoLite2-Country.mmdb'):
                    self.db_reader = maxminddb.open_database('GeoLite2-Country.mmdb')
                    break # Успешно открыли, выходим из цикла
            except Exception as e:
                print(f"Ошибка загрузки локальной базы (попытка {attempt+1}): {e}")
                self.db_reader = None
                try:
                    os.remove('GeoLite2-Country.mmdb')
                    print("Битый файл базы удалён, скачиваем заново...")
                except:
                    pass
            
        self.collect()
        if not self._cancel_event.is_set(): self.collect_random()
        if not self._cancel_event.is_set(): self.validate()
        if not self._cancel_event.is_set(): self.advanced_filter()
        self.save()
        m, s = divmod(int(time.time() - t0), 60)
        print(f"\n⏱   Общее время работы: {m}м {s}с")
        if self._cancel_event.is_set():
            print("❌ Работа была прервана пользователем.")

def main():
    parser = argparse.ArgumentParser(description='Proxy Hunter v4.0 - Advanced Filtration')
    parser.add_argument('--threads', type=int, default=300, help='Количество потоков')
    parser.add_argument('--timeout', type=int, default=5, help='Таймаут соединения в секундах')
    parser.add_argument('--countries', default='US,CA,GB,AT,BE,BG,HR,CY,CZ,DK,EE,FI,FR,DE,GR,HU,IE,IT,LV,LT,LU,MT,NL,PL,PT,RO,SK,SI,ES,SE', type=str, help='Разрешенные страны через запятую')
    parser.add_argument('--max-ping', type=float, default=700, help='Макс пинг в мс')
    parser.add_argument('--min-speed', type=float, default=1.0, help='Мин скорость Мбит/с')
    parser.add_argument('--check-smtp', choices=['True', 'False'], default='True', help='Включить проверку SMTP портов (True/False)')
    parser.add_argument('--residential-only', action='store_true', help='Только residential/мобильные IP')
    
    args = parser.parse_args()
    check_smtp_bool = args.check_smtp == 'True'
    countries_list = [c.strip().upper() for c in args.countries.split(',')
    ] if args.countries else None

    try:
        import tqdm
        import dns.resolver
    except ImportError:
        print("❌ Установите зависимости: pip install tqdm requests dnspython")
        sys.exit(1)

    hunter = ProxyHunter(
        threads=args.threads, 
        timeout=args.timeout,
        countries=countries_list, 
        max_ping=args.max_ping,
        min_speed=args.min_speed, 
        check_smtp=check_smtp_bool,
        residential_only=args.residential_only
    )
    hunter.run()

if __name__ == '__main__':
    main()
