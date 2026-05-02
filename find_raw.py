import requests

repos = ["r00tee/Proxy-List", "Firmfox/Proxify", "noctiro/getproxy", "Airuop/cross"]
paths = [
    "main/proxies/http.txt", "main/proxies/socks5.txt",
    "master/proxies/http.txt", "master/proxies/socks5.txt",
    "main/http.txt", "main/socks5.txt",
    "master/http.txt", "master/socks5.txt",
    "main/proxies.txt", "master/proxies.txt"
]

for repo in repos:
    for path in paths:
        url = f"https://raw.githubusercontent.com/{repo}/{path}"
        r = requests.get(url)
        if r.status_code == 200:
            print(f"FOUND: {url}")
