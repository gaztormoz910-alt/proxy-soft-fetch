import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

def download(url, filename):
    try:
        r = requests.get(url, headers=headers, timeout=15)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(r.text)
        print(f"Saved {url} to {filename} (Len: {len(r.text)})")
    except Exception as e:
        print(f"Error {url}: {e}")

download('https://spys.one/en/free-proxy-list/', 'spys.html')
download('https://hidemy.name/en/proxy-list/', 'hidemy.html')
download('https://proxy-list.download/api/v1/get?type=http', 'proxy_list_download.txt')
