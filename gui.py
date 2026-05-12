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
        if PROGRESS_CALLBACK:
            PROGRESS_CALLBACK(self._desc, pct, self._n, self._total)
            
        if self._n - self._last_print >= self._step:
            self._last_print = self._n
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
    "RU": {},
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
        "tab_settings": "⚡ Settings",
        "tab_countries": "🌍 Countries",
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
        "start": "▶ START HUNT",
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
        "tab_terminal": "📟 Terminal",
        "tab_results": "📋 Results",
        "proto": "Protocol",
        "ip": "IP Address",
        "port": "Port",
        "country": "Country",
        "copy": "📋 Copy",
        "refresh": "🔄 Refresh",
        "download": "📥 Download:",
        "csv": "CSV (Full)",
        "txt1": "TXT (IP:Port)",
        "txt2": "TXT (IP Only)",
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
        "proto_all": "All"
    },
    "RU": {
        "cfg": "Конфигурация",
        "lang_lbl": "Язык:",
        "tab_settings": "⚡ Параметры",
        "tab_countries": "🌍 Страны",
        "threads": "Потоки (Threads)",
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
        "start": "▶ НАЧАТЬ СБОР",
        "running": "■ РАБОТАЕТ...",
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
        "tab_terminal": "📟 Терминал",
        "tab_results": "📋 Результаты",
        "proto": "Протокол",
        "ip": "IP-адрес",
        "port": "Порт",
        "country": "Страна",
        "copy": "📋 Копировать",
        "refresh": "🔄 Обновить",
        "download": "📥 Скачать:",
        "csv": "CSV (Полный)",
        "txt1": "TXT (IP:Port)",
        "txt2": "TXT (Только IP)",
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
        "source_elite": "Элитные",
        "proto_all": "Все"
    }
}

class ProxyHunterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Proxy Hunter v4.0")
        self.geometry("1280x860")
        self.minsize(1300, 700)
        self.configure(fg_color=BG)
        self.is_running = False
        self.hunter_thread = None
        self.country_vars = {}
        self._countries_built = False
        self._my_country = self._detect_my_country()
        self._region_btns = []  # for translation of per-category 'All' buttons
        self._region_reset_btns = []  # for translation of per-category 'Reset' buttons

        # Фиксированный горизонтальный layout — никакой адаптации
        self.root_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.root_frame.pack(fill="both", expand=True)

        self.root_frame.grid_columnconfigure(0, weight=0, minsize=450)  # фиксированная ширина сайдбара
        self.root_frame.grid_columnconfigure(1, weight=1)
        self.root_frame.grid_rowconfigure(0, weight=1)

        self.current_lang = "RU"
        self.interactive_widgets = []

        self._build_sidebar()
        self._build_main()

        self.bind_all("<Button-1>", self._on_click_outside)
        
    def _t(self, key):
        return LANG[self.current_lang].get(key, key)
        
    def _set_language(self, lang):
        self.current_lang = lang
        self._apply_language()
        
    def _set_ui_state(self, state):
        for w in self.interactive_widgets:
            if w.winfo_exists():
                w.configure(state=state)
        # Also disable country checkboxes
        for var in self.country_vars.values():
            pass # We can't disable just the var, we need the checkbox widgets. Let's just disable the tabview so they can't switch to it.
        # self.tab_view.configure(state=state)
                
    def _on_click_outside(self, event):
        try:
            widget_type = str(event.widget).lower()
            if "entry" not in widget_type:
                self.focus_set()
        except Exception:
            pass


    def _apply_language(self):
        self.lbl_cfg.configure(text="  " + self._t("cfg"))
        self.lbl_lang.configure(text=self._t("lang_lbl"))
        
        if hasattr(self, "lbl_threads"): self.lbl_threads.configure(text=self._t("threads"))
        if hasattr(self, "lbl_timeout"): self.lbl_timeout.configure(text=self._t("timeout"))
        if hasattr(self, "lbl_ping"): self.lbl_ping.configure(text=self._t("ping"))
        if hasattr(self, "lbl_speed"): self.lbl_speed.configure(text=self._t("speed"))
        
        if hasattr(self, "btn_all") and self.btn_all.winfo_exists(): self.btn_all.configure(text=self._t("all"))
        if hasattr(self, "btn_reset") and self.btn_reset.winfo_exists(): self.btn_reset.configure(text=self._t("reset"))
        if hasattr(self, "btn_europe") and self.btn_europe.winfo_exists(): self.btn_europe.configure(text=self._t("europe"))
        if hasattr(self, "btn_tier1") and self.btn_tier1.winfo_exists(): self.btn_tier1.configure(text=self._t("tier1"))
        
        # Translate per-category 'All' and 'Reset' buttons
        for btn in getattr(self, "_region_btns", []):
            if btn.winfo_exists(): btn.configure(text=self._t("all_short"))
        for btn in getattr(self, "_region_reset_btns", []):
            if btn.winfo_exists(): btn.configure(text=self._t("reset_short"))
        
        self.smtp_switch.configure(text=self._t("smtp"))
        self.res_switch.configure(text=self._t("res"))
        
        if not self.is_running:
            self.start_btn.configure(text=self._t("start"))
        else:
            self.start_btn.configure(text=self._t("running"))
            
        self.lbl_stat_total.configure(text=self._t("total"))
        self.lbl_stat_live.configure(text=self._t("live"))
        self.lbl_stat_elite.configure(text=self._t("elite"))
        
        self.btn_copy.configure(text=self._t("copy"))
        self.btn_refresh.configure(text=self._t("refresh"))
        self.lbl_download.configure(text=self._t("download"))
        self.btn_csv.configure(text=self._t("csv"))
        self.btn_txt1.configure(text=self._t("txt1"))
        self.btn_txt2.configure(text=self._t("txt2"))
        
        # Subtitle
        if hasattr(self, "subtitle_lbl"): self.subtitle_lbl.configure(text=self._t("subtitle"))
        
        # HW info labels
        if hasattr(self, "hw_title_lbl") and self.hw_title_lbl.winfo_exists():
            self.hw_title_lbl.configure(text=self._t("hw_title"))
            self.hw_cores_lbl.configure(text=self._t("hw_cores").format(self._hw_cores))
            self.hw_ram_lbl.configure(text=self._t("hw_ram").format(self._hw_ram))
            self.hw_threads_lbl.configure(text=self._t("hw_threads").format(self._hw_max_threads))
            self.hw_class_lbl.configure(text=self._t("hw_class"))
            self.hw_tier_lbl.configure(text=self._t(self._hw_tier_key))
        
        # Result count label
        if hasattr(self, "result_count_lbl"):
            txt = self.result_count_lbl.cget("text")
            import re as _re
            m = _re.search(r'(\d+)', txt)
            if m:
                self.result_count_lbl.configure(text=self._t("proxies_count").format(m.group(1)))
        
        # Source segmented buttons (Live/Elite)
        if hasattr(self, "source_seg"):
            try:
                for k, btn in self.source_seg._buttons_dict.items():
                    if k == "Live": btn.configure(text=self._t("source_live"))
                    elif k == "Elite": btn.configure(text=self._t("source_elite"))
            except Exception: pass
        
        self.proxy_tree.heading("proto", text=self._t("proto"))
        self.proxy_tree.heading("ip", text=self._t("ip"))
        self.proxy_tree.heading("port", text=self._t("port"))
        self.proxy_tree.heading("country", text=self._t("country"))
        
        if hasattr(self, "tab_view"):
            if "⚡ Параметры" in self.tab_view._segmented_button._buttons_dict:
                self.tab_view._segmented_button._buttons_dict["⚡ Параметры"].configure(text=self._t("tab_settings"))
            if "🌍 Страны" in self.tab_view._segmented_button._buttons_dict:
                self.tab_view._segmented_button._buttons_dict["🌍 Страны"].configure(text=self._t("tab_countries"))
                
        if hasattr(self, "main_tabs"):
            if "📟 Терминал" in self.main_tabs._segmented_button._buttons_dict:
                self.main_tabs._segmented_button._buttons_dict["📟 Терминал"].configure(text=self._t("tab_terminal"))
            if "📋 Результаты" in self.main_tabs._segmented_button._buttons_dict:
                self.main_tabs._segmented_button._buttons_dict["📋 Результаты"].configure(text=self._t("tab_results"))

        if hasattr(self, "progress_lbl"):
            txt = self.progress_lbl.cget("text")
            if txt in ["Ожидание запуска...", "Waiting to start..."]:
                self.progress_lbl.configure(text=self._t("wait"))

        if hasattr(self, "result_count_lbl"):
            txt = self.result_count_lbl.cget("text")
            if txt in ["Нет данных", "No data"]:
                self.result_count_lbl.configure(text=self._t("no_data"))
            elif "сохранен" in txt or "saved" in txt:
                pass # Already translated on action
                
        if hasattr(self, "proto_seg") and "Все" in self.proto_seg._buttons_dict:
            self.proto_seg._buttons_dict["Все"].configure(text=self._t("all_short"))

        # Rebuild countries list on language switch
        if getattr(self, "_countries_built", False):
            # Save existing checked states
            old_state = {iso: var.get() for iso, var in getattr(self, "country_vars", {}).items() if var.get()}
            self._old_country_state = old_state
            
            if hasattr(self, "tab_view"):
                try:
                    tab_countries = self.tab_view.tab("🌍 Страны")
                    for w in tab_countries.winfo_children():
                        w.destroy()
                except Exception:
                    pass
            self._countries_built = False
            
            if hasattr(self, "tab_view") and self.tab_view.get() == "🌍 Страны":
                tab_countries = self.tab_view.tab("🌍 Страны")
                self._build_countries_tab(tab_countries)
                self._countries_built = True

        # Reload the results table to update country names if they are currently loaded
        if hasattr(self, "proxy_tree"):
            self._load_results()
    # ===================== SIDEBAR =====================
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.root_frame, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER, width=450)
        self.sidebar.grid(row=0, column=0, padx=(15, 8), pady=15, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(0, weight=1)

        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 8))
        ctk.CTkLabel(header, text="⚙", font=("Segoe UI", 20), text_color=BLUE).pack(side="left")
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

        tab_settings = self.tab_view.add("⚡ Параметры")
        self.tab_countries_ref = self.tab_view.add("🌍 Страны")

        self._build_settings_tab(tab_settings)

    def _on_tab_change(self):
        """Ленивая загрузка вкладки стран — строим чекбоксы только при первом открытии"""
        if self.tab_view.get() == "🌍 Страны" and not self._countries_built:
            self._countries_built = True
            self._build_countries_tab(self.tab_countries_ref)

    # --- Вкладка ПАРАМЕТРЫ ---
    def _build_settings_tab(self, parent):
        frame = ctk.CTkScrollableFrame(parent, fg_color="transparent", corner_radius=0)
        frame.pack(fill="both", expand=True)
        self._settings_scroll_frame = frame  # keep reference for scroll reset
        self._enable_autohide_scrollbar(frame)

        # Start UI building
        self._hw_cores, self._hw_ram, self._hw_max_threads, self._hw_tier_key, self._hw_tier_color = get_hardware_limits()
        default_threads = min(500, self._hw_max_threads)

        self._add_slider(frame, "Threads", 10, self._hw_max_threads, default_threads, 1, "threads")
        self._add_slider(frame, "Timeout", 1, 20, 5, 1, "timeout")
        self._add_slider(frame, "Max Ping", 50, 2000, 700, 10, "ping")
        self._add_slider(frame, "Min Speed", 0.1, 10, 1.0, 0.1, "speed")

        ctk.CTkFrame(frame, fg_color=BORDER, height=1).pack(fill="x", padx=10, pady=12)

        self.smtp_var = ctk.BooleanVar(value=True)
        self.smtp_switch = ctk.CTkSwitch(frame, text=self._t("smtp"), variable=self.smtp_var, fg_color=BORDER, progress_color=BLUE, font=("Segoe UI", 13), text_color=TEXT)
        self.smtp_switch.pack(anchor="w", padx=10, pady=4)
        self.interactive_widgets.append(self.smtp_switch)

        self.res_var = ctk.BooleanVar(value=False)
        self.res_switch = ctk.CTkSwitch(frame, text=self._t("res"), variable=self.res_var, fg_color=BORDER, progress_color=BLUE, font=("Segoe UI", 13), text_color=TEXT)
        self.res_switch.pack(anchor="w", padx=10, pady=4)
        self.interactive_widgets.append(self.res_switch)

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
            entry.after(50, lambda: entry.select_range(0, "end"))

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
            _last_valid_value[0] = fmt(new)
            _set_border_ok()

        ctk.CTkButton(ctrl, text="−", width=28, height=28, fg_color=BORDER, hover_color="#2D3748",
                       font=("Segoe UI", 16, "bold"), text_color="white", corner_radius=6,
                       command=lambda: update_val(-step)).pack(side="left", padx=(0, 4))
        entry.pack(side="left")
        ctk.CTkButton(ctrl, text="+", width=28, height=28, fg_color=BORDER, hover_color="#2D3748",
                       font=("Segoe UI", 16, "bold"), text_color="white", corner_radius=6,
                       command=lambda: update_val(step)).pack(side="left", padx=(4, 0))

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

    def _enable_autohide_scrollbar(self, scrollable_frame):
        """Hides the scrollbar if the content fits inside the view, shows it otherwise.
        Also prevents mouse-wheel scroll from propagating to any outer scrollable container."""
        def check_scrollbar(*args):
            try:
                if not scrollable_frame.winfo_exists() or not scrollable_frame._parent_frame.winfo_exists():
                    return
                inner_h = scrollable_frame._parent_frame.winfo_reqheight()
                canvas_h = scrollable_frame._parent_canvas.winfo_height()
                # If content fits entirely within the view or the view is still initializing
                if inner_h <= canvas_h or canvas_h < 10:
                    if scrollable_frame._scrollbar.winfo_ismapped():
                        scrollable_frame._scrollbar.grid_remove()
                else:
                    if not scrollable_frame._scrollbar.winfo_ismapped():
                        scrollable_frame._scrollbar.grid(row=0, column=1, sticky="ns")
            except Exception:
                pass

        scrollable_frame._parent_canvas.bind("<Configure>", check_scrollbar, add="+")
        scrollable_frame._parent_frame.bind("<Configure>", check_scrollbar, add="+")
        # Delayed initial checks — widget heights are reported only after first render
        self.after(300, check_scrollbar)
        self.after(800, check_scrollbar)

        # ── Isolate mouse-wheel: scroll only THIS frame, not the outer root ──
        inner_canvas = scrollable_frame._parent_canvas

        def _scroll_this(e):
            ih = scrollable_frame._parent_frame.winfo_reqheight()
            ch = scrollable_frame._parent_canvas.winfo_height()
            if ih > ch:
                inner_canvas.yview_scroll(-1 * (e.delta // 120), "units")
            return "break"  # always stop propagation to outer CTkScrollableFrame

        # Bind directly on the canvas (not bind_all) — fires when cursor is over it
        inner_canvas.bind("<MouseWheel>", _scroll_this, add="+")
        # Also bind on child widgets inside the scrollable frame
        scrollable_frame.bind("<MouseWheel>", _scroll_this, add="+")

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

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True)
        self._enable_autohide_scrollbar(scroll)

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
            grid.grid_columnconfigure((0, 1), weight=1)

            for i, (iso, name) in enumerate(sorted(countries.items(), key=lambda x: x[1])):
                var = ctk.BooleanVar(value=False)
                self.country_vars[iso] = var
                cb = ctk.CTkCheckBox(grid, text=f"{name} ({iso})", variable=var,
                                 fg_color=BORDER, hover_color="#2D3748", checkmark_color="white",
                                 border_color=BORDER, font=("Segoe UI", 11), text_color=TEXT,
                                 command=self._update_count, width=150
                                 )
                cb.grid(row=i // 2, column=i % 2, sticky="w", padx=4, pady=1)
                self.interactive_widgets.append(cb)
                cb.configure(state=state)

            # Планируем загрузку следующего региона через 10мс
            if self._pending_regions:
                self.after(10, self._load_next_region)
            else:
                if hasattr(self, "_old_country_state") and self._old_country_state:
                    for iso, val in self._old_country_state.items():
                        if iso in self.country_vars: self.country_vars[iso].set(val)
                    self._update_count()
                    self._old_country_state = None
        except Exception as e:
            print(f"Error loading region: {e}")

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
        sel = [iso for iso, var in self.country_vars.items() if var.get()]
        if sel:
            return sel
        # Nothing selected = parse ALL except user's country
        all_isos = list(self.country_vars.keys())
        if self._my_country and self._my_country in all_isos:
            all_isos.remove(self._my_country)
        return all_isos if all_isos else None

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
            loc = locale.getdefaultlocale()[0]  # e.g. 'ru_RU'
            if loc and '_' in loc:
                return loc.split('_')[1].upper()
        except Exception:
            pass
        return None

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
        ctk.CTkLabel(shield, text="🛡", font=("Segoe UI", 18)).pack(expand=True)
        titles = ctk.CTkFrame(logo, fg_color="transparent")
        titles.pack(side="left")
        ctk.CTkLabel(titles, text="PROXY HUNTER", font=("Segoe UI", 22, "bold"), text_color="white").pack(anchor="w")
        self.subtitle_lbl = ctk.CTkLabel(titles, text=self._t("subtitle"), font=("Segoe UI", 11), text_color="#475569")
        self.subtitle_lbl.pack(anchor="w")

        self.start_btn = ctk.CTkButton(header, text=self._t("start"), font=("Segoe UI", 14, "bold"),
                                        fg_color=BLUE, hover_color="#2563EB", corner_radius=12,
                                        width=190, height=48, command=self._run_hunter)
        self.start_btn.pack(side="right")

        stats = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        stats.grid_columnconfigure((0, 1, 2), weight=1)
        self.stat_total, self.lbl_stat_total = self._card(stats, self._t("total"), BLUE, "🌐", 0)
        self.stat_live, self.lbl_stat_live = self._card(stats, self._t("live"), GREEN, "⚡", 1)
        self.stat_elite, self.lbl_stat_elite = self._card(stats, self._t("elite"), GOLD, "⭐", 2)

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

        tab_terminal = self.main_tabs.add("📟 Терминал")
        tab_results = self.main_tabs.add("📋 Результаты")

        self._build_terminal_tab(tab_terminal)
        self._build_results_tab(tab_results)

    def _on_main_tab_change(self):
        if self.main_tabs.get() == "📋 Результаты":
            self._load_results()

    def _build_terminal_tab(self, parent):
        self.terminal = ctk.CTkTextbox(parent, fg_color="#060B14", corner_radius=10, border_width=1, border_color=BORDER,
                                        font=("Consolas", 12), text_color="#94A3B8", state="disabled",
                                        activate_scrollbars=True, wrap="word")
        self.terminal.pack(fill="both", expand=True)
        self.terminal._textbox.tag_config("blue", foreground=BLUE)
        self.terminal._textbox.tag_config("green", foreground=GREEN)
        self.terminal._textbox.tag_config("red", foreground=RED)
        self.terminal._textbox.tag_config("purple", foreground="#A855F7")
        self.terminal._textbox.tag_config("default", foreground="#94A3B8")

    def _build_results_tab(self, parent):
        # Панель управления
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.pack(fill="x", pady=(5, 8))

        # Переключатель Live / Elite
        self.result_source = ctk.StringVar(value="live")
        self.source_seg = ctk.CTkSegmentedButton(toolbar, values=["Live", "Elite"], variable=self.result_source,
                                fg_color=BORDER, selected_color=BLUE, unselected_color=CARD,
                                font=("Segoe UI", 12, "bold"),
                                command=lambda v: self._load_results())
        self.source_seg.pack(side="left", padx=(5, 10))

        # Фильтр по протоколу
        self.proto_filter = ctk.StringVar(value="Все")
        self.proto_seg = ctk.CTkSegmentedButton(toolbar, values=["Все", "HTTP", "SOCKS4", "SOCKS5"], variable=self.proto_filter,
                                fg_color=BORDER, selected_color="#6366F1", unselected_color=CARD,
                                font=("Segoe UI", 11),
                                command=lambda v: self._load_results())
        self.proto_seg.pack(side="left", padx=(0, 10))

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
        self.btn_txt1 = ctk.CTkButton(export_toolbar, text=self._t("txt1"), width=120, height=28, fg_color="#4F46E5", hover_color="#4338CA",
                       font=("Segoe UI", 11, "bold"), corner_radius=6, command=self._export_txt_full)
        self.btn_txt1.pack(side="left", padx=5)
        self.btn_txt2 = ctk.CTkButton(export_toolbar, text=self._t("txt2"), width=120, height=28, fg_color="#D97706", hover_color="#B45309",
                       font=("Segoe UI", 11, "bold"), corner_radius=6, command=self._export_txt_ip)
        self.btn_txt2.pack(side="left", padx=5)

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
        self.proxy_tree.heading("proto", text="Протокол")
        self.proxy_tree.heading("ip", text="IP-адрес")
        self.proxy_tree.heading("port", text="Порт")
        self.proxy_tree.heading("country", text="Страна")
        self.proxy_tree.column("proto", width=90, minwidth=70, anchor="center")
        self.proxy_tree.column("ip", width=180, minwidth=120, anchor="center")
        self.proxy_tree.column("port", width=70, minwidth=50, anchor="center")
        self.proxy_tree.column("country", width=120, minwidth=80, anchor="center")

        scrollbar = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.proxy_tree.yview, fg_color="#060B14", button_color=BORDER, button_hover_color=MUTED)
        self.proxy_tree.configure(yscrollcommand=scrollbar.set)
        self.proxy_tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", pady=8, padx=(0, 4))

    def _load_results(self):
        """Загружаем результаты из CSV в таблицу"""
        self.proxy_tree.delete(*self.proxy_tree.get_children())

        source = self.result_source.get().lower()
        folder = f"results_{source}"
        proto = self.proto_filter.get().lower()

        if proto == "все":
            csv_file = os.path.join(folder, "all.csv")
        else:
            csv_file = os.path.join(folder, f"{proto}.csv")

        if not os.path.exists(csv_file):
            self.result_count_lbl.configure(text=self._t("no_data"))
            return

        count = 0
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # skip header
                for row in reader:
                    if len(row) >= 4:
                        country_name = ISO_TO_NAME[self.current_lang].get(row[3], row[3])
                        self.proxy_tree.insert("", "end", values=(row[0], row[1], row[2], country_name))
                        count += 1
        except Exception:
            pass

        self.result_count_lbl.configure(text=self._t("proxies_count").format(count))

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
        path = fd.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Сохранить CSV")
        if not path: return
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Протокол', 'IP', 'Port', 'Страна'])
            for item in self.proxy_tree.get_children():
                vals = self.proxy_tree.item(item, 'values')
                country_name = ISO_TO_NAME[self.current_lang].get(vals[3], vals[3])
                writer.writerow([vals[0].upper(), vals[1], vals[2], country_name])
        self.result_count_lbl.configure(text=self._t("csv_saved"))

    def _export_txt_full(self):
        if not self.proxy_tree.get_children(): return
        path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="Сохранить TXT (IP:Port)")
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            for item in self.proxy_tree.get_children():
                vals = self.proxy_tree.item(item, 'values')
                f.write(f"{vals[1]}:{vals[2]}\n")
        self.result_count_lbl.configure(text=self._t("txt_saved"))

    def _export_txt_ip(self):
        if not self.proxy_tree.get_children(): return
        path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="Сохранить TXT (Только IP)")
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            ips = set()
            for item in self.proxy_tree.get_children():
                vals = self.proxy_tree.item(item, 'values')
                ips.add(vals[1])
            for ip in sorted(ips):
                f.write(f"{ip}\n")
        self.result_count_lbl.configure(text=self._t("txt_ip_saved"))

    def _card(self, parent, title, accent, emoji, col):
        c = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14, border_width=1, border_color=BORDER)
        c.grid(row=0, column=col, padx=6, sticky="ew")
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
        """Инициализация буферизированного лога — обновляем UI макс 5 раз/сек"""
        self._log_buffer = deque(maxlen=2000)
        self._log_lock = threading.Lock()
        self._flush_log()

    def _flush_log(self):
        """Сбрасываем накопленные логи в терминал каждые 200мс"""
        with self._log_lock:
            batch = []
            while self._log_buffer:
                batch.append(self._log_buffer.popleft())

        if batch:
            self.terminal.configure(state="normal")
            for text, tag in batch:
                self.terminal.insert("end", text + "\n", tag)
            # Обрезаем до 1000 строк
            lines = int(self.terminal.index('end-1c').split('.')[0])
            if lines > 1000:
                self.terminal.delete("1.0", f"{lines - 1000}.0")
            self.terminal.see("end")
            self.terminal.configure(state="disabled")

        # Повторяем каждые 200мс
        self.after(200, self._flush_log)

    def _enqueue_log(self, text, tag):
        """Добавляем лог в очередь (вызывается из рабочего потока — потокобезопасно)"""
        with self._log_lock:
            self._log_buffer.append((text, tag))

    def _get_tag(self, text):
        if "[+]" in text or "ШАГ" in text: return "blue"
        if "[✓]" in text or "Готово" in text: return "green"
        if "[x]" in text or "Ошибка" in text or "[!]" in text: return "red"
        if "🚀" in text: return "purple"
        return "default"

    def _parse_stats(self, text):
        if "Уникальных IP:PORT" in text:
            m = re.search(r'(\d+)', text)
            if m: self.after(0, lambda v=m.group(1): self.stat_total.configure(text=v))
        elif "Живых прокси:" in text:
            m = re.search(r'Живых прокси: (\d+)', text)
            if m: self.after(0, lambda v=m.group(1): self.stat_live.configure(text=v))
        elif "прошедших все фильтры:" in text or "passed all filters:" in text:
            m = re.search(r'(?:прошедших все фильтры:|passed all filters:) (\d+)', text)
            if m: self.after(0, lambda v=m.group(1): self.stat_elite.configure(text=v))
        elif "[REALTIME_LIVE]" in text:
            m = re.search(r'\[REALTIME_LIVE\] (\d+)', text)
            if m: self.after(0, lambda v=m.group(1): self.stat_live.configure(text=v))
        elif "[REALTIME_ELITE]" in text:
            m = re.search(r'\[REALTIME_ELITE\] (\d+)', text)
            if m: self.after(0, lambda v=m.group(1): self.stat_elite.configure(text=v))
        elif "[REALTIME_NEW_LIVE]" in text:
            try:
                import json
                json_str = text.split("[REALTIME_NEW_LIVE] ")[1].strip()
                data = json.loads(json_str)
                self.after(0, lambda d=data: self._handle_realtime_proxy(d, "live"))
            except Exception: pass
        elif "[REALTIME_NEW_ELITE]" in text:
            try:
                import json
                json_str = text.split("[REALTIME_NEW_ELITE] ")[1].strip()
                data = json.loads(json_str)
                self.after(0, lambda d=data: self._handle_realtime_proxy(d, "elite"))
            except Exception: pass

    def _handle_realtime_proxy(self, data, source):
        """Вставляет новый прокси в таблицу, если он подходит под текущие фильтры"""
        if not hasattr(self, "proxy_tree"): return
        
        # Проверяем, что выбран именно тот источник, из которого пришел прокси
        if hasattr(self, "result_source"):
            current_src = self.result_source.get()
            # current_src is "Live" or "Elite" or "Рабочие" or "Элитные"
            # Map it back to "live" or "elite" based on current language
            mapped_src = "live" if current_src in ("Live", self._t("source_live")) else "elite"
            if mapped_src != source:
                return
        
        current_filter = "all"
        if hasattr(self, "proto_filter"):
            f_val = self.proto_filter.get().lower()
            if f_val != "все": current_filter = f_val
            
        if current_filter == "all" or current_filter == data["protocol"].lower():
            country_name = ISO_TO_NAME[self.current_lang].get(data["country"], data["country"])
            self.proxy_tree.insert("", "end", values=(data["protocol"], data["ip"], data["port"], country_name))
            
            # Обновляем счетчик
            if hasattr(self, "result_count_lbl"):
                count = len(self.proxy_tree.get_children())
                self.result_count_lbl.configure(text=self._t("proxies_count").format(count))

    def _run_hunter(self):
        if self.is_running: return
        self.is_running = True
        self._set_ui_state("disabled")
        self.start_btn.configure(text=self._t("running"), fg_color=RED, hover_color="#B91C1C")
        self.terminal.configure(state="normal")
        self.terminal.delete("1.0", "end")
        self.terminal.configure(state="disabled")
        self.stat_total.configure(text="0")
        self.stat_live.configure(text="0")
        self.stat_elite.configure(text="0")
        
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
                if not text.strip(): return
                try: sys.__stdout__.write(text)
                except: pass
                clean = text.strip()
                tag = app._get_tag(clean)
                app._enqueue_log(clean, tag)
                app._parse_stats(clean)
                
                # Парсинг шагов для UI
                if "ШАГ 1:" in clean:
                    app.after(0, lambda: app.progress_lbl.configure(text=app._t("step1")))
                    app.after(0, lambda: app.progress_bar.set(0.1))
                    app.after(0, lambda: app.progress_pct.configure(text="10%"))
                elif "ШАГ 2:" in clean:
                    app.after(0, lambda: app.progress_lbl.configure(text=app._t("step2")))
                elif "ШАГ 3:" in clean:
                    app.after(0, lambda: app.progress_lbl.configure(text=app._t("step3")))
                    app.after(0, lambda: app.progress_bar.set(0.9))
                    app.after(0, lambda: app.progress_pct.configure(text="90%"))
                elif "Готово!" in clean or "Done!" in clean:
                    app.after(0, lambda: app.progress_lbl.configure(text=app._t("step4")))
                    app.after(0, lambda: app.progress_bar.set(1.0))
                    app.after(0, lambda: app.progress_pct.configure(text="100%"))
            def flush(self): pass

        def target():
            old = sys.stdout
            sys.stdout = Redir()
            try:
                h = ProxyHunter(
                    threads=int(float(self.entry_threads.get())),
                    timeout=int(float(self.entry_timeout.get())),
                    countries=self._get_selected_countries(),
                    max_ping=float(self.entry_ping.get()),
                    min_speed=float(self.entry_speed.get()),
                    check_smtp=self.smtp_var.get(),
                    residential_only=self.res_var.get(),
                )
                h.run()
                print(f"\n{self._t('done_msg')}")
                # Автоматически загружаем результаты и переключаемся на вкладку
                self.after(500, self._load_results)
                self.after(600, lambda: self.main_tabs.set("📋 Результаты"))
            except Exception as ex:
                print(f"\n[x] Критическая ошибка: {ex}")
                traceback.print_exc()
            finally:
                sys.stdout = old
                self.is_running = False
                self.after(0, lambda: self._set_ui_state("normal"))
                self.after(0, lambda: self.start_btn.configure(text=self._t("start"), fg_color=BLUE, hover_color="#2563EB"))

        threading.Thread(target=target, daemon=True).start()

if __name__ == "__main__":
    app = ProxyHunterApp()
    app.mainloop()
