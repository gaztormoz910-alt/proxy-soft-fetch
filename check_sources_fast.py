import urllib.request
import urllib.error
import ssl
from concurrent.futures import ThreadPoolExecutor

urls = [
    ('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt', 'all'),
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt', 'https'),
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/HTTP.txt', 'http'),
    ('https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/HyperBeats/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt', 'http'),
    ('https://raw.githubusercontent.com/BlackSnowDot/proxylist-update-every-minute/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/BlackSnowDot/proxylist-update-every-minute/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/BlackSnowDot/proxylist-update-every-minute/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/BlackSnowDot/proxylist-update-every-minute/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/manuGMG/proxy-365/main/SOCKS5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/tahaluindo/Free-Proxies/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/tahaluindo/Free-Proxies/main/proxies/https.txt', 'https'),
    ('https://raw.githubusercontent.com/tahaluindo/Free-Proxies/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/tahaluindo/Free-Proxies/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/tahaluindo/Free-Proxies/main/proxies/all.txt', 'all'),
    ('https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list', 'all'), 
    ('https://raw.githubusercontent.com/Kitsun3Sec/ProxyList/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Kitsun3Sec/ProxyList/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Kitsun3Sec/ProxyList/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Kurosec/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Kurosec/proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Kurosec/proxy-list/main/socks5.txt', 'socks5'),
    ('https://www.proxy-list.download/api/v1/get?type=http', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=https', 'https'),
    ('https://www.proxy-list.download/api/v1/get?type=socks4', 'socks4'),
    ('https://www.proxy-list.download/api/v1/get?type=socks5', 'socks5'),
    ('https://www.proxyscan.io/download?type=http', 'http'),
    ('https://www.proxyscan.io/download?type=https', 'https'),
    ('https://www.proxyscan.io/download?type=socks4', 'socks4'),
    ('https://www.proxyscan.io/download?type=socks5', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=https&timeout=10000&country=all', 'https'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=https&timeout=10000&country=all&ssl=all&anonymity=all', 'https'),
    ('https://multiproxy.org/txt_all/proxy.txt', 'all'),
    ('http://alexa.lr2b.com/proxylist.txt', 'all')
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

valid = []
invalid = []

def check_url(item):
    url, proto = item
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as r:
            data = r.read(1024).decode('utf-8', errors='ignore')
            if len(data) > 10 and r.getcode() == 200:
                return item, True, 'OK'
            else:
                return item, False, 'Empty content'
    except urllib.error.HTTPError as e:
        return item, False, f'Status {e.code}'
    except Exception as e:
        return item, False, str(e)

with ThreadPoolExecutor(max_workers=20) as ex:
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

with open('valid_sources3.txt', 'w', encoding='utf-8') as f:
    for u, p in valid:
        f.write(f"    ('{u}', '{p}'),\n")
