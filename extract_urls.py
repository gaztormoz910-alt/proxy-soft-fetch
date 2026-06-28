import subprocess
import re
import json

repo_dir = r'c:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy'

commits = subprocess.check_output(['git', 'log', '--format=%h'], cwd=repo_dir).decode('utf-8').strip().split('\n')
print(f'Found {len(commits)} commits.')

all_urls = set()

for commit in commits:
    try:
        content = subprocess.check_output(['git', 'show', f'{commit}:fetch_proxy.py'], cwd=repo_dir, stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
        
        # Regex to find all string literals that look like URLs
        urls = re.findall(r'[\'"](https?://[^\'"]+)[\'"]', content)
        for url in urls:
            # Filter out known non-proxy sources
            if 'github.com' in url and 'GeoLite' in url: continue
            if 'api.github.com' in url: continue
            if 'ip-api.com' in url: continue
            if 'ipinfo.io' in url: continue
            if 'speedtest.tele2.net' in url: continue
            if 'portquiz.net' in url: continue
            if 'raw.githubusercontent.com' not in url and 'github' in url: continue # usually repo links
            
            all_urls.add(url)
    except Exception as e:
        pass

print(f'Found {len(all_urls)} unique URLs.')
with open(r'c:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy\extracted_urls.json', 'w', encoding='utf-8') as f:
    json.dump(list(all_urls), f, indent=2)
