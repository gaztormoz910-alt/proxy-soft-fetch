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

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        
    def enter(self, event=None):
        self.schedule()
        
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()
        
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)
        
    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)
            
    def showtip(self):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#1E293B", foreground="white", relief='solid', borderwidth=1,
                         font=("Segoe UI", 10))
        label.pack(ipadx=4, ipady=2)
        
    def hidetip(self):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()

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
    max_threads = min(max_threads, 1000)
    max_threads = max(max_threads, 300)
    
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
        if 'PROGRESS_CALLBACK' in globals() and PROGRESS_CALLBACK:
            PROGRESS_CALLBACK(self._desc, 0.0, 0, self._total)
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
import contextlib

@contextlib.contextmanager
def patch_tqdm():
    original_tqdm = sys.modules.get('tqdm')
    original_tqdm_auto = sys.modules.get('tqdm.auto')
    
    sys.modules['tqdm'] = _tqdm_mock
    sys.modules['tqdm.auto'] = _tqdm_mock
    
    try:
        yield
    finally:
        if original_tqdm is not None:
            sys.modules['tqdm'] = original_tqdm
        else:
            sys.modules.pop('tqdm', None)
            
        if original_tqdm_auto is not None:
            sys.modules['tqdm.auto'] = original_tqdm_auto
        else:
            sys.modules.pop('tqdm.auto', None)

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
        "RS": "Сербия"
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
        "GE": "Грузия",
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
    },
    "🌍 Остальные": {
        "AD": "Андорра",
        "AG": "Антигуа и Барбуда",
        "AI": "Ангилья",
        "AQ": "Антарктида",
        "AS": "Американское Самоа",
        "AW": "Аруба",
        "AX": "Аландские о-ва",
        "BB": "Барбадос",
        "BF": "Буркина-Фасо",
        "BH": "Бахрейн",
        "BI": "Бурунди",
        "BJ": "Бенин",
        "BL": "Сен-Бартелеми",
        "BM": "Бермудские о-ва",
        "BN": "Бруней-Даруссалам",
        "BQ": "Бонэйр, Синт-Эстатиус и Саба",
        "BS": "Багамы",
        "BT": "Бутан",
        "BV": "о-в Буве",
        "BW": "Ботсвана",
        "BZ": "Белиз",
        "CC": "Кокосовые о-ва",
        "CF": "Центрально-Африканская Республика",
        "CG": "Конго - Браззавиль",
        "CI": "Кот-д’Ивуар",
        "CK": "Острова Кука",
        "CV": "Кабо-Верде",
        "CW": "Кюрасао",
        "CX": "о-в Рождества",
        "DJ": "Джибути",
        "DM": "Доминика",
        "EH": "Западная Сахара",
        "ER": "Эритрея",
        "FK": "Фолклендские о-ва",
        "FM": "Федеративные Штаты Микронезии",
        "FO": "Фарерские о-ва",
        "GA": "Габон",
        "GD": "Гренада",
        "GF": "Французская Гвиана",
        "GG": "Гернси",
        "GI": "Гибралтар",
        "GL": "Гренландия",
        "GM": "Гамбия",
        "GN": "Гвинея",
        "GP": "Гваделупа",
        "GQ": "Экваториальная Гвинея",
        "GS": "Южная Георгия и Южные Сандвичевы о-ва",
        "GU": "Гуам",
        "GW": "Гвинея-Бисау",
        "GY": "Гайана",
        "HM": "о-ва Херд и Макдональд",
        "IM": "о-в Мэн",
        "IO": "Британская территория в Индийском океане",
        "JE": "Джерси",
        "KI": "Кирибати",
        "KM": "Коморы",
        "KN": "Сент-Китс и Невис",
        "KY": "Острова Кайман",
        "LA": "Лаос",
        "LC": "Сент-Люсия",
        "LI": "Лихтенштейн",
        "LR": "Либерия",
        "LS": "Лесото",
        "MC": "Монако",
        "MF": "Сен-Мартен",
        "MG": "Мадагаскар",
        "MH": "Маршалловы Острова",
        "ML": "Мали",
        "MO": "Макао (САР)",
        "MP": "Северные Марианские о-ва",
        "MQ": "Мартиника",
        "MR": "Мавритания",
        "MS": "Монтсеррат",
        "MU": "Маврикий",
        "MV": "Мальдивы",
        "MW": "Малави",
        "NA": "Намибия",
        "NC": "Новая Каледония",
        "NE": "Нигер",
        "NF": "о-в Норфолк",
        "NR": "Науру",
        "NU": "Ниуэ",
        "OM": "Оман",
        "PF": "Французская Полинезия",
        "PM": "Сен-Пьер и Микелон",
        "PN": "о-ва Питкэрн",
        "PR": "Пуэрто-Рико",
        "PS": "Палестинские территории",
        "PW": "Палау",
        "RE": "Реюньон",
        "SB": "Соломоновы Острова",
        "SC": "Сейшельские Острова",
        "SD": "Судан",
        "SH": "о-в Св. Елены",
        "SJ": "Шпицберген и Ян-Майен",
        "SL": "Сьерра-Леоне",
        "SM": "Сан-Марино",
        "SR": "Суринам",
        "SS": "Южный Судан",
        "ST": "Сан-Томе и Принсипи",
        "SX": "Синт-Мартен",
        "SY": "Сирия",
        "SZ": "Эсватини",
        "TC": "о-ва Тёркс и Кайкос",
        "TD": "Чад",
        "TF": "Французские Южные территории",
        "TG": "Того",
        "TK": "Токелау",
        "TL": "Восточный Тимор",
        "TO": "Тонга",
        "TV": "Тувалу",
        "UM": "Внешние малые о-ва (США)",
        "VA": "Ватикан",
        "VC": "Сент-Винсент и Гренадины",
        "VG": "Виргинские о-ва (Великобритания)",
        "VI": "Виргинские о-ва (США)",
        "VU": "Вануату",
        "WF": "Уоллис и Футуна",
        "WS": "Самоа",
        "YE": "Йемен",
        "YT": "Майотта",
        "ZM": "Замбия",
        "ZW": "Зимбабве"
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
        "RS": "Serbia"
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
        "GE": "Georgia",
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
    },
    "🌍 Others": {
        "AD": "Andorra",
        "AG": "Antigua & Barbuda",
        "AI": "Anguilla",
        "AQ": "Antarctica",
        "AS": "American Samoa",
        "AW": "Aruba",
        "AX": "Åland Islands",
        "BB": "Barbados",
        "BF": "Burkina Faso",
        "BH": "Bahrain",
        "BI": "Burundi",
        "BJ": "Benin",
        "BL": "St. Barthélemy",
        "BM": "Bermuda",
        "BN": "Brunei",
        "BQ": "Caribbean Netherlands",
        "BS": "Bahamas",
        "BT": "Bhutan",
        "BV": "Bouvet Island",
        "BW": "Botswana",
        "BZ": "Belize",
        "CC": "Cocos (Keeling) Islands",
        "CF": "Central African Republic",
        "CG": "Congo - Brazzaville",
        "CI": "Côte d’Ivoire",
        "CK": "Cook Islands",
        "CV": "Cape Verde",
        "CW": "Curaçao",
        "CX": "Christmas Island",
        "DJ": "Djibouti",
        "DM": "Dominica",
        "EH": "Western Sahara",
        "ER": "Eritrea",
        "FK": "Falkland Islands",
        "FM": "Micronesia",
        "FO": "Faroe Islands",
        "GA": "Gabon",
        "GD": "Grenada",
        "GF": "French Guiana",
        "GG": "Guernsey",
        "GI": "Gibraltar",
        "GL": "Greenland",
        "GM": "Gambia",
        "GN": "Guinea",
        "GP": "Guadeloupe",
        "GQ": "Equatorial Guinea",
        "GS": "South Georgia & South Sandwich Islands",
        "GU": "Guam",
        "GW": "Guinea-Bissau",
        "GY": "Guyana",
        "HM": "Heard & McDonald Islands",
        "IM": "Isle of Man",
        "IO": "British Indian Ocean Territory",
        "JE": "Jersey",
        "KI": "Kiribati",
        "KM": "Comoros",
        "KN": "St. Kitts & Nevis",
        "KY": "Cayman Islands",
        "LA": "Laos",
        "LC": "St. Lucia",
        "LI": "Liechtenstein",
        "LR": "Liberia",
        "LS": "Lesotho",
        "MC": "Monaco",
        "MF": "St. Martin",
        "MG": "Madagascar",
        "MH": "Marshall Islands",
        "ML": "Mali",
        "MO": "Macao SAR China",
        "MP": "Northern Mariana Islands",
        "MQ": "Martinique",
        "MR": "Mauritania",
        "MS": "Montserrat",
        "MU": "Mauritius",
        "MV": "Maldives",
        "MW": "Malawi",
        "NA": "Namibia",
        "NC": "New Caledonia",
        "NE": "Niger",
        "NF": "Norfolk Island",
        "NR": "Nauru",
        "NU": "Niue",
        "OM": "Oman",
        "PF": "French Polynesia",
        "PM": "St. Pierre & Miquelon",
        "PN": "Pitcairn Islands",
        "PR": "Puerto Rico",
        "PS": "Palestinian Territories",
        "PW": "Palau",
        "RE": "Réunion",
        "SB": "Solomon Islands",
        "SC": "Seychelles",
        "SD": "Sudan",
        "SH": "St. Helena",
        "SJ": "Svalbard & Jan Mayen",
        "SL": "Sierra Leone",
        "SM": "San Marino",
        "SR": "Suriname",
        "SS": "South Sudan",
        "ST": "São Tomé & Príncipe",
        "SX": "Sint Maarten",
        "SY": "Syria",
        "SZ": "Eswatini",
        "TC": "Turks & Caicos Islands",
        "TD": "Chad",
        "TF": "French Southern Territories",
        "TG": "Togo",
        "TK": "Tokelau",
        "TL": "Timor-Leste",
        "TO": "Tonga",
        "TV": "Tuvalu",
        "UM": "U.S. Outlying Islands",
        "VA": "Vatican City",
        "VC": "St. Vincent & Grenadines",
        "VG": "British Virgin Islands",
        "VI": "U.S. Virgin Islands",
        "VU": "Vanuatu",
        "WF": "Wallis & Futuna",
        "WS": "Samoa",
        "YE": "Yemen",
        "YT": "Mayotte",
        "ZM": "Zambia",
        "ZW": "Zimbabwe"
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
        "tab_proxies": "Proxies",
        "tab_github": "GitHub API",
        "github_tm_label": "Use GitHub API",
        "github_token_label": "Token:",
        "github_token_placeholder": "ghp_...",
        "github_token_save": "Save Token",
        "github_token_status": "Token saved!",

        "threads": "Threads",
        "timeout": "Timeout",
        "ping": "Max Ping",
        "speed": "Min Speed",
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
        "csv": "CSV",
        "txt_proto": "Protocol://IP:Port",
        "txt1": "IP:Port",
        "txt2": "IP Only",
        "copied": "✓ Copied!",
        "csv_saved": "✓ CSV saved!",
        "txt_saved": "✓ TXT saved!",
        "txt_ip_saved": "✓ TXT saved!",
        "no_data": "No data",
        "error_no_countries": "Select at least 1 country!",
        "error_no_folder": "Select a save folder!",
        "output_dir_save": "Save",
        "output_dir_saved": "✓ Saved!",
        "github_days": "Time Machine Days:",
        "europe": "Europe",
        "hw_title": "💻 PC SPECIFICATIONS",
        "hw_cores": "• Processor: {0} Cores",
        "hw_ram": "• RAM: {0} GB",
        "hw_threads": "• Safe thread limit: {0}",
        "hw_class": "• Class: ",
        "tier_ultra": "ULTRA",
        "tier_high": "HIGH",
        "tier_medium": "MEDIUM",
        "tier_low": "LOW",
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
        "protocols_n": "Protocols ▼",
        "apply_filter": "Apply Filter",
        "reset_filter": "Reset Filter",
        "select_all_btn": "Select All",
        "tab_checker": "Checker",
        "checker_input_lbl": "Paste proxies:",
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
        "checker_h_country": "Country",
        "checker_category": "Category",
        "checker_h_category": "Category",
        "chk_fetching_categories": "Fetching Categories...",
        "checker_save_criteria": "Save by criteria:",
        "checker_only_alive": "Alive",
        "checker_only_elite": "Elite",
        "checker_only_clean": "Clean",
        "checker_only_smtp": "SMTP",
        "checker_only_res": "Residential",
        "checker_only_mob": "Mobile",
        "checker_only_dc": "Datacenter",
        "checker_download": "Download",
        "checker_saved": "✓ Saved",
        "checker_copy": "Copy",
        "checker_copied": "✓ Copied",
        "chk_unique_0": "Unique: 0",
        "chk_unique_n": "Unique: {0}",
        "chk_unique_n_total": "Unique: {0}",
        "chk_selected": "To copy/save: {0}",
        "log_live_found": "[+] Live proxy: {0}:{1}",
        "log_elite_found": "[+] 💎 Elite proxy: {0}:{1}",
        "log_user_abort": "Task was aborted by user.",
        "error_no_proxies": "No valid proxies found!",
        "error_file_size": "File too large!",
        "error_file_type": "Invalid file type!",
        "checker_placeholder_text": "Proxies:\nhttp://user:pass@ip:port\nhttps://user:pass@ip:port\nsocks5h://user:pass@ip:port\n\nOnly IP:\n192.168.x.x\n10.0.x.x",
        "proxy_title": "🔗 Proxies for scanning",
        "search": "Search...",
        "copy_lbl": "📋 Copy:",
        "proxy_load": "Load",
        "proxy_clear": "Clear",
        "proxy_scan_via": "Scan through proxies",
        "proxy_rotation": "Auto-rotation",
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
        "chk_clean": "✨ Clean",
        "output_dir_lbl": "Save Folder:",
        "output_dir_btn": "Browse"
    },
    "RU": {

        "cfg": "Конфигурация",
        "lang_lbl": "Язык:",
        "tab_settings": "Параметры",
        "tab_countries": "Страны",
        "threads": "Потоки",
        "timeout": "Таймаут",
        "ping": "Макс Пинг",
        "speed": "Мин Скор.",
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
        "step2": "Базовая проверка...",
        "step3": "Расширенная фильтрация...",
        "step4": "Завершено!",
        "done_msg": "[✓] Готово! Результаты в папках.",
        "tab_terminal": "Терминал",
        "tab_results": "Результаты",
        "proto": "Протокол",
        "ip": "IP-адрес",
        "port": "Порт",
        "country": "Страна",
        "copy": "📋 Копировать",
        "refresh": "🔄 Обновить",
        "download": "📥 Скачать:",
        "csv": "CSV",
        "txt_proto": "Protocol://IP:Port",
        "txt1": "IP:Port",
        "txt2": "Только IP",
        "copied": "✓ Скопировано!",
        "csv_saved": "✓ CSV сохранен!",
        "txt_saved": "✓ TXT сохранен!",
        "txt_ip_saved": "✓ TXT сохранен!",
        "no_data": "Нет данных",
        "europe": "Европа",
        "hw_title": "💻 ХАРАКТЕРИСТИКИ ПК",
        "hw_cores": "• Процессор: {0} Ядер",
        "hw_ram": "• ОЗУ: {0} GB",
        "hw_threads": "• Лимит потоков: {0}",
        "hw_class": "• Класс: ",
        "tier_ultra": "ULTRA",
        "tier_high": "HIGH",
        "tier_medium": "MEDIUM",
        "tier_low": "LOW",
        "proxies_count": "{0} прокси",
        "subtitle": "v4.0 · Продвинутая фильтрация",
        "source_live": "Рабочие",
        "source_elite": "Элитные",
        "source_datacenter": "Датацентры",
        "source_residential": "Резидентные",
        "source_mobile": "Мобильные",
        "proto_all": "Все",
        "pause": "Пауза",
        "resume": "▶ Продолжить",
        "cancel": "Отмена",
        "copy_terminal": "Копировать",
        "copied_terminal": "✓ Скопировано",
        "all_protocols": "Все протоколы",
        "all_countries_filter": "Все страны",
        "protocols_n": "Протоколы ▼",
        "countries_n": "Страны ▼",
        "apply_filter": "Задать фильтр",
        "tab_checker": "Проверка",
        "checker_input_lbl": "Вставьте прокси:",
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
        "checker_h_country": "Страна",
        "checker_category": "Категория",
        "checker_h_category": "Категория",
        "chk_fetching_categories": "Загрузка категорий...",
        "checker_save_criteria": "Сохранить по критериям:",
        "checker_only_alive": "Рабочие",
        "checker_only_elite": "Элитные",
        "checker_only_clean": "Чистые",
        "checker_only_smtp": "SMTP",
        "checker_only_res": "Резидентный",
        "checker_only_mob": "Мобильный",
        "checker_only_dc": "Датацентр",
        "checker_download": "Скачать",
        "checker_saved": "✓ Сохранено",
        "checker_copy": "Копировать",
        "checker_copied": "✓ Скопировано",
        "chk_unique_0": "Уникальных: 0",
        "chk_unique_n": "Уникальных: {0}",
        "chk_unique_n_total": "Уникальных: {0}",
        "chk_selected": "К сохранению: {0}",
        "log_live_found": "[+] Рабочий прокси: {0}:{1}",
        "log_elite_found": "[+] 💎 Элитный прокси: {0}:{1}",
        "log_user_abort": "Работа прервана.",
        "error_no_countries": "Выберите хотя бы 1 страну!",
        "error_no_folder": "Выберите папку!",
        "output_dir_save": "Сохранить",
        "output_dir_saved": "✓ Сохранено!",
        "error_no_proxies": "Нет валидных прокси!",
        "github_days": "Глубина поиска:",
        "error_file_size": "Файл слишком большой!",
        "error_file_type": "Неверный формат!",
        "checker_placeholder_text": "Прокси:\nhttp://user:pass@ip:port\nhttps://user:pass@ip:port\nsocks5h://user:pass@ip:port\n\nТолько IP:\n192.168.x.x\n10.0.x.x",
        "tab_proxies": "Прокси",
        "proxy_title": "🔗 Прокси для сканирования",
        "reset_filter": "Сбросить фильтр",
        "select_all_btn": "Выбрать всё",
        "search": "Поиск...",
        "copy_lbl": "📋 Скопировать:",
        "proxy_load": "Загрузить",
        "proxy_clear": "Очистить",
        "proxy_scan_via": "Сканировать через прокси",
        "proxy_rotation": "Авто-ротация",
        "proxy_remove_dead": "Удалять мёртвые",
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
        "chk_clean": "✨ Чистый",
        "output_dir_lbl": "Папка сохранения:",
        "output_dir_btn": "Выбрать",
        "tab_github": "API ГитХаба",
        "github_tm_label": "Машина Времени",
        "github_token_label": "Токен:",
        "github_token_placeholder": "ghp_...",
        "github_token_save": "Сохранить",
        "github_token_status": "Сохранено!"
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
        import threading
        self._log_lock = threading.Lock()
        
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
        self._my_country = self._detect_my_country() # L-06 FIX: Move here after current_lang is set
        self.interactive_widgets = []

        self._build_sidebar()
        self._build_main()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.bind_all("<Button-1>", self._on_click_outside)
        
    def _on_closing(self):
        try:
            self.is_running = False
            self.checker_is_running = False
            if hasattr(self, "hunter_instance") and self.hunter_instance:
                self.hunter_instance.is_running = False
                self.hunter_instance.is_checking = False
            self.destroy()
        except Exception:
            pass
        finally:
            import os
            os._exit(0)
    
    def _load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_settings(self):
        try:
            settings = self._load_settings()
            if hasattr(self, "output_dir"):
                settings["output_dir"] = self.output_dir.get()
            if hasattr(self, "github_token_var"):
                settings["github_token"] = self.github_token_var.get().strip().replace('\n', '').replace('\r', '')
            if hasattr(self, "github_tm_enabled"):
                settings["github_tm_enabled"] = self.github_tm_enabled.get()
            if hasattr(self, "github_tm_days_var"):
                try:
                    val = int(self.github_tm_days_var.get())
                    settings["github_tm_days"] = max(1, min(30, val))
                except ValueError:
                    settings["github_tm_days"] = 1
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def _safe_config(self, widget, **kwargs):
        try:
            if hasattr(widget, "winfo_exists") and widget.winfo_exists():
                widget.configure(**kwargs)
        except Exception:
            pass

    def _t(self, key):
        return LANG[self.current_lang].get(key, key)
        
    def _format_country(self, iso_code):
        if not iso_code or iso_code.lower() == 'unknown':
            return self._t("source_unknown") if "source_unknown" in LANG[self.current_lang] else "Unknown"
        name = ISO_TO_NAME.get(self.current_lang, {}).get(iso_code, iso_code)
        return name.strip()

        
    def _set_language(self, lang):
        self.current_lang = lang
        if hasattr(self, "hunter_instance") and self.hunter_instance:
            self.hunter_instance.lang = lang
        self._apply_language()
        
    def _set_ui_state(self, state):
        for w in self.interactive_widgets:
            if w.winfo_exists():
                w.configure(state=state)
                
    def _on_click_outside(self, event):
        try:
            w = event.widget
            # Не сбрасываем фокус, если кликнули по вводу, тексту, самому Treeview или его холсту
            # (CTkTtkTreeview использует внутренние Canvas/Treeview)
            exclusions = (tk.Entry, tk.Text, ctk.CTkEntry, ctk.CTkTextbox, tk.ttk.Treeview, tk.Canvas, ctk.CTkScrollbar, tk.Scrollbar, tk.ttk.Scrollbar)
            if not isinstance(w, exclusions):
                self.focus_set()
                
            # Дополнительно: если кликнули мимо таблиц, принудительно снимаем выделение с них
            # Исключаем фреймы и основное окно, так как при скролле (через колесико или ползунок)
            # могут генерироваться события или клик может попадать в промежутки
            deselect_exclusions = exclusions + (ctk.CTkFrame, ctk.CTkScrollableFrame, tk.Frame, tk.Tk, tk.Toplevel, tk.Label, ctk.CTkLabel, tk.Canvas)
            if not isinstance(w, deselect_exclusions):
                if hasattr(self, 'proxy_tree'):
                    self.proxy_tree.selection_remove(self.proxy_tree.selection())
                if hasattr(self, 'check_tree'):
                    self.check_tree.selection_remove(self.check_tree.selection())
            elif isinstance(w, tk.ttk.Treeview):
                # Если кликнули по самому Treeview, проверим куда именно
                # x и y в событии относительны виджета
                try:
                    region = w.identify_region(event.x, event.y)
                    # Если кликнули в пустую область (nothing) внутри treeview, снимаем выделение
                    if region == "nothing":
                        w.selection_remove(w.selection())
                except:
                    pass
        except Exception:
            pass

    def _flash_error_widget(self, widget, temp_text=None):
        if not widget.winfo_exists(): return
        if getattr(widget, "_is_flashing", False): return
        try:
            widget._is_flashing = True
            orig_fg = widget.cget("fg_color")
            try:
                orig_hover = widget.cget("hover_color")
            except:
                orig_hover = None
            try:
                orig_text = widget.cget("text")
            except:
                orig_text = None
            
            widget.configure(fg_color="#7F1D1D")
            if orig_hover: widget.configure(hover_color="#7F1D1D")
            if temp_text and orig_text: widget.configure(text=temp_text)
            
            def restore():
                if not widget.winfo_exists(): return
                widget.configure(fg_color=orig_fg)
                if orig_hover: widget.configure(hover_color=orig_hover)
                if temp_text and orig_text: widget.configure(text=orig_text)
                widget._is_flashing = False
            self.after(800, restore)
        except Exception:
            widget._is_flashing = False

    def _flash_success_widget(self, widget, temp_text=None):
        if not widget.winfo_exists(): return
        if getattr(widget, "_is_flashing", False): return
        try:
            widget._is_flashing = True
            orig_fg = widget.cget("fg_color")
            try:
                orig_hover = widget.cget("hover_color")
            except:
                orig_hover = None
            try:
                orig_text = widget.cget("text")
            except:
                orig_text = None
            
            widget.configure(fg_color="#059669")
            if orig_hover: widget.configure(hover_color="#047857")
            if temp_text and orig_text: widget.configure(text=temp_text)
            
            def restore():
                if not widget.winfo_exists(): return
                widget.configure(fg_color=orig_fg)
                if orig_hover: widget.configure(hover_color=orig_hover)
                if temp_text and orig_text: widget.configure(text=orig_text)
                widget._is_flashing = False
            self.after(3000, restore)
        except Exception:
            widget._is_flashing = False

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
        
        if hasattr(self, "lbl_github_tm"): self._safe_config(self.lbl_github_tm, text=self._t("github_tm_label"))
        if hasattr(self, "lbl_github_token"): self._safe_config(self.lbl_github_token, text=self._t("github_token_label"))
        if hasattr(self, "entry_github_token"): self._safe_config(self.entry_github_token, placeholder_text=self._t("github_token_placeholder"))
        if hasattr(self, "btn_save_github"): self._safe_config(self.btn_save_github, text=self._t("github_token_save"))
        

        if hasattr(self, "lbl_github_days"): self._safe_config(self.lbl_github_days, text=self._t("github_days"))
        
        if not self.is_running:
            self._safe_config(self.start_btn, text="", image=self.icons["play"])
        else:
            self._safe_config(self.start_btn, text="", image=self.icons["stop"])
            
        if hasattr(self, "pause_btn"):
            if getattr(self, "is_paused", False):
                self._safe_config(self.pause_btn, text="", image=self.icons["play"])
            else:
                self._safe_config(self.pause_btn, text="", image=self.icons["pause"])
        if hasattr(self, "cancel_btn"):
            self._safe_config(self.cancel_btn, text="", image=self.icons["cancel"])
            
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
        if hasattr(self, "lbl_out_dir"): self._safe_config(self.lbl_out_dir, text=self._t("output_dir_lbl"))
        if hasattr(self, "btn_out_dir"): self._safe_config(self.btn_out_dir, text=self._t("output_dir_btn"))
        if hasattr(self, "btn_save_out_dir"): self._safe_config(self.btn_save_out_dir, text=self._t("output_dir_save"))
        
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
                    elif k == "Datacenter": self._safe_config(btn, text=self._t("source_datacenter"))
                    elif k == "Residential": self._safe_config(btn, text=self._t("source_residential"))
                    elif k == "Mobile": self._safe_config(btn, text=self._t("source_mobile"))
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
                
        # Checker tab filters
        if hasattr(self, "btn_checker_proto_filter"):
            a_p = {p for p in getattr(self, "checker_selected_protos", set()) if p in getattr(self, "checker_all_protos", set())}
            if not getattr(self, "checker_selected_protos", set()) or len(a_p) == len(getattr(self, "checker_all_protos", set())):
                self._safe_config(self.btn_checker_proto_filter, text=self._t("all_protocols"))
            else:
                self._safe_config(self.btn_checker_proto_filter, text=self._t("protocols_n").format(len(a_p)))
        if hasattr(self, "btn_checker_country_filter"):
            a_c = {c for c in getattr(self, "checker_selected_countries", set()) if c in getattr(self, "checker_all_countries", set())}
            if not getattr(self, "checker_selected_countries", set()) or len(a_c) == len(getattr(self, "checker_all_countries", set())):
                self._safe_config(self.btn_checker_country_filter, text=self._t("all_countries_filter"))
            else:
                self._safe_config(self.btn_checker_country_filter, text=self._t("countries_n").format(len(a_c)))

        # Checker tab — full update
        if hasattr(self, "btn_check_start") and self.btn_check_start.cget("state") != "disabled":
            self._safe_config(self.btn_check_start, text=self._t("checker_start"))
        if hasattr(self, "_chk_btn_load"):
            self._safe_config(self._chk_btn_load, text=self._t("checker_load"))
            self._safe_config(self._chk_btn_clear, text=self._t("checker_clear"))
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
            if hasattr(self, "_chk_cb_res"): self._safe_config(self._chk_cb_res, text=self._t("checker_only_res"))
            if hasattr(self, "_chk_cb_mob"): self._safe_config(self._chk_cb_mob, text=self._t("checker_only_mob"))
            if hasattr(self, "_chk_cb_dc"): self._safe_config(self._chk_cb_dc, text=self._t("checker_only_dc"))
            self._safe_config(self.btn_save_checker, text=self._t("checker_download"))
            self._safe_config(self.btn_copy_checker, text=self._t("checker_copy"))
            # Checker tree headings
            self.check_tree.heading("proxy", text=self._t("checker_h_proxy"))
            self.check_tree.heading("ping", text=self._t("checker_h_ping"))
            self.check_tree.heading("anon", text=self._t("checker_h_anon"))
            self.check_tree.heading("bl", text=self._t("checker_h_bl"))
            self.check_tree.heading("speed", text=self._t("checker_h_speed"))
            self.check_tree.heading("country", text=self._t("checker_h_country"))
            try: self.check_tree.heading("category", text=self._t("checker_h_category"))
            except Exception: pass

            if hasattr(self, "check_tree"):
                other_lang = "RU" if self.current_lang == "EN" else "EN"
                status_keys = ["chk_timeout", "chk_error", "chk_skip", "chk_transparent", "chk_elite", 
                               "chk_open", "chk_closed", "chk_blacklisted", "chk_clean",
                               "checker_only_res", "checker_only_mob", "checker_only_dc"]
                trans_map = {LANG[other_lang][k]: LANG[self.current_lang][k] for k in status_keys}
                
                def _translate_vals(vals):
                    if not vals or len(vals) < 9: return vals
                    v = list(vals)
                    
                    # Try to re-translate country (v[2])
                    current_c = str(v[2])
                    iso = ""
                    for mapping in ISO_TO_NAME.values():
                        for k, name in mapping.items():
                            if name in current_c:
                                iso = k
                                break
                        if iso: break
                    if iso:
                        v[2] = self._format_country(iso)

                    # Category (v[3])
                    if str(v[3]) in trans_map: v[3] = trans_map[str(v[3])]

                    # Ping (v[4])
                    if " мс" in str(v[4]) or " ms" in str(v[4]):
                        val = str(v[4]).replace(" мс", "").replace(" ms", "")
                        v[4] = self._t("chk_ping_ok").format(val)
                    elif str(v[4]) in trans_map: v[4] = trans_map[str(v[4])]
                    
                    # Anon (v[5]), BL (v[6])
                    if str(v[5]) in trans_map: v[5] = trans_map[str(v[5])]
                    if str(v[6]) in trans_map: v[6] = trans_map[str(v[6])]
                    
                    # Speed (v[7])
                    if " Мбит/с" in str(v[7]) or " Mbps" in str(v[7]):
                        val = str(v[7]).replace(" Мбит/с", "").replace(" Mbps", "")
                        v[7] = self._t("chk_speed_ok").format(val)
                    elif str(v[7]) in trans_map: v[7] = trans_map[str(v[7])]
                    
                    # SMTP (v[8])
                    if str(v[8]) in trans_map: v[8] = trans_map[str(v[8])]
                    
                    return v

                for item in self.check_tree.get_children():
                    self.check_tree.item(item, values=_translate_vals(self.check_tree.item(item, 'values')))
                
                if hasattr(self, "_checker_detached"):
                    for item, idx in self._checker_detached:
                        try:
                            self.check_tree.item(item, values=_translate_vals(self.check_tree.item(item, 'values')))
                        except: pass
                
                # Update checker metrics text
                if hasattr(self, "_update_checker_metrics"):
                    self._update_checker_metrics()
                if hasattr(self, "_update_checker_count"):
                    self._update_checker_count()


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
                if hasattr(self, "lbl_random_https"): self._safe_config(self.lbl_random_https, text=self._t("random_count") + " HTTPS")
                if hasattr(self, "lbl_random_socks4"): self._safe_config(self.lbl_random_socks4, text=self._t("random_count") + " SOCKS4")
                if hasattr(self, "lbl_random_socks5"): self._safe_config(self.lbl_random_socks5, text=self._t("random_count") + " SOCKS5")
                
                # Update placeholder
                old_ph = getattr(self, "proxy_placeholder_text", "")
                new_ph = self._t("proxy_placeholder")
                if hasattr(self, "proxy_text") and self.proxy_text.get("1.0", "end-1c").strip() == old_ph.strip():
                    self.proxy_text.delete("1.0", "end")
                    self.proxy_text.insert("1.0", new_ph)
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
                val1 = ""
                try: val1 = widget.get("1.0", "end-1c").strip()
                except: pass
                val2 = ""
                try: val2 = widget.get("0.0", "end-1c").strip()
                except: pass
                if val1 == ph.strip() or val2 == ph.strip():
                    try: widget.delete("1.0", "end")
                    except: widget.delete("0.0", "end")
                    widget.configure(fg="#E2E8F0")
                widget.insert("insert", text_to_insert)
            else:
                # Скорее всего это proxy_text
                ph = getattr(self, "proxy_placeholder_text", "")
                val1 = ""
                try: val1 = widget.get("1.0", "end-1c").strip()
                except: pass
                val2 = ""
                try: val2 = widget.get("0.0", "end-1c").strip()
                except: pass
                if val1 == ph.strip() or val2 == ph.strip():
                    try: widget.delete("1.0", "end")
                    except: widget.delete("0.0", "end")
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
                
            widget.focus_set()
            widget.tag_add("sel", "1.0", "end")
            widget.mark_set("insert", "1.0")
            widget.see("insert")
            return "break"
        except Exception:
            pass

    def _smart_copy(self, event):
        try:
            widget = event.widget
            if hasattr(widget, "master") and hasattr(widget.master, "_textbox"):
                widget = widget.master._textbox
            elif hasattr(widget, "_textbox"):
                widget = widget._textbox
            
            if not widget.tag_ranges("sel"):
                widget.tag_add("sel", "1.0", "end")
                
            self.clipboard_clear()
            self.clipboard_append(widget.get("sel.first", "sel.last"))
            return "break"
        except Exception:
            pass

    def _bind_treeview_events(self, tree):
        def on_double_click(event):
            item = tree.identify_row(event.y)
            column = tree.identify_column(event.x)
            if not item or not column: return
            try:
                col_idx = int(column.replace('#', '')) - 1
                vals = tree.item(item, "values")
                if col_idx < 0 or col_idx >= len(vals): return
                text = str(vals[col_idx])
            except: return
            try:
                x, y, width, height = tree.bbox(item, column)
                entry = tk.Entry(tree, font=tree.cget("font"), justify="center", bg="#060B14", fg="white", readonlybackground="#1A202C")
                entry.place(x=x, y=y, width=width, height=height)
                entry.insert(0, text)
                entry.configure(state="normal") # Позволяем выделение и копирование
                entry.selection_range(0, 'end')
                entry.focus_set()
                def destroy_entry(e=None):
                    entry.destroy()
                entry.bind("<FocusOut>", destroy_entry)
                entry.bind("<Return>", destroy_entry)
                entry.bind("<Escape>", destroy_entry)
                
                # Стандартные комбинации для копирования в Entry (Windows)
                def copy_and_destroy(e):
                    tree.clipboard_clear()
                    try:
                        sel_text = entry.selection_get()
                    except tk.TclError:
                        sel_text = text # Если ничего не выделено - копируем всё
                    tree.clipboard_append(sel_text)
                    destroy_entry()
                    return "break"
                    
                entry.bind("<Control-c>", copy_and_destroy)
                entry.bind("<Control-C>", copy_and_destroy)
                try:
                    entry.bind("<Control-с>", copy_and_destroy) # Кириллица
                    entry.bind("<Control-С>", copy_and_destroy)
                except: pass

            except: pass

        def on_ctrl_c(event):
            sel = tree.selection()
            if not sel: return
            lines = []
            for item in sel:
                vals = tree.item(item, "values")
                lines.append("\t".join(str(v) for v in vals))
            tree.clipboard_clear()
            tree.clipboard_append("\n".join(lines))

        def on_click(event):
            region = tree.identify("region", event.x, event.y)
            if region == "heading" or region == "separator":
                return
            item = tree.identify_row(event.y)
            if not item:
                # Кликнули в пустую область таблицы -> снимаем выделение
                tree.selection_remove(tree.selection())

        tree.bind("<ButtonRelease-1>", on_click, add="+")
        tree.bind("<Double-Button-1>", on_double_click)
        tree.bind("<Control-c>", on_ctrl_c)
        tree.bind("<Control-C>", on_ctrl_c)
        try:
            tree.bind("<Control-с>", on_ctrl_c)
            tree.bind("<Control-С>", on_ctrl_c)
        except: pass
    def _on_tab_change(self):
        """Ленивая загрузка вкладок стран и прокси"""
        if self.tab_view.get() in ["Страны", "Countries"] and not getattr(self, "_countries_built", False):
            self._countries_built = True
            self._build_countries_tab(self.tab_countries_ref)
        elif self.tab_view.get() in ["Прокси", "Proxies"] and not getattr(self, "_proxies_built", False):
            self._proxies_built = True
            self._build_proxies_tab(self.tab_proxies_ref)



    # --- Вкладка ПАРАМЕТРЫ ---

    def _select_output_dir(self):
        from tkinter import filedialog as fd
        path = fd.askdirectory(title=self._t("output_dir_lbl"), initialdir=self.output_dir.get())
        if path:
            self.output_dir.set(path)

    def _build_settings_tab(self, parent):
        frame = ctk.CTkScrollableFrame(parent, fg_color="transparent", corner_radius=0)
        frame.pack(fill="both", expand=True)

        def _do_check():
            if not hasattr(frame, "_scrollbar"): return
            try:
                bbox = frame._parent_canvas.bbox("all")
                if bbox:
                    frame._parent_canvas.configure(scrollregion=bbox)
                content_height = (bbox[3] - bbox[1]) if bbox else frame._parent_frame.winfo_reqheight()
                canvas_height = frame._parent_canvas.winfo_height()
                if content_height > canvas_height and canvas_height > 10:
                    frame._scrollbar.grid()
                else:
                    frame._scrollbar.grid_remove()
            except Exception:
                pass

        def _check_scroll_size(e=None):
            if hasattr(frame, "after"):
                frame.after(50, _do_check)
                
        frame._parent_canvas.bind("<Configure>", _check_scroll_size, add="+")
        if hasattr(frame, "_parent_frame"):
            frame._parent_frame.bind("<Configure>", _check_scroll_size, add="+")

        # Start UI building
        self._hw_cores, self._hw_ram, self._hw_max_threads, self._hw_tier_key, self._hw_tier_color = get_hardware_limits()
        default_threads = min(500, self._hw_max_threads)

        self._add_slider(frame, self._t("threads"), 10, self._hw_max_threads, default_threads, 1, "threads")
        self._add_slider(frame, self._t("timeout"), 1, 300, 5, 1, "timeout")
        self._add_slider(frame, self._t("ping"), 50, 2000, 700, 10, "ping")
        self._add_slider(frame, self._t("speed"), 0.1, 10, 1.0, 0.1, "speed")

        ctk.CTkFrame(frame, fg_color=BORDER, height=1).pack(fill="x", padx=10, pady=12)

        self.smtp_var = ctk.BooleanVar(value=True)
        self.smtp_switch = ctk.CTkSwitch(frame, text=self._t("smtp"), variable=self.smtp_var, fg_color=BORDER, progress_color=BLUE, font=("Segoe UI", 13), text_color=TEXT)
        self.smtp_switch.pack(anchor="w", padx=10, pady=4)
        self.interactive_widgets.append(self.smtp_switch)

        self.dc_var = ctk.BooleanVar(value=True)
        self.res_var = ctk.BooleanVar(value=True)
        self.mob_var = ctk.BooleanVar(value=True)
        settings = self._load_settings()

        # Output Directory
        ctk.CTkFrame(frame, fg_color=BORDER, height=1).pack(fill="x", padx=10, pady=12)
        out_frame = ctk.CTkFrame(frame, fg_color="transparent")
        out_frame.pack(fill="x", padx=10, pady=4)
        
        if not hasattr(self, "output_dir"):
            self.output_dir = tk.StringVar(value=settings.get("output_dir", ""))
            
        self.lbl_out_dir = ctk.CTkLabel(out_frame, text=self._t("output_dir_lbl"), font=("Segoe UI", 12, "bold"), text_color=MUTED)
        self.lbl_out_dir.pack(anchor="w", pady=(0, 5))
        
        dir_inner = ctk.CTkFrame(out_frame, fg_color="transparent")
        dir_inner.pack(fill="x")
        
        # Text color white so it's readable when disabled (using a trick or just read-only)
        self.entry_out_dir = ctk.CTkEntry(dir_inner, textvariable=self.output_dir, state="readonly", fg_color="#060B14", border_color=BORDER, text_color="#E2E8F0")
        self.entry_out_dir.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_out_dir = ctk.CTkButton(dir_inner, text=self._t("output_dir_btn"), width=80, fg_color=BORDER, hover_color="#4A5568", command=self._select_output_dir)
        self.btn_out_dir.pack(side="right")
        self.interactive_widgets.append(self.btn_out_dir)

        dir_save_frame = ctk.CTkFrame(out_frame, fg_color="transparent")
        dir_save_frame.pack(fill="x", pady=(5, 0))

        self.btn_save_out_dir = ctk.CTkButton(
            dir_save_frame, 
            text=self._t("output_dir_save"), 
            fg_color=BLUE, hover_color="#2563EB", 
            command=lambda: (self._save_settings(), self._flash_success_widget(self.btn_save_out_dir, self._t("output_dir_saved")))
        )
        self.btn_save_out_dir.pack(fill="x", expand=True)
        self.interactive_widgets.append(self.btn_save_out_dir)

        # GitHub API Token
        ctk.CTkFrame(frame, fg_color=BORDER, height=1).pack(fill="x", padx=10, pady=12)
        gh_frame = ctk.CTkFrame(frame, fg_color="transparent")
        gh_frame.pack(fill="x", padx=10, pady=4)

        self.github_tm_enabled = ctk.BooleanVar(value=settings.get("github_tm_enabled", True))
        self.lbl_github_tm = ctk.CTkSwitch(gh_frame, text=self._t("github_tm_label"), variable=self.github_tm_enabled, font=("Segoe UI", 12))
        self.lbl_github_tm.pack(anchor="w", pady=(0, 15))

        self.lbl_github_token = ctk.CTkLabel(gh_frame, text=self._t("github_token_label"), font=("Segoe UI", 12, "bold"), text_color=MUTED)
        self.lbl_github_token.pack(anchor="w", pady=(0, 5))
        
        gh_inner = ctk.CTkFrame(gh_frame, fg_color="transparent")
        gh_inner.pack(fill="x")
        
        self.github_token_var = tk.StringVar()
        
        if "github_token" in settings:
            self.github_token_var.set(settings["github_token"].strip().replace('\n', '').replace('\r', ''))
            

        self.entry_github_token = ctk.CTkEntry(
            gh_inner, 
            textvariable=self.github_token_var,
            placeholder_text=self._t("github_token_placeholder"),
            font=("Consolas", 12),
            fg_color="#060B14", border_color=BORDER, text_color="#E2E8F0",
            show="*"
        )
        self.interactive_widgets.append(self.lbl_github_tm)
        self.interactive_widgets.append(self.entry_github_token)
        self.btn_save_github = ctk.CTkButton(
            gh_inner, 
            text=self._t("github_token_save"),
            font=("Segoe UI", 12),
            width=100,
            fg_color=BLUE, hover_color="#2563EB",
            command=lambda: (self._save_settings(), self._flash_success_widget(self.btn_save_github, self._t("github_token_status")))
        )
        # Pack button on the right first to prevent it being pushed out
        self.btn_save_github.pack(side="right")
        self.interactive_widgets.append(self.btn_save_github)

        self.entry_github_token.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def _gh_paste(e):
            try:
                text = self.entry_github_token.clipboard_get().strip()
                if self.entry_github_token.select_present():
                    self.entry_github_token.delete("sel.first", "sel.last")
                self.entry_github_token.insert("insert", text)
                return "break"
            except: pass
        
        def _gh_select_all(e):
            self.entry_github_token.select_range(0, "end")
            self.entry_github_token.icursor("end")
            return "break"
            
        def _gh_copy(e):
            try:
                if self.entry_github_token.select_present():
                    self.entry_github_token.clipboard_clear()
                    self.entry_github_token.clipboard_append(self.entry_github_token.selection_get())
                    return "break"
            except: pass

        for key in ["<Control-v>", "<Control-V>", "<<Paste>>", "<Control-KeyPress-m>", "<Control-KeyPress-M>", "<Control-Cyrillic_em>", "<Control-Cyrillic_EM>"]: self.entry_github_token.bind(key, _gh_paste)
        for key in ["<Control-c>", "<Control-C>"]: self.entry_github_token.bind(key, _gh_copy)
        for key in ["<Control-a>", "<Control-A>"]: self.entry_github_token.bind(key, _gh_select_all)

        gh_days_frame = ctk.CTkFrame(gh_frame, fg_color="transparent")
        gh_days_frame.pack(fill="x", pady=(10, 0))
        
        self.lbl_github_days = ctk.CTkLabel(gh_days_frame, text=self._t("github_days"), font=("Segoe UI", 12, "bold"), text_color=MUTED)
        self.lbl_github_days.pack(side="left", padx=(0, 10))
        
        self.github_tm_days_var = tk.StringVar(value=str(settings.get("github_tm_days", 1)))
        
        def _validate_days(*args):
            val = self.github_tm_days_var.get()
            if val == "": return
            if not val.isdigit():
                self.github_tm_days_var.set("1")
                return
            v = int(val)
            if v < 1: self.github_tm_days_var.set("1")
            elif v > 30: self.github_tm_days_var.set("30")
            
        self.github_tm_days_var.trace_add("write", _validate_days)
        
        self.entry_github_days = ctk.CTkEntry(
            gh_days_frame, 
            textvariable=self.github_tm_days_var,
            width=60,
            font=("Consolas", 12),
            fg_color="#060B14", border_color=BORDER, text_color="#E2E8F0"
        )
        self.entry_github_days.pack(side="left")
        self.interactive_widgets.append(self.entry_github_days)
        
        def toggle_github_options(*args):
            state = "normal" if self.github_tm_enabled.get() else "disabled"
            try:
                self.entry_github_token.configure(state=state)
                self.btn_save_github.configure(state=state)
                self.entry_github_days.configure(state=state)
                self.lbl_github_token.configure(text_color=TEXT if state=="normal" else MUTED)
                self.lbl_github_days.configure(text_color=TEXT if state=="normal" else MUTED)
            except Exception: pass

        self.github_tm_enabled.trace_add("write", toggle_github_options)
        self.after(100, toggle_github_options)
        
        # Removed lbl_github_status as we now flash the button instead

        # Spacer + HW info
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
        entry.bind("<KeyRelease>", _sanitize_and_sync, add="+")
        entry.bind("<FocusOut>", _on_focus_out)
        entry.bind("<FocusIn>", _on_focus_in)
        entry.bind("<Control-v>", _on_paste)
        entry.bind("<Control-V>", _on_paste)
        entry.bind("<<Paste>>", _on_paste)
        entry.bind("<Control-KeyPress-m>", _on_paste)
        entry.bind("<Control-KeyPress-M>", _on_paste)
        entry.bind("<Control-Cyrillic_em>", _on_paste)
        entry.bind("<Control-Cyrillic_EM>", _on_paste)
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
        self.interactive_widgets.extend([slider, entry, btn_minus, btn_plus])

    def _add_number_input(self, parent, label_text, from_, to, default, step, var):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(5, 0))
        lbl = ctk.CTkLabel(row, text=label_text, font=("Segoe UI", 12), text_color=MUTED)
        lbl.pack(side="left")

        ctrl = ctk.CTkFrame(row, fg_color="transparent")
        ctrl.pack(side="right")

        is_int = (step >= 1)

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

        entry.bind("<KeyRelease>", _sanitize_and_sync, add="+")
        entry.bind("<FocusOut>", _on_focus_out)
        entry.bind("<FocusIn>", _on_focus_in)
        def _on_ctrl_key_num(e):
            if getattr(e, 'keycode', 0) in (65, 97):
                entry.select_range(0, "end")
                return "break"
            elif getattr(e, 'keycode', 0) in (86, 118):
                _on_paste(e)
                return "break"
            elif getattr(e, 'keycode', 0) in (90, 122, 89, 121):
                _block(e)
                return "break"

        entry.bind("<Control-KeyPress>", _on_ctrl_key_num)
        entry.bind("<<Paste>>", _on_paste)
        entry.bind("<Shift-Insert>", _on_paste)
        entry.bind("<Command-v>", _on_paste)
        entry.bind("<Command-a>", lambda e: entry.select_range(0, "end"))
        entry.bind("<Button-2>", _block)
        entry.bind("<Button-3>", _block)
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

        self.interactive_widgets.extend([entry, btn_minus, btn_plus])
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
                       font=("Segoe UI", 11, "bold"), corner_radius=6, command=self._select_all_countries)
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
        self.tab_country_search.bind("<KeyRelease>", self._filter_countries_tab, add="+")

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
                cb = ctk.CTkCheckBox(grid, text=name, variable=var,
                                 fg_color=BORDER, hover_color="#2D3748", checkmark_color="white",
                                 border_color=BORDER, font=("Segoe UI", 11), text_color=TEXT,
                                 command=self._update_count, width=130)
                self.interactive_widgets.append(cb)
                cb.configure(state=state)
                cb.grid(row=idx // FIXED_COLS, column=idx % FIXED_COLS, sticky="w", padx=4, pady=2)
                
                # Привязка тултипа к полному названию страны
                ToolTip(cb, name)
                
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

    def _select_all_countries(self):
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
                if bbox:
                    scroll._parent_canvas.configure(scrollregion=bbox)
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
        self.random_counts = {"http": ctk.StringVar(value="5000000"), "https": ctk.StringVar(value="5000000"), "socks4": ctk.StringVar(value="5000000"), "socks5": ctk.StringVar(value="5000000")}
        
        for proto in ["http", "https", "socks4", "socks5"]:
            lbl = self._add_number_input(
                parent=scroll,
                label_text=f'{self._t("random_count")} {proto.upper()}',
                from_=0,
                to=99999999,
                default=5000000,
                step=100000,
                var=self.random_counts[proto]
            )
            setattr(self, f"lbl_random_{proto}", lbl)
        
    def _clear_proxy_placeholder(self):
        if self.proxy_text.get("1.0", "end-1c").strip() == self._t("proxy_placeholder").strip():
            self.proxy_text.delete("1.0", "end")
            
    def _restore_proxy_placeholder(self):
        if not self.proxy_text.get("1.0", "end-1c").strip():
            self.proxy_text.insert("1.0", self._t("proxy_placeholder"))

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
            if self.proxy_text.get("1.0", "end-1c").strip() == self._t("proxy_placeholder").strip():
                self.proxy_text.delete("1.0", "end")
            self.proxy_text.insert("end", content + "\n")
            self._update_chain_count()
        except Exception as e:
            pass

    def _parse_chain_proxies(self, silent=False) -> list:
        content = self.proxy_text.get("1.0", "end")
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
        
        self.pause_btn = ctk.CTkButton(self.btn_frame, text="", image=self.icons["pause"],
                                        fg_color=GOLD, hover_color="#D97706", corner_radius=12,
                                        width=48, height=48, command=self._toggle_pause, state="disabled")
        self.pause_btn.pack(side="left", padx=(0, 10))

        self.cancel_btn = ctk.CTkButton(self.btn_frame, text="", image=self.icons["cancel"],
                                        fg_color=RED, hover_color="#B91C1C", corner_radius=12,
                                        width=48, height=48, command=self._cancel_hunter, state="disabled")
        self.cancel_btn.pack(side="left", padx=(0, 10))

        self.start_btn = ctk.CTkButton(self.btn_frame, text="", image=self.icons["play"],
                                        fg_color=BLUE, hover_color="#2563EB", corner_radius=12,
                                        width=48, height=48, command=self._run_hunter)
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
        self.result_source = ctk.StringVar(value=self._t("source_live"))
        initial_vals = [
            self._t("source_live"),
            self._t("source_elite"),
            self._t("source_datacenter"),
            self._t("source_residential"),
            self._t("source_mobile")
        ]
        self.source_seg = ctk.CTkSegmentedButton(toolbar, values=initial_vals, variable=self.result_source,
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
        self._bind_treeview_events(self.proxy_tree)
        self.proxy_tree.heading("proto", text=self._t("proto"), command=lambda: self._sort_tree("proto", False))
        self.proxy_tree.heading("ip", text=self._t("ip"), command=lambda: self._sort_tree("ip", False))
        self.proxy_tree.heading("port", text=self._t("port"), command=lambda: self._sort_tree("port", False))
        self.proxy_tree.heading("country", text=self._t("country"), command=lambda: self._sort_tree("country", False))
        self.proxy_tree.column("proto", width=90, minwidth=70, anchor="center")
        self.proxy_tree.column("ip", width=180, minwidth=120, anchor="center")
        self.proxy_tree.column("port", width=70, minwidth=50, anchor="center")
        self.proxy_tree.column("country", width=120, minwidth=80, anchor="center")

        scrollbar = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.proxy_tree.yview, fg_color="#060B14", button_color=BORDER, button_hover_color=MUTED)
        self.proxy_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", pady=8, padx=(0, 4))
        self.proxy_tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        
        # Панель Пагинации
        pagination_toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        pagination_toolbar.pack(fill="x", pady=(0, 5))
        self.btn_prev_page = ctk.CTkButton(pagination_toolbar, text="◀", width=40, height=28, fg_color=BORDER, hover_color="#4A5568", command=self._prev_page)
        self.btn_prev_page.pack(side="left", padx=5)
        self.lbl_page = ctk.CTkLabel(pagination_toolbar, text="1 / 1", font=("Segoe UI", 11, "bold"), text_color=MUTED)
        self.lbl_page.pack(side="left", padx=5)
        self.btn_next_page = ctk.CTkButton(pagination_toolbar, text="▶", width=40, height=28, fg_color=BORDER, hover_color="#4A5568", command=self._next_page)
        self.btn_next_page.pack(side="left", padx=5)
        
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
                if data["country"] in ("RU", "BY", "KZ", "UZ", "AM", "AZ", "KG", "MD", "TJ", "TM", "AF", "KP", "SO"):
                    continue
                c_name = self._format_country(data["country"])
                p_name = data["protocol"].upper()
                self._current_raw_data.append((p_name, data["ip"], data["port"], c_name))
                protos.add(p_name)
                countries.add(c_name)
                self.proto_counts[p_name] = self.proto_counts.get(p_name, 0) + 1
                self.country_counts[c_name] = self.country_counts.get(c_name, 0) + 1
        else:
            base_dir = self.output_dir.get() if hasattr(self, "output_dir") else "."
            
            # Маппинг имен файлов для новой структуры
            file_map = {
                "live": "alive.txt",
                "elite": "elite.txt",
                "datacenter": "datacenter.txt",
                "residential": "residential.txt",
                "mobile": "mobile.txt"
            }
            # Пытаемся найти результаты в новой папке 'results', а если там нет, то в старых 'results_*'
            txt_file_new = os.path.join(base_dir, "results", file_map.get(mapped_src, f"{mapped_src}.txt"))
            txt_file_old = os.path.join(base_dir, f"results_{mapped_src}", file_map.get(mapped_src, f"{mapped_src}.txt"))
            
            txt_file = txt_file_new if os.path.exists(txt_file_new) else txt_file_old
            
            if os.path.exists(txt_file):
                # Инициализация базы стран для отображения
                geoip_reader = None
                if os.path.exists('GeoLite2-Country.mmdb'):
                    try:
                        import maxminddb
                        geoip_reader = maxminddb.open_database('GeoLite2-Country.mmdb')
                    except: pass
                    
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                line = line.strip()
                                if not line or line.startswith('#'): continue
                                
                                # Парсинг proto://ip:port
                                if '://' in line:
                                    proto, ipp = line.split('://', 1)
                                    proto = proto.upper()
                                    if proto.lower() in ('vless', 'vmess', 'ss', 'ssr', 'trojan', 'tuic', 'hysteria2', 'mtproto'):
                                        import fetch_proxy
                                        ext_ip, ext_port = fetch_proxy.ProxyUtils.extract_ip_port(line)
                                        ip_str, port_str = ext_ip, ext_port
                                    else:
                                        if ':' in ipp:
                                            ip_str, port_str = ipp.rsplit(':', 1)
                                        else:
                                            ip_str, port_str = ipp, ""
                                    
                                    # Определяем страну
                                    c_name = "Unknown"
                                    if geoip_reader:
                                        try:
                                            match = geoip_reader.get(ip_str)
                                            if match and 'country' in match:
                                                c_name = match['country']['iso_code']
                                        except: pass
                                    c_name = self._format_country(c_name)
                                    
                                    self._current_raw_data.append((proto, ip_str, port_str, c_name))
                                    protos.add(proto)
                                    countries.add(c_name)
                                    self.proto_counts[proto] = self.proto_counts.get(proto, 0) + 1
                                    self.country_counts[c_name] = self.country_counts.get(c_name, 0) + 1
                            except Exception:
                                continue # Игнорируем ошибки парсинга отдельной строки
                except Exception as e:
                    print(f"Error reading {txt_file}: {e}")
                finally:
                    if geoip_reader:
                        try: geoip_reader.close()
                        except: pass

        self.all_protos_in_db = protos
        self.all_countries_in_db = countries
        
        # Translate selected countries to the current language to prevent resetting on language switch
        new_selected = set()
        for c in self.selected_countries:
            iso_code = c
            for lang, mapping in ISO_TO_NAME.items():
                found = False
                for k, v in mapping.items():
                    if v == c or (len(c) > 3 and c[2] == " " and c[3:] == v):
                        iso_code = k
                        found = True
                        break
                if found:
                    break
            new_selected.add(self._format_country(iso_code))
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
            
        if len(protos) >= 2:
            self.btn_proto_filter.pack(side="left", padx=5, before=self.result_count_lbl)
        else:
            self.btn_proto_filter.pack_forget()
            
        if len(countries) >= 2:
            self.btn_country_filter.pack(side="left", padx=5, before=self.result_count_lbl)
        else:
            self.btn_country_filter.pack_forget()
            
        
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
        menu_frame = ctk.CTkFrame(btn_widget.winfo_toplevel(), fg_color=CARD2, corner_radius=8, border_width=1, border_color=BORDER)
        self._active_menu = menu_frame
        
        # Решение проблемы сдвига при масштабировании экрана (DPI) в Windows.
        scale = ctk.ScalingTracker.get_widget_scaling(btn_widget)
        
        toplevel = btn_widget.winfo_toplevel()
        
        phys_x = btn_widget.winfo_rootx() - toplevel.winfo_rootx()
        phys_y = btn_widget.winfo_rooty() - toplevel.winfo_rooty() + btn_widget.winfo_height() + int(5 * scale)
        
        logic_y = phys_y / scale
        
        is_checker_tab = False
        if hasattr(self, 'btn_checker_proto_filter') and btn_widget == self.btn_checker_proto_filter:
            is_checker_tab = True
        if hasattr(self, 'btn_checker_country_filter') and btn_widget == self.btn_checker_country_filter:
            is_checker_tab = True

        if is_checker_tab:
            phys_right_x = phys_x + btn_widget.winfo_width()
            logic_right_x = phys_right_x / scale
            menu_frame.place(x=logic_right_x, y=logic_y, anchor="ne")
        else:
            logic_x = phys_x / scale
            menu_frame.place(x=logic_x, y=logic_y, anchor="nw")
            
        menu_frame.lift()
        
        search_entry = ctk.CTkEntry(menu_frame, placeholder_text=self._t("search"), height=24, font=("Segoe UI", 11))
        search_entry.pack(fill="x", padx=5, pady=(5, 0))
        search_entry.after(10, search_entry.focus)

        scroll_h = min(65, max(40, len(items)*22))
        scroll = ctk.CTkScrollableFrame(menu_frame, fg_color="transparent", width=180, height=scroll_h)
        # У кастомного скроллбара минимальная высота 200, поэтому он не дает блоку стать меньше!
        # Фиксим это принудительно задавая высоту самого скроллбара:
        if hasattr(scroll, "_scrollbar"):
            scroll._scrollbar.configure(height=scroll_h)
            
        scroll.pack(padx=5, pady=5)
        
        check_vars = {}
        cb_widgets = {}
        for item in sorted(items):
            var = ctk.BooleanVar(value=(item in selected_set))
            
            display_text = f"{item} ({counts[item]})" if counts and item in counts else item
            
            cb = ctk.CTkCheckBox(scroll, text=display_text, variable=var, font=("Segoe UI", 11), 
                                 checkbox_width=18, checkbox_height=18, corner_radius=4)
            cb.pack(anchor="w", pady=2, padx=2)
            check_vars[item] = var
            cb_widgets[item] = cb
            
        def filter_items(*args):
            query = search_entry.get().lower()
            for item, cb in cb_widgets.items():
                iso_code = item
                for lang, mapping in ISO_TO_NAME.items():
                    found = False
                    for k, v in mapping.items():
                        if item == v or (len(item) > 3 and item[2] == " " and item[3:] == v):
                            iso_code = k
                            found = True
                            break
                    if found:
                        break
                
                translations = [item.lower()]
                if iso_code in ISO_TO_NAME.get("EN", {}):
                    translations.append(ISO_TO_NAME["EN"][iso_code].lower())
                if iso_code in ISO_TO_NAME.get("RU", {}):
                    translations.append(ISO_TO_NAME["RU"][iso_code].lower())
                
                if any(query in t for t in translations):
                    cb.pack(anchor="w", pady=2, padx=2)
                else:
                    cb.pack_forget()
                    
            if hasattr(scroll, '_parent_canvas'):
                scroll.after(10, lambda: scroll._parent_canvas.yview_moveto(0.0))
                    
        search_entry.bind("<KeyRelease>", filter_items, add="+")
            
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
                
        def select_all():
            for item, var in check_vars.items():
                var.set(True)
                
        def reset():
            selected_set.clear()
            on_apply()
            menu_frame.destroy()
            self._active_menu = None
            if hasattr(self, "_active_menu_bind") and self._active_menu_bind:
                try:
                    self.unbind("<Button-1>", self._active_menu_bind)
                except Exception: pass
            
        btn_select_all = ctk.CTkButton(menu_frame, text=self._t("select_all_btn"), fg_color="#059669", hover_color="#047857", height=24, font=("Segoe UI", 11), command=select_all)
        btn_select_all.pack(fill="x", padx=5, pady=(0, 2))
            
        btn = ctk.CTkButton(menu_frame, text=self._t("apply_filter"), fg_color=BLUE, hover_color="#2563EB", height=24, font=("Segoe UI", 11), command=apply)
        btn.pack(fill="x", padx=5, pady=(0, 2))
        
        btn_reset = ctk.CTkButton(menu_frame, text=self._t("reset_filter") if hasattr(self, "_t") else "Reset Filter", fg_color=BORDER, hover_color="#4A5568", height=24, font=("Segoe UI", 11), command=reset)
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

    def _on_checker_proto_btn_click(self):
        if not self.checker_all_protos: return
        self._create_floating_menu(self.btn_checker_proto_filter, self.checker_all_protos, self.checker_selected_protos, self._on_checker_proto_apply, counts=getattr(self, "checker_proto_counts", {}))
        
    def _on_checker_country_btn_click(self):
        if not self.checker_all_countries: return
        self._create_floating_menu(self.btn_checker_country_filter, self.checker_all_countries, self.checker_selected_countries, self._on_checker_country_apply, counts=getattr(self, "checker_country_counts", {}))

    def _on_checker_proto_apply(self):
        active_protos = {p for p in self.checker_selected_protos if p in self.checker_all_protos}
        if not self.checker_selected_protos or len(active_protos) == len(self.checker_all_protos):
            self.btn_checker_proto_filter.configure(text=self._t("all_protocols"))
        else:
            self.btn_checker_proto_filter.configure(text=self._t("protocols_n").format(len(active_protos)))
        self._apply_checker_filter()

    def _on_checker_country_apply(self):
        active_countries = {c for c in self.checker_selected_countries if c in self.checker_all_countries}
        if not self.checker_selected_countries or len(active_countries) == len(self.checker_all_countries):
            self.btn_checker_country_filter.configure(text=self._t("all_countries_filter"))
        else:
            self.btn_checker_country_filter.configure(text=self._t("countries_n").format(len(active_countries)))
        self._apply_checker_filter()

    def _sort_tree(self, col, reverse):
        """Алгоритмически правильная сортировка столбцов"""
        if not hasattr(self, "_filtered_data") or not self._filtered_data:
            return
            
        # Индексы столбцов в self._filtered_data: 0: proto, 1: ip, 2: port, 3: country
        col_map = {"proto": 0, "ip": 1, "port": 2, "country": 3}
        idx = col_map.get(col, 1)
        
        if col == "ip":
            import ipaddress
            def ip_key(item):
                try:
                    return int(ipaddress.IPv4Address(item[1]))
                except Exception:
                    return 0
            self._filtered_data.sort(key=ip_key, reverse=reverse)
        elif col == "port":
            self._filtered_data.sort(key=lambda x: int(x[2]) if str(x[2]).isdigit() else 0, reverse=reverse)
        else:
            self._filtered_data.sort(key=lambda x: str(x[idx]).lower(), reverse=reverse)
            
        # Обновляем заголовок столбца для смены направления при следующем клике
        self.proxy_tree.heading(col, command=lambda: self._sort_tree(col, not reverse))
        
        # Сброс на первую страницу и применение
        self.current_page = 1
        self._apply_filters()

    def _apply_filters(self):
        """Мгновенная перерисовка таблицы по выбранным фильтрам"""
        sel_protos = self.selected_protos
        sel_countries = self.selected_countries
        
        active_protos = {p for p in sel_protos if p in self.all_protos_in_db}
        all_p = not sel_protos or len(active_protos) == len(self.all_protos_in_db)
        active_countries = {c for c in sel_countries if c in self.all_countries_in_db}
        all_c = not sel_countries or len(active_countries) == len(self.all_countries_in_db)
        
        self._filtered_data = []
        for proto, ip, port, country in getattr(self, "_current_raw_data", []):
            match_proto = all_p or proto in sel_protos
            match_country = all_c or country in sel_countries
            if match_proto and match_country:
                self._filtered_data.append((proto, ip, port, country))
                
        self.current_page = 0
        self._render_page()

    def _prev_page(self):
        if hasattr(self, "current_page") and self.current_page > 0:
            self.current_page -= 1
            self._render_page()

    def _next_page(self):
        if hasattr(self, "current_page") and hasattr(self, "_filtered_data"):
            if (self.current_page + 1) * 1000 < len(self._filtered_data):
                self.current_page += 1
                self._render_page()

    def _render_page(self):
        self.proxy_tree.delete(*self.proxy_tree.get_children())
        
        if not hasattr(self, "_filtered_data"): return
        
        start_idx = self.current_page * 1000
        end_idx = start_idx + 1000
        page_data = self._filtered_data[start_idx:end_idx]
        
        for proto, ip, port, country in page_data:
            self.proxy_tree.insert("", "end", values=(proto, ip, port, country))
            
        count = len(self._filtered_data)
        if count == 0:
            self.result_count_lbl.configure(text=self._t("no_data"))
            self.lbl_page.configure(text="0 / 0")
            if hasattr(self, "results_empty_lbl"):
                self.results_empty_lbl.place(relx=0.5, rely=0.5, anchor="center")
        else:
            total_pages = (count + 999) // 1000
            self.result_count_lbl.configure(text=self._t("proxies_count").format(count))
            self.lbl_page.configure(text=f"{self.current_page + 1} / {total_pages}")
            if hasattr(self, "results_empty_lbl"):
                self.results_empty_lbl.place_forget()

    def _copy_results(self):
        """Копируем все прокси из таблицы в буфер обмена"""
        if not hasattr(self, "_filtered_data"): return
        lines = []
        for vals in self._filtered_data:
            lines.append(f"{vals[0].lower()}://{vals[1]}:{vals[2]}")
        if lines:
            self.clipboard_clear()
            self.clipboard_append("\n".join(lines))
            self.result_count_lbl.configure(text=self._t("copied"))
            self.after(2000, self._load_results)

    def _export_csv(self):
        if not getattr(self, "_filtered_data", []): return
        path = fd.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title=self._t("dialog_save_csv"))
        if not path: return
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self._t('proto'), self._t('ip'), self._t('port'), self._t('country')])
            for vals in self._filtered_data:
                country_name = ISO_TO_NAME[self.current_lang].get(vals[3], vals[3])
                writer.writerow([vals[0].upper(), vals[1], vals[2], country_name])
        self.result_count_lbl.configure(text=self._t("csv_saved"))

    def _export_txt_proto(self):
        if not getattr(self, "_filtered_data", []): return
        path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title=self._t("dialog_save_txt1"))
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            for vals in self._filtered_data:
                f.write(f"{vals[0].lower()}://{vals[1]}:{vals[2]}\n")
        self.result_count_lbl.configure(text=self._t("txt_saved"))

    def _export_txt_full(self):
        if not getattr(self, "_filtered_data", []): return
        path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title=self._t("dialog_save_txt2"))
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            for vals in self._filtered_data:
                f.write(f"{vals[1]}:{vals[2]}\n")
        self.result_count_lbl.configure(text=self._t("txt_saved"))

    def _export_txt_ip(self):
        if not getattr(self, "_filtered_data", []): return
        path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title=self._t("dialog_save_txt3"))
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            ips = set()
            for vals in self._filtered_data:
                ips.add(vals[1])
            for ip in sorted(ips):
                f.write(f"{ip}\n")
        self.result_count_lbl.configure(text=self._t("txt_ip_saved"))

    def _copy_csv_all(self):
        if not getattr(self, "_filtered_data", []): return
        lines = []
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([self._t('proto'), self._t('ip'), self._t('port'), self._t('country')])
        for vals in self._filtered_data:
            country_name = ISO_TO_NAME[self.current_lang].get(vals[3], vals[3])
            writer.writerow([vals[0].upper(), vals[1], vals[2], country_name])
        lines.append(output.getvalue().strip())
        if lines:
            self.clipboard_clear()
            self.clipboard_append("\n".join(lines))
            self.result_count_lbl.configure(text=self._t("copied"))
            self.after(2000, self._load_results)

    def _copy_txt_proto_all(self):
        if not getattr(self, "_filtered_data", []): return
        lines = []
        for vals in self._filtered_data:
            lines.append(f"{vals[0].lower()}://{vals[1]}:{vals[2]}")
        if lines:
            self.clipboard_clear()
            self.clipboard_append("\n".join(lines))
            self.result_count_lbl.configure(text=self._t("copied"))
            self.after(2000, self._load_results)

    def _copy_txt_full_all(self):
        if not getattr(self, "_filtered_data", []): return
        lines = []
        for vals in self._filtered_data:
            lines.append(f"{vals[1]}:{vals[2]}")
        if lines:
            self.clipboard_clear()
            self.clipboard_append("\n".join(lines))
            self.result_count_lbl.configure(text=self._t("copied"))
            self.after(2000, self._load_results)

    def _copy_txt_ip_all(self):
        if not getattr(self, "_filtered_data", []): return
        ips = set()
        for vals in self._filtered_data:
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
        from collections import deque
        self._log_buffer = deque(maxlen=500)
        self._proxy_queue = []
        self._stat_updates = {}
        if not hasattr(self, '_log_lock'):
            import threading
            self._log_lock = threading.Lock()
        self._live_log_counter = 0  # Троттлинг логов Live-прокси
        self._delayed_live_logs = deque(maxlen=500)
        self._flush_log()

    def _flush_log(self):
        """Сбрасываем накопленные логи из быстрой очереди каждые 100мс"""
        import queue
        processed = 0
        qsize = self._fast_queue.qsize()
        limit = max(500, min(qsize, 5000))
        
        while processed < limit:  # Process up to 5000 logs per tick based on load
            try:
                clean = self._fast_queue.get_nowait()
                processed += 1
                
                # Parse steps for UI
                if "ШАГ 1:" in clean or "STEP 1:" in clean:
                    self.progress_lbl.configure(text=self._t("step1"))
                    self.progress_bar.set(0.1)
                    self.progress_pct.configure(text="10%")
                elif "ШАГ 2:" in clean or "STEP 2:" in clean:
                    self.progress_lbl.configure(text=self._t("step2"))
                elif "ШАГ 3:" in clean or "STEP 3:" in clean:
                    self.progress_lbl.configure(text=self._t("step3"))
                
                # Parse stats quickly
                self._parse_stats(clean)
                
                if not clean.startswith("[REALTIME") and not clean.startswith(("    [Загрузка", "    [Проверка", "    [Фильтрация", "[Загрузка", "[Проверка", "[Фильтрация", "    [Downloading", "    [Checking", "    [Filtering", "[Downloading", "[Checking", "[Filtering")):
                    tag = self._get_log_color(clean)
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
        
        # Pull text logs from deque
        batch = []
        p_queue = []
        with self._log_lock:
            for _ in range(min(50, len(self._log_buffer))):
                batch.append(self._log_buffer.popleft())
            
            # Извлекаем ВСЕ накопившиеся прокси, чтобы не было утечки памяти и отставания
            p_queue = self._proxy_queue[:]
            self._proxy_queue.clear()
            
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
                # ОПТИМИЗАЦИЯ GUI: Удаляем пачкой по 500 строк, чтобы Tkinter не лагал от частых удалений
                if lines_count > 1500:
                    self.terminal.delete("1.0", "500.0")
                    
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
                
            sel_protos = getattr(self, "selected_protos", set())
            sel_countries = getattr(self, "selected_countries", set())
            active_protos = {p for p in sel_protos if p in getattr(self, "all_protos_in_db", set())}
            all_p = not sel_protos or len(active_protos) == len(getattr(self, "all_protos_in_db", set()))
            active_countries = {c for c in sel_countries if c in getattr(self, "all_countries_in_db", set())}
            all_c = not sel_countries or len(active_countries) == len(getattr(self, "all_countries_in_db", set()))
                
            inserted = 0
            if hasattr(self, "proxy_tree"):
                tree_len = len(self.proxy_tree.get_children())
            else:
                tree_len = 0
                
            updated_filtered = False
            
            # --- BATCH REMOVE LIVE PROXIES ---
            to_remove = set()
            for data, source in p_queue:
                if source == "remove_live":
                    to_remove.add((data["protocol"].lower(), data["ip"], str(data["port"])))
                    if hasattr(self, "_seen_proxies"):
                        uniq_id = f"live:{data['protocol'].lower()}:{data['ip']}:{data['port']}"
                        self._seen_proxies.discard(uniq_id)
                        
            if to_remove:
                if hasattr(self, "realtime_proxies") and "live" in self.realtime_proxies:
                    self.realtime_proxies["live"] = [
                        d for d in self.realtime_proxies["live"] 
                        if (d["protocol"].lower(), d["ip"], str(d["port"])) not in to_remove
                    ]
                    
                if mapped_src == "live":
                    if hasattr(self, "_current_raw_data"):
                        self._current_raw_data = [
                            r for r in self._current_raw_data 
                            if (r[0].lower(), r[1], str(r[2])) not in to_remove
                        ]
                    if hasattr(self, "_filtered_data"):
                        old_len = len(self._filtered_data)
                        self._filtered_data = [
                            r for r in self._filtered_data 
                            if (r[0].lower(), r[1], str(r[2])) not in to_remove
                        ]
                        if len(self._filtered_data) < old_len:
                            updated_filtered = True

            # --- ADD NEW PROXIES ---
            for data, source in p_queue:
                if source == "remove_live":
                    continue

                self.realtime_proxies.setdefault(source, []).append(data)
                
                if mapped_src == source:
                    country_name = self._format_country(data["country"])
                    row_tuple = (data["protocol"].upper(), data["ip"], data["port"], country_name)
                    
                    if not hasattr(self, "_current_raw_data"): self._current_raw_data = []
                    self._current_raw_data.append(row_tuple)
                    
                    # Backwards compatibility for combobox filters if checkboxes aren't present
                    match_proto = all_p or row_tuple[0] in sel_protos
                    match_country = all_c or row_tuple[3] in sel_countries
                    if current_filter != "all" and current_filter != data["protocol"].lower():
                        match_proto = False
                        
                    if match_proto and match_country:
                        if not hasattr(self, "_filtered_data"): self._filtered_data = []
                        self._filtered_data.append(row_tuple)
                        updated_filtered = True
                        
                        if hasattr(self, "proxy_tree"):
                            if tree_len < 1000 and inserted < 50:
                                self.proxy_tree.insert("", "end", values=row_tuple)
                                tree_len += 1
                                inserted += 1
                                
            if updated_filtered and hasattr(self, "_filtered_data") and hasattr(self, "result_count_lbl"):
                self.result_count_lbl.configure(text=self._t("proxies_count").format(len(self._filtered_data)))
                                
            # BUG FIX: Accurate GUI metrics directly from tables
            # Remove set() deduplication here because self.realtime_proxies already contains purely unique elements thanks to _seen_proxies.
            # And it properly counts different protocols on the same IP as distinct, matching the backend's set() logic exactly.
            self.stat_live.configure(text=str(len(self.realtime_proxies.get("live", []))))
            
            total_elite_count = len(self.realtime_proxies.get("elite", []))
            self.stat_elite.configure(text=str(total_elite_count))
            
            if hasattr(self, 'stat_dc'):
                self.stat_dc.configure(text=str(len(self.realtime_proxies.get("datacenter", []))))
                self.stat_res.configure(text=str(len(self.realtime_proxies.get("residential", []))))
                self.stat_mob.configure(text=str(len(self.realtime_proxies.get("mobile", []))))
                            
        self.after(100, self._flush_log)

    def _enqueue_log(self, text, tag):
        """Добавляем лог в очередь (вызывается из рабочего потока — потокобезопасно)"""
        if getattr(self, "_is_cancelling", False): return
        with self._log_lock:
            self._log_buffer.append((text, tag))

    def _enqueue_live_log(self, msg, tag):
        """Накапливаем логи для отложенного вывода после полной проверки"""
        if not hasattr(self, "_delayed_live_logs"):
            self._delayed_live_logs = deque(maxlen=500)
        self._delayed_live_logs.append((msg, tag))

    def _get_log_color(self, text):
        if "[+]" in text or "ШАГ" in text or "STEP" in text: return "blue"
        if "[✓]" in text or "Готово" in text or "Done" in text: return "green"
        if "[x]" in text or "Ошибка" in text or "Error" in text or "[!]" in text: return "red"
        if "🚀" in text: return "purple"
        return "default"

    def _parse_stats(self, text):
        if getattr(self, "_is_cancelling", False): return
        
        # Fast string matching without regex and without locks
        if "[REALTIME_TOTAL]" in text:
            try:
                num = int(text.split("[REALTIME_TOTAL]")[-1].strip())
                self._base_total_persistent = num
                total_val = num + getattr(self, '_gen_total_persistent', 0)
                self._stat_updates['total'] = str(total_val)
                if hasattr(self, 'lbl_results_count'):
                    self.lbl_results_count.configure(text=self._t("proxies_count").format(total_val))
            except: pass
        elif "Уникальных IP:PORT" in text or "log_unique_ip" in text or "Unique IP:PORT" in text:
            try:
                num = int(text.split(":")[-1].strip())
                self._base_total_persistent = num
                self._stat_updates['total'] = str(num + getattr(self, '_gen_total_persistent', 0))
            except: pass
        elif "Сгенерировано рандомных:" in text or "random_generated:" in text or "Generated random:" in text:
            try:
                num = int(text.split(":")[-1].strip())
                self._gen_total_persistent = num
                self._stat_updates['total'] = str(num + getattr(self, '_base_total_persistent', 0))
            except: pass
        elif "[REALTIME_NEW_LIVE]" in text:
            try:
                parts = text.split("[REALTIME_NEW_LIVE]")[1].strip().split("|")
                data = {"ip": parts[0], "port": parts[1], "protocol": parts[2], "country": parts[3]}
                uniq_id = f"live:{data['protocol']}:{data['ip']}:{data['port']}"
                if not hasattr(self, "_seen_proxies"): self._seen_proxies = set()
                if uniq_id not in self._seen_proxies:
                    self._seen_proxies.add(uniq_id)
                    self._proxy_queue.append((data, "live"))
            except: pass
        elif "[REALTIME_NEW_ELITE]" in text:
            try:
                parts = text.split("[REALTIME_NEW_ELITE]")[1].strip().split("|")
                data = {"ip": parts[0], "port": parts[1], "protocol": parts[2], "country": parts[3], "category": parts[4]}
                uniq_id = f"elite:{data['protocol']}:{data['ip']}:{data['port']}"
                if not hasattr(self, "_seen_proxies"): self._seen_proxies = set()
                if uniq_id not in self._seen_proxies:
                    self._seen_proxies.add(uniq_id)
                    self._proxy_queue.append((data, "elite"))
            except: pass
        elif "[REALTIME_NEW_CATEGORY]" in text:
            try:
                parts = text.split("[REALTIME_NEW_CATEGORY]")[1].strip().split("|")
                data = {"ip": parts[0], "port": parts[1], "protocol": parts[2], "country": parts[3], "category": parts[4]}
                uniq_id = f"cat:{data['protocol']}:{data['ip']}:{data['port']}"
                if not hasattr(self, "_seen_proxies"): self._seen_proxies = set()
                if uniq_id not in self._seen_proxies:
                    self._seen_proxies.add(uniq_id)
                    cat = data.get("category", "datacenter").lower()
                    self._proxy_queue.append((data, cat))
            except: pass
        elif "[REALTIME_REMOVE_LIVE]" in text:
            try:
                parts = text.split("[REALTIME_REMOVE_LIVE]")[1].strip().split("|")
                data = {"ip": parts[1], "port": parts[2], "protocol": parts[0]}
                self._proxy_queue.append((data, "remove_live"))
            except: pass
    def _toggle_pause(self):
        if not self.is_running or not self.hunter_thread: return
        self.is_paused = not getattr(self, "is_paused", False)
        if self.is_paused:
            self.pause_btn.configure(text="", image=self.icons["play"], fg_color=GREEN, hover_color="#059669")
            if hasattr(self, "hunter_instance"):
                self.hunter_instance.pause()
        else:
            self.pause_btn.configure(text="", image=self.icons["pause"], fg_color=GOLD, hover_color="#D97706")
            if hasattr(self, "hunter_instance"):
                self.hunter_instance.resume()

    def _cancel_hunter(self):
        if not self.is_running or not self.hunter_thread: return
        self.cancel_btn.configure(state="disabled")
        self._is_cancelling = True
        if hasattr(self, "hunter_instance"):
            self.hunter_instance.cancel()
            
        # Полное мгновенное обнуление всего интерфейса
        self._base_total_persistent = 0
        self._gen_total_persistent = 0
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
        out_dir = self.output_dir.get().strip()
        import os
        if not out_dir or not os.path.isdir(out_dir):
            self._flash_error_widget(self.start_btn, temp_text=self._t("error_no_folder"))
            return
            
        try:
            test_file = os.path.join(out_dir, '.write_test_tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception:
            self._flash_error_widget(self.start_btn, temp_text="No Write Permission!")
            return

        if not self._get_selected_countries():
            self._flash_error_widget(self.start_btn, temp_text=self._t("error_no_countries"))
            return
            
        try:
            threads = max(1, min(1000, int(float(self.entry_threads.get()))))
            timeout = max(1, min(300, int(float(self.entry_timeout.get()))))
            ping = max(0.0, float(self.entry_ping.get()))
            speed = max(0.0, float(self.entry_speed.get()))
        except ValueError:
            self._flash_error_widget(self.start_btn, temp_text="Invalid Settings!")
            return
            
        self.is_running = True
        self.is_paused = False
        self._is_cancelling = False
        self._live_count = 0
        self._elite_count = 0
        self.realtime_proxies = {"live": [], "elite": [], "datacenter": [], "residential": [], "mobile": []}
        self._seen_proxies = set()
        
        self._set_ui_state("disabled")
        self.start_btn.configure(text="", image=self.icons["stop"], fg_color=RED, hover_color="#B91C1C", state="disabled")
        self.pause_btn.configure(state="normal", text="", image=self.icons["pause"], fg_color=GOLD, hover_color="#D97706")
        self.cancel_btn.configure(state="normal")
        
        self.terminal.configure(state="normal")
        self.terminal.delete("1.0", "end")
        self.terminal.configure(state="disabled")
        self._base_total_persistent = 0
        self._gen_total_persistent = 0
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
                
                for line in text.split('\n'):
                    clean = line.strip()
                    if not clean: continue
                    
                    is_realtime = clean.startswith("[REALTIME")
                    
                    # Push everything to the fast queue to be processed by the main thread
                    app._fast_queue.put(clean)
                    
                    if not is_realtime and not clean.startswith(("    [Загрузка", "    [Проверка", "    [Фильтрация", "[Загрузка", "[Проверка", "[Фильтрация", "    [Downloading", "    [Checking", "    [Filtering", "[Downloading", "[Checking", "[Filtering")):
                        try: sys.__stdout__.write(line + "\n")
                        except: pass
            
            def flush(self):
                try: sys.__stdout__.flush()
                except: pass
            def isatty(self):
                return False
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
        random_counts_val = {"http": 0, "https": 0, "socks4": 0, "socks5": 0}
        if getattr(self, "random_gen_enabled", None) and self.random_gen_enabled.get() and hasattr(self, "random_counts"):
            random_counts_val = {
                "http": max(0, min(10_000_000, int(float(self.random_counts["http"].get())))),
                "https": max(0, min(10_000_000, int(float(self.random_counts["https"].get())))),
                "socks4": max(0, min(10_000_000, int(float(self.random_counts["socks4"].get())))),
                "socks5": max(0, min(10_000_000, int(float(self.random_counts["socks5"].get()))))
            }

        def target():
            old = sys.stdout
            sys.stdout = Redir()
            try:
                try:
                    gh_days = int(self.github_tm_days_var.get())
                except Exception:
                    gh_days = 1
                    
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
                    random_counts=random_counts_val,
                    output_dir=self.output_dir.get(),
                    lang=self.current_lang,
                    github_token=self.github_token_var.get().strip().replace('\n', '').replace('\r', '') if hasattr(self, 'github_token_var') else "",
                    github_tm_enabled=self.github_tm_enabled.get() if hasattr(self, 'github_tm_enabled') else True,
                    github_tm_days=gh_days
                )
                with patch_tqdm():
                    self.hunter_instance.run()
                if hasattr(self, "_delayed_live_logs") and self._delayed_live_logs:
                    with self._log_lock:
                        for msg, tag in self._delayed_live_logs:
                            self._log_buffer.append((msg, tag))
                    self._delayed_live_logs.clear()
                print(f"\n{self._t('done_msg')}")
                # Автоматически загружаем результаты и переключаемся на вкладку
                self.after(500, self._load_results)
                self.after(600, lambda: self.main_tabs.set(self._t("tab_results")))
            except Exception as ex:
                import traceback
                print(f"\n[x] Error / Ошибка: {ex}")
                traceback.print_exc()
            finally:
                sys.stdout = old
                self.is_running = False
                self.hunter_thread = None
                self.hunter_instance = None
                self.after(0, lambda: self._set_ui_state("normal"))
                self.after(0, lambda: self.start_btn.configure(text="", image=self.icons["play"], fg_color=BLUE, hover_color="#1D4ED8"))
                self.after(0, lambda: self.pause_btn.configure(state="disabled"))
                self.after(0, lambda: self.cancel_btn.configure(state="disabled"))
                
        self.hunter_thread = threading.Thread(target=target, daemon=True)
        self.hunter_thread.start()


    def _build_checker_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1, uniform="checker_main")
        parent.grid_columnconfigure(1, weight=3, uniform="checker_main")
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

        # --- ФИЛЬТРЫ ПРОВЕРКИ (Всегда включены, скрыты из интерфейса) ---
        self.do_check_anon = ctk.BooleanVar(value=True)
        self.do_check_bl = ctk.BooleanVar(value=True)
        self.do_check_speed = ctk.BooleanVar(value=True)
        self.do_check_smtp = ctk.BooleanVar(value=True)
        self.do_check_category = ctk.BooleanVar(value=True)

        # === ПОТОМ pack-им верхние элементы — инпут заполняет ОСТАВШЕЕСЯ пространство ===
        chk_input_header = ctk.CTkFrame(left_panel, fg_color="transparent")
        chk_input_header.pack(fill="x", pady=(0, 5))
        
        self._chk_lbl_input = ctk.CTkLabel(chk_input_header, text=self._t("checker_input_lbl"), font=("Segoe UI", 12, "bold"))
        self._chk_lbl_input.pack(side="left")
        
        self.chk_lbl_count = ctk.CTkLabel(chk_input_header, text=self._t("chk_unique_0"), font=("Segoe UI", 11), text_color=MUTED)
        self.chk_lbl_count.pack(side="right")


        input_frame = ctk.CTkFrame(left_panel, fg_color="#060B14", corner_radius=8, border_width=1, border_color=BORDER)
        input_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        self.checker_input = tk.Text(input_frame, bg="#060B14", fg=MUTED, insertbackground="#E2E8F0",
                                     font=("Consolas", 11), relief="flat", padx=8, pady=8, bd=0, highlightthickness=0)
        
        self.checker_scrollbar = ctk.CTkScrollbar(input_frame, command=self.checker_input.yview)
        self.checker_input.configure(yscrollcommand=self.checker_scrollbar.set)
        
        self.checker_scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)
        self.checker_input.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        
        self.checker_placeholder = self._t("checker_placeholder_text")
        self.checker_input.insert("1.0", self.checker_placeholder)
        
        def _on_focus_in(e):
            if self.checker_input.get("1.0", "end-1c") == self.checker_placeholder:
                self.checker_input.delete("1.0", "end")
                self.checker_input.configure(fg="#E2E8F0")
                
        def _on_focus_out(e):
            if str(self.checker_input.cget("state")) == "normal" and not self.checker_input.get("1.0", "end-1c").strip():
                self.checker_input.delete("1.0", "end")
                self.checker_input.insert("1.0", self.checker_placeholder)
                self.checker_input.configure(fg=MUTED)
                
        self.checker_input.bind("<FocusIn>", _on_focus_in)
        self.checker_input.bind("<FocusOut>", _on_focus_out)
        self.checker_input.bind("<KeyRelease>", self._update_checker_count, add="+")
        self.checker_input.bind("<<Paste>>", self._smart_paste)
        def _on_ctrl_key(e):
            if getattr(e, 'keycode', 0) in (65, 97):
                self._select_all(e)
                return "break"
            elif getattr(e, 'keycode', 0) in (67, 99):
                self._smart_copy(e)
                return "break"
            elif getattr(e, 'keycode', 0) in (86, 118):
                self._smart_paste(e)
                return "break"
            elif getattr(e, 'keycode', 0) in (88, 120):
                self.checker_input.event_generate("<<Cut>>")
                return "break"

        self.checker_input.bind("<Control-KeyPress>", _on_ctrl_key)
        self.checker_input.bind("<<Paste>>", self._smart_paste)
        self.checker_input.bind("<Shift-Insert>", self._smart_paste)
        self.checker_input.bind("<Command-v>", self._smart_paste)
        self.checker_input.bind("<Command-a>", self._select_all)
        self.checker_input.bind("<Command-c>", self._smart_copy)
        self.checker_input.bind("<Command-x>", lambda e: self.checker_input.event_generate("<<Cut>>"))

        right_panel = ctk.CTkFrame(parent, fg_color="#060B14", corner_radius=10)
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        # --- PROGRESS BAR ---
        self.checker_prog_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.checker_prog_frame.pack(fill="x", padx=8, pady=(8, 0))
        
        self.checker_lbl_prog = ctk.CTkLabel(self.checker_prog_frame, text="0%", font=("Segoe UI", 11, "bold"), text_color=MUTED)
        self.checker_lbl_prog.pack(side="right", padx=(5, 0))
        
        self.checker_progress = ctk.CTkProgressBar(self.checker_prog_frame, height=6, fg_color=BORDER, progress_color=GREEN)
        self.checker_progress.pack(side="left", fill="x", expand=True)
        self.checker_progress.set(0)

        # --- TOP FILTERS (Countries, Protocols) ---
        self.checker_top_filters_frame = ctk.CTkFrame(right_panel, fg_color="transparent", height=30)
        # We pack it dynamically in _update_checker_metrics when needed
        
        self.checker_all_countries = []
        self.checker_selected_countries = set()
        self.checker_all_protos = []
        self.checker_selected_protos = set()
        
        self.btn_checker_country_filter = ctk.CTkButton(self.checker_top_filters_frame, text=self._t("all_countries"), width=140, fg_color=BORDER, hover_color="#4A5568", command=self._on_checker_country_btn_click)
        self.btn_checker_country_filter.pack(side="right", padx=(5, 0))
        self.btn_checker_country_filter.pack_forget() # Hide initially
        
        self.btn_checker_proto_filter = ctk.CTkButton(self.checker_top_filters_frame, text=self._t("all_protocols"), width=140, fg_color=BORDER, hover_color="#4A5568", command=self._on_checker_proto_btn_click)
        self.btn_checker_proto_filter.pack(side="right", padx=(10, 5))
        self.btn_checker_proto_filter.pack_forget() # Hide initially
    
        cols = ("#", "proxy", "country", "category", "ping", "anon", "bl", "speed", "smtp")
        self.check_tree_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.check_tree = tk.ttk.Treeview(self.check_tree_frame, columns=cols, show="headings", style="Proxy.Treeview")
        self._bind_treeview_events(self.check_tree)
        
        self.check_tree.heading("#", text="#")
        self.check_tree.heading("proxy", text=self._t("checker_h_proxy"))
        self.check_tree.heading("country", text=self._t("checker_h_country"))
        self.check_tree.heading("category", text=self._t("checker_h_category"))
        self.check_tree.heading("ping", text=self._t("checker_h_ping"))
        self.check_tree.heading("anon", text=self._t("checker_h_anon"))
        self.check_tree.heading("bl", text=self._t("checker_h_bl"))
        self.check_tree.heading("speed", text=self._t("checker_h_speed"))
        self.check_tree.heading("smtp", text="SMTP")
    
        self.check_tree.column("#", width=40, minwidth=40, anchor="center")
        self.check_tree.column("proxy", width=160, anchor="w")
        self.check_tree.column("country", width=120, anchor="center")
        self.check_tree.column("category", width=90, anchor="center")
        self.check_tree.column("ping", width=70, anchor="center")
        self.check_tree.column("anon", width=100, anchor="center")
        self.check_tree.column("bl", width=110, anchor="center")
        self.check_tree.column("speed", width=90, anchor="center")
        self.check_tree.column("smtp", width=70, anchor="center")
    
        # (Progress bar moved above filters)
        # --- ФИЛЬТРЫ СКАЧИВАНИЯ (Что сохранять) ---
        download_panel = ctk.CTkFrame(right_panel, fg_color=CARD, corner_radius=8, border_width=1, border_color=BORDER)
        download_panel.pack(side="bottom", fill="x", padx=8, pady=8)
        
        # Layout: Left side for criteria and checkboxes, Right side for buttons
        left_side = ctk.CTkFrame(download_panel, fg_color="transparent")
        left_side.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        right_side = ctk.CTkFrame(download_panel, fg_color="transparent")
        right_side.pack(side="right", fill="y", padx=15, pady=10)
        
        self._chk_lbl_criteria = ctk.CTkLabel(left_side, text=self._t("checker_save_criteria"), font=("Segoe UI", 12, "bold"), text_color=TEXT)
        self._chk_lbl_criteria.pack(anchor="w", pady=(0, 8))
        
        cb_frame = ctk.CTkFrame(left_side, fg_color="transparent")
        cb_frame.pack(fill="x")
        
        self._chk_lbl_total_save = ctk.CTkLabel(right_side, text=self._t("proxies_count").format(0), font=("Segoe UI", 11, "bold"), text_color=MUTED)
        self._chk_lbl_total_save.pack(side="top", anchor="center", pady=(0, 6))
    
        self.btn_copy_checker = ctk.CTkButton(right_side, text=self._t("checker_copy"), image=self.icons.get("copy", None), fg_color=BORDER, hover_color="#374151", font=("Segoe UI", 12, "bold"), width=140, height=30, command=self._copy_checker_results)
        self.btn_copy_checker.pack(side="top", fill="x", pady=(0, 6))
    
        self.btn_save_checker = ctk.CTkButton(right_side, text=self._t("checker_download"), image=self.icons["download"], fg_color=BLUE, hover_color="#2563EB", font=("Segoe UI", 12, "bold"), width=140, height=30, command=self._save_checker_results)
        self.btn_save_checker.pack(side="top", fill="x")
        
        self.save_req_alive = ctk.BooleanVar(value=False)
        self.save_req_elite = ctk.BooleanVar(value=False)
        self.save_req_clean = ctk.BooleanVar(value=False)
        self.save_req_smtp = ctk.BooleanVar(value=False)
        
        self._chk_cb_alive = ctk.CTkCheckBox(cb_frame, text=self._t("checker_only_alive"), variable=self.save_req_alive, font=("Segoe UI", 11), checkbox_width=18, checkbox_height=18, command=self._apply_checker_filter)
        self._chk_cb_alive.grid(row=0, column=0, sticky="w", padx=(0, 12), pady=2)
        
        self.save_req_res = ctk.BooleanVar(value=False)
        self.save_req_mob = ctk.BooleanVar(value=False)
        self.save_req_dc = ctk.BooleanVar(value=False)
        
        self._chk_cb_elite = ctk.CTkCheckBox(cb_frame, text=self._t("checker_only_elite"), variable=self.save_req_elite, font=("Segoe UI", 11), checkbox_width=18, checkbox_height=18, command=self._apply_checker_filter)
        self._chk_cb_elite.grid(row=0, column=1, sticky="w", padx=(0, 12), pady=2)
        
        self._chk_cb_res = ctk.CTkCheckBox(cb_frame, text=self._t("checker_only_res"), variable=self.save_req_res, font=("Segoe UI", 11), checkbox_width=18, checkbox_height=18, command=self._apply_checker_filter)
        self._chk_cb_res.grid(row=0, column=2, sticky="w", padx=(0, 12), pady=2)
        
        self._chk_cb_mob = ctk.CTkCheckBox(cb_frame, text=self._t("checker_only_mob"), variable=self.save_req_mob, font=("Segoe UI", 11), checkbox_width=18, checkbox_height=18, command=self._apply_checker_filter)
        self._chk_cb_mob.grid(row=0, column=3, sticky="w", padx=(0, 12), pady=2)
        
        self._chk_cb_clean = ctk.CTkCheckBox(cb_frame, text=self._t("checker_only_clean"), variable=self.save_req_clean, font=("Segoe UI", 11), checkbox_width=18, checkbox_height=18, command=self._apply_checker_filter)
        self._chk_cb_clean.grid(row=1, column=0, sticky="w", padx=(0, 12), pady=2)
        
        self._chk_cb_smtp = ctk.CTkCheckBox(cb_frame, text=self._t("checker_only_smtp"), variable=self.save_req_smtp, font=("Segoe UI", 11), checkbox_width=18, checkbox_height=18, command=self._apply_checker_filter)
        self._chk_cb_smtp.grid(row=1, column=1, sticky="w", padx=(0, 12), pady=2)

        self._chk_cb_dc = ctk.CTkCheckBox(cb_frame, text=self._t("checker_only_dc"), variable=self.save_req_dc, font=("Segoe UI", 11), checkbox_width=18, checkbox_height=18, command=self._apply_checker_filter)
        self._chk_cb_dc.grid(row=1, column=2, sticky="w", padx=(0, 12), pady=2)
        
        self.checker_scrollbar_tree = ctk.CTkScrollbar(self.check_tree_frame, orientation="vertical", command=self.check_tree.yview, fg_color="#060B14", button_color=BORDER, button_hover_color=MUTED)
        self.check_tree.configure(yscrollcommand=self.checker_scrollbar_tree.set)
        self.checker_scrollbar_tree.pack(side="right", fill="y", padx=(0, 4))
        self.check_tree.pack(side="left", fill="both", expand=True)
        self.check_tree_frame.pack(fill="both", expand=True, padx=8, pady=(8, 0))
        
        self.checker_pagination_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.checker_pagination_frame.pack(fill="x", padx=8, pady=(4, 0))
        
        self.btn_page_first = ctk.CTkButton(self.checker_pagination_frame, text="<<", width=30, command=self._checker_page_first)
        self.btn_page_first.pack(side="left", padx=2)
        
        self.btn_page_prev = ctk.CTkButton(self.checker_pagination_frame, text="<", width=30, command=self._checker_page_prev)
        self.btn_page_prev.pack(side="left", padx=2)
        
        self.lbl_checker_page = ctk.CTkLabel(self.checker_pagination_frame, text="Page 1 of 1", font=("Segoe UI", 12))
        self.lbl_checker_page.pack(side="left", padx=10)
        
        self.btn_page_next = ctk.CTkButton(self.checker_pagination_frame, text=">", width=30, command=self._checker_page_next)
        self.btn_page_next.pack(side="left", padx=2)
        
        self.btn_page_last = ctk.CTkButton(self.checker_pagination_frame, text=">>", width=30, command=self._checker_page_last)
        self.btn_page_last.pack(side="left", padx=2)
    
    def _checker_page_first(self):
        if not getattr(self, "checker_current_page", None) is not None: return
        if self.checker_current_page > 0:
            self.checker_current_page = 0
            self._render_checker_page()

    def _checker_page_prev(self):
        if not getattr(self, "checker_current_page", None) is not None: return
        if self.checker_current_page > 0:
            self.checker_current_page -= 1
            self._render_checker_page()

    def _checker_page_next(self):
        if not getattr(self, "checker_current_page", None) is not None: return
        total_pages = max(1, (len(self.checker_filtered_proxies) + self.checker_page_size - 1) // self.checker_page_size)
        if self.checker_current_page < total_pages - 1:
            self.checker_current_page += 1
            self._render_checker_page()

    def _checker_page_last(self):
        if not getattr(self, "checker_current_page", None) is not None: return
        total_pages = max(1, (len(self.checker_filtered_proxies) + self.checker_page_size - 1) // self.checker_page_size)
        if self.checker_current_page < total_pages - 1:
            self.checker_current_page = total_pages - 1
            self._render_checker_page()
            
    def _render_checker_page(self):
        if not hasattr(self, "checker_filtered_proxies"): return
        
        # Clear current treeview items
        for item in self.check_tree.get_children():
            self.check_tree.delete(item)
        self.check_tree_items.clear()
        
        # Determine slice
        total_proxies = len(self.checker_filtered_proxies)
        total_pages = max(1, (total_proxies + self.checker_page_size - 1) // self.checker_page_size)
        
        if self.checker_current_page >= total_pages:
            self.checker_current_page = max(0, total_pages - 1)
            
        start_idx = self.checker_current_page * self.checker_page_size
        end_idx = min(start_idx + self.checker_page_size, total_proxies)
        
        # Insert slice
        for proxy_str in self.checker_filtered_proxies[start_idx:end_idx]:
            vals = self.checker_data.get(proxy_str)
            if vals:
                item_id = self.check_tree.insert("", "end", values=vals)
                self.check_tree_items[proxy_str] = item_id
                
        # Update UI labels and buttons
        self.lbl_checker_page.configure(text=f"Page {self.checker_current_page + 1} of {total_pages}")
        self.btn_page_first.configure(state="normal" if self.checker_current_page > 0 else "disabled")
        self.btn_page_prev.configure(state="normal" if self.checker_current_page > 0 else "disabled")
        self.btn_page_next.configure(state="normal" if self.checker_current_page < total_pages - 1 else "disabled")
        self.btn_page_last.configure(state="normal" if self.checker_current_page < total_pages - 1 else "disabled")
    
    def _update_checker_count(self, event=None):
        if not hasattr(self, "checker_input") or not hasattr(self, "chk_lbl_count"): return
        raw_text = self.checker_input.get("1.0", "end").strip()
        ph_text = getattr(self, "checker_placeholder", "").strip()
        if not raw_text or raw_text.replace('\r', '') == ph_text.replace('\r', ''):
            self.chk_lbl_count.configure(text=self._t("chk_unique_0"))
            return
            
        import re
        pattern = re.compile(r'(?:[a-zA-Z0-9]+://)?(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::\d{1,5})?')
        found = pattern.findall(raw_text)
        unique_proxies = list(dict.fromkeys(found))
        
        if len(found) > len(unique_proxies):
            count_text = self._t("chk_unique_n_total").format(len(unique_proxies), len(found))
        else:
            count_text = self._t("chk_unique_n").format(len(unique_proxies))
        self.chk_lbl_count.configure(text=count_text)


    def _copy_checker_results(self):
        if not hasattr(self, "checker_filtered_proxies"): return
        lines = []
        for p in self.checker_filtered_proxies:
            try:
                vals = self.checker_data.get(p)
                if vals and len(vals) >= 8:
                    lines.append(str(vals[1]))
            except: continue
        
        if not lines:
            self.btn_copy_checker.configure(text="⚠ 0", fg_color="#7F1D1D")
            self.after(2000, lambda: self.btn_copy_checker.configure(text=self._t("checker_copy"), image=self.icons.get("copy", None), fg_color=BORDER))
            return
            
        text = "\n".join(lines) + "\n"
        self.clipboard_clear()
        self.clipboard_append(text)
        self.btn_copy_checker.configure(text=f"✓ {len(lines)}", fg_color=GREEN)
        self.after(2000, lambda: self.btn_copy_checker.configure(text=self._t("checker_copy"), image=self.icons.get("copy", None), fg_color=BORDER))

    def _save_checker_results(self):
        from tkinter import filedialog as fd
        path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], initialfile="checked_proxies.txt")
        if not path: return
        
        if not hasattr(self, "checker_filtered_proxies"): return
        
        saved_count = 0
        with open(path, 'w', encoding='utf-8') as f:
            for p in self.checker_filtered_proxies:
                try:
                    vals = self.checker_data.get(p)
                    if vals and len(vals) >= 8:
                        f.write(str(vals[1]) + "\n")
                        saved_count += 1
                except: continue
        
        # BUG-16: Warn if nothing saved
        if saved_count == 0:
            self.btn_save_checker.configure(text="⚠ 0", fg_color="#7F1D1D")
            self.after(2000, lambda: self.btn_save_checker.configure(text=self._t("checker_download"), image=self.icons["download"], fg_color=BLUE))
        else:
            self.btn_save_checker.configure(text=self._t("checker_saved").format(saved_count), fg_color=GREEN)
        self.after(2000, lambda: self.btn_save_checker.configure(text=self._t("checker_download"), image=self.icons["download"], fg_color=BLUE))

    def _load_checker_file(self):
        from tkinter import filedialog as fd
        import re
        paths = fd.askopenfilenames(filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")])
        if not paths: return
        
        import os
        
        current_content = self.checker_input.get("1.0", "end-1c").strip()
        ph_text = self.checker_placeholder.strip()
        if current_content.replace('\r', '') == ph_text.replace('\r', ''):
            current_content = ""
            
        all_text = current_content + "\n"
        
        total_size = 0
        for path in paths:
            fsize = os.path.getsize(path)
            if fsize > 10 * 1024 * 1024:
                self._flash_error_widget(self._chk_btn_load, temp_text=self._t("error_file_size"))
                continue
            if total_size + fsize > 50 * 1024 * 1024:
                self._flash_error_widget(self._chk_btn_load, temp_text="Max 50MB total allowed!")
                break
            total_size += fsize
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    all_text += f.read() + "\n"
            except Exception:
                self._flash_error_widget(self._chk_btn_load, temp_text=self._t("error_file_type"))
                continue

        pattern = re.compile(r'(?:[a-zA-Z0-9]+://)?(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::\d{1,5})?')
        found = pattern.findall(all_text)
        unique_proxies = list(dict.fromkeys(found))
        
        self.checker_input.delete("1.0", "end")
        if unique_proxies:
            self.checker_input.insert("end", "\n".join(unique_proxies) + "\n")
        
        self._update_checker_count()

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
            if hasattr(self, "_active_dummy_hunter"):
                self._active_dummy_hunter._cancel_event.set()
            return

        raw_text = self.checker_input.get("1.0", "end").strip()
        ph_text = self.checker_placeholder.strip()
        if not raw_text or raw_text.replace('\r', '') == ph_text.replace('\r', ''):
            self._flash_error_widget(self.btn_check_start, temp_text=self._t("error_no_proxies"))
            return
        
        # BUG-02: Delete detached items too
        for item_id, _ in getattr(self, '_checker_detached', []):
            try:
                self.check_tree.delete(item_id)
            except Exception:
                pass
        self._checker_detached = []
        
        for item in self.check_tree.get_children():
            self.check_tree.delete(item)

        import re
        self.check_tree_items = {} 
        
        # Мощный regex для умного поиска валидных IP:PORT (с возможным протоколом) в любом мусоре
        pattern = re.compile(r'(?:[a-zA-Z0-9]+://)?(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::\d{1,5})?')
        found = pattern.findall(raw_text)
        
        # Дедупликация и нормализация (всегда добавляем протокол)
        seen = set()
        proxies_list = []
        for match in found:
            if "://" in match:
                proto, ip_port = match.split("://", 1)
                proto = proto.lower()
            else:
                proto = "http"
                ip_port = match
            normalized = f"{proto}://{ip_port}"
            if normalized not in seen:
                seen.add(normalized)
                proxies_list.append(normalized)
        
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
            checker_timeout = max(1, min(300, int(float(self.entry_timeout.get()))))
        except ValueError:
            checker_timeout = 10

        self.checker_data = {}
        self.checker_all_proxies = proxies_list
        self.checker_filtered_proxies = list(proxies_list)
        self.checker_current_page = 0
        self.checker_page_size = 100
        
        for idx, p in enumerate(proxies_list, 1):
            vals = [idx, p, "⏳", "⏳", "⏳", "⏳", "⏳", "⏳", "⏳"]
            self.checker_data[p] = vals
            
        self._render_checker_page()

        self.checker_is_running = True
        self._checker_detached = []
        self._checker_pending_updates = {}
        
        def _periodic_flush():
            if not getattr(self, "checker_is_running", False):
                self._flush_checker_updates()
                # Final progress update
                if hasattr(self, 'checker_progress'):
                    self.checker_progress.set(1.0)
                    self.checker_lbl_prog.configure(text="100%")
                return
            self._flush_checker_updates()
            # Update progress bar from main thread (no lock needed for reading int)
            if hasattr(self, '_checker_total') and self._checker_total > 0:
                try:
                    done = self._checker_done
                    total = self._checker_total
                    pct = min(100, int((done / total) * 100))
                    prog_val = min(1.0, done / total)
                    self.checker_progress.set(prog_val)
                    self.checker_lbl_prog.configure(text=f"{pct}%")
                except Exception:
                    pass
            self.after(500, _periodic_flush)
            
        self.after(500, _periodic_flush)
        
        self.checker_progress.set(0)
        self.checker_lbl_prog.configure(text="0%")
        self._checker_total = len(proxies_list) * 5
        self._checker_done = 0
        
        self.btn_check_start.configure(text=self._t("cancel"), image=self.icons["cancel"], fg_color=RED, hover_color="#991B1B")
        self._chk_btn_load.configure(state="disabled")
        self._chk_btn_clear.configure(state="disabled")
        self.btn_save_checker.configure(state="disabled")
        
        self._chk_cb_alive.configure(state="disabled")
        self._chk_cb_elite.configure(state="disabled")
        self._chk_cb_clean.configure(state="disabled")
        self._chk_cb_smtp.configure(state="disabled")
        if hasattr(self, '_chk_cb_res'): self._chk_cb_res.configure(state="disabled")
        if hasattr(self, '_chk_cb_mob'): self._chk_cb_mob.configure(state="disabled")
        if hasattr(self, '_chk_cb_dc'): self._chk_cb_dc.configure(state="disabled")
        self.checker_input.configure(state="disabled")

        # Dynamic column visibility
        visible_cols = ["#", "proxy", "country"]
        if getattr(self, "do_check_category", None) and self.do_check_category.get(): visible_cols.append("category")
        visible_cols.append("ping")
        if self.do_check_anon.get(): visible_cols.append("anon")
        if self.do_check_bl.get(): visible_cols.append("bl")
        if self.do_check_speed.get(): visible_cols.append("speed")
        if self.do_check_smtp.get(): visible_cols.append("smtp")
        self.check_tree["displaycolumns"] = visible_cols

        threading.Thread(target=self._run_checker_thread, args=(list(self.checker_all_proxies), checker_timeout), daemon=True).start()

    def _run_checker_thread(self, proxies, timeout=10):
        from fetch_proxy import ProxyUtils, ProxyHunter
        import requests, time, os
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        dummy_hunter = ProxyHunter(threads=1)
        if hasattr(self, 'hunter') and self.hunter:
            dummy_hunter.ip_cache = self.hunter.ip_cache
            dummy_hunter.asn_cache = self.hunter.asn_cache
        self._active_dummy_hunter = dummy_hunter
        if os.path.exists('GeoLite2-Country.mmdb'):
            try:
                import maxminddb
                dummy_hunter.db_reader = maxminddb.open_database('GeoLite2-Country.mmdb')
            except Exception:
                pass

        # Фиксированно 1000 потоков для чекера, как просил пользователь
        max_threads = 1000
        max_workers = min(max_threads, len(proxies))
        
                # Pre-fetch categories dynamically in background
        if getattr(self, "do_check_category", None) and self.do_check_category.get() and self.checker_is_running:
            def _fetch_categories_bg():
                unique_ips = set()
                ip_to_proxies = {}
                for p in proxies:
                    clean_p = p.split("://")[-1]
                    ip = clean_p.split(":")[0]
                    if ip not in ip_to_proxies: ip_to_proxies[ip] = []
                    ip_to_proxies[ip].append(p)
                    
                    ip_info = dummy_hunter.ip_cache.get(ip, {})
                    if 'datacenter' not in ip_info:
                        unique_ips.add(ip)
                    else:
                        mobile = ip_info.get("mobile", False)
                        hosting = ip_info.get("datacenter", False)
                        asn_str = ip_info.get("asn", "")
                        asn_num = asn_str.split()[0] if asn_str else ""
                        asn_type = dummy_hunter.asn_cache.get(asn_num, "").lower()
                        cat = "Unknown"
                        if mobile: cat = self._t("checker_only_mob")
                        elif asn_type == "isp": cat = self._t("checker_only_res")
                        elif asn_type in ("hosting", "business"): cat = self._t("checker_only_dc")
                        elif hosting: cat = self._t("checker_only_dc")
                        else: cat = self._t("checker_only_res")
                        self._update_check_row(p, "category", cat)
                    
                if not unique_ips: return
                
                import requests, time
                import threading
                from concurrent.futures import ThreadPoolExecutor, as_completed
                
                ips_list = list(unique_ips)
                chunks = [ips_list[i:i+100] for i in range(0, len(ips_list), 100)]
                
                asn_lock = threading.Lock()
                def _fetch_asn_info(asn):
                    if asn in dummy_hunter.asn_cache: return
                    for attempt in range(3):
                        if dummy_hunter._cancel_event.is_set(): return
                        try:
                            html_url = f"https://ipinfo.io/{asn}"
                            resp_html = requests.get(html_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                            if resp_html.status_code == 200:
                                import re
                                m = re.search(r'ASN type.*?>\s*(ISP|Hosting|Business)\s*<', resp_html.text, re.IGNORECASE)
                                if m:
                                    with asn_lock:
                                        dummy_hunter.asn_cache[asn] = m.group(1).lower()
                                break
                            elif resp_html.status_code == 429:
                                time.sleep(3 + attempt * 2)
                            else:
                                break
                        except Exception:
                            time.sleep(2)

                for chunk in chunks:
                    if dummy_hunter._cancel_event.is_set(): break
                    retries = 3
                    backoff = 4
                    chunk_asns_to_fetch = set()
                    
                    for attempt in range(retries):
                        try:
                            resp = requests.post("http://ip-api.com/batch?fields=query,isp,org,as,hosting,mobile,countryCode", json=chunk, timeout=10)
                            if resp.status_code == 429:
                                time.sleep(backoff)
                                backoff *= 2
                                continue
                            if resp.status_code == 200:
                                try:
                                    json_data = resp.json()
                                    if not isinstance(json_data, list): break
                                    with dummy_hunter._lock:
                                        for data in json_data:
                                            if not isinstance(data, dict): continue
                                            query_ip = data.get('query')
                                            if not query_ip: continue
                                            if query_ip not in dummy_hunter.ip_cache:
                                                dummy_hunter.ip_cache[query_ip] = {}
                                            
                                            asn_str = data.get('as', '')
                                            dummy_hunter.ip_cache[query_ip].update({
                                                'country': data.get('countryCode', ''),
                                                'datacenter': data.get('hosting', False),
                                                'mobile': data.get('mobile', False),
                                                'isp': data.get('isp', '').lower(),
                                                'asn': asn_str
                                            })
                                            
                                            if asn_str:
                                                asn_num = asn_str.split()[0]
                                                if asn_num.startswith('AS') and asn_num not in dummy_hunter.asn_cache:
                                                    chunk_asns_to_fetch.add(asn_num)
                                    break
                                except Exception:
                                    break
                            else:
                                break
                        except Exception:
                            time.sleep(2)
                    
                    # Fetch ASNs for this chunk in parallel
                    if chunk_asns_to_fetch:
                        with ThreadPoolExecutor(max_workers=min(20, len(chunk_asns_to_fetch))) as executor:
                            futures = [executor.submit(_fetch_asn_info, asn) for asn in chunk_asns_to_fetch]
                            for f in as_completed(futures):
                                if dummy_hunter._cancel_event.is_set():
                                    for remaining in futures: remaining.cancel()
                                    executor._work_queue.queue.clear()
                                    break
                                    
                    # Update UI for proxies belonging to this chunk
                    with dummy_hunter._lock:
                        for ip in chunk:
                            ip_info = dummy_hunter.ip_cache.get(ip, {})
                            if not ip_info: continue
                            
                            mobile = ip_info.get("mobile", False)
                            hosting = ip_info.get("datacenter", False)
                            asn_str = ip_info.get("asn", "")
                            asn_num = asn_str.split()[0] if asn_str else ""
                            has_api_data = 'datacenter' in ip_info
                            
                            asn_type = dummy_hunter.asn_cache.get(asn_num, "").lower()
                            
                            cat = "Unknown"
                            if mobile:
                                cat = self._t("checker_only_mob")
                            elif asn_type == "isp":
                                cat = self._t("checker_only_res")
                            elif asn_type in ("hosting", "business"):
                                cat = self._t("checker_only_dc")
                            elif not has_api_data:
                                cat = self._t("checker_only_dc")
                            elif hosting:
                                cat = self._t("checker_only_dc")
                            else:
                                cat = self._t("checker_only_res")
                                
                            for proxy in ip_to_proxies.get(ip, []):
                                self._update_check_row(proxy, "category", cat)
                                
                    self.after(0, self._flush_checker_updates)
                    time.sleep(4) # Respect rate limits for next chunk
            
            import threading
            threading.Thread(target=_fetch_categories_bg, daemon=True).start()

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
                        self._update_check_row(proxy, "anon", self._t("chk_skip"))
                        self._update_check_row(proxy, "speed", self._t("chk_skip"))
                        self._update_check_row(proxy, "smtp", self._t("chk_skip"))
                        self._update_check_row(proxy, "bl", self._t("chk_skip"))
                        return
                    is_ip_only = False
                    if protocol_prefix:
                        # H-08 FIX: Proper SOCKS support in checker
                        if 'socks' in protocol_prefix.lower():
                            try:
                                import socks
                                proxies_dict = {'http': f"{protocol_prefix}://{clean_proxy}", 'https': f"{protocol_prefix}://{clean_proxy}"}
                            except ImportError:
                                self._update_check_row(proxy, "ping", self._t("chk_skip"))
                                self._update_check_row(proxy, "anon", self._t("chk_skip") + " (No PySocks)")
                                self._update_check_row(proxy, "speed", self._t("chk_skip"))
                                self._update_check_row(proxy, "smtp", self._t("chk_skip"))
                                self._update_check_row(proxy, "bl", self._t("chk_skip"))
                                return
                        else:
                            proxies_dict = {'http': f"{protocol_prefix}://{clean_proxy}", 'https': f"{protocol_prefix}://{clean_proxy}"}
                    else:
                        proxies_dict = {'http': f"http://{clean_proxy}", 'https': f"http://{clean_proxy}"}
                else:
                    ip = clean_proxy.strip()
                    port = None
                    is_ip_only = True
                    proxies_dict = None
                    
                if is_ip_only:
                    country_iso = dummy_hunter._get_country(ip)
                    self._update_check_row(proxy, "country", self._format_country(country_iso))
                    
                    if getattr(self, "do_check_category", None) and self.do_check_category.get():
                        pass # bg thread sets it
                    else:
                        self._update_check_row(proxy, "category", self._t("chk_skip"))
                        
                    self._update_check_row(proxy, "ping", self._t("chk_skip"))
                    self._update_check_row(proxy, "anon", self._t("chk_skip"))
                    self._update_check_row(proxy, "speed", self._t("chk_skip"))
                    self._update_check_row(proxy, "smtp", self._t("chk_skip"))
                    # C-03 FIX: BL check for IP-only entries
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
                else:
                    if not self.checker_is_running: return
                    country_iso = dummy_hunter._get_country(ip)
                    self._update_check_row(proxy, "country", self._format_country(country_iso))
                    
                    if getattr(self, "do_check_category", None) and self.do_check_category.get():
                        pass # bg thread sets it
                    else:
                        self._update_check_row(proxy, "category", self._t("chk_skip"))

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
                                r = requests.get('http://speed.cloudflare.com/__down?bytes=100000', proxies=proxies_dict, timeout=timeout)
                                if r.status_code == 200:
                                    actual_size = len(r.content)
                                    dl_time = max(0.001, time.time() - t0)
                                    mbps = round((actual_size * 8) / dl_time / 1000000, 1)
                                    if mbps > 0.5:
                                        self._update_check_row(proxy, "speed", self._t("chk_speed_ok").format(mbps))
                                    else:
                                        self._update_check_row(proxy, "speed", self._t("chk_speed_bad").format(mbps))
                                else:
                                    self._update_check_row(proxy, "speed", self._t("chk_error"))
                            except Exception:
                                self._update_check_row(proxy, "speed", self._t("chk_error"))
                        else:
                            self._update_check_row(proxy, "speed", self._t("chk_skip"))

                        if not self.checker_is_running: return
                        # 4. SMTP (Deep)
                        if self.do_check_smtp.get():
                            s = None
                            try:
                                import socket
                                import socks
                                import ssl
                                
                                p_type = socks.PROXY_TYPE_HTTP
                                if protocol_prefix:
                                    if protocol_prefix.lower() == 'socks4':
                                        p_type = socks.PROXY_TYPE_SOCKS4
                                    elif protocol_prefix.lower() == 'socks5':
                                        p_type = socks.PROXY_TYPE_SOCKS5
                                
                                smtp_servers = [
                                    ('smtp.gmail.com', 587, False),
                                    ('smtp-mail.outlook.com', 587, False),
                                    ('smtp.mail.yahoo.com', 587, False),
                                    ('smtp.gmail.com', 465, True),
                                    ('smtp.mail.yahoo.com', 465, True),
                                    ('smtp.aol.com', 587, False),
                                    ('smtp.mail.me.com', 587, False),
                                    ('smtp.zoho.com', 587, False),
                                    ('mail.gmx.com', 587, False),
                                ]
                                
                                smtp_success = False
                                for shost, sport, use_ssl in smtp_servers:
                                    s_loop = None
                                    try:
                                        s_loop = socks.socksocket()
                                        s_loop.settimeout(timeout)
                                        s_loop.set_proxy(p_type, ip, port)
                                        s_loop.connect((shost, sport))
                                        
                                        if use_ssl:
                                            context = ssl.create_default_context()
                                            context.check_hostname = False
                                            context.verify_mode = ssl.CERT_NONE
                                            s_loop = context.wrap_socket(s_loop, server_hostname=shost)
                                            
                                        banner = s_loop.recv(1024)
                                        if banner[:3] == b'220':
                                            s_loop.sendall(b'EHLO localhost\r\n')
                                            ehlo_resp = s_loop.recv(1024)
                                            if ehlo_resp[:3] == b'250':
                                                s_loop.sendall(b'QUIT\r\n')
                                                smtp_success = True
                                                break
                                    except Exception:
                                        pass
                                    finally:
                                        if s_loop:
                                            try: s_loop.close()
                                            except Exception: pass
                                
                                if smtp_success:
                                    self._update_check_row(proxy, "smtp", self._t("chk_open"))
                                else:
                                    self._update_check_row(proxy, "smtp", self._t("chk_closed"))
                            except ImportError:
                                self._update_check_row(proxy, "smtp", self._t("chk_skip") + " (No PySocks)")
                            except Exception:
                                self._update_check_row(proxy, "smtp", self._t("chk_closed"))
                            finally:
                                pass
                        else:
                            self._update_check_row(proxy, "smtp", self._t("chk_skip"))

                        # C-03 FIX: BL check INSIDE alive block (не тратим DNS на мёртвые прокси)
                        if not self.checker_is_running: return
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
        
        # M-05 FIX: Lock for thread-safe counter increment
        import threading as _thr
        _checker_lock = _thr.Lock()
        
        # BUG-21: Parallel execution with ThreadPoolExecutor
        pool = ThreadPoolExecutor(max_workers=max_workers)
        try:
            futures = [pool.submit(check_one, p) for p in proxies]
            for f in as_completed(futures):
                if not self.checker_is_running:
                    # M-07 FIX: Cancel all futures and stop processing results
                    for remaining in futures:
                        remaining.cancel()
                    # Clear futures list to allow garbage collection
                    try:
                        pool._work_queue.queue.clear()
                    except Exception:
                        pass
                    break
                pass
        finally:
            try: pool.shutdown(wait=False, cancel_futures=True)
            except TypeError: pool.shutdown(wait=False)

        # H-05 FIX: Закрываем db_reader чтобы не было утечки файловых дескрипторов
        if hasattr(dummy_hunter, 'db_reader') and dummy_hunter.db_reader:
            try:
                dummy_hunter.db_reader.close()
            except Exception:
                pass
            dummy_hunter.db_reader = None

        self.checker_is_running = False
        def _reset_ui():
            # M-05 FIX: Replace remaining hourglasses with skip
            if hasattr(self, 'checker_data'):
                for proxy, vals in self.checker_data.items():
                    if len(vals) > 8:
                        pass # Retain category '⏳' if background fetch is still running
                        
            self.btn_check_start.configure(state="normal", text=self._t("checker_start"), image=self.icons["play"], fg_color=GREEN, hover_color="#047857")
            self._chk_btn_load.configure(state="normal")
            self._chk_btn_clear.configure(state="normal")
            self.btn_save_checker.configure(state="normal")
            
            self._chk_cb_alive.configure(state="normal")
            self._chk_cb_elite.configure(state="normal")
            self._chk_cb_clean.configure(state="normal")
            self._chk_cb_smtp.configure(state="normal")
            if hasattr(self, '_chk_cb_res'): self._chk_cb_res.configure(state="normal")
            if hasattr(self, '_chk_cb_mob'): self._chk_cb_mob.configure(state="normal")
            if hasattr(self, '_chk_cb_dc'): self._chk_cb_dc.configure(state="normal")
            self.checker_input.configure(state="normal")
            # Restore all columns
            visible_cols = ["#", "proxy", "country"]
            if getattr(self, "do_check_category", None) and self.do_check_category.get():
                visible_cols.append("category")
            visible_cols.extend(["ping", "anon", "bl", "speed", "smtp"])
            self.check_tree["displaycolumns"] = visible_cols
            self._update_checker_metrics()
        self.after(0, _reset_ui)

    def _update_check_row(self, proxy_str, col_name, value):
        if not hasattr(self, '_checker_pending_updates'): return
        
        with self._log_lock:
            if proxy_str not in self._checker_pending_updates:
                self._checker_pending_updates[proxy_str] = {}
            self._checker_pending_updates[proxy_str][col_name] = value
        
        # Increment step counter OUTSIDE lock (int increment is atomic in CPython)
        if col_name in ("ping", "anon", "speed", "smtp", "bl") and hasattr(self, '_checker_total'):
            self._checker_done += 1
        
        # Progress bar is updated by _periodic_flush every 500ms on the main thread

    def _flush_checker_updates(self):
        
        with self._log_lock:
            updates = self._checker_pending_updates.copy()
            self._checker_pending_updates.clear()
            
        if not updates: return
        
        col_indices = {"country": 2, "category": 3, "ping": 4, "anon": 5, "bl": 6, "speed": 7, "smtp": 8}
        
        # Batch apply updates to Tkinter and python cache
        for proxy_str, col_data in updates.items():
            # Update Python cache
            if getattr(self, "checker_data", None) is not None and proxy_str in self.checker_data:
                vals = self.checker_data[proxy_str]
                for c_name, val in col_data.items():
                    if c_name in col_indices:
                        vals[col_indices[c_name]] = val
                        
            # Update Tkinter Treeview if item is on current page
            item_id = self.check_tree_items.get(proxy_str)
            if item_id:
                try:
                    if self.check_tree.exists(item_id):
                        self.check_tree.item(item_id, values=self.checker_data[proxy_str])
                except Exception:
                    pass
                    
        # Calculate metrics directly from python dictionary without IPC overhead
        self._update_checker_metrics()

    def _update_checker_metrics(self):
        """Update live counts on filter checkboxes"""
        alive_count = 0
        elite_count = 0
        clean_count = 0
        smtp_count = 0
        res_count = 0
        mob_count = 0
        dc_count = 0
        unique_countries = set()
        unique_protos = set()
        
        self.checker_country_counts = {}
        self.checker_proto_counts = {}
        
        if not getattr(self, "checker_data", None): return
        
        for p_str, vals in self.checker_data.items():
            try:
                if not vals or len(vals) < 9:
                    continue
                _, proxy, country, category, ping, anon, bl, speed, smtp = vals
                
                c_str = str(country)
                unique_countries.add(c_str)
                self.checker_country_counts[c_str] = self.checker_country_counts.get(c_str, 0) + 1
                
                proto = "http"
                if "://" in p_str:
                    proto = p_str.split("://")[0].lower()
                unique_protos.add(proto)
                self.checker_proto_counts[proto] = self.checker_proto_counts.get(proto, 0) + 1
                # M-02 FIX: Locale-independent status checking
                ping_str = str(ping)
                if ping_str and ping_str != self._t("chk_timeout") and ping_str != self._t("chk_skip") and ping_str != self._t("chk_error"):
                    alive_count += 1
                if str(anon) == self._t("chk_elite"):
                    elite_count += 1
                if str(bl) == self._t("chk_clean"):
                    clean_count += 1
                if str(smtp) == self._t("chk_open"):
                    smtp_count += 1
                cat_str = str(category)
                if cat_str == self._t("checker_only_res") or "Residential" in cat_str or "Резидент" in cat_str: res_count += 1
                elif cat_str == self._t("checker_only_mob") or "Mobile" in cat_str or "Мобиль" in cat_str: mob_count += 1
                elif cat_str == self._t("checker_only_dc") or "Datacenter" in cat_str or "Датацентр" in cat_str: dc_count += 1
            except:
                pass
        
        if hasattr(self, '_chk_cb_alive'):
            self._chk_cb_alive.configure(text=f"{self._t('checker_only_alive')} ({alive_count})")
            self._chk_cb_elite.configure(text=f"{self._t('checker_only_elite')} ({elite_count})")
            self._chk_cb_clean.configure(text=f"{self._t('checker_only_clean')} ({clean_count})")
            self._chk_cb_smtp.configure(text=f"{self._t('checker_only_smtp')} ({smtp_count})")
            if hasattr(self, '_chk_cb_res'):
                self._chk_cb_res.configure(text=f"{self._t('checker_only_res')} ({res_count})")
                self._chk_cb_mob.configure(text=f"{self._t('checker_only_mob')} ({mob_count})")
                self._chk_cb_dc.configure(text=f"{self._t('checker_only_dc')} ({dc_count})")

        if hasattr(self, '_chk_lbl_total_save'):
            vis_count = len(getattr(self, "checker_filtered_proxies", []))
            self._chk_lbl_total_save.configure(text=self._t("proxies_count").format(vis_count))
            
        self.checker_all_countries = sorted(list(unique_countries))
        self.checker_all_protos = sorted(list(unique_protos))

        show_frame = False

        if hasattr(self, "btn_checker_country_filter"):
            active_c = self.checker_selected_countries.intersection(self.checker_all_countries)
            if not self.checker_selected_countries or len(active_c) == len(self.checker_all_countries):
                self.btn_checker_country_filter.configure(text=self._t("all_countries_filter"))
            else:
                self.btn_checker_country_filter.configure(text=self._t("countries_n").format(len(active_c)))
                
            if len(self.checker_all_countries) >= 2:
                self.btn_checker_country_filter.pack(side="right", padx=(5, 5))
                show_frame = True
            else:
                self.btn_checker_country_filter.pack_forget()

        if hasattr(self, "btn_checker_proto_filter"):
            active_p = self.checker_selected_protos.intersection(self.checker_all_protos)
            if not self.checker_selected_protos or len(active_p) == len(self.checker_all_protos):
                self.btn_checker_proto_filter.configure(text=self._t("all_protocols"))
            else:
                self.btn_checker_proto_filter.configure(text=self._t("protocols_n").format(len(active_p)))
                
            if len(self.checker_all_protos) >= 2:
                try:
                    self.btn_checker_proto_filter.pack(side="right", padx=(10, 5), before=self.btn_checker_country_filter)
                except tk.TclError:
                    self.btn_checker_proto_filter.pack(side="right", padx=(10, 5))
                show_frame = True
            else:
                self.btn_checker_proto_filter.pack_forget()

        if show_frame:
            self.checker_top_filters_frame.pack(side="top", fill="x", padx=8, pady=(4, 0), before=self.check_tree_frame)
        else:
            self.checker_top_filters_frame.pack_forget()

    def _apply_checker_filter(self):
        """Instantly show/hide rows based on filter checkboxes"""
        if not hasattr(self, "checker_all_proxies"): return
        
        active_c = set()
        if hasattr(self, "checker_selected_countries"):
            active_c = self.checker_selected_countries.intersection(self.checker_all_countries)
            
        active_p = set()
        if hasattr(self, "checker_selected_protos"):
            active_p = self.checker_selected_protos.intersection(self.checker_all_protos)
            
        any_filter = (self.save_req_alive.get() or self.save_req_elite.get() or 
                      self.save_req_clean.get() or self.save_req_smtp.get() or
                      (hasattr(self, "save_req_res") and self.save_req_res.get()) or
                      (hasattr(self, "save_req_mob") and self.save_req_mob.get()) or
                      (hasattr(self, "save_req_dc") and self.save_req_dc.get()) or
                      (active_c and len(active_c) != len(self.checker_all_countries)) or
                      (active_p and len(active_p) != len(self.checker_all_protos)))
        
        if not any_filter:
            self.checker_filtered_proxies = list(self.checker_all_proxies)
            self.checker_current_page = 0
            self._render_checker_page()
            self._update_checker_metrics()
            return
        
        filtered = []
        for proxy_str in self.checker_all_proxies:
            try:
                vals = self.checker_data.get(proxy_str)
                if not vals or len(vals) < 9:
                    filtered.append(proxy_str)
                    continue
                _, proxy, country, category, ping, anon, bl, speed, smtp = vals
                
                hide = False
                if self.save_req_alive.get() and ("❌" in str(ping) or "⏳" in str(ping) or "—" in str(ping)):
                    hide = True
                if self.save_req_elite.get() and "💎" not in str(anon):
                    hide = True
                if self.save_req_clean.get() and "✨" not in str(bl):
                    hide = True
                if self.save_req_smtp.get() and "■" not in str(smtp):
                    hide = True
                    
                active_cats = []
                if getattr(self, "save_req_res", None) and self.save_req_res.get():
                    active_cats.extend(["Residential", "Резидент", self._t("checker_only_res")])
                if getattr(self, "save_req_mob", None) and self.save_req_mob.get():
                    active_cats.extend(["Mobile", "Мобиль", self._t("checker_only_mob")])
                if getattr(self, "save_req_dc", None) and self.save_req_dc.get():
                    active_cats.extend(["Datacenter", "Датацентр", self._t("checker_only_dc")])
                
                if active_cats:
                    cat_match = False
                    for ac in active_cats:
                        if ac in str(category):
                            cat_match = True
                            break
                    if not cat_match:
                        hide = True
                    
                if not hide and active_c and len(active_c) != len(self.checker_all_countries):
                    if str(country) not in active_c:
                        hide = True
                        
                if not hide and active_p and len(active_p) != len(self.checker_all_protos):
                    p_str = str(proxy)
                    proto = "http"
                    if "://" in p_str:
                        proto = p_str.split("://")[0].lower()
                    if proto not in active_p:
                        hide = True
                
                if not hide:
                    filtered.append(proxy_str)
            except Exception:
                pass
        
        self.checker_filtered_proxies = filtered
        self.checker_current_page = 0
        self._render_checker_page()
        self._update_checker_metrics()


if __name__ == "__main__":
    app = ProxyHunterApp()
    app.mainloop()
