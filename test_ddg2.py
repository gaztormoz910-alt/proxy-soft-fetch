import sys
sys.path.append('.')
from fetch_proxy import ProxyUtils
import re

url = 'https://html.duckduckgo.com/html/?q=site:pastebin.com+"socks5"+intext:"1080"&df=d'
content = ProxyUtils.fetch_url(url, 15)
with open('ddg_content.html', 'w', encoding='utf-8') as f:
    f.write(content if content else '')

# Find the duckduckgo proxy link
links = re.findall(r'href="(/l/\?uddg=[^"]+)"', content if content else '')
print("uddg links:", len(links))

direct_links = re.findall(r'href="(https?://(?:pastebin\.com|rentry\.co|ghostbin\.com)[^"]+)"', content if content else '')
print("direct links:", len(direct_links))
