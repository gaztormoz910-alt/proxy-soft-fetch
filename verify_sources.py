import json
import urllib.request
import re
import urllib.error
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. Read existing URLs from fetch_proxy.py to avoid duplicates
existing_urls = set()
with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
    text = f.read()
    urls = re.findall(r'[\'"](https?://[^\'"]+)[\'"]', text)
    for url in urls:
        existing_urls.add(url)

# 2. Read the 688 extracted URLs
with open('extracted_urls.json', 'r', encoding='utf-8') as f:
    historical_urls = json.load(f)

# 3. GitHub Token for API requests
GITHUB_TOKEN = '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'

def check_url(url):
    # If it's already in the file, skip it entirely
    if url in existing_urls:
        return None
        
    # Check if GitHub URL
    # format: https://raw.githubusercontent.com/user/repo/branch/file
    is_github = False
    if 'raw.githubusercontent.com' in url:
        is_github = True
        parts = url.split('/')
        if len(parts) >= 6:
            user = parts[3]
            repo = parts[4]
            branch = parts[5]
            file_path = '/'.join(parts[6:])
            api_url = f'https://api.github.com/repos/{user}/{repo}/commits?path={file_path}&sha={branch}&per_page=1'
            
            # Request github API
            req = urllib.request.Request(api_url)
            req.add_header('Authorization', f'token {GITHUB_TOKEN}')
            req.add_header('User-Agent', 'Mozilla/5.0')
            try:
                resp = urllib.request.urlopen(req, timeout=10)
                data = json.loads(resp.read())
                if len(data) > 0:
                    last_date_str = data[0]['commit']['committer']['date']
                    # e.g., "2023-11-20T18:14:02Z"
                    import datetime
                    last_date = datetime.datetime.strptime(last_date_str, "%Y-%m-%dT%H:%M:%SZ")
                    days_ago = (datetime.datetime.utcnow() - last_date).days
                    if days_ago > 365:
                        return None # Too old!
                else:
                    return None # No commits found, weird
            except Exception as e:
                return None # API error or 404
                
    # Now verify if the actual URL returns 200 OK
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        if resp.getcode() == 200:
            return url
    except Exception:
        return None

valid_new_urls = []
print(f"Total historical URLs: {len(historical_urls)}")
print(f"Skipping URLs already in fetch_proxy.py")

# Process in parallel
with ThreadPoolExecutor(max_workers=30) as executor:
    futures = {executor.submit(check_url, u): u for u in historical_urls}
    for count, future in enumerate(as_completed(futures), 1):
        if count % 50 == 0:
            print(f"Checked {count}/{len(historical_urls)}...")
        res = future.result()
        if res:
            valid_new_urls.append(res)

print(f"Finished. Found {len(valid_new_urls)} new valid dynamic URLs.")
with open('valid_new_urls.json', 'w', encoding='utf-8') as f:
    json.dump(valid_new_urls, f, indent=2)
