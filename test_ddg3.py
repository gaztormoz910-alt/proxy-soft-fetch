import sys
sys.path.append('.')
from fetch_proxy import ProxyUtils
import re

url = 'https://html.duckduckgo.com/html/?q=site:pastebin.com+"socks5"'
content = ProxyUtils.fetch_url(url, 15)
links = re.findall(r'href="(//duckduckgo\.com/l/\?uddg=[^"]+)"', content if content else '')
print('Found uddg links:', len(links))

links2 = re.findall(r'class="result__url"\s+href="([^"]+)"', content if content else '')
print('Found result__url links:', len(links2))
