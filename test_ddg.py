import sys
sys.path.append('.')
from fetch_proxy import ProxyUtils
import re
from urllib.parse import urlparse, parse_qs, unquote

url = 'https://html.duckduckgo.com/html/?q=site:pastebin.com+"socks5"+intext:"1080"&df=d'
content = ProxyUtils.fetch_url(url, 15)
if not content:
    print("Failed to fetch")
    sys.exit(1)

links = re.findall(r'href="/l/\?uddg=([^"]+)"', content)
real_links = [unquote(l) for l in links]

print("Found:", len(real_links))
if real_links:
    for link in real_links[:5]:
        print(link)
