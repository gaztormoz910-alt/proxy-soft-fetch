import requests

repos = ["r00tee/Proxy-List", "noctiro/getproxy", "Airuop/cross"]
for repo in repos:
    try:
        url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 404:
            url = f"https://api.github.com/repos/{repo}/git/trees/master?recursive=1"
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        if resp.status_code == 200:
            files = [item['path'] for item in resp.json().get('tree', []) if item['type'] == 'blob' and item['path'].endswith('.txt')]
            print(f"[{repo}] Files: {files[:10]}")
        else:
            print(f"[{repo}] Error: {resp.status_code}")
    except Exception as e:
        print(f"[{repo}] Error: {e}")
