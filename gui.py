import customtkinter as ctk
import sys
import threading
import re
import traceback
import tkinter as tk
import tkinter.filedialog as fd
import types
import time
import os
import csv
import ctypes
import json
from collections import deque

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]
    def __init__(self):
        import queue
        self._fast_queue = queue.Queue()
        self.dwLength = ctypes.sizeof(self)
        super(MEMORYSTATUSEX, self).__init__()

def get_hardware_limits():
    cores = os.cpu_count() or 4
    ram_gb = 4
    try:
        if os.name == 'nt':
            stat = MEMORYSTATUSEX()
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            ram_gb = stat.ullTotalPhys / (1024 ** 3)
    except: pass
    max_threads = int((cores * 150) + (ram_gb * 100))
    max_threads = min(max_threads, 5000)
    max_threads = max(max_threads, 500)
    
    if max_threads >= 3000:
        tier_key = "tier_ultra"
        color = "#10B981"
    elif max_threads >= 1500:
        tier_key = "tier_high"
        color = "#3B82F6"
    elif max_threads >= 800:
        tier_key = "tier_medium"
        color = "#F59E0B"
    else:
        tier_key = "tier_low"
        color = "#EF4444"
        
    return cores, round(ram_gb, 1), max_threads, tier_key, color

# Глобальный коллбэк для прогресс-бара
PROGRESS_CALLBACK = None

# Заглушка для tqdm — вместо прогресс-бара печатает прогресс текстом и дёргает UI
_tqdm_mock = types.ModuleType('tqdm')
class _FakeTqdm:
    def __init__(self, iterable=None, *args, **kwargs):
        self._it = iterable
        self._total = kwargs.get('total', 0)
        if not self._total and hasattr(iterable, '__len__'):
            self._total = len(iterable)
        self._desc = kwargs.get('desc', 'Прогресс')
        self._n = 0
        self._step = max(1, self._total // 100) if self._total else 100
        self._last_print = 0
    def __iter__(self):
        for item in (self._it or []):
            yield item
            self.update(1)
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def update(self, n=1):
        self._n += n
        pct = self._n / self._total if self._total else 0
            
        if self._n - self._last_print >= self._step:
            self._last_print = self._n
            if PROGRESS_CALLBACK:
                PROGRESS_CALLBACK(self._desc, pct, self._n, self._total)
            if self._total:
                print(f"    [{self._desc}] {self._n}/{self._total} ({int(pct*100)}%)")
            else:
                print(f"    [{self._desc}] {self._n}...")
    def close(self):
        if self._total:
            print(f"    [{self._desc}] {self._total}/{self._total} (100%) ✓")
            if PROGRESS_CALLBACK:
                PROGRESS_CALLBACK(self._desc, 1.0, self._total, self._total)
    def set_description(self, *a, **kw): pass
    def set_postfix(self, *a, **kw): pass
_tqdm_mock.tqdm = _FakeTqdm
_tqdm_mock.trange = lambda *a, **kw: range(*a)
sys.modules['tqdm'] = _tqdm_mock
sys.modules['tqdm.auto'] = _tqdm_mock

from fetch_proxy import ProxyHunter

# --- ТЕМА ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#0B0F19"
CARD = "#111827"
CARD2 = "#0D1117"
BORDER = "#1E293B"
BLUE = "#3B82F6"
GREEN = "#10B981"
RED = "#EF4444"
GOLD = "#F59E0B"
MUTED = "#64748B"
TEXT = "#E2E8F0"

# --- ВСЕ СТРАНЫ МИРА ПО КОНТИНЕНТАМ ---
REGIONS = {
    "RU": {

    "🇪🇺 Европа": {
        "AT": "Австрия",
        "BE": "Бельгия",
        "BG": "Болгария",
        "HR": "Хорватия",
        "CY": "Кипр",
        "CZ": "Чехия",
        "DK": "Дания",
        "EE": "Эстония",
        "FI": "Финляндия",
        "FR": "Франция",
        "DE": "Германия",
        "GR": "Греция",
        "HU": "Венгрия",
        "IE": "Ирландия",
        "IT": "Италия",
        "LV": "Латвия",
        "LT": "Литва",
        "LU": "Люксембург",
        "MT": "Мальта",
        "NL": "Нидерланды",
        "PL": "Польша",
        "PT": "Португалия",
        "RO": "Румыния",
        "SK": "Словакия",
        "SI": "Словения",
        "ES": "Испания",
        "SE": "Швеция",
        "NO": "Норвегия",
        "CH": "Швейцария",
        "GB": "Великобритания",
        "IS": "Исландия",
        "AL": "Албания",
        "BA": "Босния",
        "ME": "Черногория",
        "MK": "Сев. Македония",
        "RS": "Сербия",
        "MD": "Молдова"
    },
    "🌎 Сев. Америка": {
        "US": "США",
        "CA": "Канада",
        "MX": "Мексика",
        "CR": "Коста-Рика",
        "PA": "Панама",
        "GT": "Гватемала",
        "HN": "Гондурас",
        "SV": "Сальвадор",
        "NI": "Никарагуа",
        "CU": "Куба",
        "DO": "Доминикана",
        "JM": "Ямайка",
        "TT": "Тринидад",
        "HT": "Гаити"
    },
    "🌎 Юж. Америка": {
        "BR": "Бразилия",
        "AR": "Аргентина",
        "CL": "Чили",
        "CO": "Колумбия",
        "PE": "Перу",
        "VE": "Венесуэла",
        "EC": "Эквадор",
        "UY": "Уругвай",
        "PY": "Парагвай",
        "BO": "Боливия"
    },
    "🌏 Азия": {
        "CN": "Китай",
        "JP": "Япония",
        "KR": "Юж. Корея",
        "IN": "Индия",
        "ID": "Индонезия",
        "TH": "Таиланд",
        "VN": "Вьетнам",
        "PH": "Филиппины",
        "MY": "Малайзия",
        "SG": "Сингапур",
        "TW": "Тайвань",
        "HK": "Гонконг",
        "BD": "Бангладеш",
        "PK": "Пакистан",
        "KZ": "Казахстан",
        "UZ": "Узбекистан",
        "AZ": "Азербайджан",
        "GE": "Грузия",
        "AM": "Армения",
        "IL": "Израиль",
        "TR": "Турция",
        "AE": "ОАЭ",
        "SA": "Сауд. Аравия",
        "QA": "Катар",
        "KW": "Кувейт",
        "IQ": "Ирак",
        "IR": "Иран",
        "LB": "Ливан",
        "JO": "Иордания",
        "MM": "Мьянма",
        "KH": "Камбоджа",
        "NP": "Непал",
        "LK": "Шри-Ланка",
        "MN": "Монголия"
    },
    "🇷🇺 СНГ": {
        "RU": "Россия",
        "UA": "Украина",
        "BY": "Беларусь",
        "KG": "Кыргызстан",
        "TJ": "Таджикистан",
        "TM": "Туркменистан"
    },
    "🌍 Африка": {
        "ZA": "ЮАР",
        "NG": "Нигерия",
        "EG": "Египет",
        "KE": "Кения",
        "GH": "Гана",
        "TZ": "Танзания",
        "ET": "Эфиопия",
        "MA": "Марокко",
        "TN": "Тунис",
        "DZ": "Алжир",
        "CM": "Камерун",
        "SN": "Сенегал",
        "UG": "Уганда",
        "MZ": "Мозамбик",
        "AO": "Ангола",
        "CD": "ДР Конго",
        "RW": "Руанда",
        "LY": "Ливия"
    },
    "🌏 Океания": {
        "AU": "Австралия",
        "NZ": "Новая Зеландия",
        "FJ": "Фиджи",
        "PG": "Папуа-Нов. Гвинея"
    }
},
    "EN": {
    "🇪🇺 Europe": {
        "AT": "Austria",
        "BE": "Belgium",
        "BG": "Bulgaria",
        "HR": "Croatia",
        "CY": "Cyprus",
        "CZ": "Czechia",
        "DK": "Denmark",
        "EE": "Estonia",
        "FI": "Finland",
        "FR": "France",
        "DE": "Germany",
        "GR": "Greece",
        "HU": "Hungary",
        "IE": "Ireland",
        "IT": "Italy",
        "LV": "Latvia",
        "LT": "Lithuania",
        "LU": "Luxembourg",
        "MT": "Malta",
        "NL": "Netherlands",
        "PL": "Poland",
        "PT": "Portugal",
        "RO": "Romania",
        "SK": "Slovakia",
        "SI": "Slovenia",
        "ES": "Spain",
        "SE": "Sweden",
        "NO": "Norway",
        "CH": "Switzerland",
        "GB": "United Kingdom",
        "IS": "Iceland",
        "AL": "Albania",
        "BA": "Bosnia",
        "ME": "Montenegro",
        "MK": "North Macedonia",
        "RS": "Serbia",
        "MD": "Moldova"
    },
    "🌎 North America": {
        "US": "USA",
        "CA": "Canada",
        "MX": "Mexico",
        "CR": "Costa Rica",
        "PA": "Panama",
        "GT": "Guatemala",
        "HN": "Honduras",
        "SV": "El Salvador",
        "NI": "Nicaragua",
        "CU": "Cuba",
        "DO": "Dominican Republic",
        "JM": "Jamaica",
        "TT": "Trinidad",
        "HT": "Haiti"
    },
    "🌎 South America": {
        "BR": "Brazil",
        "AR": "Argentina",
        "CL": "Chile",
        "CO": "Colombia",
        "PE": "Peru",
        "VE": "Venezuela",
        "EC": "Ecuador",
        "UY": "Uruguay",
        "PY": "Paraguay",
        "BO": "Bolivia"
    },
    "🌏 Asia": {
        "CN": "China",
        "JP": "Japan",
        "KR": "South Korea",
        "IN": "India",
        "ID": "Indonesia",
        "TH": "Thailand",
        "VN": "Vietnam",
        "PH": "Philippines",
        "MY": "Malaysia",
        "SG": "Singapore",
        "TW": "Taiwan",
        "HK": "Hong Kong",
        "BD": "Bangladesh",
        "PK": "Pakistan",
        "KZ": "Kazakhstan",
        "UZ": "Uzbekistan",
        "AZ": "Azerbaijan",
        "GE": "Georgia",
        "AM": "Armenia",
        "IL": "Israel",
        "TR": "Turkey",
        "AE": "UAE",
        "SA": "Saudi Arabia",
        "QA": "Qatar",
        "KW": "Kuwait",
        "IQ": "Iraq",
        "IR": "Iran",
        "LB": "Lebanon",
        "JO": "Jordan",
        "MM": "Myanmar",
        "KH": "Cambodia",
        "NP": "Nepal",
        "LK": "Sri Lanka",
        "MN": "Mongolia"
    },
    "🇷🇺 CIS": {
        "RU": "Russia",
        "UA": "Ukraine",
        "BY": "Belarus",
        "KG": "Kyrgyzstan",
        "TJ": "Tajikistan",
        "TM": "Turkmenistan"
    },
    "🌍 Africa": {
        "ZA": "South Africa",
        "NG": "Nigeria",
        "EG": "Egypt",
        "KE": "Kenya",
        "GH": "Ghana",
        "TZ": "Tanzania",
        "ET": "Ethiopia",
        "MA": "Morocco",
        "TN": "Tunisia",
        "DZ": "Algeria",
        "CM": "Cameroon",
        "SN": "Senegal",
        "UG": "Uganda",
        "MZ": "Mozambique",
        "AO": "Angola",
        "CD": "DR Congo",
        "RW": "Rwanda",
        "LY": "Libya"
    },
    "🌏 Oceania": {
        "AU": "Australia",
        "NZ": "New Zealand",
        "FJ": "Fiji",
        "PG": "Papua New Guinea"
    }
}
}

ISO_TO_NAME = {
    "RU": {
},
    "EN": {}
}
for lang in ["RU", "EN"]:
    for r, countries in REGIONS[lang].items():
        ISO_TO_NAME[lang].update(countries)
    ISO_TO_NAME[lang]['Unknown'] = "Unknown" if lang == "EN" else "Неизвестно"


LANG = {
    "EN": {
        "cfg": "Configuration",
        "lang_lbl": "Language:",
        "tab_settings": "Settings",
        "tab_countries": "Countries",
        "threads": "Threads",
        "timeout": "Timeout (sec)",
        "ping": "Max Ping (ms)",
        "speed": "Min Speed (Mbps)",
        "smtp": "Check SMTP",
        "res": "Residential Only",
        "all": "✓ All",
        "all_short": "All",
        "reset": "✗ Reset",
        "reset_short": "Reset",
        "tier1": "Tier-1",
        "start": " START HUNT",
        "running": "■ RUNNING...",
        "prepare": "Preparing...",
        "total": "Total Collected",
        "live": "Live Proxies",
        "elite": "Elite Proxies",
        "wait": "Waiting to start...",
        "step1": "Fetching from sources...",
        "step2": "Basic liveness check...",
        "step3": "Advanced filtering...",
        "step4": "Completed!",
        "done_msg": "[✓] Done! Results in folders results_elite and results_live.",
        "tab_terminal": "Terminal",
        "tab_results": "Results",
        "proto": "Protocol",
        "ip": "IP Address",
        "port": "Port",
        "country": "Country",
        "copy": "📋 Copy",
        "refresh": "🔄 Refresh",
        "download": "📥 Download:",
        "csv": "CSV (Full)",
        "txt_proto": "Protocol://IP:Port",
        "txt1": "IP:Port",
        "txt2": "IP Only",
        "copied": "✓ Copied!",
        "csv_saved": "✓ CSV saved!",
        "txt_saved": "✓ TXT saved!",
        "txt_ip_saved": "✓ TXT (IP) saved!",
        "no_data": "No data",
        "europe": "Europe",
        "hw_title": "💻 PC SPECIFICATIONS",
        "hw_cores": "• Processor: {0} Cores",
        "hw_ram": "• RAM: {0} GB",
        "hw_threads": "• Safe thread limit: {0}",
        "hw_class": "• Class: ",
        "tier_ultra": "ULTRA (Beast 🚀)",
        "tier_high": "HIGH (Gaming ⚡)",
        "tier_medium": "MEDIUM (Office 🖥️)",
        "tier_low": "LOW (Potato 🥔)",
        "proxies_count": "{0} proxies",
        "subtitle": "v4.0 · Advanced Filtration",
        "source_live": "Live",
        "source_elite": "Elite",
        "source_datacenter": "Datacenter",
        "source_residential": "Residential",
        "source_mobile": "Mobile",
        "proto_all": "All",
        "pause": " Pause",
        "resume": "▶ Resume",
        "cancel": " Cancel",
        "copy_terminal": "Copy Terminal",
        "copied_terminal": "✓ Copied",
        "all_protocols": "All Protocols",
        "all_countries_filter": "All Countries",
        "protocols_n": "Protocols ({0}) ▼",
        "countries_n": "Countries ({0}) ▼",
        "apply_filter": "Apply Filter",
        "tab_checker": "Checker",
        "checker_input_lbl": "Paste proxies (IP:PORT):",
        "checker_start": "START CHECK",
        "checker_stopping": "STOPPING...",
        "checker_running": "CHECKING...",
        "checker_load": "Load",
        "checker_clear": "Clear",
        "checker_what": "What to check:",
        "checker_anon": "Anonymity",
        "checker_bl": "Blacklists",
        "checker_speed": "Speed",
        "checker_h_proxy": "Proxy",
        "checker_h_ping": "Ping",
        "checker_h_anon": "Anonymity",
        "checker_h_bl": "Blacklists",
        "checker_h_speed": "Speed",
        "checker_save_criteria": "Save by criteria:",
        "checker_only_alive": "Alive Only",
        "checker_only_elite": "Elite Only",
        "checker_only_clean": "Clean Only",
        "checker_only_smtp": "SMTP Only",
        "checker_download": "Download .txt",
        "checker_saved": "✓ Saved ({0})",
        "log_live_found": "[+] Live proxy: {0}:{1} ({2} - {3})",
        "log_elite_found": "[+] 💎 Elite proxy: {0}:{1} ({2} - {3})",
        "error_no_countries": "Select at least 1 country!",
        "error_no_proxies": "No valid proxies found!",
        "error_file_size": "File too large (max 10MB)!",
        "error_file_type": "Invalid file type!",
        "checker_placeholder_text": "Proxies (full check):\nhttp://user:pass@ip:port\nhttps://user:pass@ip:port\nsocks5h://user:pass@ip:port\n\nOnly IP (reputation check):\n192.168.x.x\n10.0.x.x",
        "tab_proxies": "Proxies",
        "proxy_title": "🔗 Proxies for scanning",
        "reset_filter": "Reset Filter",
        "search": "Search...",
        "copy_lbl": "📋 Copy:",
        "proxy_load": "Load",
        "proxy_clear": "Clear",
        "proxy_scan_via": "Scan through proxies",
        "proxy_rotation": "Auto-rotation (round-robin)",
        "proxy_remove_dead": "Remove dead automatically",
        "proxy_loaded": "Loaded: {0}",
        "terminal_empty": "[ Terminal empty ]",
        "proxy_alive": "Alive: {0}",
        "random_title": "🎲 RANDOM GENERATION",
        "random_count": "Count:",
        "random_enable": "Generate random on start",
        "proxy_placeholder": "Paste proxies:\nhttp://ip:port\nsocks5://ip:port",
        "chk_ping_ok": "{0} ms",
        "chk_timeout": "⏳ Timeout",
        "chk_error": "❌ Error",
        "chk_skip": "— Skip",
        "chk_transparent": "Transparent",
        "chk_elite": "💎 Elite",
        "chk_speed_ok": "{0} Mbps",
        "chk_speed_bad": "{0} Mbps",
        "chk_open": "■ Open",
        "chk_closed": "🚫 Closed",
        "chk_blacklisted": "💀 Blacklisted",
        "chk_clean": "✨ Clean"
    },
    "RU": {

        "cfg": "Конфигурация",
        "lang_lbl": "Язык:",
        "tab_settings": "Параметры",
        "tab_countries": "Страны",
        "threads": "Потоки",
        "timeout": "Таймаут (сек)",
        "ping": "Макс Пинг (мс)",
        "speed": "Мин Скор. (Мбит/с)",
        "smtp": "Проверять SMTP",
        "res": "Только Residential",
        "all": "✓ Все",
        "all_short": "Все",
        "reset": "✗ Сброс",
        "reset_short": "Сброс",
        "tier1": "Tier-1",
        "start": "НАЧАТЬ СБОР",
        "running": "РАБОТАЕТ...",
        "prepare": "Подготовка...",
        "total": "Всего собрано",
        "live": "Рабочие",
        "elite": "Элитные",
        "wait": "Ожидание запуска...",
        "step1": "Сбор из источников...",
        "step2": "Базовая проверка на живость...",
        "step3": "Расширенная фильтрация...",
        "step4": "Завершено!",
        "done_msg": "[✓] Готово! Результаты в папках results_elite и results_live.",
        "tab_terminal": "Терминал",
        "tab_results": "Результаты",
        "proto": "Протокол",
        "ip": "IP-адрес",
        "port": "Порт",
        "country": "Страна",
        "copy": "📋 Копировать",
        "refresh": "🔄 Обновить",
        "download": "📥 Скачать:",
        "csv": "CSV (Полный)",
        "txt_proto": "Protocol://IP:Port",
        "txt1": "IP:Port",
        "txt2": "Только IP",
        "copied": "✓ Скопировано!",
        "csv_saved": "✓ CSV сохранен!",
        "txt_saved": "✓ TXT сохранен!",
        "txt_ip_saved": "✓ TXT (IP) сохранен!",
        "no_data": "Нет данных",
        "europe": "Европа",
        "hw_title": "💻 ХАРАКТЕРИСТИКИ ПК",
        "hw_cores": "• Процессор: {0} Ядер",
        "hw_ram": "• ОЗУ: {0} GB",
        "hw_threads": "• Безопасный лимит потоков: {0}",
        "hw_class": "• Класс: ",
        "tier_ultra": "ULTRA (Монстр 🚀)",
        "tier_high": "HIGH (Игровой ⚡)",
        "tier_medium": "MEDIUM (Офисный 🖥️)",
        "tier_low": "LOW (Картошка 🥔)",
        "proxies_count": "{0} прокси",
        "subtitle": "v4.0 · Продвинутая фильтрация",
        "source_live": "Рабочие",
        "source_elite": "Elite",
        "source_datacenter": "Datacenter",
        "source_residential": "Residential",
        "source_mobile": "Mobile",
        "proto_all": "Все",
        "pause": "Пауза",
        "resume": "▶ Продолжить",
        "cancel": "Отмена",
        "copy_terminal": "Копировать терминал",
        "copied_terminal": "✓ Скопировано",
        "all_protocols": "Все протоколы",
        "all_countries_filter": "Все страны",
        "protocols_n": "Протоколы ({0}) ▼",
        "countries_n": "Страны ({0}) ▼",
        "apply_filter": "Задать фильтр",
        "tab_checker": "Проверка",
        "checker_input_lbl": "Вставьте прокси (IP:PORT):",
        "checker_start": "НАЧАТЬ ПРОВЕРКУ",
        "checker_stopping": "ОСТАНОВКА...",
        "checker_running": "ПРОВЕРКА...",
        "checker_load": "Загрузить",
        "checker_clear": "Очистить",
        "checker_what": "Что проверять:",
        "checker_anon": "Анонимность",
        "checker_bl": "Блеклисты",
        "checker_speed": "Скорость",
        "checker_h_proxy": "Прокси",
        "checker_h_ping": "Пинг",
        "checker_h_anon": "Анонимность",
        "checker_h_bl": "Блеклисты",
        "checker_h_speed": "Скорость",
        "checker_save_criteria": "Сохранить по критериям:",
        "checker_only_alive": "Только Рабочие",
        "checker_only_elite": "Только Elite",
        "checker_only_clean": "Только Clean (без спам-баз)",
        "checker_only_smtp": "Только SMTP",
        "checker_download": "Скачать .txt",
        "checker_saved": "✓ Сохранено ({0})",
        "log_live_found": "[+] Рабочий прокси: {0}:{1} ({2} - {3})",
        "log_elite_found": "[+] 💎 Элитный прокси: {0}:{1} ({2} - {3})",
        "error_no_countries": "Выберите хотя бы 1 страну!",
        "error_no_proxies": "Нет валидных прокси!",
        "error_file_size": "Файл слишком большой (макс 10МБ)!",
        "error_file_type": "Неверный формат файла!",
        "checker_placeholder_text": "Прокси (полная проверка):\nhttp://user:pass@ip:port\nhttps://user:pass@ip:port\nsocks5h://user:pass@ip:port\n\nТолько IP (проверка репутации):\n192.168.x.x\n10.0.x.x",
        "tab_proxies": "Прокси",
        "proxy_title": "🔗 Прокси для сканирования",
        "reset_filter": "Сбросить фильтр",
        "search": "Поиск...",
        "copy_lbl": "📋 Скопировать:",
        "proxy_load": "Загрузить",
        "proxy_clear": "Очистить",
        "proxy_scan_via": "Сканировать через прокси",
        "proxy_rotation": "Авто-ротация (round-robin)",
        "proxy_remove_dead": "Удалять мёртвые автоматически",
        "proxy_loaded": "Загружено: {0}",
        "terminal_empty": "[ Терминал пуст ]",
        "proxy_alive": "Живых: {0}",
        "random_title": "🎲 РАНДОМНАЯ ГЕНЕРАЦИЯ",
        "random_count": "Количество:",
        "random_enable": "Генерировать рандомные при запуске",
        "proxy_placeholder": "Вставьте прокси:\nhttp://ip:port\nsocks5://ip:port",
        "chk_ping_ok": "{0} мс",
        "chk_timeout": "⏳ Таймаут",
        "chk_error": "❌ Ошибка",
        "chk_skip": "— Пропуск",
        "chk_transparent": "Transparent",
        "chk_elite": "💎 Elite",
        "chk_speed_ok": "{0} Мбит/с",
        "chk_speed_bad": "{0} Мбит/с",
        "chk_open": "■ Открыт",
        "chk_closed": "🚫 Закрыт",
        "chk_blacklisted": "💀 В блэклисте",
        "chk_clean": "✨ Чистый"
    }
}
import os
from PIL import Image

def load_icon(name):
    try:
        light = Image.open(f"assets/icons/{name}_dark.png")
        dark = Image.open(f"assets/icons/{name}_light.png")
        return ctk.CTkImage(light_image=light, dark_image=dark, size=(18, 18))
    except Exception as e:
        print(f"Error loading {name}: {e}")
        return None

class ProxyHunterApp(ctk.CTk):
    def __init__(self):
        import queue
        self._fast_queue = queue.Queue()
        super().__init__()
        
        # Load all minimalist SVG-like icons
        self.icons = {
            "settings": load_icon("settings"),
            "lightning-bolt": load_icon("lightning-bolt"),
            "globe": load_icon("globe"),
            "minus": load_icon("minus"),
            "shield": load_icon("shield"),
            "console": load_icon("console"),
            "clipboard": load_icon("clipboard"),
            "checked": load_icon("checked"),
            "play": load_icon("play"),
            "stop": load_icon("stop"),
            "pause": load_icon("pause"),
            "cancel": load_icon("cancel"),
            "folder-invoices": load_icon("folder-invoices"),
            "trash": load_icon("trash"),
            "download": load_icon("download")
        }

        self.title("Proxy Hunter v4.0")
        self.geometry("1375x770")
        self.minsize(1375, 770)
        self.configure(fg_color=BG)
        self.is_running = False
        self.hunter_thread = None
        self.checker_is_running = False
        self.country_vars = {}
        self._countries_built = False
        self._my_country = self._detect_my_country()
        self._region_btns = []  # for translation of per-category 'All' buttons
        self._region_reset_btns = []  # for translation of per-category 'Reset' buttons

        # Корневой фрейм — обычный CTkFrame (НЕ scrollable, чтобы не было конфликтов)
        self.root_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.root_frame.pack(fill="both", expand=True)
        
        # Жёсткий 2-колоночный layout
        self.root_frame.grid_columnconfigure(0, weight=0, minsize=360)
        self.root_frame.grid_columnconfigure(1, weight=1)
        self.root_frame.grid_rowconfigure(0, weight=1)

        self.current_lang = "RU"
        self.interactive_widgets = []

        self._build_sidebar()
        self._build_main()

        self.bind_all("<Button-1>", self._on_click_outside)
        
    
    def _safe_config(self, widget, **kwargs):
        try:
            if hasattr(widget, "winfo_exists") and widget.winfo_exists():
                widget.configure(**kwargs)
        except Exception:
            pass

    def _t(self, key):
        return LANG[self.current_lang].get(key, key)
        
    def _set_language(self, lang):
        self.current_lang = lang
        self._apply_language()
        
    def _set_ui_state(self, state):
        for w in self.interactive_widgets:
            if w.winfo_exists():
                w.configure(state=state)
                
    def _on_click_outside(self, event):
        try:
            widget_type = str(event.widget).lower()
            if "entry" not in widget_type and "text" not in widget_type:
                self.focus_set()
        except Exception:
            pass

    def _flash_error_widget(self, widget, temp_text=None):
        if not widget.winfo_exists(): return
        try:
            orig_fg = widget.cget("fg_color")
            orig_hover = widget.cget("hover_color") if hasattr(widget, "cget") and "hover_color" in widget.configure() else None
            orig_text = widget.cget("text") if hasattr(widget, "cget") and "text" in widget.configure() else None
            
            widget.configure(fg_color="#7F1D1D")
            if orig_hover: widget.configure(hover_color="#7F1D1D")
            if temp_text and orig_text: widget.configure(text=temp_text)
            
            def restore():
                if not widget.winfo_exists(): return
                widget.configure(fg_color=orig_fg)
                if orig_hover: widget.configure(hover_color=orig_hover)
                if temp_text and orig_text: widget.configure(text=orig_text)
            self.after(800, restore)
        except Exception: pass


    def _apply_language(self):
        self._safe_config(self.lbl_cfg, text="  " + self._t("cfg"))
        self._safe_config(self.lbl_lang, text=self._t("lang_lbl"))
        
        if hasattr(self, "lbl_threads"): self._safe_config(self.lbl_threads, text=self._t("threads"))
        if hasattr(self, "lbl_timeout"): self._safe_config(self.lbl_timeout, text=self._t("timeout"))
        if hasattr(self, "lbl_ping"): self._safe_config(self.lbl_ping, text=self._t("ping"))
        if hasattr(self, "lbl_speed"): self._safe_config(self.lbl_speed, text=self._t("speed"))
        
        if hasattr(self, "btn_all") and self.btn_all.winfo_exists(): self._safe_config(self.btn_all, text=self._t("all"))
        if hasattr(self, "btn_reset") and self.btn_reset.winfo_exists(): self._safe_config(self.btn_reset, text=self._t("reset"))
        if hasattr(self, "btn_europe") and self.btn_europe.winfo_exists(): self._safe_config(self.btn_europe, text=self._t("europe"))
        if hasattr(self, "btn_tier1") and self.btn_tier1.winfo_exists(): self._safe_config(self.btn_tier1, text=self._t("tier1"))
        
        # Translate per-category 'All' and 'Reset' buttons
        for btn in getattr(self, "_region_btns", []):
            if btn.winfo_exists(): self._safe_config(btn, text=self._t("all_short"))
        for btn in getattr(self, "_region_reset_btns", []):
            if btn.winfo_exists(): self._safe_config(btn, text=self._t("reset_short"))
        
        self._safe_config(self.smtp_switch, text=self._t("smtp"))
        self._safe_config(self.res_switch, text=self._t("res"))
        
        if not self.is_running:
            self._safe_config(self.start_btn, text=self._t("start"), image=self.icons["play"])
        else:
            self._safe_config(self.start_btn, text=self._t("running"), image=self.icons["stop"])
            
        if hasattr(self, "pause_btn"):
            if getattr(self, "is_paused", False):
                self._safe_config(self.pause_btn, text=self._t("resume"), image=self.icons["play"])
            else:
                self._safe_config(self.pause_btn, text=self._t("pause"), image=self.icons["pause"])
        if hasattr(self, "cancel_btn"):
            self._safe_config(self.cancel_btn, text=self._t("cancel"), image=self.icons["cancel"])
            
        self._safe_config(self.lbl_stat_total, text=self._t("total"))
        self._safe_config(self.lbl_stat_live, text=self._t("live"))
        self._safe_config(self.lbl_stat_elite, text=self._t("elite"))
        if hasattr(self, "lbl_stat_dc"): self._safe_config(self.lbl_stat_dc, text=self._t("source_datacenter"))
        if hasattr(self, "lbl_stat_res"): self._safe_config(self.lbl_stat_res, text=self._t("source_residential"))
        if hasattr(self, "lbl_stat_mob"): self._safe_config(self.lbl_stat_mob, text=self._t("source_mobile"))
        
        self._safe_config(self.btn_copy, text=self._t("copy"))
        self._safe_config(self.btn_refresh, text=self._t("refresh"))
        self._safe_config(self.lbl_download, text=self._t("download"))
        self._safe_config(self.btn_csv, text=self._t("csv"))
        self._safe_config(self.btn_txt1, text=self._t("txt1"))
        self._safe_config(self.btn_txt2, text=self._t("txt2"))
        
        if hasattr(self, "lbl_copy_sec"): self._safe_config(self.lbl_copy_sec, text=self._t("copy_lbl"))
        if hasattr(self, "btn_copy_csv"): self._safe_config(self.btn_copy_csv, text=self._t("csv"))
        if hasattr(self, "btn_copy_txt_proto"): self._safe_config(self.btn_copy_txt_proto, text=self._t("txt_proto"))
        if hasattr(self, "btn_copy_txt1"): self._safe_config(self.btn_copy_txt1, text=self._t("txt1"))
        if hasattr(self, "btn_copy_txt2"): self._safe_config(self.btn_copy_txt2, text=self._t("txt2"))
        
        # Subtitle
        if hasattr(self, "subtitle_lbl"): self._safe_config(self.subtitle_lbl, text=self._t("subtitle"))
        
        # HW info labels
        if hasattr(self, "hw_title_lbl") and self.hw_title_lbl.winfo_exists():
            self._safe_config(self.hw_title_lbl, text=self._t("hw_title"))
            self._safe_config(self.hw_cores_lbl, text=self._t("hw_cores").format(self._hw_cores))
            self._safe_config(self.hw_ram_lbl, text=self._t("hw_ram").format(self._hw_ram))
            self._safe_config(self.hw_threads_lbl, text=self._t("hw_threads").format(self._hw_max_threads))
            self._safe_config(self.hw_class_lbl, text=self._t("hw_class"))
            self._safe_config(self.hw_tier_lbl, text=self._t(self._hw_tier_key))

        # --- MISSING APPLY LANGUAGE UPDATES ---
        if hasattr(self, "dc_switch"): self._safe_config(self.dc_switch, text=self._t("source_datacenter"))
        if hasattr(self, "mob_switch"): self._safe_config(self.mob_switch, text=self._t("source_mobile"))
        
        if hasattr(self, "country_count_label"):
            txt = self.country_count_label.cget("text")
            import re
            m = re.search(r'\d+', txt)
            if m: self._safe_config(self.country_count_label, text=self._t("countries_n").format(m.group(0)))
            
        if hasattr(self, "btn_txt_proto"): self._safe_config(self.btn_txt_proto, text=self._t("txt_proto"))
        if hasattr(self, "btn_txt2"): self._safe_config(self.btn_txt2, text=self._t("txt2"))
        
        if hasattr(self, "results_empty_lbl") and self.results_empty_lbl.winfo_exists():
            self._safe_config(self.results_empty_lbl, text=self._t("no_data"))
            
        if hasattr(self, "terminal_empty_lbl") and self.terminal_empty_lbl.winfo_exists():
            self._safe_config(self.terminal_empty_lbl, text=self._t("terminal_empty"))
            
        if hasattr(self, "btn_copy_term"): self._safe_config(self.btn_copy_term, text=self._t("copy_terminal"))
        if hasattr(self, "btn_proto_filter"): self._safe_config(self.btn_proto_filter, text=self._t("all_protocols"))
        if hasattr(self, "btn_country_filter"): self._safe_config(self.btn_country_filter, text=self._t("all_countries_filter"))

        # In _apply_language, there is a proxy tab check:
        # if hasattr(self, "_proxies_built") and self._proxies_built:
        # we need to make sure random generation is covered.

        
        # Result count label
        if hasattr(self, "result_count_lbl"):
            txt = self.result_count_lbl.cget("text")
            import re as _re
            m = _re.search(r'(\d+)', txt)
            if m:
                self._safe_config(self.result_count_lbl, text=self._t("proxies_count").format(m.group(1)))
        
        # Source segmented buttons (Live/Elite)
        if hasattr(self, "source_seg"):
            try:
                for k, btn in self.source_seg._buttons_dict.items():
                    if k == "Live": self._safe_config(btn, text=self._t("source_live"))
                    elif k == "Elite": self._safe_config(btn, text=self._t("source_elite"))
            except Exception: pass
        
        self.proxy_tree.heading("proto", text=self._t("proto"))
        self.proxy_tree.heading("ip", text=self._t("ip"))
        self.proxy_tree.heading("port", text=self._t("port"))
        self.proxy_tree.heading("country", text=self._t("country"))
        
        if hasattr(self, "tab_view"):
            for k in ["Параметры", "Settings"]:
                if k in self.tab_view._segmented_button._buttons_dict:
                    self._safe_config(self.tab_view._segmented_button._buttons_dict[k], text=self._t("tab_settings"))
            for k in ["Страны", "Countries"]:
                if k in self.tab_view._segmented_button._buttons_dict:
                    self._safe_config(self.tab_view._segmented_button._buttons_dict[k], text=self._t("tab_countries"))
            for k in ["Прокси", "Proxies"]:
                if k in self.tab_view._segmented_button._buttons_dict:
                    self._safe_config(self.tab_view._segmented_button._buttons_dict[k], text=self._t("tab_proxies"))
                
        if hasattr(self, "main_tabs"):
            for k in ["Терминал", "Terminal"]:
                if k in self.main_tabs._segmented_button._buttons_dict:
                    self._safe_config(self.main_tabs._segmented_button._buttons_dict[k], text=self._t("tab_terminal"))
            for k in ["Результаты", "Results"]:
                if k in self.main_tabs._segmented_button._buttons_dict:
                    self._safe_config(self.main_tabs._segmented_button._buttons_dict[k], text=self._t("tab_results"))
            for k in ["Проверка", "Checker"]:
                if k in self.main_tabs._segmented_button._buttons_dict:
                    self._safe_config(self.main_tabs._segmented_button._buttons_dict[k], text=self._t("tab_checker"))

        # Terminal tab
        if hasattr(self, "btn_copy_term"):
            self._safe_config(self.btn_copy_term, text=self._t("copy_terminal"))
        if hasattr(self, "tab_country_search"):
            self._safe_config(self.tab_country_search, placeholder_text=self._t("search"))
        
        # Results tab filters
        if hasattr(self, "btn_proto_filter"):
            a_p = {p for p in getattr(self, "selected_protos", set()) if p in getattr(self, "all_protos_in_db", set())}
            if not getattr(self, "selected_protos", set()) or len(a_p) == len(getattr(self, "all_protos_in_db", set())):
                self._safe_config(self.btn_proto_filter, text=self._t("all_protocols"))
            else:
                self._safe_config(self.btn_proto_filter, text=self._t("protocols_n").format(len(a_p)))
        if hasattr(self, "btn_country_filter"):
            a_c = {c for c in getattr(self, "selected_countries", set()) if c in getattr(self, "all_countries_in_db", set())}
            if not getattr(self, "selected_countries", set()) or len(a_c) == len(getattr(self, "all_countries_in_db", set())):
                self._safe_config(self.btn_country_filter, text=self._t("all_countries_filter"))
            else:
                self._safe_config(self.btn_country_filter, text=self._t("countries_n").format(len(a_c)))

        # Checker tab — full update
        if hasattr(self, "btn_check_start") and self.btn_check_start.cget("state") != "disabled":
            self._safe_config(self.btn_check_start, text=self._t("checker_start"))
        if hasattr(self, "_chk_btn_load"):
            self._safe_config(self._chk_btn_load, text=self._t("checker_load"))
            self._safe_config(self._chk_btn_clear, text=self._t("checker_clear"))
            self._safe_config(self._chk_lbl_what, text=self._t("checker_what"))
            self._safe_config(self._chk_cb_anon, text=self._t("checker_anon"))
            self._safe_config(self._chk_cb_bl, text=self._t("checker_bl"))
            self._safe_config(self._chk_cb_speed, text=self._t("checker_speed"))
            self._safe_config(self._chk_lbl_input, text=self._t("checker_input_lbl"))
            self._safe_config(self._chk_lbl_criteria, text=self._t("checker_save_criteria"))
            
            if hasattr(self, "terminal_empty_lbl"):
                if self.terminal_empty_lbl.cget("text") in ["[ Терминал пуст ]", "[ Terminal empty ]"]:
                    self._safe_config(self.terminal_empty_lbl, text=self._t("terminal_empty"))
            
            # Перевод плейсхолдера с сохранением введенного текста (если он не изменен)
            old_ph = getattr(self, "checker_placeholder", "")
            new_ph = self._t("checker_placeholder_text")
            if hasattr(self, "checker_input") and self.checker_input.get("1.0", "end-1c") == old_ph:
                self.checker_input.delete("1.0", "end")
                self.checker_input.insert("1.0", new_ph)
            self.checker_placeholder = new_ph
            self._safe_config(self._chk_cb_alive, text=self._t("checker_only_alive"))
            self._safe_config(self._chk_cb_elite, text=self._t("checker_only_elite"))
            self._safe_config(self._chk_cb_clean, text=self._t("checker_only_clean"))
            self._safe_config(self._chk_cb_smtp, text=self._t("checker_only_smtp"))
            self._safe_config(self.btn_save_checker, text=self._t("checker_download"))
            # Checker tree headings
            self.check_tree.heading("proxy", text=self._t("checker_h_proxy"))
            self.check_tree.heading("ping", text=self._t("checker_h_ping"))
            self.check_tree.heading("anon", text=self._t("checker_h_anon"))
            self.check_tree.heading("bl", text=self._t("checker_h_bl"))
            self.check_tree.heading("speed", text=self._t("checker_h_speed"))

            if hasattr(self, "check_tree"):
                other_lang = "RU" if self.current_lang == "EN" else "EN"
                status_keys = ["chk_timeout", "chk_error", "chk_skip", "chk_transparent", "chk_elite", 
                               "chk_open", "chk_closed", "chk_blacklisted", "chk_clean"]
                trans_map = {LANG[other_lang][k]: LANG[self.current_lang][k] for k in status_keys}
                
                def _translate_vals(vals):
                    if not vals or len(vals) < 7: return vals
                    v = list(vals)
                    if " мс" in str(v[2]) or " ms" in str(v[2]):
                        val = str(v[2]).replace(" мс", "").replace(" ms", "")
                        v[2] = self._t("chk_ping_ok").format(val)
                    elif str(v[2]) in trans_map: v[2] = trans_map[str(v[2])]
                    
                    if str(v[3]) in trans_map: v[3] = trans_map[str(v[3])]
                    if str(v[4]) in trans_map: v[4] = trans_map[str(v[4])]
                    
                    if " Мбит/с" in str(v[5]) or " Mbps" in str(v[5]):
                        val = str(v[5]).replace(" Мбит/с", "").replace(" Mbps", "")
                        v[5] = self._t("chk_speed_ok").format(val)
                    elif str(v[5]) in trans_map: v[5] = trans_map[str(v[5])]
                    
                    if str(v[6]) in trans_map: v[6] = trans_map[str(v[6])]
                    return v

                for item in self.check_tree.get_children():
                    self.check_tree.item(item, values=_translate_vals(self.check_tree.item(item, 'values')))
                
                if hasattr(self, "_checker_detached"):
                    for item, idx in self._checker_detached:
                        try:
                            self.check_tree.item(item, values=_translate_vals(self.check_tree.item(item, 'values')))
                        except: pass


        if hasattr(self, "progress_lbl"):
            txt = self.progress_lbl.cget("text")
            if txt in ["Ожидание запуска...", "Waiting to start..."]:
                self._safe_config(self.progress_lbl, text=self._t("wait"))

        if hasattr(self, "result_count_lbl"):
            txt = self.result_count_lbl.cget("text")
            if txt in ["Нет данных", "No data"]:
                self._safe_config(self.result_count_lbl, text=self._t("no_data"))
            elif "сохранен" in txt or "saved" in txt:
                pass # Already translated on action
                
        if hasattr(self, "proto_seg") and "Все" in self.proto_seg._buttons_dict:
            self._safe_config(self.proto_seg._buttons_dict["Все"], text=self._t("all_short"))

        # Rebuild countries list on language switch
        if getattr(self, "_countries_built", False):
            # Save existing checked states
            old_state = {iso: var.get() for iso, var in getattr(self, "country_vars", {}).items() if var.get()}
            if not getattr(self, "_old_country_state", None):
                self._old_country_state = old_state
            
            if hasattr(self, "tab_countries_ref"):
                try:
                    for w in self.tab_countries_ref.winfo_children():
                        w.destroy()
                except Exception:
                    pass
                self._countries_built = False
                
                # Rebuild it immediately so we don't leave it blank
                self._build_countries_tab(self.tab_countries_ref)
                self._countries_built = True

        # Reload the results table to update country names if they are currently loaded
        if hasattr(self, "proxy_tree"):
            self._load_results()
            
        # Update Proxy Tab Translations
        if hasattr(self, "_proxies_built") and self._proxies_built:
            try:
                if hasattr(self, "proxy_title_lbl"): self._safe_config(self.proxy_title_lbl, text=self._t("proxy_title"))
                if hasattr(self, "proxy_load_btn"): self._safe_config(self.proxy_load_btn, text=self._t("proxy_load"))
                if hasattr(self, "proxy_clear_btn"): self._safe_config(self.proxy_clear_btn, text=self._t("proxy_clear"))
                if hasattr(self, "proxy_scan_switch"): self._safe_config(self.proxy_scan_switch, text=self._t("proxy_scan_via"))
                if hasattr(self, "proxy_rot_switch"): self._safe_config(self.proxy_rot_switch, text=self._t("proxy_rotation"))
                if hasattr(self, "proxy_dead_switch"): self._safe_config(self.proxy_dead_switch, text=self._t("proxy_remove_dead"))
                if hasattr(self, "proxy_lbl_loaded"): self._safe_config(self.proxy_lbl_loaded, text=self._t("proxy_loaded").format(self._parsed_chain_count))
                if hasattr(self, "random_title_lbl"): self._safe_config(self.random_title_lbl, text=self._t("random_title"))
                if hasattr(self, "random_en_switch"): self._safe_config(self.random_en_switch, text=self._t("random_enable"))
                
                # Check if random labels exist
                if hasattr(self, "lbl_random_http"): self._safe_config(self.lbl_random_http, text=self._t("random_count") + " HTTP")
                if hasattr(self, "lbl_random_socks4"): self._safe_config(self.lbl_random_socks4, text=self._t("random_count") + " SOCKS4")
                if hasattr(self, "lbl_random_socks5"): self._safe_config(self.lbl_random_socks5, text=self._t("random_count") + " SOCKS5")
                
                # Update placeholder
                old_ph = getattr(self, "proxy_placeholder_text", "")
                new_ph = self._t("proxy_placeholder")
                if hasattr(self, "proxy_text") and self.proxy_text.get("0.0", "end-1c").strip() == old_ph.strip():
                    self.proxy_text.delete("0.0", "end")
                    self.proxy_text.insert("0.0", new_ph)
                self.proxy_placeholder_text = new_ph
                
            except Exception:
                pass
                
    # ===================== SIDEBAR =====================
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.root_frame, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER, width=360)
        self.sidebar.grid(row=0, column=0, padx=(15, 8), pady=15, sticky="nsew")
        self.sidebar.grid_rowconfigure(0, weight=1)
        self.sidebar.pack_propagate(False)  # Не позволять содержимому расширять sidebar

        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 8))
        ctk.CTkLabel(header, text="", image=self.icons["settings"], text_color=BLUE).pack(side="left")
        self.lbl_cfg = ctk.CTkLabel(header, text="  " + self._t("cfg"), font=("Segoe UI", 17, "bold"), text_color="white")
        self.lbl_cfg.pack(side="left")


        lang_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        lang_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.lbl_lang = ctk.CTkLabel(lang_frame, text=self._t("lang_lbl"), font=("Segoe UI", 12), text_color=MUTED)
        self.lbl_lang.pack(side="left", padx=(0, 10))
        self.lang_seg = ctk.CTkSegmentedButton(lang_frame, values=["EN", "RU"], command=self._set_language, fg_color=BORDER, selected_color=BLUE, unselected_color=CARD)
        self.lang_seg.set("RU")
        self.lang_seg.pack(side="left", fill="x", expand=True)

        self.tab_view = ctk.CTkTabview(self.sidebar, fg_color=CARD2, segmented_button_fg_color=BORDER,
                                        segmented_button_selected_color=BLUE, segmented_button_unselected_color=CARD,
                                        corner_radius=12, border_width=1, border_color=BORDER,
                                        command=self._on_tab_change)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tab_settings = self.tab_view.add("Параметры")
        self.tab_countries_ref = self.tab_view.add("Страны")
        self.tab_proxies_ref = self.tab_view.add("Прокси")

        self._build_settings_tab(tab_settings)

    def _smart_paste(self, event):
        try:
            widget = event.widget
            # For CTkTextbox, the event might come from the outer frame or inner text
            # We get the actual inner tk.Text widget to access methods properly
            if hasattr(widget, "master") and hasattr(widget.master, "_textbox"):
                widget = widget.master._textbox
            elif hasattr(widget, "_textbox"):
                widget = widget._textbox

            try:
                clipboard = widget.clipboard_get()
            except Exception:
                return "break"
                
            import re
            
            results = []
            text = clipboard
            
            # Сначала ищем VLESS/VMESS/SS и прочие URI
            URI_RE = re.compile(r'((?:vless|vmess|ss|ssr|trojan|tuic|hysteria2|tg)://[^\s"\'<>]+|https://t\.me/proxy\?[^\s"\'<>]+)', re.IGNORECASE)
            for uri in URI_RE.findall(text):
                results.append(uri)
                text = text.replace(uri, ' ')
                
            # Ищем классические IP:PORT с возможным протоколом и авторизацией
            IP_RE = re.compile(r'(?:[a-zA-Z0-9]+://)?(?:[a-zA-Z0-9_.-]+:[a-zA-Z0-9_.-]+@)?(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::\d{1,5})?')
            for p in IP_RE.findall(text):
                results.append(p)
                
            proxies = list(dict.fromkeys(results))
            if not proxies:
                text_to_insert = clipboard
            else:
                text_to_insert = "\n".join(proxies) + "\n"
            
            # Очищаем плейсхолдер перед вставкой
            if widget == getattr(self, "checker_input", None):
                ph = getattr(self, "checker_placeholder", "")
                if widget.get("1.0", "end-1c").strip() == ph.strip() or widget.get("0.0", "end-1c").strip() == ph.strip():
                    widget.delete("1.0", "end")
                    widget.configure(fg="#E2E8F0")
                widget.insert("insert", text_to_insert)
            else:
                # Скорее всего это proxy_text
                ph = getattr(self, "proxy_placeholder_text", "")
                if widget.get("1.0", "end-1c").strip() == ph.strip() or widget.get("0.0", "end-1c").strip() == ph.strip():
                    widget.delete("1.0", "end")
                widget.insert("insert", text_to_insert)
                if hasattr(self, "_update_chain_count"):
                    self.after(50, self._update_chain_count)
                
            return "break"
        except Exception:
            return "break"

    def _select_all(self, event):
        try:
            widget = event.widget
            if hasattr(widget, "master") and hasattr(widget.master, "_textbox"):
                widget = widget.master._textbox
            elif hasattr(widget, "_textbox"):
                widget = widget._textbox
            widget.tag_add("sel", "1.0", "end")
            return "break"
        except Exception:
            pass
    def _on_tab_change(self):
        """Ленивая загрузка вкладок стран и прокси"""
        if self.tab_view.get() in ["Страны", "Countries"] and not getattr(self, "_countries_built", False):
            self._countries_built = True
            self._build_countries_tab(self.tab_countries_ref)
        elif self.tab_view.get() in ["Прокси", "Proxies"] and not getattr(self, "_proxies_built", False):
            self._proxies_built = True
            self._build_proxies_tab(self.tab_proxies_ref)



    # --- Вкладка ПАРАМЕТРЫ ---
    def _build_settings_tab(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        frame.pack(fill="both", expand=True)

        # Start UI building
        self._hw_cores, self._hw_ram, self._hw_max_threads, self._hw_tier_key, self._hw_tier_color = get_hardware_limits()
        default_threads = min(500, self._hw_max_threads)

        self._add_slider(frame, "Threads", 10, self._hw_max_threads, default_threads, 1, "threads")
        self._add_slider(frame, "Timeout", 1, 60, 5, 1, "timeout")
        self._add_slider(frame, "Max Ping", 50, 2000, 700, 10, "ping")
        self._add_slider(frame, "Min Speed", 0.1, 10, 1.0, 0.1, "speed")

        ctk.CTkFrame(frame, fg_color=BORDER, height=1).pack(fill="x", padx=10, pady=12)

        self.smtp_var = ctk.BooleanVar(value=True)
        self.smtp_switch = ctk.CTkSwitch(frame, text=self._t("smtp"), variable=self.smtp_var, fg_color=BORDER, progress_color=BLUE, font=("Segoe UI", 13), text_color=TEXT)
        self.smtp_switch.pack(anchor="w", padx=10, pady=4)
        self.interactive_widgets.append(self.smtp_switch)

        self.dc_var = ctk.BooleanVar(value=True)
        self.dc_switch = ctk.CTkSwitch(frame, text=self._t("source_datacenter"), variable=self.dc_var, fg_color=BORDER, progress_color=BLUE, font=("Segoe UI", 13), text_color=TEXT)
        self.dc_switch.pack(anchor="w", padx=10, pady=4)
        self.interactive_widgets.append(self.dc_switch)

        self.res_var = ctk.BooleanVar(value=False)
        self.res_switch = ctk.CTkSwitch(frame, text=self._t("source_residential"), variable=self.res_var, fg_color=BORDER, progress_color=BLUE, font=("Segoe UI", 13), text_color=TEXT)
        self.res_switch.pack(anchor="w", padx=10, pady=4)
        self.interactive_widgets.append(self.res_switch)

        self.mob_var = ctk.BooleanVar(value=False)
        self.mob_switch = ctk.CTkSwitch(frame, text=self._t("source_mobile"), variable=self.mob_var, fg_color=BORDER, progress_color=BLUE, font=("Segoe UI", 13), text_color=TEXT)
        self.mob_switch.pack(anchor="w", padx=10, pady=4)
        self.interactive_widgets.append(self.mob_switch)

        # Spacer + HW info
        ctk.CTkFrame(frame, fg_color=BORDER, height=1).pack(fill="x", padx=10, pady=12)

        hw_frame = ctk.CTkFrame(frame, fg_color="transparent")
        hw_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.hw_title_lbl = ctk.CTkLabel(hw_frame, text=self._t("hw_title"), font=("Segoe UI", 12, "bold"), text_color=MUTED)
        self.hw_title_lbl.pack(anchor="w")
        self.hw_cores_lbl = ctk.CTkLabel(hw_frame, text=self._t("hw_cores").format(self._hw_cores), font=("Segoe UI", 11), text_color=TEXT)
        self.hw_cores_lbl.pack(anchor="w", pady=(5, 0))
        self.hw_ram_lbl = ctk.CTkLabel(hw_frame, text=self._t("hw_ram").format(self._hw_ram), font=("Segoe UI", 11), text_color=TEXT)
        self.hw_ram_lbl.pack(anchor="w")
        self.hw_threads_lbl = ctk.CTkLabel(hw_frame, text=self._t("hw_threads").format(self._hw_max_threads), font=("Segoe UI", 11), text_color=TEXT)
        self.hw_threads_lbl.pack(anchor="w")
        
        tier_frame = ctk.CTkFrame(hw_frame, fg_color="transparent")
        tier_frame.pack(fill="x", pady=(5, 0))
        self.hw_class_lbl = ctk.CTkLabel(tier_frame, text=self._t("hw_class"), font=("Segoe UI", 11), text_color=TEXT)
        self.hw_class_lbl.pack(side="left")
        self.hw_tier_lbl = ctk.CTkLabel(tier_frame, text=self._t(self._hw_tier_key), font=("Segoe UI", 11, "bold"), text_color=self._hw_tier_color)
        self.hw_tier_lbl.pack(side="left")

    def _add_slider(self, parent, label, from_, to, default, step, attr):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(10, 0))
        lbl = ctk.CTkLabel(row, text=self._t(attr), font=("Segoe UI", 12), text_color=MUTED)
        lbl.pack(side="left")
        setattr(self, f"lbl_{attr}", lbl)

        ctrl = ctk.CTkFrame(row, fg_color="transparent")
        ctrl.pack(side="right")

        is_int = (step >= 1 and from_ >= 1)

        def fmt(v):
            return str(int(v)) if is_int else f"{v:.1f}"

        entry = ctk.CTkEntry(ctrl, width=60, height=28, fg_color=CARD2, border_color=BORDER,
                              text_color=BLUE, font=("Segoe UI", 12, "bold"), justify="center")
        entry.insert(0, fmt(default))

        # ═══════════════════════════════════════════════════════════
        #  ЖЁСТКАЯ ВАЛИДАЦИЯ ВВОДА — МАКСИМАЛЬНАЯ ЗАЩИТА
        # ═══════════════════════════════════════════════════════════

        _last_valid_value = [fmt(default)]  # mutable container for closure

        # 1) Tkinter-level validate — блокирует ввод ЛЮБЫХ нечисловых символов
        inner_entry = entry._entry
        vcmd = (inner_entry.register(lambda action, new_text:
            self._validate_numeric_input(action, new_text, is_int, from_, to)
        ), '%d', '%P')
        inner_entry.configure(validate='key', validatecommand=vcmd)

        # 2) Визуальная обратная связь
        def _set_border_ok():
            entry.configure(border_color=BORDER, text_color=BLUE)
        def _set_border_err():
            entry.configure(border_color=RED, text_color=RED)

        # 3) Анимация тряски при невалидном вводе
        def _shake():
            orig_x = entry.winfo_x()
            for dx in [6, -6, 4, -4, 2, -2, 0]:
                try:
                    entry.place(x=orig_x + dx) if entry.place_info() else None
                except Exception:
                    pass

        # 4) Анимация мигания при clamp (значение было исправлено)
        def _flash_clamp():
            entry.configure(text_color=GOLD)
            entry.after(150, lambda: entry.configure(text_color="#FF6B6B"))
            entry.after(300, lambda: entry.configure(text_color=GOLD))
            entry.after(450, lambda: entry.configure(text_color=BLUE))

        # 5) Полная проверка + clamp при КАЖДОМ изменении
        def _sanitize_and_sync(*_):
            val_str = entry.get().strip()
            if not val_str or val_str == '.':
                _set_border_err()
                return
            try:
                val = float(val_str)
            except ValueError:
                _set_border_err()
                return
            if val < from_ or val > to:
                _set_border_err()
            else:
                _set_border_ok()
                slider.set(val)
                try: slider.update_idletasks()
                except Exception: pass
                _last_valid_value[0] = val_str

        # 6) Жёсткий clamp + восстановление при потере фокуса
        def _on_focus_out(e=None):
            val_str = entry.get().strip()
            # Пустое / мусор → восстанавливаем последнее валидное
            if not val_str or val_str == '.':
                entry.delete(0, "end")
                entry.insert(0, _last_valid_value[0])
                try:
                    slider.set(float(_last_valid_value[0]))
                except ValueError:
                    slider.set(default)
                _set_border_ok()
                _flash_clamp()
                return
            try:
                val = float(val_str)
            except ValueError:
                entry.delete(0, "end")
                entry.insert(0, _last_valid_value[0])
                try:
                    slider.set(float(_last_valid_value[0]))
                except ValueError:
                    slider.set(default)
                _set_border_ok()
                _flash_clamp()
                return
            # Clamp в допустимый диапазон
            clamped = max(from_, min(to, val))
            was_clamped = (clamped != val)
            entry.delete(0, "end")
            entry.insert(0, fmt(clamped))
            slider.set(clamped)
            _last_valid_value[0] = fmt(clamped)
            _set_border_ok()
            if was_clamped:
                _flash_clamp()

        # 7) При фокусе — выделить весь текст для удобства перезаписи
        def _on_focus_in(e):
            pass

        # 8) Блокировка Ctrl+V мусора — перехватываем вставку и чистим
        def _on_paste(e):
            try:
                clipboard = self.clipboard_get()
                cleaned = ''.join(c for c in clipboard if c.isdigit() or (c == '.' and not is_int))
                if not cleaned:
                    return "break"
                current = entry.get()
                try:
                    sel_start = entry.index("sel.first")
                    sel_end = entry.index("sel.last")
                    new_text = current[:sel_start] + cleaned + current[sel_end:]
                except Exception:
                    cursor = entry.index("insert")
                    new_text = current[:cursor] + cleaned + current[cursor:]
                # Проверяем результат
                if new_text.count('.') > 1:
                    return "break"
                try:
                    float(new_text)
                except ValueError:
                    return "break"
                if len(new_text) > 8:
                    return "break"
                entry.delete(0, "end")
                entry.insert(0, new_text)
                _sanitize_and_sync()
            except Exception:
                pass
            return "break"

        # 9) Блокировка ВСЕХ обходных путей ввода мусора
        def _block(e):
            return "break"

        # 10) Скролл колёсиком мыши для изменения значения
        def _on_mousewheel(e):
            if entry == self.focus_get() or inner_entry == self.focus_get():
                delta = step if e.delta > 0 else -step
                update_val(delta)
                return "break"

        # 11) Периодический watchdog — перепроверяет валидность каждые 2 секунды
        def _watchdog():
            try:
                if not entry.winfo_exists():
                    return
                val_str = entry.get().strip()
                if val_str and val_str != '.':
                    try:
                        val = float(val_str)
                        if val < from_ or val > to:
                            _set_border_err()
                        else:
                            _set_border_ok()
                    except ValueError:
                        _set_border_err()
                entry.after(2000, _watchdog)
            except Exception:
                pass
        entry.after(2000, _watchdog)

        def update_val(delta):
            try: cur = float(entry.get())
            except ValueError: cur = float(_last_valid_value[0]) if _last_valid_value[0] not in ('.', '') else default
            new = max(from_, min(to, cur + delta))
            entry.delete(0, "end")
            entry.insert(0, fmt(new))
            slider.set(new)
            try: slider.update_idletasks()
            except Exception: pass
            _last_valid_value[0] = fmt(new)
            _set_border_ok()
            entry.after(10, entry.focus)

        repeat_job = [None]
        def _start_repeat(delta, initial=True):
            update_val(delta)
            def _repeat():
                _start_repeat(delta, initial=False)
            delay = 300 if initial else 50
            repeat_job[0] = entry.after(delay, _repeat)

        def _stop_repeat(*args):
            if repeat_job[0]:
                entry.after_cancel(repeat_job[0])
                repeat_job[0] = None

        btn_minus = ctk.CTkButton(ctrl, text="-", width=28, height=28, fg_color=BORDER, hover_color="#2D3748",
                       font=("Segoe UI", 16, "bold"), text_color="white", corner_radius=6)
        btn_minus.pack(side="left", padx=(0, 4))
        btn_minus.bind("<ButtonPress-1>", lambda e: _start_repeat(-step))
        btn_minus.bind("<ButtonRelease-1>", _stop_repeat)
        btn_minus.bind("<Leave>", _stop_repeat)
        
        entry.pack(side="left")
        
        btn_plus = ctk.CTkButton(ctrl, text="+", width=28, height=28, fg_color=BORDER, hover_color="#2D3748",
                       font=("Segoe UI", 16, "bold"), text_color="white", corner_radius=6)
        btn_plus.pack(side="left", padx=(4, 0))
        btn_plus.bind("<ButtonPress-1>", lambda e: _start_repeat(step))
        btn_plus.bind("<ButtonRelease-1>", _stop_repeat)
        btn_plus.bind("<Leave>", _stop_repeat)

        slider = ctk.CTkSlider(parent, from_=from_, to=to,
                                number_of_steps=max(10, int((to - from_) / step)),
                                fg_color=BORDER, progress_color=BLUE, button_color=BLUE, button_hover_color="#60A5FA")
        slider.set(default)
        slider.pack(fill="x", padx=10, pady=(4, 0))

        def on_slide(v):
            entry.delete(0, "end")
            entry.insert(0, fmt(slider.get()))
            _last_valid_value[0] = fmt(slider.get())
            _set_border_ok()
            if self.focus_get() != entry:
                entry.focus()
        slider.configure(command=on_slide)

        # ═══ ПРИВЯЗКА ВСЕХ СОБЫТИЙ ═══
        entry.bind("<KeyRelease>", _sanitize_and_sync)
        entry.bind("<FocusOut>", _on_focus_out)
        entry.bind("<FocusIn>", _on_focus_in)
        entry.bind("<Control-v>", _on_paste)
        entry.bind("<Control-V>", _on_paste)
        entry.bind("<Shift-Insert>", _on_paste)          # Shift+Insert paste
        entry.bind("<Button-2>", _block)                  # Middle mouse button paste (Linux)
        entry.bind("<Button-3>", _block)                  # Right-click context menu — заблокировано
        entry.bind("<Control-z>", _block)                 # Ctrl+Z undo — может вернуть мусор
        entry.bind("<Control-Z>", _block)
        entry.bind("<Control-y>", _block)                 # Ctrl+Y redo — тоже блокируем
        entry.bind("<Control-Y>", _block)
        entry.bind("<Control-a>", lambda e: entry.select_range(0, "end"))  # Ctrl+A = select all
        entry.bind("<Control-A>", lambda e: entry.select_range(0, "end"))
        entry.bind("<MouseWheel>", _on_mousewheel)        # Скролл колёсиком = ±step
        entry.bind("<Up>", lambda e: update_val(step))
        entry.bind("<Down>", lambda e: update_val(-step))
        entry.bind("<Return>", lambda e: (_on_focus_out(), e.widget.tk_focusNext().focus(), "break")[-1])
        entry.bind("<Escape>", lambda e: (entry.delete(0, "end"), entry.insert(0, _last_valid_value[0]),
                                           _set_border_ok(), self.focus_set(), "break")[-1])

        # 12) Тултип с допустимым диапазоном
        range_text = f"{fmt(from_)} – {fmt(to)}"
        _tip_window = [None]
        def _show_tip(e):
            if _tip_window[0]: return
            x = entry.winfo_rootx() + entry.winfo_width() // 2
            y = entry.winfo_rooty() - 28
            tw = tk.Toplevel(entry)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x-40}+{y}")
            tw.configure(bg="#1E293B")
            tk.Label(tw, text=f"⚡ {range_text}", bg="#1E293B", fg="#94A3B8",
                     font=("Segoe UI", 9), padx=6, pady=2).pack()
            _tip_window[0] = tw
        def _hide_tip(e):
            if _tip_window[0]:
                _tip_window[0].destroy()
                _tip_window[0] = None
        entry.bind("<Enter>", _show_tip)
        entry.bind("<Leave>", _hide_tip)

        setattr(self, f"slider_{attr}", slider)
        setattr(self, f"entry_{attr}", entry)
        self.interactive_widgets.extend([slider, entry])

    def _add_number_input(self, parent, label_text, from_, to, default, step, var):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(5, 0))
        lbl = ctk.CTkLabel(row, text=label_text, font=("Segoe UI", 12), text_color=MUTED)
        lbl.pack(side="left")

        ctrl = ctk.CTkFrame(row, fg_color="transparent")
        ctrl.pack(side="right")

        is_int = (step >= 1 and from_ >= 1)

        def fmt(v):
            return str(int(v)) if is_int else f"{v:.1f}"

        entry = ctk.CTkEntry(ctrl, width=80, height=28, fg_color=CARD2, border_color=BORDER,
                              text_color=BLUE, font=("Segoe UI", 12, "bold"), justify="center")
        entry.insert(0, fmt(default))

        _last_valid_value = [fmt(default)]

        inner_entry = entry._entry
        vcmd = (inner_entry.register(lambda action, new_text:
            self._validate_numeric_input(action, new_text, is_int, from_, to)
        ), '%d', '%P')
        inner_entry.configure(validate='key', validatecommand=vcmd)

        def _set_border_ok():
            entry.configure(border_color=BORDER, text_color=BLUE)
        def _set_border_err():
            entry.configure(border_color=RED, text_color=RED)

        def _shake():
            orig_x = entry.winfo_x()
            for dx in [6, -6, 4, -4, 2, -2, 0]:
                try: entry.place(x=orig_x + dx) if entry.place_info() else None
                except Exception: pass

        def _flash_clamp():
            entry.configure(text_color=GOLD)
            entry.after(150, lambda: entry.configure(text_color="#FF6B6B"))
            entry.after(300, lambda: entry.configure(text_color=GOLD))
            entry.after(450, lambda: entry.configure(text_color=BLUE))

        def _sanitize_and_sync(*_):
            val_str = entry.get().strip()
            if not val_str or val_str == '.':
                _set_border_err()
                return
            try: val = float(val_str)
            except ValueError:
                _set_border_err()
                return
            if val < from_ or val > to:
                _set_border_err()
            else:
                _set_border_ok()
                var.set(fmt(val))
                _last_valid_value[0] = val_str

        def _on_focus_out(e=None):
            val_str = entry.get().strip()
            if not val_str or val_str == '.':
                entry.delete(0, "end")
                entry.insert(0, _last_valid_value[0])
                var.set(_last_valid_value[0])
                _set_border_ok()
                _flash_clamp()
                return
            try: val = float(val_str)
            except ValueError:
                entry.delete(0, "end")
                entry.insert(0, _last_valid_value[0])
                var.set(_last_valid_value[0])
                _set_border_ok()
                _flash_clamp()
                return
            clamped = max(from_, min(to, val))
            was_clamped = (clamped != val)
            entry.delete(0, "end")
            entry.insert(0, fmt(clamped))
            var.set(fmt(clamped))
            _last_valid_value[0] = fmt(clamped)
            _set_border_ok()
            if was_clamped: _flash_clamp()

        def _on_focus_in(e):
            pass

        def _on_paste(e):
            try:
                clipboard = self.clipboard_get()
                cleaned = ''.join(c for c in clipboard if c.isdigit() or (c == '.' and not is_int))
                if not cleaned: return "break"
                current = entry.get()
                try:
                    sel_start = entry.index("sel.first")
                    sel_end = entry.index("sel.last")
                    new_text = current[:sel_start] + cleaned + current[sel_end:]
                except Exception:
                    cursor = entry.index("insert")
                    new_text = current[:cursor] + cleaned + current[cursor:]
                if new_text.count('.') > 1: return "break"
                try: float(new_text)
                except ValueError: return "break"
                if len(new_text) > 8: return "break"
                entry.delete(0, "end")
                entry.insert(0, new_text)
                _sanitize_and_sync()
            except Exception: pass
            return "break"

        def _block(e): return "break"

        def update_val(delta):
            try: cur = float(entry.get())
            except ValueError: cur = float(_last_valid_value[0]) if _last_valid_value[0] not in ('.', '') else default
            new = max(from_, min(to, cur + delta))
            entry.delete(0, "end")
            entry.insert(0, fmt(new))
            var.set(fmt(new))
            _last_valid_value[0] = fmt(new)
            _set_border_ok()
            entry.after(10, entry.focus)

        def _on_mousewheel(e):
            if entry == self.focus_get() or inner_entry == self.focus_get():
                delta = step if e.delta > 0 else -step
                update_val(delta)
                return "break"

        def _watchdog():
            try:
                if not entry.winfo_exists(): return
                val_str = entry.get().strip()
                if val_str and val_str != '.':
                    try:
                        val = float(val_str)
                        if val < from_ or val > to: _set_border_err()
                        else: _set_border_ok()
                    except ValueError: _set_border_err()
                entry.after(2000, _watchdog)
            except Exception: pass
        entry.after(2000, _watchdog)

        repeat_job = [None]
        def _start_repeat(delta, initial=True):
            update_val(delta)
            def _repeat():
                _start_repeat(delta, initial=False)
            delay = 300 if initial else 50
            repeat_job[0] = entry.after(delay, _repeat)

        def _stop_repeat(*args):
            if repeat_job[0]:
                entry.after_cancel(repeat_job[0])
                repeat_job[0] = None

        btn_minus = ctk.CTkButton(ctrl, text="-", width=28, height=28, fg_color=BORDER, hover_color="#2D3748",
                       font=("Segoe UI", 16, "bold"), text_color="white", corner_radius=6)
        btn_minus.pack(side="left", padx=(0, 4))
        btn_minus.bind("<ButtonPress-1>", lambda e: _start_repeat(-step))
        btn_minus.bind("<ButtonRelease-1>", _stop_repeat)
        btn_minus.bind("<Leave>", _stop_repeat)
        
        entry.pack(side="left")
        
        btn_plus = ctk.CTkButton(ctrl, text="+", width=28, height=28, fg_color=BORDER, hover_color="#2D3748",
                       font=("Segoe UI", 16, "bold"), text_color="white", corner_radius=6)
        btn_plus.pack(side="left", padx=(4, 0))
        btn_plus.bind("<ButtonPress-1>", lambda e: _start_repeat(step))
        btn_plus.bind("<ButtonRelease-1>", _stop_repeat)
        btn_plus.bind("<Leave>", _stop_repeat)

        entry.bind("<KeyRelease>", _sanitize_and_sync)
        entry.bind("<FocusOut>", _on_focus_out)
        entry.bind("<FocusIn>", _on_focus_in)
        entry.bind("<Control-v>", _on_paste)
        entry.bind("<Control-V>", _on_paste)
        entry.bind("<Shift-Insert>", _on_paste)
        entry.bind("<Button-2>", _block)
        entry.bind("<Button-3>", _block)
        entry.bind("<Control-z>", _block)
        entry.bind("<Control-Z>", _block)
        entry.bind("<Control-y>", _block)
        entry.bind("<Control-Y>", _block)
        entry.bind("<Control-a>", lambda e: entry.select_range(0, "end"))
        entry.bind("<Control-A>", lambda e: entry.select_range(0, "end"))
        entry.bind("<MouseWheel>", _on_mousewheel)
        entry.bind("<Up>", lambda e: update_val(step))
        entry.bind("<Down>", lambda e: update_val(-step))
        entry.bind("<Return>", lambda e: (_on_focus_out(), e.widget.tk_focusNext().focus(), "break")[-1])
        entry.bind("<Escape>", lambda e: (entry.delete(0, "end"), entry.insert(0, _last_valid_value[0]), _set_border_ok(), self.focus_set(), "break")[-1])

        range_text = f"{fmt(from_)} – {fmt(to)}"
        _tip_window = [None]
        def _show_tip(e):
            if _tip_window[0]: return
            x = entry.winfo_rootx() + entry.winfo_width() // 2
            y = entry.winfo_rooty() - 28
            tw = tk.Toplevel(entry)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x-40}+{y}")
            tw.configure(bg="#1E293B")
            tk.Label(tw, text=f"⚡ {range_text}", bg="#1E293B", fg="#94A3B8", font=("Segoe UI", 9), padx=6, pady=2).pack()
            _tip_window[0] = tw
        def _hide_tip(e):
            if _tip_window[0]: _tip_window[0].destroy(); _tip_window[0] = None
        entry.bind("<Enter>", _show_tip)
        entry.bind("<Leave>", _hide_tip)

        self.interactive_widgets.append(entry)
        return lbl

    @staticmethod
    def _validate_numeric_input(action, new_text, is_int, from_, to):
        """Tkinter validation callback — вызывается ДО каждого изменения текста.
        Возвращает True только если новый текст допустим."""
        # Удаление всегда ок
        if action == '0':
            return True
        # Пустая строка — ок (пользователь стирает)
        if not new_text:
            return True
        # Только одна точка для float-полей
        if new_text == '.' and not is_int:
            return True
        # Проверка посимвольно: только цифры и (для float) одна точка
        dot_count = 0
        for ch in new_text:
            if ch.isdigit():
                continue
            if ch == '.' and not is_int:
                dot_count += 1
                if dot_count > 1:
                    return False
                continue
            # Любой другой символ — блокируем
            return False
        # Не пропускаем ведущие нули (кроме "0" и "0.xxx")
        if len(new_text) > 1 and new_text[0] == '0' and new_text[1] != '.':
            return False
        # Ограничение длины — максимум 8 символов
        if len(new_text) > 8:
            return False
        # Для целых — блокируем точку в любой позиции
        if is_int and '.' in new_text:
            return False
        # Не разрешаем больше 1 цифры после точки для float
        if not is_int and '.' in new_text:
            parts = new_text.split('.')
            if len(parts) == 2 and len(parts[1]) > 1:
                return False
        return True



    # --- Вкладка СТРАНЫ (ленивая загрузка) ---
    def _build_countries_tab(self, parent):
        # Быстрые кнопки
        quick = ctk.CTkFrame(parent, fg_color="transparent")
        quick.pack(fill="x", padx=5, pady=(5, 8))
        self.btn_all = ctk.CTkButton(quick, text=self._t("all"), width=55, height=26, fg_color=GREEN, hover_color="#059669",
                       font=("Segoe UI", 11, "bold"), corner_radius=6, command=self._select_all)
        self.btn_all.pack(side="left", padx=2)
        self.btn_reset = ctk.CTkButton(quick, text=self._t("reset"), width=65, height=26, fg_color=RED, hover_color="#B91C1C",
                       font=("Segoe UI", 11, "bold"), corner_radius=6, command=self._deselect_all)
        self.btn_reset.pack(side="left", padx=2)
        self.btn_europe = ctk.CTkButton(quick, text=self._t("europe"), width=65, height=26, fg_color=BLUE, hover_color="#2563EB",
                       font=("Segoe UI", 11, "bold"), corner_radius=6,
                       command=lambda: self._select_region(list(REGIONS[self.current_lang].keys())[0]))
        self.btn_europe.pack(side="left", padx=2)
        self.btn_tier1 = ctk.CTkButton(quick, text=self._t("tier1"), width=55, height=26, fg_color=GOLD, hover_color="#D97706",
                       font=("Segoe UI", 11, "bold"), corner_radius=6, text_color="#0B0F19",
                       command=self._select_tier1)
        self.btn_tier1.pack(side="left", padx=2)
        self.interactive_widgets.extend([self.btn_all, self.btn_reset, self.btn_europe, self.btn_tier1])
        
        state = "disabled" if getattr(self, "is_running", False) else "normal"
        self.btn_all.configure(state=state)
        self.btn_reset.configure(state=state)
        self.btn_europe.configure(state=state)
        self.btn_tier1.configure(state=state)

        self.country_count_label = ctk.CTkLabel(quick, text="0", font=("Segoe UI", 11, "bold"), text_color=BLUE)
        self.country_count_label.pack(side="right", padx=5)
        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(0, 8))

        self.tab_country_search = ctk.CTkEntry(search_frame, placeholder_text=self._t("search"), height=28)
        self.tab_country_search.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.tab_country_search.bind("<KeyRelease>", self._filter_countries_tab)

        def clear_search():
            self.tab_country_search.delete(0, "end")
            self._filter_countries_tab()

        self.btn_clear_search = ctk.CTkButton(search_frame, text="✕", width=28, height=28, 
                                            fg_color=BORDER, hover_color="#374151",
                                            font=("Segoe UI", 12, "bold"), corner_radius=6,
                                            command=clear_search)
        self.btn_clear_search.pack(side="right")

        self._region_frames = {}
        self._country_cbs = {}

        # CTkScrollableFrame ТОЛЬКО для списка стран — единственное место с реальным скроллом
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True)

        # Собираем все данные для пакетной загрузки
        self._pending_regions = list(REGIONS[self.current_lang].items())
        self._country_scroll = scroll
        self._load_next_region()

    def _load_next_region(self):
        """Загружаем по одному региону за кадр — нет фризов"""
        try:
            if not self._pending_regions:
                if hasattr(self, "_old_country_state") and self._old_country_state:
                    for iso, val in self._old_country_state.items():
                        if iso in self.country_vars: self.country_vars[iso].set(val)
                    self._update_count()
                    self._old_country_state = None
                return

            region_name, countries = self._pending_regions.pop(0)

            hdr = ctk.CTkFrame(self._country_scroll, fg_color=BORDER, corner_radius=8)
            hdr.pack(fill="x", padx=4, pady=(6, 3))
            ctk.CTkLabel(hdr, text=f"{region_name}  ({len(countries)})", font=("Segoe UI", 12, "bold"),
                          text_color="white").pack(side="left", padx=10, pady=4)
            btn_all = ctk.CTkButton(hdr, text=self._t("all_short"), width=36, height=20, fg_color=BLUE, hover_color="#2563EB",
                           font=("Segoe UI", 10), corner_radius=4,
                           command=lambda rn=region_name: self._select_region(rn))
            btn_all.pack(side="right", padx=5, pady=3)
            self.interactive_widgets.append(btn_all)
            self._region_btns.append(btn_all)
            
            btn_reset = ctk.CTkButton(hdr, text=self._t("reset_short"), width=36, height=20, fg_color=RED, hover_color="#B91C1C",
                           font=("Segoe UI", 10), corner_radius=4,
                           command=lambda rn=region_name: self._deselect_region(rn))
            btn_reset.pack(side="right", padx=5, pady=3)
            self.interactive_widgets.append(btn_reset)
            self._region_reset_btns.append(btn_reset)
            
            state = "disabled" if getattr(self, "is_running", False) else "normal"
            btn_all.configure(state=state)
            btn_reset.configure(state=state)

            grid = ctk.CTkFrame(self._country_scroll, fg_color="transparent")
            grid.pack(fill="x", padx=4, pady=(0, 2))

            self._region_frames[region_name] = (hdr, grid)

            # Фиксированная сетка в 2 колонки (боковая панель 450px — всегда 2 колонки)
            FIXED_COLS = 2
            grid.grid_columnconfigure(0, weight=1)
            grid.grid_columnconfigure(1, weight=1)

            for idx, (iso, name) in enumerate(sorted(countries.items(), key=lambda x: x[1])):
                var = ctk.BooleanVar(value=False)
                self.country_vars[iso] = var
                cb = ctk.CTkCheckBox(grid, text=f"{name} ({iso})", variable=var,
                                 fg_color=BORDER, hover_color="#2D3748", checkmark_color="white",
                                 border_color=BORDER, font=("Segoe UI", 11), text_color=TEXT,
                                 command=self._update_count, width=130)
                self.interactive_widgets.append(cb)
                cb.configure(state=state)
                cb.grid(row=idx // FIXED_COLS, column=idx % FIXED_COLS, sticky="w", padx=4, pady=2)
                
                self._country_cbs[iso] = (cb, region_name)

            # Планируем загрузку следующего региона через 10мс
            if self._pending_regions:
                self.after(10, self._load_next_region)
            else:
                # Добавляем пустой отступ внизу, чтобы последний ряд не прилипал к краю и скролл работал корректно
                self._country_scroll_pad = ctk.CTkFrame(self._country_scroll, fg_color="transparent", height=30)
                self._country_scroll_pad.pack(fill="x")
                
                if hasattr(self, "_old_country_state") and self._old_country_state:
                    for iso, val in self._old_country_state.items():
                        if iso in self.country_vars: self.country_vars[iso].set(val)
                    self._update_count()
                    self._old_country_state = None
        except Exception as e:
            print(f"Error loading region: {e}")

    def _filter_countries_tab(self, *args):
        query = self.tab_country_search.get().lower()
        
        for region_name, (hdr, grid) in self._region_frames.items():
            hdr.pack_forget()
            grid.pack_forget()
        
        if hasattr(self, "_country_scroll_pad") and self._country_scroll_pad.winfo_exists():
            self._country_scroll_pad.pack_forget()

        for region_name, (hdr, grid) in self._region_frames.items():
            if region_name not in REGIONS[self.current_lang]: continue
            
            countries = REGIONS[self.current_lang][region_name]
            visible_count = 0
            
            for iso, name in sorted(countries.items(), key=lambda x: x[1]):
                if iso not in self._country_cbs: continue
                cb, _ = self._country_cbs[iso]
                
                translations = [iso.lower()]
                if iso in ISO_TO_NAME.get("EN", {}):
                    translations.append(ISO_TO_NAME["EN"][iso].lower())
                if iso in ISO_TO_NAME.get("RU", {}):
                    translations.append(ISO_TO_NAME["RU"][iso].lower())
                    
                if any(query in t for t in translations):
                    cb.grid(row=visible_count // 2, column=visible_count % 2, sticky="w", padx=4, pady=2)
                    visible_count += 1
                else:
                    cb.grid_remove()
                    
            if visible_count > 0:
                hdr.pack(fill="x", padx=4, pady=(6, 3))
                grid.pack(fill="x", padx=4, pady=(0, 2))
                
        if hasattr(self, "_country_scroll_pad") and self._country_scroll_pad.winfo_exists():
            self._country_scroll_pad.pack(fill="x")

    def _update_count(self):
        count = sum(1 for v in self.country_vars.values() if v.get())
        self.country_count_label.configure(text=str(count))

    def _select_all(self):
        """Select all countries EXCEPT user's own country"""
        for iso, v in self.country_vars.items():
            v.set(iso != self._my_country)
        self._update_count()

    def _deselect_all(self):
        for v in self.country_vars.values(): v.set(False)
        self._update_count()

    def _select_region(self, region_name):
        """ADD all countries from a region to current selection (not reset)"""
        if region_name in REGIONS[self.current_lang]:
            for iso in REGIONS[self.current_lang][region_name]:
                if iso in self.country_vars and iso != self._my_country:
                    self.country_vars[iso].set(True)
        self._update_count()

    def _deselect_region(self, region_name):
        """Deselect all countries from a specific region"""
        if region_name in REGIONS[self.current_lang]:
            for iso in REGIONS[self.current_lang][region_name]:
                if iso in self.country_vars:
                    self.country_vars[iso].set(False)
        self._update_count()

    def _select_tier1(self):
        self._deselect_all()
        for iso in ["US", "CA", "GB", "DE", "FR", "AU", "NL", "SE", "NO", "CH", "DK", "FI", "AT", "NZ", "IE", "BE"]:
            if iso in self.country_vars and iso != self._my_country:
                self.country_vars[iso].set(True)
        self._update_count()

    def _get_selected_countries(self):
        # Строгая валидация: возвращаем только реально выбранные страны
        return [iso for iso, var in self.country_vars.items() if var.get()]

    def _detect_my_country(self):
        """Detect user's country via IP geolocation (fast, one-shot)"""
        try:
            import requests
            r = requests.get('https://ipapi.co/country_code/', timeout=3)
            if r.status_code == 200:
                code = r.text.strip().upper()
                if len(code) == 2:
                    return code
        except Exception:
            pass
        # Fallback: try to detect from system locale
        try:
            import locale
            loc = locale.getlocale()[0]  # e.g. 'ru_RU'
            if loc and '_' in loc:
                return loc.split('_')[1].upper()
        except Exception:
            pass
        return None

    def _build_proxies_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True)
        
        # Auto-hide scrollbar logic
        def _do_check():
            if not hasattr(scroll, "_scrollbar"): return
            try:
                bbox = scroll._parent_canvas.bbox("all")
                content_height = (bbox[3] - bbox[1]) if bbox else scroll._parent_frame.winfo_reqheight()
                canvas_height = scroll._parent_canvas.winfo_height()
                if content_height > canvas_height and canvas_height > 10:
                    scroll._scrollbar.grid()
                else:
                    scroll._scrollbar.grid_remove()
            except Exception:
                pass

        def _check_scroll_size(e=None):
            if hasattr(scroll, "after"):
                scroll.after(50, _do_check)
                
        scroll._parent_canvas.bind("<Configure>", _check_scroll_size, add="+")
        if hasattr(scroll, "_parent_frame"):
            scroll._parent_frame.bind("<Configure>", _check_scroll_size, add="+")
        
        self.random_title_lbl = ctk.CTkLabel(scroll, text=self._t("random_title"), font=("Segoe UI", 13, "bold"), text_color=GOLD)
        self.random_title_lbl.pack(anchor="w", padx=10, pady=(0, 10))
        
        self.random_gen_enabled = ctk.BooleanVar(value=False)
        self.random_en_switch = ctk.CTkSwitch(scroll, text=self._t("random_enable"), variable=self.random_gen_enabled, fg_color=BORDER, progress_color=GOLD, font=("Segoe UI", 12, "bold"))
        self.random_en_switch.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Настройки количества с мощной валидацией
        self.random_counts = {"http": ctk.StringVar(value="5000000"), "socks4": ctk.StringVar(value="5000000"), "socks5": ctk.StringVar(value="5000000")}
        
        for proto in ["http", "socks4", "socks5"]:
            lbl = self._add_number_input(
                parent=scroll,
                label_text=f'{self._t("random_count")} {proto.upper()}',
                from_=1,
                to=99999999,
                default=5000000,
                step=100000,
                var=self.random_counts[proto]
            )
            setattr(self, f"lbl_random_{proto}", lbl)
        
    def _clear_proxy_placeholder(self):
        if self.proxy_text.get("0.0", "end-1c").strip() == self._t("proxy_placeholder").strip():
            self.proxy_text.delete("0.0", "end")
            
    def _restore_proxy_placeholder(self):
        if not self.proxy_text.get("0.0", "end-1c").strip():
            self.proxy_text.insert("0.0", self._t("proxy_placeholder"))

    def _update_chain_count(self, event=None):
        proxies = self._parse_chain_proxies(silent=True)
        self._parsed_chain_count = len(proxies)
        if hasattr(self, "proxy_lbl_loaded"):
            self.proxy_lbl_loaded.configure(text=self._t("proxy_loaded").format(self._parsed_chain_count))

    def _load_chain_proxies(self):
        path = fd.askopenfilename(filetypes=[("Text files", "*.txt")], title=self._t("dialog_load_proxy"))
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if self.proxy_text.get("0.0", "end-1c").strip() == self._t("proxy_placeholder").strip():
                self.proxy_text.delete("0.0", "end")
            self.proxy_text.insert("end", content + "\n")
            self._update_chain_count()
        except Exception as e:
            pass

    def _parse_chain_proxies(self, silent=False) -> list:
        content = self.proxy_text.get("0.0", "end")
        from fetch_proxy import ProxyUtils
        import re
        URI_RE = re.compile(r'(?:http|https|socks4|socks5|socks5h)://\S+', re.IGNORECASE)
        found = URI_RE.findall(content)
        PLAIN_RE = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3})[:\s,;|"\']+(\d{1,5})\b')
        for ip, port in PLAIN_RE.findall(content):
            if ProxyUtils.is_valid(ip, int(port)):
                found.append(f"http://{ip}:{port}")
        
        valid = []
        for uri in found:
            ptype, pip, pport = ProxyUtils._parse_proxy_uri(uri)
            if pip and ProxyUtils.is_valid(pip, int(pport)):
                valid.append(uri.lower())
                
        return list(set(valid))

    # ===================== MAIN PANEL =====================
    def _build_main(self):
        self.main_panel = ctk.CTkFrame(self.root_frame, fg_color="transparent")
        self.main_panel.grid(row=0, column=1, padx=(8, 15), pady=15, sticky="nsew")
        self.main_panel.grid_rowconfigure(3, weight=1)
        self.main_panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        logo = ctk.CTkFrame(header, fg_color="transparent")
        logo.pack(side="left")
        shield = ctk.CTkFrame(logo, fg_color=BLUE, corner_radius=12, width=44, height=44)
        shield.pack(side="left", padx=(0, 12))
        shield.pack_propagate(False)
        ctk.CTkLabel(shield, text="", image=self.icons["shield"]).pack(expand=True)
        titles = ctk.CTkFrame(logo, fg_color="transparent")
        titles.pack(side="left")
        ctk.CTkLabel(titles, text="PROXY HUNTER", font=("Segoe UI", 22, "bold"), text_color="white").pack(anchor="w")
        self.subtitle_lbl = ctk.CTkLabel(titles, text=self._t("subtitle"), font=("Segoe UI", 11), text_color="#475569")
        self.subtitle_lbl.pack(anchor="w")

        self.btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        self.btn_frame.pack(side="right")
        
        self.pause_btn = ctk.CTkButton(self.btn_frame, text=self._t("pause"), image=self.icons["pause"], font=("Segoe UI", 14, "bold"),
                                        fg_color=GOLD, hover_color="#D97706", corner_radius=12,
                                        width=110, height=48, command=self._toggle_pause, state="disabled")
        self.pause_btn.pack(side="left", padx=(0, 10))

        self.cancel_btn = ctk.CTkButton(self.btn_frame, text=self._t("cancel"), image=self.icons["cancel"], font=("Segoe UI", 14, "bold"),
                                        fg_color=RED, hover_color="#B91C1C", corner_radius=12,
                                        width=110, height=48, command=self._cancel_hunter, state="disabled")
        self.cancel_btn.pack(side="left", padx=(0, 10))

        self.start_btn = ctk.CTkButton(self.btn_frame, text=self._t("start"), image=self.icons["play"], font=("Segoe UI", 14, "bold"),
                                        fg_color=BLUE, hover_color="#2563EB", corner_radius=12,
                                        width=190, height=48, command=self._run_hunter)
        self.start_btn.pack(side="left")

        stats = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        stats.grid_columnconfigure((0, 1, 2), weight=1, uniform="stats_cards")
        stats.grid_rowconfigure((0, 1), weight=1)
        self.stat_total, self.lbl_stat_total = self._card(stats, self._t("total"), BLUE, "🌐", 0, 0)
        self.stat_live, self.lbl_stat_live = self._card(stats, self._t("live"), GREEN, "⚡", 0, 1)
        self.stat_elite, self.lbl_stat_elite = self._card(stats, self._t("elite"), GOLD, "⭐", 0, 2)
        self.stat_dc, self.lbl_stat_dc = self._card(stats, self._t("source_datacenter"), BLUE, "🏢", 1, 0)
        self.stat_res, self.lbl_stat_res = self._card(stats, self._t("source_residential"), GREEN, "🏠", 1, 1)
        self.stat_mob, self.lbl_stat_mob = self._card(stats, self._t("source_mobile"), GOLD, "📱", 1, 2)

        # --- PROGRESS BAR ---
        prog_frame = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        prog_frame.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        self.progress_lbl = ctk.CTkLabel(prog_frame, text=self._t("wait"), font=("Segoe UI", 12), text_color=MUTED)
        self.progress_lbl.pack(side="left", padx=(5, 10))
        self.progress_bar = ctk.CTkProgressBar(prog_frame, fg_color=BORDER, progress_color=BLUE, height=12)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=5)
        self.progress_pct = ctk.CTkLabel(prog_frame, text="0%", font=("Segoe UI", 12, "bold"), text_color=BLUE, width=40, anchor="e")
        self.progress_pct.pack(side="right", padx=(10, 5))

        # Табы: Терминал / Результаты
        self.main_tabs = ctk.CTkTabview(self.main_panel, fg_color=CARD2, segmented_button_fg_color=BORDER,
                                         segmented_button_selected_color=BLUE, segmented_button_unselected_color=CARD,
                                         corner_radius=14, border_width=1, border_color=BORDER,
                                         command=self._on_main_tab_change)
        self.main_tabs.grid(row=3, column=0, sticky="nsew")

        tab_terminal = self.main_tabs.add("Терминал")
        tab_results = self.main_tabs.add("Результаты")
        tab_checker = self.main_tabs.add("Проверка")

        self._build_terminal_tab(tab_terminal)
        self._build_results_tab(tab_results)
        self._build_checker_tab(tab_checker)
        
        try:
            for k in ["Терминал", "Terminal"]:
                try:
                    self.main_tabs.set(k)
                    break
                except ValueError:
                    pass
        except: pass

    def _on_main_tab_change(self):
        if self.main_tabs.get() in ["Результаты", "Results"]:
            self._load_results()


    def _build_terminal_tab(self, parent):
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.pack(fill="x", pady=(0, 5))
        self.btn_copy_term = ctk.CTkButton(top, text=self._t("copy_terminal"), image=self.icons["clipboard"], width=160, height=28, fg_color=BLUE, hover_color="#2563EB", command=self._copy_terminal)
        self.btn_copy_term.pack(side="right", padx=5)

        self.terminal = ctk.CTkTextbox(parent, fg_color="#060B14", corner_radius=10, border_width=1, border_color=BORDER,
                                        font=("Consolas", 12), text_color="#94A3B8", state="normal",
                                        activate_scrollbars=True, wrap="word")
        self.terminal.pack(fill="both", expand=True)
        self.terminal._textbox.tag_config("blue", foreground=BLUE)
        self.terminal._textbox.tag_config("green", foreground=GREEN)
        self.terminal._textbox.tag_config("red", foreground=RED)
        self.terminal._textbox.tag_config("purple", foreground="#A855F7")
        self.terminal._textbox.tag_config("default", foreground="#94A3B8")
        
        self.terminal_empty_lbl = ctk.CTkLabel(self.terminal, text=self._t("terminal_empty"), font=("Consolas", 14), text_color=MUTED)
        self.terminal_empty_lbl.place(relx=0.5, rely=0.5, anchor="center")
        
        self.terminal.configure(state="disabled")

    def _copy_terminal(self):
        text = self.terminal.get("1.0", "end-1c").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.btn_copy_term.configure(text=self._t("copied_terminal"), fg_color=GREEN)
            self.after(2000, lambda: self.btn_copy_term.configure(text=self._t("copy_terminal"), image=self.icons["clipboard"], fg_color=BLUE))

    def _build_results_tab(self, parent):
        # Панель управления
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.pack(fill="x", pady=(5, 8))

        # Переключатель Live / Elite
        self.result_source = ctk.StringVar(value="live")
        self.source_seg = ctk.CTkSegmentedButton(toolbar, values=["Live", "Elite", "Datacenter", "Residential", "Mobile"], variable=self.result_source,
                                fg_color=BORDER, selected_color=BLUE, unselected_color=CARD,
                                font=("Segoe UI", 12, "bold"),
                                command=lambda v: self._load_results())
        self.source_seg.pack(side="left", padx=(5, 10))

        # Динамические фильтры (Кнопки с выпадающим окном)
        self.selected_protos = set()
        self.selected_countries = set()
        self.all_protos_in_db = set()
        self.all_countries_in_db = set()
        
        self.btn_proto_filter = ctk.CTkButton(toolbar, text=self._t("all_protocols"), width=140, fg_color=BORDER, hover_color="#4A5568", command=self._on_proto_btn_click)
        self.btn_proto_filter.pack(side="left", padx=5)

        self.btn_country_filter = ctk.CTkButton(toolbar, text=self._t("all_countries_filter"), width=140, fg_color=BORDER, hover_color="#4A5568", command=self._on_country_btn_click)
        self.btn_country_filter.pack(side="left", padx=5)

        # Счётчик
        self.result_count_lbl = ctk.CTkLabel(toolbar, text=self._t("proxies_count").format(0), font=("Segoe UI", 12, "bold"), text_color=MUTED)
        self.result_count_lbl.pack(side="left", padx=10)

        # Кнопки
        self.btn_copy = ctk.CTkButton(toolbar, text=self._t("copy"), width=110, height=30, fg_color=BLUE, hover_color="#2563EB",
                       font=("Segoe UI", 11, "bold"), corner_radius=8, command=self._copy_results)
        self.btn_copy.pack(side="right", padx=5)
        self.btn_refresh = ctk.CTkButton(toolbar, text=self._t("refresh"), width=100, height=30, fg_color=BORDER, hover_color="#2D3748",
                       font=("Segoe UI", 11, "bold"), corner_radius=8, command=self._load_results)
        self.btn_refresh.pack(side="right", padx=5)

        # Панель Экспорта
        export_toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        export_toolbar.pack(fill="x", pady=(0, 8))
        
        self.lbl_download = ctk.CTkLabel(export_toolbar, text=self._t("download"), font=("Segoe UI", 12, "bold"), text_color=MUTED)
        self.lbl_download.pack(side="left", padx=(5, 10))
        self.btn_csv = ctk.CTkButton(export_toolbar, text=self._t("csv"), width=120, height=28, fg_color="#059669", hover_color="#047857",
                       font=("Segoe UI", 11, "bold"), corner_radius=6, command=self._export_csv)
        self.btn_csv.pack(side="left", padx=5)
        self.btn_txt_proto = ctk.CTkButton(export_toolbar, text=self._t("txt_proto"), width=180, height=28, fg_color="#0EA5E9", hover_color="#0284C7",
                       font=("Segoe UI", 11, "bold"), corner_radius=6, command=self._export_txt_proto)
        self.btn_txt_proto.pack(side="left", padx=5)
        self.btn_txt1 = ctk.CTkButton(export_toolbar, text=self._t("txt1"), width=120, height=28, fg_color="#4F46E5", hover_color="#4338CA",
                       font=("Segoe UI", 11, "bold"), corner_radius=6, command=self._export_txt_full)
        self.btn_txt1.pack(side="left", padx=5)
        self.btn_txt2 = ctk.CTkButton(export_toolbar, text=self._t("txt2"), width=120, height=28, fg_color="#D97706", hover_color="#B45309",
                       font=("Segoe UI", 11, "bold"), corner_radius=6, command=self._export_txt_ip)
        self.btn_txt2.pack(side="left", padx=5)

        # Панель Копирования
        copy_toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        copy_toolbar.pack(fill="x", pady=(0, 8))
        
        self.lbl_copy_sec = ctk.CTkLabel(copy_toolbar, text=self._t("copy_lbl") if hasattr(self, "_t") else "📋 Copy:", font=("Segoe UI", 12, "bold"), text_color=MUTED)
        self.lbl_copy_sec.pack(side="left", padx=(5, 10))
        self.btn_copy_txt_proto = ctk.CTkButton(copy_toolbar, text=self._t("txt_proto"), width=180, height=28, fg_color="#0EA5E9", hover_color="#0284C7",
                       font=("Segoe UI", 11, "bold"), corner_radius=6, command=self._copy_txt_proto_all)
        self.btn_copy_txt_proto.pack(side="left", padx=5)
        self.btn_copy_txt1 = ctk.CTkButton(copy_toolbar, text=self._t("txt1"), width=120, height=28, fg_color="#4F46E5", hover_color="#4338CA",
                       font=("Segoe UI", 11, "bold"), corner_radius=6, command=self._copy_txt_full_all)
        self.btn_copy_txt1.pack(side="left", padx=5)
        self.btn_copy_txt2 = ctk.CTkButton(copy_toolbar, text=self._t("txt2"), width=120, height=28, fg_color="#D97706", hover_color="#B45309",
                       font=("Segoe UI", 11, "bold"), corner_radius=6, command=self._copy_txt_ip_all)
        self.btn_copy_txt2.pack(side="left", padx=5)

        # Таблица результатов (Treeview)
        tree_frame = ctk.CTkFrame(parent, fg_color="#060B14", corner_radius=10, border_width=0)
        tree_frame.pack(fill="both", expand=True, pady=(0, 5))

        style = tk.ttk.Style()
        style.theme_use("clam")
        style.configure("Proxy.Treeview", background="#060B14", foreground=TEXT, fieldbackground="#060B14",
                         font=("Consolas", 11), rowheight=26, borderwidth=0, relief="flat")
        style.layout("Proxy.Treeview", [("Proxy.Treeview.treearea", {"sticky": "nswe"})])
        style.configure("Proxy.Treeview.Heading", background=CARD, foreground="white",
                         font=("Segoe UI", 11, "bold"), borderwidth=0, relief="flat")
        style.map("Proxy.Treeview", background=[("selected", BLUE)], foreground=[("selected", "white")])
        style.map("Proxy.Treeview.Heading", background=[("active", BORDER)])

        cols = ("proto", "ip", "port", "country")
        self.proxy_tree = tk.ttk.Treeview(tree_frame, columns=cols, show="headings", style="Proxy.Treeview", selectmode="extended")
        self.proxy_tree.heading("proto", text=self._t("proto"))
        self.proxy_tree.heading("ip", text=self._t("ip"))
        self.proxy_tree.heading("port", text=self._t("port"))
        self.proxy_tree.heading("country", text=self._t("country"))
        self.proxy_tree.column("proto", width=90, minwidth=70, anchor="center")
        self.proxy_tree.column("ip", width=180, minwidth=120, anchor="center")
        self.proxy_tree.column("port", width=70, minwidth=50, anchor="center")
        self.proxy_tree.column("country", width=120, minwidth=80, anchor="center")

        scrollbar = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.proxy_tree.yview, fg_color="#060B14", button_color=BORDER, button_hover_color=MUTED)
        self.proxy_tree.configure(yscrollcommand=scrollbar.set)
        self.proxy_tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", pady=8, padx=(0, 4))
        
        self.results_empty_lbl = ctk.CTkLabel(self.proxy_tree, text=self._t("no_data"), font=("Consolas", 14), text_color=MUTED, bg_color="#060B14")
        self.results_empty_lbl.place(relx=0.5, rely=0.5, anchor="center")

    def _load_results(self):
        """Загрузка сырых данных в память и обновление фильтров"""
        source = self.result_source.get()
        v = source.lower()
        if v in ("live", self._t("source_live").lower()): mapped_src = "live"
        elif v in ("elite", self._t("source_elite").lower()): mapped_src = "elite"
        elif v in ("datacenter", self._t("source_datacenter").lower()): mapped_src = "datacenter"
        elif v in ("residential", self._t("source_residential").lower()): mapped_src = "residential"
        elif v in ("mobile", self._t("source_mobile").lower()): mapped_src = "mobile"
        else: mapped_src = "elite"
        
        self._current_raw_data = []
        protos, countries = set(), set()
        self.proto_counts = {}
        self.country_counts = {}

        if self.is_running and hasattr(self, "realtime_proxies"):
            data_list = self.realtime_proxies.get(mapped_src, [])
            for data in data_list:
                c_name = ISO_TO_NAME[self.current_lang].get(data["country"], data["country"])
                p_name = data["protocol"].upper()
                self._current_raw_data.append((p_name, data["ip"], data["port"], c_name))
                protos.add(p_name)
                countries.add(c_name)
                self.proto_counts[p_name] = self.proto_counts.get(p_name, 0) + 1
                self.country_counts[c_name] = self.country_counts.get(c_name, 0) + 1
        else:
            folder = f"results_{mapped_src}"
            csv_file = os.path.join(folder, "all.csv")
            if os.path.exists(csv_file):
                try:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        next(reader)
                        for row in reader:
                            if len(row) >= 4:
                                c_name = ISO_TO_NAME[self.current_lang].get(row[3], row[3])
                                p_name = row[0].upper()
                                self._current_raw_data.append((p_name, row[1], row[2], c_name))
                                protos.add(p_name)
                                countries.add(c_name)
                                self.proto_counts[p_name] = self.proto_counts.get(p_name, 0) + 1
                                self.country_counts[c_name] = self.country_counts.get(c_name, 0) + 1
                except Exception:
                    pass

        self.all_protos_in_db = protos
        self.all_countries_in_db = countries
        
        # Translate selected countries to the current language to prevent resetting on language switch
        new_selected = set()
        for c in self.selected_countries:
            iso_code = c
            for lang, mapping in ISO_TO_NAME.items():
                for k, v in mapping.items():
                    if v == c:
                        iso_code = k
                        break
            new_selected.add(ISO_TO_NAME[self.current_lang].get(iso_code, iso_code))
        self.selected_countries = new_selected
        active_protos = {p for p in self.selected_protos if p in protos}
        active_countries = {c for c in self.selected_countries if c in countries}
        
        if not self.selected_protos or len(active_protos) == len(protos):
            self.btn_proto_filter.configure(text=self._t("all_protocols"))
        else:
            self.btn_proto_filter.configure(text=self._t("protocols_n").format(len(active_protos)))
            
        if not self.selected_countries or len(active_countries) == len(countries):
            self.btn_country_filter.configure(text=self._t("all_countries_filter"))
        else:
            self.btn_country_filter.configure(text=self._t("countries_n").format(len(active_countries)))
        
        self._apply_filters()

    def _create_floating_menu(self, btn_widget, items, selected_set, on_apply, counts=None):
        if hasattr(self, "_active_menu") and self._active_menu:
            self._active_menu.destroy()
            if hasattr(self, "_active_menu_bind") and self._active_menu_bind:
                try:
                    self.unbind("<Button-1>", self._active_menu_bind)
                except Exception: pass
            self._active_menu = None
            
        # Родитель кнопки это toolbar. Его родитель это вкладка results_tab.
        results_tab = btn_widget.master.master
        menu_frame = ctk.CTkFrame(results_tab, fg_color=CARD2, corner_radius=8, border_width=1, border_color=BORDER)
        self._active_menu = menu_frame
        
        # Решение проблемы сдвига при масштабировании экрана (DPI) в Windows.
        # winfo_x() возвращает физические пиксели, а place() ждет логические.
        # Поэтому делим физические координаты на масштаб CustomTkinter.
        scale = ctk.ScalingTracker.get_widget_scaling(btn_widget)
        
        phys_x = btn_widget.winfo_x() + btn_widget.master.winfo_x()
        phys_y = btn_widget.winfo_y() + btn_widget.master.winfo_y() + btn_widget.winfo_height() + int(5 * scale)
        
        logic_x = phys_x / scale
        logic_y = phys_y / scale
        
        menu_frame.place(x=logic_x, y=logic_y)
        menu_frame.lift()
        
        search_entry = ctk.CTkEntry(menu_frame, placeholder_text=self._t("search"), height=28)
        search_entry.pack(fill="x", padx=5, pady=(5, 0))

        scroll = ctk.CTkScrollableFrame(menu_frame, fg_color="transparent", width=180, height=min(200, max(50, len(items)*30)))
        scroll.pack(padx=5, pady=5)
        
        check_vars = {}
        cb_widgets = {}
        for item in sorted(items):
            var = ctk.BooleanVar(value=(item in selected_set))
            
            display_text = f"{item} ({counts[item]})" if counts and item in counts else item
            
            cb = ctk.CTkCheckBox(scroll, text=display_text, variable=var, font=("Segoe UI", 11), 
                                 checkbox_width=20, checkbox_height=20, corner_radius=4)
            cb.pack(anchor="w", pady=4, padx=2)
            check_vars[item] = var
            cb_widgets[item] = cb
            
        def filter_items(*args):
            query = search_entry.get().lower()
            for item, cb in cb_widgets.items():
                iso_code = item
                for lang, mapping in ISO_TO_NAME.items():
                    for k, v in mapping.items():
                        if v == item:
                            iso_code = k
                            break
                
                translations = [item.lower()]
                if iso_code in ISO_TO_NAME.get("EN", {}):
                    translations.append(ISO_TO_NAME["EN"][iso_code].lower())
                if iso_code in ISO_TO_NAME.get("RU", {}):
                    translations.append(ISO_TO_NAME["RU"][iso_code].lower())
                
                if any(query in t for t in translations):
                    cb.pack(anchor="w", pady=4, padx=2)
                else:
                    cb.pack_forget()
                    
        search_entry.bind("<KeyRelease>", filter_items)
            
        def apply():
            selected_set.clear()
            for item, var in check_vars.items():
                if var.get():
                    selected_set.add(item)
            on_apply()
            
            menu_frame.destroy()
            self._active_menu = None
            if hasattr(self, "_active_menu_bind") and self._active_menu_bind:
                try:
                    self.unbind("<Button-1>", self._active_menu_bind)
                except Exception: pass
            
        btn = ctk.CTkButton(menu_frame, text=self._t("apply_filter"), fg_color=BLUE, hover_color="#2563EB", height=28, command=apply)
        btn.pack(fill="x", padx=5, pady=(0, 5))
        
        def reset():
            selected_set.clear()
            on_apply()
            menu_frame.destroy()
            self._active_menu = None
            if hasattr(self, "_active_menu_bind") and self._active_menu_bind:
                try:
                    self.unbind("<Button-1>", self._active_menu_bind)
                except Exception: pass
                
        btn_reset = ctk.CTkButton(menu_frame, text=self._t("reset_filter") if hasattr(self, "_t") else "Reset Filter", fg_color=BORDER, hover_color="#4A5568", height=28, command=reset)
        btn_reset.pack(fill="x", padx=5, pady=(0, 5))
        
        def on_click(e):
            if not self._active_menu: return
            try:
                x_root, y_root = e.x_root, e.y_root
                clicked_widget = self.winfo_containing(x_root, y_root)
                
                # Проверяем, находится ли кликнутый виджет ВНУТРИ нашего меню или это сама кнопка
                is_inside = False
                w = clicked_widget
                while w:
                    if w == menu_frame or w == btn_widget:
                        is_inside = True
                        break
                    parent_str = w.winfo_parent()
                    if not parent_str:
                        break
                    w = w._nametowidget(parent_str)
                    
                if is_inside:
                    return
                
                menu_frame.destroy()
                self._active_menu = None
                if hasattr(self, "_active_menu_bind") and self._active_menu_bind:
                    self.unbind("<Button-1>", self._active_menu_bind)
            except Exception: pass
            
        self._active_menu_bind = self.bind("<Button-1>", on_click, add="+")

    def _on_proto_btn_click(self):
        if not self.all_protos_in_db: return
        self._create_floating_menu(self.btn_proto_filter, self.all_protos_in_db, self.selected_protos, self._on_proto_apply, counts=getattr(self, "proto_counts", {}))
        
    def _on_country_btn_click(self):
        if not self.all_countries_in_db: return
        self._create_floating_menu(self.btn_country_filter, self.all_countries_in_db, self.selected_countries, self._on_country_apply, counts=getattr(self, "country_counts", {}))

    def _on_proto_apply(self):
        active_protos = {p for p in self.selected_protos if p in self.all_protos_in_db}
        if not self.selected_protos or len(active_protos) == len(self.all_protos_in_db):
            self.btn_proto_filter.configure(text=self._t("all_protocols"))
        else:
            self.btn_proto_filter.configure(text=self._t("protocols_n").format(len(active_protos)))
        self._apply_filters()

    def _on_country_apply(self):
        active_countries = {c for c in self.selected_countries if c in self.all_countries_in_db}
        if not self.selected_countries or len(active_countries) == len(self.all_countries_in_db):
            self.btn_country_filter.configure(text=self._t("all_countries_filter"))
        else:
            self.btn_country_filter.configure(text=self._t("countries_n").format(len(active_countries)))
        self._apply_filters()

    def _apply_filters(self):
        """Мгновенная перерисовка таблицы по выбранным фильтрам"""
        self.proxy_tree.delete(*self.proxy_tree.get_children())
        
        sel_protos = self.selected_protos
        sel_countries = self.selected_countries
        count = 0
        
        active_protos = {p for p in sel_protos if p in self.all_protos_in_db}
        all_p = not sel_protos or len(active_protos) == len(self.all_protos_in_db)
        active_countries = {c for c in sel_countries if c in self.all_countries_in_db}
        all_c = not sel_countries or len(active_countries) == len(self.all_countries_in_db)
        
        for proto, ip, port, country in getattr(self, "_current_raw_data", []):
            match_proto = all_p or proto in sel_protos
            match_country = all_c or country in sel_countries
            
            if match_proto and match_country:
                self.proxy_tree.insert("", "end", values=(proto, ip, port, country))
                count += 1
                
        if count == 0:
            self.result_count_lbl.configure(text=self._t("no_data"))
            if hasattr(self, "results_empty_lbl"):
                self.results_empty_lbl.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.result_count_lbl.configure(text=self._t("proxies_count").format(count))
            if hasattr(self, "results_empty_lbl"):
                self.results_empty_lbl.place_forget()

    def _copy_results(self):
        """Копируем все прокси из таблицы в буфер обмена"""
        lines = []
        for item in self.proxy_tree.get_children():
            vals = self.proxy_tree.item(item, 'values')
            lines.append(f"{vals[0].lower()}://{vals[1]}:{vals[2]}")
        if lines:
            self.clipboard_clear()
            self.clipboard_append("\n".join(lines))
            self.result_count_lbl.configure(text=self._t("copied"))
            self.after(2000, self._load_results)

    def _export_csv(self):
        if not self.proxy_tree.get_children(): return
        path = fd.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title=self._t("dialog_save_csv"))
        if not path: return
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self._t('proto'), self._t('ip'), self._t('port'), self._t('country')])
            for item in self.proxy_tree.get_children():
                vals = self.proxy_tree.item(item, 'values')
                country_name = ISO_TO_NAME[self.current_lang].get(vals[3], vals[3])
                writer.writerow([vals[0].upper(), vals[1], vals[2], country_name])
        self.result_count_lbl.configure(text=self._t("csv_saved"))

    def _export_txt_proto(self):
        if not self.proxy_tree.get_children(): return
        path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title=self._t("dialog_save_txt1"))
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            for item in self.proxy_tree.get_children():
                vals = self.proxy_tree.item(item, 'values')
                f.write(f"{vals[0].lower()}://{vals[1]}:{vals[2]}\n")
        self.result_count_lbl.configure(text=self._t("txt_saved"))

    def _export_txt_full(self):
        if not self.proxy_tree.get_children(): return
        path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title=self._t("dialog_save_txt2"))
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            for item in self.proxy_tree.get_children():
                vals = self.proxy_tree.item(item, 'values')
                f.write(f"{vals[1]}:{vals[2]}\n")
        self.result_count_lbl.configure(text=self._t("txt_saved"))

    def _export_txt_ip(self):
        if not self.proxy_tree.get_children(): return
        path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title=self._t("dialog_save_txt3"))
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            ips = set()
            for item in self.proxy_tree.get_children():
                vals = self.proxy_tree.item(item, 'values')
                ips.add(vals[1])
            for ip in sorted(ips):
                f.write(f"{ip}\n")
        self.result_count_lbl.configure(text=self._t("txt_ip_saved"))

    def _copy_csv_all(self):
        if not self.proxy_tree.get_children(): return
        lines = []
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([self._t('proto'), self._t('ip'), self._t('port'), self._t('country')])
        for item in self.proxy_tree.get_children():
            vals = self.proxy_tree.item(item, 'values')
            country_name = ISO_TO_NAME[self.current_lang].get(vals[3], vals[3])
            writer.writerow([vals[0].upper(), vals[1], vals[2], country_name])
        lines.append(output.getvalue().strip())
        if lines:
            self.clipboard_clear()
            self.clipboard_append("\n".join(lines))
            self.result_count_lbl.configure(text=self._t("copied"))
            self.after(2000, self._load_results)

    def _copy_txt_proto_all(self):
        if not self.proxy_tree.get_children(): return
        lines = []
        for item in self.proxy_tree.get_children():
            vals = self.proxy_tree.item(item, 'values')
            lines.append(f"{vals[0].lower()}://{vals[1]}:{vals[2]}")
        if lines:
            self.clipboard_clear()
            self.clipboard_append("\n".join(lines))
            self.result_count_lbl.configure(text=self._t("copied"))
            self.after(2000, self._load_results)

    def _copy_txt_full_all(self):
        if not self.proxy_tree.get_children(): return
        lines = []
        for item in self.proxy_tree.get_children():
            vals = self.proxy_tree.item(item, 'values')
            lines.append(f"{vals[1]}:{vals[2]}")
        if lines:
            self.clipboard_clear()
            self.clipboard_append("\n".join(lines))
            self.result_count_lbl.configure(text=self._t("copied"))
            self.after(2000, self._load_results)

    def _copy_txt_ip_all(self):
        if not self.proxy_tree.get_children(): return
        ips = set()
        for item in self.proxy_tree.get_children():
            vals = self.proxy_tree.item(item, 'values')
            ips.add(vals[1])
        if ips:
            self.clipboard_clear()
            self.clipboard_append("\n".join(sorted(ips)))
            self.result_count_lbl.configure(text=self._t("copied"))
            self.after(2000, self._load_results)

    def _card(self, parent, title, accent, emoji, row, col):
        c = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14, border_width=1, border_color=BORDER)
        c.grid(row=row, column=col, padx=6, pady=(0,10), sticky="ew")
        inner = ctk.CTkFrame(c, fg_color="transparent")
        inner.pack(padx=18, pady=14, fill="x")
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=emoji, font=("Segoe UI", 16)).pack(side="left", padx=(0, 8))
        lbl_title = ctk.CTkLabel(top, text=title, font=("Segoe UI", 12), text_color=MUTED)
        lbl_title.pack(side="left")
        lbl = ctk.CTkLabel(inner, text="0", font=("Segoe UI", 28, "bold"), text_color=accent)
        lbl.pack(anchor="w", pady=(4, 0))
        return lbl, lbl_title

    # ===================== ЛОГИКА =====================
    def _init_log_buffer(self):
        """Инициализация буферизированного лога — обновляем UI макс 2 раза/сек"""
        self._log_buffer = deque(maxlen=500)
        self._proxy_queue = []
        self._stat_updates = {}
        self._log_lock = threading.Lock()
        self._live_log_counter = 0  # Троттлинг логов Live-прокси
        self._delayed_live_logs = []
        self._flush_log()

    def _flush_log(self):
        """Сбрасываем накопленные логи из быстрой очереди каждые 100мс"""
        import queue
        processed = 0
        
        while processed < 500:  # Process up to 500 logs per tick to avoid freezing
            try:
                clean = self._fast_queue.get_nowait()
                processed += 1
                
                # Parse steps for UI
                if "ШАГ 1:" in clean:
                    self.progress_lbl.configure(text=self._t("step1"))
                    self.progress_bar.set(0.1)
                    self.progress_pct.configure(text="10%")
                elif "ШАГ 2:" in clean:
                    self.progress_lbl.configure(text=self._t("step2"))
                elif "ШАГ 3:" in clean:
                    self.progress_lbl.configure(text=self._t("step3"))
                
                # Parse stats quickly
                self._parse_stats(clean)
                
                if not clean.startswith("[REALTIME") and not clean.startswith(("    [Загрузка", "    [Проверка", "    [Фильтрация", "[Загрузка", "[Проверка", "[Фильтрация")):
                    tag = self._get_tag(clean)
                    self._enqueue_log(clean, tag)
                    
                if clean.startswith("[REALTIME_NEW_ELITE]"):
                    try:
                        parts = clean.split("[REALTIME_NEW_ELITE]")[1].strip().split("|")
                        msg = self._t("log_elite_found").format(parts[0], parts[1], parts[2], parts[3])
                        self._enqueue_live_log(msg, "gold")
                    except: pass
                elif clean.startswith("[REALTIME_NEW_LIVE]"):
                    try:
                        parts = clean.split("[REALTIME_NEW_LIVE]")[1].strip().split("|")
                        msg = self._t("log_live_found").format(parts[0], parts[1], parts[2], parts[3])
                        self._enqueue_live_log(msg, "green")
                    except: pass
            except queue.Empty:
                break
                
        # Now update the UI with batched stat updates
        s_updates = self._stat_updates.copy()
        self._stat_updates.clear()
        
        if 'total' in s_updates: self.stat_total.configure(text=s_updates['total'])
        if 'live' in s_updates: self.stat_live.configure(text=s_updates['live'])
        if 'elite' in s_updates: self.stat_elite.configure(text=s_updates['elite'])
        if hasattr(self, 'stat_dc') and 'dc' in s_updates: self.stat_dc.configure(text=s_updates['dc'])
        if hasattr(self, 'stat_res') and 'res' in s_updates: self.stat_res.configure(text=s_updates['res'])
        if hasattr(self, 'stat_mob') and 'mob' in s_updates: self.stat_mob.configure(text=s_updates['mob'])
        
        # Pull text logs from deque
        batch = []
        with self._log_lock:
            for _ in range(min(50, len(self._log_buffer))):
                batch.append(self._log_buffer.popleft())
            
            p_queue = self._proxy_queue[:50]
            self._proxy_queue = self._proxy_queue[50:]
            
        # Update text widget
        if batch:
            try:
                if hasattr(self, "terminal_empty_lbl"):
                    try: self.terminal_empty_lbl.place_forget()
                    except: pass
                    
                self.terminal.configure(state="normal")
                for text, tag in batch:
                    self.terminal.insert("end", text + "\n", tag)
                
                lines_count = int(self.terminal.index('end-1c').split('.')[0])
                if lines_count > 1000:
                    self.terminal.delete("1.0", f"{lines_count - 1000}.0")
                self.terminal.see("end")
                self.terminal.configure(state="disabled")
            except: pass
            
        # Update proxy table
        if p_queue:
            if not hasattr(self, "realtime_proxies"):
                self.realtime_proxies = {"live": [], "elite": [], "datacenter": [], "residential": [], "mobile": []}
                
            current_src = getattr(self, "result_source", None)
            mapped_src = None
            if current_src:
                v = current_src.get().lower()
                if v in ("live", self._t("source_live").lower()): mapped_src = "live"
                elif v in ("elite", self._t("source_elite").lower()): mapped_src = "elite"
                elif v in ("datacenter", self._t("source_datacenter").lower()): mapped_src = "datacenter"
                elif v in ("residential", self._t("source_residential").lower()): mapped_src = "residential"
                elif v in ("mobile", self._t("source_mobile").lower()): mapped_src = "mobile"
                else: mapped_src = "elite"
                
            current_filter = "all"
            if hasattr(self, "proto_filter"):
                f_val = self.proto_filter.get()
                if f_val not in ("Все", self._t("all_short")): current_filter = f_val.lower()
                
            inserted = 0
            for data, source in p_queue:
                self.realtime_proxies.setdefault(source, []).append(data)
                
                if mapped_src == source:
                    if current_filter == "all" or current_filter == data["protocol"].lower():
                        if hasattr(self, "proxy_tree"):
                            # Safety limit for realtime tree to avoid massive lag
                            if len(self.proxy_tree.get_children()) < 1000:
                                country_name = ISO_TO_NAME[self.current_lang].get(data["country"], data["country"])
                                self.proxy_tree.insert("", "end", values=(data["protocol"], data["ip"], data["port"], country_name))
                            
        self.after(100, self._flush_log)
    def _enqueue_log(self, text, tag):
        """Добавляем лог в очередь (вызывается из рабочего потока — потокобезопасно)"""
        if getattr(self, "_is_cancelling", False): return
        with self._log_lock:
            self._log_buffer.append((text, tag))

    def _enqueue_live_log(self, msg, tag):
        """Накапливаем логи для отложенного вывода после полной проверки"""
        if not hasattr(self, "_delayed_live_logs"):
            self._delayed_live_logs = []
        self._delayed_live_logs.append((msg, tag))

    def _get_tag(self, text):
        if "[+]" in text or "ШАГ" in text: return "blue"
        if "[✓]" in text or "Готово" in text: return "green"
        if "[x]" in text or "Ошибка" in text or "[!]" in text: return "red"
        if "🚀" in text: return "purple"
        return "default"

    def _parse_stats(self, text):
        if getattr(self, "_is_cancelling", False): return
        
        # Fast string matching without regex and without locks
        if "Уникальных IP:PORT" in text or "Unique IP:PORT" in text:
            try: self._stat_updates['total'] = text.split(":")[-1].strip()
            except: pass
        elif "Живых прокси:" in text or "Live proxies:" in text:
            try: self._stat_updates['live'] = text.split(":")[-1].strip()
            except: pass
        elif "прошедших все фильтры:" in text or "passed all filters:" in text:
            try: self._stat_updates['elite'] = text.split(":")[-1].strip()
            except: pass
        elif "[REALTIME_LIVE]" in text:
            try: self._stat_updates['live'] = text.split("[REALTIME_LIVE]")[1].strip()
            except: pass
        elif "[REALTIME_ELITE]" in text:
            try: self._stat_updates['elite'] = text.split("[REALTIME_ELITE]")[1].strip()
            except: pass
        elif "[REALTIME_NEW_LIVE]" in text:
            try:
                parts = text.split("[REALTIME_NEW_LIVE]")[1].strip().split("|")
                data = {"ip": parts[0], "port": parts[1], "protocol": parts[2], "country": parts[3]}
                self._proxy_queue.append((data, "live"))
                self._live_count = getattr(self, '_live_count', 0) + 1
                self._stat_updates['live'] = str(self._live_count)
            except: pass
        elif "[REALTIME_NEW_ELITE]" in text:
            try:
                parts = text.split("[REALTIME_NEW_ELITE]")[1].strip().split("|")
                data = {"ip": parts[0], "port": parts[1], "protocol": parts[2], "country": parts[3], "category": parts[4]}
                
                self._elite_count = getattr(self, '_elite_count', 0) + 1
                self._stat_updates['elite'] = str(self._elite_count)
                
                cat = data.get("category", "Elite").lower()
                if cat == "datacenter":
                    self._dc_count = getattr(self, '_dc_count', 0) + 1
                    self._stat_updates['dc'] = str(self._dc_count)
                elif cat == "residential":
                    self._res_count = getattr(self, '_res_count', 0) + 1
                    self._stat_updates['res'] = str(self._res_count)
                elif cat == "mobile":
                    self._mob_count = getattr(self, '_mob_count', 0) + 1
                    self._stat_updates['mob'] = str(self._mob_count)
                    
                self._proxy_queue.append((data, cat))
            except: pass
    def _toggle_pause(self):
        if not self.is_running or not self.hunter_thread: return
        self.is_paused = not getattr(self, "is_paused", False)
        if self.is_paused:
            self.pause_btn.configure(text=self._t("resume"), image=self.icons["play"], fg_color=GREEN, hover_color="#059669")
            if hasattr(self, "hunter_instance"):
                self.hunter_instance.pause()
        else:
            self.pause_btn.configure(text=self._t("pause"), image=self.icons["pause"], fg_color=GOLD, hover_color="#D97706")
            if hasattr(self, "hunter_instance"):
                self.hunter_instance.resume()

    def _cancel_hunter(self):
        if not self.is_running or not self.hunter_thread: return
        self.cancel_btn.configure(state="disabled")
        self._is_cancelling = True
        if hasattr(self, "hunter_instance"):
            self.hunter_instance.cancel()
            
        # Полное мгновенное обнуление всего интерфейса
        self.stat_total.configure(text="0")
        self.stat_live.configure(text="0")
        self.stat_elite.configure(text="0")
        if hasattr(self, 'stat_dc'):
            self.stat_dc.configure(text="0")
            self.stat_res.configure(text="0")
            self.stat_mob.configure(text="0")
        self.progress_bar.set(0)
        self.progress_pct.configure(text="0%")
        self.progress_lbl.configure(text=self._t("wait"))
        self.realtime_proxies = {"live": [], "elite": [], "datacenter": [], "residential": [], "mobile": []}
        
        if hasattr(self, "proxy_tree"):
            for item in self.proxy_tree.get_children():
                self.proxy_tree.delete(item)
            if hasattr(self, "results_empty_lbl"):
                self.results_empty_lbl.place(relx=0.5, rely=0.5, anchor="center")
        if hasattr(self, "result_count_lbl"):
            self.result_count_lbl.configure(text=self._t("proxies_count").format(0))
            
        with self._log_lock:
            self._log_buffer.clear()
            
        self.terminal.configure(state="normal")
        self.terminal.delete("1.0", "end")
        self.terminal.insert("end", self._t("log_user_abort"), "red")
        self.terminal.configure(state="disabled")

    def _run_hunter(self):
        if self.is_running: return
        
        # Тотальная валидация перед запуском
        if not self._get_selected_countries():
            self._flash_error_widget(self.start_btn, temp_text=self._t("error_no_countries"))
            return
            
        try:
            threads = int(float(self.entry_threads.get()))
            timeout = int(float(self.entry_timeout.get()))
            ping = float(self.entry_ping.get())
            speed = float(self.entry_speed.get())
        except ValueError:
            self._flash_error_widget(self.start_btn, temp_text="Invalid Settings!")
            return
            
        self.is_running = True
        self.is_paused = False
        self._is_cancelling = False
        self._live_count = 0
        self._elite_count = 0
        self.realtime_proxies = {"live": [], "elite": [], "datacenter": [], "residential": [], "mobile": []}
        
        self._set_ui_state("disabled")
        self.start_btn.configure(text=self._t("running"), image=self.icons["stop"], fg_color=RED, hover_color="#B91C1C", state="disabled")
        self.pause_btn.configure(state="normal", text=self._t("pause"), image=self.icons["pause"], fg_color=GOLD, hover_color="#D97706")
        self.cancel_btn.configure(state="normal")
        
        self.terminal.configure(state="normal")
        self.terminal.delete("1.0", "end")
        self.terminal.configure(state="disabled")
        self.stat_total.configure(text="0")
        self.stat_live.configure(text="0")
        self.stat_elite.configure(text="0")
        if hasattr(self, 'stat_dc'):
            self.stat_dc.configure(text="0")
            self.stat_res.configure(text="0")
            self.stat_mob.configure(text="0")
        
        # Clear the proxy table from previous runs
        if hasattr(self, "proxy_tree"):
            for item in self.proxy_tree.get_children():
                self.proxy_tree.delete(item)
        if hasattr(self, "result_count_lbl"):
            self.result_count_lbl.configure(text=self._t("proxies_count").format(0))

        self.progress_bar.set(0)
        self.progress_pct.configure(text="0%")
        self.progress_lbl.configure(text=self._t("prepare"))
        
        global PROGRESS_CALLBACK
        PROGRESS_CALLBACK = lambda desc, pct, n, tot: self.after(0, lambda: (
            self.progress_lbl.configure(text=f"{desc} ({n}/{tot})" if tot else f"{desc} ({n}...)"),
            self.progress_bar.set(pct),
            self.progress_pct.configure(text=f"{int(pct*100)}%")
        ))

        # Запускаем буфер логов
        self._init_log_buffer()

        app = self
        class Redir:
            def write(self, text):
                if getattr(app, "_is_cancelling", False): return
                clean = text.strip()
                if not clean: return
                
                is_realtime = clean.startswith("[REALTIME")
                
                # Push everything to the fast queue to be processed by the main thread
                app._fast_queue.put(clean)
                
                if not is_realtime and not clean.startswith(("    [Загрузка", "    [Проверка", "    [Фильтрация", "[Загрузка", "[Проверка", "[Фильтрация")):
                    try: sys.__stdout__.write(text)
                    except: pass
        # Извлекаем значения для рабочего потока
        threads_val = threads
        timeout_val = timeout
        countries_val = self._get_selected_countries()
        max_ping_val = ping
        min_speed_val = speed
        check_smtp_val = self.smtp_var.get()
        dc_val = self.dc_var.get()
        res_val = self.res_var.get()
        mob_val = self.mob_var.get()
        
        # Случайные генерации
        random_counts_val = {
            "http": int(float(self.random_counts["http"].get())) if self.random_gen_enabled.get() else 0,
            "socks4": int(float(self.random_counts["socks4"].get())) if self.random_gen_enabled.get() else 0,
            "socks5": int(float(self.random_counts["socks5"].get())) if self.random_gen_enabled.get() else 0
        }

        def target():
            old = sys.stdout
            sys.stdout = Redir()
            try:
                self.hunter_instance = ProxyHunter(
                    threads=threads_val,
                    timeout=timeout_val,
                    countries=countries_val,
                    max_ping=max_ping_val,
                    min_speed=min_speed_val,
                    check_smtp=check_smtp_val,
                    collect_dc=dc_val,
                    collect_res=res_val,
                    collect_mob=mob_val,
                    random_counts=random_counts_val
                )
                self.hunter_instance.run()
                if hasattr(self, "_delayed_live_logs") and self._delayed_live_logs:
                    with self._log_lock:
                        for msg, tag in self._delayed_live_logs:
                            self._log_buffer.append((msg, tag))
                    self._delayed_live_logs = []
                print(f"\n{self._t('done_msg')}")
                # Автоматически загружаем результаты и переключаемся на вкладку
                self.after(500, self._load_results)
                self.after(600, lambda: self.main_tabs.set("Результаты"))
            except Exception as ex:
                import traceback
                print(f"\n[x] Критическая ошибка: {ex}")
                traceback.print_exc()
            finally:
                sys.stdout = old
                self.is_running = False
                self.hunter_thread = None
                self.hunter_instance = None
                self.after(0, lambda: self._set_ui_state("normal"))
                self.after(0, lambda: self.start_btn.configure(text=self._t("start"), image=self.icons["play"], fg_color=BLUE, hover_color="#1D4ED8"))
                self.after(0, lambda: self.pause_btn.configure(state="disabled"))
                self.after(0, lambda: self.cancel_btn.configure(state="disabled"))
                
        self.hunter_thread = threading.Thread(target=target, daemon=True)
        self.hunter_thread.start()


    def _build_checker_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1, uniform="checker_main")
        parent.grid_columnconfigure(1, weight=2, uniform="checker_main")
        parent.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(parent, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # === СНАЧАЛА pack-им нижние элементы (side=bottom) — они ВСЕГДА видны ===
        self.btn_check_start = ctk.CTkButton(left_panel, text=self._t("checker_start"), image=self.icons["play"], fg_color=GREEN, hover_color="#047857",
                                 font=("Segoe UI", 12, "bold"), height=40, command=self._start_custom_checker)
        self.btn_check_start.pack(side="bottom", fill="x")

        btn_row = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_row.pack(side="bottom", fill="x", pady=(0, 5))
        btn_row.grid_columnconfigure(0, weight=1, uniform="checker_btns")
        btn_row.grid_columnconfigure(1, weight=1, uniform="checker_btns")
        
        self._chk_btn_load = ctk.CTkButton(btn_row, text=self._t("checker_load"), image=self.icons["folder-invoices"], fg_color=BORDER, hover_color="#2D3748",
                                 command=self._load_checker_file)
        self._chk_btn_load.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        self._chk_btn_clear = ctk.CTkButton(btn_row, text=self._t("checker_clear"), image=self.icons["trash"], fg_color=RED, hover_color="#991B1B",
                                 command=self._clear_checker_input)
        self._chk_btn_clear.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        # --- ФИЛЬТРЫ ПРОВЕРКИ (Что проверять) ---
        chk_options_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        chk_options_frame.pack(side="bottom", fill="x", pady=(0, 5))
        
        self._chk_lbl_what = ctk.CTkLabel(chk_options_frame, text=self._t("checker_what"), font=("Segoe UI", 11, "bold"), text_color=MUTED)
        self._chk_lbl_what.pack(anchor="w", pady=(0, 5))
        
        self.do_check_anon = ctk.BooleanVar(value=True)
        self.do_check_bl = ctk.BooleanVar(value=True)
        self.do_check_speed = ctk.BooleanVar(value=True)
        self.do_check_smtp = ctk.BooleanVar(value=True)
        
        grid_opts = ctk.CTkFrame(chk_options_frame, fg_color="transparent")
        grid_opts.pack(fill="x")
        grid_opts.grid_columnconfigure((0, 1), weight=1, uniform="chk_opts")
        self._chk_cb_anon = ctk.CTkCheckBox(grid_opts, text=self._t("checker_anon"), variable=self.do_check_anon, font=("Segoe UI", 11), checkbox_width=16, checkbox_height=16)
        self._chk_cb_anon.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=2)
        self._chk_cb_bl = ctk.CTkCheckBox(grid_opts, text=self._t("checker_bl"), variable=self.do_check_bl, font=("Segoe UI", 11), checkbox_width=16, checkbox_height=16)
        self._chk_cb_bl.grid(row=0, column=1, sticky="w", pady=2)
        self._chk_cb_speed = ctk.CTkCheckBox(grid_opts, text=self._t("checker_speed"), variable=self.do_check_speed, font=("Segoe UI", 11), checkbox_width=16, checkbox_height=16)
        self._chk_cb_speed.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=2)
        self._chk_cb_smtp = ctk.CTkCheckBox(grid_opts, text="SMTP (25/587)", variable=self.do_check_smtp, font=("Segoe UI", 11), checkbox_width=16, checkbox_height=16)
        self._chk_cb_smtp.grid(row=1, column=1, sticky="w", pady=2)

        # === ПОТОМ pack-им верхние элементы — инпут заполняет ОСТАВШЕЕСЯ пространство ===
        self._chk_lbl_input = ctk.CTkLabel(left_panel, text=self._t("checker_input_lbl"), font=("Segoe UI", 12, "bold"))
        self._chk_lbl_input.pack(anchor="w", pady=(0, 5))

        input_frame = ctk.CTkFrame(left_panel, fg_color="#060B14", corner_radius=8, border_width=1, border_color=BORDER)
        input_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        self.checker_input = tk.Text(input_frame, bg="#060B14", fg=MUTED, insertbackground="#E2E8F0",
                                     font=("Consolas", 11), relief="flat", padx=8, pady=8, bd=0, highlightthickness=0)
        self.checker_input.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.checker_placeholder = self._t("checker_placeholder_text")
        self.checker_input.insert("1.0", self.checker_placeholder)
        
        def _on_focus_in(e):
            if self.checker_input.get("1.0", "end-1c") == self.checker_placeholder:
                self.checker_input.delete("1.0", "end")
                self.checker_input.configure(fg="#E2E8F0")
                
        def _on_focus_out(e):
            if not self.checker_input.get("1.0", "end-1c").strip():
                self.checker_input.delete("1.0", "end")
                self.checker_input.insert("1.0", self.checker_placeholder)
                self.checker_input.configure(fg=MUTED)
                
        self.checker_input.bind("<FocusIn>", _on_focus_in)
        self.checker_input.bind("<FocusOut>", _on_focus_out)
        self.checker_input.bind("<<Paste>>", self._smart_paste)
        self.checker_input.bind("<Control-v>", self._smart_paste)
        self.checker_input.bind("<Command-v>", self._smart_paste)
        try:
            self.checker_input.bind("<Control-м>", self._smart_paste)
            self.checker_input.bind("<Control-М>", self._smart_paste)
        except Exception: pass
        
        self.checker_input.bind("<Control-a>", self._select_all)
        self.checker_input.bind("<Command-a>", self._select_all)
        try:
            self.checker_input.bind("<Control-ф>", self._select_all)
            self.checker_input.bind("<Control-Ф>", self._select_all)
        except Exception: pass


        right_panel = ctk.CTkFrame(parent, fg_color="#060B14", corner_radius=10)
        right_panel.grid(row=0, column=1, sticky="nsew")

        cols = ("#", "proxy", "ping", "anon", "bl", "speed", "smtp")
        self.check_tree = tk.ttk.Treeview(right_panel, columns=cols, show="headings", style="Proxy.Treeview")
        
        self.check_tree.heading("#", text="#")
        self.check_tree.heading("proxy", text=self._t("checker_h_proxy"))
        self.check_tree.heading("ping", text=self._t("checker_h_ping"))
        self.check_tree.heading("anon", text=self._t("checker_h_anon"))
        self.check_tree.heading("bl", text=self._t("checker_h_bl"))
        self.check_tree.heading("speed", text=self._t("checker_h_speed"))
        self.check_tree.heading("smtp", text="SMTP")

        self.check_tree.column("#", width=40, minwidth=40, anchor="center")
        self.check_tree.column("proxy", width=160, anchor="w")
        self.check_tree.column("ping", width=70, anchor="center")
        self.check_tree.column("anon", width=100, anchor="center")
        self.check_tree.column("bl", width=110, anchor="center")
        self.check_tree.column("speed", width=90, anchor="center")
        self.check_tree.column("smtp", width=70, anchor="center")

        self.check_tree.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        # --- ФИЛЬТРЫ СКАЧИВАНИЯ (Что сохранять) ---
        download_panel = ctk.CTkFrame(right_panel, fg_color=CARD, corner_radius=8, border_width=1, border_color=BORDER)
        download_panel.pack(fill="x", padx=8, pady=8)
        
        download_panel.grid_columnconfigure(0, weight=1)
        download_panel.grid_columnconfigure(1, weight=1)

        self._chk_lbl_criteria = ctk.CTkLabel(download_panel, text=self._t("checker_save_criteria"), font=("Segoe UI", 12, "bold"), text_color=TEXT)
        self._chk_lbl_criteria.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.btn_save_checker = ctk.CTkButton(download_panel, text=self._t("checker_download"), image=self.icons["download"], fg_color=BLUE, hover_color="#2563EB", font=("Segoe UI", 12, "bold"), width=120, command=self._save_checker_results)
        self.btn_save_checker.grid(row=0, column=1, sticky="e", padx=10, pady=(10, 0))
        
        cb_frame = ctk.CTkFrame(download_panel, fg_color="transparent")
        cb_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 10))
        cb_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.save_req_alive = ctk.BooleanVar(value=False)
        self.save_req_elite = ctk.BooleanVar(value=False)
        self.save_req_clean = ctk.BooleanVar(value=False)
        self.save_req_smtp = ctk.BooleanVar(value=False)
        
        self._chk_cb_alive = ctk.CTkCheckBox(cb_frame, text=self._t("checker_only_alive"), variable=self.save_req_alive, font=("Segoe UI", 11), checkbox_width=18, checkbox_height=18, command=self._apply_checker_filter)
        self._chk_cb_alive.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        self._chk_cb_elite = ctk.CTkCheckBox(cb_frame, text=self._t("checker_only_elite"), variable=self.save_req_elite, font=("Segoe UI", 11), checkbox_width=18, checkbox_height=18, command=self._apply_checker_filter)
        self._chk_cb_elite.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        self._chk_cb_clean = ctk.CTkCheckBox(cb_frame, text=self._t("checker_only_clean"), variable=self.save_req_clean, font=("Segoe UI", 11), checkbox_width=18, checkbox_height=18, command=self._apply_checker_filter)
        self._chk_cb_clean.grid(row=0, column=2, padx=5, pady=2, sticky="w")
        
        self._chk_cb_smtp = ctk.CTkCheckBox(cb_frame, text=self._t("checker_only_smtp"), variable=self.save_req_smtp, font=("Segoe UI", 11), checkbox_width=18, checkbox_height=18, command=self._apply_checker_filter)
        self._chk_cb_smtp.grid(row=0, column=3, padx=5, pady=2, sticky="w")

    def _save_checker_results(self):
        from tkinter import filedialog as fd
        path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], initialfile="checked_proxies.txt")
        if not path: return
        
        saved_count = 0
        # BUG-01: Include detached items too
        all_item_ids = list(self.check_tree.get_children()) + [item_id for item_id, _ in getattr(self, '_checker_detached', [])]
        with open(path, 'w', encoding='utf-8') as f:
            for item_id in all_item_ids:
                try:
                    vals = self.check_tree.item(item_id, "values")
                except Exception:
                    continue
                if not vals or len(vals) < 7: continue
                _, proxy, ping, anon, bl, speed, smtp = vals
                
                # Применяем фильтры (на базе emoji — независимо от языка)
                if self.save_req_alive.get() and ("❌" in str(ping) or "⏳" in str(ping) or "—" in str(ping)):
                    continue
                if self.save_req_elite.get() and "💎" not in str(anon):
                    continue
                if self.save_req_clean.get() and "✨" not in str(bl):
                    continue
                if self.save_req_smtp.get() and "■" not in str(smtp):
                    continue
                
                f.write(str(proxy) + "\n")
                saved_count += 1
        
        # BUG-16: Warn if nothing saved
        if saved_count == 0:
            self.btn_save_checker.configure(text="⚠ 0", fg_color="#7F1D1D")
            self.after(2000, lambda: self.btn_save_checker.configure(text=self._t("checker_download"), image=self.icons["download"], fg_color=BLUE))
        else:
            self.btn_save_checker.configure(text=self._t("checker_saved").format(saved_count), fg_color=GREEN)
            self.after(2000, lambda: self.btn_save_checker.configure(text=self._t("checker_download"), image=self.icons["download"], fg_color=BLUE))

    def _load_checker_file(self):
        from tkinter import filedialog as fd
        path = fd.askopenfilename(filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")])
        if not path: return
        
        import os
        # Проверка размера (макс 10 MB)
        if os.path.getsize(path) > 10 * 1024 * 1024:
            self._flash_error_widget(self._chk_btn_load, temp_text=self._t("error_file_size"))
            return
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.checker_input.delete("1.0", "end")
            self.checker_input.insert("end", content)
            self.checker_input.configure(fg="#E2E8F0")
        except UnicodeDecodeError:
            self._flash_error_widget(self._chk_btn_load, temp_text=self._t("error_file_type"))

    def _clear_checker_input(self):
        if getattr(self, 'checker_is_running', False):
            return
        self.checker_input.delete("1.0", "end")
        self.checker_input.insert("1.0", self.checker_placeholder)
        self.checker_input.configure(fg=MUTED)
        # BUG-02: Delete detached items too
        for item_id, _ in getattr(self, '_checker_detached', []):
            try:
                self.check_tree.reattach(item_id, '', 'end')
            except Exception:
                pass
        self._checker_detached = []
        for item in self.check_tree.get_children():
            self.check_tree.delete(item)

    def _start_custom_checker(self):
        if getattr(self, 'checker_is_running', False):
            self.checker_is_running = False
            self.btn_check_start.configure(state="disabled", text=self._t("checker_stopping"))
            return

        raw_text = self.checker_input.get("1.0", "end").strip()
        ph_text = self.checker_placeholder.strip()
        if not raw_text or raw_text.replace('\r', '') == ph_text.replace('\r', ''):
            self._flash_error_widget(self.btn_check_start, temp_text=self._t("error_no_proxies"))
            return
        
        for item in self.check_tree.get_children():
            self.check_tree.delete(item)

        import re
        self.check_tree_items = {} 
        
        # Мощный regex для умного поиска валидных IP:PORT (с возможным протоколом) в любом мусоре
        pattern = re.compile(r'(?:[a-zA-Z0-9]+://)?(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::\d{1,5})?')
        found = pattern.findall(raw_text)
        
        # Дедупликация с сохранением порядка
        proxies_list = list(dict.fromkeys(found))
        
        if not proxies_list:
            self._flash_error_widget(self.btn_check_start, temp_text=self._t("error_no_proxies"))
            return

        # BUG-05: Reset filter checkboxes for clean start
        self.save_req_alive.set(False)
        self.save_req_elite.set(False)
        self.save_req_clean.set(False)
        self.save_req_smtp.set(False)
        self._chk_cb_alive.configure(text=self._t("checker_only_alive"))
        self._chk_cb_elite.configure(text=self._t("checker_only_elite"))
        self._chk_cb_clean.configure(text=self._t("checker_only_clean"))
        self._chk_cb_smtp.configure(text=self._t("checker_only_smtp"))

        # Read timeout from settings slider
        try:
            checker_timeout = int(float(self.entry_timeout.get()))
        except ValueError:
            checker_timeout = 10

        for idx, p in enumerate(proxies_list, 1):
            item_id = self.check_tree.insert("", "end", values=(idx, p, "⏳", "⏳", "⏳", "⏳", "⏳"))
            self.check_tree_items[p] = item_id

        self.checker_is_running = True
        self._checker_detached = []
        self._metrics_scheduled = False
        self.btn_check_start.configure(text=self._t("cancel"), image=self.icons["cancel"], fg_color=RED, hover_color="#991B1B")
        self._chk_btn_load.configure(state="disabled")
        self._chk_btn_clear.configure(state="disabled")
        self.btn_save_checker.configure(state="disabled")
        self._chk_cb_anon.configure(state="disabled")
        self._chk_cb_bl.configure(state="disabled")
        self._chk_cb_speed.configure(state="disabled")
        self._chk_cb_smtp.configure(state="disabled")
        self.checker_input.configure(state="disabled")

        # Dynamic column visibility
        visible_cols = ["#", "proxy", "ping"]
        if self.do_check_anon.get(): visible_cols.append("anon")
        if self.do_check_bl.get(): visible_cols.append("bl")
        if self.do_check_speed.get(): visible_cols.append("speed")
        if self.do_check_smtp.get(): visible_cols.append("smtp")
        self.check_tree["displaycolumns"] = visible_cols

        threading.Thread(target=self._run_checker_thread, args=(list(self.check_tree_items.keys()), checker_timeout), daemon=True).start()

    def _run_checker_thread(self, proxies, timeout=10):
        from fetch_proxy import ProxyUtils, ProxyHunter
        import requests, time
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        dummy_hunter = ProxyHunter(threads=1)
        max_workers = min(30, len(proxies))
        
        def check_one(proxy):
            if not getattr(self, 'checker_is_running', False):
                return
            try:
                clean_proxy = proxy
                protocol_prefix = ""
                if "://" in proxy:
                    protocol_prefix, clean_proxy = proxy.split("://", 1)
                    
                if ':' in clean_proxy:
                    ip, port_str = clean_proxy.split(':', 1)
                    # BUG-14: Guard non-numeric port
                    try:
                        port = int(port_str)
                    except ValueError:
                        self._update_check_row(proxy, "ping", self._t("chk_error"))
                        return
                    is_ip_only = False
                    if protocol_prefix:
                        proxies_dict = {'http': f"{protocol_prefix}://{clean_proxy}", 'https': f"{protocol_prefix}://{clean_proxy}"}
                    else:
                        proxies_dict = {'http': f"http://{clean_proxy}", 'https': f"http://{clean_proxy}"}
                else:
                    ip = clean_proxy.strip()
                    port = None
                    is_ip_only = True
                    proxies_dict = None
                    
                if is_ip_only:
                    self._update_check_row(proxy, "ping", self._t("chk_skip"))
                    self._update_check_row(proxy, "anon", self._t("chk_skip"))
                    self._update_check_row(proxy, "speed", self._t("chk_skip"))
                    self._update_check_row(proxy, "smtp", self._t("chk_skip"))
                else:
                    if not self.checker_is_running: return
                    # 1. Ping
                    start_ping = time.time()
                    alive = ProxyUtils.tcp_ping(ip, port, timeout=timeout)
                    ping_ms = int((time.time() - start_ping) * 1000)
                    
                    if not alive:
                        self._update_check_row(proxy, "ping", self._t("chk_timeout"))
                        self._update_check_row(proxy, "anon", self._t("chk_skip"))
                        self._update_check_row(proxy, "bl", self._t("chk_skip"))
                        self._update_check_row(proxy, "speed", self._t("chk_skip"))
                        self._update_check_row(proxy, "smtp", self._t("chk_skip"))
                    else:
                        self._update_check_row(proxy, "ping", self._t("chk_ping_ok").format(ping_ms))
                        
                        if not self.checker_is_running: return
                        # 2. Anonymity
                        if self.do_check_anon.get():
                            try:
                                r = requests.get('http://httpbin.org/headers', proxies=proxies_dict, timeout=timeout)
                                headers = str(r.json().get('headers', {})).lower()
                                if 'x-forwarded-for' in headers or 'via' in headers:
                                    self._update_check_row(proxy, "anon", self._t("chk_transparent"))
                                else:
                                    self._update_check_row(proxy, "anon", self._t("chk_elite"))
                            except Exception:
                                self._update_check_row(proxy, "anon", self._t("chk_error"))
                        else:
                            self._update_check_row(proxy, "anon", self._t("chk_skip"))

                        if not self.checker_is_running: return
                        # 3. Speed
                        if self.do_check_speed.get():
                            try:
                                t0 = time.time()
                                r = requests.get('https://speed.cloudflare.com/__down?bytes=100000', proxies=proxies_dict, timeout=timeout)
                                dl_time = max(0.001, time.time() - t0)  # BUG-15: Guard ZeroDivision
                                mbps = round((100000 * 8) / dl_time / 1000000, 1)
                                if mbps > 0.5:
                                    self._update_check_row(proxy, "speed", self._t("chk_speed_ok").format(mbps))
                                else:
                                    self._update_check_row(proxy, "speed", self._t("chk_speed_bad").format(mbps))
                            except Exception:
                                self._update_check_row(proxy, "speed", self._t("chk_error"))
                        else:
                            self._update_check_row(proxy, "speed", self._t("chk_skip"))

                        if not self.checker_is_running: return
                        # 4. SMTP
                        if self.do_check_smtp.get():
                            try:
                                r = requests.get('http://portquiz.net:587', proxies=proxies_dict, timeout=timeout)
                                self._update_check_row(proxy, "smtp", self._t("chk_open") if r.status_code == 200 else self._t("chk_closed"))
                            except Exception:
                                self._update_check_row(proxy, "smtp", self._t("chk_closed"))
                        else:
                            self._update_check_row(proxy, "smtp", self._t("chk_skip"))

                if not self.checker_is_running: return
                # 5. Blacklists
                if self.do_check_bl.get():
                    try:
                        res = dummy_hunter._check_rdns_and_bl(ip)
                        if res.get('rdns_dirty') or res.get('dnsbl'):
                            self._update_check_row(proxy, "bl", self._t("chk_blacklisted"))
                        else:
                            self._update_check_row(proxy, "bl", self._t("chk_clean"))
                    except Exception:
                        self._update_check_row(proxy, "bl", self._t("chk_error"))
                else:
                    self._update_check_row(proxy, "bl", self._t("chk_skip"))
                    
            except Exception:
                pass
        
        # BUG-21: Parallel execution with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(check_one, p) for p in proxies]
            for f in as_completed(futures):
                if not self.checker_is_running:
                    for remaining in futures:
                        remaining.cancel()
                    break

        self.checker_is_running = False
        def _reset_ui():
            self.btn_check_start.configure(state="normal", text=self._t("checker_start"), image=self.icons["play"], fg_color=GREEN, hover_color="#047857")
            self._chk_btn_load.configure(state="normal")
            self._chk_btn_clear.configure(state="normal")
            self.btn_save_checker.configure(state="normal")
            self._chk_cb_anon.configure(state="normal")
            self._chk_cb_bl.configure(state="normal")
            self._chk_cb_speed.configure(state="normal")
            self._chk_cb_smtp.configure(state="normal")
            self.checker_input.configure(state="normal")
            # Restore all columns
            self.check_tree["displaycolumns"] = ("#", "proxy", "ping", "anon", "bl", "speed", "smtp")
            self._do_metrics_update()
        self.after(0, _reset_ui)

    def _update_check_row(self, proxy_str, col_name, value):
        item_id = self.check_tree_items.get(proxy_str)
        if not item_id: return
        
        col_indices = {"ping": 2, "anon": 3, "bl": 4, "speed": 5, "smtp": 6}
        idx = col_indices[col_name]
        
        def do_update():
            try:
                # BUG-06: Check item still exists before updating
                if not self.check_tree.exists(item_id): return
                current_vals = list(self.check_tree.item(item_id, "values"))
                current_vals[idx] = value
                self.check_tree.item(item_id, values=current_vals)
                # BUG-12: Throttle metrics (max 2x/sec)
                if not getattr(self, '_metrics_scheduled', False):
                    self._metrics_scheduled = True
                    self.after(500, self._do_metrics_update)
            except Exception: pass
            
        self.after(0, do_update)

    def _do_metrics_update(self):
        """Throttled wrapper for _update_checker_metrics"""
        self._metrics_scheduled = False
        self._update_checker_metrics()

    def _update_checker_metrics(self):
        """Update live counts on filter checkboxes"""
        alive_count = 0
        elite_count = 0
        clean_count = 0
        smtp_count = 0
        
        all_items = list(self.check_tree.get_children()) + [item_id for item_id, _ in getattr(self, '_checker_detached', [])]
        for item_id in all_items:
            try:
                vals = self.check_tree.item(item_id, "values")
                if not vals or len(vals) < 7:
                    continue
                _, proxy, ping, anon, bl, speed, smtp = vals
                
                if "❌" not in str(ping) and "⏳" not in str(ping) and "—" not in str(ping):
                    alive_count += 1
                if "💎" in str(anon):
                    elite_count += 1
                if "✨" in str(bl):
                    clean_count += 1
                if "■" in str(smtp):
                    smtp_count += 1
            except:
                pass
        
        if hasattr(self, '_chk_cb_alive'):
            self._chk_cb_alive.configure(text=f"{self._t('checker_only_alive')} ({alive_count})")
            self._chk_cb_elite.configure(text=f"{self._t('checker_only_elite')} ({elite_count})")
            self._chk_cb_clean.configure(text=f"{self._t('checker_only_clean')} ({clean_count})")
            self._chk_cb_smtp.configure(text=f"{self._t('checker_only_smtp')} ({smtp_count})")

    def _apply_checker_filter(self):
        """Instantly show/hide rows based on filter checkboxes"""
        # BUG-17: Reattach in correct order (ascending index)
        detached = getattr(self, '_checker_detached', [])
        for item_id, orig_idx in sorted(detached, key=lambda x: x[1]):
            try:
                self.check_tree.reattach(item_id, '', orig_idx)
            except Exception:
                try:
                    self.check_tree.reattach(item_id, '', 'end')
                except Exception:
                    pass
        self._checker_detached = []
        
        any_filter = (self.save_req_alive.get() or self.save_req_elite.get() or 
                      self.save_req_clean.get() or self.save_req_smtp.get())
        
        if not any_filter:
            self._update_checker_metrics()
            return
        
        # Collect items to detach with their original indices
        to_detach = []
        for item_id in list(self.check_tree.get_children()):
            try:
                vals = self.check_tree.item(item_id, "values")
                if not vals or len(vals) < 7:
                    continue
                _, proxy, ping, anon, bl, speed, smtp = vals
                
                hide = False
                if self.save_req_alive.get() and ("❌" in str(ping) or "⏳" in str(ping) or "—" in str(ping)):
                    hide = True
                if self.save_req_elite.get() and "💎" not in str(anon):
                    hide = True
                if self.save_req_clean.get() and "✨" not in str(bl):
                    hide = True
                if self.save_req_smtp.get() and "■" not in str(smtp):
                    hide = True
                
                if hide:
                    idx = self.check_tree.index(item_id)
                    to_detach.append((item_id, idx))
            except Exception:
                pass
        
        # Detach from bottom to top so indices stay valid
        for item_id, idx in reversed(to_detach):
            self.check_tree.detach(item_id)
        self._checker_detached = to_detach
        
        self._update_checker_metrics()


if __name__ == "__main__":
    app = ProxyHunterApp()
    app.mainloop()
