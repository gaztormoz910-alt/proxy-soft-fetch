import requests

urls = [
    'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
    'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt',
    'https://raw.githubusercontent.com/almroot/proxylist/master/list.txt',
    'https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/http.txt',
    'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt'
]

for url in urls:
    try:
        r = requests.head(url)
        print(f'{url.split("/")[3]}: {r.headers.get("Last-Modified", "None")}')
    except:
        pass
