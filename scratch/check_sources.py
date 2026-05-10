import re
import requests
import urllib3
import json
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

raw_text = """
https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/http.txt
https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/socks4.txt
https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/socks5.txt
https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt
https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt
https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt
https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt
https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json
https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.csv
https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt
https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json
https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.csv
https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt
https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.json
https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.csv
https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt
https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.json
https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.csv
https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt
https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt
https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt
https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt
https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/json/proxies.json
https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/csv/proxies.csv
https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/xml/proxies.xml
https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/yaml/proxies.yaml
https://raw.githubusercontent.com/fyvri/fresh-proxy-list/main/latest/proxies.txt
https://raw.githubusercontent.com/fyvri/fresh-proxy-list/main/latest/proxies.json
https://raw.githubusercontent.com/fyvri/fresh-proxy-list/main/latest/proxies.csv
https://raw.githubusercontent.com/fyvri/fresh-proxy-list/main/latest/proxies.xml
https://raw.githubusercontent.com/fyvri/fresh-proxy-list/main/latest/proxies.yaml
https://raw.githubusercontent.com/mmpx12/proxy-list/master/proxies.txt
https://raw.githubusercontent.com/mmpx12/proxy-list/master/proxies.json
https://raw.githubusercontent.com/mmpx12/proxy-list/master/proxies.csv
https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt
https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.json
https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.csv
https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt
https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.json
https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.csv
https://raw.githubusercontent.com/zloi-user/hideip.me/master/http.txt
https://raw.githubusercontent.com/zloi-user/hideip.me/master/https.txt
https://raw.githubusercontent.com/zloi-user/hideip.me/master/socks4.txt
https://raw.githubusercontent.com/zloi-user/hideip.me/master/socks5.txt
https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt
https://raw.githubusercontent.com/hookzof/socks5_list/master/tg/mtproto.json
https://raw.githubusercontent.com/roosterkid/openproxylist/master/HTTPS.txt
https://raw.githubusercontent.com/roosterkid/openproxylist/master/HTTPS.json
https://raw.githubusercontent.com/roosterkid/openproxylist/master/HTTPS.csv
https://raw.githubusercontent.com/Skillter/ProxyGather/main/working.txt
https://raw.githubusercontent.com/Skillter/ProxyGather/main/http.txt
https://raw.githubusercontent.com/Skillter/ProxyGather/main/https.txt
https://raw.githubusercontent.com/Skillter/ProxyGather/main/socks4.txt
https://raw.githubusercontent.com/Skillter/ProxyGather/main/socks5.txt
https://raw.githubusercontent.com/Skillter/ProxyGather/main/backup.json
https://raw.githubusercontent.com/stormsia/proxy-list/main/proxies/all.txt
https://raw.githubusercontent.com/stormsia/proxy-list/main/proxies/http.txt
https://raw.githubusercontent.com/stormsia/proxy-list/main/proxies/socks4.txt
https://raw.githubusercontent.com/stormsia/proxy-list/main/proxies/socks5.txt
https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/latest/all.txt
https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/latest/http.txt
https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/latest/https.txt
https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/latest/socks4.txt
https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/latest/socks5.txt
https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/latest/all.json
https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/latest/top-http.json
https://raw.githubusercontent.com/GoekhanDev/free-proxy-list/main/proxies/all.json
https://raw.githubusercontent.com/GoekhanDev/free-proxy-list/main/proxies/all.csv
https://raw.githubusercontent.com/GoekhanDev/free-proxy-list/main/proxies/all.txt
https://raw.githubusercontent.com/GoekhanDev/free-proxy-list/main/proxies/http.json
https://raw.githubusercontent.com/GoekhanDev/free-proxy-list/main/proxies/http.csv
https://raw.githubusercontent.com/GoekhanDev/free-proxy-list/main/proxies/http.txt
https://raw.githubusercontent.com/GoekhanDev/free-proxy-list/main/proxies/socks4.json
https://raw.githubusercontent.com/GoekhanDev/free-proxy-list/main/proxies/socks4.csv
https://raw.githubusercontent.com/GoekhanDev/free-proxy-list/main/proxies/socks4.txt
https://raw.githubusercontent.com/GoekhanDev/free-proxy-list/main/proxies/socks5.json
https://raw.githubusercontent.com/GoekhanDev/free-proxy-list/main/proxies/socks5.csv
https://raw.githubusercontent.com/GoekhanDev/free-proxy-list/main/proxies/socks5.txt
https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/working_proxies.txt
https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable.txt
https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Stable.txt
https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Unstable.txt
https://raw.githubusercontent.com/Hatois/free-proxy-list/main/proxies/latest/http.txt
https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/proxies/http/latest.txt
https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/proxies/https/latest.txt
https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/proxies/socks4/latest.txt
https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/proxies/socks5/latest.txt
https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/proxies/all.json
https://raw.githubusercontent.com/handeveloper1/DailyProxy---Auto-Update-List/main/HTTPS.txt
https://raw.githubusercontent.com/handeveloper1/DailyProxy---Auto-Update-List/main/HTTP.txt
https://raw.githubusercontent.com/handeveloper1/DailyProxy---Auto-Update-List/main/SOCKS4.txt
https://raw.githubusercontent.com/handeveloper1/DailyProxy---Auto-Update-List/main/SOCKS5.txt
https://raw.githubusercontent.com/Firmfox/Proxify/main/proxy.txt
https://raw.githubusercontent.com/Firmfox/Proxify/main/proxy.json
https://raw.githubusercontent.com/Firmfox/Proxify/main/proxy_v2ray.txt
https://raw.githubusercontent.com/Firmfox/Proxify/main/proxy_v2ray.json
https://raw.githubusercontent.com/SoliSpirit/mtproto/main/mtproto.txt
https://raw.githubusercontent.com/SoliSpirit/mtproto/main/mtproto.json
https://raw.githubusercontent.com/Grim1313/mtproto-for-telegram/main/mtproto.txt
https://raw.githubusercontent.com/Grim1313/mtproto-for-telegram/main/mtproto.json
https://raw.githubusercontent.com/26info/vless-proxy-list/main/working-proxies.txt
https://raw.githubusercontent.com/duckray-client/free-vless-keys/main/keys.txt
https://raw.githubusercontent.com/duckray-client/free-vless-keys/main/keys.json
https://raw.githubusercontent.com/Farid-Karimi/Config-Collector/main/configs.txt
https://raw.githubusercontent.com/Farid-Karimi/Config-Collector/main/configs.json
https://raw.githubusercontent.com/MrMohebi/xray-proxy-grabber-telegram/main/output/proxies.json
https://raw.githubusercontent.com/MrMohebi/xray-proxy-grabber-telegram/main/output/proxies.yaml
https://raw.githubusercontent.com/V2RayRoot/V2RayConfig/main/config.txt
https://raw.githubusercontent.com/V2RayRoot/V2RayConfig/main/config.json
https://raw.githubusercontent.com/ircfspace/tconfig/main/config.txt
https://raw.githubusercontent.com/ircfspace/tconfig/main/config.json
https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/configs.txt
https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/configs.json
https://raw.githubusercontent.com/pourih/pfs-servers-list/main/servers.txt
https://raw.githubusercontent.com/pourih/pfs-servers-list/main/servers.json
https://raw.githubusercontent.com/M450ud/config-fetcher/main/configs.txt
https://raw.githubusercontent.com/M450ud/config-fetcher/main/configs.json
https://raw.githubusercontent.com/rtwo2/FastNodes/main/nodes.txt
https://raw.githubusercontent.com/rtwo2/FastNodes/main/nodes.json
https://raw.githubusercontent.com/asakura42/vss/main/servers.txt
https://raw.githubusercontent.com/asakura42/vss/main/servers.json
https://raw.githubusercontent.com/xing2kong/ProxyScraper2/main/http.txt
https://raw.githubusercontent.com/xing2kong/ProxyScraper2/main/sock4.txt
https://raw.githubusercontent.com/xing2kong/ProxyScraper2/main/sock5.txt
https://raw.githubusercontent.com/vAHiD55555/ProxyScraper/main/proxies.txt
https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/all.json
https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/all.txt
https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/http.json
https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/http.txt
https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/socks4.json
https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/socks4.txt
https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/socks5.json
https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/socks5.txt
https://raw.githubusercontent.com/PhoenixZuko/website-proxy-automation/main/proxies.json
https://raw.githubusercontent.com/Itzyetiii/Proxiescraper/main/proxies.txt
https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_ru.txt
https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_eu.txt
https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_all.txt
https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/all_proxies.txt
https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/http.txt
https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/socks4.txt
https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/socks5.txt
https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxies.txt
https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxies.json
https://raw.githubusercontent.com/MuadPro/proxy-list/main/proxies.txt
https://raw.githubusercontent.com/MuadPro/proxy-list/main/proxies.json
https://raw.githubusercontent.com/theriturajps/proxy-list/main/proxies.txt
https://raw.githubusercontent.com/theriturajps/proxy-list/main/proxies.json
https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies.txt
https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies.json
https://raw.githubusercontent.com/wyu-4/osint-proxy/main/proxies/http.txt
https://raw.githubusercontent.com/wyu-4/osint-proxy/main/proxies/https.txt
https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/proxies.txt
https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/proxies.json
https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/proxies.csv
https://raw.githubusercontent.com/Argh94/Proxy-List/main/proxies.txt
https://raw.githubusercontent.com/Argh94/Proxy-List/main/proxies.json
https://raw.githubusercontent.com/mahdibland/V2RayAggregator/main/sub/sub_merge.txt
https://raw.githubusercontent.com/mahdibland/V2RayAggregator/main/sub/sub_merge_yaml.yml
https://raw.githubusercontent.com/mahdibland/V2RayAggregator/main/sub/sub_merge_base64.txt
https://raw.githubusercontent.com/wzdnzd/aggregator/main/data/clash.yaml
https://raw.githubusercontent.com/wzdnzd/aggregator/main/data/v2ray.txt
https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/config.json
https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/config.txt
https://proxylist.to/proxy-list.txt
https://proxyroller.com/proxy.txt
https://proxyscrape.com/free-proxy-list/get
https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=protocolonly&format=text&timeout=20000
https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks4&proxy_format=protocolonly&format=text&timeout=20000
https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5&proxy_format=protocolonly&format=text&timeout=20000
https://proxifly.dev/api/proxy/latest.txt
https://proxifly.dev/api/proxy/latest.json
https://proxifly.dev/api/proxy/latest.csv
https://proxifly.dev/api/proxy/http/latest.txt
https://proxifly.dev/api/proxy/http/latest.json
https://proxifly.dev/api/proxy/http/latest.csv
https://proxifly.dev/api/proxy/https/latest.txt
https://proxifly.dev/api/proxy/https/latest.json
https://proxifly.dev/api/proxy/https/latest.csv
https://proxifly.dev/api/proxy/socks4/latest.txt
https://proxifly.dev/api/proxy/socks4/latest.json
https://proxifly.dev/api/proxy/socks4/latest.csv
https://proxifly.dev/api/proxy/socks5/latest.txt
https://proxifly.dev/api/proxy/socks5/latest.json
https://proxifly.dev/api/proxy/socks5/latest.csv
https://proxy5.net/api/free-proxy?format=txt
https://proxy5.net/api/free-proxy?format=csv
https://proxy5.net/api/free-proxy?format=json
https://proxy-list.download/api/v2/get?l=en&t=text
https://proxy-list.download/api/v2/get?l=en&t=csv
https://proxy-list.download/api/v2/get?l=en&t=json
https://proxysniper.com/api/proxy?format=text
https://proxysniper.com/api/proxy?format=json
https://free-proxy-list.net/export/txt
https://free-proxy-list.net/export/json
https://free-proxy-list.net/export/csv
https://spys.me/proxy.txt
https://spys.me/proxy.json
https://spys.one/proxy.txt
https://spys.one/proxy.json
https://openproxy.space/list/txt
https://openproxy.space/list/json
https://openproxy.space/list/csv
https://clearproxy.io/api/proxies?format=txt
https://clearproxy.io/api/proxies?format=json
https://clearproxy.io/api/proxies?format=csv
https://getfreeproxy.com/api/v1/proxies?format=txt
https://getfreeproxy.com/api/v1/proxies?format=json
https://getfreeproxy.com/api/v1/proxies?format=csv
https://proxystash.com/api/proxy?format=txt
https://proxystash.com/api/proxy?format=json
https://proxystash.com/api/proxy?format=csv
https://rapidapi.com/sharmadhirajnp2/api/free-proxies-api/endpoints
https://pastebin.com/raw/XJsxHu4D
https://codeberg.org/dbarker/public-proxy-list/raw/branch/main/proxies.txt
https://bitbucket.org/vanholt-proxies/public-http-proxies/raw/main/README.md
https://telegra.ph/Free-Proxy-List-for-Scraping-and-SEO-Updated-Daily-04-07
https://docs.google.com/spreadsheets/d/1guW73RgKLUcLUFGx9QRtqtAmbqMJG7aXKJGlT_XU2t4/export?format=csv
https://docs.google.com/spreadsheets/d/1guW73RgKLUcLUFGx9QRtqtAmbqMJG7aXKJGlT_XU2t4/export?format=txt
"""

links = re.findall(r'https?://[^\s]+', raw_text)
# Deduplicate links natively
unique_links = list(set(links))

print(f"Total links given: {len(links)}")
print(f"Total unique links: {len(unique_links)}")

# Filter out non raw formats for our proxy hunter (.json, .txt, API endpoints)
# Ignore github repo base links, pypi, docs, pub.dev etc.
filtered = []
for link in unique_links:
    if "pypi.org" in link or "github.com" in link and "raw.githubusercontent" not in link and "api.github" not in link: continue
    if "pkg.go.dev" in link or "pub.dev" in link or "t.me" in link or "lolz.live" in link or "nohide.space" in link or "crackermain" in link: continue
    if link.endswith('.csv') or link.endswith('.xml') or link.endswith('.yaml') or link.endswith('.yml'): continue # we don't parse csv properly yet or xml, and json/txt is usually alongside it.
    filtered.append(link)

print(f"Filtered raw endpoints: {len(filtered)}")

valid = []
dead = []

def check(url):
    try:
        r = requests.get(url, timeout=5, verify=False, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            if len(r.text) > 10: # Ensure it has some content
                return True, url
        return False, url
    except:
        return False, url

with ThreadPoolExecutor(max_workers=50) as executor:
    results = executor.map(check, filtered)
    for is_ok, url in results:
        if is_ok:
            valid.append(url)
        else:
            dead.append(url)

with open('scratch/valid_sources.json', 'w') as f:
    json.dump({'valid': valid, 'dead': dead}, f, indent=2)

print(f"Valid: {len(valid)}, Dead: {len(dead)}")
