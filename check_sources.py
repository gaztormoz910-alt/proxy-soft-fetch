import re
import urllib.request
from bs4 import BeautifulSoup

def extract_urls_from_file(filepath):
    try:
        content = open(filepath, encoding='utf-8').read()
        return set(re.findall(r'https?://[a-zA-Z0-9.-]+(?:/[^\s\'"<]*)?', content))
    except Exception as e:
        return set()

existing_urls = extract_urls_from_file('c:/Users/Bog_1/OneDrive/Desktop/Fetch Free Proxy/fetch_proxy.py')
print(f'Found {len(existing_urls)} URLs in fetch_proxy.py.')

urls_to_check = [
    "https://github.com/gaztormoz910-alt/smtp-mailer",
    "https://github.com/livetok-ai/live-proxy",
    "https://github.com/gazoprojects/proxy-generator",
    "https://github.com/gazoprojects/proxy-generator/blob/main/proxygen.py",
    "https://github.com/kubaam/Proxy-Checker-and-Generator",
    "https://github.com/constverum/ProxyBroker"
]

new_sources = set()

for url in urls_to_check:
    try:
        print(f"Checking {url}...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        # Simple extraction of anything looking like a raw github or text url containing proxies
        potential_urls = set(re.findall(r'https?://[a-zA-Z0-9.-]+(?:/[^\s\'"<>`]+)', html))
        
        for p_url in potential_urls:
            if p_url not in existing_urls:
                if 'raw.githubusercontent.com' in p_url or '.txt' in p_url or 'api.' in p_url or 'proxy' in p_url.lower():
                    # filter out github html pages, we want raw lists or APIs
                    if 'github.com' in p_url and '/blob/' in p_url:
                        continue
                    new_sources.add(p_url)
    except Exception as e:
        print(f"Error checking {url}: {e}")

print(f"Found {len(new_sources)} potential new sources.")
with open('new_sources_found.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_sources))
