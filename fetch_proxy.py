import re
import socket
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import argparse
import sys
import os
import dns.resolver
import dns.reversename
import csv
try:
    import maxminddb
except ImportError:
    pass

# ═══════════════════════════════════════════════════════════════
#  РАСШИРЕННЫЙ СПИСОК ИСТОЧНИКОВ (Объединенный)
# ═══════════════════════════════════════════════════════════════
SOURCES = [
    # ── ИЗ СТАРОГО СПИСКА (РАБОЧИЕ API И САЙТЫ) ───────────────
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all', 'http'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all', 'socks4'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all', 'socks5'),
    ('https://api.openproxylist.xyz/http.txt', 'http'),
    ('https://api.openproxylist.xyz/socks4.txt', 'socks4'),
    ('https://api.openproxylist.xyz/socks5.txt', 'socks5'),
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc', 'http'),
    ('https://free-proxy-list.net/', 'http'),
    ('https://www.sslproxies.org/', 'http'),
    ('https://www.us-proxy.org/', 'http'),

    # ── НОВЫЕ И ЛУЧШИЕ RAW GITHUB-БОТЫ (Из Анализа) ───────────
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt', 'http'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt', 'http'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt', 'socks4'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt', 'socks5'),
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/socks5.txt', 'socks5'),
    
    # ── ДОБАВЛЕННЫЕ ИЗ CHECK_LINKS.TXT ───────────
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt', 'socks5'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/all.txt', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/all.json', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/http.txt', 'http'),
    ('https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/https.txt', 'http'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/socks5.txt', 'socks5'),
    
    # ── НОВЫЕ ИСТОЧНИКИ ОТ DEEPSEEK (Проверено на динамичность) ──
    ('https://www.socks-proxy.net/', 'socks5'),
    ('https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/iplocate/free-proxy-list/main/all-proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt', 'socks5'),
    
    # ── НОВЫЕ ИСТОЧНИКИ ОТ DEEPSEEK (Партия 2 - Проверено на динамичность) ──
    ('https://raw.githubusercontent.com/Firmfox/Proxify/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Firmfox/Proxify/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt', 'http'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/noctiro/getproxy/main/file/http.txt', 'http'),
    ('https://raw.githubusercontent.com/noctiro/getproxy/main/file/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/noctiro/getproxy/main/file/socks5.txt', 'socks5'),
    ('https://proxyroller.com/api/proxies?protocol=http&anonymity=elite&limit=100', 'http'),
]

PROXY_RE  = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3}):(\d{1,5})\b')
JSON_IP_FIRST = re.compile(r'(?:"ip"|"host"|"proxy")\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"[^}]*?(?:"port")\s*:\s*"?(\d{1,5})"?', re.IGNORECASE)
JSON_PORT_FIRST = re.compile(r'(?:"port")\s*:\s*"?(\d{1,5})"?[^}]*?(?:"ip"|"host"|"proxy")\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"', re.IGNORECASE)
TABLE_RE  = re.compile(r'<td[^>]*>\s*(\d{1,3}(?:\.\d{1,3}){3})\s*</td>\s*<td[^>]*>\s*(\d{1,5})\s*</td>', re.IGNORECASE | re.DOTALL)

def is_valid(ip: str, port: int) -> bool:
    parts = ip.split('.')
    return (len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
            and 1 <= port <= 65535 and ip not in ('0.0.0.0', '127.0.0.1', '255.255.255.255'))

def parse_proxies(content: str) -> list:
    found = set()
    for ip, port in JSON_IP_FIRST.findall(content):
        if is_valid(ip, int(port)): found.add(f"{ip}:{port}")
    for port, ip in JSON_PORT_FIRST.findall(content):
        if is_valid(ip, int(port)): found.add(f"{ip}:{port}")
    for ip, port in TABLE_RE.findall(content):
        if is_valid(ip.strip(), int(port)): found.add(f"{ip.strip()}:{port}")
    for ip, port in PROXY_RE.findall(content):
        if is_valid(ip, int(port)): found.add(f"{ip}:{port}")



    return list(found)

def fetch_url(url: str, timeout: int = 10) -> str:
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
        resp.raise_for_status()
        chunks, size = [], 0
        for chunk in resp.iter_content(chunk_size=8192):
            chunks.append(chunk.decode('utf-8', errors='ignore'))
            size += len(chunk)
            if size > 512 * 1024: break
        return ''.join(chunks)
    except: return ''

def tcp_ping(ip: str, port: int, timeout: int) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        res = sock.connect_ex((ip, port))
        sock.close()
        return res == 0
    except: return False

def http_check(ip: str, port: int, proto: str, timeout: int) -> bool:
    proxy_url = f"{proto}://{ip}:{port}"
    proxies   = {'http': proxy_url, 'https': proxy_url}
    for url in ['http://httpbin.org/ip', 'http://ifconfig.me/ip']:
        try:
            resp = requests.get(url, proxies=proxies, timeout=timeout)
            if resp.status_code == 200: return True
        except: continue
    return False

def check_proxy(ip: str, port: int, protos: set, timeout: int) -> set:
    if not tcp_ping(ip, port, timeout // 2 or 1): return set()
    working_protos = set()
    for proto in sorted(protos):
        if http_check(ip, port, proto, timeout):
            working_protos.add(proto)
            break
    return working_protos

class ProxyHunter:
    def __init__(self, threads=300, timeout=3, max_live=0, output='live_proxies.txt',
                 output_good='good.txt', countries=None, max_ping=700, min_speed=1.0,
                 check_smtp=True, residential_only=False):
        self.threads = min(threads, 500)
        self.timeout = timeout
        self.max_live = max_live
        self.output = output
        self.output_good = output_good

        self.countries = set(c.upper() for c in (countries or ['US','CA','GB','AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE']))
        self.max_ping = max_ping
        self.min_speed = min_speed
        self.check_smtp = check_smtp
        self.residential_only = residential_only

        self.proxy_protocols = defaultdict(set)
        self.live_results = []
        self.good_results = []
        self._lock = threading.Lock()
        
        self.ip_cache = {} # Кэш для IP: geo, type, dnsbl, rdns

    def collect(self):
        print(f"\n[+] ШАГ 1: Сбор из {len(SOURCES)} источников...")
        total_raw, ok_sources = 0, 0
        try:
            from tqdm import tqdm
            pbar = tqdm(total=len(SOURCES), desc="Загрузка")
        except:
            pbar = None

        with ThreadPoolExecutor(max_workers=min(len(SOURCES), 30)) as ex:
            fmap = {ex.submit(fetch_url, url, 12): (url, proto) for url, proto in SOURCES}
            for fut in as_completed(fmap):
                url, proto = fmap[fut]
                content = fut.result()
                if content:
                    ok_sources += 1
                    proxies = parse_proxies(content)
                    total_raw += len(proxies)
                    with self._lock:
                        for p in proxies:
                            self.proxy_protocols[p].add(proto)
                if pbar: pbar.update(1)
        
        if pbar: pbar.close()
        print(f"    Ответило источников: {ok_sources}/{len(SOURCES)}")
        print(f"    Собрано (Уникальных IP:PORT): {len(self.proxy_protocols)}")

    def validate(self):
        if not self.proxy_protocols: return
        candidates = list(self.proxy_protocols.items())
        total = len(candidates)
        stop = threading.Event()
        print(f"\n[+] ШАГ 2: Базовая проверка {total} прокси на живость...")

        def worker(item):
            if stop.is_set(): return None
            ip_port, protos = item
            ip, port_s = ip_port.split(':')
            working = check_proxy(ip, int(port_s), protos, self.timeout)
            if working: return (ip_port, working)
            return None

        try:
            from tqdm import tqdm
            pbar = tqdm(total=total, desc="Проверка")
        except: pbar = None

        checked = 0
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            futs = [ex.submit(worker, item) for item in candidates]
            for fut in as_completed(futs):
                res = fut.result()
                checked += 1
                if res:
                    ip_port, working_protos = res
                    with self._lock:
                        for p in sorted(working_protos): self.live_results.append(f"{p}://{ip_port}")
                if pbar: pbar.update(1)

        if pbar: pbar.close()
        self.live_results = sorted(set(self.live_results))
        print(f"    Живых прокси: {len(self.live_results)}")

    def _download_mmdb_if_needed(self):
        db_path = 'GeoLite2-Country.mmdb'
        if not os.path.exists(db_path):
            print(f"\n[!] Локальная база {db_path} не найдена. Скачиваю (около 5MB)...")
            url = 'https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb'
            try:
                r = requests.get(url, stream=True, timeout=30)
                r.raise_for_status()
                with open(db_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("[✓] Локальная база успешно скачана!")
            except Exception as e:
                print(f"[x] Ошибка скачивания базы: {e}")

    def _batch_ip_info(self, ips):
        """Пакетный запрос в ip-api.com для кэширования гео/ISP"""
        chunks = [list(ips)[i:i+100] for i in range(0, len(ips), 100)]
        for chunk in chunks:
            try:
                # rate limit ip-api bulk is 15 req/min
                resp = requests.post("http://ip-api.com/batch?fields=query,isp,org,hosting,mobile,countryCode", json=chunk, timeout=10)
                if resp.status_code == 200:
                    for data in resp.json():
                        self.ip_cache[data['query']] = {
                            'country': data.get('countryCode', ''),
                            'datacenter': data.get('hosting', False),
                            'isp': data.get('isp', '').lower()
                        }
            except Exception as e:
                pass
            time.sleep(4)

    def _check_rdns_and_bl(self, ip):
        """Кэшируемая проверка RDNS и DNSBL"""
        if ip in self.ip_cache and 'dnsbl' in self.ip_cache[ip]:
            return self.ip_cache[ip]

        fast_resolver = dns.resolver.Resolver()
        fast_resolver.timeout = 1.0
        fast_resolver.lifetime = 1.0

        # 1. Reverse DNS (С быстрым таймаутом вместо долгого socket)
        rdns = ""
        try:
            rev_name = dns.reversename.from_address(ip)
            rdns = str(fast_resolver.resolve(rev_name, 'PTR')[0]).lower()
        except: pass

        dirty_rdns = any(x in rdns for x in ['amazonaws', 'googleusercontent', 'digitalocean', 'hetzner', 'ovh', 'linode'])

        # 2. DNSBL Check (Оптимизировано: только 4 самых важных базы вместо 25!)
        rev_ip = '.'.join(reversed(ip.split('.')))
        bls = ['zen.spamhaus.org', 'b.barracudacentral.org', 'bl.spamcop.net', 'dnsbl.sorbs.net']
        is_bl = False
        for bl in bls:
            try:
                fast_resolver.resolve(f'{rev_ip}.{bl}', 'A')
                is_bl = True
                break
            except: pass

        # 3. Open Ports Check
        bad_ports = [22, 23, 3389, 3128] # 8080 skipped as many legit proxies run on it
        has_bad_port = False
        for port in bad_ports:
            if tcp_ping(ip, port, timeout=1):
                has_bad_port = True
                break

        if ip not in self.ip_cache: self.ip_cache[ip] = {}
        self.ip_cache[ip].update({'rdns_dirty': dirty_rdns, 'dnsbl': is_bl, 'bad_ports': has_bad_port})
        return self.ip_cache[ip]

    def advanced_filter(self):
        if not self.live_results: return
        print(f"\n[+] ШАГ 3: Расширенная фильтрация {len(self.live_results)} прокси...")
        
        self._download_mmdb_if_needed()
        db_reader = None
        try:
            if os.path.exists('GeoLite2-Country.mmdb'):
                db_reader = maxminddb.open_database('GeoLite2-Country.mmdb')
        except Exception as e:
            print(f"Ошибка загрузки локальной базы: {e}")

        # 1. Быстрая локальная фильтрация по ГЕО
        filtered_by_geo = []
        for item in self.live_results:
            ip = item.split('://')[1].split(':')[0]
            country = ''
            if db_reader:
                try:
                    geo_info = db_reader.get(ip)
                    if geo_info and 'country' in geo_info:
                        country = geo_info['country']['iso_code']
                except: pass
            
            if self.countries and country.upper() not in self.countries:
                continue
            
            if ip not in self.ip_cache: self.ip_cache[ip] = {}
            self.ip_cache[ip]['country'] = country
            filtered_by_geo.append(item)
            
        if db_reader:
            db_reader.close()

        # Обновляем основной список, чтобы в live_proxies.txt попадали ТОЛЬКО нужные страны!
        self.live_results = filtered_by_geo

        print(f"    После проверки ГЕО (локально за микросекунды) осталось: {len(filtered_by_geo)}")
        
        # 2. Проверка Residential (только если нужно и только для прошедших ГЕО)
        if self.residential_only and filtered_by_geo:
            residential_ips = set([r.split('://')[1].split(':')[0] for r in filtered_by_geo])
            print(f"    Запрашиваю тип прокси (Residential) для {len(residential_ips)} IP через ip-api...")
            self._batch_ip_info(residential_ips)
        elif not self.residential_only:
            print("    Флаг --residential-only не установлен. Пропускаем долгий опрос ip-api.com!")

        def run_filters(item):
            proto, ipp = item.split('://')
            ip, port = ipp.split(':')
            port = int(port)

            ip_info = self.ip_cache.get(ip, {})
            # ГЕО уже проверено выше.
            if self.residential_only and ip_info.get('datacenter', True):
                return None

            # 2. RDNS, DNSBL, Открытые порты
            net_info = self._check_rdns_and_bl(ip)
            if net_info.get('rdns_dirty') or net_info.get('dnsbl') or net_info.get('bad_ports'):
                return None

            proxy_url = f"{proto}://{ip}:{port}"
            proxies = {'http': proxy_url, 'https': proxy_url}

            # 3. Анонимность (Elite)
            try:
                resp = requests.get('http://httpbin.org/headers', proxies=proxies, timeout=self.timeout)
                if resp.status_code == 200:
                    headers = str(resp.json().get('headers', {})).lower()
                    if 'x-forwarded-for' in headers or 'via' in headers or 'proxy-connection' in headers:
                        return None # Не анонимный
            except: return None

            # 4. Скорость и Пинг
            start = time.time()
            try:
                # Скачиваем 100KB для проверки скорости
                resp = requests.get('https://speed.cloudflare.com/__down?bytes=100000', proxies=proxies, timeout=self.timeout)
                elapsed = (time.time() - start)
                ping_ms = elapsed * 1000
                speed_mbps = (100000 * 8) / elapsed / 1000000
                if ping_ms > self.max_ping or speed_mbps < self.min_speed:
                    return None
            except: return None

            # 5. SMTP порты (25, 587)
            if self.check_smtp:
                smtp_ok = False
                try:
                    r25 = requests.get('http://portquiz.net:25', proxies=proxies, timeout=self.timeout)
                    if r25.status_code == 200: smtp_ok = True
                except: pass
                if not smtp_ok:
                    try:
                        r587 = requests.get('http://portquiz.net:587', proxies=proxies, timeout=self.timeout)
                        if r587.status_code == 200: smtp_ok = True
                    except: pass
                if not smtp_ok: return None

            return item

        try:
            from tqdm import tqdm
            pbar = tqdm(total=len(self.live_results), desc="Фильтрация")
        except: pbar = None

        with ThreadPoolExecutor(max_workers=min(self.threads, 100)) as ex:
            futs = [ex.submit(run_filters, item) for item in self.live_results]
            for fut in as_completed(futs):
                res = fut.result()
                if res:
                    with self._lock: self.good_results.append(res)
                if pbar: pbar.update(1)

        if pbar: pbar.close()
        self.good_results = sorted(set(self.good_results))
        print(f"    Годных, прошедших все фильтры: {len(self.good_results)}")

    def save(self):
        # 1. Сохраняем просто "живые"
        if self.live_results:
            with open(self.output, 'w', encoding='utf-8') as f:
                f.write(f"# Живых строк: {len(self.live_results)}\n")
                for p in self.live_results: f.write(p + '\n')
            print(f"[✓] Базовый список сохранен в {self.output}")
            
            # Сохранение базового списка в CSV
            csv_output = self.output.replace('.txt', '.csv') if '.txt' in self.output else self.output + '.csv'
            with open(csv_output, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Протокол', 'IP', 'Port', 'Страна'])
                for p in self.live_results:
                    proto, ipp = p.split('://')
                    ip, port = ipp.split(':')
                    country = self.ip_cache.get(ip, {}).get('country', '')
                    if not country: country = 'Unknown'
                    writer.writerow([proto.upper(), ip, port, country])
            print(f"[✓] Базовый CSV сохранен в {csv_output}")

        # 2. Сохраняем "расширенно отфильтрованные"
        if hasattr(self, 'good_results') and self.good_results:
            with open(self.output_good, 'w', encoding='utf-8') as f:
                f.write(f"# Годных строк (Elite/NoDNSBL/Residential/Fast): {len(self.good_results)}\n")
                for p in self.good_results: f.write(p + '\n')
            print(f"[✓] ЭЛИТНЫЙ список сохранен в {self.output_good}")
            
            # Сохранение элитного списка в CSV
            csv_good = self.output_good.replace('.txt', '.csv') if '.txt' in self.output_good else self.output_good + '.csv'
            with open(csv_good, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Протокол', 'IP', 'Port', 'Страна'])
                for p in self.good_results:
                    proto, ipp = p.split('://')
                    ip, port = ipp.split(':')
                    country = self.ip_cache.get(ip, {}).get('country', '')
                    if not country: country = 'Unknown'
                    writer.writerow([proto.upper(), ip, port, country])
            print(f"[✓] ЭЛИТНЫЙ CSV сохранен в {csv_good}")

    def run(self):
        t0 = time.time()
        print("\n🚀 ULTIMATE PROXY HUNTER v4.0 (ADVANCED FILTERS)")
        self.collect()
        self.validate()
        self.advanced_filter()
        self.save()
        m, s = divmod(int(time.time() - t0), 60)
        print(f"\n⏱   Общее время работы: {m}м {s}с")

def main():
    parser = argparse.ArgumentParser(description='Proxy Hunter v4.0 - Advanced Filtration')
    parser.add_argument('--threads', type=int, default=300)
    parser.add_argument('--timeout', type=int, default=5)
    parser.add_argument('--max', type=int, default=0)
    parser.add_argument('--output', default='live_proxies.txt')
    # Новые аргументы:
    parser.add_argument('--output-good', default='good.txt', help='Файл для чистого элитного списка')
    parser.add_argument('--countries', default='US,CA,GB,AT,BE,BG,HR,CY,CZ,DK,EE,FI,FR,DE,GR,HU,IE,IT,LV,LT,LU,MT,NL,PL,PT,RO,SK,SI,ES,SE', type=str, help='Разрешенные страны через запятую')
    parser.add_argument('--max-ping', type=float, default=700, help='Макс пинг в мс')
    parser.add_argument('--min-speed', type=float, default=1.0, help='Мин скорость Мбит/с')
    parser.add_argument('--check-smtp', choices=['True', 'False'], default='True', help='Включить проверку SMTP портов (True/False)')
    parser.add_argument('--residential-only', action='store_true', help='Только residential/мобильные IP')
    
    args = parser.parse_args()

    # Парсим булево значение для SMTP
    check_smtp_bool = args.check_smtp == 'True'

    # Парсим страны
    countries_list = [c.strip().upper() for c in args.countries.split(',')]

    try:
        import tqdm
        import dns.resolver
    except ImportError:
        print("❌ Установите зависимости: pip install tqdm requests dnspython")
        sys.exit(1)

    hunter = ProxyHunter(
        threads=args.threads, timeout=args.timeout, max_live=args.max,
        output=args.output, output_good=args.output_good,
        countries=countries_list, max_ping=args.max_ping,
        min_speed=args.min_speed, check_smtp=check_smtp_bool,
        residential_only=args.residential_only
    )
    hunter.run()

if __name__ == '__main__':
    main()
