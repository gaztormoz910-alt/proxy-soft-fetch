import re
import json

with open('temp_code.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Instead of executing directly (which has syntax errors due to the user's text), let's just use Regex to find all tuples.
# AND for loops, we can just execute the python parts.
# Let's write a clean version of the user's code:
code = """
SOURCES = []
TOP_COUNTRIES = ['US', 'RU', 'GB', 'DE', 'FR', 'BR', 'IN', 'CN', 'ID', 'IR', 'KR', 'JP', 'UA', 'NL', 'CA']
NOVA_COUNTRIES = ['ca', 'br', 'in', 'jp', 'cn', 'ua', 'id', 'sg', 'nl', 'it', 'es', 'pl', 'kr', 'th', 'vn']
GEO_COUNTRIES = ['US', 'RU', 'GB', 'DE', 'FR', 'BR', 'IN', 'CN', 'ID', 'IR', 'KR', 'JP', 'UA', 'NL', 'CA', 'PL', 'IT']
CUSTOM_TIMEOUTS = [1500, 2500, 3500, 4500, 6000, 7500, 8500, 9500]
LITPORT_COUNTRIES = ['US', 'RU', 'GB', 'DE', 'FR', 'NL', 'CA', 'SG', 'IN', 'BR', 'UA', 'PL']
DATABAY_COUNTRIES = ['CN', 'BR', 'ID', 'IR', 'JP', 'UA', 'IN', 'CA', 'FR', 'IT', 'ES', 'PL', 'SG', 'KR', 'TH']
SOCKS5_COUNTRIES = ['US', 'RU', 'GB', 'DE', 'FR', 'BR', 'IN', 'CN', 'ID', 'IR', 'KR', 'JP', 'UA', 'NL', 'CA', 'SG', 'PL', 'VN']
SOCKS5_TIMEOUTS = [1000, 1500, 2500, 3500, 4500, 6000]

for country in TOP_COUNTRIES:
    SOURCES.extend([
        (f'https://www.proxy-list.download/api/v1/get?type=http&country={country}', 'http'),
        (f'https://www.proxy-list.download/api/v1/get?type=https&country={country}', 'https'),
        (f'https://www.proxy-list.download/api/v1/get?type=socks4&country={country}', 'socks4'),
        (f'https://www.proxy-list.download/api/v1/get?type=socks5&country={country}', 'socks5'),
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=2000&country={country}&ssl=yes&anonymity=elite', 'http'),
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=2000&country={country}&anonymity=elite', 'socks4'),
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=2000&country={country}&anonymity=elite', 'socks5')
    ])

SOURCES.extend([(f'https://www.my-proxy.com/free-proxy-list-{i}.html', 'http') for i in range(2, 11)])
SOURCES.extend([(f'https://www.proxynova.com/proxy-server-list/country-{c}/', 'http') for c in NOVA_COUNTRIES])

for country in GEO_COUNTRIES:
    SOURCES.extend([
        (f'https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country={country}&protocols=http', 'http'),
        (f'https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country={country}&protocols=https', 'https'),
        (f'https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country={country}&protocols=socks4', 'socks4'),
        (f'https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country={country}&protocols=socks5', 'socks5')
    ])

import datetime
today = datetime.datetime.now()
SOURCES.extend([(f'https://checkerproxy.net/api/archive/{(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d")}', 'all') for i in range(15, 31)])

for tm in CUSTOM_TIMEOUTS:
    SOURCES.extend([
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout={tm}&country=all&ssl=all&anonymity=elite', 'http'),
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout={tm}&country=all', 'socks4'),
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout={tm}&country=all', 'socks5')
    ])

for c in LITPORT_COUNTRIES:
    SOURCES.extend([
        (f'https://litport.net/api/free-proxy?format=txt&protocol=http&country={c}', 'http'),
        (f'https://litport.net/api/free-proxy?format=txt&protocol=socks4&country={c}', 'socks4'),
        (f'https://litport.net/api/free-proxy?format=txt&protocol=socks5&country={c}', 'socks5')
    ])

for c in DATABAY_COUNTRIES:
    SOURCES.extend([
        (f'https://databay.com/api/v1/proxy-list?format=txt&protocol=http&country={c}', 'http'),
        (f'https://databay.com/api/v1/proxy-list?format=txt&protocol=https&country={c}', 'https'),
        (f'https://databay.com/api/v1/proxy-list?format=txt&protocol=socks4&country={c}', 'socks4'),
        (f'https://databay.com/api/v1/proxy-list?format=txt&protocol=socks5&country={c}', 'socks5')
    ])

SOURCES.extend([(f'https://proxydb.net/?protocol=http&offset={i*15}', 'http') for i in range(21, 61)])
SOURCES.extend([(f'https://proxydb.net/?protocol=https&offset={i*15}', 'https') for i in range(21, 61)])
SOURCES.extend([(f'https://proxydb.net/?protocol=socks4&offset={i*15}', 'socks4') for i in range(21, 61)])
SOURCES.extend([(f'https://proxydb.net/?protocol=socks5&offset={i*15}', 'socks5') for i in range(21, 61)])
SOURCES.extend([(f'https://proxy-list.org/english/index.php?p={i}', 'all') for i in range(11, 21)])

for c in SOCKS5_COUNTRIES:
    SOURCES.extend([
        (f'https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country={c}', 'socks5'),
        (f'https://databay.com/api/v1/proxy-list?format=txt&protocol=socks5&country={c}', 'socks5'),
        (f'https://www.proxy-list.download/api/v1/get?type=socks5&country={c}', 'socks5'),
        (f'https://litport.net/api/free-proxy?format=txt&protocol=socks5&country={c}', 'socks5')
    ])

for tm in SOCKS5_TIMEOUTS:
    SOURCES.extend([
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout={tm}&country=all', 'socks5'),
        (f'https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5&proxy_format=ipport&format=text&timeout={tm}', 'socks5'),
        (f'https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text&protocol=socks5&timeout={tm}', 'socks5')
    ])
SOURCES.extend([(f'https://proxydb.net/?protocol=socks5&offset={i*15}', 'socks5') for i in range(40)])
SOURCES.extend([(f'https://advanced.name/freeproxy?type=socks5&page={i}', 'socks5') for i in range(1, 60)])
"""
import re

with open('extracted_prompt.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract static sources
urls = []
for match in re.finditer(r"\('([^']+)',\s*'([^']+)'\)", text):
    u, p = match.group(1), match.group(2)
    # Fix fake protocols
    if p in ['base64_html', 'html_table', 'json_dynamic_search']:
        p = 'all'
    urls.append((u, p))

# Also execute the dynamic loops code to add to the list
exec_locals = {}
exec(code, {}, exec_locals)

all_sources = urls + exec_locals['SOURCES']

with open('all_new_sources.json', 'w', encoding='utf-8') as f:
    json.dump(all_sources, f, indent=2)

print(f"Extracted {len(all_sources)} sources!")
