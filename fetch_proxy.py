import re
import socket
import threading
import time
import requests
import argparse
import sys
import os
import csv
import dns.resolver
import dns.reversename
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from typing import List, Set, Tuple, Optional, Dict

try:
    import maxminddb
except ImportError:
    pass

# ═══════════════════════════════════════════════════════════════
#  РАСШИРЕННЫЙ СПИСОК ИСТОЧНИКОВ (Объединенный)
# ═══════════════════════════════════════════════════════════════
SOURCES = [
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
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json', 'http'),
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
    ('https://www.socks-proxy.net/', 'socks5'),
    ('https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/iplocate/free-proxy-list/main/all-proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt', 'http'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/Firmfox/Proxify/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/Firmfox/Proxify/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt', 'http'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt', 'socks5'),
    ('https://proxyroller.com/api/proxies?protocol=http&anonymity=elite&limit=100', 'http'),
    ('https://raw.githubusercontent.com/xing2kong/ProxyScraper2/main/http.txt', 'http'),
    ('https://raw.githubusercontent.com/xing2kong/ProxyScraper2/main/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/xing2kong/ProxyScraper2/main/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.json', 'socks4'),
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt', 'http'),
    ('https://raw.githubusercontent.com/26info/vless-proxy-list/main/working-proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/master/https.txt', 'http'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5&proxy_format=protocolonly&format=text&timeout=20000', 'socks5'),
    ('https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/master/http.txt', 'http'),
    ('https://codeberg.org/dbarker/public-proxy-list/raw/branch/main/proxies.txt', 'http'),
    ('https://docs.google.com/spreadsheets/d/1guW73RgKLUcLUFGx9QRtqtAmbqMJG7aXKJGlT_XU2t4/export?format=csv', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt', 'socks4'),
    ('https://raw.githubusercontent.com/duckray-client/free-vless-keys/main/keys.txt', 'http'),
    ('https://raw.githubusercontent.com/mmpx12/proxy-list/master/proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/master/HTTPS.txt', 'http'),
    ('https://raw.githubusercontent.com/theriturajps/proxy-list/main/proxies.txt', 'http'),
    ('https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/http.txt', 'http'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/master/socks5.txt', 'socks5'),
    ('https://proxylist.to/proxy-list.txt', 'http'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.json', 'socks5'),
    ('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt', 'http'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt', 'http'),
    ('https://spys.me/proxy.txt', 'http'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json', 'http'),
    ('https://raw.githubusercontent.com/zloi-user/hideip.me/master/socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/vAHiD55555/ProxyScraper/main/proxies.txt', 'http'),
    ('https://pastebin.com/raw/XJsxHu4D', 'http'),
    ('https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_eu.txt', 'http'),
    ('https://bitbucket.org/vanholt-proxies/public-http-proxies/raw/main/README.md', 'http'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks4&proxy_format=protocolonly&format=text&timeout=20000', 'socks4'),
    ('https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/json/proxies.json', 'http'),
    ('https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_all.txt', 'http'),
    ('https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_ru.txt', 'http'),
    ('https://telegra.ph/Free-Proxy-List-for-Scraping-and-SEO-Updated-Daily-04-07', 'http'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt', 'http'),
    ('https://raw.githubusercontent.com/theriturajps/proxy-list/main/proxies.json', 'http'),
    ('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=protocolonly&format=text&timeout=20000', 'http'),
    ('https://raw.githubusercontent.com/hookzof/socks5_list/master/tg/mtproto.json', 'socks5')
]

class ProxyUtils:
    """Утилиты для работы с сетью и парсинга прокси"""
    
    PROXY_RE  = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3}):(\d{1,5})\b')
    JSON_IP_FIRST = re.compile(r'(?:"ip"|"host"|"proxy")\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"[^}]*?(?:"port")\s*:\s*"?(\d{1,5})"?', re.IGNORECASE)
    JSON_PORT_FIRST = re.compile(r'(?:"port")\s*:\s*"?(\d{1,5})"?[^}]*?(?:"ip"|"host"|"proxy")\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"', re.IGNORECASE)
    TABLE_RE  = re.compile(r'<td[^>]*>\s*(\d{1,3}(?:\.\d{1,3}){3})\s*</td>\s*<td[^>]*>\s*(\d{1,5})\s*</td>', re.IGNORECASE | re.DOTALL)

    @staticmethod
    def is_valid(ip: str, port: int) -> bool:
        parts = ip.split('.')
        return (len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
                and 1 <= port <= 65535 and ip not in ('0.0.0.0', '127.0.0.1', '255.255.255.255'))

    @classmethod
    def parse_proxies(cls, content: str) -> List[str]:
        found = set()
        for ip, port in cls.JSON_IP_FIRST.findall(content):
            if cls.is_valid(ip, int(port)): found.add(f"{ip}:{port}")
        for port, ip in cls.JSON_PORT_FIRST.findall(content):
            if cls.is_valid(ip, int(port)): found.add(f"{ip}:{port}")
        for ip, port in cls.TABLE_RE.findall(content):
            if cls.is_valid(ip.strip(), int(port)): found.add(f"{ip.strip()}:{port}")
        for ip, port in cls.PROXY_RE.findall(content):
            if cls.is_valid(ip, int(port)): found.add(f"{ip}:{port}")
        return list(found)

    @staticmethod
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
        except Exception: 
            return ''

    @staticmethod
    def tcp_ping(ip: str, port: int, timeout: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                return sock.connect_ex((ip, port)) == 0
        except Exception: 
            return False

    @staticmethod
    def http_check(ip: str, port: int, proto: str, timeout: int) -> bool:
        proxy_url = f"{proto}://{ip}:{port}"
        proxies = {'http': proxy_url, 'https': proxy_url}
        for url in ['http://httpbin.org/ip', 'http://ifconfig.me/ip']:
            try:
                resp = requests.get(url, proxies=proxies, timeout=timeout)
                if resp.status_code == 200: return True
            except Exception: 
                continue
        return False

    @classmethod
    def check_proxy(cls, ip: str, port: int, protos: Set[str], timeout: int) -> Set[str]:
        if not cls.tcp_ping(ip, port, timeout): return set()
        working_protos = set()
        for proto in sorted(protos):
            if cls.http_check(ip, port, proto, timeout):
                working_protos.add(proto)
                break
        return working_protos


class ProxyHunter:
    """Главный класс сборщика и валидатора прокси"""
    
    def __init__(self, threads: int = 300, timeout: int = 3, countries: Optional[List[str]] = None, 
                 max_ping: float = 700.0, min_speed: float = 1.0,
                 check_smtp: bool = True, residential_only: bool = False,
                 pause_event: threading.Event = None, cancel_event: threading.Event = None):
        
        self.threads = min(threads, 500)
        self.timeout = timeout
        
        default_countries = ['US','CA','GB','AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE',
                             'GR','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE']
        self.countries = set(c.upper() for c in (countries or default_countries))
        
        self.max_ping = max_ping
        self.min_speed = min_speed
        self.check_smtp = check_smtp
        self.residential_only = residential_only

        self.proxy_protocols: Dict[str, Set[str]] = defaultdict(set)
        self.live_results: List[str] = []
        self.good_results: List[str] = []
        self._lock = threading.Lock()
        
        self.ip_cache: Dict[str, dict] = {}

        # Управление паузой и отменой
        self._pause_event = pause_event    # threading.Event — set = пауза
        self._cancel_event = cancel_event  # threading.Event — set = отмена

    def _check_pause_cancel(self) -> bool:
        """Проверяет состояние паузы/отмены. Возвращает True если отменено."""
        if self._cancel_event and self._cancel_event.is_set():
            return True
        if self._pause_event and self._pause_event.is_set():
            while self._pause_event.is_set():
                if self._cancel_event and self._cancel_event.is_set():
                    return True
                time.sleep(0.2)
        return False

    def collect(self):
        print(f"\n[+] ШАГ 1: Сбор из {len(SOURCES)} источников...")
        total_raw, ok_sources = 0, 0
        try:
            from tqdm import tqdm
            pbar = tqdm(total=len(SOURCES), desc="Загрузка")
        except ImportError:
            pbar = None

        with ThreadPoolExecutor(max_workers=min(len(SOURCES), 30)) as ex:
            fmap = {ex.submit(ProxyUtils.fetch_url, url, 12): (url, proto) for url, proto in SOURCES}
            for fut in as_completed(fmap):
                url, proto = fmap[fut]
                content = fut.result()
                if content:
                    ok_sources += 1
                    proxies = ProxyUtils.parse_proxies(content)
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

        def worker(item: Tuple[str, Set[str]]) -> Optional[Tuple[str, Set[str]]]:
            if stop.is_set(): return None
            if self._check_pause_cancel():
                stop.set()
                return None
            ip_port, protos = item
            ip, port_s = ip_port.split(':')
            working = ProxyUtils.check_proxy(ip, int(port_s), protos, self.timeout)
            if working: return (ip_port, working)
            return None

        try:
            from tqdm import tqdm
            pbar = tqdm(total=total, desc="Проверка")
        except ImportError: 
            pbar = None

        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            futs = [ex.submit(worker, item) for item in candidates]
            for fut in as_completed(futs):
                res = fut.result()
                if res:
                    ip_port, working_protos = res
                    with self._lock:
                        for p in sorted(working_protos): 
                            self.live_results.append(f"{p}://{ip_port}")
                            ip, port = ip_port.split(':')
                            import json
                            print(f"    [REALTIME_NEW_LIVE] {json.dumps({'ip': ip, 'port': port, 'protocol': p, 'country': 'Unknown'})}")
                        if len(self.live_results) % 5 == 0 or len(self.live_results) < 10:
                            print(f"    [REALTIME_LIVE] {len(self.live_results)}")
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

    def _batch_ip_info(self, ips: Set[str]):
        """Пакетный запрос в ip-api.com для кэширования гео/ISP"""
        chunks = [list(ips)[i:i+100] for i in range(0, len(ips), 100)]
        for chunk in chunks:
            try:
                resp = requests.post("http://ip-api.com/batch?fields=query,isp,org,hosting,mobile,countryCode", json=chunk, timeout=10)
                if resp.status_code == 200:
                    for data in resp.json():
                        self.ip_cache[data['query']] = {
                            'country': data.get('countryCode', ''),
                            'datacenter': data.get('hosting', False),
                            'isp': data.get('isp', '').lower()
                        }
            except Exception:
                pass
            time.sleep(4)

    def _check_rdns_and_bl(self, ip: str) -> dict:
        """Кэшируемая проверка RDNS и DNSBL"""
        if ip in self.ip_cache and 'dnsbl' in self.ip_cache[ip]:
            return self.ip_cache[ip]

        fast_resolver = dns.resolver.Resolver()
        fast_resolver.timeout = 1.0
        fast_resolver.lifetime = 1.0

        rdns = ""
        try:
            rev_name = dns.reversename.from_address(ip)
            rdns = str(fast_resolver.resolve(rev_name, 'PTR')[0]).lower()
        except Exception: 
            pass

        dirty_rdns = any(x in rdns for x in ['amazonaws', 'googleusercontent', 'digitalocean', 'hetzner', 'ovh', 'linode'])

        rev_ip = '.'.join(reversed(ip.split('.')))
        bls = ['zen.spamhaus.org', 'b.barracudacentral.org', 'bl.spamcop.net', 'dnsbl.sorbs.net']
        is_bl = False
        for bl in bls:
            try:
                fast_resolver.resolve(f'{rev_ip}.{bl}', 'A')
                is_bl = True
                break
            except Exception: 
                pass

        bad_ports = [22, 23, 3389, 3128]
        has_bad_port = False
        for port in bad_ports:
            if ProxyUtils.tcp_ping(ip, port, timeout=1):
                has_bad_port = True
                break

        if ip not in self.ip_cache: self.ip_cache[ip] = {}
        self.ip_cache[ip].update({'rdns_dirty': dirty_rdns, 'dnsbl': is_bl, 'bad_ports': has_bad_port})
        return self.ip_cache[ip]

    def _run_single_filter(self, item: str) -> Optional[str]:
        """Логика расширенной проверки одного прокси"""
        if self._check_pause_cancel():
            return None

        proto, ipp = item.split('://')
        ip, port_s = ipp.split(':')
        port = int(port_s)

        ip_info = self.ip_cache.get(ip, {})
        if self.residential_only and ip_info.get('datacenter', True):
            return None

        net_info = self._check_rdns_and_bl(ip)
        if net_info.get('rdns_dirty') or net_info.get('dnsbl') or net_info.get('bad_ports'):
            return None

        proxy_url = f"{proto}://{ip}:{port}"
        proxies = {'http': proxy_url, 'https': proxy_url}

        try:
            resp = requests.get('http://httpbin.org/headers', proxies=proxies, timeout=self.timeout)
            if resp.status_code == 200:
                headers = str(resp.json().get('headers', {})).lower()
                if 'x-forwarded-for' in headers or 'via' in headers or 'proxy-connection' in headers:
                    return None
        except Exception: 
            return None

        start = time.time()
        try:
            resp = requests.get('https://speed.cloudflare.com/__down?bytes=100000', proxies=proxies, timeout=self.timeout)
            elapsed = (time.time() - start)
            ping_ms = elapsed * 1000
            speed_mbps = (100000 * 8) / elapsed / 1000000
            if ping_ms > self.max_ping or speed_mbps < self.min_speed:
                return None
        except Exception: 
            return None

        if self.check_smtp:
            smtp_ok = False
            try:
                if requests.get('http://portquiz.net:25', proxies=proxies, timeout=self.timeout).status_code == 200: 
                    smtp_ok = True
            except Exception: pass
            
            if not smtp_ok:
                try:
                    if requests.get('http://portquiz.net:587', proxies=proxies, timeout=self.timeout).status_code == 200: 
                        smtp_ok = True
                except Exception: pass
            if not smtp_ok: return None

        return item

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

        filtered_by_geo = []
        for item in self.live_results:
            ip = item.split('://')[1].split(':')[0]
            country = ''
            if db_reader:
                try:
                    geo_info = db_reader.get(ip)
                    if geo_info and 'country' in geo_info:
                        country = geo_info['country']['iso_code']
                except Exception: pass
            
            if self.countries and country.upper() not in self.countries:
                continue
            
            if ip not in self.ip_cache: self.ip_cache[ip] = {}
            self.ip_cache[ip]['country'] = country
            filtered_by_geo.append(item)
            
        if db_reader:
            db_reader.close()

        self.live_results = filtered_by_geo
        print(f"    После проверки ГЕО (локально за микросекунды) осталось: {len(filtered_by_geo)}")
        print(f"    [REALTIME_LIVE] {len(filtered_by_geo)}")
        
        if self.residential_only and filtered_by_geo:
            residential_ips = set([r.split('://')[1].split(':')[0] for r in filtered_by_geo])
            print(f"    Запрашиваю тип прокси (Residential) для {len(residential_ips)} IP через ip-api...")
            self._batch_ip_info(residential_ips)
        elif not self.residential_only:
            print("    Флаг --residential-only не установлен. Пропускаем долгий опрос ip-api.com!")

        try:
            from tqdm import tqdm
            pbar = tqdm(total=len(self.live_results), desc="Фильтрация")
        except ImportError: 
            pbar = None

        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            futs = [ex.submit(self._run_single_filter, item) for item in self.live_results]
            for fut in as_completed(futs):
                res = fut.result()
                if res:
                    with self._lock: 
                        self.good_results.append(res)
                        proto, ipp = res.split('://')
                        ip, port = ipp.split(':')
                        country = self.ip_cache.get(ip, {}).get('country', 'Unknown')
                        import json
                        print(f"    [REALTIME_NEW_ELITE] {json.dumps({'ip': ip, 'port': port, 'protocol': proto, 'country': country})}")
                        if len(self.good_results) % 2 == 0 or len(self.good_results) < 5:
                            print(f"    [REALTIME_ELITE] {len(self.good_results)}")
                if pbar: pbar.update(1)

        if pbar: pbar.close()
        self.good_results = sorted(set(self.good_results))
        print(f"    Годных, прошедших все фильтры: {len(self.good_results)}")

    def _save_category(self, folder_name: str, results_list: List[str], description: str):
        os.makedirs(folder_name, exist_ok=True)
        
        by_proto = defaultdict(list)
        for p in results_list:
            proto, ipp = p.split('://')
            by_proto[proto.lower()].append(p)
            
        with open(os.path.join(folder_name, 'all.txt'), 'w', encoding='utf-8') as f:
            f.write(f"# {description}: {len(results_list)}\n")
            for p in results_list: f.write(p + '\n')
            
        with open(os.path.join(folder_name, 'all.csv'), 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Протокол', 'IP', 'Port', 'Страна'])
            for p in results_list:
                proto, ipp = p.split('://')
                ip, port = ipp.split(':')
                country = self.ip_cache.get(ip, {}).get('country', 'Unknown') or 'Unknown'
                writer.writerow([proto.upper(), ip, port, country])
                
        unique_ips = sorted(set(p.split('://')[1].split(':')[0] for p in results_list))
        with open(os.path.join(folder_name, 'all_ips.txt'), 'w', encoding='utf-8') as f:
            f.write(f"# {description} (Только уникальные IP): {len(unique_ips)}\n")
            for ip in unique_ips: f.write(ip + '\n')
                
        for proto, items in by_proto.items():
            with open(os.path.join(folder_name, f'{proto}.txt'), 'w', encoding='utf-8') as f:
                f.write(f"# {description} ({proto.upper()}): {len(items)}\n")
                for p in items: f.write(p + '\n')
                
            with open(os.path.join(folder_name, f'{proto}.csv'), 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Протокол', 'IP', 'Port', 'Страна'])
                for p in items:
                    _, ipp = p.split('://')
                    ip, port = ipp.split(':')
                    country = self.ip_cache.get(ip, {}).get('country', 'Unknown') or 'Unknown'
                    writer.writerow([proto.upper(), ip, port, country])
                    
            proto_ips = sorted(set(p.split('://')[1].split(':')[0] for p in items))
            with open(os.path.join(folder_name, f'{proto}_ips.txt'), 'w', encoding='utf-8') as f:
                f.write(f"# {description} ({proto.upper()} - Только уникальные IP): {len(proto_ips)}\n")
                for ip in proto_ips: f.write(ip + '\n')

    def save(self):
        if self.live_results:
            self._save_category('results_live', self.live_results, 'Живые прокси')
            print("[✓] Базовые списки по категориям сохранены в папку 'results_live/'")
            
        if hasattr(self, 'good_results') and self.good_results:
            self._save_category('results_elite', self.good_results, 'Элитные прокси (Elite/NoDNSBL/Fast)')
            print("[✓] Элитные списки по категориям сохранены в папку 'results_elite/'")

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
    parser.add_argument('--threads', type=int, default=300, help='Количество потоков')
    parser.add_argument('--timeout', type=int, default=5, help='Таймаут соединения в секундах')
    parser.add_argument('--countries', default='US,CA,GB,AT,BE,BG,HR,CY,CZ,DK,EE,FI,FR,DE,GR,HU,IE,IT,LV,LT,LU,MT,NL,PL,PT,RO,SK,SI,ES,SE', type=str, help='Разрешенные страны через запятую')
    parser.add_argument('--max-ping', type=float, default=700, help='Макс пинг в мс')
    parser.add_argument('--min-speed', type=float, default=1.0, help='Мин скорость Мбит/с')
    parser.add_argument('--check-smtp', choices=['True', 'False'], default='True', help='Включить проверку SMTP портов (True/False)')
    parser.add_argument('--residential-only', action='store_true', help='Только residential/мобильные IP')
    
    args = parser.parse_args()
    check_smtp_bool = args.check_smtp == 'True'
    countries_list = [c.strip().upper() for c in args.countries.split(',')] if args.countries else None

    try:
        import tqdm
        import dns.resolver
    except ImportError:
        print("❌ Установите зависимости: pip install tqdm requests dnspython")
        sys.exit(1)

    hunter = ProxyHunter(
        threads=args.threads, 
        timeout=args.timeout,
        countries=countries_list, 
        max_ping=args.max_ping,
        min_speed=args.min_speed, 
        check_smtp=check_smtp_bool,
        residential_only=args.residential_only
    )
    hunter.run()

if __name__ == '__main__':
    main()
