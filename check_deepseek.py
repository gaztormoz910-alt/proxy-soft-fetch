import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

github_repos = [
    "proxygenerator1/ProxyGenerator",
    "prxchk/proxy-list",
    "Ian-Lusule/Proxies",
    "iplocate/free-proxy-list",
    "mmpx12/proxy-list",
    "mahdiproxyca/Proxy",
    "gfpcom/free-proxy-list",
    "nikita29a/FreeProxyList"
]

urls_to_check = [
    "https://api.getproxylist.com/",
    "https://api.proxify.workers.dev",
    "https://api.proxylist.to/",
    "https://api.torproxies.info/get",
    "https://www.zdaye.com/doc/api/FreeProxy_get",
    "https://openproxy.space/list",
    "https://www.socks-proxy.net/",
    "https://www.freeproxylists.net/"
]

def check_github(repo):
    try:
        api_url = f"https://api.github.com/repos/{repo}/commits?per_page=1"
        resp = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            date = resp.json()[0]['commit']['committer']['date']
            return f"[GitHub] {repo}: Last updated {date}"
        else:
            return f"[GitHub] {repo}: Error {resp.status_code}"
    except Exception as e:
        return f"[GitHub] {repo}: Error {str(e)}"

def check_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url, headers=headers, timeout=10)
        return f"[URL] {url} - Status: {resp.status_code}, Length: {len(resp.text)}"
    except Exception as e:
        return f"[URL] {url} - Error: {str(type(e).__name__)}"

print("Checking Deepseek sources...")

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    for r in github_repos:
        futures.append(executor.submit(check_github, r))
    for u in urls_to_check:
        futures.append(executor.submit(check_url, u))
        
    for future in as_completed(futures):
        print(future.result())
