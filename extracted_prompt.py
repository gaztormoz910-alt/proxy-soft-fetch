<USER_REQUEST>
('https://www.proxy-list.download/api/v1/get?type=http', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=https', 'https'),
    ('https://www.proxy-list.download/api/v1/get?type=socks4', 'socks4'),
    ('https://www.proxy-list.download/api/v1/get?type=socks5', 'socks5'),

    # ProxyScan.io - еще один отличный стабильный API с прямой отдачей txt
    ('https://www.proxyscan.io/download?type=http', 'http'),
    ('https://www.proxyscan.io/download?type=https', 'https'),
    ('https://www.proxyscan.io/download?type=socks4', 'socks4'),
    ('https://www.proxyscan.io/download?type=socks5', 'socks5'),

    # Реальные GitHub репозитории (регулярно обновляются ботами, 200 OK)
    ('https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt', 'http'),
    ('https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/https.txt', 'https'),
    ('https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/socks5.txt', 'socks5'),
    
    ('https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/socks5.txt', 'socks5'),

    ('https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt', 'http'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/manuGMG/proxy-365/main/SOCKS5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/AsmSafat/free-proxy-list/master/proxy.txt', 'all'),
    ('https://raw.githubusercontent.com/Zishan-Adil/free-proxy-list/master/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/Toffanello/Free-Proxy-List/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/Bardiafa/Proxy-Leecher/main/proxies.txt', 'all'),

    # Дополнительные Телеграм-каналы (веб-версия t.me/s/ позволяет парсить сырой текст регулярками)
    ('https://t.me/s/Free_Proxies_List', 'all'), 
    ('https://t.me/s/proxy_socks5_http_https', 'all'),
    ('https://t.me/s/Proxy_List_World', 'all')








('https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/https.txt', 'https'),
    ('https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt', 'socks5'),

    # 2. LalatinaHub - стабильно обновляется ботом
    ('https://raw.githubusercontent.com/LalatinaHub/Proxy-List/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/LalatinaHub/Proxy-List/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/LalatinaHub/Proxy-List/main/socks5.txt', 'socks5'),

    # 3. NotUnko - автообновляемые прокси
    ('https://raw.githubusercontent.com/NotUnko/autoupdate-proxies/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/NotUnko/autoupdate-proxies/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/NotUnko/autoupdate-proxies/main/socks5.txt', 'socks5'),

    # 4. Другие рабочие гитхаб-репы с автокоммитами (существующие 100%)
    ('https://raw.githubusercontent.com/devmeireles/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/ahmadhasanakiza/Proxy-List/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Xyli-ous/Proxy-List/main/all.txt', 'all'),
    ('https://raw.githubusercontent.com/FatApe/Proxy-List/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Boster12/Free_Proxy_List/main/http.txt', 'http'), # У тебя был только HTTPS от него
    ('https://raw.githubusercontent.com/Boster12/Free_Proxy_List/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Boster12/Free_Proxy_List/main/socks5.txt', 'socks5'),

    # 5. Telegram-каналы (Используй t.me/s/ - это веб-версия, парсится обычным requests.get)
    # Оттуда просто вытаскиваешь регуляркой r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{2,5}\b'
    ('https://t.me/s/v2ray_free_conf', 'all'),
    ('https://t.me/s/free_proxies_socks5', 'socks5'),
    ('https://t.me/s/ProxyForYou', 'all'),
    ('https://t.me/s/GoodProxy', 'all'),
    ('https://t.me/s/proxies_for_all', 'all'),

    # 6. Proxy11 API (Лимитированный бесплатный доступ, но отдаёт текст)
    ('https://proxy11.com/api/proxy.txt?key=FREE', 'all')







('https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP_RAW.txt', 'http'),
    
    # 2. Прямые ссылки с репозитория fyvri (у тебя парсился их старый архив, а это актуальные main ветки)
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/main/proxies/https.txt', 'https'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/main/proxies/socks5.txt', 'socks5'),

    # 3. Отборные списки VPSLab (у тебя были только общие свалки, а тут строго Elite и Anonymous)
    ('https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_elite.txt', 'http'),
    ('https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_anonymous.txt', 'http'),
    ('https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/all_elite.txt', 'all'),

    # 4. Свежие автообновляемые репозитории (коммитятся ботами регулярно)
    ('https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxy-list/data.txt', 'all'),
    ('https://raw.githubusercontent.com/Zeller-Studios/Proxy-List/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/murtaja89/public-proxies/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/murtaja89/public-proxies/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.json', 'http'), # Огромный JSON с пингами
    
    # 5. Proxies.st Free API (отдают списки напрямую в txt)
    ('https://api.proxies.st/v1/free-list?type=http', 'http'),
    ('https://api.proxies.st/v1/free-list?type=socks4', 'socks4'),
    ('https://api.proxies.st/v1/free-list?type=socks5', 'socks5'),

    # 6. Свежие Телеграм-источники (через t.me/s/ для парсинга IP:PORT)
    ('https://t.me/s/proxies_socks5_http', 'all'),
    ('https://t.me/s/free_proxy_socks5_http', 'all'),
    ('https://t.me/s/proxylist_free_update', 'all')










('https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt', 'http'),
    ('https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt', 'https'),
    ('https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt', 'socks5'),

    # 2. Proxy-list.download API — фильтрация строго по уровню (Elite)
    # (В первой партии я давал общий список, этот запрос отдаст только элитные, скрывающие твой IP)
    ('https://www.proxy-list.download/api/v1/get?type=http&anon=elite', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=https&anon=elite', 'https'),
    ('https://www.proxy-list.download/api/v1/get?type=socks4&anon=elite', 'socks4'),
    ('https://www.proxy-list.download/api/v1/get?type=socks5&anon=elite', 'socks5'),

    # 3. Proxy-list.download API — фильтрация по уровню (Anonymous)
    ('https://www.proxy-list.download/api/v1/get?type=http&anon=anonymous', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=https&anon=anonymous', 'https'),
    ('https://www.proxy-list.download/api/v1/get?type=socks4&anon=anonymous', 'socks4'),
    ('https://www.proxy-list.download/api/v1/get?type=socks5&anon=anonymous', 'socks5'),

    # 4. ProxyScrape API - жесткий таймаут (только быстрые прокси)
    # (Мы запрашиваем список с пингом до 3000мс, он отсеет весь мертвый мусор, который висит в обычных all-запросах)
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=ipport&format=text&timeout=3000', 'http'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks4&proxy_format=ipport&format=text&timeout=3000', 'socks4'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5&proxy_format=ipport&format=text&timeout=3000', 'socks5'),

    # 5. Geonode API - Строго по скорости (Speed = Fast)
    # У тебя уже есть их пагинация, но добавление параметра speed=fast выдает отдельный отсортированный пул
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&speed=fast', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=https&speed=fast', 'https'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks4&speed=fast', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&speed=fast', 'socks5'),

    # 6. Новые живые Телеграм-каналы (Идеально под парсинг регулярками, как я писал выше)
    ('https://t.me/s/socks5list', 'socks5'),
    ('https://t.me/s/Free_Proxy_vip', 'all'),
    ('https://t.me/s/private_proxy_free', 'all'),
    ('https://t.me/s/free_proxy_list_update', 'all'),
    ('https://t.me/s/proxy_socks5_free', 'socks5')










('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt', 'http'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/all.txt', 'all'),

    # 2. ProxyForEveryone - Сводные проверенные пулы (у тебя были только разбитые по папкам)
    ('https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/xResults/Proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/officialputuid/ProxyForEveryone/main/xResults/RAW.txt', 'all'),

    # 3. Good-Proxies API (Публичный эндпоинт, который используют в парсерах на Rust)
    ('https://api.good-proxies.ru/getfree.php?count=1000&key=freeproxy', 'all'),

    # 4. Редкие Гитхаб-репозитории, которые регулярно обновляются скриптами
    ('https://raw.githubusercontent.com/HyperBeats/proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks5.txt', 'socks5'),

    ('https://raw.githubusercontent.com/fahimscirex/proxybd/master/proxylist/http.txt', 'http'),
    ('https://raw.githubusercontent.com/fahimscirex/proxybd/master/proxylist/https.txt', 'https'),
    ('https://raw.githubusercontent.com/fahimscirex/proxybd/master/proxylist/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/fahimscirex/proxybd/master/proxylist/socks5.txt', 'socks5'),

    # 5. Пропущенный HTTPS файл из мощного репо Thordata (у тебя были http, socks, all)
    ('https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/https.txt', 'https'),

    # 6. Свежак: API Proxy-List с открытым доступом к TXT-выгрузке
    ('https://www.proxy-list.download/api/v1/get?type=http&anon=transparent', 'http'),
    ('https://www.proxy-list.download/api/v1/get?type=https&anon=transparent', 'https'),

    # 7. Ещё пачка ТГ-каналов (выдирать регуляркой r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}')
    ('https://t.me/s/socks5_proxy_list', 'socks5'),
    ('https://t.me/s/free_proxy_http_socks5', 'all'),
    ('https://t.me/s/HTTP_Proxy_List', 'http'),
    ('https://t.me/s/proxylist_socks5', 'socks5'),
    
    # 8. Web-scraping (если твой скрипт умеет парсить HTML-код страниц)
    # Это не прямые txt файлы, но отсюда можно вырезать тысячи свежих IP
    ('https://premiumproxy.net/full-proxy-list', 'all'),
    ('https://www.megaproxylist.net/', 'all')












Этот код мне другой ИИ написал:

# === ШЕСТАЯ ПАРТИЯ (Абуз API по странам и новые параметры) ===

# Список самых популярных стран, где крутится 90% прокси серверов мира
TOP_COUNTRIES = ['US', 'RU', 'GB', 'DE', 'FR', 'BR', 'IN', 'CN', 'ID', 'IR', 'KR', 'JP', 'UA', 'NL', 'CA']

API_ABUSE_SOURCES = []

# 1. Выдаиваем Proxy-List.download по каждой стране (Это даст в 5 раз больше уникальных IP)
for country in TOP_COUNTRIES:
    API_ABUSE_SOURCES.extend([
        (f'https://www.proxy-list.download/api/v1/get?type=http&country={country}', 'http'),
        (f'https://www.proxy-list.download/api/v1/get?type=https&country={country}', 'https'),
        (f'https://www.proxy-list.download/api/v1/get?type=socks4&country={country}', 'socks4'),
        (f'https://www.proxy-list.download/api/v1/get?type=socks5&country={country}', 'socks5')
    ])

# 2. Выдаиваем ProxyScrape v2 по странам с жестким пингом и SSL
for country in TOP_COUNTRIES:
    API_ABUSE_SOURCES.extend([
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=2000&country={country}&ssl=yes&anonymity=elite', 'http'),
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=2000&country={country}&anonymity=elite', 'socks4'),
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=2000&country={country}&anonymity=elite', 'socks5')
    ])

# 3. PubProxy обход лимита (Разделяем запросы по типу и уровню анонимности, чтобы вытащить разные пачки)
API_ABUSE_SOURCES.extend([
    ('http://pubproxy.com/api/proxy?limit=5&format=txt&http=true&level=elite', 'http'),
    ('http://pubproxy.com/api/proxy?limit=5&format=txt&http=true&level=anonymous', 'http'),
    ('http://pubproxy.com/api/proxy?limit=5&format=txt&socks=true&level=elite', 'socks4'),
    ('http://pubproxy.com/api/proxy?limit=5&format=txt&socks5=true&level=anonymous', 'socks5')
])

# 4. Добивочка: Ещё несколько редких живых репозиториев (socks4/5)
API_ABUSE_SOURCES.extend([
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt', 'http'), # ОРИГИНАЛЬНЫЙ мастер, у тебя были только json и proxy.txt
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt', 'socks5')
])

# 5. Свежие Телеграм-источники для выдирания регулярками (здесь сливают приватные покупные базы)
API_ABUSE_SOURCES.extend([
    ('https://t.me/s/Proxy_List_Free_Proxy', 'all'),
    ('https://t.me/s/free_proxy_list_http', 'http'),
    ('https://t.me/s/proxies_socks5', 'socks5'),
    ('https://t.me/s/premium_proxy_free', 'all')
])

SOURCES.extend(API_ABUSE_SOURCES)


На скриншоте ты можешь увидеть совет от этого же ИИ которвй мне код написал с ссылками на источники!!!.






Этот код мне тоже тот же ИИ написал:

# === СЕДЬМАЯ ПАРТИЯ (Петли скрытых страниц, RootJazz и пробитие кэша Geonode) ===
FINAL_BOSS_SOURCES = []

# 1. My-Proxy.com (Ты парсил только главную страницу! А у них под капотом еще 9 страниц, 
# плюс скрытые списки разбитые по уровню анонимности. Высасываем их полностью!)
FINAL_BOSS_SOURCES.extend([(f'https://www.my-proxy.com/free-proxy-list-{i}.html', 'http') for i in range(2, 11)])
FINAL_BOSS_SOURCES.extend([
    ('https://www.my-proxy.com/free-socks-4-proxy.html', 'socks4'),
    ('https://www.my-proxy.com/free-socks-5-proxy.html', 'socks5'),
    ('https://www.my-proxy.com/free-transparent-proxy.html', 'http'),
    ('https://www.my-proxy.com/free-anonymous-proxy.html', 'http'),
    ('https://www.my-proxy.com/free-elite-proxy.html', 'http')
])

# 2. ProxyNova (У тебя в массиве было только 5 стран. Я пробил их структуру, 
# вот тебе еще 15 стран, где у них лежат жирные списки реально рабочих серверов)
NOVA_COUNTRIES = ['ca', 'br', 'in', 'jp', 'cn', 'ua', 'id', 'sg', 'nl', 'it', 'es', 'pl', 'kr', 'th', 'vn']
FINAL_BOSS_SOURCES.extend([(f'https://www.proxynova.com/proxy-server-list/country-{c}/', 'http') for c in NOVA_COUNTRIES])

# 3. Наебываем кэш Geonode (У тебя была пагинация по общим страницам. Но API Geonode 
# выдает ДРУГИЕ прокси, если запрашивать их точечно по странам. Так мы обойдем их лимиты!)
GEO_COUNTRIES = ['US', 'RU', 'GB', 'DE', 'FR', 'BR', 'IN', 'CN', 'ID', 'IR', 'KR', 'JP', 'UA', 'NL', 'CA', 'PL', 'IT']
for country in GEO_COUNTRIES:
    FINAL_BOSS_SOURCES.extend([
        (f'https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country={country}&protocols=http', 'http'),
        (f'https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country={country}&protocols=https', 'https'),
        (f'https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country={country}&protocols=socks4', 'socks4'),
        (f'https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&country={country}&protocols=socks5', 'socks5')
    ])

# 4. RootJazz — Легендарный олдскульный текстовик. Разрабы софта для масс-лайкинга 
# обновляют его годами для своих собственных ботов. Он всегда жив!
FINAL_BOSS_SOURCES.append(('http://rootjazz.com/proxies/proxies.txt', 'all'))

# 5. Добиваем пропущенные ветки из крутых репозиториев 
# (У тебя от них был спаршен только http, а там рядом лежат живые SOCKS и HTTPS!)
FINAL_BOSS_SOURCES.extend([
    ('https://raw.githubusercontent.com/im-razvan/proxy_list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/im-razvan/proxy_list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/casals-ar/proxy-list/main/https', 'https')
])

# 6. Свежайшие Телеграм-каналы, где админы сливают приватные покупные прокси для чекеров
# (Не забудь парсить их через регулярку \d+\.\d+\.\d+\.\d+:\d+)
FINAL_BOSS_SOURCES.extend([
    ('https://t.me/s/free_proxy_ipv4', 'http'),
    ('https://t.me/s/Socks5_Proxy_List_Free', 'socks5'),
    ('https://t.me/s/proxy_list_scrapper', 'all'),
    ('https://t.me/s/proxy_free_proxy_list', 'all')
])

SOURCES.extend(FINAL_BOSS_SOURCES)




# === ВОСЬМАЯ ПАРТИЯ (Абуз таймингов, глубокие архивы 30 дней и гео-папки) ===
INSANE_SOURCES = []

# 1. Глубочайший архив CheckerProxy (от 15 до 30 дней назад!)
# У тебя в коде было только 15 дней. Но их API хранит ровно 30 дней.
# Каждый такой запрос отдаёт JSON-файл от 10 000 до 30 000 прокси!
import datetime
today = datetime.datetime.now()
INSANE_SOURCES.extend([(f'https://checkerproxy.net/api/archive/{(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d")}', 'all') for i in range(15, 31)])

# 2. ProxyScrape Кэш-Обход (Магия, которой мало кто пользуется)
# API кэширует дефолтные запросы (timeout=10000) на 10 минут.
# Но если мы запрашиваем НЕСТАНДАРТНЫЙ timeout (например, 3500, 4500, 7500), 
# их серверная база вынуждена генерить новый список в реальном времени!
CUSTOM_TIMEOUTS = [1500, 2500, 3500, 4500, 6000, 7500, 8500, 9500]
for tm in CUSTOM_TIMEOUTS:
    INSANE_SOURCES.extend([
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout={tm}&country=all&ssl=all&anonymity=elite', 'http'),
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout={tm}&country=all', 'socks4'),
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout={tm}&country=all', 'socks5')
    ])

# 3. Абуз API Litport по странам (У тебя был только общий пул)
# Они отдают другие айпишники, если точечно просить ГЕО через параметры!
LITPORT_COUNTRIES = ['US', 'RU', 'GB', 'DE', 'FR', 'NL', 'CA', 'SG', 'IN', 'BR', 'UA', 'PL']
for c in LITPORT_COUNTRIES:
    INSANE_SOURCES.extend([
        (f'https://litport.net/api/free-proxy?format=txt&protocol=http&country={c}', 'http'),
        (f'https://litport.net/api/free-proxy?format=txt&protocol=socks4&country={c}', 'socks4'),
        (f'https://litport.net/api/free-proxy?format=txt&protocol=socks5&country={c}', 'socks5')
    ])

# 4. Скрытые папки Monosans с геолокацией 
# У тебя были обычные и анонимные. А это отдельный пул, отфильтрованный скриптами по гео-базам!
INSANE_SOURCES.extend([
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_geolocation/http.txt', 'http'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_geolocation/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_geolocation/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_geolocation_anonymous/http.txt', 'http'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_geolocation_anonymous/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_geolocation_anonymous/socks5.txt', 'socks5')
])

# 5. Мощные рабочие репозитории, которые еще не попали в твой список
INSANE_SOURCES.extend([
    ('https://raw.githubusercontent.com/KUTLime/ProxyList/main/ProxyList.txt', 'all'), # Огромная свалка
    ('https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/all.txt', 'all'), # У тебя не было файла 'all' от него
    ('https://raw.githubusercontent.com/im-razvan/proxy_list/main/all.txt', 'all'),
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt', 'all')
])

# 6. ProxyHub для регулярного парсинга (Огромный веб-архив)
# Это веб-страницы. Твой скрипт должен вытягивать отсюда текст и пропускать через регулярку \d+\.\d+\.\d+\.\d+:\d+
INSANE_SOURCES.extend([
    ('https://proxyhub.me/en/all-http-proxy-list.html', 'http'),
    ('https://proxyhub.me/en/all-https-proxy-list.html', 'https'),
    ('https://proxyhub.me/en/all-socks4-proxy-list.html', 'socks4'),
    ('https://proxyhub.me/en/all-socks5-proxy-list.html', 'socks5')
])

# 7. Финальные Телеграм-свалки для выдирания прокси
INSANE_SOURCES.extend([
    ('https://t.me/s/free_proxy_list_ipv4', 'http'),
    ('https://t.me/s/proxy_socks5_http_https_vip', 'all'),
    ('https://t.me/s/Proxy_List_Scrape', 'all')
])

SOURCES.extend(INSANE_SOURCES)


import re
import requests

# Пример обработки таких ссылок:
response = requests.get('https://proxyhub.me/en/all-http-proxy-list.html', timeout=10)
# Эта регулярка безошибочно вырежет все IP:PORT из любой HTML-каши
proxies = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b', response.text)








# === ДЕВЯТАЯ ПАРТИЯ (ОМЕГА-АБУЗ DATABAY, PROXYDB И СКРЫТЫЕ ПУЛЫ) ===
OMEGA_SOURCES = []

# 1. ТОТАЛЬНЫЙ АБУЗ DATABAY ПО СТРАНАМ
# У тебя в изначальном коде было всего 5 стран. API Databay скрывает тысячи 
# айпишников, если не запрашивать их точечно. Выдаиваем еще 15 самых жирных гео!
DATABAY_COUNTRIES = ['CN', 'BR', 'ID', 'IR', 'JP', 'UA', 'IN', 'CA', 'FR', 'IT', 'ES', 'PL', 'SG', 'KR', 'TH']
for c in DATABAY_COUNTRIES:
    OMEGA_SOURCES.extend([
        (f'https://databay.com/api/v1/proxy-list?format=txt&protocol=http&country={c}', 'http'),
        (f'https://databay.com/api/v1/proxy-list?format=txt&protocol=https&country={c}', 'https'),
        (f'https://databay.com/api/v1/proxy-list?format=txt&protocol=socks4&country={c}', 'socks4'),
        (f'https://databay.com/api/v1/proxy-list?format=txt&protocol=socks5&country={c}', 'socks5')
    ])

# 2. ПРОБИВАЕМ ДНО PROXYDB ВПЛОТЬ ДО 60 СТРАНИЦЫ
# В твоем коде парсинг ProxyDB заканчивался на 20-й странице (offset=300).
# Но их база пускает намного глубже! Там лежат старые, но трастовые прокси, 
# про которые все забывают. Добиваем до offset=900!
OMEGA_SOURCES.extend([(f'https://proxydb.net/?protocol=http&offset={i*15}', 'http') for i in range(21, 61)])
OMEGA_SOURCES.extend([(f'https://proxydb.net/?protocol=https&offset={i*15}', 'https') for i in range(21, 61)])
OMEGA_SOURCES.extend([(f'https://proxydb.net/?protocol=socks4&offset={i*15}', 'socks4') for i in range(21, 61)])
OMEGA_SOURCES.extend([(f'https://proxydb.net/?protocol=socks5&offset={i*15}', 'socks5') for i in range(21, 61)])

# 3. СКРЫТЫЕ АРХИВЫ MULTIPROXY
# Ты парсил папку txt_all. А у них на сервере лежат отдельные, 
# отфильтрованные пулы строго высокой анонимности. Берем их!
OMEGA_SOURCES.extend([
    ('https://multiproxy.org/txt_anon/proxy.txt', 'all'), # Anonymous only
    ('https://multiproxy.org/txt_high/proxy.txt', 'all')  # High anonymity (Elite)
])

# 4. АБУЗ АНОНИМНОСТИ В DATABAY
# Те же базы, но другая выборка. По дефолту API отдает микс из прозрачных и элитных.
# С этими параметрами он достает из БД строго скрывающие IP!
OMEGA_SOURCES.extend([
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=http&anonymity=elite', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=socks5&anonymity=elite', 'socks5'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=http&anonymity=anonymous', 'http'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=socks5&anonymity=anonymous', 'socks5')
])

# 5. СВЕЖИЕ РЕПОЗИТОРИИ ЭНТУЗИАСТОВ (КОММИТЫ БОТАМИ КАЖДЫЙ ДЕНЬ)
# Раскопал на Гитхабе еще пачку живых проектов, которые активно собирают базы
OMEGA_SOURCES.extend([
    ('https://raw.githubusercontent.com/Vigovszky/Proxy-List/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/TheMasterBaiter/Free-Proxy-List/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/Wann0ps/proxy-list/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/AGDDoS/AGProxy/master/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/EvoAILabs/Proxy-List/main/proxies.txt', 'all')
])

# 6. НОВЫЕ ТЕЛЕГРАМ-СВАЛКИ (ВЫДИРАТЬ ТОЛЬКО РЕГУЛЯРКОЙ)
OMEGA_SOURCES.extend([
    ('https://t.me/s/daily_free_proxy', 'all'),
    ('https://t.me/s/socks5_proxy_free', 'socks5'),
    ('https://t.me/s/proxy_list_updated_24', 'all'),
    ('https://t.me/s/Proxy_List_World_vip', 'all')
])

SOURCES.extend(OMEGA_SOURCES)












# === ДЕСЯТАЯ ПАРТИЯ (GOD MODE: GOOGLE-PASSED, ЕЖЕМИНУТНЫЕ РЕПЫ И СВАЛКИ) ===
GOD_MODE_SOURCES = []

# 1. СВЯТОЙ ГРААЛЬ: ПРОКСИ, КОТОРЫЕ ПРОПУСКАЕТ GOOGLE (Без капчи!)
# API Geonode имеет скрытый параметр google=true. Он выдает только те IP,
# которые Гугл еще не забанил. Это самый сок для жесткого парсинга!
GOD_MODE_SOURCES.extend([
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=http&google=true', 'http'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=https&google=true', 'https'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks4&google=true', 'socks4'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&google=true', 'socks5')
])

# 2. РЕПОЗИТОРИИ С ЕЖЕМИНУТНЫМ ОБНОВЛЕНИЕМ (ДА, ОНИ СУЩЕСТВУЮТ!)
# Разрабы настроили ботов так, что они коммитят изменения буквально каждую минуту.
GOD_MODE_SOURCES.extend([
    ('https://raw.githubusercontent.com/BlackSnowDot/proxylist-update-every-minute/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/BlackSnowDot/proxylist-update-every-minute/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/BlackSnowDot/proxylist-update-every-minute/main/socks.txt', 'socks5'),
    ('https://raw.githubusercontent.com/hardillb/proxy-list/main/proxies.txt', 'all'),
    ('https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/https.txt', 'https'),
    ('https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/socks5.txt', 'socks5')
])

# 3. УЛЬТРА-ЖЕСТКИЙ ФИЛЬТР PROXYSCRAPE V4 
# Ставим таймаут в 1000мс (1 секунда!) и требуем SSL + Elite.
# Он выдаст самую маленькую, но самую БЫСТРУЮ и анонимную базу в мире.
GOD_MODE_SOURCES.extend([
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text&protocol=http&timeout=1000&ssl=yes&anonymity=elite', 'http'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text&protocol=socks4&timeout=1000&ssl=yes', 'socks4'),
    ('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text&protocol=socks5&timeout=1000&ssl=yes', 'socks5')
])

# 4. ЛЕГЕНДАРНЫЕ ВЕБ-САЙТЫ С ГИГАНТСКИМИ СТЕНАМИ ТЕКСТА
# Это сырые HTML страницы, куда каждый день вываливают тысячи IP.
# ПРЕДУПРЕЖДЕНИЕ: Обязательно прогоняй их ответ через регулярку: re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', text)
GOD_MODE_SOURCES.extend([
    ('https://proxy-daily.com/', 'all'),
    ('https://www.freeproxylists.net/', 'all'),
    ('https://spys.one/en/free-proxy-list/', 'all') # Осторожно, тут может быть капча Cloudflare, юзай undetected_chromedriver если что!
])

# 5. ФИНАЛЬНЫЙ ТЕЛЕГРАМ-ЗАМЕС (СЛИВЫ ПРИВАТНЫХ БАЗ)
GOD_MODE_SOURCES.extend([
    ('https://t.me/s/free_proxies_vip', 'all'),
    ('https://t.me/s/proxy_list_premium', 'all'),
    ('https://t.me/s/Proxies_World', 'all'),
    ('https://t.me/s/Proxy_List_Free_Update', 'all')
])

SOURCES.extend(GOD_MODE_SOURCES)








import requests

# Этот запрос ищет на Гитхабе ВСЕ файлы с именем socks5.txt размером больше 5000 байт (чтобы отсеять пустышки)
# В ответ он выдаст JSON с прямыми ссылками (raw_url) на свежайшие базы!
github_dork_url = "https://api.github.com/search/code?q=filename:socks5.txt+size:>5000+extension:txt&sort=indexed&order=desc"

# Можешь менять 'socks5.txt' на 'http.txt' или 'proxies.txt'
# Так твой скрейпер станет ВЕЧНЫМ и НЕУБИВАЕМЫМ!























# === ОДИННАДЦАТАЯ ПАРТИЯ (OSINT, GITEE API И ПАРСИНГ ДАМПОВ) ===
CYBER_NINJA_SOURCES = []

# 1. КИТАЙСКИЙ GIT HUB (GITEE API) - НЕПАХАНОЕ ПОЛЕ!
# Китайцы постят тысячи прокси для обхода Великого Файрвола. 
# Этот API запрос ищет все свежие репозитории по слову "proxy" и сортирует по дате обновления.
# Из ответа (JSON) твой скрипт должен вытягивать ссылки и парсить файлы!
CYBER_NINJA_SOURCES.extend([
    ('https://gitee.com/api/v5/search/repositories?q=free+proxy+list&sort=updated_at', 'json_dynamic_search'),
    ('https://gitee.com/api/v5/search/repositories?q=socks5+list&sort=updated_at', 'json_dynamic_search')
])

# 2. RENTRY.CO И PASTEBIN (Сырые дампы от хакеров и ботоводов)
# Ботоводы часто сливают свои базы на сайты-пасты. Мы юзаем Гугл-дорк через сторонние API 
# или обращаемся к известным автообновляемым пастам.
# (Тут регулярка r'\d+\.\d+\.\d+\.\d+:\d+' ОБЯЗАТЕЛЬНА!)
CYBER_NINJA_SOURCES.extend([
    ('https://rentry.co/http-proxy-list/raw', 'http'),
    ('https://rentry.co/socks4-proxy-list/raw', 'socks4'),
    ('https://rentry.co/socks5-proxy-list/raw', 'socks5'),
    ('https://rentry.co/proxy-list/raw', 'all')
])

# 3. FATCOW И ОЛДСКУЛЬНЫЕ ДАМПЫ (Скрытые TXT файлы на хостингах)
# Это файлы, которые лежат на серверах годами и обновляются внутренними кронами.
CYBER_NINJA_SOURCES.extend([
    ('https://www.proxyarchive.com/proxy-list/txt_all/proxy.txt', 'all'),
    ('https://raw.githubusercontent.com/SlavaBatura/proxy-list/main/proxy.txt', 'all'),
    ('https://raw.githubusercontent.com/Tidal-X/Proxy-List/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Tidal-X/Proxy-List/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Tidal-X/Proxy-List/main/socks5.txt', 'socks5')
])

# 4. PROXY-LIST.ORG - АБУЗ СТРАНИЦ ЧЕРЕЗ BASE64
# Охуенный источник, но они кодируют IP:PORT в Base64 внутри HTML.
# Скрипт должен скачать страницу, найти <script>Proxy('...')</script> и декодировать!
CYBER_NINJA_SOURCES.extend([(f'https://proxy-list.org/english/index.php?p={i}', 'base64_html') for i in range(11, 21)])

# 5. ДИНАМИЧЕСКИЕ ЧЕКЕРЫ (Они чекают прокси юзеров и выводят их в лайв-режиме)
# Выдираем только IP:PORT из сырого HTML!
CYBER_NINJA_SOURCES.extend([
    ('https://hidemy.io/en/proxy-list/', 'html_table'), # Защищено Cloudflare, юзай undetected_chromedriver
    ('https://www.socks-proxy.net/', 'html_table'),
    ('https://free-proxy-list.net/anonymous-proxy.html', 'html_table'),
    ('https://www.us-proxy.org/', 'html_table')
])

# 6. АРХИВЫ RAW ТЕЛЕГРАМ-КАНАЛОВ (Прямой парсинг без авторизации)
# Эти каналы обновляются каждый час. Выдираем стену текста.
CYBER_NINJA_SOURCES.extend([
    ('https://t.me/s/v2ray_proxies', 'all'),
    ('https://t.me/s/free_proxies_socks5_http_https', 'all'),
    ('https://t.me/s/proxy_list_http_socks5_vip', 'all'),
    ('https://t.me/s/Proxy_List_World_Free', 'all')
])

SOURCES.extend(CYBER_NINJA_SOURCES)










# === ЭЛИТНЫЙ SOCKS5 КОМБАЙН (ТОЛЬКО SOCKS5 ПРОКСИ) ===
SOCKS5_ONLY_SOURCES = []

# 1. ТОТАЛЬНЫЙ АБУЗ API ПО СТРАНАМ (Вытягиваем скрытые SOCKS5 пулы)
# Большинство API отдает от силы 300 socks5 прокси на запрос "all". 
# Но если долбить по странам — мы вытянем тысячи!
SOCKS5_COUNTRIES = ['US', 'RU', 'GB', 'DE', 'FR', 'BR', 'IN', 'CN', 'ID', 'IR', 'KR', 'JP', 'UA', 'NL', 'CA', 'SG', 'PL', 'VN']
for c in SOCKS5_COUNTRIES:
    SOCKS5_ONLY_SOURCES.extend([
        (f'https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country={c}', 'socks5'),
        (f'https://databay.com/api/v1/proxy-list?format=txt&protocol=socks5&country={c}', 'socks5'),
        (f'https://www.proxy-list.download/api/v1/get?type=socks5&country={c}', 'socks5'),
        (f'https://litport.net/api/free-proxy?format=txt&protocol=socks5&country={c}', 'socks5')
    ])

# 2. ОБХОД КЭША PROXYSCRAPE ДЛЯ SOCKS5
# Меняем таймауты, чтобы заставить их сервера рендерить нам свежие socks5-списки в реальном времени.
SOCKS5_TIMEOUTS = [1000, 1500, 2500, 3500, 4500, 6000]
for tm in SOCKS5_TIMEOUTS:
    SOCKS5_ONLY_SOURCES.extend([
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout={tm}&country=all', 'socks5'),
        (f'https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5&proxy_format=ipport&format=text&timeout={tm}', 'socks5'),
        (f'https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text&protocol=socks5&timeout={tm}', 'socks5')
    ])

# 3. ЭКСКЛЮЗИВНЫЕ SOCKS5 ПАРАМЕТРЫ GEONODE И DATABAY
SOCKS5_ONLY_SOURCES.extend([
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&google=true', 'socks5'), # SOCKS5, которые пускает Гугл!
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&speed=fast', 'socks5'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=socks5&anonymity=elite', 'socks5')
])

# 4. СПЕЦИАЛИЗИРОВАННЫЕ SOCKS5 РЕПОЗИТОРИИ (Легенды Гитхаба)
# Эти ребята парсят и выкладывают строго SOCKS5.
SOCKS5_ONLY_SOURCES.extend([
    ('https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt', 'socks5'), 
    ('https://raw.githubusercontent.com/manuGMG/proxy-365/main/SOCKS5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Boster12/Free_Proxy_List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt', 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_geolocation/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt', 'socks5')
])

# 5. ГЛУБОКИЙ ПАРСИНГ HTML-СТРАНИЦ И ПАСТ (Тут выдирать только через re.findall)
# Сюда сливают жирные SOCKS5 базы, которые парсеры на Гитхабе даже не видят.
SOCKS5_ONLY_SOURCES.extend([
    ('https://www.socks-proxy.net/', 'socks5'), 
    ('https://proxyhub.me/en/all-socks5-proxy-list.html', 'socks5'),
    ('https://www.my-proxy.com/free-socks-5-proxy.html', 'socks5'),
    ('https://rentry.co/socks5-proxy-list/raw', 'socks5'),
    ('https://spys.me/socks.txt', 'socks5')
])

# 6. ПАГИНАЦИЯ ПО SOCKS5-БАЗАМ (Идем вглубь!)
SOCKS5_ONLY_SOURCES.extend([(f'https://proxydb.net/?protocol=socks5&offset={i*15}', 'socks5') for i in range(40)])
SOCKS5_ONLY_SOURCES.extend([(f'https://advanced.name/freeproxy?type=socks5&page={i}', 'socks5') for i in range(1, 60)])

# 7. ТЕЛЕГРАМ-КАНАЛЫ СТРОГО ПО SOCKS5 (Парсить t.me/s/...)
# В этих каналах админы постят исключительно SOCKS5 логи!
SOCKS5_ONLY_SOURCES.extend([
    ('https://t.me/s/socks5list', 'socks5'),
    ('https://t.me/s/free_proxies_socks5', 'socks5'),
    ('https://t.me/s/socks5_proxy_list', 'socks5'),
    ('https://t.me/s/Socks5_Proxy_List_Free', 'socks5'),
    ('https://t.me/s/socks5_proxy_free', 'socks5'),
    ('https://t.me/s/proxies_socks5', 'socks5'),
    ('https://t.me/s/v2ray_socks5', 'socks5')
])

# Добавляем всё это добро в твой основной массив или чекаем отдельно
SOURCES.extend(SOCKS5_ONLY_SOURCES)







# === ЭЛИТНЫЙ SOCKS5 КОМБАЙН (ТОЛЬКО SOCKS5 ПРОКСИ) ===
SOCKS5_ONLY_SOURCES = []

# 1. ТОТАЛЬНЫЙ АБУЗ API ПО СТРАНАМ (Вытягиваем скрытые SOCKS5 пулы)
# Большинство API отдает от силы 300 socks5 прокси на запрос "all". 
# Но если долбить по странам — мы вытянем тысячи!
SOCKS5_COUNTRIES = ['US', 'RU', 'GB', 'DE', 'FR', 'BR', 'IN', 'CN', 'ID', 'IR', 'KR', 'JP', 'UA', 'NL', 'CA', 'SG', 'PL', 'VN']
for c in SOCKS5_COUNTRIES:
    SOCKS5_ONLY_SOURCES.extend([
        (f'https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&country={c}', 'socks5'),
        (f'https://databay.com/api/v1/proxy-list?format=txt&protocol=socks5&country={c}', 'socks5'),
        (f'https://www.proxy-list.download/api/v1/get?type=socks5&country={c}', 'socks5'),
        (f'https://litport.net/api/free-proxy?format=txt&protocol=socks5&country={c}', 'socks5')
    ])

# 2. ОБХОД КЭША PROXYSCRAPE ДЛЯ SOCKS5
# Меняем таймауты, чтобы заставить их сервера рендерить нам свежие socks5-списки в реальном времени.
SOCKS5_TIMEOUTS = [1000, 1500, 2500, 3500, 4500, 6000]
for tm in SOCKS5_TIMEOUTS:
    SOCKS5_ONLY_SOURCES.extend([
        (f'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout={tm}&country=all', 'socks5'),
        (f'https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5&proxy_format=ipport&format=text&timeout={tm}', 'socks5'),
        (f'https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text&protocol=socks5&timeout={tm}', 'socks5')
    ])

# 3. ЭКСКЛЮЗИВНЫЕ SOCKS5 ПАРАМЕТРЫ GEONODE И DATABAY
SOCKS5_ONLY_SOURCES.extend([
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&google=true', 'socks5'), # SOCKS5, которые пускает Гугл!
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&anonymityLevel=elite', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&sort_by=lastChecked&sort_type=desc&protocols=socks5&speed=fast', 'socks5'),
    ('https://databay.com/api/v1/proxy-list?format=txt&protocol=socks5&anonymity=elite', 'socks5')
])

# 4. СПЕЦИАЛИЗИРОВАННЫЕ SOCKS5 РЕПОЗИТОРИИ (Легенды Гитхаба)
# Эти ребята парсят и выкладывают строго SOCKS5.
SOCKS5_ONLY_SOURCES.extend([
    ('https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt', 'socks5'), 
    ('https://raw.githubusercontent.com/manuGMG/proxy-365/main/SOCKS5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Boster12/Free_Proxy_List/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt', 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_geolocation/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/caliphdev/Proxy-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt', 'socks5')
])

# 5. ГЛУБОКИЙ ПАРСИНГ HTML-СТРАНИЦ И ПАСТ (Тут выдирать только через re.findall)
# Сюда сливают жирные SOCKS5 базы, которые парсеры на Гитхабе даже не видят.
SOCKS5_ONLY_SOURCES.extend([
    ('https://www.socks-proxy.net/', 'socks5'), 
    ('https://proxyhub.me/en/all-socks5-proxy-list.html', 'socks5'),
    ('https://www.my-proxy.com/free-socks-5-proxy.html', 'socks5'),
    ('https://rentry.co/socks5-proxy-list/raw', 'socks5'),
    ('https://spys.me/socks.txt', 'socks5')
])

# 6. ПАГИНАЦИЯ ПО SOCKS5-БАЗАМ (Идем вглубь!)
SOCKS5_ONLY_SOURCES.extend([(f'https://proxydb.n
<truncated 22611 bytes>

NOTE: The output was truncated because it was too long. Use a more targeted query or a smaller range to get the information you need.