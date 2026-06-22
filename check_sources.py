import requests
from concurrent.futures import ThreadPoolExecutor

urls = [
    ('https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/socks5.txt', 'socks5'),
    ('https://cdn.jsdelivr.net/gh/officialputuid/ProxyForEveryone@main/http/http.txt', 'http'),
    ('https://cdn.jsdelivr.net/gh/officialputuid/ProxyForEveryone@main/socks4/socks4.txt', 'socks4'),
    ('https://cdn.jsdelivr.net/gh/officialputuid/ProxyForEveryone@main/socks5/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxylist-to/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/proxylist-to/proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/proxylist-to/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt', 'http'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt', 'https'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/BGPK/Proxy-List/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/BGPK/Proxy-List/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/BGPK/Proxy-List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ebrasha/abdal-proxy-hub/main/http-proxy-list-by-EbraSha.txt', 'http'),
    ('https://raw.githubusercontent.com/ebrasha/abdal-proxy-hub/main/socks4-proxy-list-by-EbraSha.txt', 'socks4'),
    ('https://raw.githubusercontent.com/ebrasha/abdal-proxy-hub/main/socks5-proxy-list-by-EbraSha.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxyscrape/free-proxy-list/main/proxies/protocols/http/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxyscrape/free-proxy-list/main/proxies/protocols/socks4/data.txt', 'socks4'),
    ('https://raw.githubusercontent.com/proxyscrape/free-proxy-list/main/proxies/protocols/socks5/data.txt', 'socks5'),
    ('https://raw.githubusercontent.com/stormsia/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/stormsia/proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/stormsia/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt', 'http'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Seeh-Saah/awesome-free-proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Seeh-Saah/awesome-free-proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Seeh-Saah/awesome-free-proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt', 'http'),
    ('https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt', 'https'),
    ('https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/im-razvan/proxy_list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/TheLime1/Validity/main/data/http.txt', 'http'),
    ('https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/http/global/http_checked.txt', 'http'),
    ('https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks4/global/socks4_checked.txt', 'socks4'),
    ('https://raw.githubusercontent.com/andigwandi/free-proxy/main/proxy_list.txt', 'all'),
    ('https://raw.githubusercontent.com/mishakorzik/Free-Proxy/main/proxy.txt', 'all'),
    ('https://raw.githubusercontent.com/casals-ar/proxy-list/main/http', 'http'),
    ('https://raw.githubusercontent.com/casals-ar/proxy-list/main/https', 'https'),
    ('https://raw.githubusercontent.com/casals-ar/proxy-list/main/socks4', 'socks4'),
    ('https://raw.githubusercontent.com/casals-ar/proxy-list/main/socks5', 'socks5'),
    ('https://raw.githubusercontent.com/zebbern/Proxy-Scraper/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/Boster12/Free_Proxy_List/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Boster12/Free_Proxy_List/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Boster12/Free_Proxy_List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Http.txt', 'http'),
    ('https://raw.githubusercontent.com/Skillter/ProxyGather/refs/heads/master/proxies/working-proxies-all.txt', 'all'),
    ('https://raw.githubusercontent.com/Skillter/ProxyGather/refs/heads/master/proxies/scraped-proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/Volodichev/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt', 'all'),
    ('https://raw.githubusercontent.com/a2u/free-proxy-list/master/free-proxy-list.txt', 'all'),
    ('https://raw.githubusercontent.com/almroot/proxylist/master/list.txt', 'all'),
    ('https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/manuGMG/proxy-365/main/SOCKS5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Toffan1/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/saisuiu/uiu/main/free.txt', 'all')
]

valid = []
invalid = []

def check_url(item):
    url, proto = item
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            if len(r.text) > 10:
                return item, True, 'OK'
            else:
                return item, False, 'Empty content'
        else:
            return item, False, f'Status {r.status_code}'
    except Exception as e:
        return item, False, str(e)

with ThreadPoolExecutor(max_workers=10) as ex:
    for res in ex.map(check_url, urls):
        item, is_ok, msg = res
        if is_ok:
            valid.append(item)
        else:
            invalid.append((item, msg))

print(f'Valid: {len(valid)}')
print(f'Invalid: {len(invalid)}')
for (url, proto), msg in invalid:
    print(f'FAIL: {url} -> {msg}')

print('=== VALID SOURCES ===')
with open('valid_sources.txt', 'w', encoding='utf-8') as f:
    for u, p in valid:
        f.write(f"    ('{u}', '{p}'),\n")
