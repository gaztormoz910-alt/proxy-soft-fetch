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
    
    PROXY_RE  = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3})[:\s,;|\"\']+(\d{1,5})\b')
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
        # Автоматический декод Base64, если весь ответ это зашифрованная строка
        stripped = content.replace('\n', '').replace('\r', '').strip()
        if len(stripped) > 20 and re.match(r'^[A-Za-z0-9+/]+={0,2}$', stripped):
            import base64
            try:
                content = base64.b64decode(stripped).decode('utf-8')
            except Exception:
                pass
        found = set()
        
        # ШАГ 1: Попытка умного парсинга JSON (защита от вложенных структур)
        try:
            import json
            data = json.loads(content)
            
            def extract_from_json(obj, depth=0):
                # Защита от бесконечной рекурсии на глубоко вложенных API (monosans geolocation ~5 уровней)
                if depth > 5:
                    return
                if isinstance(obj, dict):
                    # Извлекаем IP: приоритет ip > host > exit_ip
                    ip_val = obj.get('ip', obj.get('host', obj.get('exit_ip', '')))
                    # Пропускаем ключ 'proxy' — он часто содержит полный URI (proxyscrape) или boolean (ip_data)
                    
                    # Конвертируем в строку и валидируем
                    ip = str(ip_val).strip() if ip_val is not None else ''
                    
                    port_val = obj.get('port', '')
                    port_str = str(port_val).strip() if port_val is not None else ''
                    
                    if ip and port_str and port_str.isdigit():
                        port_int = int(port_str)
                        if cls.is_valid(ip, port_int):
                            found.add(f"{ip}:{port_str}")
                    
                    # Рекурсия только в объекты, которые вероятно содержат прокси-данные
                    # (пропускаем вложенные метаданные типа geolocation, ip_data, asn)
                    skip_keys = {'geolocation', 'location', 'ip_data', 'asn', 'city', 
                                 'continent', 'country', 'registered_country', 'subdivisions',
                                 'postal', 'names'}
                    for key, val in obj.items():
                        if key not in skip_keys and isinstance(val, (dict, list)):
                            extract_from_json(val, depth + 1)
                            
                elif isinstance(obj, list):
                    for item in obj:
                        extract_from_json(item, depth + 1)
            
            extract_from_json(data)
            # Если JSON успешно распарсился и мы нашли прокси, возвращаем результат (без Regex)
            if found:
                return list(found)
        except Exception:
            pass # Не валидный JSON или пусто — падаем в Regex-фолбэк
            
        # ШАГ 2: Fallback на регулярные выражения (для текстовых списков и таблиц)
        for i, match in enumerate(cls.TABLE_RE.finditer(content)):
            ip, port = match.groups()
            if cls.is_valid(ip.strip(), int(port)): found.add(f"{ip.strip()}:{port}")
            if i % 1000 == 0: time.sleep(0.001)
        for i, match in enumerate(cls.PROXY_RE.finditer(content)):
            ip, port = match.groups()
            if cls.is_valid(ip, int(port)): found.add(f"{ip}:{port}")
            if i % 1000 == 0: time.sleep(0.001)
            
        # Парсинг зашифрованных протоколов (VLESS, VMess, SS, Trojan, MTProto и др.)
        URI_RE = re.compile(r'((?:vless|vmess|ss|ssr|trojan|tuic|hysteria2|tg)://[^\s\"\'<>]+|https://t\.me/proxy\?[^\s\"\'<>]+)', re.IGNORECASE)
        IPV4_CHECK = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}$')
        for i, match in enumerate(URI_RE.finditer(content)):
            uri = match.group(1)
            ext_ip, _ = cls.extract_ip_port(uri)
            if IPV4_CHECK.match(ext_ip) and cls.is_valid(ext_ip, 1):
                found.add(uri)
            if i % 1000 == 0: time.sleep(0.001)
            
        return list(found)
    @staticmethod
    def extract_ip_port(uri: str) -> tuple[str, str]:
        import urllib.parse
        import base64
        import json
        try:
            if uri.startswith("vmess://"):
                b64 = uri[8:].split('#')[0]  # BUG-FP07 FIX: strip #remark fragment
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
    def fetch_url(url: str, timeout: int = 10) -> str:
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
            resp.raise_for_status()
            chunks, size = [], 0
            for chunk in resp.iter_content(chunk_size=8192):
                chunks.append(chunk.decode('utf-8', errors='ignore'))
                size += len(chunk)
                # Увеличен лимит до 2 МБ, чтобы не ломать крупные JSON ответы
                if size > 2 * 1024 * 1024: break
            resp.close()
            return ''.join(chunks)
        except Exception: 
            return ''
    @staticmethod
    def tcp_ping(ip: str, port: int, timeout: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                return sock.connect_ex((ip, port)) == 0
        except Exception: 
            return False
    @staticmethod
    def http_check(ip: str, port: int, proto: str, timeout: int) -> bool:
        proxy_url = f"{proto}://{ip}:{port}"
        proxies = {'http': proxy_url, 'https': proxy_url}
        try:
            resp = requests.get("http://gstatic.com/generate_204", proxies=proxies, timeout=timeout)
            if resp.status_code == 204: return True
        except Exception: 
            pass
        return False
    @classmethod
    def check_proxy(cls, ip: str, port: int, protos: Set[str], timeout: int) -> Set[str]:
        if not cls.tcp_ping(ip, port, timeout): return set()
        working_protos = set()
        for proto in sorted(protos):
            if cls.http_check(ip, port, proto, timeout):
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
    def generate(cls, count: int, protocol: str):
        pool = cls.POPULAR_PORTS.get(protocol.lower(), [80, 8080])
        generated_count = 0
        
        while generated_count < count:
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
                    
                yield f"{ip_obj}:{port}"
                generated_count += 1
            except Exception:
                pass
    @classmethod
    def generate_all(cls, counts: Dict[str, int]):
        for proto, count in counts.items():
            if count > 0:
                for proxy in cls.generate(count, proto):
                    yield proto, proxy
TRANS = {
    "RU": {
        "log_unique_ip": "Уникальных IP:PORT",
        "step1": "ШАГ 1: Асинхронный сбор из {0} источников...",
        "step1_5": "ШАГ 1.5: Генерация рандомных прокси...",
        "step2": "ШАГ 2: Базовая проверка {0} прокси на живость...",
        "step3": "ШАГ 3: Классификация и фильтрация {0} рабочих прокси...",
        "tqdm_dl": "Загрузка",
        "tqdm_check": "Проверка",
        "tqdm_filter": "Фильтрация",
        "live_proxies": "Живых прокси:",
        "elite_proxies": "Элитных прокси, прошедших все фильтры:",
        "sources_replied": "Ответило источников:",
        "random_generated": "Сгенерировано рандомных:",
        "time_total": "Общее время работы: {0}м {1}с",
        "user_abort": "Работа была прервана пользователем.",
        "start": "[*] Запуск сбора прокси (Лимит потоков: {max_workers})",
        "step1": "ШАГ 1: Асинхронный сбор из {0} источников...",
        "fetch_err": "    [x] Ошибка {source}: {e}",
        "raw_found": "    [+] Сырых прокси собрано: {0}",
        "step2": "ШАГ 2: Базовая проверка на живость...",
        "live_found": "    [✓] Живых прокси: {0}",
        "step3": "ШАГ 3: Расширенная фильтрация (Анон, Блеклисты, Тип)...",
        "ipinfo": "    [ipinfo.io] Получены типы для {checked}/{total} ASN",
        "passed": "    [★] Уникальных IP:PORT прошедших все фильтры: {0}",
        "done": "\n[✓] Готово! Сохранение результатов...",
        "save_live": "[✓] Базовые списки по категориям сохранены в папку 'results_live/'",
        "cancel": "[!] Задача отменена пользователем",
        "elite": "  [★ ЭЛИТНЫЙ] Прошел все фильтры: {proxy} ({proto}) - {country}",
        "working": "  [✓ РАБОЧИЙ] Найден: {proxy} ({proto}) - {country}"
    },
    "EN": {
        "start": "[*] Starting proxy collection (Thread limit: {max_workers})",
        "step1": "STEP 1: Async fetching from {0} sources...",
        "fetch_err": "    [x] Error {source}: {e}",
        "raw_found": "    [+] Raw proxies collected: {0}",
        "step2": "STEP 2: Basic live check...",
        "live_found": "    [✓] Live proxies: {0}",
        "step3": "STEP 3: Advanced filtering (Anon, Blacklists, Type)...",
        "ipinfo": "    [ipinfo.io] Fetched types for {checked}/{total} ASN",
        "passed": "    [★] Unique IP:PORT passed all filters: {0}",
        "done": "\n[✓] Done! Saving results...",
        "save_live": "[✓] Basic category lists saved to 'results_live/' folder",
        "cancel": "[!] Task cancelled by user",
        "elite": "  [★ ELITE] Passed all filters: {proxy} ({proto}) - {country}",
        "working": "  [✓ WORKING] Found: {proxy} ({proto}) - {country}"
    }
}
class ProxyHunter:
    """Главный класс сборщика и валидатора прокси"""
    
    def __init__(self, threads: int = 300, timeout: int = 3, countries: Optional[List[str]] = None, 
                 max_ping: float = 700.0, min_speed: float = 1.0,
                 check_smtp: bool = False,
                 collect_dc: bool = True, collect_res: bool = True, collect_mob: bool = True,
                 random_counts: Optional[Dict[str, int]] = None, lang: str = "RU"):
        
        self.lang = lang
        self.threads = min(threads, 5000)
        self.timeout = timeout
        
        default_countries = ['US','CA','GB','AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE',
                             'GR','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE']
        self.countries = set(c.upper() for c in (countries or default_countries))
        
        self.max_ping = max_ping
        self.min_speed = min_speed
        self.check_smtp = check_smtp
        
        self.collect_dc = collect_dc
        self.collect_res = collect_res
        self.collect_mob = collect_mob
        self.random_counts = random_counts or {'http': 0, 'socks4': 0, 'socks5': 0}
        self.proxy_protocols: Dict[str, Set[str]] = defaultdict(set)
        self.live_results: List[str] = []
        self.elite_results: List[str] = []
        
        self.results_datacenter: List[str] = []
        self.results_residential: List[str] = []
        self.results_mobile: List[str] = []
        
        self._lock = threading.Lock()
        
        self.ip_cache: Dict[str, dict] = {}
        self.asn_cache: Dict[str, str] = {}  # ASN → type (isp/hosting/business) from ipinfo.io
        self.db_reader = None
        
        self._pause_event = threading.Event()
        self._cancel_event = threading.Event()
    def _t(self, key, *args, **kwargs):
        text = TRANS.get(self.lang, TRANS["EN"]).get(key, key)
        if args or kwargs:
            try:
                return text.format(*args, **kwargs)
            except Exception:
                return text
        return text
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
        print(f"\n[+] " + self._t("step1").format(len(SOURCES)))
        total_raw, ok_sources = 0, 0
        try:
            from tqdm import tqdm
            pbar = tqdm(total=len(SOURCES), desc=self._t("tqdm_dl"))
        except ImportError:
            pbar = None
        with ThreadPoolExecutor(max_workers=min(len(SOURCES), 30)) as ex:
            fmap = {}
            for url, proto in SOURCES:
                fmap[ex.submit(ProxyUtils.fetch_url, url, 12)] = (url, proto)
                
            for fut in as_completed(fmap):
                if self._wait_if_paused(): break
                if self._cancel_event.is_set(): break
                url, proto = fmap[fut]
                content = fut.result()
                if content:
                    ok_sources += 1
                    proxies = ProxyUtils.parse_proxies(content)
                    total_raw += len(proxies)
                    with self._lock:
                        for p in proxies:
                            self.proxy_protocols[p].add(proto)
                if pbar: pbar.update(1)
        
        if pbar: pbar.close()
        print(f"    {self._t('sources_replied')}: {ok_sources}/{len(SOURCES)}")
        print(f"    {self._t('log_unique_ip')}: {len(self.proxy_protocols)}")
    def collect_random(self):
        total_random = sum(self.random_counts.values())
        if total_random == 0:
            return
            
        print(f"\n[+] " + self._t("step1_5"))
        count = 0
        with self._lock:
            for proto, proxy in RandomProxyGenerator.generate_all(self.random_counts):
                self.proxy_protocols[proxy].add(proto)
                count += 1
        print(f"    {self._t('random_generated')}: {count}")
    def validate(self):
        if not self.proxy_protocols: return
        candidates = list(self.proxy_protocols.items())
        total = len(candidates)
        print(f"\n[+] " + self._t("step2").format(total))
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
                
            ip, port_s = ip_port.rsplit(':', 1)  # BUG-09 FIX: rsplit для защиты от IPv6/мусора
            working = ProxyUtils.check_proxy(ip, int(port_s), protos, self.timeout)
            if working: 
                if self._cancel_event.is_set(): return None
                
                # Фильтр по странам — сразу отсеиваем невыбранные страны
                country = self._get_country(ip)
                if self.countries and country.upper() not in self.countries:
                    return None
                
                if self._wait_if_paused(): return None
                
                return (ip_port, working)
            return None
        try:
            from tqdm import tqdm
            pbar = tqdm(total=total, desc=self._t("tqdm_check"))
        except ImportError: 
            pbar = None
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            import itertools
            import concurrent.futures
            
            candidate_iter = iter(candidates)
            active_futs = set()
            
            for item in itertools.islice(candidate_iter, self.threads * 2):
                active_futs.add(ex.submit(worker, item))
                
            while active_futs:
                done, active_futs = concurrent.futures.wait(
                    active_futs, return_when=concurrent.futures.FIRST_COMPLETED
                )
                
                for fut in done:
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
                                        print(f"    [REALTIME_NEW_LIVE] {ext_ip}|{ext_port}|{p.upper()}|{ext_country}")
                                else:
                                    self.live_results.append(f"{p}://{ip_port}")
                                    ip, port = ip_port.rsplit(':', 1)  # BUG-09 FIX
                                    country = self.ip_cache.get(ip, {}).get('country', '') or self._get_country(ip)
                                    if ip not in self.ip_cache: self.ip_cache[ip] = {}
                                    self.ip_cache[ip]['country'] = country
                                    print(f"    [REALTIME_NEW_LIVE] {ip}|{port}|{p.upper()}|{country}")
                            if len(self.live_results) % 5 == 0 or len(self.live_results) < 10:
                                print(f"    [REALTIME_LIVE] {len(self.live_results)}")
                    if pbar: pbar.update(1)
                if self._cancel_event.is_set(): break
                
                for item in itertools.islice(candidate_iter, len(done)):
                    active_futs.add(ex.submit(worker, item))
        if pbar: pbar.close()
        self.live_results = sorted(set(self.live_results))
        print(f"    {self._t('live_proxies')} {len(self.live_results)}")
    def _download_mmdb_if_needed(self):
        db_path = 'GeoLite2-Country.mmdb'
        needs_download = False
        
        if not os.path.exists(db_path):
            needs_download = True
            print(f"\n[!] Локальная база {db_path} не была найдена. Скачиваю (около 5MB)...")
        else:
            # Обновляем базу, если она старше 7 дней (604800 секунд)
            if time.time() - os.path.getmtime(db_path) > 604800:
                needs_download = True
                print(f"\n[!] Локальная база {db_path} устарела (старше 7 дней). Обновляю...")
                
        if needs_download:
            url = 'https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb'
            tmp_path = db_path + '.tmp'
            try:
                r = requests.get(url, stream=True, timeout=30)
                r.raise_for_status()
                # BUG FIX: Используем временный файл, чтобы не оставить битую базу при обрыве сети
                with open(tmp_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk: f.write(chunk)
                # Если скачивание завершено успешно, атомарно заменяем старый файл новым
                os.replace(tmp_path, db_path)
                print("[✓] Локальная база успешно скачана/обновлена!")
            except Exception as e:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                print(f"[x] Ошибка обновления базы (работаем без GeoIP): {e}")
    def _batch_ip_info(self, ips: Set[str]):
        """Пакетный запрос в ip-api.com с Exponential Backoff для обхода 429 Rate Limit"""
        chunks = [list(ips)[i:i+100] for i in range(0, len(ips), 100)]
        for chunk in chunks:
            if self._wait_if_paused(): break
            if self._cancel_event.is_set(): break
            
            retries = 3
            backoff = 4
            for attempt in range(retries):
                try:
                    resp = requests.post("http://ip-api.com/batch?fields=query,isp,org,as,hosting,mobile,countryCode", json=chunk, timeout=10)
                    
                    if resp.status_code == 429:
                        # Rate Limit: ждем дольше и пробуем снова
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                        
                    if resp.status_code == 200:
                        try:
                            json_data = resp.json()
                            if not isinstance(json_data, list): break # Защита от кривого контракта
                            
                            with self._lock: # Защита от состояния гонки (Race Condition)
                                for data in json_data:
                                    if not isinstance(data, dict): continue
                                    query_ip = data.get('query')
                                    if not query_ip: continue
                                    
                                    if query_ip not in self.ip_cache:
                                        self.ip_cache[query_ip] = {}
                                        
                                    self.ip_cache[query_ip].update({
                                        'country': data.get('countryCode', ''),
                                        'datacenter': data.get('hosting', False),
                                        'mobile': data.get('mobile', False),
                                        'isp': data.get('isp', '').lower(),
                                        'asn': data.get('as', '')  # e.g. "AS265606 DIGY NETWORKS"
                                    })
                            break # Успешно, выходим из цикла ретраев
                        except Exception:
                            break # JSON Decode error или другая фатальная ошибка структуры
                    else:
                        break # Другие ошибки (500, 403 и т.д.) - пропускаем чанк
                except Exception:
                    time.sleep(2)
                    
            time.sleep(4) # Базовый кулдаун API
    def _batch_asn_type(self):
        """Запрос типа ASN (isp/hosting/business) через ipinfo.io для определения Residential.
        
        Проверяем каждый уникальный ASN один раз. Результат кешируется в self.asn_cache.
        ASN type 'isp' = Residential, 'hosting' = Datacenter, 'business' = Datacenter.
        """
        # Собираем уникальные ASN из ip_cache
        unique_asns = set()
        with self._lock:
            for ip, info in self.ip_cache.items():
                asn_str = info.get('asn', '')
                if asn_str:
                    asn_num = asn_str.split()[0]  # "AS265606 DIGY NETWORKS" → "AS265606"
                    if asn_num.startswith('AS'):
                        unique_asns.add(asn_num)
        
        # Убираем уже закешированные
        unique_asns -= set(self.asn_cache.keys())
        if not unique_asns:
            return
        
        print(f"    [ipinfo.io] Проверяю тип {len(unique_asns)} уникальных ASN (Residential/Hosting)...")
        
        checked = 0
        for asn in unique_asns:
            if self._cancel_event.is_set(): break
            
            try:
                resp = requests.get(f"https://ipinfo.io/{asn}/json", timeout=5,
                                    headers={'Accept': 'application/json', 'User-Agent': 'ProxyHunter/4.0'})
                if resp.status_code == 200:
                    data = resp.json()
                    asn_type = data.get('type', '').lower()  # "isp", "hosting", "business"
                    if asn_type:
                        self.asn_cache[asn] = asn_type
                        checked += 1
                elif resp.status_code == 429:
                    # Rate limit — подождём и продолжим
                    time.sleep(5)
                    try:
                        resp = requests.get(f"https://ipinfo.io/{asn}/json", timeout=5,
                                            headers={'Accept': 'application/json', 'User-Agent': 'ProxyHunter/4.0'})
                        if resp.status_code == 200:
                            data = resp.json()
                            asn_type = data.get('type', '').lower()
                            if asn_type:
                                self.asn_cache[asn] = asn_type
                                checked += 1
                    except Exception:
                        pass
            except Exception:
                pass
            
            time.sleep(0.3)  # Мягкий rate-limit для ipinfo.io
        
        print(self._t("ipinfo", checked=checked, total=len(unique_asns)))
    def _check_rdns_and_bl(self, ip: str) -> dict:
        """Кэшируемая проверка RDNS и DNSBL"""
        # BUG-4 FIX: чтение кэша под локом, возврат копии для thread-safety
        with self._lock:
            if ip in self.ip_cache and 'dnsbl' in self.ip_cache[ip]:
                return self.ip_cache[ip].copy()
        fast_resolver = dns.resolver.Resolver()
        fast_resolver.timeout = 1.0
        fast_resolver.lifetime = 1.0
        rdns = ""
        try:
            rev_name = dns.reversename.from_address(ip)
            rdns = str(fast_resolver.resolve(rev_name, 'PTR')[0]).lower()
        except Exception: 
            pass
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
                    if ip_str.startswith('127.0.0.') or ip_str.startswith('127.0.1.'):
                        is_bl = True
                        break
                if is_bl: break
            except Exception: 
                pass
        bad_ports = [21, 22, 23, 25, 3389, 3128]
        has_bad_port = False
        for port in bad_ports:
            if ProxyUtils.tcp_ping(ip, port, timeout=1):
                has_bad_port = True
                break
        # Защита от состояния гонки при записи из множества потоков
        with self._lock:
            if ip not in self.ip_cache: self.ip_cache[ip] = {}
            self.ip_cache[ip].update({'rdns': rdns, 'dnsbl': is_bl, 'bad_ports': has_bad_port})
            return self.ip_cache[ip].copy()
    def _run_single_filter(self, item: str) -> Optional[Tuple[str, str]]:
        """Классификация и фильтрация одного прокси.
        
        Классификация СТРОГО по данным ip-api.com:
          hosting=true  → Datacenter
          mobile=true   → Mobile
          оба false     → Residential (ISP)
        """
        if self._wait_if_paused(): return None
        if self._cancel_event.is_set(): return None
        
        try:
            proto, ipp = item.split('://', 1)
        except ValueError:
            return None
        
        encrypted_protos = ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto')
        
        # --- Извлечение IP и порта ---
        if proto.lower() in encrypted_protos:
            ext_ip, _ = ProxyUtils.extract_ip_port(item)
            if ext_ip == "Config" or not re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', ext_ip):
                # Зашифрованные конфиги без видимого IP — по умолчанию Datacenter
                if not getattr(self, 'collect_dc', True):
                    return None
                return (item, "Datacenter")
            ip = ext_ip
            port = 443
        else:
            if ':' not in ipp: return None
            ip, port_s = ipp.rsplit(':', 1)
            try: port = int(port_s)
            except ValueError: return None
        
        # === КЛАССИФИКАЦИЯ ===
        # ip-api.com → mobile detection
        # ipinfo.io  → residential detection (ASN type = "isp")
        with self._lock:
            ip_info = self.ip_cache.get(ip, {}).copy()
        
        has_api_data = 'datacenter' in ip_info
        is_mobile_api = ip_info.get('mobile', False)       # ip-api.com
        is_hosting_api = ip_info.get('datacenter', False)  # ip-api.com
        
        # Получаем тип ASN из ipinfo.io
        asn_str = ip_info.get('asn', '')
        asn_num = asn_str.split()[0] if asn_str else ''
        asn_type = self.asn_cache.get(asn_num, '')  # "isp", "hosting", "business" или ""
        
        # Приоритет классификации:
        # 1. ip-api.com mobile=true → Mobile
        # 2. ipinfo.io ASN type="isp" → Residential
        # 3. ipinfo.io ASN type="hosting"/"business" → Datacenter
        # 4. Fallback: ip-api.com hosting=true → Datacenter
        # 5. Fallback: нет данных → Datacenter
        if is_mobile_api:
            category = "Mobile"
        elif asn_type == "isp":
            category = "Residential"
        elif asn_type in ("hosting", "business"):
            category = "Datacenter"
        elif not has_api_data:
            category = "Datacenter"
        elif is_hosting_api:
            category = "Datacenter"
        else:
            category = "Residential"
        
        # === ФИЛЬТР по выбору пользователя (галочки в GUI) ===
        if category == "Datacenter" and not getattr(self, 'collect_dc', True):
            return None
        if category == "Residential" and not getattr(self, 'collect_res', True):
            return None
        if category == "Mobile" and not getattr(self, 'collect_mob', True):
            return None
        
        # === ПРОВЕРКА ПИНГА (только для стандартных прокси) ===
        if proto.lower() not in encrypted_protos and self.max_ping > 0:
            try:
                ping_start = time.time()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(min(3.0, self.timeout))
                    sock.connect((ip, port))
                ping_ms = (time.time() - ping_start) * 1000
                if ping_ms > self.max_ping:
                    return None
            except Exception:
                return None
        
        # === ПРОВЕРКА SMTP (если включена пользователем) ===
        if self.check_smtp and proto.lower() not in encrypted_protos:
            proxy_proto = proto.lower()
            if proxy_proto in ('socks4', 'socks5'):
                proxy_url = f"{proxy_proto}://{ip}:{port}"
            elif proxy_proto == 'socks5h':
                proxy_url = f"socks5h://{ip}:{port}"
            else:
                proxy_url = f"http://{ip}:{port}"
            proxies_dict = {'http': proxy_url, 'https': proxy_url}
            
            smtp_ok = False
            for smtp_port in [25, 587]:
                try:
                    resp = requests.get(f'http://portquiz.net:{smtp_port}',
                                       proxies=proxies_dict, timeout=self.timeout)
                    if resp.status_code == 200:
                        smtp_ok = True
                        break
                except Exception:
                    pass
            if not smtp_ok:
                return None
        
        return (item, category)
    def advanced_filter(self):
        if not self.live_results: return
        print(f"\n[+] " + self._t("step3").format(len(self.live_results)))
        
        # Собираем уникальные IP для пакетного запроса
        unique_ips = set()
        for r in self.live_results:
            ext_ip, _ = ProxyUtils.extract_ip_port(r)
            if ext_ip != "Config" and re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', ext_ip):
                unique_ips.add(ext_ip)
        
        # 1) ip-api.com — определяем mobile/hosting флаги для каждого IP
        print(f"    [ip-api.com] Определяю mobile/hosting для {len(unique_ips)} IP...")
        self._batch_ip_info(unique_ips)
        print(f"    [ip-api.com] Данные получены.")
        
        # 2) ipinfo.io — определяем тип ASN (isp/hosting/business) для Residential-детекции
        self._batch_asn_type()
        print(f"    Классифицирую и фильтрую прокси...")
        
        try:
            from tqdm import tqdm
            pbar = tqdm(total=len(self.live_results), desc=self._t("tqdm_filter"))
        except ImportError:
            pbar = None
        
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            import itertools
            import concurrent.futures
            
            candidate_iter = iter(self.live_results)
            active_futs = set()
            
            for item in itertools.islice(candidate_iter, self.threads * 2):
                active_futs.add(ex.submit(self._run_single_filter, item))
            
            while active_futs:
                done, active_futs = concurrent.futures.wait(
                    active_futs, return_when=concurrent.futures.FIRST_COMPLETED
                )
                
                for fut in done:
                    if self._wait_if_paused(): break
                    if self._cancel_event.is_set(): break
                    res_tuple = fut.result()
                    if res_tuple:
                        res, category = res_tuple
                        with self._lock:
                            self.elite_results.append(res)
                            if category == "Datacenter": self.results_datacenter.append(res)
                            elif category == "Residential": self.results_residential.append(res)
                            elif category == "Mobile": self.results_mobile.append(res)
                            
                            # REALTIME вывод для GUI
                            proto, ipp = res.split('://', 1)
                            if proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                                ext_ip, ext_port = ProxyUtils.extract_ip_port(res)
                                ext_country = (self.ip_cache.get(ext_ip, {}).get('country') or self._get_country(ext_ip)) if ext_ip != "Config" else "Unknown"
                                print(f"    [REALTIME_NEW_ELITE] {ext_ip}|{ext_port}|{proto.upper()}|{ext_country}|{category}")
                            else:
                                ip, port = ipp.rsplit(':', 1)
                                country = self.ip_cache.get(ip, {}).get('country') or self._get_country(ip)
                                print(f"    [REALTIME_NEW_ELITE] {ip}|{port}|{proto}|{country}|{category}")
                            
                            total_elite = len(self.elite_results)
                            if total_elite % 2 == 0 or total_elite < 5:
                                print(f"    [REALTIME_ELITE] {total_elite}")
                    if pbar: pbar.update(1)
                
                if self._cancel_event.is_set(): break
                
                for item in itertools.islice(candidate_iter, len(done)):
                    active_futs.add(ex.submit(self._run_single_filter, item))
        
        if pbar: pbar.close()
        self.results_datacenter = sorted(set(self.results_datacenter))
        self.results_residential = sorted(set(self.results_residential))
        self.results_mobile = sorted(set(self.results_mobile))
        self.elite_results = sorted(set(self.elite_results))
        
        total_elite = len(self.elite_results)
        print(f"    {self._t('elite_proxies')} {total_elite} (DC: {len(self.results_datacenter)}, Res: {len(self.results_residential)}, Mob: {len(self.results_mobile)})")
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
            print(self._t("save_live"))
            
        # BUG-7 FIX: Сохраняем elite_results, которые GUI ожидает в results_elite/
        if self.elite_results:
            self._save_category('results_elite', self.elite_results, 'Elite Proxies')
            
        if hasattr(self, 'results_datacenter') and self.results_datacenter:
            self._save_category('results_datacenter', self.results_datacenter, 'Datacenter Proxies')
        if hasattr(self, 'results_residential') and self.results_residential:
            self._save_category('results_residential', self.results_residential, 'Residential Proxies')
        if hasattr(self, 'results_mobile') and self.results_mobile:
            self._save_category('results_mobile', self.results_mobile, 'Mobile Proxies')
    def run(self):
        t0 = time.time()
        print("\n🚀 ULTIMATE PROXY HUNTER v4.0 (ADVANCED FILTERS)")
            
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
                except Exception:  # BUG-10 FIX: bare except
                    pass
            
        self.collect()
        if not self._cancel_event.is_set(): self.collect_random()
        if not self._cancel_event.is_set(): self.validate()
        if not self._cancel_event.is_set(): self.advanced_filter()
        if not self._cancel_event.is_set():  # BUG-FP35 FIX: не сохраняем при отмене
            self.save()
        m, s = divmod(int(time.time() - t0), 60)
        print("\n⏱   " + self._t("time_total").format(m, s))
        if self._cancel_event.is_set():
            print("❌ " + self._t("user_abort"))
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
    # BUG-2 FIX: residential_only не существует в __init__, используем collect_dc
    hunter = ProxyHunter(
        threads=args.threads, 
        timeout=args.timeout,
        countries=countries_list, 
        max_ping=args.max_ping,
        min_speed=args.min_speed, 
        check_smtp=check_smtp_bool,
        collect_dc=not args.residential_only,
        collect_res=True,
        collect_mob=True
    )
    hunter.run()
if __name__ == '__main__':
    main()