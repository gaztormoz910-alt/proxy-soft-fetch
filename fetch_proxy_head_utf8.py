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
# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
#  ╨á╨É╨í╨¿╨ÿ╨á╨ò╨¥╨¥╨½╨Ö ╨í╨ƒ╨ÿ╨í╨₧╨Ü ╨ÿ╨í╨ó╨₧╨º╨¥╨ÿ╨Ü╨₧╨Æ (╨₧╨▒╤è╨╡╨┤╨╕╨╜╨╡╨╜╨╜╤ï╨╣)
# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
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
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc', 'http'),
    ('https://proxymania.su/free-proxy', 'http'),
    ('https://proxyspace.pro/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/BreakingTechFr/Proxy_Free/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/http/raw/all.txt', 'http'),
    ('https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Firmfox/Proxify/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/MrMarble/proxy-list/main/all.txt', 'http'),
    ('https://raw.githubusercontent.com/Noctiro/getproxy/master/file/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Skillter/ProxyGather/refs/heads/master/proxies/working-proxies-http.txt', 'http'),
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/all.txt', 'http'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/top-http.txt', 'http'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/berkay-digital/Proxy-Scraper/main/proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/http.txt', 'http'),
    ('https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/sources/auto.txt', 'http'),
    ('https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/sources/http.txt', 'http'),
    ('https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt', 'http'),
    ('https://raw.githubusercontent.com/iplocate/free-proxy-list/main/all-proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/http.txt', 'http'),
    ('https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt', 'http'),
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
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt', 'http'),
    ('https://raw.githubusercontent.com/stormsia/proxy-list/main/working_proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/themiralay/Proxy-List-World/master/data.txt', 'http'),
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
    ('https://sunny9577.github.io/proxy-scraper/generated/http_proxies.txt', 'http'),
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
# === ╨ƒ╨É╨ô╨ÿ╨¥╨É╨ª╨ÿ╨» (╨ö╨ÿ╨¥╨É╨£╨ÿ╨º╨ò╨í╨Ü╨ÿ╨ò ╨ÿ╨í╨ó╨₧╨º╨¥╨ÿ╨Ü╨ÿ) ===
# Advanced.name (╨┤╨╛ 150 ╤ü╤é╤Ç╨░╨╜╨╕╤å)
SOURCES.extend([(f'https://advanced.name/freeproxy?page={i}', 'http') for i in range(1, 151)])
SOURCES.extend([(f'https://advanced.name/freeproxy?type=socks4&page={i}', 'socks4') for i in range(1, 151)])
SOURCES.extend([(f'https://advanced.name/freeproxy?type=socks5&page={i}', 'socks5') for i in range(1, 151)])

# Geonode API (╨┤╨╛ 20 ╤ü╤é╤Ç╨░╨╜╨╕╤å, limit=500)
SOURCES.extend([(f'https://proxylist.geonode.com/api/proxy-list?limit=500&page={i}&sort_by=lastChecked&sort_type=desc', 'http') for i in range(1, 21)])

# PubProxy API (5 ╨╖╨░╨┐╤Ç╨╛╤ü╨╛╨▓ - ╨╗╨╕╨╝╨╕╤é ╨┤╨╗╤Å free-╨┐╨╛╨╗╤î╨╖╨╛╨▓╨░╤é╨╡╨╗╨╡╨╣)
SOURCES.extend([(f'http://pubproxy.com/api/proxy?limit=5&format=txt&http=true&level=anonymous,elite&type=http,socks4,socks5', 'http') for i in range(5)])

SOURCES.append(('https://good-proxies.ru/proxy-list/free/us/', 'http'))
class ProxyUtils:
    """╨ú╤é╨╕╨╗╨╕╤é╤ï ╨┤╨╗╤Å ╤Ç╨░╨▒╨╛╤é╤ï ╤ü ╤ü╨╡╤é╤î╤Ä ╨╕ ╨┐╨░╤Ç╤ü╨╕╨╜╨│╨░ ╨┐╤Ç╨╛╨║╤ü╨╕"""
    
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
        # ╨É╨▓╤é╨╛╨╝╨░╤é╨╕╤ç╨╡╤ü╨║╨╕╨╣ ╨┤╨╡╨║╨╛╨┤ Base64, ╨╡╤ü╨╗╨╕ ╨▓╨╡╤ü╤î ╨╛╤é╨▓╨╡╤é ╤ì╤é╨╛ ╨╖╨░╤ê╨╕╤ä╤Ç╨╛╨▓╨░╨╜╨╜╨░╤Å ╤ü╤é╤Ç╨╛╨║╨░
        stripped = content.replace('\n', '').replace('\r', '').strip()
        if len(stripped) > 20 and re.match(r'^[A-Za-z0-9+/]+={0,2}$', stripped):
            import base64
            try:
                content = base64.b64decode(stripped).decode('utf-8')
            except Exception:
                pass
        found = set()
        
        # ╨¿╨É╨ô 1: ╨ƒ╨╛╨┐╤ï╤é╨║╨░ ╤â╨╝╨╜╨╛╨│╨╛ ╨┐╨░╤Ç╤ü╨╕╨╜╨│╨░ JSON (╨╖╨░╤ë╨╕╤é╨░ ╨╛╤é ╨▓╨╗╨╛╨╢╨╡╨╜╨╜╤ï╤à ╤ü╤é╤Ç╤â╨║╤é╤â╤Ç)
        try:
            try: import orjson as json; data = json.loads(content)
            except: import json; data = json.loads(content)
            
            def extract_from_json(obj, depth=0):
                # ╨ù╨░╤ë╨╕╤é╨░ ╨╛╤é ╨▒╨╡╤ü╨║╨╛╨╜╨╡╤ç╨╜╨╛╨╣ ╤Ç╨╡╨║╤â╤Ç╤ü╨╕╨╕ ╨╜╨░ ╨│╨╗╤â╨▒╨╛╨║╨╛ ╨▓╨╗╨╛╨╢╨╡╨╜╨╜╤ï╤à API (monosans geolocation ~5 ╤â╤Ç╨╛╨▓╨╜╨╡╨╣)
                if depth > 5:
                    return
                if isinstance(obj, dict):
                    # ╨ÿ╨╖╨▓╨╗╨╡╨║╨░╨╡╨╝ IP: ╨┐╤Ç╨╕╨╛╤Ç╨╕╤é╨╡╤é ip > host > exit_ip
                    ip_val = obj.get('ip', obj.get('host', obj.get('exit_ip', '')))
                    # ╨ƒ╤Ç╨╛╨┐╤â╤ü╨║╨░╨╡╨╝ ╨║╨╗╤Ä╤ç 'proxy' ΓÇö ╨╛╨╜ ╤ç╨░╤ü╤é╨╛ ╤ü╨╛╨┤╨╡╤Ç╨╢╨╕╤é ╨┐╨╛╨╗╨╜╤ï╨╣ URI (proxyscrape) ╨╕╨╗╨╕ boolean (ip_data)
                    
                    # ╨Ü╨╛╨╜╨▓╨╡╤Ç╤é╨╕╤Ç╤â╨╡╨╝ ╨▓ ╤ü╤é╤Ç╨╛╨║╤â ╨╕ ╨▓╨░╨╗╨╕╨┤╨╕╤Ç╤â╨╡╨╝
                    ip = str(ip_val).strip() if ip_val is not None else ''
                    
                    port_val = obj.get('port', '')
                    port_str = str(port_val).strip() if port_val is not None else ''
                    
                    if ip and port_str and port_str.isdigit():
                        port_int = int(port_str)
                        if cls.is_valid(ip, port_int):
                            found.add(f"{ip}:{port_str}")
                    
                    # ╨á╨╡╨║╤â╤Ç╤ü╨╕╤Å ╤é╨╛╨╗╤î╨║╨╛ ╨▓ ╨╛╨▒╤è╨╡╨║╤é╤ï, ╨║╨╛╤é╨╛╤Ç╤ï╨╡ ╨▓╨╡╤Ç╨╛╤Å╤é╨╜╨╛ ╤ü╨╛╨┤╨╡╤Ç╨╢╨░╤é ╨┐╤Ç╨╛╨║╤ü╨╕-╨┤╨░╨╜╨╜╤ï╨╡
                    # (╨┐╤Ç╨╛╨┐╤â╤ü╨║╨░╨╡╨╝ ╨▓╨╗╨╛╨╢╨╡╨╜╨╜╤ï╨╡ ╨╝╨╡╤é╨░╨┤╨░╨╜╨╜╤ï╨╡ ╤é╨╕╨┐╨░ geolocation, ip_data, asn)
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
            # ╨ò╤ü╨╗╨╕ JSON ╤â╤ü╨┐╨╡╤ê╨╜╨╛ ╤Ç╨░╤ü╨┐╨░╤Ç╤ü╨╕╨╗╤ü╤Å ╨╕ ╨╝╤ï ╨╜╨░╤ê╨╗╨╕ ╨┐╤Ç╨╛╨║╤ü╨╕, ╨▓╨╛╨╖╨▓╤Ç╨░╤ë╨░╨╡╨╝ ╤Ç╨╡╨╖╤â╨╗╤î╤é╨░╤é (╨▒╨╡╨╖ Regex)
            if found:
                return list(found)
        except Exception:
            pass # ╨¥╨╡ ╨▓╨░╨╗╨╕╨┤╨╜╤ï╨╣ JSON ╨╕╨╗╨╕ ╨┐╤â╤ü╤é╨╛ ΓÇö ╨┐╨░╨┤╨░╨╡╨╝ ╨▓ Regex-╤ä╨╛╨╗╨▒╤ì╨║
            
                # ╨¿╨É╨ô 2: Fallback ╨╜╨░ ╤Ç╨╡╨│╤â╨╗╤Å╤Ç╨╜╤ï╨╡ ╨▓╤ï╤Ç╨░╨╢╨╡╨╜╨╕╤Å (╨┤╨╗╤Å ╤é╨╡╨║╤ü╤é╨╛╨▓╤ï╤à ╤ü╨┐╨╕╤ü╨║╨╛╨▓ ╨╕ ╤é╨░╨▒╨╗╨╕╤å)
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
            
        # ╨ƒ╨░╤Ç╤ü╨╕╨╜╨│ ╨╖╨░╤ê╨╕╤ä╤Ç╨╛╨▓╨░╨╜╨╜╤ï╤à ╨┐╤Ç╨╛╤é╨╛╨║╨╛╨╗╨╛╨▓ (VLESS, VMess, SS, Trojan, MTProto ╨╕ ╨┤╤Ç.)
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
        since_date = (datetime.datetime.utcnow() - datetime.timedelta(hours=hours_back)).isoformat() + 'Z'
        
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
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
            resp.raise_for_status()
            chunks, size = [], 0
            for chunk in resp.iter_content(chunk_size=8192):
                chunks.append(chunk.decode('utf-8', errors='ignore'))
                size += len(chunk)
                # ╨ú╨▓╨╡╨╗╨╕╤ç╨╡╨╜ ╨╗╨╕╨╝╨╕╤é ╨┤╨╛ 2 ╨£╨æ, ╤ç╤é╨╛╨▒╤ï ╨╜╨╡ ╨╗╨╛╨╝╨░╤é╤î ╨║╤Ç╤â╨┐╨╜╤ï╨╡ JSON ╨╛╤é╨▓╨╡╤é╤ï
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
                break # If one works, we stop testing others (like original logic)
        return working_protos
class RandomProxyGenerator:
    """╨ô╨╡╨╜╨╡╤Ç╨░╤é╨╛╤Ç ╤Ç╨░╨╜╨┤╨╛╨╝╨╜╤ï╤à IP:PORT ╨┤╨╗╤Å ╨╝╨░╤ü╤ü╨╛╨▓╨╛╨╣ ╨┐╤Ç╨╛╨▓╨╡╤Ç╨║╨╕"""
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
        import socket
        import struct
        
        while generated_count < count:
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
                # ╨£╨╕╨║╤ü ╨┐╨╛╤Ç╤é╨╛╨▓: 50% ╨╕╨╖ ╨┐╤â╨╗╨░, 50% ╨┐╨╛╨╗╨╜╨╛╤ü╤é╤î╤Ä ╤Ç╨░╨╜╨┤╨╛╨╝╨╜╤ï╨╡
                if random.random() < 0.5:
                    port = random.choice(pool)
                else:
                    port = random.randint(1, 65535)
                    
                yield f"{ip_str}:{port}"
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
        "log_unique_ip": "╨ú╨╜╨╕╨║╨░╨╗╤î╨╜╤ï╤à IP:PORT",
        "step1": "╨¿╨É╨ô 1: ╨É╤ü╨╕╨╜╤à╤Ç╨╛╨╜╨╜╤ï╨╣ ╤ü╨▒╨╛╤Ç ╨╕╨╖ {0} ╨╕╤ü╤é╨╛╤ç╨╜╨╕╨║╨╛╨▓...",
        "step1_5": "╨¿╨É╨ô 1.5: ╨ô╨╡╨╜╨╡╤Ç╨░╤å╨╕╤Å ╤Ç╨░╨╜╨┤╨╛╨╝╨╜╤ï╤à ╨┐╤Ç╨╛╨║╤ü╨╕...",
        "step2": "╨¿╨É╨ô 2: ╨æ╨░╨╖╨╛╨▓╨░╤Å ╨┐╤Ç╨╛╨▓╨╡╤Ç╨║╨░ {0} ╨┐╤Ç╨╛╨║╤ü╨╕ ╨╜╨░ ╨╢╨╕╨▓╨╛╤ü╤é╤î...",
        "step3": "╨¿╨É╨ô 3: ╨Ü╨╗╨░╤ü╤ü╨╕╤ä╨╕╨║╨░╤å╨╕╤Å ╨╕ ╤ä╨╕╨╗╤î╤é╤Ç╨░╤å╨╕╤Å {0} ╤Ç╨░╨▒╨╛╤ç╨╕╤à ╨┐╤Ç╨╛╨║╤ü╨╕...",
        "tqdm_dl": "╨ù╨░╨│╤Ç╤â╨╖╨║╨░",
        "tqdm_check": "╨ƒ╤Ç╨╛╨▓╨╡╤Ç╨║╨░",
        "tqdm_filter": "╨ñ╨╕╨╗╤î╤é╤Ç╨░╤å╨╕╤Å",
        "live_proxies": "╨û╨╕╨▓╤ï╤à ╨┐╤Ç╨╛╨║╤ü╨╕:",
        "elite_proxies": "╨¡╨╗╨╕╤é╨╜╤ï╤à ╨┐╤Ç╨╛╨║╤ü╨╕, ╨┐╤Ç╨╛╤ê╨╡╨┤╤ê╨╕╤à ╨▓╤ü╨╡ ╤ä╨╕╨╗╤î╤é╤Ç╤ï:",
        "sources_replied": "╨₧╤é╨▓╨╡╤é╨╕╨╗╨╛ ╨╕╤ü╤é╨╛╤ç╨╜╨╕╨║╨╛╨▓",
        "random_generated": "╨í╨│╨╡╨╜╨╡╤Ç╨╕╤Ç╨╛╨▓╨░╨╜╨╛ ╤Ç╨░╨╜╨┤╨╛╨╝╨╜╤ï╤à",
        "time_total": "╨₧╨▒╤ë╨╡╨╡ ╨▓╤Ç╨╡╨╝╤Å ╤Ç╨░╨▒╨╛╤é╤ï: {0}╨╝ {1}╤ü",
        "user_abort": "╨á╨░╨▒╨╛╤é╨░ ╨▒╤ï╨╗╨░ ╨┐╤Ç╨╡╤Ç╨▓╨░╨╜╨░ ╨┐╨╛╨╗╤î╨╖╨╛╨▓╨░╤é╨╡╨╗╨╡╨╝.",
        "start": "[*] ╨ù╨░╨┐╤â╤ü╨║ ╤ü╨▒╨╛╤Ç╨░ ╨┐╤Ç╨╛╨║╤ü╨╕ (╨¢╨╕╨╝╨╕╤é ╨┐╨╛╤é╨╛╨║╨╛╨▓: {max_workers})",
        "fetch_err": "    [x] ╨₧╤ê╨╕╨▒╨║╨░ {source}: {e}",
        "raw_found": "    [+] ╨í╤ï╤Ç╤ï╤à ╨┐╤Ç╨╛╨║╤ü╨╕ ╤ü╨╛╨▒╤Ç╨░╨╜╨╛: {0}",
        "live_found": "    [Γ£ô] ╨û╨╕╨▓╤ï╤à ╨┐╤Ç╨╛╨║╤ü╨╕: {0}",
        "ipinfo": "    [ipinfo.io] ╨ƒ╨╛╨╗╤â╤ç╨╡╨╜╤ï ╤é╨╕╨┐╤ï ╨┤╨╗╤Å {checked}/{total} ASN",
        "passed": "    [Γÿà] ╨ú╨╜╨╕╨║╨░╨╗╤î╨╜╤ï╤à IP:PORT ╨┐╤Ç╨╛╤ê╨╡╨┤╤ê╨╕╤à ╨▓╤ü╨╡ ╤ä╨╕╨╗╤î╤é╤Ç╤ï: {0}",
        "done": "\n[Γ£ô] ╨ô╨╛╤é╨╛╨▓╨╛! ╨í╨╛╤à╤Ç╨░╨╜╨╡╨╜╨╕╨╡ ╤Ç╨╡╨╖╤â╨╗╤î╤é╨░╤é╨╛╨▓...",
        "save_live": "[Γ£ô] ╨æ╨░╨╖╨╛╨▓╤ï╨╡ ╤ü╨┐╨╕╤ü╨║╨╕ ╨┐╨╛ ╨║╨░╤é╨╡╨│╨╛╤Ç╨╕╤Å╨╝ ╤ü╨╛╤à╤Ç╨░╨╜╨╡╨╜╤ï ╨▓ ╨┐╨░╨┐╨║╤â 'results_live/'",
        "cancel": "[!] ╨ù╨░╨┤╨░╤ç╨░ ╨╛╤é╨╝╨╡╨╜╨╡╨╜╨░ ╨┐╨╛╨╗╤î╨╖╨╛╨▓╨░╤é╨╡╨╗╨╡╨╝",
        "no_candidates": "╨¥╨╡╤é ╨┐╤Ç╨╛╨║╤ü╨╕ ╨┤╨╗╤Å ╨┐╤Ç╨╛╨▓╨╡╤Ç╨║╨╕.",
        "db_not_found": "\n[!] ╨¢╨╛╨║╨░╨╗╤î╨╜╨░╤Å ╨▒╨░╨╖╨░ {0} ╨╜╨╡ ╨▒╤ï╨╗╨░ ╨╜╨░╨╣╨┤╨╡╨╜╨░. ╨í╨║╨░╤ç╨╕╨▓╨░╤Ä (╨╛╨║╨╛╨╗╨╛ 5MB)...",
        "db_outdated": "\n[!] ╨¢╨╛╨║╨░╨╗╤î╨╜╨░╤Å ╨▒╨░╨╖╨░ {0} ╤â╤ü╤é╨░╤Ç╨╡╨╗╨░ (╤ü╤é╨░╤Ç╤ê╨╡ 7 ╨┤╨╜╨╡╨╣). ╨₧╨▒╨╜╨╛╨▓╨╗╤Å╤Ä...",
        "db_success": "[Γ£ô] ╨¢╨╛╨║╨░╨╗╤î╨╜╨░╤Å ╨▒╨░╨╖╨░ ╤â╤ü╨┐╨╡╤ê╨╜╨╛ ╤ü╨║╨░╤ç╨░╨╜╨░/╨╛╨▒╨╜╨╛╨▓╨╗╨╡╨╜╨░!",
        "db_error": "[x] ╨₧╤ê╨╕╨▒╨║╨░ ╨╛╨▒╨╜╨╛╨▓╨╗╨╡╨╜╨╕╤Å ╨▒╨░╨╖╤ï (╤Ç╨░╨▒╨╛╤é╨░╨╡╨╝ ╨▒╨╡╨╖ GeoIP): {0}",
        "check_asn": "    [ipinfo.io] ╨ƒ╤Ç╨╛╨▓╨╡╤Ç╤Å╤Ä ╤é╨╕╨┐ {0} ╤â╨╜╨╕╨║╨░╨╗╤î╨╜╤ï╤à ASN (Residential/Hosting)...",
        "check_ipapi": "    [ip-api.com] ╨₧╨┐╤Ç╨╡╨┤╨╡╨╗╤Å╤Ä mobile/hosting ╨┤╨╗╤Å {0} IP...",
        "ipapi_success": "    [ip-api.com] ╨ö╨░╨╜╨╜╤ï╨╡ ╨┐╨╛╨╗╤â╤ç╨╡╨╜╤ï.",
        "classify_filter": "    ╨Ü╨╗╨░╤ü╤ü╨╕╤ä╨╕╤å╨╕╤Ç╤â╤Ä ╨╕ ╤ä╨╕╨╗╤î╤é╤Ç╤â╤Ä ╨┐╤Ç╨╛╨║╤ü╨╕...",
        "db_load_err": "╨₧╤ê╨╕╨▒╨║╨░ ╨╖╨░╨│╤Ç╤â╨╖╨║╨╕ ╨╗╨╛╨║╨░╨╗╤î╨╜╨╛╨╣ ╨▒╨░╨╖╤ï (╨┐╨╛╨┐╤ï╤é╨║╨░ {0}): {1}",
        "db_corrupted": "╨æ╨╕╤é╤ï╨╣ ╤ä╨░╨╣╨╗ ╨▒╨░╨╖╤ï ╤â╨┤╨░╨╗╤æ╨╜, ╤ü╨║╨░╤ç╨╕╨▓╨░╨╡╨╝ ╨╖╨░╨╜╨╛╨▓╨╛...",
        "elite": "  [Γÿà ╨¡╨¢╨ÿ╨ó╨¥╨½╨Ö] ╨ƒ╤Ç╨╛╤ê╨╡╨╗ ╨▓╤ü╨╡ ╤ä╨╕╨╗╤î╤é╤Ç╤ï: {proxy} ({proto}) - {country}",
        "working": "  [Γ£ô ╨á╨É╨æ╨₧╨º╨ÿ╨Ö] ╨¥╨░╨╣╨┤╨╡╨╜: {proxy} ({proto}) - {country}"
    },
    "EN": {
        "log_unique_ip": "Unique IP:PORT",
        "random_generated": "Random generated",
        "start": "[*] Starting proxy collection (Thread limit: {max_workers})",
        "step1": "STEP 1: Async fetching from {0} sources...",
        "step1_5": "STEP 1.5: Generating random proxies...",
        "fetch_err": "    [x] Error {source}: {e}",
        "raw_found": "    [+] Raw proxies collected: {0}",
        "step2": "STEP 2: Basic live check...",
        "live_found": "    [Γ£ô] Live proxies: {0}",
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
        "passed": "    [Γÿà] Unique IP:PORT passed all filters: {0}",
        "done": "\n[Γ£ô] Done! Saving results...",
        "save_live": "[Γ£ô] Basic category lists saved to 'results_live/' folder",
        "cancel": "[!] Task cancelled by user",
        "no_candidates": "No proxies to check.",
        "db_not_found": "\n[!] Local database {0} not found. Downloading (about 5MB)...",
        "db_outdated": "\n[!] Local database {0} is outdated (older than 7 days). Updating...",
        "db_success": "[Γ£ô] Local database successfully downloaded/updated!",
        "db_error": "[x] Database update error (working without GeoIP): {0}",
        "check_asn": "    [ipinfo.io] Checking type of {0} unique ASNs (Residential/Hosting)...",
        "check_ipapi": "    [ip-api.com] Determining mobile/hosting for {0} IPs...",
        "ipapi_success": "    [ip-api.com] Data received.",
        "classify_filter": "    Classifying and filtering proxies...",
        "db_load_err": "Error loading local database (attempt {0}): {1}",
        "db_corrupted": "Corrupted database file deleted, downloading again...",
        "elite": "  [Γÿà ELITE] Passed all filters: {proxy} ({proto}) - {country}",
        "working": "  [Γ£ô WORKING] Found: {proxy} ({proto}) - {country}"
    }
}
class ProxyHunter:
    """╨ô╨╗╨░╨▓╨╜╤ï╨╣ ╨║╨╗╨░╤ü╤ü ╤ü╨▒╨╛╤Ç╤ë╨╕╨║╨░ ╨╕ ╨▓╨░╨╗╨╕╨┤╨░╤é╨╛╤Ç╨░ ╨┐╤Ç╨╛╨║╤ü╨╕"""
    
    def __init__(self, threads: int = 300, timeout: int = 3, countries: Optional[List[str]] = None, 
                 max_ping: float = 700.0, min_speed: float = 1.0,
                 check_smtp: bool = False,
                 collect_dc: bool = True, collect_res: bool = True, collect_mob: bool = True,
                 random_counts: Optional[Dict[str, int]] = None, lang: str = "RU", output_dir: str = ".",
                 github_token: str = ""):
        
        self.output_dir = output_dir
        self.lang = lang
        self.github_token = github_token
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
        self.asn_cache: Dict[str, str] = {}  # ASN ΓåÆ type (isp/hosting/business) from ipinfo.io
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

    def _dynamic_t(self, key):
        class DynamicText:
            def __str__(inner_self):
                return self._t(key)
        return DynamicText()
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
            pbar = tqdm(total=len(SOURCES), desc=self._dynamic_t("tqdm_dl"))
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
        print(f"    ╨ú╨╜╨╕╨║╨░╨╗╤î╨╜╤ï╤à IP:PORT ╨┐╨╛╤ü╨╗╨╡ ╨╛╤ü╨╜╨╛╨▓╨╜╨╛╨│╨╛ ╨┐╨░╤Ç╤ü╨╕╨╜╨│╨░: {len(self.proxy_protocols)}")

        # ╨£╨É╨¿╨ÿ╨¥╨É ╨Æ╨á╨ò╨£╨ò╨¥╨ÿ (╨╛╤é╨┤╨╡╨╗╤î╨╜╤ï╨╝ ╤ê╨░╨│╨╛╨╝)
        if getattr(self, 'github_token', None):
            print(f"\n[*] ╨ù╨░╨┐╤â╤ü╨║ ╨£╨░╤ê╨╕╨╜╤ï ╨Æ╤Ç╨╡╨╝╨╡╨╜╨╕ GitHub (╨┐╨╛╨╕╤ü╨║ ╨║╨╛╨╝╨╝╨╕╤é╨╛╨▓ ╨╖╨░ 24 ╤ç╨░╤ü╨░)...")
            history_sources = []
            rate_limits = []
            
            def _resolve_commits(item):
                url, proto = item
                if "raw.githubusercontent.com" in url or "cdn.jsdelivr.net" in url:
                    commits, limit_info = ProxyUtils.fetch_github_commits(url, self.github_token, 24)
                    return [(c, proto) for c in commits], limit_info
                return [], {}

            with ThreadPoolExecutor(max_workers=10) as ex:
                futures = [ex.submit(_resolve_commits, item) for item in SOURCES]
                for fut in as_completed(futures):
                    if self._cancel_event.is_set(): break
                    res_urls, limit_info = fut.result()
                    history_sources.extend(res_urls)
                    if limit_info and 'remaining' in limit_info:
                        rate_limits.append(limit_info)
            
            history_sources = list(dict.fromkeys(history_sources))
            
            if rate_limits:
                min_remaining = min(rate_limits, key=lambda x: int(x['remaining']))
                import datetime
                reset_time = datetime.datetime.fromtimestamp(int(min_remaining['reset'])).strftime('%H:%M:%S')
                print(f"    [API INFO] ╨¢╨╕╨╝╨╕╤é: {min_remaining['limit']} | ╨₧╤ü╤é╨░╨╗╨╛╤ü╤î: {min_remaining['remaining']} | ╨í╨▒╤Ç╨╛╤ü: {reset_time}")
            
            print(f"    [+] ╨¥╨░╨╣╨┤╨╡╨╜╨╛ {len(history_sources)} ╨╕╤ü╤é╨╛╤Ç╨╕╤ç╨╡╤ü╨║╨╕╤à ╤ä╨░╨╣╨╗╨╛╨▓. ╨¥╨░╤ç╨╕╨╜╨░╨╡╨╝ ╤ü╨║╨░╤ç╨╕╨▓╨░╨╜╨╕╨╡...")
            
            if history_sources:
                try:
                    pbar_hist = tqdm(total=len(history_sources), desc="╨£╨░╤ê╨╕╨╜╨░ ╨▓╤Ç╨╡╨╝╨╡╨╜╨╕")
                except:
                    pbar_hist = None
                    
                ok_hist = 0
                with ThreadPoolExecutor(max_workers=min(len(history_sources), 50)) as ex:
                    fmap = {}
                    for url, proto in history_sources:
                        fmap[ex.submit(ProxyUtils.fetch_url, url, 12)] = (url, proto)
                        
                    for fut in as_completed(fmap):
                        if self._wait_if_paused(): break
                        if self._cancel_event.is_set(): break
                        url, proto = fmap[fut]
                        content = fut.result()
                        if content:
                            ok_hist += 1
                            proxies = ProxyUtils.parse_proxies(content)
                            total_raw += len(proxies)
                            with self._lock:
                                for p in proxies:
                                    self.proxy_protocols[p].add(proto)
                        if pbar_hist: pbar_hist.update(1)
                
                if pbar_hist: pbar_hist.close()
                print(f"    ╨ú╤ü╨┐╨╡╤ê╨╜╨╛ ╤ü╨║╨░╤ç╨░╨╜╨╛ ╨╕╤ü╤é╨╛╤Ç╨╕╤ç╨╡╤ü╨║╨╕╤à ╤ä╨░╨╣╨╗╨╛╨▓: {ok_hist}/{len(history_sources)}")
        print(f"    {self._t('log_unique_ip')}: {len(self.proxy_protocols)}")
    def collect_random(self):
        print(f"\n[+] " + self._t("step1_5"))
        # ╨¥╨╡ ╨│╨╡╨╜╨╡╤Ç╨╕╤Ç╤â╨╡╨╝ ╨▓╤ü╨╡ IP ╨▓ ╨┐╨░╨╝╤Å╤é╤î, ╨┐╤Ç╨╛╤ü╤é╨╛ ╤ü╤ç╨╕╤é╨░╨╡╨╝ ╨╕╤à ╨║╨╛╨╗╨╕╤ç╨╡╤ü╤é╨▓╨╛
        rand_total = sum(self.random_counts.values())
        print(f"    {self._t('random_generated')}: {rand_total}")
        
        # ╨í╨╛╨╖╨┤╨░╨╡╨╝ ╨╗╨╡╨╜╨╕╨▓╤ï╨╣ ╨│╨╡╨╜╨╡╤Ç╨░╤é╨╛╤Ç ╨║╨░╨╜╨┤╨╕╨┤╨░╤é╨╛╨▓ (Pipeline)
        def candidate_generator():
            # ╨í╨╜╨░╤ç╨░╨╗╨░ ╨╛╤é╨┤╨░╨╡╨╝ ╤ü╨╛╨▒╤Ç╨░╨╜╨╜╤ï╨╡ ╨╕╨╖ ╨╕╤ü╤é╨╛╤ç╨╜╨╕╨║╨╛╨▓
            for ip_port, protos in self.proxy_protocols.items():
                yield ip_port, list(protos)
            # ╨ù╨░╤é╨╡╨╝ ╨│╨╡╨╜╨╡╤Ç╨╕╤Ç╤â╨╡╨╝ ╤Ç╨░╨╜╨┤╨╛╨╝╨╜╤ï╨╡ ╨╜╨░ ╨╗╨╡╤é╤â
            for proto, ip_port in RandomProxyGenerator.generate_all(self.random_counts):
                yield ip_port, [proto]
                
        self.candidate_generator = candidate_generator()
        self.candidate_total = len(self.proxy_protocols) + rand_total

    def validate(self):
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
            
            # ╨ƒ╤Ç╨╛╨┐╤â╤ü╨║╨░╨╡╨╝ ╨╖╨░╤ê╨╕╤ä╤Ç╨╛╨▓╨░╨╜╨╜╤ï╨╡ ╨║╨╛╨╜╤ä╨╕╨│╨╕ ╨╜╨░╨┐╤Ç╤Å╨╝╤â╤Ä ╨▓ ╤Ç╨╡╨╖╤â╨╗╤î╤é╨░╤é╤ï
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
            working = await ProxyUtils.async_check_proxy(ip, int(port_s), protos, self.timeout)
            if working:
                if self._cancel_event.is_set(): return None
                country = self._get_country(ip)
                if self.countries and country.upper() not in self.countries:
                    return None
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
            
        asyncio.run(main_loop())
        self.live_results = sorted(set(self.live_results))
        print(f"    {self._t('live_proxies')} {len(self.live_results)}")
    def _download_mmdb_if_needed(self):
        db_path = 'GeoLite2-Country.mmdb'
        needs_download = False
        
        if not os.path.exists(db_path):
            needs_download = True
            print(self._t("db_not_found").format(db_path))
        else:
            # ╨₧╨▒╨╜╨╛╨▓╨╗╤Å╨╡╨╝ ╨▒╨░╨╖╤â, ╨╡╤ü╨╗╨╕ ╨╛╨╜╨░ ╤ü╤é╨░╤Ç╤ê╨╡ 7 ╨┤╨╜╨╡╨╣ (604800 ╤ü╨╡╨║╤â╨╜╨┤)
            if time.time() - os.path.getmtime(db_path) > 604800:
                needs_download = True
                print(self._t("db_outdated").format(db_path))
                
        if needs_download:
            url = 'https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb'
            tmp_path = db_path + '.tmp'
            try:
                r = requests.get(url, stream=True, timeout=30)
                r.raise_for_status()
                # BUG FIX: ╨ÿ╤ü╨┐╨╛╨╗╤î╨╖╤â╨╡╨╝ ╨▓╤Ç╨╡╨╝╨╡╨╜╨╜╤ï╨╣ ╤ä╨░╨╣╨╗, ╤ç╤é╨╛╨▒╤ï ╨╜╨╡ ╨╛╤ü╤é╨░╨▓╨╕╤é╤î ╨▒╨╕╤é╤â╤Ä ╨▒╨░╨╖╤â ╨┐╤Ç╨╕ ╨╛╨▒╤Ç╤ï╨▓╨╡ ╤ü╨╡╤é╨╕
                with open(tmp_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk: f.write(chunk)
                # ╨ò╤ü╨╗╨╕ ╤ü╨║╨░╤ç╨╕╨▓╨░╨╜╨╕╨╡ ╨╖╨░╨▓╨╡╤Ç╤ê╨╡╨╜╨╛ ╤â╤ü╨┐╨╡╤ê╨╜╨╛, ╨░╤é╨╛╨╝╨░╤Ç╨╜╨╛ ╨╖╨░╨╝╨╡╨╜╤Å╨╡╨╝ ╤ü╤é╨░╤Ç╤ï╨╣ ╤ä╨░╨╣╨╗ ╨╜╨╛╨▓╤ï╨╝
                os.replace(tmp_path, db_path)
                print(self._t("db_success"))
            except Exception as e:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                print(self._t("db_error").format(e))
    def _batch_ip_info(self, ips: Set[str]):
        """╨ƒ╨░╨║╨╡╤é╨╜╤ï╨╣ ╨╖╨░╨┐╤Ç╨╛╤ü ╨▓ ip-api.com ╤ü Exponential Backoff ╨┤╨╗╤Å ╨╛╨▒╤à╨╛╨┤╨░ 429 Rate Limit"""
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
                        # Rate Limit: ╨╢╨┤╨╡╨╝ ╨┤╨╛╨╗╤î╤ê╨╡ ╨╕ ╨┐╤Ç╨╛╨▒╤â╨╡╨╝ ╤ü╨╜╨╛╨▓╨░
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                        
                    if resp.status_code == 200:
                        try:
                            json_data = resp.json()
                            if not isinstance(json_data, list): break # ╨ù╨░╤ë╨╕╤é╨░ ╨╛╤é ╨║╤Ç╨╕╨▓╨╛╨│╨╛ ╨║╨╛╨╜╤é╤Ç╨░╨║╤é╨░
                            
                            with self._lock: # ╨ù╨░╤ë╨╕╤é╨░ ╨╛╤é ╤ü╨╛╤ü╤é╨╛╤Å╨╜╨╕╤Å ╨│╨╛╨╜╨║╨╕ (Race Condition)
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
                            break # ╨ú╤ü╨┐╨╡╤ê╨╜╨╛, ╨▓╤ï╤à╨╛╨┤╨╕╨╝ ╨╕╨╖ ╤å╨╕╨║╨╗╨░ ╤Ç╨╡╤é╤Ç╨░╨╡╨▓
                        except Exception:
                            break # JSON Decode error ╨╕╨╗╨╕ ╨┤╤Ç╤â╨│╨░╤Å ╤ä╨░╤é╨░╨╗╤î╨╜╨░╤Å ╨╛╤ê╨╕╨▒╨║╨░ ╤ü╤é╤Ç╤â╨║╤é╤â╤Ç╤ï
                    else:
                        break # ╨ö╤Ç╤â╨│╨╕╨╡ ╨╛╤ê╨╕╨▒╨║╨╕ (500, 403 ╨╕ ╤é.╨┤.) - ╨┐╤Ç╨╛╨┐╤â╤ü╨║╨░╨╡╨╝ ╤ç╨░╨╜╨║
                except Exception:
                    time.sleep(2)
                    
            time.sleep(4) # ╨æ╨░╨╖╨╛╨▓╤ï╨╣ ╨║╤â╨╗╨┤╨░╤â╨╜ API
    def _batch_asn_type(self):
        """╨ù╨░╨┐╤Ç╨╛╤ü ╤é╨╕╨┐╨░ ASN (isp/hosting/business) ╤ç╨╡╤Ç╨╡╨╖ ipinfo.io ╨┤╨╗╤Å ╨╛╨┐╤Ç╨╡╨┤╨╡╨╗╨╡╨╜╨╕╤Å Residential.
        
        ╨ƒ╤Ç╨╛╨▓╨╡╤Ç╤Å╨╡╨╝ ╨║╨░╨╢╨┤╤ï╨╣ ╤â╨╜╨╕╨║╨░╨╗╤î╨╜╤ï╨╣ ASN ╨╛╨┤╨╕╨╜ ╤Ç╨░╨╖. ╨á╨╡╨╖╤â╨╗╤î╤é╨░╤é ╨║╨╡╤ê╨╕╤Ç╤â╨╡╤é╤ü╤Å ╨▓ self.asn_cache.
        ASN type 'isp' = Residential, 'hosting' = Datacenter, 'business' = Datacenter.
        """
        # ╨í╨╛╨▒╨╕╤Ç╨░╨╡╨╝ ╤â╨╜╨╕╨║╨░╨╗╤î╨╜╤ï╨╡ ASN ╨╕╨╖ ip_cache
        unique_asns = set()
        with self._lock:
            for ip, info in self.ip_cache.items():
                asn_str = info.get('asn', '')
                if asn_str:
                    asn_num = asn_str.split()[0]  # "AS265606 DIGY NETWORKS" ΓåÆ "AS265606"
                    if asn_num.startswith('AS'):
                        unique_asns.add(asn_num)
        
        # ╨ú╨▒╨╕╤Ç╨░╨╡╨╝ ╤â╨╢╨╡ ╨╖╨░╨║╨╡╤ê╨╕╤Ç╨╛╨▓╨░╨╜╨╜╤ï╨╡
        unique_asns -= set(self.asn_cache.keys())
        if not unique_asns:
            return
        
        print(self._t("check_asn").format(len(unique_asns)))
        
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
                    # Rate limit ΓÇö ╨┐╨╛╨┤╨╛╨╢╨┤╤æ╨╝ ╨╕ ╨┐╤Ç╨╛╨┤╨╛╨╗╨╢╨╕╨╝
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
                        elif resp.status_code == 429:
                            # Rate limit ΓÇö ╨┐╨╛╨┤╨╛╨╢╨┤╤æ╨╝ ╨╕ ╨┐╤Ç╨╛╨┤╨╛╨╗╨╢╨╕╨╝
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
            except Exception:
                pass
            
            time.sleep(0.3)  # ╨£╤Å╨│╨║╨╕╨╣ rate-limit ╨┤╨╗╤Å ipinfo.io
        
        print(self._t("ipinfo", checked=checked, total=len(unique_asns)))
    def _check_rdns_and_bl(self, ip: str) -> dict:
        """╨Ü╤ì╤ê╨╕╤Ç╤â╨╡╨╝╨░╤Å ╨┐╤Ç╨╛╨▓╨╡╤Ç╨║╨░ RDNS ╨╕ DNSBL"""
        # BUG-4 FIX: ╤ç╤é╨╡╨╜╨╕╨╡ ╨║╤ì╤ê╨░ ╨┐╨╛╨┤ ╨╗╨╛╨║╨╛╨╝, ╨▓╨╛╨╖╨▓╤Ç╨░╤é ╨║╨╛╨┐╨╕╨╕ ╨┤╨╗╤Å thread-safety
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
                    # ╨ÿ╨│╨╜╨╛╤Ç╨╕╤Ç╤â╨╡╨╝ ╨╛╤é╨▓╨╡╤é╤ï ╨▓╨╕╨┤╨░ 127.255.255.X (╨╛╤ê╨╕╨▒╨║╨░ Spamhaus: "Public DNS blocked")
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
        # ╨ù╨░╤ë╨╕╤é╨░ ╨╛╤é ╤ü╨╛╤ü╤é╨╛╤Å╨╜╨╕╤Å ╨│╨╛╨╜╨║╨╕ ╨┐╤Ç╨╕ ╨╖╨░╨┐╨╕╤ü╨╕ ╨╕╨╖ ╨╝╨╜╨╛╨╢╨╡╤ü╤é╨▓╨░ ╨┐╨╛╤é╨╛╨║╨╛╨▓
        with self._lock:
            if ip not in self.ip_cache: self.ip_cache[ip] = {}
            self.ip_cache[ip].update({'rdns': rdns, 'dnsbl': is_bl, 'bad_ports': has_bad_port})
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
                reader, writer = await asyncio.wait_for(fut, timeout=min(3.0, self.timeout))
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
            
            # ╨É╤ü╨╕╨╜╤à╤Ç╨╛╨╜╨╜╨░╤Å ╨┐╤Ç╨╛╨▓╨╡╤Ç╨║╨░ SMTP (Port 25)
            # ╨º╤é╨╛╨▒╤ï ╨╜╨╡ ╤â╤ü╨╗╨╛╨╢╨╜╤Å╤é╤î SOCKS ╤à╤ì╨╜╨┤╤ê╨╡╨╣╨║╨╕ ╨┤╨╗╤Å ╨┐╤Ç╨╛╨╕╨╖╨▓╨╛╨╗╤î╨╜╤ï╤à ╨┐╨╛╤Ç╤é╨╛╨▓ (╤é.╨║. ╨╜╤â╨╢╨╜╨╛ ╨┐╨╡╤Ç╨╡╨┐╨╕╤ü╤ï╨▓╨░╤é╤î ╨▒╨░╨╣╤é-╨║╨╛╨┤ ╨┤╨╗╤Å ╨┐╨╛╤Ç╤é╨░ 25),
            # ╨╝╤ï ╨╕╤ü╨┐╨╛╨╗╤î╨╖╤â╨╡╨╝ aiohttp ╨╡╤ü╨╗╨╕ ╨╡╤ü╤é╤î aiohttp_socks, ╨╕╨╜╨░╤ç╨╡ ╨┐╤Ç╨╛╨┐╤â╤ü╨║╨░╨╡╨╝ ╤é╨╡╤ü╤é ╨┤╨╗╤Å SOCKS
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
                    # ╨ò╤ü╨╗╨╕ ╨╜╨╡╤é aiohttp_socks, ╤ü╤ç╨╕╤é╨░╨╡╨╝ ╤ç╤é╨╛ SMTP ╤é╨╡╤ü╤é ╨╜╨╡ ╨┐╤Ç╨╛╨╣╨┤╨╡╨╜, ╨╗╨╕╨▒╨╛ ╨┐╤Ç╨╛╨╣╨┤╨╡╨╜ ╤â╤ü╨╗╨╛╨▓╨╜╨╛
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
    def advanced_filter(self):
        if not self.live_results: return
        print(f"\n[+] " + self._t("step3").format(len(self.live_results)))
        
        # ╨í╨╛╨▒╨╕╤Ç╨░╨╡╨╝ ╤â╨╜╨╕╨║╨░╨╗╤î╨╜╤ï╨╡ IP ╨┤╨╗╤Å ╨┐╨░╨║╨╡╤é╨╜╨╛╨│╨╛ ╨╖╨░╨┐╤Ç╨╛╤ü╨░
        unique_ips = set()
        for r in self.live_results:
            ext_ip, _ = ProxyUtils.extract_ip_port(r)
            if ext_ip != "Config" and re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', ext_ip):
                unique_ips.add(ext_ip)
        
        # 1) ip-api.com ΓÇö ╨╛╨┐╤Ç╨╡╨┤╨╡╨╗╤Å╨╡╨╝ mobile/hosting ╤ä╨╗╨░╨│╨╕ ╨┤╨╗╤Å ╨║╨░╨╢╨┤╨╛╨│╨╛ IP
        print(self._t("check_ipapi").format(len(unique_ips)))
        self._batch_ip_info(unique_ips)
        print(self._t("ipapi_success"))
        
        # 2) ipinfo.io ΓÇö ╨╛╨┐╤Ç╨╡╨┤╨╡╨╗╤Å╨╡╨╝ ╤é╨╕╨┐ ASN (isp/hosting/business) ╨┤╨╗╤Å Residential-╨┤╨╡╤é╨╡╨║╤å╨╕╨╕
        self._batch_asn_type()
        print(self._t("classify_filter"))
        
        import asyncio
        try: from tqdm import tqdm
        except ImportError: tqdm = None
        
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
                                
                            # ╨û╨╡╤ü╤é╨║╨╕╨╣ ╨▓╤é╨╛╤Ç╨╕╤ç╨╜╤ï╨╣ ╤ä╨╕╨╗╤î╤é╤Ç: ╨╛╤é╤ü╨╡╨║╨░╨╡╨╝ ╨┐╨╡╤Ç╨╡╨╛╨┐╤Ç╨╡╨┤╨╡╨╗╨╡╨╜╨╜╤ï╨╡ ╤ü╤é╤Ç╨░╨╜╤ï
                            if self.countries and chk_country.upper() not in self.countries:
                                with self._lock:
                                    to_remove_live.add(res)
                            else:
                                with self._lock:
                                    self.elite_results.append(res)
                                    if category == "Datacenter": self.results_datacenter.append(res)
                                    elif category == "Residential": self.results_residential.append(res)
                                    elif category == "Mobile": self.results_mobile.append(res)
                                    
                                    # REALTIME ╨▓╤ï╨▓╨╛╨┤ ╨┤╨╗╤Å GUI
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
            
        to_remove_live = asyncio.run(main_loop())
        
        if to_remove_live:
            self.live_results = [r for r in self.live_results if r not in to_remove_live]
            
        self.results_datacenter = sorted(set(self.results_datacenter))
        self.results_residential = sorted(set(self.results_residential))
        self.results_mobile = sorted(set(self.results_mobile))
        self.elite_results = sorted(set(self.elite_results))
        
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
            writer.writerow(['╨ƒ╤Ç╨╛╤é╨╛╨║╨╛╨╗', 'IP/Config', 'Port', '╨í╤é╤Ç╨░╨╜╨░'])
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
        with open(os.path.join(full_path, 'all_ips.txt'), 'w', encoding='utf-8') as f:
            f.write(f"# {description} (╨ó╨╛╨╗╤î╨║╨╛ ╤â╨╜╨╕╨║╨░╨╗╤î╨╜╤ï╨╡ IP): {len(unique_ips)}\n")
            for ip in unique_ips: f.write(ip + '\n')
                
        for proto, items in by_proto.items():
            with open(os.path.join(full_path, f'{proto}.txt'), 'w', encoding='utf-8') as f:
                f.write(f"# {description} ({proto.upper()}): {len(items)}\n")
                for p in items: f.write(p + '\n')
                
            with open(os.path.join(full_path, f'{proto}.csv'), 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['╨ƒ╤Ç╨╛╤é╨╛╨║╨╛╨╗', 'IP/Config', 'Port', '╨í╤é╤Ç╨░╨╜╨░'])
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
            with open(os.path.join(full_path, f'{proto}_ips.txt'), 'w', encoding='utf-8') as f:
                f.write(f"# {description} ({proto.upper()} - ╨ó╨╛╨╗╤î╨║╨╛ ╤â╨╜╨╕╨║╨░╨╗╤î╨╜╤ï╨╡ IP): {len(proto_ips)}\n")
                for ip in proto_ips: f.write(ip + '\n')
    def save(self):
        if self.live_results:
            self._save_category('results_live', self.live_results, '╨û╨╕╨▓╤ï╨╡ ╨┐╤Ç╨╛╨║╤ü╨╕')
            print(self._t("save_live"))
            
        # BUG-7 FIX: ╨í╨╛╤à╤Ç╨░╨╜╤Å╨╡╨╝ elite_results, ╨║╨╛╤é╨╛╤Ç╤ï╨╡ GUI ╨╛╨╢╨╕╨┤╨░╨╡╤é ╨▓ results_elite/
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
        print("\n≡ƒÜÇ ULTIMATE PROXY HUNTER v4.0 (ADVANCED FILTERS)")
        
        # ╨₧╤ç╨╕╤ë╨░╨╡╨╝ ╤ü╤é╨░╤Ç╤ï╨╡ ╤Ç╨╡╨╖╤â╨╗╤î╤é╨░╤é╤ï ╨┐╨╡╤Ç╨╡╨┤ ╨╜╨░╤ç╨░╨╗╨╛╨╝ ╨╜╨╛╨▓╨╛╨│╨╛ ╤ü╨▒╨╛╤Ç╨░
        import shutil
        for category in ['live', 'elite', 'datacenter', 'residential', 'mobile']:
            folder_path = os.path.join(self.output_dir, f"results_{category}")
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path, ignore_errors=True)
            
        for attempt in range(2):
            self._download_mmdb_if_needed()
            try:
                if os.path.exists('GeoLite2-Country.mmdb'):
                    self.db_reader = maxminddb.open_database('GeoLite2-Country.mmdb')
                    break # ╨ú╤ü╨┐╨╡╤ê╨╜╨╛ ╨╛╤é╨║╤Ç╤ï╨╗╨╕, ╨▓╤ï╤à╨╛╨┤╨╕╨╝ ╨╕╨╖ ╤å╨╕╨║╨╗╨░
            except Exception as e:
                print(self._t("db_load_err").format(attempt+1, e))
                self.db_reader = None
                try:
                    os.remove('GeoLite2-Country.mmdb')
                    print(self._t("db_corrupted"))
                except Exception:  # BUG-10 FIX: bare except
                    pass
            
        self.collect()
        if not self._cancel_event.is_set(): self.collect_random()
        if not self._cancel_event.is_set(): self.validate()
        if not self._cancel_event.is_set(): self.advanced_filter()
        if not self._cancel_event.is_set():  # BUG-FP35 FIX: ╨╜╨╡ ╤ü╨╛╤à╤Ç╨░╨╜╤Å╨╡╨╝ ╨┐╤Ç╨╕ ╨╛╤é╨╝╨╡╨╜╨╡
            self.save()
        m, s = divmod(int(time.time() - t0), 60)
        print("\nΓÅ▒   " + self._t("time_total").format(m, s))
        if self._cancel_event.is_set():
            print("Γ¥î " + self._t("user_abort"))
def main():
    parser = argparse.ArgumentParser(description='Proxy Hunter v4.0 - Advanced Filtration')
    parser.add_argument('--threads', type=int, default=300, help='╨Ü╨╛╨╗╨╕╤ç╨╡╤ü╤é╨▓╨╛ ╨┐╨╛╤é╨╛╨║╨╛╨▓')
    parser.add_argument('--timeout', type=int, default=5, help='╨ó╨░╨╣╨╝╨░╤â╤é ╤ü╨╛╨╡╨┤╨╕╨╜╨╡╨╜╨╕╤Å ╨▓ ╤ü╨╡╨║╤â╨╜╨┤╨░╤à')
    parser.add_argument('--countries', default='US,CA,GB,AT,BE,BG,HR,CY,CZ,DK,EE,FI,FR,DE,GR,HU,IE,IT,LV,LT,LU,MT,NL,PL,PT,RO,SK,SI,ES,SE', type=str, help='╨á╨░╨╖╤Ç╨╡╤ê╨╡╨╜╨╜╤ï╨╡ ╤ü╤é╤Ç╨░╨╜╤ï ╤ç╨╡╤Ç╨╡╨╖ ╨╖╨░╨┐╤Å╤é╤â╤Ä')
    parser.add_argument('--max-ping', type=float, default=700, help='╨£╨░╨║╤ü ╨┐╨╕╨╜╨│ ╨▓ ╨╝╤ü')
    parser.add_argument('--min-speed', type=float, default=1.0, help='╨£╨╕╨╜ ╤ü╨║╨╛╤Ç╨╛╤ü╤é╤î ╨£╨▒╨╕╤é/╤ü')
    parser.add_argument('--check-smtp', choices=['True', 'False'], default='True', help='╨Æ╨║╨╗╤Ä╤ç╨╕╤é╤î ╨┐╤Ç╨╛╨▓╨╡╤Ç╨║╤â SMTP ╨┐╨╛╤Ç╤é╨╛╨▓ (True/False)')
    parser.add_argument('--residential-only', action='store_true', help='╨ó╨╛╨╗╤î╨║╨╛ residential/╨╝╨╛╨▒╨╕╨╗╤î╨╜╤ï╨╡ IP')
    
    args = parser.parse_args()
    check_smtp_bool = args.check_smtp == 'True'
    countries_list = [c.strip().upper() for c in args.countries.split(',')
    ] if args.countries else None
    try:
        import tqdm
        import dns.resolver
    except ImportError:
        print("Γ¥î ╨ú╤ü╤é╨░╨╜╨╛╨▓╨╕╤é╨╡ ╨╖╨░╨▓╨╕╤ü╨╕╨╝╨╛╤ü╤é╨╕: pip install tqdm requests dnspython")
        sys.exit(1)
    # BUG-2 FIX: residential_only ╨╜╨╡ ╤ü╤â╤ë╨╡╤ü╤é╨▓╤â╨╡╤é ╨▓ __init__, ╨╕╤ü╨┐╨╛╨╗╤î╨╖╤â╨╡╨╝ collect_dc
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
