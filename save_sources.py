NEW_SOCKS5_SOURCES = [
    # --- GitHub Raw (Где ты пропустил socks5 или их вообще не было в списке) ---
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt', 'socks5'), # У тебя был socks4, но 5-й ты упустил
    ('https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt', 'socks5'), # У тебя от них был только HTTPS
    ('https://raw.githubusercontent.com/Boster12/Free_Proxy_List/main/socks5.txt', 'socks5'), # Тоже был только HTTPS
    ('https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/socks5.txt', 'socks5'), # Был только socks4
    ('https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ArrayIterator/proxy-lists/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/zenjahid/FreeProxy4u/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxylist-to/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/casals-ar/proxy-list/main/socks5', 'socks5'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5.txt', 'socks5'), # У тебя SOCKS5_RAW, а это другой файл с иной структурой

    # --- API и сервисы (Без 404, стабильно отдают свежак) ---
    ('https://www.proxy-list.download/api/v1/get?type=socks5', 'socks5'),
    ('https://cdn.rei.my.id/proxy/SOCKS5', 'socks5'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5&proxy_format=ipport&format=text&timeout=3000', 'socks5'), # v3 эндпоинт SOCKS5 (у тебя был v2 и v4)
]

# --- ПАГИНАЦИЯ (Динамика API) ---
# Geonode API: собираем чистые SOCKS5 без привязки к стране (сортировка по свежести)
NEW_SOCKS5_SOURCES.extend([(f'https://proxylist.geonode.com/api/proxy-list?limit=500&page={i}&sort_by=lastChecked&sort_type=desc&protocols=socks5', 'socks5') for i in range(1, 15)])

MOAR_SOCKS5_SOURCES = [
    # ⚡️ ТОП: Серьёзные чекеры (Глубокая проверка соединений, отбрасывают дохлый мусор)
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/Stable/socks5.txt', 'socks5'),
    
    # ⚡️ ТОП: Огромные агрегаторы (Много сырых IP)
    # gfpcom прячет листы в ветке wiki - там лежит гигантский пул
    ('https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/socks5.txt', 'socks5'),
    # У тебя в базе были checked-листы от dinoz0rg, но тут его огромная scraped-база
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/scraped_proxies/socks5.txt', 'socks5'), 
    
    # ⚡️ ТОП: Обновление каждые 15-30 минут (Активные боты)
    ('https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/socks5_all.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/refs/heads/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt', 'socks5'),

    # 🕸️ Web API, которые отдают чистый SOCKS5 (Лимиты на API зависят от твоего IP, но не 404)
    ('https://pubproxy.com/api/proxy?format=txt&type=socks5', 'socks5'),
]

DEEP_WEB_SOCKS5_SOURCES = [
    # 🕵️♂️ Узкоспециализированные парсеры (Отличный свежак, часто обновляются)
    ('https://raw.githubusercontent.com/RX4096/proxy-list/main/online/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Androz2091/proxies/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/NotUnko/autoproxies/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/AGDDoS/AGDDoS/main/proxies/socks5.txt', 'socks5'),
    
    # 🥷 У тебя был ProxyForEveryone, но там ты брал общий "Proxies.txt", 
    # а у них есть отдельный отфильтрованный дамп чисто по пятым носкам:
    ('https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/socks5/socks5.txt', 'socks5'),
    
    # 🛠️ Свежие форки и личные свалки авторегеров (Малоизвестные, но живые)
    ('https://raw.githubusercontent.com/xzus/Proxy-scraper/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ttxtxt/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/mrcakil/MrcakilProxyList/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Vigov5/github-proxy/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/a2u/free-proxy-list/master/free-proxy-list-socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/NoName-404/proxy-list/main/socks5.txt', 'socks5'),

    # 📡 Telegram-каналы (Web-шлюз). Они часто постят сырые списки IP:PORT прямо в сообщениях.
    ('https://t.me/s/proxy_list_socks5', 'socks5'),
    ('https://t.me/s/proxylist_free', 'socks5'),
]

INSANE_SOCKS5_SOURCES = [
    # 🔥 Свежак от независимых ботов-скраперов на GitHub
    ('https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/dpangestian/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Bardiafa/Proxy-Leecher/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Wannabe1337/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/saisuiu/uiu/main/free_proxy/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/fahimk58/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/KutG0/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/roxy-tt/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Zallerick/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ToffanUS/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt', 'socks5'),
    
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=all&anonymity=elite', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=all&anonymity=anonymous', 'socks5'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5&proxy_format=protocolipport&format=text&anonymity=elite', 'socks5'),
]

INSANE_SOCKS5_SOURCES.extend([(f'https://proxylist.geonode.com/api/proxy-list?limit=500&page={i}&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite', 'socks5') for i in range(1, 10)])
INSANE_SOCKS5_SOURCES.extend([(f'https://proxylist.geonode.com/api/proxy-list?limit=500&page={i}&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=anonymous', 'socks5') for i in range(1, 10)])

import datetime
today = datetime.datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

FINAL_SOCKS5_SOURCES = [
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/ForSites/google/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/ForSites/discord/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/ForSites/instagram/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/ForSites/netflix/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/telegramProxys.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/discord/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/google/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/reddit/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/tiktok/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/custom/x/socks5.txt', 'socks5'),
]
FINAL_SOCKS5_SOURCES.append((f'https://checkerproxy.net/api/archive/{today}', 'socks5'))
FINAL_SOCKS5_SOURCES.append((f'https://checkerproxy.net/api/archive/{yesterday}', 'socks5'))

top_countries = ['US', 'GB', 'DE', 'FR', 'CA', 'BR', 'RU', 'IN', 'ID', 'CN', 'JP', 'KR', 'VN', 'IR', 'UA', 'PL']
FINAL_SOCKS5_SOURCES.extend([(f'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country={c}', 'socks5') for c in top_countries])

ABYSS_SOCKS5_SOURCES = [
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/stamparm/aux/master/fetch-public-proxies/list.txt', 'socks5'),
    ('https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list', 'socks5'),
    ('https://raw.githubusercontent.com/Aptans/Proxy-Scraper/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/cherviel/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Xyliuss/Proxy-List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/jubaer-hosain/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Zall-dev/proxy-list/main/socks5.txt', 'socks5'),
]

matrix_countries = ['US', 'GB', 'DE', 'FR', 'CA', 'BR', 'RU', 'IN', 'ID', 'CN', 'JP', 'KR', 'VN', 'IR', 'UA', 'PL', 'TR', 'IT', 'ES', 'NL']
for country in matrix_countries:
    for page in range(1, 4):
        ABYSS_SOCKS5_SOURCES.append((f'https://proxylist.geonode.com/api/proxy-list?limit=500&page={page}&sort_by=lastChecked&sort_type=desc&protocols=socks5&country={country}', 'socks5'))

MARIANA_TRENCH_SOCKS5 = [
    ('https://raw.githubusercontent.com/MiyakoYakusa/auto-proxy/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/LancerXz/Proxy-List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Thongz-1/Proxy-List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Bhinneka-Sec/Proxy-List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/AliAbedalkarim/Proxy-List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/mhmjz/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/carldago/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/rohitbabu56/Proxy-List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/MrAdnane/Proxy-List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/SlavaBazanov/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/ZephrFish/Free-Proxy-List/main/socks5.txt', 'socks5'),
    ('https://t.me/s/v2ray_vpn_config', 'socks5'),
    ('https://t.me/s/socks5_proxy_list', 'socks5'),
    ('https://t.me/s/vpn_proxy_socks5', 'socks5'),
    ('https://t.me/s/proxy_socks5_free', 'socks5'),
]

ULTIMATE_SOCKS5_ENDPOINTS = [
    ('https://www.proxyscan.io/download?type=socks5', 'socks5'),
    ('https://www.proxyscan.io/api/proxy?format=txt&type=socks5&limit=1000', 'socks5'),
    ('https://api.proxyscrape.com/proxytable.php?type=socks5', 'socks5'),
    ('https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/socks5.txt', 'socks5'), 
    ('https://raw.githubusercontent.com/0x1337fy/fresh-proxy-list/archive/storage/classic/socks5.txt', 'socks5'),
]

HTML_SOCKS5_SOURCES = [
    ('https://www.freeproxy.world/?type=socks5', 'socks5'),
    ('https://proxyhub.me/en/all-socks5-proxy-list.html', 'socks5'),
    ('https://hidemy.life/en/proxy-list/socks5', 'socks5'),
]
HTML_SOCKS5_SOURCES.extend([(f'https://www.freeproxy.world/?type=socks5&page={i}', 'socks5') for i in range(1, 11)])
HTML_SOCKS5_SOURCES.extend([(f'https://proxyhub.me/en/all-socks5-proxy-list.html?page={i}', 'socks5') for i in range(1, 11)])

TELEGRAM_MEGA_EMPIRE = [
    ('https://t.me/s/Proxy_socks5_list', 'socks5'),
    ('https://t.me/s/Free_Proxies_Socks5', 'socks5'),
    ('https://t.me/s/proxy_list_scraped', 'socks5'),
    ('https://t.me/s/socks5_proxies_free', 'socks5'),
    ('https://t.me/s/vip_proxy_free', 'socks5'),
    ('https://t.me/s/proxies_for_all', 'socks5'),
    ('https://t.me/s/socks5_list', 'socks5'),
    ('https://t.me/s/socks_proxy_list', 'socks5'),
    ('https://t.me/s/free_proxy_socks5_http', 'socks5'),
    ('https://t.me/s/proxylist_updated', 'socks5'),
    ('https://t.me/s/Premium_proxy_list', 'socks5'),
]

ALL = []
ALL.extend(NEW_SOCKS5_SOURCES)
ALL.extend(MOAR_SOCKS5_SOURCES)
ALL.extend(DEEP_WEB_SOCKS5_SOURCES)
ALL.extend(INSANE_SOCKS5_SOURCES)
ALL.extend(FINAL_SOCKS5_SOURCES)
ALL.extend(ABYSS_SOCKS5_SOURCES)
ALL.extend(MARIANA_TRENCH_SOCKS5)
ALL.extend(ULTIMATE_SOCKS5_ENDPOINTS)
ALL.extend(HTML_SOCKS5_SOURCES)
ALL.extend(TELEGRAM_MEGA_EMPIRE)

# Also there were some raw URLs the user pasted:
raw_urls = """
https://aimultiple.com/socks5-proxies
https://github.com/TheSpeedX/PROXY-List/blob/master/socks5.txt
https://cocalc.com/github/TheSpeedX/PROXY-List/blob/master/socks5.txt
https://proxyscrape.com/free-proxy-list/germany#free-proxy-table
https://www.911proxy.com/socks-5-proxy-list-txt/
https://github.com/roosterkid/openproxylist/blob/main/SOCKS5.txt
https://discourse.openbullet.dev/t/fetch-proxies-remove-dupes-api/7930
https://databay.com/free-proxy-list/socks5
https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt
https://www.proxy4free.com/blog/proxy-txt/?srsltid=AfmBOopqjc0ff6g4CXN0jsuEz1-w7WwGToOwi17ynXPAfpZWx_U1Vzsj
https://docs.brightdata.com/proxy-networks/socks5
https://wproxy.org/en/docs/rules/socks.html
https://httpie.io/docs/cli/other-notes
https://mullvad.net/en/help/socks5-proxy
https://github.com/vakhov/fresh-proxy-list/blob/master/socks5.txt
https://proxyscrape.com/free-proxy-list
"""
for line in raw_urls.strip().split('\n'):
    u = line.strip()
    if u:
        if 'github.com' in u and '/blob/' in u:
            u = u.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
        ALL.append((u, 'socks5'))

import json
with open('all_new_sources.json', 'w') as f:
    json.dump(ALL, f)

print(f"Saved {len(ALL)} sources to all_new_sources.json")
