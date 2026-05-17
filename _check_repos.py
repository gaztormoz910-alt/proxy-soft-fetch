import requests, json, sys
from datetime import datetime

repos = [
    "TheSpeedX/PROXY-List", "monosans/proxy-list", "komutan234/Proxy-List-Free",
    "proxifly/free-proxy-list", "hookzof/socks5_list", "fyvri/fresh-proxy-list",
    "jetkai/proxy-list", "dinoz0rg/proxy-list", "r00tee/Proxy-List",
    "Vann-Dev/proxy-list", "roosterkid/openproxylist", "mmpx12/proxy-list",
    "Firmfox/Proxify", "Ian-Lusule/Proxies", "xing2kong/ProxyScraper2",
    "vAHiD55555/ProxyScraper", "zloi-user/hideip.me", "ShiftyTR/Proxy-List",
    "clarketm/proxy-list", "theriturajps/proxy-list", "iplocate/free-proxy-list",
    "proxygenerator1/ProxyGenerator", "Thordata/awesome-free-proxy-list",
    "stormsia/proxy-list", "GoekhanDev/free-proxy-list", "Hatois/free-proxy-list",
    "ClearProxy/checked-proxy-list", "handeveloper1/DailyProxy---Auto-Update-List",
    "Skillter/ProxyGather", "kort0881/telegram-proxy-collector",
    "ALIILAPRO/Proxy", "databay-labs/free-proxy-list", "murtaja89/public-proxies",
    "Anonym0usWork1221/Free-Proxies", "MuadPro/proxy-list",
    "26info/vless-proxy-list", "Argh94/Proxy-List",
]

now = datetime.utcnow()
alive = []
dead = []

for repo in repos:
    try:
        r = requests.get(f"https://api.github.com/repos/{repo}", timeout=10)
        if r.status_code == 404:
            dead.append((repo, "404 NOT FOUND"))
            continue
        d = r.json()
        pushed = d.get("pushed_at", "")
        archived = d.get("archived", False)
        
        if pushed:
            dt = datetime.strptime(pushed, "%Y-%m-%dT%H:%M:%SZ")
            days = (now - dt).days
        else:
            days = 9999
            
        status = "ARCHIVED" if archived else ("ALIVE" if days < 30 else f"STALE ({days}d)")
        entry = f"{repo:50s} | {status:15s} | last push: {pushed[:10] if pushed else 'N/A':10s} | {days}d ago"
        
        if status == "ALIVE":
            alive.append(entry)
        else:
            dead.append((repo, entry))
        
        print(entry)
    except Exception as e:
        dead.append((repo, str(e)))
        print(f"{repo:50s} | ERROR: {e}")

print(f"\n{'='*80}")
print(f"ALIVE: {len(alive)} | DEAD/STALE: {len(dead)}")
