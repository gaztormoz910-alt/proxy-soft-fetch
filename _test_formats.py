import urllib.request

test_urls = [
    "https://databay.com/api/v1/proxy-list?format=csv",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.csv",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json",
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=json&protocol=http",
    "http://htmlweb.ru/analiz/proxy_list.php"
]

for url in test_urls:
    print(f"\n--- {url} ---")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            content = response.read().decode('utf-8', errors='ignore')
            print(content[:300])
    except Exception as e:
        print(f"Error: {e}")
