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
SOURCES = [    ('https://api.openproxylist.xyz/http.txt', 'http'),
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
    ('https://databay.com/api/v1/proxy-list?format=txt&country=US', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=http', 'http'),
    ('https://databay.com/api/v1/proxy-list?protocol=http', 'http'),
    ('https://free-proxy-list.net/', 'http'),
    ('https://free-proxy-list.net/anonymous-proxy.html', 'http'),
    ('https://free-proxy-list.net/uk-proxy.html', 'http'),
    ('https://hidemium.io/free-proxy', 'http'),
    ('https://litport.net/api/free-proxy', 'http'),
    ('https://proxy-spider.com/api/proxies.example.txt', 'http'),
    ('https://proxymania.su/free-proxy', 'http'),
    ('https://proxyspace.pro/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/BreakingTechFr/Proxy_Free/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/http/raw/all.txt', 'all'),
    ('https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt', 'http'),
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
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/proxylist.json', 'http'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/proxylist.txt', 'http'),
    ('https://raw.githubusercontent.com/yuceltoluyag/GoodProxy/main/raw.txt', 'http'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt', 'http'),
    ('https://spys.me/proxy.txt', 'http'),
    ('https://sunny9577.github.io/proxy-scraper/generated/http_proxies.txt', 'all'),
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
    ('https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt', 'https'),
    ('https://raw.githubusercontent.com/Noctiro/getproxy/master/file/https.txt', 'https'),
    ('https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/https.txt', 'https'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/https.txt', 'https'),
    ('https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt', 'https'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt', 'https'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt', 'https'),
    ('https://raw.githubusercontent.com/trio666/proxy-checker/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt', 'https'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt', 'https'),
    ('https://vakhov.github.io/fresh-proxy-list/https.txt', 'https'),
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
    ('https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Noctiro/getproxy/master/file/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Skillter/ProxyGather/refs/heads/master/proxies/working-proxies-socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks4.txt', 'socks4'),
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
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt', 'socks5'),
    ('https://spys.me/socks.txt', 'socks5'),
    ('https://sunny9577.github.io/proxy-scraper/generated/socks5_proxies.txt', 'socks5'),
    ('https://vakhov.github.io/fresh-proxy-list/socks5.txt', 'socks5'),
    # --- NEW SOCKS5 SOURCES ADDED ---
    ('https://raw.githubusercontent.com/proxylist-to/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/socks5/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5.txt', 'socks5'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5&proxy_format=protocolipport&format=text&anonymity=elite', 'socks5'),
    ('https://raw.githubusercontent.com/casals-ar/proxy-list/main/socks5', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=PL', 'socks5'),
    ('https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list', 'socks5'),
    ('https://api.proxyscrape.com/proxytable.php?type=socks5', 'socks5'),
    ('https://proxyscrape.com/free-proxy-list/germany#free-proxy-table', 'socks5'),
    ('https://databay.com/free-proxy-list/socks5', 'socks5'),
    ('https://proxyscrape.com/free-proxy-list', 'socks5'),
    ('https://wproxy.org/en/docs/rules/socks.html', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=7&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt', 'socks5'),
    ('https://httpie.io/docs/cli/other-notes', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=8&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=6&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://mullvad.net/en/help/socks5-proxy', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=5&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://aimultiple.com/socks5-proxies', 'socks5'),
    ('https://cocalc.com/github/TheSpeedX/PROXY-List/blob/master/socks5.txt', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=4&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=4&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=6&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite', 'socks5'),
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/scraped_proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/socks5.txt', 'socks5'),
    # --- RATE LIMITED BUT VALID (GEONODE/PROXYSCRAPE) ---
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5&proxy_format=ipport&format=text&timeout=3000', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=9&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=10&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=11&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=12&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=13&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=14&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=all&anonymity=elite', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=all&anonymity=anonymous', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=5&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=7&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=8&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=9&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=anonymous', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=anonymous', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=anonymous', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=4&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=anonymous', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=5&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=anonymous', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=6&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=anonymous', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=7&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=anonymous', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=8&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=anonymous', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=9&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=anonymous', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=US', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=GB', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=DE', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=FR', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=CA', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=BR', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=IN', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=ID', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=CN', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=JP', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=KR', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=VN', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=IR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=US', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=US', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=US', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=GB', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=GB', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=GB', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=DE', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=DE', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=DE', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=FR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=FR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=FR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=CA', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=CA', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=CA', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=BR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=BR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=BR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=IN', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=IN', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=IN', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=ID', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=ID', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=ID', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=CN', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=CN', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=CN', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=JP', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=JP', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=JP', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=KR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=KR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=KR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=VN', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=VN', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=VN', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=IR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=IR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=IR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=PL', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=PL', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=PL', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=TR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=TR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=TR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=IT', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=IT', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=IT', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=ES', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=ES', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=ES', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=NL', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=NL', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=NL', 'socks5'),
    # --- PASTEBIN/RENTRY SEARCH DORKING (DuckDuckGo HTML) ---
    ('https://html.duckduckgo.com/html/?q=site:pastebin.com+"socks5"+intext:"1080"&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:pastebin.com+"socks5://"+IP+PORT&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:pastebin.com+"proxy+list"+"socks5"&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:rentry.co+"socks5"&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:ghostbin.com+"socks5"&df=d', 'socks5'),
    ("https://raw.githubusercontent.com/proxyscrape/free-proxy-list/main/proxies/protocols/socks5/data.json", "socks5"),
    ("https://t.me/s/free_proxies_list_Socks5_http", "socks5"),
    ("https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset", "http"),
    ("https://raw.githubusercontent.com/ahahaabas/bulk-proxy-list/main/socks4.txt", "socks4"),
    ("https://t.me/s/socks5_proxy", "socks5"),
    ("https://proxy-tools.com/proxy/https", "http"),
    ("https://t.me/s/https_proxy_list", "http"),
    ("https://t.me/s/proxies_anonymous", "http"),
    ("http://free-proxy.cz/en/proxylist/country/all/https/ping/all", "http"),
    ("https://api.proxyscrape.com/v2/?request=getproxies&protocol=https&timeout=10000&country=all&simplified=true", "http"),
    ("https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all&simplified=true", "socks5"),
    ("https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all&ssl=all&anonymity=all", "socks5"),
    ("https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/clash.yml", "vless"),
    ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_nossl.txt", "http"),
    ("https://t.me/s/socks5_proxies", "socks5"),
    ("https://raw.githubusercontent.com/ahahaabas/bulk-proxy-list/main/http.txt", "http"),
    ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_transparent.txt", "http"),
    ("https://api.proxyscrape.com/proxytable.php?req=getproxies&country=all&proxytype=https", "http"),
    ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_ssl_elite.txt", "http"),
    ("https://raw.githubusercontent.com/proxyscrape/free-proxy-list/main/proxies/protocols/https/data.json", "http"),
    ("https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml", "vless"),
    ("https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt", "vless"),
    ("https://raw.githubusercontent.com/ahahaabas/bulk-proxy-list/main/socks5.txt", "socks5"),
    ("https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_anonymous.txt", "http"),
    ("https://proxy-tools.com/proxy/socks5", "socks5"),
    ("https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt", "socks5"),
    ("https://api.proxyscrape.com/v2/?request=getproxies&protocol=https&timeout=10000&country=all&ssl=all&anonymity=all", "http"),
    ("https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS.txt", "http"),
    ("https://hidemy.name/en/proxy-list/?type=s#list", "http"),
    ("https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt", "vless"),
    ("https://t.me/s/proxy_socks5_http_https", "socks5"),
    ("https://t.me/s/proxies_for_you", "http"),
    ("https://raw.githubusercontent.com/Hookzof/socks5_list/master/proxy.txt", "socks5"),
    ("https://t.me/s/proxy_list_pro", "http"),
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


# --- NEW VALIDATED AI SOURCES ---
SOURCES.extend([
    ('https://t.me/s/v2ray_free_conf', 'all'),
    ('https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_elite.txt', 'http'),
    ('https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/all_elite.txt', 'all'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=ipport&format=text&timeout=3000', 'http'),
    ('https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.json', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&speed=fast', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=https&speed=fast', 'https'),
    ('https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/xResults/RAW.txt', 'all'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/im-razvan/proxy_list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/KUTLime/ProxyList/main/ProxyList.txt', 'all'),
    ('https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/xResults/Proxies.txt', 'all'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=http&anonymity=elite', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks4&speed=fast', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&speed=fast', 'socks5'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=2000&country=GB&anonymity=elite', 'socks5'),
    ('https://spys.me/socks.txt', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=2000&country=FR&ssl=yes&anonymity=elite', 'http'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=2000&country=IN&anonymity=elite', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=2000&country=IN&ssl=yes&anonymity=elite', 'http'),
    ('https://t.me/s/daily_free_proxy', 'all'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=US&protocols=https', 'https'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=GB&protocols=https', 'https'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=DE&protocols=http', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=DE&protocols=socks4', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=FR&protocols=http', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=FR&protocols=https', 'https'),
    ('https://t.me/s/v2ray_proxies', 'all'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=IN&protocols=socks4', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=BR&protocols=socks4', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=IN&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=ID&protocols=http', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=GB&protocols=socks4', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=GB&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=DE&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=FR&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=BR&protocols=socks5', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=FR&protocols=socks4', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=CN&protocols=socks5', 'socks5'),
    ('https://litport.net/api/free-proxy?format=txt&protocol=http&country=PL', 'http'),
    ('https://litport.net/api/free-proxy?format=txt&protocol=socks4&country=CA', 'socks4'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=socks4&country=IR', 'socks4'),
    ('https://litport.net/api/free-proxy?format=txt&protocol=http&country=SG', 'http'),
    ('https://litport.net/api/free-proxy?format=txt&protocol=http&country=IN', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=https&country=IR', 'https'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=http&country=JP', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=socks5&country=IR', 'socks5'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=http&country=IN', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=http&country=CA', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=http&country=IT', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=socks4&country=ES', 'socks4'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=socks5&country=ES', 'socks5'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=http&country=SG', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=socks4&country=SG', 'socks4'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=http&country=KR', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=US&protocols=socks5', 'socks5'),
    ('https://hidemy.io/en/proxy-list/', 'all'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=US&protocols=socks4', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country=CN&protocols=socks4', 'socks4'),
    ('https://premiumproxy.net/full-proxy-list', 'all'),
    ('https://proxydb.net/?protocol=http&offset=360', 'http'),
    ('https://proxydb.net/?protocol=http&offset=375', 'http'),
    ('https://www.my-proxy.com/free-anonymous-proxy.html', 'http'),
    ('https://www.my-proxy.com/free-socks-5-proxy.html', 'socks5'),
    ('https://www.my-proxy.com/free-proxy-list-6.html', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=FR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=BR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=ID', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=IN', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=CN', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=IR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=KR', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=JP', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=SG', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=CA', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=PL', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=VN', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=GB', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=US', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=DE', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=NL', 'socks5'),
    ('https://advanced.name/freeproxy?type=socks5&page=2', 'socks5'),
    ('https://advanced.name/freeproxy?type=socks5&page=1', 'socks5'),
    ('https://www.my-proxy.com/free-transparent-proxy.html', 'http'),
])


SOURCES.extend([
    ('https://www.proxy-list.download/api/v1/get?type=http', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=https', 'https'),
    ('https://www.proxy-list.download/api/v1/get?type=socks4', 'socks4'),
    ('https://www.proxy-list.download/api/v1/get?type=socks5', 'socks5'),
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt', 'https'),
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Volodichev/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt', 'http'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt', 'https'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/im-razvan/proxy_list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/http/global/http_checked.txt', 'http'),
    ('https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks4/global/socks4_checked.txt', 'socks4'),
    ('https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/almroot/proxylist/master/list.txt', 'http'),
    ('https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt', 'all'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=anonymous', 'http'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=elite', 'http'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=5000&country=all&anonymity=elite', 'socks4'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=5000&country=all&anonymity=anonymous', 'socks4'),
    ('https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/casals-ar/proxy-list/main/http', 'http'),
    ('https://raw.githubusercontent.com/casals-ar/proxy-list/main/socks4', 'socks4'),
    ('https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/http/http.txt', 'http'),
    ('https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/socks4/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://www.proxy-list.download/api/v1/get?type=http&anon=elite', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=https&anon=elite', 'https'),
    ('https://www.proxy-list.download/api/v1/get?type=socks4&anon=elite', 'socks4'),
    ('https://www.proxy-list.download/api/v1/get?type=socks5&anon=elite', 'socks5'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=ipport&format=text&timeout=5000&ssl=yes', 'http'),
    ('https://cdn.jsdelivr.net/gh/TheSpeedX/PROXY-List@master/http.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/TheSpeedX/SOCKS-List@master/socks4.txt', 'socks4'),
    ('https://cdn.jsdelivr.net/gh/TheSpeedX/SOCKS-List@master/socks5.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/ShiftyTR/Proxy-List@master/http.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/ShiftyTR/Proxy-List@master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/nguywnben/daily-proxy-updates/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/nguywnben/daily-proxy-updates/main/proxies/https.txt', 'https'),
    ('https://raw.githubusercontent.com/nguywnben/daily-proxy-updates/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/nguywnben/daily-proxy-updates/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/http.txt', 'http'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Stable/http.txt', 'http'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Stable/https.txt', 'https'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Stable/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Stable/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/http.txt', 'http'),
    ('https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/https.txt', 'https'),
    ('https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/socks5.txt', 'socks5'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=ipport&format=text&timeout=2000', 'http'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5&proxy_format=ipport&format=text&timeout=2000', 'socks5'),
    ('https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_all.txt', 'http'),
    ('https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_ssl.txt', 'https'),
    ('https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/socks4_all.txt', 'socks4'),
    ('https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/socks5_all.txt', 'socks5'),
    ('https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/all_proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/proxyscrape/free-proxy-list/main/proxies/protocols/http/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxyscrape/free-proxy-list/main/proxies/protocols/https/data.txt', 'https'),
    ('https://raw.githubusercontent.com/proxyscrape/free-proxy-list/main/proxies/protocols/socks4/data.txt', 'socks4'),
    ('https://raw.githubusercontent.com/proxyscrape/free-proxy-list/main/proxies/protocols/socks5/data.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxyscrape/free-proxy-list/main/proxies/all/data.txt', 'all'),
    ('https://raw.githubusercontent.com/TheLime1/Validity/main/data/http.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/protocols/http/data.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/protocols/https/data.txt', 'https'),
    ('https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/protocols/socks4/data.txt', 'socks4'),
    ('https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/protocols/socks5/data.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/monosans/proxy-list@main/proxies/http.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/monosans/proxy-list@main/proxies/socks4.txt', 'socks4'),
    ('https://cdn.jsdelivr.net/gh/monosans/proxy-list@main/proxies/socks5.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/prxchk/proxy-list@main/http.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/prxchk/proxy-list@main/socks4.txt', 'socks4'),
    ('https://cdn.jsdelivr.net/gh/prxchk/proxy-list@main/socks5.txt', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&anonymityLevel=elite&speed=fast', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=https&anonymityLevel=elite&speed=fast', 'https'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks4&anonymityLevel=elite&speed=fast', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite&speed=fast', 'socks5'),
    ('https://raw.githubusercontent.com/adasd223/http-socks-proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/adasd223/http-socks-proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/adasd223/http-socks-proxy-list/main/socks5.txt', 'socks5'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text&protocol=http', 'http'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text&protocol=socks4', 'socks4'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text&protocol=socks5', 'socks5'),
    ('https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/HTTP.txt', 'http'),
    ('https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Unstable/http.txt', 'http'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Unstable/https.txt', 'https'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Unstable/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Unstable/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/zevtyardt/proxy-list/main/all.txt', 'all'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&speed=medium', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks4&speed=medium', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&speed=medium', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&anonymityLevel=transparent', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=transparent', 'socks5'),
    ('https://openproxylist.xyz/http.txt', 'http'),
    ('https://openproxylist.xyz/socks4.txt', 'socks4'),
    ('https://openproxylist.xyz/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/tiktok/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/tiktok/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/discord/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/discord/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/instagram/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/reddit/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/x/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/x/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/google/http.txt', 'http'),
    ('https://databay.com/api/v1/proxy-list?ssl=strict&protocol=http&format=txt', 'http'),
    ('https://databay.com/api/v1/proxy-list?ssl=strict&protocol=socks4&format=txt', 'socks4'),
    ('https://databay.com/api/v1/proxy-list?ssl=strict&protocol=socks5&format=txt', 'socks5'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/top-http.txt', 'http'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/summary.json', 'all'),
    ('https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt', 'socks5'),
    ('https://vakhov.github.io/fresh-proxy-list/proxylist.csv', 'all'),
    ('https://raw.githubusercontent.com/mishakorzik/Free-Proxy/main/proxy.txt', 'all'),
    ('https://raw.githubusercontent.com/SevenworksDev/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/SevenworksDev/proxy-list/main/proxies/https.txt', 'https'),
    ('https://raw.githubusercontent.com/SevenworksDev/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/SevenworksDev/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:textbin.net+"socks5://"+intext:"1080"&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:controlc.com+"proxy+list"+intext:"http"&df=d', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:rentry.co+"http://"+IP+PORT&df=d', 'http'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/all.txt', 'all'),
    ('https://html.duckduckgo.com/html/?q=intitle:"index+of"+inurl:"proxies.txt"&df=w', 'all'),
    ('https://html.duckduckgo.com/html/?q=intitle:"index+of"+inurl:"socks5.txt"&df=w', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=inurl:"/proxy/http.txt"+ext:txt&df=w', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:pastebin.com+"HTTP/1.1"+intext:"8080"&df=d', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:rentry.co+"SOCKS5"+intext:"1080"&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:ghostbin.com+"proxy+list"+ext:txt&df=w', 'all'),
    ('https://html.duckduckgo.com/html/?q=site:gist.githubusercontent.com+"proxy"+ext:txt&df=m', 'all'),
    ('https://html.duckduckgo.com/html/?q=site:gist.githubusercontent.com+"socks5"+ext:txt&df=m', 'socks5'),
    ('https://t.me/s/proxylist_update', 'all'),
    ('https://t.me/s/socks5_proxy_free', 'socks5'),
    ('https://t.me/s/Free_Proxies', 'all'),
    ('https://t.me/s/proxy_list_scraped', 'http'),
    ('https://t.me/s/daily_proxy_list', 'all'),
    ('https://t.me/s/v2ray_free_conf', 'socks5'),
    ('https://t.me/s/ProxyListFree', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:fofa.info+"port:1080"+"socks5"&df=w', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:fofa.info+"port:3128"+"Squid"&df=w', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:zoomeye.org+"http+proxy"+intext:"8080"&df=w', 'http'),
    ('http://pubproxy.com/api/proxy?limit=5&format=txt&http=true&country=US&type=http', 'http'),
    ('http://pubproxy.com/api/proxy?limit=5&format=txt&socks4=true&country=DE&type=socks4', 'socks4'),
    ('http://pubproxy.com/api/proxy?limit=5&format=txt&https=true&level=elite', 'https'),
    ('https://gitlab.com/haithamaouati/proxy-list/-/raw/main/http.txt', 'http'),
    ('https://gitlab.com/haithamaouati/proxy-list/-/raw/main/socks4.txt', 'socks4'),
    ('https://gitlab.com/haithamaouati/proxy-list/-/raw/main/socks5.txt', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:gitee.com+"proxy+list"+"socks5"&df=w', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:gitee.com+"free-proxy"+ext:txt&df=m', 'all'),
    ('https://api.proxyscrape.com/proxytable.php?req=getproxies&country=all&proxytype=http', 'http'),
    ('https://api.proxyscrape.com/proxytable.php?req=getproxies&country=all&proxytype=socks4', 'socks4'),
    ('https://api.proxyscrape.com/proxytable.php?req=getproxies&country=all&proxytype=socks5', 'socks5'),
])

SOURCES.extend([(f'http://proxydb.net/?protocol=http&offset={i}', 'http') for i in range(0, 751, 15)])
SOURCES.extend([(f'http://proxydb.net/?protocol=https&offset={i}', 'https') for i in range(0, 751, 15)])
SOURCES.extend([(f'http://proxydb.net/?protocol=socks4&offset={i}', 'socks4') for i in range(0, 751, 15)])
SOURCES.extend([(f'http://proxydb.net/?protocol=socks5&offset={i}', 'socks5') for i in range(0, 751, 15)])
SOURCES.extend([(f'https://www.my-proxy.com/free-proxy-list-{i}.html', 'http') for i in range(1, 11)])

# --- RECOVERED HISTORICAL SOURCES (DYNAMIC, 365-DAY FRESHNESS) ---
SOURCES.extend([
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks4&proxy_format=protocolonly&format=text&timeout=20000', 'socks4'),
    ('https://pastebin.com/raw/XJsxHu4D', 'http'),
    ('https://telegra.ph/Free-Proxy-List-for-Scraping-and-SEO-Updated-Daily-04-07', 'http'),
    ('https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_all.txt', 'http'),
    ('https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_eu.txt', 'http'),
    ('https://rootjazz.com/proxies/proxies.txt', 'http'),
    ('https://www.proxynova.com/proxy-server-list/', 'http'),
    ('https://raw.githubusercontent.com/26info/vless-proxy-list/main/working-proxies.txt', 'vless'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/all.json', 'http'),
    ('https://codeberg.org/dbarker/public-proxy-list/raw/branch/main/proxies.txt', 'http'),
    ('https://flashproxy.com/resources/free-proxies', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/socks5.txt', 'socks5'),
    ('https://proxyhub.me/en/all-free-proxy-list.html', 'http'),
    ('https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/http.txt', 'http'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=protocolonly&format=text&timeout=20000', 'http'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5&proxy_format=protocolonly&format=text&timeout=20000', 'socks5'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json', 'http'),
    ('https://proxylist.to/proxy-list.txt', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/all.txt', 'http'),
    ('https://raw.githubusercontent.com/theriturajps/proxy-list/main/proxies.txt', 'http'),
    ('https://bitbucket.org/vanholt-proxies/public-http-proxies/raw/main/README.md', 'http'),
    ('https://raw.githubusercontent.com/duckray-client/free-vless-keys/main/keys.txt', 'vless'),
    ('https://raw.githubusercontent.com/theriturajps/proxy-list/main/proxies.json', 'http'),
    ('https://raw.githubusercontent.com/saisuiu/uiu/main/free.txt', 'http'),
    ('https://raw.githubusercontent.com/vAHiD55555/ProxyScraper/main/proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.json', 'socks5'),
    ('https://proxyroller.com/api/proxies?protocol=http&anonymity=elite&limit=100', 'http'),
    ('https://raw.githubusercontent.com/hookzof/socks5_list/master/tg/mtproto.json', 'mtproto'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.json', 'socks4'),
    ('https://docs.google.com/spreadsheets/d/1guW73RgKLUcLUFGx9QRtqtAmbqMJG7aXKJGlT_XU2t4/export?format=csv', 'http')
])


class ProxyUtils:
    """Утилиты для работы с сетью и парсинга прокси"""
    
    PROXY_RE  = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3})[:\s,;|\"\']+(\d{1,5})\b')
    JSON_IP_FIRST = re.compile(r'(?:"ip"|"host"|"proxy")\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"[^}]*?(?:"port")\s*:\s*"?(\d{1,5})"?', re.IGNORECASE)
    JSON_PORT_FIRST = re.compile(r'(?:"port")\s*:\s*"?(\d{1,5})"?[^}]*?(?:"ip"|"host"|"proxy")\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"', re.IGNORECASE)
    # Значение в ячейке таблицы часто обёрнуто в инлайновую разметку:
    # <td class="ip-cell"><span class="ip-text">1.2.3.4</span></td>
    # <td><a href="/?port=80">80</a></td>
    # Старый TABLE_RE требовал, чтобы значение лежало прямо в <td>, и такие
    # источники давали ноль прокси при полностью корректном HTML.
    # Ни одна из групп повторения не может совпасть с пустой строкой (\s — один
    # пробельный символ, тег — минимум три), поэтому катастрофического
    # бэктрекинга здесь нет; проверено на 7.7 МБ таблицы за 89 мс.
    _TD_OPEN = r'<td[^>]*>\s*(?:<[^/>][^>]*>\s*)*'
    _TD_CLOSE = r'\s*(?:</[a-zA-Z]+>\s*)*</td>'
    TABLE_RE = re.compile(
        _TD_OPEN + r'(\d{1,3}(?:\.\d{1,3}){3})' + _TD_CLOSE + r'\s*' +
        _TD_OPEN + r'(\d{1,5})' + _TD_CLOSE,
        re.IGNORECASE | re.DOTALL)
    @staticmethod
    def _octet(part: str) -> Optional[int]:
        """Разбирает один октет IPv4 или возвращает None.

        COR-07: str.isdigit() истинен для любых Unicode-цифр, поэтому '٣.1.1.1'
        раньше проходил валидацию как настоящий адрес, а '².1.1.1' ронял int()
        с ValueError. Нужны строго ASCII-десятичные цифры.

        Ведущие нули тоже отклоняются: inet_aton трактует '010' как восьмеричное,
        то есть '010.1.1.1' и '10.1.1.1' — разные адреса, и запись с нулём
        обходила бы проверку приватных диапазонов ниже.
        """
        if not (1 <= len(part) <= 3 and part.isascii() and part.isdecimal()):
            return None
        if len(part) > 1 and part[0] == '0':
            return None
        value = int(part)
        return value if value <= 255 else None

    @staticmethod
    def is_valid(ip: str, port: int) -> bool:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        octets = [ProxyUtils._octet(p) for p in parts]
        if any(o is None for o in octets):
            return False
        if not 1 <= port <= 65535:
            return False
        # L-02 FIX: Block private/reserved IPs
        first, second = octets[0], octets[1]
        if first in (0, 10, 127) or first >= 224:
            return False
        if first == 172 and 16 <= second <= 31:
            return False
        if first == 192 and second == 168:
            return False
        if first == 169 and second == 254:
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
                    
                    # COR-06: одна битая запись не должна ронять разбор всего
                    # источника. Раньше исключение отсюда всплывало до внешнего
                    # `except Exception: pass` и обнуляло весь результат.
                    try:
                        if ip and port_str and port_str.isdigit():
                            port_int = int(port_str)
                            if cls.is_valid(ip, port_int):
                                found.add(f"{ip}:{port_str}")
                    except Exception:
                        pass


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
            
        for i, match in enumerate(re.finditer(r"Proxy\(['\"]([A-Za-z0-9+/=]+)['\"]\)", content)):
            try:
                decoded = base64.b64decode(match.group(1)).decode('utf-8').strip()
                if ':' in decoded:
                    ip, port = decoded.split(':', 1)
                    if port.isdigit() and cls.is_valid(ip, int(port)):
                        found.add(f"{ip}:{port}")
            except Exception:
                pass
            if i % 1000 == 0: time.sleep(0.001)

        # COR-06: JSON-регулярки существовали с самого начала, но не были
        # подключены. Без них оборванный или невалидный JSON давал ноль прокси:
        # PROXY_RE требует, чтобы порт шёл сразу за адресом, а в JSON между ними
        # стоит `","port":"`. Теперь такой текст всё-таки разбирается.
        for i, match in enumerate(cls.JSON_IP_FIRST.finditer(content)):
            ip, port = match.groups()
            try:
                if cls.is_valid(ip, int(port)): found.add(f"{ip}:{port}")
            except Exception:
                pass
            if i % 1000 == 0: time.sleep(0.001)

        for i, match in enumerate(cls.JSON_PORT_FIRST.finditer(content)):
            port, ip = match.groups()
            try:
                if cls.is_valid(ip, int(port)): found.add(f"{ip}:{port}")
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
    # Причины отказа GitHub API. Раньше любой не-200 просто не добавлял ничего
    # в результат, поэтому протухший токен, исчерпанный лимит и «за period
    # коммитов не было» давали одинаковое «Найдено 0 исторических файлов».
    GITHUB_TOKEN_REJECTED = "токен отклонён (401)"
    GITHUB_RATE_LIMITED = "лимит API исчерпан (403)"

    @classmethod
    def classify_github_status(cls, status: int, headers=None) -> str:
        """Человекочитаемая причина отказа GitHub API."""
        if status == 401:
            return cls.GITHUB_TOKEN_REJECTED
        if status == 403:
            # 403 у GitHub — и «кончился лимит», и «нет доступа». Отличаются
            # только по заголовку остатка: при исчерпанном лимите он ноль.
            remaining = (headers or {}).get('X-RateLimit-Remaining')
            if remaining is not None and str(remaining).strip() == '0':
                return cls.GITHUB_RATE_LIMITED
            return "доступ запрещён (403)"
        if status == 429:
            return cls.GITHUB_RATE_LIMITED
        if status == 404:
            return "репозиторий или файл не найден (404)"
        return f"HTTP {status}"

    # Страница ipinfo.io с описанием ASN распаковывается в ~700 КБ текста, а
    # единственное нужное слово («ISP» / «Hosting» / «Business») стабильно лежит
    # около 35 000-го символа — примерно 5% от начала. Замерено на AS15169,
    # AS24940, AS7922, AS20473: позиция 34539..34681 при длине 677..720 тыс.
    # символов. Поэтому читаем потоком и обрываем, как только нашли.
    #
    # Экономия НЕ в трафике: ipinfo отдаёт страницу gzip, по проводу это ~120 КБ
    # в обоих случаях. Выигрыш в объёме распаковки и разбора — а он даёт и время.
    # Замер на 10 ASN, по 3 прогона с чередованием порядка:
    #   страница целиком : медиана 7.72 c, разобрано 19.5 МБ
    #   поток с обрывом  : медиана 5.14 c, разобрано  1.4 МБ
    #   => 1.50x по времени, 14x по объёму разбора
    # Запас до 192 КБ — пятикратный резерв на случай, если вёрстку сдвинут.
    ASN_TYPE_RE = re.compile(r'ASN type.*?>\s*(ISP|Hosting|Business)\s*<', re.IGNORECASE)
    ASN_PAGE_READ_LIMIT = 192 * 1024

    @classmethod
    def asn_type_from_ipinfo(cls, asn: str, timeout: int = 10, attempts: int = 3,
                             cancel_event=None) -> Optional[str]:
        """Тип ASN с ipinfo.io: 'isp' / 'hosting' / 'business', иначе None.

        Читает ответ потоком и прекращает загрузку, как только слово найдено.
        Ретраит только 429 — остальные ответы и сетевые ошибки наружу не
        выпускает.
        """
        for attempt in range(attempts):
            if cancel_event is not None and cancel_event.is_set():
                return None
            resp = None
            try:
                resp = requests.get(
                    "https://ipinfo.io/" + asn, timeout=timeout, stream=True,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'})
                if resp.status_code == 429:
                    time.sleep(3 + attempt * 2)
                    continue
                if resp.status_code != 200:
                    return None

                buffer = ""
                for chunk in resp.iter_content(chunk_size=16384):
                    if not chunk:
                        continue
                    buffer += chunk.decode('utf-8', errors='ignore')
                    m = cls.ASN_TYPE_RE.search(buffer)
                    if m:
                        return m.group(1).lower()
                    if len(buffer) > cls.ASN_PAGE_READ_LIMIT:
                        return None
                return None
            except Exception:
                time.sleep(2)
            finally:
                if resp is not None:
                    try:
                        resp.close()
                    except Exception:
                        pass
        return None

    @classmethod
    def check_github_token(cls, token: str, timeout: int = 10) -> Tuple[bool, str, Optional[int]]:
        """Один запрос к /rate_limit до массовой рассылки.

        Возвращает (годен, причина, остаток лимита). Смысл в том, чтобы не
        отправлять 407 обречённых запросов, когда токен заведомо не принимается:
        причина у всех будет одна и та же, а узнать её можно за один вызов.
        """
        try:
            resp = requests.get(
                "https://api.github.com/rate_limit",
                headers={"Authorization": f"token {token}",
                         "Accept": "application/vnd.github.v3+json"},
                timeout=timeout)
        except Exception as exc:
            return False, cls.classify_fetch_error(exc), None

        if resp.status_code != 200:
            return False, cls.classify_github_status(resp.status_code, resp.headers), None

        try:
            core = resp.json().get('resources', {}).get('core', {})
            remaining = core.get('remaining')
        except Exception:
            remaining = None

        if remaining is not None and int(remaining) <= 0:
            return False, cls.GITHUB_RATE_LIMITED, 0
        return True, "", remaining

    @classmethod
    def fetch_github_commits(cls, url: str, token: str, hours_back: int = 24, cancel_event=None, pause_event=None) -> tuple:
        owner, repo, branch, path = None, None, None, None
        
        m_raw = re.match(r'https?://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.*)', url)
        if m_raw:
            owner, repo, branch, path = m_raw.groups()
            
        m_cdn = re.match(r'https?://cdn\.jsdelivr\.net/gh/([^/]+)/([^@/]+)(?:@([^/]+))?/(.*)', url)
        if m_cdn:
            owner, repo, branch, path = m_cdn.groups()
            if not branch: branch = "main"
            
        if not owner or not repo or not path:
            return [], {}, "не распознан как ссылка на GitHub"

        # SEC-05: owner/repo/path приходят из строки в SOURCES, которая правится
        # руками девятью «волнами». Раньше path подставлялся в URL как есть, и
        # '?' или '&' в нём превратились бы в лишние параметры запроса к GitHub
        # API — с нашим токеном в заголовке. Экранируем и валидируем.
        if not re.fullmatch(r'[A-Za-z0-9._-]+', owner) or not re.fullmatch(r'[A-Za-z0-9._-]+', repo):
            return [], {}, "недопустимое имя owner/repo"
        import urllib.parse
        path = urllib.parse.quote(path, safe='/')

        import datetime
        since_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/commits?path={path}&since={since_date}&per_page=100"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        
        commit_urls = []
        rate_limit = {}
        error = ""

        def _absorb_headers(resp):
            if 'X-RateLimit-Limit' in resp.headers:
                rate_limit['limit'] = resp.headers.get('X-RateLimit-Limit')
                rate_limit['remaining'] = resp.headers.get('X-RateLimit-Remaining')
                rate_limit['reset'] = resp.headers.get('X-RateLimit-Reset')
                rate_limit['used'] = resp.headers.get('X-RateLimit-Used')

        def _collect_shas(resp):
            for c in resp.json():
                sha = c.get('sha')
                if sha:
                    commit_urls.append(f"https://raw.githubusercontent.com/{owner}/{repo}/{sha}/{path}")

        try:
            resp = requests.get(api_url, headers=headers, timeout=10)
            _absorb_headers(resp)

            if resp.status_code == 200:
                _collect_shas(resp)
            else:
                # Раньше здесь молча не делалось ничего, и отказ был неотличим
                # от «за период коммитов не было».
                return [], rate_limit, cls.classify_github_status(resp.status_code, resp.headers)

            while 'next' in resp.links:
                resp = requests.get(resp.links['next']['url'], headers=headers, timeout=10)
                _absorb_headers(resp)
                if resp.status_code == 200:
                    _collect_shas(resp)
                else:
                    # Первая страница уже получена — отдаём её и называем причину,
                    # по которой обрыв случился на середине.
                    error = cls.classify_github_status(resp.status_code, resp.headers)
                    break
        except Exception as exc:
            return commit_urls, rate_limit, cls.classify_fetch_error(exc)

        return commit_urls, rate_limit, error

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
    # SEC-02: сертификаты источников проверяются по умолчанию. Раньше здесь стоял
    # безусловный verify=False, из-за чего активный MITM мог подменить содержимое
    # любого из 1710 источников и подсунуть пользователю свои точки выхода.
    # Флаг включается пользователем явно и разрешает ровно один повтор без
    # проверки — и только если запрос упал именно на SSLError.
    ALLOW_INSECURE_SOURCES = False
    _insecure_hosts_logged: Set[str] = set()
    _insecure_lock = threading.Lock()

    # PERF-03: сессия на поток — переиспользует TCP+TLS-соединение между
    # запросами. Раньше здесь был голый requests.get(), то есть каждый из ~1630
    # запросов открывал соединение заново и делал новый TLS-хендшейк. Запросы
    # сильно сконцентрированы по хостам (450 к advanced.name, 200 к proxydb.net,
    # 188 к geonode, десятки к raw.githubusercontent.com), поэтому пул окупается.
    # Замер: 15 запросов к одному хосту — 4.33 c против 1.89 c (−56%).
    # Сессия именно потоко-локальная: requests.Session не потокобезопасна, а
    # сбор идёт из пула на 50 воркеров.
    _thread_state = threading.local()

    @classmethod
    def _session(cls) -> "requests.Session":
        session = getattr(cls._thread_state, 'session', None)
        if session is None:
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=20)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            cls._thread_state.session = session
        return session

    @classmethod
    def _get_with_tls_policy(cls, url: str, headers: dict, timeout: int):
        """GET с проверкой TLS; при SSLError — опциональный повтор без проверки."""
        session = cls._session()
        # Куки не переносим между источниками: requests.get() их не хранил, и
        # накапливать чужие куки на 1600 запросов ни к чему.
        session.cookies.clear()
        try:
            return session.get(url, headers=headers, timeout=timeout, stream=True)
        except requests.exceptions.SSLError:
            if not cls.ALLOW_INSECURE_SOURCES:
                raise
            import urllib3
            import urllib.parse
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            host = urllib.parse.urlsplit(url).hostname or url
            with cls._insecure_lock:
                first_time = host not in cls._insecure_hosts_logged
                if first_time:
                    cls._insecure_hosts_logged.add(host)
            if first_time:
                print(f"    [!] TLS-сертификат {host} не прошёл проверку — "
                      f"источник загружен без проверки (включён режим небезопасных источников)")
            return session.get(url, headers=headers, timeout=timeout, stream=True, verify=False)

    @staticmethod
    def classify_fetch_error(exc: BaseException) -> str:
        """Короткая причина отказа источника — для сводки в логе.

        REL-05: fetch_url заканчивался `except Exception: return ''`, поэтому
        DNS, TLS, 403, 429 и таймаут были неотличимы от «источник пуст». Строка
        перевода fetch_err была объявлена в обоих языках и не использовалась
        нигде. При этом в репозитории лежат dead_github_sources.txt и
        stale_repos.txt — мёртвые источники были известной проблемой, которую
        нечем было диагностировать.
        """
        if isinstance(exc, requests.exceptions.SSLError):
            return "TLS"
        if isinstance(exc, requests.exceptions.Timeout):
            return "таймаут"
        if isinstance(exc, requests.exceptions.HTTPError):
            resp = getattr(exc, "response", None)
            return f"HTTP {resp.status_code}" if resp is not None else "HTTP"
        if isinstance(exc, requests.exceptions.ConnectionError):
            return "соединение"
        return type(exc).__name__

    @classmethod
    def fetch_url(cls, url: str, timeout: int = 10) -> str:
        """Скачивает источник. Пустая строка — не ответил или пуст."""
        return cls.fetch_url_with_error(url, timeout)[0]

    @staticmethod
    def fetch_url_with_error(url: str, timeout: int = 10) -> Tuple[str, str]:
        """Как fetch_url, но вторым элементом — причина отказа ('' если её нет)."""
        import random, time, json
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
            resp = ProxyUtils._get_with_tls_policy(url, headers, timeout)
            resp.raise_for_status()
            
            # COR-01: раньше здесь для application/json возвращался str(resp.json()) —
            # Python-repr словаря с одинарными кавычками. parse_proxies() не умеет
            # разбирать такой текст: JSON-ветка на нём падает, а PROXY_RE не может
            # перепрыгнуть через "', 'port': " между IP и портом. В итоге ~220 из
            # 1710 источников (в том числе 188 страниц Geonode) молча давали ноль.
            # Тело отдаётся как есть — parse_proxies сам разберёт и JSON, и текст.

            # Special parsing for Telegram
            if 't.me/s/' in url:
                html_text = resp.text
                import re
                # Extract text from tgme_widget_message_text
                messages = re.findall(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', html_text, re.IGNORECASE | re.DOTALL)
                # Remove html tags
                clean_text = '\\n'.join([re.sub(r'<[^>]+>', ' ', m) for m in messages])
                return clean_text, ''

            chunks, size = [], 0
            
            start_time = time.time()
            
            for chunk in resp.iter_content(chunk_size=8192):
                if time.time() - start_time > timeout:
                    break # Обрываем стрим, если сервер тянет время (защита от DDoS/Tarpit)
                chunks.append(chunk.decode('utf-8', errors='ignore'))
                size += len(chunk)
                # Увеличен лимит до 20 МБ, чтобы не ломать крупные JSON ответы и длинные списки
                if size > 20 * 1024 * 1024: break
            resp.close()
            return ''.join(chunks), ''
        except Exception as exc:
            return '', ProxyUtils.classify_fetch_error(exc)
    @staticmethod
    def tcp_ping(ip: str, port: int, timeout: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                sock.connect((ip, port))
                return True
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
                    
                elif proto == 'https':
                    # В списках прокси метка «https» означает не отдельный
                    # протокол, а HTTP-прокси, умеющий CONNECT — то есть
                    # туннелировать TLS. Ветки для него не было вовсе, и такой
                    # прокси проваливался мимо всех условий: функция возвращала
                    # None, то есть «не работает», каким бы живым он ни был.
                    # В SOURCES 104 источника помечены https.
                    req = b"CONNECT gstatic.com:443 HTTP/1.1\r\nHost: gstatic.com:443\r\n\r\n"
                    writer.write(req)
                    await writer.drain()
                    resp = await asyncio.wait_for(reader.read(1024), timeout=timeout)
                    # Успех — «HTTP/1.1 200 Connection established». Смотрим
                    # только статусную строку: тело может содержать что угодно.
                    status_line = resp.split(b"\r\n", 1)[0]
                    return status_line.startswith(b"HTTP/") and b" 200" in status_line

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

                # Явный возврат вместо неявного None: именно «провалиться мимо
                # всех веток» и было багом с https — тихое None читалось как
                # «не работает», и отличить его от настоящего отказа было
                # невозможно ни в коде, ни в логе.
                return False
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
        "save_live": "[✓] Базовые списки по категориям сохранены в папку 'results/'",
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
        "db_required": ("[x] ОСТАНОВЛЕНО: база GeoLite2-Country.mmdb недоступна.\n"
                        "    Без неё страна каждого прокси определяется как 'Unknown',\n"
                        "    и фильтр стран отбросил бы весь результат.\n"
                        "    Проверьте доступ в интернет либо положите GeoLite2-Country.mmdb\n"
                        "    рядом с программой и запустите сбор заново."),
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
        "db_required": ("[x] STOPPED: the GeoLite2-Country.mmdb database is unavailable.\n"
                        "    Without it every proxy resolves to country 'Unknown',\n"
                        "    and the country filter would discard the entire result.\n"
                        "    Check your internet access or place GeoLite2-Country.mmdb\n"
                        "    next to the program and start the run again."),
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
                 github_token: str = "", github_tm_enabled: bool = True, github_tm_days: int = 1,
                 allow_insecure_sources: Optional[bool] = None):
        
        self.output_dir = output_dir
        self.lang = lang
        self.github_token = github_token
        self.github_tm_enabled = github_tm_enabled
        self.github_tm_days = github_tm_days

        # None = «не трогать текущую политику». Так вспомогательный
        # ProxyHunter(threads=1), который GUI создаёт для чекера, не сбрасывает
        # флаг, выставленный запущенным сбором.
        if allow_insecure_sources is not None:
            ProxyUtils.ALLOW_INSECURE_SOURCES = bool(allow_insecure_sources)

        self.threads = threads
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
        self.open_geoip()
        self.total_collected = 0
        
        # Создаётся заново на каждый event loop — см. _reset_speed_semaphore().
        self._speed_sem = None

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
        """Ленивая строка перевода — подпись прогресс-бара следует за сменой языка.

        Настоящий tqdm обращается к desc как к обычной строке:
        `prefix[-2:] == ": "`, затем `prefix + ": "`. Раньше здесь был объект
        только с __str__, поэтому tqdm падал с
        `TypeError: 'DynamicText' object is not subscriptable`
        прямо в конструкторе прогресс-бара — то есть `python fetch_proxy.py`
        не доживал до первого источника. В GUI это не проявлялось: там
        patch_tqdm() подменяет tqdm заглушкой, которая только хранит desc.
        """
        outer = self

        class DynamicText:
            def _value(self) -> str:
                return outer._t(key)

            def __str__(self):
                return self._value()

            def __repr__(self):
                return repr(self._value())

            def __getitem__(self, item):
                return self._value()[item]

            def __len__(self):
                return len(self._value())

            def __bool__(self):
                return bool(self._value())

            def __add__(self, other):
                return self._value() + other

            def __radd__(self, other):
                return other + self._value()

            def __format__(self, spec):
                return format(self._value(), spec)

            def __eq__(self, other):
                return self._value() == other

            def __hash__(self):
                return hash(self._value())

        return DynamicText()
    def cancel(self):
        self._cancel_event.set()
        self.resume()  # Unblock paused threads

    def pause(self):
        self._pause_event.set()

    def resume(self):
        self._pause_event.clear()

    # Ограничение параллельных замеров скорости: тест качает 100 КБ через каждый
    # прокси, и без ограничения тысяча воркеров разом забьёт канал — все замеры
    # окажутся заниженными и живые прокси отсеются как «медленные».
    SPEED_TEST_CONCURRENCY = 30

    # Столько же, сколько использует аналогичный запрос в gui.py: ipinfo.io
    # отдаёт 429 при более агрессивном опросе.
    ASN_LOOKUP_WORKERS = 20

    def _reset_speed_semaphore(self):
        """Создаёт новый семафор замеров скорости для текущего event loop.

        COR-03: asyncio.Semaphore запоминает цикл, в котором впервые ждал, и
        бросает RuntimeError при попытке использовать его в другом. У нас
        validate() и advanced_filter() создают новый цикл на каждый проход,
        поэтому переиспользованный семафор на втором проходе падал. Исключение
        глотал внешний `except Exception: pass`, speed_ok оставался False — и
        ВСЕ сгенерированные прокси проваливали фильтр скорости.
        """
        import asyncio
        self._speed_sem = asyncio.Semaphore(self.SPEED_TEST_CONCURRENCY)

    def _wait_if_paused(self) -> bool:
        """Блокирует поток, пока стоит пауза. True — работа отменена.

        Только для обычных потоков (сбор источников). В корутинах используйте
        _await_if_paused: см. REL-02.
        """
        while self._pause_event.is_set() and not self._cancel_event.is_set():
            time.sleep(0.5)
        return self._cancel_event.is_set()

    async def _await_if_paused(self) -> bool:
        """Асинхронный вариант паузы. True — работа отменена.

        REL-02: раньше корутины звали синхронный _wait_if_paused с time.sleep,
        то есть первый же вставший на паузу воркер блокировал ВЕСЬ event loop.
        Пауза «работала» побочным эффектом: замирали и остальные воркеры, и
        обновление прогресса, при этом таймауты уже открытых соединений
        продолжали тикать — после снятия паузы часть живых прокси оказывалась
        отброшена как мёртвые.
        """
        import asyncio
        while self._pause_event.is_set() and not self._cancel_event.is_set():
            await asyncio.sleep(0.1)
        return self._cancel_event.is_set()
    GEOIP_DB_PATH = 'GeoLite2-Country.mmdb'

    def close_geoip(self):
        """Закрывает открытую базу GeoIP, если она есть."""
        reader, self.db_reader = getattr(self, 'db_reader', None), None
        if reader is not None:
            try:
                reader.close()
            except Exception:
                pass

    def open_geoip(self) -> bool:
        """Открывает базу GeoIP, предварительно закрыв предыдущую.

        REL-01: раньше база открывалась в __init__, а потом ещё раз в run() и в
        чекере GUI — старый объект просто перезаписывался. Каждый такой вызов
        оставлял открытый mmap на 8.4 МБ и файловый дескриптор; на Windows
        незакрытый хэндл вдобавок мешает os.replace() обновить сам файл базы.
        """
        self.close_geoip()
        try:
            import maxminddb
            if os.path.exists(self.GEOIP_DB_PATH):
                self.db_reader = maxminddb.open_database(self.GEOIP_DB_PATH)
        except Exception:
            self.db_reader = None
        return self.db_reader is not None

    def _get_country(self, ip: str) -> str:
        if hasattr(self, 'db_reader') and self.db_reader:
            try:
                geo_info = self.db_reader.get(ip)
                if geo_info and 'country' in geo_info:
                    return geo_info['country']['iso_code']
            except Exception:
                pass
        return 'Unknown'
    @staticmethod
    def _report_failures(failures: Dict[str, int], limit: int = 6,
                         label: str = "Не ответило источников"):
        """Печатает сводку причин отказа — агрегатом, а не строкой на источник."""
        total = sum(failures.values())
        if not total:
            return
        top = sorted(failures.items(), key=lambda kv: -kv[1])[:limit]
        detail = ", ".join(f"{reason} — {count}" for reason, count in top)
        if len(failures) > limit:
            detail += ", …"
        print(f"    [!] {label}: {total} ({detail})")

    def collect(self):
        # 32 URL перечислены в SOURCES под двумя протоколами сразу — один и тот
        # же файл качался и разбирался дважды. Группируем по URL: скачиваем
        # один раз, а найденные прокси помечаем всеми протоколами источника.
        # Содержимое proxy_protocols то же, запросов — на 32 меньше.
        by_url: Dict[str, Set[str]] = {}
        for url, proto in SOURCES:
            by_url.setdefault(url, set()).add(proto)

        print(f"\n[+] " + self._t("step1").format(len(by_url)))
        total_raw, ok_sources = 0, 0
        # REL-05: причины отказов, чтобы «не ответило N» перестало быть
        # безымянным числом. Копим агрегат, а не строку на каждый источник —
        # 400 сообщений в лог пользы не принесут.
        failures: Dict[str, int] = defaultdict(int)
        try:
            from tqdm import tqdm
            pbar = tqdm(total=len(by_url), desc=self._dynamic_t("tqdm_dl"))
        except ImportError:
            pbar = None
        def _fetch_and_parse(url, protos, fetch_timeout):
            # COR-05: задача могла простоять в очереди пула минуты — проверяем
            # отмену до того, как уйти в сеть на fetch_timeout секунд.
            if self._cancel_event.is_set():
                return protos, [], False, ''
            content, error = ProxyUtils.fetch_url_with_error(url, fetch_timeout)
            responded = bool(content)
            proxies = []
            if content:
                if 'html.duckduckgo.com' in url:
                    import urllib.parse
                    # Extract target URLs (Pastebin, Rentry, Ghostbin)
                    links = re.findall(r'href="([^"]+)"', content)
                    real_links = []
                    for l in links:
                        if 'uddg=' in l:
                            try:
                                parsed = urllib.parse.urlparse("https://html.duckduckgo.com" + l)
                                uddg = urllib.parse.parse_qs(parsed.query).get('uddg', [None])[0]
                                if uddg: real_links.append(urllib.parse.unquote(uddg))
                            except: pass
                        else:
                            real_links.append(l)
                            
                    # Filter for our targets
                    targets = [l for l in real_links if 'pastebin.com' in l or 'rentry.co' in l or 'ghostbin.com' in l]
                    for t_url in set(targets):
                        if 'rentry.co' in t_url and not t_url.endswith('/raw'): t_url += '/raw'
                        sub_content = ProxyUtils.fetch_url(t_url, fetch_timeout)
                        if sub_content:
                            proxies.extend(ProxyUtils.parse_proxies(sub_content))
                else:
                    proxies.extend(ProxyUtils.parse_proxies(content))
            return protos, proxies, responded, error

        def _record(protos, proxies):
            """Помечает найденные прокси всеми протоколами их источника."""
            with self._lock:
                for p in proxies:
                    for proto in protos:
                        if proto == 'all':
                            self.proxy_protocols[p].update(['http', 'socks4', 'socks5'])
                        else:
                            self.proxy_protocols[p].add(proto)

        # COR-05: раньше здесь стоял `with ThreadPoolExecutor(...)`. При отмене мы
        # выходили из цикла as_completed, но выход из блока вызывал
        # shutdown(wait=True) БЕЗ отмены очереди — и ждал все оставшиеся задачи
        # (до 1710 штук по 15 с таймаута каждая). Кнопка «Отмена» залипала на
        # минуты, хотя интерфейс уже рапортовал об остановке.
        ex = ThreadPoolExecutor(max_workers=50)
        try:
            fmap = {}
            for url, protos in by_url.items():
                fetch_timeout = max(15, self.timeout)
                fmap[ex.submit(_fetch_and_parse, url, protos, fetch_timeout)] = url

            for fut in as_completed(fmap):
                if self._wait_if_paused(): break
                if self._cancel_event.is_set(): break
                url = fmap[fut]
                try:
                    protos, proxies, responded, error = fut.result()
                    if responded:
                        ok_sources += 1
                    else:
                        failures[error or "пустой ответ"] += 1
                except Exception as exc:
                    failures[ProxyUtils.classify_fetch_error(exc)] += 1
                    if pbar: pbar.update(1)
                    continue

                if proxies:
                    total_raw += len(proxies)
                    _record(protos, proxies)
                    print(f"[REALTIME_TOTAL] {len(self.proxy_protocols)}")
                if pbar: pbar.update(1)
        finally:
            ex.shutdown(wait=False, cancel_futures=True)

        if pbar: pbar.close()
        print(f"    {self._t('sources_replied')}: {ok_sources}")
        self._report_failures(failures)

        # МАШИНА ВРЕМЕНИ (отдельным шагом)
        if getattr(self, 'github_token', None) and getattr(self, 'github_tm_enabled', True):
            tm_days = getattr(self, "github_tm_days", 1)
            print(f"\n[*] Запуск Машины Времени GitHub (поиск коммитов за {tm_days*24} часа)...")
            
            # Один запрос вместо 407 обречённых: если токен не принимается или
            # лимит уже исчерпан, причина у всех источников будет одна и та же.
            token_ok, token_error, limit_before = ProxyUtils.check_github_token(self.github_token)
            if not token_ok:
                print(f"    [x] Машина времени пропущена: {token_error}")
                if token_error == ProxyUtils.GITHUB_TOKEN_REJECTED:
                    print("        GitHub не принял токен — он мог истечь или быть отозван.")
                    print("        Создайте новый на github.com/settings/tokens (права не нужны)")
                    print("        и вставьте в настройках; либо снимите галочку «Машина времени».")
                elif token_error == ProxyUtils.GITHUB_RATE_LIMITED:
                    print("        Лимит запросов к GitHub API исчерпан. Он восстанавливается")
                    print("        раз в час; либо уменьшите глубину поиска в настройках.")
                history_sources = []
                rate_limits = []
            else:
                history_sources = []
                rate_limits = []
                gh_failures: Dict[str, int] = defaultdict(int)

                def _resolve_commits(item):
                    if self._cancel_event.is_set():
                        return [], {}, ""
                    url, proto = item
                    if "raw.githubusercontent.com" in url or "cdn.jsdelivr.net" in url:
                        commits, limit_info, error = ProxyUtils.fetch_github_commits(url, self.github_token, tm_days*24)
                        return [(c, proto) for c in commits], limit_info, error
                    return [], {}, ""

                ex = ThreadPoolExecutor(max_workers=50)
                try:
                    futures = [ex.submit(_resolve_commits, item) for item in SOURCES]
                    for fut in as_completed(futures):
                        if self._cancel_event.is_set(): break
                        try:
                            res_urls, limit_info, error = fut.result()
                        except Exception as exc:
                            gh_failures[ProxyUtils.classify_fetch_error(exc)] += 1
                            continue
                        if error:
                            gh_failures[error] += 1
                        history_sources.extend(res_urls)
                        if limit_info and 'remaining' in limit_info:
                            rate_limits.append(limit_info)
                finally:
                    ex.shutdown(wait=False, cancel_futures=True)   # COR-05

                self._report_failures(gh_failures, label="Не удалось прочитать историю")


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
            
            # Тот же приём, что и для основного списка: один URL — одно скачивание.
            hist_by_url: Dict[str, Set[str]] = {}
            for url, proto in history_sources:
                hist_by_url.setdefault(url, set()).add(proto)

            if hist_by_url:
                try:
                    pbar_hist = tqdm(total=len(hist_by_url), desc="Машина времени")
                except Exception:
                    pbar_hist = None

                ok_hist = 0
                ex = ThreadPoolExecutor(max_workers=50)
                try:
                    fmap = {}
                    for url, protos in hist_by_url.items():
                        fetch_timeout = max(15, self.timeout)
                        fmap[ex.submit(_fetch_and_parse, url, protos, fetch_timeout)] = url

                    for fut in as_completed(fmap):
                        if self._wait_if_paused(): break
                        if self._cancel_event.is_set(): break
                        url = fmap[fut]
                        try:
                            protos, proxies, responded, _error = fut.result()
                        except Exception:
                            if pbar_hist: pbar_hist.update(1)
                            continue
                        if proxies:
                            ok_hist += 1
                            total_raw += len(proxies)
                            _record(protos, proxies)
                        if pbar_hist: pbar_hist.update(1)
                finally:
                    ex.shutdown(wait=False, cancel_futures=True)   # COR-05

                if pbar_hist: pbar_hist.close()
                print(f"    Успешно скачано исторических файлов: {ok_hist}/{len(hist_by_url)}")
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
            if await self._await_if_paused(): return None
            ip_port, protos = item
            
            # Зашифрованные конфиги (vless/vmess/trojan/mtproto и прочие)
            if '://' in ip_port:
                scheme = ip_port.split('://', 1)[0].lower()
                if scheme in ('tg', 'https'): scheme = 'mtproto'
                ext_ip, ext_port = ProxyUtils.extract_ip_port(ip_port)
                if not re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', ext_ip):
                    return None
                country = self._get_country(ext_ip)
                if country.upper() in ("RU", "BY", "KZ", "UZ", "AM", "AZ", "KG", "MD", "TJ", "TM", "AF", "KP", "SO"):
                    return None
                if self.countries:
                    if country.upper() not in self.countries:
                        return None

                # Раньше здесь стоял безусловный return: конфиг попадал
                # в «Рабочие», не будучи проверенным вообще ничем, кроме
                # страны. Полноценно проверить vless/trojan без реализации
                # самого протокола нельзя, но подтвердить, что endpoint хотя бы
                # принимает соединения, можно и нужно — это нижняя планка,
                # общая с остальными протоколами.
                try:
                    port = int(ext_port)
                except (TypeError, ValueError):
                    # Порт не извлёкся: та же подстановка, что и в
                    # async_run_single_filter, чтобы поведение не расходилось.
                    port = 443
                if not await ProxyUtils.async_tcp_ping(ext_ip, port, self.timeout):
                    return None
                return (ip_port, {scheme})
                
            ip, port_s = ip_port.rsplit(':', 1)
            
            # GeoIP Filter (moved BEFORE network ping to massively speed up filtering)
            country = self._get_country(ip)
            if country.upper() in ("RU", "BY", "KZ", "UZ", "AM", "AZ", "KG", "MD", "TJ", "TM", "AF", "KP", "SO"):
                return None
            if self.countries:
                if country.upper() not in self.countries:
                    return None
                    
            working = await ProxyUtils.async_check_proxy(ip, int(port_s), protos, self.timeout)
            if working:
                if self._cancel_event.is_set(): return None
                if await self._await_if_paused(): return None
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

                    # REL-03: task_done() и pbar.update() обязаны выполниться даже
                    # если тело воркера бросит. Раньше они стояли после try/except,
                    # и любое исключение оттуда (например TclError из подменённого
                    # в GUI tqdm после закрытия окна) убивало воркер без
                    # task_done() — queue.join() ниже висел вечно, а вместе с ним
                    # и весь поток сбора.
                    try:
                        if self._cancel_event.is_set():
                            continue

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
                    finally:
                        try:
                            if pbar: pbar.update(1)
                        except Exception:
                            pass
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
        # PERF-01: было `[list(ips)[i:i+100] for i in ...]` — list(ips) строился
        # заново на КАЖДОЙ итерации, то есть O(n²) вместо O(n).
        # Замер: 50 000 IP — 272 мс против 1.33 мс (в 204 раза).
        ips_list = list(ips)
        chunks = [ips_list[i:i + 100] for i in range(0, len(ips_list), 100)]
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

        def _lookup(asn):
            return ProxyUtils.asn_type_from_ipinfo(asn, cancel_event=self._cancel_event)

        # PERF-02: раньше ASN опрашивались строго последовательно, да ещё с
        # time.sleep(0.5) после каждого. При 3000 уникальных ASN это ≥25 минут
        # на одном лишь шаге классификации. Точно такой же запрос в gui.py уже
        # был распараллелен на 20 воркеров — переносим сюда то же решение.
        checked = 0
        ex = ThreadPoolExecutor(max_workers=min(self.ASN_LOOKUP_WORKERS, len(unique_asns)))
        try:
            futures = {ex.submit(_lookup, asn): asn for asn in unique_asns}
            for fut in as_completed(futures):
                if self._cancel_event.is_set():
                    break
                try:
                    asn_type = fut.result()
                except Exception:
                    continue
                if asn_type:
                    with self._lock:
                        self.asn_cache[futures[fut]] = asn_type
                    checked += 1
        finally:
            ex.shutdown(wait=False, cancel_futures=True)

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
        # PERF-06: здесь стоял скан шести портов (21/22/23/25/3389/3128) с
        # таймаутом 1 c каждый. Его результат клался в кэш под ключом
        # 'bad_ports' и НЕ читался ничем: единственный потребитель этой функции
        # (проверка «Чистый» в чекере) смотрит только rdns_dirty и dnsbl.
        # Замер на реальных IP: PTR 0.27 c, DNSBL 1.95 c, скан портов 6.04 c —
        # то есть 69% времени уходило на значение, которое никто не спрашивал.
        # Признак сам по себе осмысленный, но включать его в критерий «чистоты»
        # значит менять результат проверки — вынесено в «Требует решения».

        # H-04 FIX: Добавляем rdns_dirty для обнаружения подозрительных hostname
        DIRTY_KEYWORDS = ['proxy', 'vpn', 'tor', 'exit', 'relay', 'anon', 'scan', 'bot', 'spam', 'abuse']
        rdns_dirty = any(kw in rdns for kw in DIRTY_KEYWORDS) if rdns else False
        # Защита от состояния гонки при записи из множества потоков
        with self._lock:
            if ip not in self.ip_cache: self.ip_cache[ip] = {}
            self.ip_cache[ip].update({'rdns': rdns, 'rdns_dirty': rdns_dirty, 'dnsbl': is_bl})
            return self.ip_cache[ip].copy()
    async def async_run_single_filter(self, item: str) -> Optional[Tuple[str, str]]:
        if await self._await_if_paused(): return None
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
        
        if self.min_speed > 0.0 and proto.lower() not in encrypted_protos:
            speed_ok = False
            proxy_url = f"{proto.lower()}://{ip}:{port}"
            try:
                import time
                import aiohttp
                import asyncio
                if getattr(self, '_speed_sem', None) is None:
                    self._reset_speed_semaphore()

                async with self._speed_sem:
                    start_time = time.time()
                    # 100KB payload from Cloudflare speed test (reliable)
                    speed_url = "http://speed.cloudflare.com/__down?bytes=100000"
                    if proto.lower() in ('socks4', 'socks5', 'socks5h'):
                        from aiohttp_socks import ProxyConnector
                        connector = ProxyConnector.from_url(proxy_url)
                        async with aiohttp.ClientSession(connector=connector) as session:
                            async with session.get(speed_url, timeout=self.timeout) as resp:
                                if resp.status == 200:
                                    data = await resp.read()
                                    duration = time.time() - start_time
                                    speed_mbps = (len(data) * 8) / (1024 * 1024) / duration if duration > 0 else 0
                                    if speed_mbps >= self.min_speed: speed_ok = True
                    else:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(speed_url, proxy=f"http://{ip}:{port}", timeout=self.timeout) as resp:
                                if resp.status == 200:
                                    data = await resp.read()
                                    duration = time.time() - start_time
                                    speed_mbps = (len(data) * 8) / (1024 * 1024) / duration if duration > 0 else 0
                                    if speed_mbps >= self.min_speed: speed_ok = True
            except Exception:
                pass
            
            if not speed_ok:
                return None

        
        if self.check_smtp and proto.lower() not in encrypted_protos:
            proxy_proto = proto.lower()
            smtp_ok = False
            
            try:
                import asyncio
                from python_socks.async_.asyncio import Proxy
                from python_socks import ProxyType
                import ssl
                
                ptype = ProxyType.SOCKS5
                if proxy_proto == 'socks4': ptype = ProxyType.SOCKS4
                elif proxy_proto == 'http': ptype = ProxyType.HTTP
                
                proxy = Proxy.create(proxy_type=ptype, host=ip, port=int(port))
                
                smtp_servers = [
                    ('smtp.gmail.com', 587, False),
                    ('smtp-mail.outlook.com', 587, False),
                    ('smtp.gmail.com', 465, True),
                    ('smtp.mail.yahoo.com', 465, True),
                ]
                
                for shost, sport, use_ssl in smtp_servers:
                    try:
                        sock = await asyncio.wait_for(proxy.connect(shost, sport), timeout=self.timeout)
                        context = None
                        if use_ssl:
                            context = ssl.create_default_context()
                            context.check_hostname = False
                            context.verify_mode = ssl.CERT_NONE
                            
                        reader, writer = await asyncio.open_connection(sock=sock, ssl=context, server_hostname=shost if use_ssl else None)
                        
                        banner = await asyncio.wait_for(reader.read(1024), timeout=self.timeout)
                        if banner[:3] == b'220':
                            smtp_ok = True
                        writer.close()
                        await writer.wait_closed()
                        
                        if smtp_ok: break
                    except Exception:
                        pass
            except ImportError:
                # Если нет python_socks, делаем поверхностную проверку через aiohttp на 587/465 порты
                try:
                    import aiohttp
                    proxy_url = f"http://{ip}:{port}" if proxy_proto == 'http' else f"{proxy_proto}://{ip}:{port}"
                    if proxy_proto in ('socks4', 'socks5', 'socks5h'):
                        from aiohttp_socks import ProxyConnector
                        connector = ProxyConnector.from_url(proxy_url)
                        session = aiohttp.ClientSession(connector=connector)
                    else:
                        session = aiohttp.ClientSession()
                        
                    async with session:
                        for smtp_port in [587, 465]:
                            kwargs = {"timeout": self.timeout}
                            if proxy_proto == 'http': kwargs["proxy"] = proxy_url
                            try:
                                async with session.get(f'http://portquiz.net:{smtp_port}', **kwargs) as resp:
                                    if resp.status == 200:
                                        smtp_ok = True
                                        break
                            except Exception: pass
                except Exception:
                    pass
            except Exception:
                pass
                
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
            
        # СРАЗУ категоризируем все рабочие прокси для UI (до проверки Elite/Speed/Ping)
        for p in self.live_results:
            try:
                proto, ipp = p.split('://', 1)
                is_enc = proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto')
                
                if is_enc:
                    ext_ip, ext_port = ProxyUtils.extract_ip_port(p)
                    ip = ext_ip if ext_ip != "Config" and re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', ext_ip) else "Config"
                    port = ext_port if ip != "Config" else 443
                else:
                    if ':' in ipp:
                        ip, port_s = ipp.rsplit(':', 1)
                        try: port = int(port_s)
                        except ValueError: port = 0
                    else:
                        continue
                
                if ip != "Config":
                    ip_info = self.ip_cache.get(ip, {})
                    has_api_data = 'datacenter' in ip_info
                    is_mobile_api = ip_info.get('mobile', False)
                    is_hosting_api = ip_info.get('datacenter', False)
                    asn_str = ip_info.get('asn', '')
                    asn_num = asn_str.split()[0] if asn_str else ''
                    asn_type = self.asn_cache.get(asn_num, '')
                    
                    if is_mobile_api: category = "Mobile"
                    elif asn_type == "isp": category = "Residential"
                    elif asn_type in ("hosting", "business"): category = "Datacenter"
                    elif not has_api_data: category = "Datacenter"
                    elif is_hosting_api: category = "Datacenter"
                    else: category = "Residential"
                else:
                    category = "Datacenter"
                    
                c = self.ip_cache.get(ip, {}).get('country') or self._get_country(ip) if ip != "Config" else "Unknown"
                
                with self._lock:
                    if category == "Datacenter": self.results_datacenter.append(p)
                    elif category == "Residential": self.results_residential.append(p)
                    elif category == "Mobile": self.results_mobile.append(p)
                    
                print(f"    [REALTIME_NEW_CATEGORY] {ip}|{port}|{proto.upper()}|{c}|{category}")
            except Exception:
                pass

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

            # COR-03: семафор обязан принадлежать этому циклу, а не тому,
            # что остался с первого прохода.
            self._reset_speed_semaphore()

            queue = asyncio.Queue(maxsize=self.threads * 2)
            pbar = tqdm(total=len(self.live_results), desc=self._dynamic_t("tqdm_filter")) if tqdm else None
            
            async def worker_task():
                while True:
                    item = await queue.get()
                    if item is None:
                        queue.task_done()
                        break

                    # REL-03: см. комментарий в validate() — task_done() обязан
                    # выполниться при любом исходе, иначе queue.join() зависает.
                    try:
                        if self._cancel_event.is_set():
                            continue

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
                                    strict_remove.add(res)
                            else:
                                with self._lock:
                                    self.elite_results.append(res)
                                    
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
                        # Прокси, не прошедший Elite/Speed/Ping, остаётся «рабочим»
                        # с первого этапа — из live_results его не убираем.
                    except Exception:
                        pass
                    finally:
                        try:
                            if pbar: pbar.update(1)
                        except Exception:
                            pass
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
        
        # Прокси, не прошедший анонимность/SMTP (или отвалившийся по таймауту на
        # расширенной проверке), базовую проверку всё-таки прошёл и остаётся
        # «Рабочим» — из live_results такие НЕ убираем.
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
        total_categorized = len(self.results_datacenter) + len(self.results_residential) + len(self.results_mobile)
        print(f"    {self._t('elite_proxies')} {total_elite} | Категоризировано: {total_categorized} (DC: {len(self.results_datacenter)}, Res: {len(self.results_residential)}, Mob: {len(self.results_mobile)})")

    def save(self):
        """Сохраняет результаты, подменяя папку results целиком и атомарно.

        REL-04: раньше run() начинался с shutil.rmtree(results), то есть старые
        результаты уничтожались ДО того, как получены новые. Упавший, отменённый
        или просто безрезультатный прогон оставлял пользователя и без старых
        данных, и без новых. Теперь пишем в соседнюю папку и переставляем её
        на место только после того, как всё записано.
        """
        import shutil

        final_path = os.path.join(self.output_dir, "results")
        staging_path = final_path + ".new"
        previous_path = final_path + ".old"

        shutil.rmtree(staging_path, ignore_errors=True)
        os.makedirs(staging_path, exist_ok=True)

        def _save_file(filename, data, desc):
            if not data: return
            with open(os.path.join(staging_path, filename), 'w', encoding='utf-8') as f:
                f.write(f"# {desc}: {len(data)}\n")
                for p in data: f.write(p + '\n')

        if self.live_results:
            _save_file('alive.txt', self.live_results, 'Живые прокси')
            print(self._t("save_live"))

        _save_file('elite.txt', getattr(self, 'elite_results', []), 'Elite Proxies')
        _save_file('datacenter.txt', getattr(self, 'results_datacenter', []), 'Datacenter Proxies')
        _save_file('residential.txt', getattr(self, 'results_residential', []), 'Residential Proxies')
        _save_file('mobile.txt', getattr(self, 'results_mobile', []), 'Mobile Proxies')

        # Переставляем папки. Окно, в котором results отсутствует, — это ровно
        # одно переименование, а не весь прогон.
        try:
            shutil.rmtree(previous_path, ignore_errors=True)
            if os.path.exists(final_path):
                os.rename(final_path, previous_path)
            os.rename(staging_path, final_path)
        except OSError as e:
            # Не смогли переставить (например, папка занята другим процессом) —
            # результаты уже на диске, сообщаем где именно.
            print(f"[x] Не удалось обновить папку {final_path}: {e}")
            print(f"    Результаты этого прогона лежат в {staging_path}")
            return
        finally:
            shutil.rmtree(previous_path, ignore_errors=True)
    def run(self):
        t0 = time.time()
        print("\n🚀 PROXYPULSE v4.0 (ADVANCED FILTERS)")

        # REL-04: старые результаты здесь больше не удаляются. Папка results
        # заменяется целиком в save(), уже после того как новые данные записаны,
        # — иначе упавший или отменённый прогон оставлял пользователя ни с чем.

        for attempt in range(2):
            # Файл базы нужно закрыть до скачивания: на Windows открытый mmap
            # не даёт os.replace() подменить его новой версией.
            self.close_geoip()
            self._download_mmdb_if_needed()
            try:
                if self.open_geoip():
                    break  # Успешно открыли, выходим из цикла
            except Exception as e:
                print(self._t("db_load_err").format(attempt + 1, e))
                self.close_geoip()
                try:
                    os.remove(self.GEOIP_DB_PATH)
                    print(self._t("db_corrupted"))
                except Exception:  # BUG-10 FIX: bare except
                    pass

        # COR-02: без открытой базы _get_country() возвращает 'Unknown', а фильтр
        # стран в validate() непустой всегда (есть список по умолчанию), поэтому
        # отбрасывались бы ВСЕ кандидаты. Раньше прогон молча заканчивался нулём
        # без единой ошибки в логе — самый дорогой в диагностике сценарий.
        if self.db_reader is None:
            print("\n" + self._t("db_required"))
            return

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
        
        if hasattr(self, 'elite_results'): self.elite_results = sorted(set(self.elite_results))
        if hasattr(self, 'results_datacenter'): self.results_datacenter = sorted(set(self.results_datacenter))
        if hasattr(self, 'results_residential'): self.results_residential = sorted(set(self.results_residential))
        if hasattr(self, 'results_mobile'): self.results_mobile = sorted(set(self.results_mobile))
        
        if not self._cancel_event.is_set():  # BUG-FP35 FIX: не сохраняем при отмене
            self.save()
        m, s = divmod(int(time.time() - t0), 60)
        print("\n⏱   " + self._t("time_total").format(m, s))
        if self._cancel_event.is_set():
            print("❌ " + self._t("user_abort"))
        # C-02 FIX: Закрываем db_reader чтобы не было утечки файловых дескрипторов
        self.close_geoip()
import datetime

# --- Start User's New Sources ---
NEW_SOURCES = [
    ('https://raw.githubusercontent.com/rxyzqc/SOCKS5-Proxy-Gen/main/socks5sites.txt', 'socks5'),
    ('https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/HyperBeats/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/manuGMG/proxy-365/main/SOCKS5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/databay-labs/free-proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/databay-labs/free-proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/databay-labs/free-proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/hproxy-com/free-proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/hproxy-com/free-proxy-list/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/hproxy-com/free-proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/hproxy-com/free-proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/GGboogie/PROXY-List/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/GGboogie/PROXY-List/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/GGboogie/PROXY-List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/BlackSnowDot/proxylist-update-every-minute/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/BlackSnowDot/proxylist-update-every-minute/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/BlackSnowDot/proxylist-update-every-minute/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/BlackSnowDot/proxylist-update-every-minute/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Dev-Team-V/Free-Proxies/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Dev-Team-V/Free-Proxies/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Dev-Team-V/Free-Proxies/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/EnoT-Hub/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/EnoT-Hub/proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/EnoT-Hub/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/RX4096/proxy-list/main/online/http.txt', 'http'),
    ('https://raw.githubusercontent.com/RX4096/proxy-list/main/online/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/RX4096/proxy-list/main/online/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt', 'http'),
    ('https://raw.githubusercontent.com/Bardiafa/Proxy-Leecher/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/AyoubSirai/proxy-list/main/proxy-list.txt', 'all'),
    ('https://raw.githubusercontent.com/joshua-ns/Proxy-Scraper/master/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/yixiu001/proxy-list/main/proxy.txt', 'all'),

    ('https://hproxy.com/api/proxy-list?format=txt&protocol=http', 'http'),
    ('https://hproxy.com/api/proxy-list?format=txt&protocol=https', 'https'),
    ('https://hproxy.com/api/proxy-list?format=txt&protocol=socks4', 'socks4'),
    ('https://hproxy.com/api/proxy-list?format=txt&protocol=socks5', 'socks5'),
    ('https://api.proxyscan.io/download?type=http', 'http'),
    ('https://api.proxyscan.io/download?type=https', 'https'),
    ('https://api.proxyscan.io/download?type=socks4', 'socks4'),
    ('https://api.proxyscan.io/download?type=socks5', 'socks5'),

    ('https://t.me/s/ProxySocks5Free', 'socks5'),
    ('https://t.me/s/proxies_http', 'http'),
    ('https://t.me/s/Proxy_List_2026', 'all'),
    ('https://t.me/s/Proxy_Scrap', 'all'),
    ('https://t.me/s/elite_proxies_list', 'all'),
    ('https://t.me/s/socks_proxy_net', 'socks5'),
    ('https://t.me/s/http_proxies_list', 'http'),
    ('https://t.me/s/free_proxy_world', 'all'),
    ('https://t.me/s/proxyhub_net', 'all'),

    ('https://html.duckduckgo.com/html/?q=site:pastebin.com+"HTTP/1.1+200+OK"+"8080"&df=d', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:rentry.co+"http_proxies"+"port"&df=d', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:justpaste.it+"proxy+list"+"elite"&df=d', 'all'),
    ('https://html.duckduckgo.com/html/?q=site:fofa.info+"HTTP+Proxy"+"X-Forwarded-For"&df=w', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:zoomeye.org+"squid"+"port:3128"&df=w', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:shodan.io+"HTTP/1.1+200+OK"+"Server:+squid"&df=w', 'http'),
]
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
NEW_SOURCES.append((f'https://checkerproxy.net/api/archive/{current_date}', 'all'))
SOURCES.extend(NEW_SOURCES)

MORE_SOURCES = [
    ('https://raw.githubusercontent.com/LalatinaHub/Proxy-List/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/parserpp/ip_ports/main/proxyinfo.txt', 'all'),
    ('https://raw.githubusercontent.com/itsallnans/proxy-list/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/Toffanello/Free-Proxy-List/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ahmadhasibul/Proxy-List/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/z2x-team/Proxy-List/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Zullis/free-proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/andig/proxylist/master/proxy.txt', 'http'),
    ('https://raw.githubusercontent.com/Spp001/Proxy-List/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/TheLime1/Validity/main/data/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/TheLime1/Validity/main/data/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/TheLime1/Validity/main/data/https.txt', 'https'),

    ('https://www.proxy-list.download/api/v1/get?type=http&anon=anonymous', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=http&anon=transparent', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=https&anon=anonymous', 'https'),
    ('https://www.proxy-list.download/api/v1/get?type=https&anon=transparent', 'https'),
    ('https://www.proxy-list.download/api/v1/get?type=socks4&anon=anonymous', 'socks4'),
    ('https://www.proxy-list.download/api/v1/get?type=socks5&anon=anonymous', 'socks5'),

    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&port=80', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&port=8080', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&port=3128', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&port=1080', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks4&port=4145', 'socks4'),

    ('https://t.me/s/free_proxies_socks5', 'socks5'),
    ('https://t.me/s/proxylist_24', 'all'),
    ('https://t.me/s/proxies_daily', 'all'),
    ('https://t.me/s/proksi_list', 'all'),
    ('https://t.me/s/Proxy_List_world', 'all'),
    ('https://t.me/s/proxy_socks5_free_vip', 'socks5'),
    ('https://t.me/s/socks5_proxy_list_http', 'all'),
    ('https://t.me/s/v2ray_vpn_configs', 'vless'),

    ('https://html.duckduckgo.com/html/?q=site:controlc.com+"socks5"+intext:"1080"&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:pastefs.com+"http+proxy"+intext:"8080"&df=d', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:hastebin.com+"proxy+list"+intext:"8080"&df=d', 'all'),
    ('https://html.duckduckgo.com/html/?q=site:dpaste.com+"socks5"+intext:"1080"&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:fofa.info+"Server:+tinyproxy"&df=w', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:fofa.info+"Server:+3proxy"&df=w', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:zoomeye.org+"3proxy"+"port:1080"&df=w', 'socks5')
]
SOURCES.extend(MORE_SOURCES)

THIRD_WAVE_SOURCES = [
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt', 'http'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/elite/http.txt', 'http'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/elite/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/elite/socks5.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/anonymity/elite/data.txt', 'all'),
    ('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/anonymity/anonymous/data.txt', 'all'),

    ('https://html.duckduckgo.com/html/?q=site:gitee.com+"proxy-list"+"http"&df=w', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:gitee.com+"socks5"+"1080"&df=w', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:gitlab.com+"proxies.txt"+"HTTP/1.1"&df=w', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:gitlab.com+"socks5.txt"+"port"&df=w', 'socks5'),

    ('https://t.me/s/free_proxy_ipv4', 'all'),
    ('https://t.me/s/proxylist4all', 'all'),
    ('https://t.me/s/premium_proxy_list', 'all'),
    ('https://t.me/s/proxy_server_list', 'all'),
    ('https://t.me/s/shadowsocks_free', 'socks5'),
    ('https://t.me/s/v2ray_custom', 'vless'),
    ('https://t.me/s/Best_Proxies_List', 'all'),

    ('https://raw.githubusercontent.com/Kitsun3Sec/ProxyList/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Kitsun3Sec/ProxyList/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Kitsun3Sec/ProxyList/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Nomad0x0/Awesome-Proxies/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/Toffanello/Free-Proxy-List/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Toffanello/Free-Proxy-List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/socks5.txt', 'socks5'),

    ('https://www.proxy-list.download/api/v1/get?type=http&country=US', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=http&country=GB', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=http&country=DE', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=socks5&country=US', 'socks5'),
    ('https://www.proxy-list.download/api/v1/get?type=socks5&country=RU', 'socks5'),

    ('https://html.duckduckgo.com/html/?q=intitle:"index+of"+inurl:"proxy.txt"&df=w', 'all'),
    ('https://html.duckduckgo.com/html/?q=intitle:"index+of"+inurl:"proxies/http.txt"&df=w', 'http'),
    ('https://html.duckduckgo.com/html/?q=intitle:"index+of"+inurl:"socks5.json"&df=w', 'socks5')
]
today = datetime.datetime.now()
yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
day_before_yesterday = (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
three_days_ago = (today - datetime.timedelta(days=3)).strftime("%Y-%m-%d")

THIRD_WAVE_SOURCES.extend([
    (f'https://checkerproxy.net/api/archive/{yesterday}', 'all'),
    (f'https://checkerproxy.net/api/archive/{day_before_yesterday}', 'all'),
    (f'https://checkerproxy.net/api/archive/{three_days_ago}', 'all')
])
SOURCES.extend(THIRD_WAVE_SOURCES)

FOURTH_WAVE_SOURCES = [
    ('https://raw.githubusercontent.com/NotUnko/Free-Proxy-List/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/TheVoidGroup/Proxy-List/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/TheVoidGroup/Proxy-List/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/TheVoidGroup/Proxy-List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/SlavaBogatov/proxy-list/main/proxies.txt', 'all'),

    ('https://html.duckduckgo.com/html/?q=intitle:"SilverBullet+Logs"+"proxy"&df=w', 'all'),
    ('https://html.duckduckgo.com/html/?q=intitle:"OpenBullet+Logs"+"proxies"&df=w', 'all'),
    
    ('https://html.duckduckgo.com/html/?q=site:0bin.net+"socks5"&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:zerobin.net+"8080"+OR+"3128"&df=d', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:paste.ee+"socks5"+intext:"1080"&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:paste.ubuntu.com+"HTTP/1.1+200+OK"&df=d', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:ideone.com+"proxy"+intext:"http"&df=d', 'http'),

    ('https://t.me/s/proxylist_premium', 'all'),
    ('https://t.me/s/free_proxies_list_2026', 'all'),
    ('https://t.me/s/MTProto_Proxy_List', 'socks5'),
    ('https://t.me/s/Socks5_Proxy_List_Vip', 'socks5'),
    ('https://t.me/s/Proxy_List_Free_VIP', 'all'),
    ('https://t.me/s/vpn_proxy_custom', 'all'),
    ('https://t.me/s/working_proxies', 'all'),

    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=1000&country=all&ssl=yes&anonymity=elite', 'http'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=1000&country=all&anonymity=elite', 'socks5'),

    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&speed=slow&anonymityLevel=transparent', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&speed=slow', 'socks5'),

    ('https://html.duckduckgo.com/html/?q=ext:log+"HTTP/1.1+200+OK"+"X-Forwarded-For"&df=w', 'http'),
    ('https://html.duckduckgo.com/html/?q=intitle:"index+of"+"proxies.txt"&df=d', 'all')
]
SOURCES.extend(FOURTH_WAVE_SOURCES)

FIFTH_WAVE_SOURCES = [
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&uptime=90', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=https&uptime=90', 'https'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks4&uptime=90', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&uptime=90', 'socks5'),

    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&ipType=ipv6', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&ipType=ipv6', 'socks5'),

    ('https://html.duckduckgo.com/html/?q=ext:yaml+"proxies:"+"type:+socks5"+"server:"&df=w', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=ext:yaml+"proxies:"+"type:+http"+"server:"&df=w', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:github.com+inurl:"clash.yaml"+"proxies"&df=w', 'all'),

    ('https://html.duckduckgo.com/html/?q=site:slexy.org+"socks5://"+port&df=w', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:paste2.org+"HTTP/1.1+200+OK"&df=w', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:rentry.co+"vmess://"&df=w', 'vless'),
    ('https://html.duckduckgo.com/html/?q=site:telegra.ph+"proxy+list"+intext:"8080"&df=w', 'http'),

    ('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt', 'all'),
    ('https://raw.githubusercontent.com/MuhammadBahaa2001/Proxy-List/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/T0x1cA114cK/Proxy-List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Bardiafa/Proxy-Leecher/main/good.txt', 'all'),
    ('https://raw.githubusercontent.com/fahimkawsar/proxy-list/main/proxy.txt', 'all'),

    ('https://t.me/s/free_proxy_socks5_http', 'all'),
    ('https://t.me/s/proxy_list_premium_free', 'all'),
    ('https://t.me/s/ProxyScraperList', 'all'),
    ('https://t.me/s/proxies_for_all', 'all'),
    ('https://t.me/s/openbullet_proxies', 'all'),

    ('https://www.proxy-list.download/api/v1/get?type=http&port=8080', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=http&port=3128', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=socks5&port=1080', 'socks5'),
    ('https://www.proxy-list.download/api/v1/get?type=socks4&port=4145', 'socks4')
]
SOURCES.extend(FIFTH_WAVE_SOURCES)

SIXTH_WAVE_SOURCES = [
    ('https://t.me/s/iran_proxy', 'all'),
    ('https://t.me/s/proxy_iran_socks5', 'socks5'),
    ('https://t.me/s/v2rayng_org', 'vless'),
    ('https://t.me/s/v2rayng_vpn', 'vless'),
    ('https://t.me/s/free_v2ray_config', 'vless'),
    ('https://t.me/s/V2ray_Alpha', 'vless'),
    ('https://t.me/s/Shadowsocks_Proxy_List', 'socks5'),
    ('https://t.me/s/vpn_fail', 'all'),
    ('https://t.me/s/vpn_fail_socks5', 'socks5'),
    ('https://t.me/s/free_proxy_list_socks5', 'socks5'),

    ('https://html.duckduckgo.com/html/?q=site:pastie.org+"socks5"+port&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:paste.fo+"HTTP/1.1"+intext:"8080"&df=d', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:textbin.net+"proxy"+"8080"&df=d', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:throwbin.io+"socks5"&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:justpaste.it+"socks4"&df=d', 'socks4'),

    ('https://t.me/s/HTTP_Proxy_List_Free', 'http'),
    ('https://t.me/s/Socks4_Proxy_List_Free', 'socks4'),
    ('https://t.me/s/Socks5_Proxy_List_Free', 'socks5'),
    ('https://t.me/s/HTTP_Proxy_List_Vip', 'http'),
    ('https://t.me/s/socks5_proxy_list_vip', 'socks5'),
    ('https://t.me/s/proxies_anonymous_elite', 'http'),

    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&anonymityLevel=elite&port=80', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite&port=1080', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks4&anonymityLevel=elite&port=4145', 'socks4'),

    ('https://raw.githubusercontent.com/Wannabe1337/Proxy-List/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/yuzhen123/Free-Proxy-List/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/sppeding/proxy-list/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/obfuskator/proxy-list/main/proxy.txt', 'all'),
    ('https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/tuanminpay/live-proxy/master/all.txt', 'all'),

    ('https://html.duckduckgo.com/html/?q=ext:txt+"HTTP/1.1+200+OK"+"Via:"+"Proxy"&df=w', 'http'),
    ('https://html.duckduckgo.com/html/?q=ext:txt+"socks5"+"auth:none"&df=w', 'socks5')
]
for days_back in range(4, 8):
    archive_date = (today - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d")
    SIXTH_WAVE_SOURCES.append((f'https://checkerproxy.net/api/archive/{archive_date}', 'all'))
SOURCES.extend(SIXTH_WAVE_SOURCES)

SEVENTH_WAVE_SOURCES = [
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=500&country=all&ssl=all&anonymity=elite', 'http'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=500&country=all&anonymity=elite', 'socks4'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=500&country=all&anonymity=elite', 'socks5'),

    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=speed&sort_type=asc&protocols=http', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=speed&sort_type=asc&protocols=https', 'https'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=speed&sort_type=asc&protocols=socks4', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=speed&sort_type=asc&protocols=socks5', 'socks5'),

    ('https://html.duckduckgo.com/html/?q=site:pastebin.pl+"socks5"+intext:"1080"&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:pastebin.pl+"http+proxy"+intext:"8080"&df=d', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:cl1p.net+"socks5"&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:cl1p.net+"proxy+list"+intext:"http"&df=d', 'http'),
    ('https://html.duckduckgo.com/html/?q=site:ghostbin.me+"socks5://"+port&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:ghostbin.me+"HTTP/1.1+200+OK"&df=d', 'http'),

    ('https://raw.githubusercontent.com/ViggoPro/proxy-list/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/Deybuhnt/proxylist/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt', 'https'),
    ('https://raw.githubusercontent.com/Zullis/free-proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Zullis/free-proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/EnoT-Hub/proxy-list/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/socks5.txt', 'socks5'),

    ('https://t.me/s/proxy_list_world_free', 'all'),
    ('https://t.me/s/free_proxy_list_vip', 'all'),
    ('https://t.me/s/proxy_socks5_http_https_vip', 'all'),
    ('https://t.me/s/proxies_scraper', 'all'),
    ('https://t.me/s/socks5_proxy_scraper', 'socks5'),
    ('https://t.me/s/proxy_list_100', 'all'),
    ('https://t.me/s/proxylist_update_24', 'all'),

    ('https://html.duckduckgo.com/html/?q=site:rentry.co+"SOCKS4"+intext:"1080"&df=w', 'socks4'),
    ('https://html.duckduckgo.com/html/?q=site:pastebin.com+ext:txt+"socks5"+intext:"1080"&df=d', 'socks5'),
    ('https://html.duckduckgo.com/html/?q=site:pastebin.com+ext:txt+"http_proxies"&df=d', 'http'),

    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=RU', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=UA', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country=KZ', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&country=RU', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&country=UA', 'http'),
]
SOURCES.extend(SEVENTH_WAVE_SOURCES)

EIGHTH_WAVE_SOURCES = [
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&google=true', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=https&google=true', 'https'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks4&google=true', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&google=true', 'socks5'),

    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=speed&sort_type=asc&protocols=socks5&google=true', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=speed&sort_type=asc&protocols=http&google=true', 'http'),

    ('https://t.me/s/Singbox_Config', 'vless'),
    ('https://t.me/s/xray_proxy', 'vless'),
    ('https://t.me/s/vless_vmess_trojan_shadowsocks', 'all'),
    ('https://t.me/s/Xray_VPN_Configs', 'vless'),
    ('https://t.me/s/reality_config', 'vless'),
    ('https://t.me/s/Singbox_Nodes', 'all'),

    ('https://t.me/s/free_proxy_socks5_http_https', 'all'),
    ('https://t.me/s/proxylist_2026_free', 'all'),
    ('https://t.me/s/socks4_proxy_list', 'socks4'),
    ('https://t.me/s/proxy_list_elite_anonymous', 'all')
]
SOURCES.extend(EIGHTH_WAVE_SOURCES)

NINTH_WAVE_SOURCES = [
    # New Working Github / CDN RAW
    ('https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.json', 'socks5'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Stable/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Unstable/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/TheLime1/Validity/main/data/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/adasd223/http-socks-proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/mishakorzik/Free-Proxy/main/proxy.txt', 'socks5'),
    ('https://raw.githubusercontent.com/theriturajps/proxy-list/main/proxies.txt', 'socks5'),
    ('https://raw.githubusercontent.com/theriturajps/proxy-list/main/proxies.json', 'socks5'),
    ('https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_all.txt', 'socks5'),
    ('https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_eu.txt', 'socks5'),
    ('https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/almroot/proxylist/master/list.txt', 'socks5'),
    ('https://raw.githubusercontent.com/saisuiu/uiu/main/free.txt', 'socks5'),
    ('https://raw.githubusercontent.com/vAHiD55555/ProxyScraper/main/proxies.txt', 'socks5'),
    ('https://raw.githubusercontent.com/duckray-client/free-vless-keys/main/keys.txt', 'socks5'),
    ('https://raw.githubusercontent.com/26info/vless-proxy-list/main/working-proxies.txt', 'socks5'),
    ('https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks5/global/socks5_checked.txt', 'socks5'),
    ('https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/xResults/RAW.txt', 'socks5'),
    ('https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/xResults/Proxies.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/KUTLime/ProxyList/main/ProxyList.txt', 'socks5'),
    ('https://raw.githubusercontent.com/SevenworksDev/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/nguywnben/daily-proxy-updates/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/nguywnben/daily-proxy-updates/main/proxies/https.txt', 'https'),
    ('https://raw.githubusercontent.com/nguywnben/daily-proxy-updates/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Stable/https.txt', 'https'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Unstable/https.txt', 'https'),
    ('https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/SevenworksDev/proxy-list/main/proxies/https.txt', 'https'),
    ('https://raw.githubusercontent.com/SevenworksDev/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/HTTP.txt', 'http'),
    ('https://raw.githubusercontent.com/TheLime1/Validity/main/data/http.txt', 'http'),
    ('https://raw.githubusercontent.com/adasd223/http-socks-proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/google/http.txt', 'http'),
    ('https://raw.githubusercontent.com/im-razvan/proxy_list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt', 'https'),
    ('https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/jetkai/proxy-list@main/online-proxies/txt/proxies-socks5.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/hookzof/socks5_list@master/proxy.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/TheSpeedX/PROXY-List@master/socks5.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/roosterkid/openproxylist@main/SOCKS5_RAW.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/monosans/proxy-list@main/proxies/socks5.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/prxchk/proxy-list@main/socks5.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/ShiftyTR/Proxy-List@master/socks5.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/zevtyardt/proxy-list@main/socks5.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/MuRongPIG/Proxy-Master@main/socks5.txt', 'socks5'),
    ('https://codeberg.org/dbarker/public-proxy-list/raw/branch/main/proxies.txt', 'socks5'),

    # APIs (returns JSON or HTML, requires custom parser if text regex doesn't match)
    ('https://api.proxy-checker.net/free-proxy/', 'socks5'),
    ('https://proxy-tools.com/proxy/socks5', 'socks5'),
    ('https://proxy-tools.com/proxy/https', 'https'),
    ('https://proxy-tools.com/proxy/http', 'http'),
    ('https://hidemy.io/en/proxy-list/', 'socks5'),
    ('https://iproyal.com/free-proxy-list/', 'socks5'),
    ('https://nodemaven.com/free-proxy-list/', 'socks5'),
    ('https://roundproxies.com/free-proxy-list/', 'socks5'),
    ('https://geonode.com/free-proxy-list/', 'socks5'),
    ('https://premiumproxy.net/full-proxy-list', 'socks5'),
    ('https://www.socks-proxy.net/', 'socks5'),
    ('https://free-proxy-list.net/en/socks-proxy.html', 'socks5'),
    ('https://spys.one/en/socks-proxy-list/', 'socks5'),
    ('https://spys.me/socks.txt', 'socks5'),
    ('http://ab57.ru/downloads/proxyold.txt', 'http'),

    # Telegram Channels
    ('https://t.me/s/socks5_proxy_free', 'socks5'),
    ('https://t.me/s/proxy_socks5_http_https', 'socks5'),
    ('https://t.me/s/proxy_list_pro', 'socks5'),
    ('https://t.me/s/proxylist_update', 'socks5'),
    ('https://t.me/s/socks5_proxies', 'socks5'),
    ('https://t.me/s/daily_free_proxy', 'socks5'),
    ('https://t.me/s/Free_Proxies', 'socks5'),
    ('https://t.me/s/proxy_list_scraped', 'socks5'),
    ('https://t.me/s/daily_proxy_list', 'socks5'),
    ('https://t.me/s/proxies_for_you', 'socks5'),
    ('https://t.me/s/proxies_anonymous', 'socks5'),
    ('https://t.me/s/https_proxy_list', 'https'),
    ('https://t.me/s/v2ray_proxies', 'socks5'),
    ('https://t.me/s/v2ray_free_conf', 'socks5'),
    ('https://t.me/s/ProxyListFree', 'socks5'),
    ('https://t.me/s/proxy_lists', 'socks5'),
]
SOURCES.extend(NINTH_WAVE_SOURCES)

# --- End User's New Sources ---

# COR-08: девять «волн» дописывались в SOURCES без сверки с уже добавленным,
# и 51 запись оказалась дублем (spys.me/socks.txt встречался трижды). Каждый
# дубль — это лишний HTTP-запрос с таймаутом до 15 c и повторный разбор ответа.
# dict.fromkeys сохраняет исходный порядок; правим список на месте, чтобы не
# осиротить ссылки на него.
# COR-09: три URL остались с неподставленным плейсхолдером `{p}` и уходили на
# сервер буквально, вместе с фигурными скобками. Разобрано по фактическому
# поведению каждого сайта (проверено запросами):
#   proxyhub.me      — пагинацию игнорирует, page=1/2/20/100 отдают одно и то же,
#                      поэтому остался один URL без параметра;
#   proxybros.com    — удалён по согласованию: список подгружается скриптом,
#                      из HTML не извлекается ничего ни на одной странице,
#                      а качалось при этом 205 КБ и 192 КБ за прогон;
#   freeproxy.world  — пагинация настоящая: 10 страниц дали 500 прокси без
#                      единого пересечения, поэтому развёрнут в диапазон.
SOURCES.extend([(f'https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page={i}', 'http')
                for i in range(1, 31)])

SOURCES[:] = list(dict.fromkeys(SOURCES))

def main():
    parser = argparse.ArgumentParser(description='ProxyPulse v4.0 - Advanced Filtration')
    parser.add_argument('--threads', type=lambda x: max(1, min(1000, int(x))), default=300, help='Количество потоков (макс. 1000)')
    parser.add_argument('--timeout', type=int, default=5, help='Таймаут соединения в секундах')
    parser.add_argument('--countries', default='US,CA,GB,AT,BE,BG,HR,CY,CZ,DK,EE,FI,FR,DE,GR,HU,IE,IT,LV,LT,LU,MT,NL,PL,PT,RO,SK,SI,ES,SE', type=str, help='Разрешенные страны через запятую')
    parser.add_argument('--max-ping', type=float, default=700, help='Макс пинг в мс')
    parser.add_argument('--min-speed', type=float, default=1.0, help='Мин скорость Мбит/с')
    parser.add_argument('--check-smtp', choices=['True', 'False'], default='True', help='Включить проверку SMTP портов (True/False)')
    parser.add_argument('--residential-only', action='store_true', help='Только residential/мобильные IP')
    parser.add_argument('--allow-insecure-sources', action='store_true',
                        help='Разрешить загрузку источников с непроверяемым TLS-сертификатом '
                             '(небезопасно: содержимое может быть подменено)')

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
        collect_mob=True,
        allow_insecure_sources=args.allow_insecure_sources
    )
    hunter.run()
if __name__ == '__main__':
    main()