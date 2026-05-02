'''

import re
import socket
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from tqdm import tqdm
import argparse
import sys

# ═══════════════════════════════════════════════════════════════
#  38 ЖИВЫХ ИСТОЧНИКОВ (мёртвые репозитории удалены)
#  Формат: (url, protocol)
#  Обновляемость: ✅ каждые 15мин-сутки (боты + API)
# ═══════════════════════════════════════════════════════════════
SOURCES = [
    # ── HTTP — только живые GitHub-боты ───────────────────────
    # TheSpeedX: бот, каждый час (~40k адресов)
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',                   'http'),

    # monosans: GitHub Actions, каждые 30 мин (~20k)
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',              'http'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt',    'http'),

    # jetkai: ежедневный бот (~15k)
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt', 'http'),

    # roosterkid: ежедневно (~8k)
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP_RAW.txt',             'http'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',            'http'),

    # ShiftyTR: ежедневно (~5k)
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',                    'http'),

    # clarketm: несколько раз в неделю
    ('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',          'http'),

    # almroot: раз в несколько дней (небольшой, но живой)
    ('https://raw.githubusercontent.com/almroot/proxylist/master/list.txt',                      'http'),

    # dinoz0rg: чекнутые вручную, обновляется периодически
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/http.txt',      'http'),

    # ── SOCKS4 — живые GitHub-боты ────────────────────────────
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',                 'socks4'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt',                 'socks4'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',            'socks4'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt', 'socks4'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt',           'socks4'),
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt',                  'socks4'),

    # ── SOCKS5 — живые GitHub-боты ────────────────────────────
    ('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',                 'socks5'),
    ('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt',                 'socks5'),
    ('https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',            'socks5'),
    ('https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt', 'socks5'),
    ('https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt',           'socks5'),
    ('https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt',                  'socks5'),
    # hookzof: обновляется каждые 3 часа ботом (~5k SOCKS5)
    ('https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',                   'socks5'),
    ('https://raw.githubusercontent.com/dinoz0rg/proxy-list/main/checked_proxies/socks5.txt',    'socks5'),

    # ── API — самые свежие, обновляются автоматически ─────────
    # proxyscrape: каждые 15 минут (~30k суммарно)
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all',   'http'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all', 'socks4'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all', 'socks5'),
    ('https://api.proxyscrape.com/v2/?request=getproxies&protocol=all&timeout=10000&country=all',    'http'),

    # proxyscan: каждый час (~10k)
    ('https://www.proxyscan.io/api/proxy?limit=5000&format=txt&type=http',                       'http'),
    ('https://www.proxyscan.io/api/proxy?limit=5000&format=txt&type=socks5',                     'socks5'),
    ('https://www.proxyscan.io/download?type=http',                                               'http'),
    ('https://www.proxyscan.io/download?type=socks4',                                             'socks4'),
    ('https://www.proxyscan.io/download?type=socks5',                                             'socks5'),

    # proxy-list.download: каждый час
    ('https://www.proxy-list.download/api/v1/get?type=http',                                     'http'),
    ('https://www.proxy-list.download/api/v1/get?type=socks4',                                   'socks4'),
    ('https://www.proxy-list.download/api/v1/get?type=socks5',                                   'socks5'),

    # openproxylist: каждые 6 часов
    ('https://api.openproxylist.xyz/http.txt',                                                    'http'),
    ('https://api.openproxylist.xyz/socks4.txt',                                                  'socks4'),
    ('https://api.openproxylist.xyz/socks5.txt',                                                  'socks5'),

    # geonode JSON API: живой, обновляется регулярно
    ('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc', 'http'),

    # ── HTML-сайты — живые, скрапим таблицы ───────────────────
    ('https://free-proxy-list.net/',                                                              'http'),
    ('https://www.sslproxies.org/',                                                               'http'),
    ('https://www.us-proxy.org/',                                                                 'http'),
    ('https://spys.one/en/free-proxy-list/',                                                      'http'),
    ('https://hidemy.name/en/proxy-list/',                                                        'http'),
]

# ═══════════════════════════════════════════════════════════════
#  Регулярки для разных форматов контента
# ═══════════════════════════════════════════════════════════════
PROXY_RE  = re.compile(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})\b')
JSON_RE   = re.compile(r'"ip"\s*:\s*"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"[^}]*"port"\s*:\s*"?(\d{1,5})"?')
TABLE_RE  = re.compile(
    r'<td[^>]*>\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*</td>\s*<td[^>]*>\s*(\d{1,5})\s*</td>',
    re.IGNORECASE | re.DOTALL
)


def is_valid(ip: str, port: int) -> bool:
    """Валидация: IP корректный, порт в диапазоне, не loopback/broadcast"""
    parts = ip.split('.')
    return (
        len(parts) == 4
        and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
        and 1 <= port <= 65535
        and ip not in ('0.0.0.0', '127.0.0.1', '255.255.255.255')
    )


def parse_proxies(content: str) -> list:
    """
    Парсит контент источника, возвращает список строк "IP:PORT".
    Поддерживает TXT, HTML-таблицы, JSON (geonode API).
    """
    found = set()

    # JSON формат (geonode и подобные API)
    for ip, port in JSON_RE.findall(content):
        if is_valid(ip, int(port)):
            found.add(f"{ip}:{port}")

    # HTML таблицы (free-proxy-list.net и т.п.)
    for ip, port in TABLE_RE.findall(content):
        ip = ip.strip()
        if is_valid(ip, int(port)):
            found.add(f"{ip}:{port}")

    # TXT / RAW формат — основной
    for ip, port in PROXY_RE.findall(content):
        if is_valid(ip, int(port)):
            found.add(f"{ip}:{port}")

    return list(found)


def fetch_url(url: str, timeout: int = 10) -> str:
    """Скачивает контент источника с лимитом 512 KB"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/plain,text/html,application/json,*/*;q=0.8',
        'Connection': 'close',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
        resp.raise_for_status()
        chunks, size = [], 0
        for chunk in resp.iter_content(chunk_size=8192):
            chunks.append(chunk.decode('utf-8', errors='ignore'))
            size += len(chunk)
            if size > 512 * 1024:
                break
        return ''.join(chunks)
    except Exception:
        return ''


# Тестовые URL для проверки реального HTTP-запроса через прокси
# Используем несколько — если один не отвечает, пробуем следующий
CHECK_URLS = [
    'http://httpbin.org/ip',          # Надёжный, возвращает JSON с IP
    'http://ip-api.com/json',         # Геолокация + IP
    'http://ifconfig.me/ip',          # Простой IP
]


def tcp_ping(ip: str, port: int, timeout: int) -> bool:
    """Шаг 1: TCP connect — быстро отсеивает закрытые порты (~90% мусора)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        res = sock.connect_ex((ip, port))
        sock.close()
        return res == 0
    except Exception:
        return False


def http_check(ip: str, port: int, proto: str, timeout: int) -> bool:
    """
    Шаг 2: Реальный HTTP-запрос ЧЕРЕЗ прокси.
    Это единственный способ убедиться, что прокси реально работает.
    Если запрос прошёл и вернул 200 — прокси живой и рабочий.
    """
    proxy_url = f"{proto}://{ip}:{port}"
    proxies   = {'http': proxy_url, 'https': proxy_url}
    headers   = {'User-Agent': 'Mozilla/5.0'}

    for url in CHECK_URLS:
        try:
            resp = requests.get(
                url,
                proxies=proxies,
                timeout=timeout,
                headers=headers,
                allow_redirects=True,
            )
            if resp.status_code == 200 and len(resp.content) > 3:
                return True
        except Exception:
            continue   # пробуем следующий check_url

    return False


def check_proxy(ip: str, port: int, protos: set, timeout: int) -> set:
    """
    Двухэтапная проверка:
      1. TCP ping  — быстро (0.01–0.1s), отсеивает закрытые порты
      2. HTTP req  — реальный запрос через прокси (timeout секунд)
    Возвращает set протоколов, по которым прокси реально работает.
    """
    # Шаг 1: проверяем — порт открыт?
    if not tcp_ping(ip, port, timeout // 2 or 1):
        return set()  # порт закрыт → не тратим время на HTTP

    # Шаг 2: реальный HTTP запрос через прокси
    working_protos = set()
    for proto in sorted(protos):           # http, socks4, socks5
        if http_check(ip, port, proto, timeout):
            working_protos.add(proto)
            break  # если хоть один протокол работает — хватит
            # (можно убрать break, чтобы проверять все протоколы)

    return working_protos


# ═══════════════════════════════════════════════════════════════
#  ГЛАВНЫЙ КЛАСС
# ═══════════════════════════════════════════════════════════════
class ProxyHunter:
    def __init__(self, threads: int = 300, timeout: int = 3,
                 max_live: int = 0, output: str = 'live_proxies.txt'):
        self.threads  = min(threads, 500)
        self.timeout  = timeout
        self.max_live = max_live  # 0 = без лимита
        self.output   = output

        # Ключ: "ip:port" → set протоколов {"http", "socks4", "socks5"}
        # Один и тот же адрес может быть и HTTP, и SOCKS5 одновременно!
        self.proxy_protocols: dict = defaultdict(set)

        self.live_results: list = []  # итог: ["http://1.2.3.4:80", ...]
        self._lock = threading.Lock()

    # ─── ШАГ 1: СБОР — все прокси в одну кучу ───────────────
    def collect(self):
        print(f"\n{'='*62}")
        print(f"  ШАГ 1: СБОР — {len(SOURCES)} источников")
        print(f"  Каждый источник помечен протоколом (HTTP/SOCKS4/SOCKS5)")
        print(f"{'='*62}")

        total_raw = 0
        ok_sources = 0

        with ThreadPoolExecutor(max_workers=min(len(SOURCES), 30)) as ex:
            # Запускаем скачивание всех источников параллельно
            fmap = {ex.submit(fetch_url, url, 12): (url, proto)
                    for url, proto in SOURCES}

            for fut in tqdm(as_completed(fmap), total=len(fmap),
                            desc="📥 Загружаем", unit="src"):
                url, proto = fmap[fut]
                content = fut.result()
                if not content:
                    continue

                ok_sources += 1
                proxies = parse_proxies(content)   # список "ip:port"
                total_raw += len(proxies)

                # Складываем всё в одну кучу, сохраняя протокол
                with self._lock:
                    for p in proxies:
                        self.proxy_protocols[p].add(proto)

        unique_count = len(self.proxy_protocols)
        duplicates   = total_raw - unique_count

        print(f"\n  Источников ответило:      {ok_sources}/{len(SOURCES)}")
        print(f"  Всего адресов собрано:    {total_raw:,}  (с дубликатами)")

        # ─── ШАГ 1.5: DEDUP через dict/set ──────────────────
        print(f"\n{'='*62}")
        print(f"  ШАГ 2: DEDUP — убираем дубликаты (set по IP:PORT)")
        print(f"{'='*62}")
        print(f"  Было (с дублями):         {total_raw:,}")
        print(f"  Дубликатов убрано:        {duplicates:,}")
        print(f"  УНИКАЛЬНЫХ адресов:       {unique_count:,}  ← будем проверять")

        # Статистика по протоколам
        http_cnt   = sum(1 for v in self.proxy_protocols.values() if 'http'   in v)
        socks4_cnt = sum(1 for v in self.proxy_protocols.values() if 'socks4' in v)
        socks5_cnt = sum(1 for v in self.proxy_protocols.values() if 'socks5' in v)
        multi_cnt  = sum(1 for v in self.proxy_protocols.values() if len(v) > 1)
        print(f"\n  Распределение протоколов:")
        print(f"    HTTP:   {http_cnt:,}")
        print(f"    SOCKS4: {socks4_cnt:,}")
        print(f"    SOCKS5: {socks5_cnt:,}")
        if multi_cnt:
            print(f"    Многопротокол (1 адрес в нескольких списках): {multi_cnt:,}")

        return unique_count

    # ─── ШАГ 3: ПРОВЕРКА ЖИВЫХ ───────────────────────────────
    def validate(self):
        if not self.proxy_protocols:
            print("❌ Нет прокси для проверки!")
            return

        candidates = list(self.proxy_protocols.items())  # [(ip:port, {protos})]
        total = len(candidates)
        stop  = threading.Event()

        print(f"\n{'='*62}")
        print(f"  ШАГ 3: ПРОВЕРКА {total:,} уникальных адресов")
        print(f"  Метод: TCP ping → реальный HTTP запрос через прокси")
        print(f"  Потоков: {self.threads} | Timeout: {self.timeout}s")
        print(f"  Цель: {'∞' if self.max_live == 0 else self.max_live} живых")
        print(f"  ⚠️  Этот шаг медленнее, но результат — только РЕАЛЬНО рабочие!")
        print(f"{'='*62}\n")

        def worker(ip_port_protos):
            if stop.is_set():
                return None
            ip_port, protos = ip_port_protos
            ip, port_s = ip_port.split(':')
            port = int(port_s)
            # Двухэтапная проверка: TCP ping + реальный HTTP через прокси
            working = check_proxy(ip, port, protos, self.timeout)
            if working:
                return (ip_port, working)
            return None

        checked = 0
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            futs = {ex.submit(worker, item): item for item in candidates}
            with tqdm(total=total, desc="🔍 Проверяем", unit="proxy") as bar:
                for fut in as_completed(futs):
                    res = fut.result()
                    checked += 1
                    if res is not None:
                        ip_port, working_protos = res
                        with self._lock:
                            for proto in sorted(working_protos):
                                self.live_results.append(f"{proto}://{ip_port}")
                            live_now = len(self.live_results)
                        bar.set_postfix(live=live_now)
                        if self.max_live > 0 and live_now >= self.max_live:
                            stop.set()
                    bar.update(1)

        self.live_results = sorted(set(self.live_results))

        live_addrs = len(set(r.split('://', 1)[1] for r in self.live_results))
        print(f"\n  Проверено адресов:     {checked:,}/{total:,}")
        print(f"  ✅ Реально рабочих:    {live_addrs:,}  (прошли HTTP-тест)")
        print(f"  Строк в файле:         {len(self.live_results):,}  (адрес × протоколы)")
        if total:
            print(f"  Выживаемость:          {live_addrs/total*100:.1f}%")

    # ─── ШАГ 4: СОХРАНЕНИЕ ───────────────────────────────────
    def save(self):
        if not self.live_results:
            print("❌ Живых прокси не найдено!")
            return

        # Группируем для красивого вывода: http + socks4 + socks5
        by_proto = defaultdict(list)
        for entry in self.live_results:
            proto = entry.split('://', 1)[0]
            by_proto[proto].append(entry)

        with open(self.output, 'w', encoding='utf-8') as f:
            f.write("# Ultimate Proxy Collector v3.1\n")
            f.write(f"# Формат: PROTOCOL://IP:PORT\n")
            f.write(f"# Живых строк: {len(self.live_results)}\n")
            f.write("# Пример использования:\n")
            f.write("#   curl --proxy socks5://1.2.3.4:1080 https://example.com\n")
            f.write("#   curl --proxy http://1.2.3.4:8080  https://example.com\n\n")

            for proto in ('http', 'socks4', 'socks5'):
                if proto in by_proto:
                    f.write(f"# ─── {proto.upper()} ({len(by_proto[proto])}) ───\n")
                    for entry in sorted(by_proto[proto]):
                        f.write(entry + '\n')
                    f.write('\n')

        print(f"\n{'='*62}")
        print(f"  💾 Файл: {self.output}")
        print(f"  Всего строк: {len(self.live_results)}")
        for proto in ('http', 'socks4', 'socks5'):
            if proto in by_proto:
                print(f"    {proto.upper():7}: {len(by_proto[proto]):,}")
        print(f"{'='*62}")
        print("  Готово для: curl | proxychains | Burp Suite | Nuclei")
        print(f"\n  Топ-10 живых:")
        for p in self.live_results[:10]:
            print(f"    {p}")

    # ─── Полный пайплайн ─────────────────────────────────────
    def run(self):
        t0 = time.time()
        print("\n🚀 ULTIMATE PROXY COLLECTOR v3.1")
        print(f"   Источников: {len(SOURCES)} | Потоков: {self.threads} | Timeout: {self.timeout}s")
        print(f"   Цель: {'∞' if self.max_live == 0 else self.max_live} живых")

        self.collect()    # Шаг 1+2: сбор + dedup
        self.validate()   # Шаг 3: socket check
        self.save()       # Шаг 4: сохранение

        m, s = divmod(int(time.time() - t0), 60)
        print(f"\n⏱️  Общее время: {m}м {s}с")


# ═══════════════════════════════════════════════════════════════
#  ТОЧКА ВХОДА
# ═══════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description='Ultimate Proxy Collector v3.1 — с протоколами',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--threads', type=int, default=300,
                        help='Потоков для проверки (max 500, default: 300)')
    parser.add_argument('--timeout', type=int, default=3,
                        help='Socket timeout в секундах (default: 3)')
    parser.add_argument('--max', type=int, default=0,
                        help='Макс. живых адресов (0 = без лимита)')
    parser.add_argument('--output', default='live_proxies.txt',
                        help='Файл вывода (default: live_proxies.txt)')
    args = parser.parse_args()

    try:
        import tqdm
    except ImportError:
        print("❌ Установите зависимости: pip install tqdm requests")
        sys.exit(1)

    ProxyHunter(
        threads=args.threads,
        timeout=args.timeout,
        max_live=args.max,
        output=args.output,
    ).run()


if __name__ == '__main__':
    main()

'''