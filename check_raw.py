import requests
urls = [
    "https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/http.txt",
    "https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/iplocate/free-proxy-list/main/all-proxies.txt",
    "https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/socks5.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
    "https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/proxies/socks5.txt",
]

for url in urls:
    resp = requests.get(url)
    print(f"{url} -> {resp.status_code}")
