import re
import socket
import threading
import time
import requests
import argparse
import sys
import os
import csv
try:
    import orjson as json
except ImportError:
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
    ('http://htmlweb.ru/analiz/proxy_list.php', 'http'),
    ('https://api.openproxylist.xyz/http.txt', 'http'),
    ('https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all', 'http'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all', 'http'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all', 'http'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=json', 'http'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=text', 'http'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get', 'http'),
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
    ('https://databay.com/api/v1/proxy-list?format=txt', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&country=DE', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&country=GB', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&country=NL', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&country=RU', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&country=US', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=http', 'http'),
    ('https://databay.com/api/v1/proxy-list?protocol=http', 'http'),
    ('https://free-proxy-list.net/', 'http'),
    ('https://free-proxy-list.net/anonymous-proxy.html', 'http'),
    ('https://free-proxy-list.net/uk-proxy.html', 'http'),
    ('https://hidemium.io/free-proxy', 'http'),
    ('https://litport.net/api/free-proxy', 'http'),
    ('https://proxy-spider.com/api/proxies.example.txt', 'http'),
    ('https://proxyfreeonly.com/ru/free-proxy-list', 'http'),

    ('https://proxymania.su/free-proxy', 'http'),
    ('https://proxyspace.pro/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/BreakingTechFr/Proxy_Free/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/http/raw/all.txt', 'all'),
    ('https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Firmfox/Proxify/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/MrMarble/proxy-list/main/all.txt', 'all'),
    ('https://raw.githubusercontent.com/Noctiro/getproxy/master/file/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Skillter/ProxyGather/refs/heads/master/proxies/working-proxies-http.txt', 'http'),
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/all.txt', 'all'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/top-http.txt', 'http'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/berkay-digital/Proxy-Scraper/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/http.txt', 'http'),
    ('https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/sources/auto.txt', 'http'),
    ('https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/sources/http.txt', 'http'),
    ('https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt', 'http'),
    ('https://raw.githubusercontent.com/iplocate/free-proxy-list/main/all-proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/http.txt', 'http'),
    ('https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies.json', 'all'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt', 'all'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.csv', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/BR/data.txt', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/CA/data.txt', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/DE/data.txt', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/FR/data.txt', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/GB/data.txt', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/IN/data.txt', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/JP/data.txt', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/NL/data.txt', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/RU/data.txt', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/SG/data.txt', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/countries/US/data.txt', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt', 'all'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/https/data.txt', 'all'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt', 'http'),
    ('https://raw.githubusercontent.com/stormsia/proxy-list/main/working_proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/themiralay/Proxy-List-World/master/data.txt', 'all'),
    ('https://raw.githubusercontent.com/trio666/proxy-checker/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/tuanminpay/live-proxy/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/main/proxylist.txt', 'http'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/proxylist.json', 'http'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/proxylist.txt', 'http'),
    ('https://raw.githubusercontent.com/yuceltoluyag/GoodProxy/main/raw.txt', 'http'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt', 'http'),
    ('https://spys.me/proxy.txt', 'http'),
    ('https://sunny9577.github.io/proxy-scraper/generated/http_proxies.txt', 'all'),
    ('https://toproxylab.com/ru/spisok-besplatnyh-proksi-serverov', 'http'),
    ('https://vakhov.github.io/fresh-proxy-list/http.txt', 'http'),
    ('https://vakhov.github.io/fresh-proxy-list/proxylist.txt', 'http'),
    ('https://www.google-proxy.net/', 'http'),
    ('https://www.my-proxy.com/free-proxy-list.html', 'http'),
    ('https://www.sslproxies.org/', 'http'),
    ('https://www.us-proxy.org/', 'http'),
    ('https://cdn.jsdelivr.net/gh/officialputuid/ProxyForEveryone@main/https/https.txt', 'https'),
    ('https://databay.com/api/v1/proxy-list?format=json&protocol=https', 'https'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=https', 'https'),
    ('https://proxyspace.pro/https.txt', 'https'),
    ('https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt', 'https'),
    ('https://raw.githubusercontent.com/Boster12/Free_Proxy_List/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt', 'https'),
    ('https://raw.githubusercontent.com/Noctiro/getproxy/master/file/https.txt', 'https'),
    ('https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/https.txt', 'https'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/https.txt', 'https'),
    ('https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt', 'https'),
    ('https://raw.githubusercontent.com/gfpcom/free-proxy-list/lists/https.txt', 'https'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt', 'https'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt', 'https'),
    ('https://raw.githubusercontent.com/trio666/proxy-checker/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt', 'https'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt', 'https'),
    ('https://vakhov.github.io/fresh-proxy-list/https.txt', 'https'),
    ('https://api.openproxylist.xyz/socks4.txt', 'socks4'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all', 'socks4'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=json&protocol=socks4', 'socks4'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text&protocol=socks4', 'socks4'),
    ('https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list/socks4.txt', 'socks4'),
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
    ('https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/sources/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt', 'socks4'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt', 'socks4'),
    ('https://raw.githubusercontent.com/trio666/proxy-checker/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/tuanminpay/live-proxy/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks4.txt', 'socks4'),
    ('https://sunny9577.github.io/proxy-scraper/generated/socks4_proxies.txt', 'socks4'),
    ('https://vakhov.github.io/fresh-proxy-list/socks4.txt', 'socks4'),
    ('https://www.socks-proxy.net/', 'socks4'),
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
    ('https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/sources/socks5.txt', 'socks5'),
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
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt', 'socks5'),
    ('https://spys.me/socks.txt', 'socks5'),
    ('https://sunny9577.github.io/proxy-scraper/generated/socks5_proxies.txt', 'socks5'),
    ('https://vakhov.github.io/fresh-proxy-list/socks5.txt', 'socks5'),
]
# === ПАГИНАЦИЯ (ДИНАМИЧЕСКИЕ ИСТОЧНИКИ) ===
# Advanced.name (до 150 страниц)
SOURCES.extend([(f'https://advanced.name/freeproxy?page={i}', 'http') for i in range(1, 151)])
SOURCES.extend([(f'https://advanced.name/freeproxy?type=socks4&page={i}', 'socks4') for i in range(1, 151)])
SOURCES.extend([(f'https://advanced.name/freeproxy?type=socks5&page={i}', 'socks5') for i in range(1, 151)])

# Geonode API (до 20 страниц, limit=500)
SOURCES.extend([(f'https://proxylist.geonode.com/api/proxy-list?limit=500&page={i}&sort_by=lastChecked&sort_type=desc', 'http') for i in range(1, 21)])

# PubProxy API (5 запросов - лимит для free-пользователей)
SOURCES.append(('http://pubproxy.com/api/proxy?limit=5&format=txt&http=true&level=anonymous,elite&type=http,socks4,socks5', 'http'))

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
        if not (len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
                and 1 <= port <= 65535):
            return False
        # L-02 FIX: Block private/reserved IPs
        first = int(parts[0])
        if first in (0, 10, 127) or first >= 224:
            return False
        if first == 172 and 16 <= int(parts[1]) <= 31:
            return False
        if first == 192 and int(parts[1]) == 168:
            return False
        if first == 169 and int(parts[1]) == 254:
            return False
        return True
    @classmethod
    def parse_proxies(cls, content: str) -> List[str]:
        # M-04 FIX: Stricter Base64 heuristic to avoid decoding plain text
        stripped = content.replace('\n', '').replace('\r', '').strip()
        if len(stripped) > 20 and re.match(r'^[A-Za-z0-9+/]+={0,2}$', stripped):
            import base64
            try:
                decoded = base64.b64decode(stripped).decode('utf-8')
                # Require some proxy-like signature in decoded text
                if re.search(r'\d{1,3}\.\d{1,3}\.', decoded) or '://' in decoded:
                    content = decoded
            except Exception:
                pass
        found = set()
        
        # ШАГ 1: Попытка умного парсинга JSON (защита от вложенных структур)
        try:
            try: import orjson as json; data = json.loads(content)
            except: import json; data = json.loads(content)
            
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
        import base64
        for i, match in enumerate(re.finditer(r'data-ip=["\']([A-Za-z0-9+/=]+)["\'].*?data-port=["\']([A-Za-z0-9+/=]+)["\']', content, re.DOTALL)):
            try:
                ip = base64.b64decode(match.group(1)).decode('utf-8').strip()
                port = base64.b64decode(match.group(2)).decode('utf-8').strip()
                if port.isdigit() and cls.is_valid(ip, int(port)):
                    found.add(f"{ip}:{port}")
            except Exception:
                pass
            if i % 1000 == 0: time.sleep(0.001)

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
    @classmethod
    def fetch_github_commits(cls, url: str, token: str, hours_back: int = 24) -> tuple:
        owner, repo, branch, path = None, None, None, None
        
        m_raw = re.match(r'https?://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.*)', url)
        if m_raw:
            owner, repo, branch, path = m_raw.groups()
            
        m_cdn = re.match(r'https?://cdn\.jsdelivr\.net/gh/([^/]+)/([^@/]+)(?:@([^/]+))?/(.*)', url)
        if m_cdn:
            owner, repo, branch, path = m_cdn.groups()
            if not branch: branch = "main"
            
        if not owner or not repo or not path:
            return [], {}
            
        import datetime
        since_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/commits?path={path}&since={since_date}&per_page=100"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        
        commit_urls = []
        rate_limit = {}
        try:
            resp = requests.get(api_url, headers=headers, timeout=10)
            if 'X-RateLimit-Limit' in resp.headers:
                rate_limit['limit'] = resp.headers.get('X-RateLimit-Limit')
                rate_limit['remaining'] = resp.headers.get('X-RateLimit-Remaining')
                rate_limit['reset'] = resp.headers.get('X-RateLimit-Reset')
                rate_limit['used'] = resp.headers.get('X-RateLimit-Used')

            if resp.status_code == 200:
                commits = resp.json()
                for c in commits:
                    sha = c.get('sha')
                    if sha:
                        commit_urls.append(f"https://raw.githubusercontent.com/{owner}/{repo}/{sha}/{path}")
            
            while 'next' in resp.links:
                resp = requests.get(resp.links['next']['url'], headers=headers, timeout=10)
                if 'X-RateLimit-Limit' in resp.headers:
                    rate_limit['limit'] = resp.headers.get('X-RateLimit-Limit')
                    rate_limit['remaining'] = resp.headers.get('X-RateLimit-Remaining')
                    rate_limit['reset'] = resp.headers.get('X-RateLimit-Reset')
                    rate_limit['used'] = resp.headers.get('X-RateLimit-Used')

                if resp.status_code == 200:
                    for c in resp.json():
                        sha = c.get('sha')
                        if sha:
                            commit_urls.append(f"https://raw.githubusercontent.com/{owner}/{repo}/{sha}/{path}")
                else:
                    break
        except Exception:
            pass
            
        return commit_urls, rate_limit

    @staticmethod
    def extract_ip_port(uri: str) -> tuple[str, str]:
        import urllib.parse
        import base64
        try: import orjson as json
        except: import json
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
        import random, time
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        headers = {'User-Agent': random.choice(user_agents)}
        
        # Stagger requests for sites with many pagination links to prevent 429 / DDoS blocks
        if "advanced.name" in url:
            time.sleep(random.uniform(0.5, 3.0))

        try:
            resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
            resp.raise_for_status()
            chunks, size = [], 0
            for chunk in resp.iter_content(chunk_size=8192):
                chunks.append(chunk.decode('utf-8', errors='ignore'))
                size += len(chunk)
                # Увеличен лимит до 20 МБ, чтобы не ломать крупные JSON ответы и длинные списки
                if size > 20 * 1024 * 1024: break
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
        return working_protos

    @staticmethod
    async def async_tcp_ping(ip: str, port: int, timeout: int) -> bool:
        import asyncio
        try:
            fut = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(fut, timeout=timeout)
            writer.close()
            try: await writer.wait_closed()
            except Exception: pass
            return True
        except Exception: 
            return False

    @staticmethod
    async def async_http_check(ip: str, port: int, proto: str, timeout: int) -> bool:
        import asyncio
        try:
            fut = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(fut, timeout=timeout)
            
            try:
                if proto == 'http':
                    req = b"GET http://gstatic.com/generate_204 HTTP/1.1\r\nHost: gstatic.com\r\nConnection: close\r\n\r\n"
                    writer.write(req)
                    await writer.drain()
                    resp = await asyncio.wait_for(reader.read(1024), timeout=timeout)
                    return b"204 No Content" in resp
                    
                elif proto == 'socks4':
                    # SOCKS4 connect request to 142.250.186.99:80
                    req = b"\x04\x01\x00\x50\x8E\xFA\xBA\x63\x00"
                    writer.write(req)
                    await writer.drain()
                    resp = await asyncio.wait_for(reader.read(8), timeout=timeout)
                    if len(resp) < 8 or resp[1] != 0x5a:
                        return False
                    req2 = b"GET /generate_204 HTTP/1.1\r\nHost: gstatic.com\r\nConnection: close\r\n\r\n"
                    writer.write(req2)
                    await writer.drain()
                    resp2 = await asyncio.wait_for(reader.read(1024), timeout=timeout)
                    return b"204 No Content" in resp2
                    
                elif proto == 'socks5':
                    writer.write(b"\x05\x01\x00")
                    await writer.drain()
                    resp = await asyncio.wait_for(reader.read(2), timeout=timeout)
                    if len(resp) < 2 or resp[1] != 0x00:
                        return False
                    host = b"gstatic.com"
                    req = b"\x05\x01\x00\x03" + bytes([len(host)]) + host + b"\x00\x50"
                    writer.write(req)
                    await writer.drain()
                    resp_hdr = await asyncio.wait_for(reader.readexactly(4), timeout=timeout)
                    if resp_hdr[1] != 0x00:
                        return False
                    atype = resp_hdr[3]
                    if atype == 0x01: await asyncio.wait_for(reader.readexactly(6), timeout=timeout)
                    elif atype == 0x03: 
                        domain_len = (await asyncio.wait_for(reader.readexactly(1), timeout=timeout))[0]
                        await asyncio.wait_for(reader.readexactly(domain_len + 2), timeout=timeout)
                    elif atype == 0x04: await asyncio.wait_for(reader.readexactly(18), timeout=timeout)
                    req2 = b"GET /generate_204 HTTP/1.1\r\nHost: gstatic.com\r\nConnection: close\r\n\r\n"
                    writer.write(req2)
                    await writer.drain()
                    resp2 = await asyncio.wait_for(reader.read(1024), timeout=timeout)
                    return b"204 No Content" in resp2
            finally:
                writer.close()
                try: await writer.wait_closed()
                except Exception: pass
        except Exception:
            return False

    @classmethod
    async def async_check_proxy(cls, ip: str, port: int, protos: Set[str], timeout: int) -> Set[str]:
        if not await cls.async_tcp_ping(ip, port, timeout): return set()
        working_protos = set()
        for proto in sorted(protos):
            if await cls.async_http_check(ip, port, proto, timeout):
                working_protos.add(proto)
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
        'https': [443, 8443, 8080, 3128, 8888, 8000, 8118, 9443, 4443, 18443, 8880, 9080, 8081, 9090, 8123],
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
    def generate(cls, count: int, protocol: str, patterns: Dict[str, List[tuple]] = None):
        pool = cls.POPULAR_PORTS.get(protocol.lower(), [80, 8080])
        generated_count = 0
        import socket
        import struct
        
        protocol_patterns = patterns.get(protocol.lower(), []) if patterns else []
        
        while generated_count < count:
            if protocol_patterns and random.random() < 0.95:
                # 95% chance to use pattern, 5% full random for diversity
                subnet24, subnet16, port = random.choice(protocol_patterns)
                if random.random() < 0.5:
                    ip_str = f"{subnet24}.{random.randint(1, 254)}"
                else:
                    ip_str = f"{subnet16}.{random.randint(1, 254)}.{random.randint(1, 254)}"
                # Quick reserved IP check for pattern-generated IPs
                b1 = int(ip_str.split('.')[0])
                if b1 in (0, 10, 127) or b1 >= 224:
                    continue
                yield f"{ip_str}:{port}"
                generated_count += 1
            else:
                ip_int = random.randint(1, 0xFFFFFFFF - 1)
                b1 = ip_int >> 24
                # Fast filter for reserved spaces
                if b1 in {0, 10, 127} or b1 >= 224:
                    continue
                b2 = (ip_int >> 16) & 0xFF
                if b1 == 172 and 16 <= b2 <= 31:
                    continue
                if b1 == 192 and b2 == 168:
                    continue
                if b1 == 100 and 64 <= b2 <= 127:
                    continue
                
                try:
                    ip_str = socket.inet_ntoa(struct.pack('!I', ip_int))
                    # Микс портов: 50% из пула, 50% полностью рандомные
                    if random.random() < 0.5:
                        port = random.choice(pool)
                    else:
                        port = random.randint(1, 65535)
                        
                    yield f"{ip_str}:{port}"
                    generated_count += 1
                except Exception:
                    pass

    @classmethod
    def generate_all(cls, counts: Dict[str, int], patterns: Dict[str, List[tuple]] = None):
        for proto, count in counts.items():
            if count > 0:
                for proxy in cls.generate(count, proto, patterns):
                    yield proto, proxy
TRANS = {
    "RU": {
        "log_unique_ip": "Уникальных IP:PORT",
        "step1": "ШАГ 1: Асинхронный сбор из {0} источников...",
        "step4": "ШАГ 4: Генерация рандомных прокси...",
        "step2": "ШАГ 2: Базовая проверка {0} прокси на живость...",
        "step5": "ШАГ 5: Базовая проверка {0} сгенерированных прокси на живость...",
        "step3": "ШАГ 3: Классификация и фильтрация {0} рабочих прокси...",
        "tqdm_dl": "Загрузка",
        "tqdm_check": "Проверка",
        "tqdm_filter": "Фильтрация",
        "live_proxies": "Живых прокси:",
        "elite_proxies": "Элитных прокси, прошедших все фильтры:",
        "sources_replied": "Ответило источников",
        "random_generated": "Сгенерировано рандомных",
        "time_total": "Общее время работы: {0}м {1}с",
        "user_abort": "Работа была прервана пользователем.",
        "start": "[*] Запуск сбора прокси (Лимит потоков: {max_workers})",
        "fetch_err": "    [x] Ошибка {source}: {e}",
        "raw_found": "    [+] Сырых прокси собрано: {0}",
        "live_found": "    [✓] Живых прокси: {0}",
        "ipinfo": "    [ipinfo.io] Получены типы для {checked}/{total} ASN",
        "passed": "    [★] Уникальных IP:PORT прошедших все фильтры: {0}",
        "done": "\n[✓] Готово! Сохранение результатов...",
        "save_live": "[✓] Базовые списки по категориям сохранены в папку 'results_live/'",
        "cancel": "[!] Задача отменена пользователем",
        "no_candidates": "Нет прокси для проверки.",
        "db_not_found": "\n[!] Локальная база {0} не была найдена. Скачиваю (около 5MB)...",
        "db_outdated": "\n[!] Локальная база {0} устарела (старше 7 дней). Обновляю...",
        "db_success": "[✓] Локальная база успешно скачана/обновлена!",
        "db_error": "[x] Ошибка обновления базы (работаем без GeoIP): {0}",
        "check_asn": "    [ipinfo.io] Проверяю тип {0} уникальных ASN (Residential/Hosting)...",
        "check_ipapi": "    [ip-api.com] Определяю mobile/hosting для {0} IP...",
        "ipapi_success": "    [ip-api.com] Данные получены.",
        "classify_filter": "    Классифицирую и фильтрую прокси...",
        "db_load_err": "Ошибка загрузки локальной базы (попытка {0}): {1}",
        "db_corrupted": "Битый файл базы удалён, скачиваем заново...",
        "elite": "  [★ ЭЛИТНЫЙ] Прошел все фильтры: {proxy} ({proto}) - {country}",
        "working": "  [✓ РАБОЧИЙ] Найден: {proxy} ({proto}) - {country}"
    },
    "EN": {
        "log_unique_ip": "Unique IP:PORT",
        "random_generated": "Random generated",
        "start": "[*] Starting proxy collection (Thread limit: {max_workers})",
        "step1": "STEP 1: Async fetching from {0} sources...",
        "step4": "STEP 4: Generating random proxies...",
        "fetch_err": "    [x] Error {source}: {e}",
        "raw_found": "    [+] Raw proxies collected: {0}",
        "step2": "STEP 2: Basic live check...",
        "step5": "STEP 5: Basic live check for generated proxies...",
        "live_found": "    [✓] Live proxies: {0}",
        "step3": "STEP 3: Advanced filtering (Anon, Blacklists, Type)...",
        "tqdm_dl": "Downloading",
        "tqdm_check": "Checking",
        "tqdm_filter": "Filtering",
        "live_proxies": "Live proxies:",
        "elite_proxies": "Elite proxies passed all filters:",
        "sources_replied": "Sources replied",
        "time_total": "Total runtime: {0}m {1}s",
        "user_abort": "Task was aborted by user.",
        "ipinfo": "    [ipinfo.io] Fetched types for {checked}/{total} ASN",
        "passed": "    [★] Unique IP:PORT passed all filters: {0}",
        "done": "\n[✓] Done! Saving results...",
        "save_live": "[✓] Basic category lists saved to 'results_live/' folder",
        "cancel": "[!] Task cancelled by user",
        "no_candidates": "No proxies to check.",
        "db_not_found": "\n[!] Local database {0} not found. Downloading (about 5MB)...",
        "db_outdated": "\n[!] Local database {0} is outdated (older than 7 days). Updating...",
        "db_success": "[✓] Local database successfully downloaded/updated!",
        "db_error": "[x] Database update error (working without GeoIP): {0}",
        "check_asn": "    [ipinfo.io] Checking type of {0} unique ASNs (Residential/Hosting)...",
        "check_ipapi": "    [ip-api.com] Determining mobile/hosting for {0} IPs...",
        "ipapi_success": "    [ip-api.com] Data received.",
        "classify_filter": "    Classifying and filtering proxies...",
        "db_load_err": "Error loading local database (attempt {0}): {1}",
        "db_corrupted": "Corrupted database file deleted, downloading again...",
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
                 random_counts: Optional[Dict[str, int]] = None, lang: str = "RU", output_dir: str = ".",
                 github_token: str = "", github_tm_enabled: bool = True, github_tm_days: int = 1, ipinfo_token: str = ""):
        
        self.output_dir = output_dir
        self.lang = lang
        self.github_token = github_token
        self.github_tm_enabled = github_tm_enabled
        self.github_tm_days = github_tm_days
        self.ipinfo_token = ipinfo_token
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
        self.random_counts = random_counts or {'http': 0, 'https': 0, 'socks4': 0, 'socks5': 0}
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
        self.total_collected = 0
        
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

    def _dynamic_t(self, key):
        class DynamicText:
            def __str__(inner_self):
                return self._t(key)
        return DynamicText()
    def cancel(self):
        self._cancel_event.set()
        self.resume()  # Unblock paused threads

    def pause(self):
        self._pause_event.set()

    def resume(self):
        self._pause_event.clear()

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
            pbar = tqdm(total=len(SOURCES), desc=self._dynamic_t("tqdm_dl"))
        except ImportError:
            pbar = None
        def _fetch_and_parse(url, proto, fetch_timeout):
            content = ProxyUtils.fetch_url(url, fetch_timeout)
            if content:
                return proto, ProxyUtils.parse_proxies(content)
            return proto, []

        with ThreadPoolExecutor(max_workers=300) as ex:
            fmap = {}
            for url, proto in SOURCES:
                fetch_timeout = max(15, self.timeout)
                fmap[ex.submit(_fetch_and_parse, url, proto, fetch_timeout)] = url
                
            for fut in as_completed(fmap):
                if self._wait_if_paused(): break
                if self._cancel_event.is_set(): break
                url = fmap[fut]
                try:
                    proto, proxies = fut.result()
                except Exception:
                    if pbar: pbar.update(1)
                    continue
                if proxies:
                    ok_sources += 1
                    total_raw += len(proxies)
                    with self._lock:
                        for p in proxies:
                            if proto == 'all':
                                self.proxy_protocols[p].update(['http', 'socks4', 'socks5'])
                            else:
                                self.proxy_protocols[p].add(proto)
                if pbar: pbar.update(1)
        
        if pbar: pbar.close()
        print(f"    {self._t('sources_replied')}: {ok_sources}")
        print(f"    Уникальных IP:PORT после основного парсинга: {len(self.proxy_protocols)}")

        # МАШИНА ВРЕМЕНИ (отдельным шагом)
        if getattr(self, 'github_token', None) and getattr(self, 'github_tm_enabled', True):
            tm_days = getattr(self, "github_tm_days", 1)
            print(f"\n[*] Запуск Машины Времени GitHub (поиск коммитов за {tm_days*24} часа)...")
            
            limit_before = None
            try:
                r_before = requests.get("https://api.github.com/rate_limit", headers={"Authorization": f"token {self.github_token}", "Accept": "application/vnd.github.v3+json"}, timeout=5)
                if r_before.status_code == 200:
                    limit_before = r_before.json().get('resources', {}).get('core', {}).get('remaining')
            except Exception: pass
            
            history_sources = []
            rate_limits = []
            
            def _resolve_commits(item):
                url, proto = item
                if "raw.githubusercontent.com" in url or "cdn.jsdelivr.net" in url:
                    commits, limit_info = ProxyUtils.fetch_github_commits(url, self.github_token, tm_days*24)
                    return [(c, proto) for c in commits], limit_info
                return [], {}

            with ThreadPoolExecutor(max_workers=300) as ex:
                futures = [ex.submit(_resolve_commits, item) for item in SOURCES]
                for fut in as_completed(futures):
                    if self._cancel_event.is_set(): break
                    res_urls, limit_info = fut.result()
                    history_sources.extend(res_urls)
                    if limit_info and 'remaining' in limit_info:
                        rate_limits.append(limit_info)
            
            history_sources = list(dict.fromkeys(history_sources))
            
            limit_after, reset_time_epoch, total_limit = None, None, 5000
            try:
                r_after = requests.get("https://api.github.com/rate_limit", headers={"Authorization": f"token {self.github_token}", "Accept": "application/vnd.github.v3+json"}, timeout=5)
                if r_after.status_code == 200:
                    core = r_after.json().get('resources', {}).get('core', {})
                    limit_after = core.get('remaining')
                    reset_time_epoch = core.get('reset')
                    total_limit = core.get('limit')
            except Exception: pass
            
            if rate_limits:
                min_remaining = min(rate_limits, key=lambda x: int(x['remaining']))
                import datetime
                reset_time = datetime.datetime.fromtimestamp(int(min_remaining['reset'])).strftime('%H:%M:%S')
                limit_after_real = int(min_remaining['remaining'])
                total_limit_real = min_remaining.get('limit', '5000')
                used_session = (limit_before - limit_after_real) if (limit_before is not None and limit_before >= limit_after_real) else 0
                print(f"    [API INFO] Потрачено за сеанс: {used_session} | Остаток лимита: {limit_after_real}/{total_limit_real} | Сброс: {reset_time}")
            elif limit_after is not None and reset_time_epoch is not None:
                import datetime
                reset_time = datetime.datetime.fromtimestamp(int(reset_time_epoch)).strftime('%H:%M:%S')
                used_session = (limit_before - limit_after) if (limit_before is not None and limit_before >= limit_after) else 0
                print(f"    [API INFO] Потрачено за сеанс: {used_session} | Остаток лимита: {limit_after}/{total_limit} | Сброс: {reset_time}")
            
            print(f"    [+] Найдено {len(history_sources)} исторических файлов. Начинаем скачивание...")
            
            if history_sources:
                try:
                    pbar_hist = tqdm(total=len(history_sources), desc="Машина времени")
                except:
                    pbar_hist = None
                    
                ok_hist = 0
                with ThreadPoolExecutor(max_workers=300) as ex:
                    fmap = {}
                    for url, proto in history_sources:
                        fetch_timeout = max(15, self.timeout)
                        fmap[ex.submit(_fetch_and_parse, url, proto, fetch_timeout)] = url
                        
                    for fut in as_completed(fmap):
                        if self._wait_if_paused(): break
                        if self._cancel_event.is_set(): break
                        url = fmap[fut]
                        try:
                            proto, proxies = fut.result()
                        except Exception:
                            if pbar_hist: pbar_hist.update(1)
                            continue
                        if proxies:
                            ok_hist += 1
                            total_raw += len(proxies)
                            with self._lock:
                                for p in proxies:
                                    if proto == 'all':
                                        self.proxy_protocols[p].update(['http', 'socks4', 'socks5'])
                                    else:
                                        self.proxy_protocols[p].add(proto)
                        if pbar_hist: pbar_hist.update(1)
                
                if pbar_hist: pbar_hist.close()
                print(f"    Успешно скачано исторических файлов: {ok_hist}/{len(history_sources)}")
        print(f"    {self._t('log_unique_ip')}: {len(self.proxy_protocols)}")
        
        # Setup candidate generator for Pass 1
        def pass1_generator():
            for ip_port, protos in self.proxy_protocols.items():
                yield ip_port, list(protos)
        self.candidate_generator = pass1_generator()
        self.candidate_total = len(self.proxy_protocols)
        self.total_collected = self.candidate_total
    def collect_random(self):
        print(f"\n[+] " + self._t("step4"))
        rand_total = sum(self.random_counts.values())
        print(f"    {self._t('random_generated')}: {rand_total}")
        
        # Build patterns from filtered Pass 1 proxies
        patterns = {'http': [], 'https': [], 'socks4': [], 'socks5': []}
        if rand_total > 0:
            # BUG-FIX: Используем ВСЕ живые прокси для паттернов, а не только elite.
            # Раньше при выключенном DC сотни живых DC-прокси не попадали в паттерны,
            # и генератор "слепнул" — сканировал только резидентные подсети, где нечего ловить.
            pass1_final = []
            if hasattr(self, '_pass1_live_backup'):
                pass1_final.extend(self._pass1_live_backup)
            # Добавляем элитные тоже (могут содержать прокси, которых нет в live_backup)
            if hasattr(self, 'elite_results'):
                pass1_final.extend(self.elite_results)
            if hasattr(self, 'results_residential'):
                pass1_final.extend(self.results_residential)
            if hasattr(self, 'results_mobile'):
                pass1_final.extend(self.results_mobile)
            if hasattr(self, 'results_datacenter'):
                pass1_final.extend(self.results_datacenter)
                
            for uri in pass1_final:
                try:
                    if '://' in uri:
                        proto, ip_port = uri.split('://', 1)
                        # Безопасный парсинг: rsplit чтобы корректно обработать URI с @
                        if '@' in ip_port:
                            ip_port = ip_port.split('@', 1)[1]
                        # Отрезаем query string если есть
                        if '?' in ip_port:
                            ip_port = ip_port.split('?', 1)[0]
                        if '#' in ip_port:
                            ip_port = ip_port.split('#', 1)[0]
                        ip, port = ip_port.rsplit(':', 1)
                        parts = ip.split('.')
                        if len(parts) == 4 and all(p.isdigit() for p in parts):
                            subnet24 = f"{parts[0]}.{parts[1]}.{parts[2]}"
                            subnet16 = f"{parts[0]}.{parts[1]}"
                            if proto in patterns:
                                patterns[proto].append((subnet24, subnet16, port))
                except Exception:
                    pass
            # Deduplicate
            for p in patterns:
                patterns[p] = list(set(patterns[p]))
        
        # Создаем ленивый генератор кандидатов (Pipeline) только для рандомных
        def pass2_generator():
            for proto, ip_port in RandomProxyGenerator.generate_all(self.random_counts, patterns):
                yield ip_port, [proto]
                
        self.candidate_generator = pass2_generator()
        self.candidate_total = rand_total

    def validate(self, is_second_pass=False):
        if is_second_pass:
            print(f"\n[+] " + self._t("step5").format(self.candidate_total))
        else:
            print(f"\n[+] " + self._t("step2").format(self.candidate_total))
        import asyncio
        
        total = self.candidate_total
        if total == 0:
            print(f"    {self._t('no_candidates')}")
            return
            
        try: from tqdm import tqdm
        except ImportError: tqdm = None
        
        async def async_worker(item):
            if self._wait_if_paused(): return None
            ip_port, protos = item
            
            # Пропускаем зашифрованные конфиги напрямую в результаты
            if '://' in ip_port:
                scheme = ip_port.split('://', 1)[0].lower()
                if scheme in ('tg', 'https'): scheme = 'mtproto'
                ext_ip, _ = ProxyUtils.extract_ip_port(ip_port)
                if not re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', ext_ip):
                    return None
                if self.countries:
                    country = self._get_country(ext_ip)
                    if country.upper() not in self.countries:
                        return None
                return (ip_port, {scheme})
                
            ip, port_s = ip_port.rsplit(':', 1)
            
            # GeoIP Filter (moved BEFORE network ping to massively speed up filtering)
            if self.countries:
                country = self._get_country(ip)
                if country.upper() not in self.countries:
                    return None
                    
            working = await ProxyUtils.async_check_proxy(ip, int(port_s), protos, self.timeout)
            if working:
                if self._cancel_event.is_set(): return None
                if self._wait_if_paused(): return None
                return (ip_port, working)
            return None
            
        async def main_loop():
            loop = asyncio.get_running_loop()
            def silence_event_loop_closed(loop, context):
                exc = context.get('exception')
                if isinstance(exc, ConnectionResetError) and getattr(exc, 'winerror', None) == 10054: return
                msg = context.get('message', '')
                if 'Transport' in msg or 'SSL' in msg or 'socket' in msg.lower(): return
            loop.set_exception_handler(silence_event_loop_closed)
            
            queue = asyncio.Queue(maxsize=self.threads * 2)
            pbar = tqdm(total=total, desc=self._dynamic_t("tqdm_check")) if tqdm else None
            
            async def worker_task():
                while True:
                    item = await queue.get()
                    if item is None:
                        queue.task_done()
                        break
                        
                    if self._cancel_event.is_set():
                        if pbar: pbar.update(1)
                        queue.task_done()
                        continue
                        
                    try:
                        res = await async_worker(item)
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
                                        ip, port = ip_port.rsplit(':', 1)
                                        country = self.ip_cache.get(ip, {}).get('country', '') or self._get_country(ip)
                                        if ip not in self.ip_cache: self.ip_cache[ip] = {}
                                        self.ip_cache[ip]['country'] = country
                                        print(f"    [REALTIME_NEW_LIVE] {ip}|{port}|{p.upper()}|{country}")
                                if len(self.live_results) % 5 == 0 or len(self.live_results) < 10:
                                    print(f"    [REALTIME_LIVE] {len(self.live_results)}")
                    except Exception:
                        pass
                        
                    if pbar: pbar.update(1)
                    queue.task_done()
                    
            workers = [asyncio.create_task(worker_task()) for _ in range(self.threads)]
            
            for item in self.candidate_generator:
                if self._cancel_event.is_set():
                    break
                while self._pause_event.is_set() and not self._cancel_event.is_set():
                    await asyncio.sleep(0.5)
                await queue.put(item)
                
            for _ in range(self.threads):
                await queue.put(None)
                
            await queue.join()
            for w in workers:
                w.cancel()
            if pbar: pbar.close()
            
        # H-03 FIX: Safely run asyncio loops without conflicting with existing ones
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.run(main_loop())
        else:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                new_loop.run_until_complete(main_loop())
            finally:
                new_loop.close()
                asyncio.set_event_loop(loop)
        self.live_results = sorted(set(self.live_results))
        print(f"    {self._t('live_proxies')} {len(self.live_results)}")
    def _download_mmdb_if_needed(self):
        db_path = 'GeoLite2-Country.mmdb'
        needs_download = False
        
        if not os.path.exists(db_path):
            needs_download = True
            print(self._t("db_not_found").format(db_path))
        else:
            # Обновляем базу, если она старше 7 дней (604800 секунд)
            if time.time() - os.path.getmtime(db_path) > 604800:
                needs_download = True
                print(self._t("db_outdated").format(db_path))
                
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
                print(self._t("db_success"))
            except Exception as e:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                print(self._t("db_error").format(e))
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
        
        print(self._t("check_asn").format(len(unique_asns)))
        
        checked = 0
        for asn in unique_asns:
            if self._cancel_event.is_set(): break
            
            for attempt in range(3):
                try:
                    url = f"https://ipinfo.io/{asn}/json"
                    if getattr(self, 'ipinfo_token', ''):
                        url += f"?token={self.ipinfo_token}"
                    resp = requests.get(url, timeout=5,
                                        headers={'Accept': 'application/json', 'User-Agent': 'ProxyHunter/4.0'})
                    if resp.status_code == 200:
                        data = resp.json()
                        asn_type = data.get('type', '').lower()  # "isp", "hosting", "business"
                        if asn_type:
                            self.asn_cache[asn] = asn_type
                            checked += 1
                        break  # Успешно, выходим из цикла retry
                    elif resp.status_code in (400, 401, 403):
                        # Бесплатный Lite токен не имеет доступа к /json ASN API.
                        # Парсим HTML страницу напрямую.
                        html_url = f"https://ipinfo.io/{asn}"
                        resp_html = requests.get(html_url, timeout=10,
                                                 headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'})
                        if resp_html.status_code == 200:
                            import re
                            m = re.search(r'ASN type.*?>(ISP|Hosting|Business)<', resp_html.text, re.IGNORECASE)
                            if m:
                                self.asn_cache[asn] = m.group(1).lower()
                                checked += 1
                        break  # Выходим из цикла retry
                    elif resp.status_code == 429:
                        time.sleep(5)  # Rate limit — подождём и попробуем снова
                    else:
                        break  # Другая ошибка, нет смысла ретраить
                except Exception:
                    time.sleep(2)  # Сетевая ошибка, небольшая пауза
            
            time.sleep(0.5)  # Мягкий rate-limit для ipinfo.io

        
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
        # H-04 FIX: Добавляем rdns_dirty для обнаружения подозрительных hostname
        DIRTY_KEYWORDS = ['proxy', 'vpn', 'tor', 'exit', 'relay', 'anon', 'scan', 'bot', 'spam', 'abuse']
        rdns_dirty = any(kw in rdns for kw in DIRTY_KEYWORDS) if rdns else False
        # Защита от состояния гонки при записи из множества потоков
        with self._lock:
            if ip not in self.ip_cache: self.ip_cache[ip] = {}
            self.ip_cache[ip].update({'rdns': rdns, 'rdns_dirty': rdns_dirty, 'dnsbl': is_bl, 'bad_ports': has_bad_port})
            return self.ip_cache[ip].copy()
    async def async_run_single_filter(self, item: str) -> Optional[Tuple[str, str]]:
        if self._wait_if_paused(): return None
        if self._cancel_event.is_set(): return None
        
        try:
            proto, ipp = item.split('://', 1)
        except ValueError:
            return None
        
        encrypted_protos = ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto')
        
        if proto.lower() in encrypted_protos:
            ext_ip, _ = ProxyUtils.extract_ip_port(item)
            if ext_ip == "Config" or not re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', ext_ip):
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
        
        with self._lock:
            ip_info = self.ip_cache.get(ip, {}).copy()
        
        has_api_data = 'datacenter' in ip_info
        is_mobile_api = ip_info.get('mobile', False)
        is_hosting_api = ip_info.get('datacenter', False)
        
        asn_str = ip_info.get('asn', '')
        asn_num = asn_str.split()[0] if asn_str else ''
        asn_type = self.asn_cache.get(asn_num, '')
        
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
        
        if category == "Datacenter" and not getattr(self, 'collect_dc', True):
            return None
        if category == "Residential" and not getattr(self, 'collect_res', True):
            return None
        if category == "Mobile" and not getattr(self, 'collect_mob', True):
            return None
        
        import asyncio
        if proto.lower() not in encrypted_protos and self.max_ping > 0:
            import time
            try:
                ping_start = time.time()
                fut = asyncio.open_connection(ip, port)
                reader, writer = await asyncio.wait_for(fut, timeout=self.max_ping / 1000.0)
                writer.close()
                try: await writer.wait_closed()
                except Exception: pass
                ping_ms = (time.time() - ping_start) * 1000
                if ping_ms > self.max_ping:
                    return None
            except Exception:
                return None
        
        if self.check_smtp and proto.lower() not in encrypted_protos:
            proxy_proto = proto.lower()
            smtp_ok = False
            
            # Асинхронная проверка SMTP (Port 25)
            # Чтобы не усложнять SOCKS хэндшейки для произвольных портов (т.к. нужно переписывать байт-код для порта 25),
            # мы используем aiohttp если есть aiohttp_socks, иначе пропускаем тест для SOCKS
            if proxy_proto in ('socks4', 'socks5', 'socks5h'):
                proxy_url = f"{proxy_proto}://{ip}:{port}"
                try:
                    import aiohttp
                    from aiohttp_socks import ProxyConnector
                    connector = ProxyConnector.from_url(proxy_url)
                    async with aiohttp.ClientSession(connector=connector) as session:
                        for smtp_port in [25, 587]:
                            try:
                                async with session.get(f'http://portquiz.net:{smtp_port}', timeout=self.timeout) as resp:
                                    if resp.status == 200:
                                        smtp_ok = True
                                        break
                            except Exception: pass
                except (ImportError, ConnectionResetError):
                    # Если нет aiohttp_socks, считаем что SMTP тест не пройден, либо пройден условно
                    smtp_ok = True 
            else:
                proxy_url = f"http://{ip}:{port}"
                try:
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        for smtp_port in [25, 587]:
                            try:
                                async with session.get(f'http://portquiz.net:{smtp_port}', proxy=proxy_url, timeout=self.timeout) as resp:
                                    if resp.status == 200:
                                        smtp_ok = True
                                        break
                            except Exception: pass
                except Exception: pass
                
            if not smtp_ok:
                return None
        
        return (item, category)
    def advanced_filter(self, is_second_pass=False):
        if not self.live_results: return
        print(f"\n[+] " + self._t("step3").format(len(self.live_results)))
        
        # Собираем уникальные IP для пакетного запроса
        unique_ips = set()
        for r in self.live_results:
            ext_ip, _ = ProxyUtils.extract_ip_port(r)
            if ext_ip != "Config" and re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', ext_ip):
                unique_ips.add(ext_ip)
        
        # 1) ip-api.com — определяем mobile/hosting флаги для каждого IP
        print(self._t("check_ipapi").format(len(unique_ips)))
        self._batch_ip_info(unique_ips)
        print(self._t("ipapi_success"))
        
        # 2) ipinfo.io — определяем тип ASN (isp/hosting/business) для Residential-детекции
        self._batch_asn_type()
        print(self._t("classify_filter"))
        
        # ЖЕСТКИЙ ФИЛЬТР СТРАН ПОСЛЕ ОБНОВЛЕНИЯ ДАННЫХ ИЗ API
        if self.countries:
            valid_live = []
            for p in self.live_results:
                proto, ipp = p.split('://', 1)
                if proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                    ext_ip, _ = ProxyUtils.extract_ip_port(p)
                    c = self.ip_cache.get(ext_ip, {}).get('country') or self._get_country(ext_ip) if ext_ip != "Config" else "Unknown"
                else:
                    ip, _ = ipp.rsplit(':', 1)
                    c = self.ip_cache.get(ip, {}).get('country') or self._get_country(ip)
                if c.upper() in self.countries:
                    valid_live.append(p)
                else:
                    # Страна изменилась и теперь не подходит
                    proto, ipp = p.split('://', 1)
                    if proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                        ip, port = ProxyUtils.extract_ip_port(p)
                    else:
                        ip, port = ipp.rsplit(':', 1)
                    print(f"    [REALTIME_REMOVE_LIVE]|{proto}|{ip}|{port}")
            self.live_results = valid_live
            print(f"    [REALTIME_LIVE] {len(self.live_results)}")

        import asyncio
        try: from tqdm import tqdm
        except ImportError: tqdm = None
        
        strict_remove = set()
        
        async def main_loop():
            loop = asyncio.get_running_loop()
            def silence_event_loop_closed(loop, context):
                exc = context.get('exception')
                if isinstance(exc, ConnectionResetError) and getattr(exc, 'winerror', None) == 10054: return
                msg = context.get('message', '')
                if 'Transport' in msg or 'SSL' in msg or 'socket' in msg.lower(): return
            loop.set_exception_handler(silence_event_loop_closed)
            
            queue = asyncio.Queue(maxsize=self.threads * 2)
            pbar = tqdm(total=len(self.live_results), desc=self._dynamic_t("tqdm_filter")) if tqdm else None
            
            to_remove_live = set()
            
            async def worker_task():
                while True:
                    item = await queue.get()
                    if item is None:
                        queue.task_done()
                        break
                        
                    if self._cancel_event.is_set():
                        if pbar: pbar.update(1)
                        queue.task_done()
                        continue
                        
                    try:
                        res_tuple = await self.async_run_single_filter(item)
                        if res_tuple:
                            res, category = res_tuple
                            proto, ipp = res.split('://', 1)
                            if proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                                chk_ip, _ = ProxyUtils.extract_ip_port(res)
                                chk_country = (self.ip_cache.get(chk_ip, {}).get('country') or self._get_country(chk_ip)) if chk_ip != "Config" else "Unknown"
                            else:
                                chk_ip, _ = ipp.rsplit(':', 1)
                                chk_country = self.ip_cache.get(chk_ip, {}).get('country') or self._get_country(chk_ip)
                                
                            # Жесткий вторичный фильтр: отсекаем переопределенные страны
                            if self.countries and chk_country.upper() not in self.countries:
                                with self._lock:
                                    to_remove_live.add(res)
                                    strict_remove.add(res)
                            else:
                                with self._lock:
                                    self.elite_results.append(res)
                                    if category == "Datacenter": self.results_datacenter.append(res)
                                    elif category == "Residential": self.results_residential.append(res)
                                    elif category == "Mobile": self.results_mobile.append(res)
                                    
                                    # REALTIME вывод для GUI
                                    if proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                                        ext_ip, ext_port = ProxyUtils.extract_ip_port(res)
                                        print(f"    [REALTIME_NEW_ELITE] {ext_ip}|{ext_port}|{proto.upper()}|{chk_country}|{category}")
                                    else:
                                        ip, port = ipp.rsplit(':', 1)
                                        print(f"    [REALTIME_NEW_ELITE] {ip}|{port}|{proto}|{chk_country}|{category}")
                                    
                                    total_elite = len(self.elite_results)
                                    if total_elite % 2 == 0 or total_elite < 5:
                                        print(f"    [REALTIME_ELITE] {total_elite}")
                        else:
                            with self._lock:
                                to_remove_live.add(item)
                    except Exception:
                        with self._lock:
                            to_remove_live.add(item)
                            
                    if pbar: pbar.update(1)
                    queue.task_done()
                    
            workers = [asyncio.create_task(worker_task()) for _ in range(self.threads)]
            
            for item in self.live_results:
                if self._cancel_event.is_set():
                    break
                while self._pause_event.is_set() and not self._cancel_event.is_set():
                    await asyncio.sleep(0.5)
                await queue.put(item)
                
            for _ in range(self.threads):
                await queue.put(None)
                
            await queue.join()
            for w in workers:
                w.cancel()
            if pbar: pbar.close()
            
            return to_remove_live
            
        # H-03 FIX: Safely run asyncio loops without conflicting with existing ones
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            to_remove_live = asyncio.run(main_loop())
        else:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                to_remove_live = new_loop.run_until_complete(main_loop())
            finally:
                new_loop.close()
                asyncio.set_event_loop(loop)
        
        # We purposefully DO NOT remove to_remove_live from self.live_results.
        # Even if a proxy fails the anonymity/SMTP check (or timeouts during advanced check), 
        # it successfully passed the basic check and therefore is genuinely "Рабочий".
        # This keeps the "Рабочие" metrics and exported lists perfectly aligned with what was found.
        # HOWEVER: We MUST remove proxies that failed the strict secondary Country filter!
        for p in strict_remove:
            proto, ipp = p.split('://', 1)
            if proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                ip, port = ProxyUtils.extract_ip_port(p)
            else:
                ip, port = ipp.rsplit(':', 1)
            print(f"    [REALTIME_REMOVE_LIVE]|{proto}|{ip}|{port}")
        self.live_results = [p for p in self.live_results if p not in strict_remove]
            
        self.results_datacenter = sorted(set(self.results_datacenter))
        self.results_residential = sorted(set(self.results_residential))
        self.results_mobile = sorted(set(self.results_mobile))
        self.elite_results = sorted(set(self.elite_results))
        self.live_results = sorted(set(self.live_results))
        
        total_elite = len(self.elite_results)
        print(f"    {self._t('elite_proxies')} {total_elite} (DC: {len(self.results_datacenter)}, Res: {len(self.results_residential)}, Mob: {len(self.results_mobile)})")

    def _save_category(self, folder_name: str, results_list: List[str], description: str):
        full_path = os.path.join(self.output_dir, folder_name)
        os.makedirs(full_path, exist_ok=True)
        
        by_proto = defaultdict(list)
        for p in results_list:
            proto, ipp = p.split('://', 1)
            by_proto[proto.lower()].append(p)
            
        with open(os.path.join(full_path, 'all.txt'), 'w', encoding='utf-8') as f:
            f.write(f"# {description}: {len(results_list)}\n")
            for p in results_list: f.write(p + '\n')
            
        with open(os.path.join(full_path, 'all.csv'), 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # M-09 FIX: Non-hardcoded CSV headers
            writer.writerow(['Protocol', 'IP/Config', 'Port', 'Country'])
            for p in results_list:
                proto, ipp = p.split('://', 1)
                if proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                    ext_ip, ext_port = ProxyUtils.extract_ip_port(p)
                    ext_country = self.ip_cache.get(ext_ip, {}).get('country', 'Unknown') if ext_ip != "Config" else "Unknown"
                    writer.writerow([proto.upper(), ext_ip, ext_port, ext_country])
                else:
                    ip, port = ipp.rsplit(':', 1)
                    country = self.ip_cache.get(ip, {}).get('country', 'Unknown') or 'Unknown'
                    writer.writerow([proto.upper(), ip, port, country])
                
        unique_ips = set()
        for p in results_list:
            proto, ipp = p.split('://', 1)
            if proto.lower() not in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                unique_ips.add(ipp.rsplit(':', 1)[0])
        unique_ips = sorted(unique_ips)
        with open(os.path.join(full_path, 'all_ips.txt'), 'w', encoding='utf-8') as f:
            f.write(f"# {description} (Только уникальные IP): {len(unique_ips)}\n")
            for ip in unique_ips: f.write(ip + '\n')
                
        for proto, items in by_proto.items():
            with open(os.path.join(full_path, f'{proto}.txt'), 'w', encoding='utf-8') as f:
                f.write(f"# {description} ({proto.upper()}): {len(items)}\n")
                for p in items: f.write(p + '\n')
                
            with open(os.path.join(full_path, f'{proto}.csv'), 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Протокол', 'IP/Config', 'Port', 'Страна'])
                for p in items:
                    _, ipp = p.split('://', 1)
                    if proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                        ext_ip, _ = ProxyUtils.extract_ip_port(p)
                        country = self.ip_cache.get(ext_ip, {}).get('country') or self._get_country(ext_ip) if ext_ip != "Config" else "Unknown"
                        writer.writerow([proto.upper(), ipp, 'N/A', country])
                    else:
                        ip, port = ipp.rsplit(':', 1)
                        country = self.ip_cache.get(ip, {}).get('country') or self._get_country(ip)
                        writer.writerow([proto.upper(), ip, port, country])
                    
            proto_ips = set()
            for p in items:
                _, ipp = p.split('://', 1)
                if proto.lower() not in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                    proto_ips.add(ipp.rsplit(':', 1)[0])
            proto_ips = sorted(proto_ips)
            with open(os.path.join(full_path, f'{proto}_ips.txt'), 'w', encoding='utf-8') as f:
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
        
        # Очищаем старые результаты перед началом нового сбора
        import shutil
        for category in ['live', 'elite', 'datacenter', 'residential', 'mobile']:
            folder_path = os.path.join(self.output_dir, f"results_{category}")
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path, ignore_errors=True)
            
        for attempt in range(2):
            self._download_mmdb_if_needed()
            try:
                if os.path.exists('GeoLite2-Country.mmdb'):
                    import maxminddb as _mmdb
                    self.db_reader = _mmdb.open_database('GeoLite2-Country.mmdb')
                    break # Успешно открыли, выходим из цикла
            except Exception as e:
                print(self._t("db_load_err").format(attempt+1, e))
                self.db_reader = None
                try:
                    os.remove('GeoLite2-Country.mmdb')
                    print(self._t("db_corrupted"))
                except Exception:  # BUG-10 FIX: bare except
                    pass
            
        self.collect()
        if not self._cancel_event.is_set(): self.validate(is_second_pass=False)
        if not self._cancel_event.is_set(): self.advanced_filter(is_second_pass=False)
        
        # Save Pass 1 live results and clear them for Pass 2 so we don't re-filter them
        pass1_live = list(self.live_results)
        self._pass1_live_backup = list(pass1_live)  # backup for collect_random fallback
        self.live_results.clear()
        
        if not self._cancel_event.is_set() and sum(self.random_counts.values()) > 0:
            self.collect_random()
            if self.candidate_total > 0:
                self.validate(is_second_pass=True)
                if not self._cancel_event.is_set(): self.advanced_filter(is_second_pass=True)
        
        # Combine back
        self.live_results.extend(pass1_live)
        self.live_results = sorted(set(self.live_results))  # Fix duplicate discrepancy between GUI card and table
        
        if not self._cancel_event.is_set():  # BUG-FP35 FIX: не сохраняем при отмене
            self.save()
        m, s = divmod(int(time.time() - t0), 60)
        print("\n⏱   " + self._t("time_total").format(m, s))
        if self._cancel_event.is_set():
            print("❌ " + self._t("user_abort"))
        # C-02 FIX: Закрываем db_reader чтобы не было утечки файловых дескрипторов
        if hasattr(self, 'db_reader') and self.db_reader:
            try:
                self.db_reader.close()
            except Exception:
                pass
            self.db_reader = None
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