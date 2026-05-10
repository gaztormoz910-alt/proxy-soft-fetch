import re
import json

REGIONS_RU = {
    "🇪🇺 Европа": {
        "AT": "Австрия", "BE": "Бельгия", "BG": "Болгария", "HR": "Хорватия", "CY": "Кипр",
        "CZ": "Чехия", "DK": "Дания", "EE": "Эстония", "FI": "Финляндия", "FR": "Франция",
        "DE": "Германия", "GR": "Греция", "HU": "Венгрия", "IE": "Ирландия", "IT": "Италия",
        "LV": "Латвия", "LT": "Литва", "LU": "Люксембург", "MT": "Мальта", "NL": "Нидерланды",
        "PL": "Польша", "PT": "Португалия", "RO": "Румыния", "SK": "Словакия", "SI": "Словения",
        "ES": "Испания", "SE": "Швеция", "NO": "Норвегия", "CH": "Швейцария", "GB": "Великобритания",
        "IS": "Исландия", "AL": "Албания", "BA": "Босния", "ME": "Черногория", "MK": "Сев. Македония",
        "RS": "Сербия", "MD": "Молдова",
    },
    "🌎 Сев. Америка": {
        "US": "США", "CA": "Канада", "MX": "Мексика", "CR": "Коста-Рика", "PA": "Панама",
        "GT": "Гватемала", "HN": "Гондурас", "SV": "Сальвадор", "NI": "Никарагуа",
        "CU": "Куба", "DO": "Доминикана", "JM": "Ямайка", "TT": "Тринидад", "HT": "Гаити",
    },
    "🌎 Юж. Америка": {
        "BR": "Бразилия", "AR": "Аргентина", "CL": "Чили", "CO": "Колумбия", "PE": "Перу",
        "VE": "Венесуэла", "EC": "Эквадор", "UY": "Уругвай", "PY": "Парагвай", "BO": "Боливия",
    },
    "🌏 Азия": {
        "CN": "Китай", "JP": "Япония", "KR": "Юж. Корея", "IN": "Индия", "ID": "Индонезия",
        "TH": "Таиланд", "VN": "Вьетнам", "PH": "Филиппины", "MY": "Малайзия", "SG": "Сингапур",
        "TW": "Тайвань", "HK": "Гонконг", "BD": "Бангладеш", "PK": "Пакистан", "KZ": "Казахстан",
        "UZ": "Узбекистан", "AZ": "Азербайджан", "GE": "Грузия", "AM": "Армения",
        "IL": "Израиль", "TR": "Турция", "AE": "ОАЭ", "SA": "Сауд. Аравия", "QA": "Катар",
        "KW": "Кувейт", "IQ": "Ирак", "IR": "Иран", "LB": "Ливан", "JO": "Иордания",
        "MM": "Мьянма", "KH": "Камбоджа", "NP": "Непал", "LK": "Шри-Ланка", "MN": "Монголия",
    },
    "🇷🇺 СНГ": {
        "RU": "Россия", "UA": "Украина", "BY": "Беларусь", "KG": "Кыргызстан",
        "TJ": "Таджикистан", "TM": "Туркменистан",
    },
    "🌍 Африка": {
        "ZA": "ЮАР", "NG": "Нигерия", "EG": "Египет", "KE": "Кения", "GH": "Гана",
        "TZ": "Танзания", "ET": "Эфиопия", "MA": "Марокко", "TN": "Тунис", "DZ": "Алжир",
        "CM": "Камерун", "SN": "Сенегал", "UG": "Уганда", "MZ": "Мозамбик", "AO": "Ангола",
        "CD": "ДР Конго", "RW": "Руанда", "LY": "Ливия",
    },
    "🌏 Океания": {
        "AU": "Австралия", "NZ": "Новая Зеландия", "FJ": "Фиджи", "PG": "Папуа-Нов. Гвинея",
    },
}

REGIONS_EN = {
    "🇪🇺 Europe": {
        "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "HR": "Croatia", "CY": "Cyprus",
        "CZ": "Czechia", "DK": "Denmark", "EE": "Estonia", "FI": "Finland", "FR": "France",
        "DE": "Germany", "GR": "Greece", "HU": "Hungary", "IE": "Ireland", "IT": "Italy",
        "LV": "Latvia", "LT": "Lithuania", "LU": "Luxembourg", "MT": "Malta", "NL": "Netherlands",
        "PL": "Poland", "PT": "Portugal", "RO": "Romania", "SK": "Slovakia", "SI": "Slovenia",
        "ES": "Spain", "SE": "Sweden", "NO": "Norway", "CH": "Switzerland", "GB": "United Kingdom",
        "IS": "Iceland", "AL": "Albania", "BA": "Bosnia", "ME": "Montenegro", "MK": "North Macedonia",
        "RS": "Serbia", "MD": "Moldova",
    },
    "🌎 North America": {
        "US": "United States", "CA": "Canada", "MX": "Mexico", "CR": "Costa Rica", "PA": "Panama",
        "GT": "Guatemala", "HN": "Honduras", "SV": "El Salvador", "NI": "Nicaragua",
        "CU": "Cuba", "DO": "Dominican Republic", "JM": "Jamaica", "TT": "Trinidad", "HT": "Haiti",
    },
    "🌎 South America": {
        "BR": "Brazil", "AR": "Argentina", "CL": "Chile", "CO": "Colombia", "PE": "Peru",
        "VE": "Venezuela", "EC": "Ecuador", "UY": "Uruguay", "PY": "Paraguay", "BO": "Bolivia",
    },
    "🌏 Asia": {
        "CN": "China", "JP": "Japan", "KR": "South Korea", "IN": "India", "ID": "Indonesia",
        "TH": "Thailand", "VN": "Vietnam", "PH": "Philippines", "MY": "Malaysia", "SG": "Singapore",
        "TW": "Taiwan", "HK": "Hong Kong", "BD": "Bangladesh", "PK": "Pakistan", "KZ": "Kazakhstan",
        "UZ": "Uzbekistan", "AZ": "Azerbaijan", "GE": "Georgia", "AM": "Armenia",
        "IL": "Israel", "TR": "Turkey", "AE": "UAE", "SA": "Saudi Arabia", "QA": "Qatar",
        "KW": "Kuwait", "IQ": "Iraq", "IR": "Iran", "LB": "Lebanon", "JO": "Jordan",
        "MM": "Myanmar", "KH": "Cambodia", "NP": "Nepal", "LK": "Sri Lanka", "MN": "Mongolia",
    },
    "🇷🇺 CIS": {
        "RU": "Russia", "UA": "Ukraine", "BY": "Belarus", "KG": "Kyrgyzstan",
        "TJ": "Tajikistan", "TM": "Turkmenistan",
    },
    "🌍 Africa": {
        "ZA": "South Africa", "NG": "Nigeria", "EG": "Egypt", "KE": "Kenya", "GH": "Ghana",
        "TZ": "Tanzania", "ET": "Ethiopia", "MA": "Morocco", "TN": "Tunisia", "DZ": "Algeria",
        "CM": "Cameroon", "SN": "Senegal", "UG": "Uganda", "MZ": "Mozambique", "AO": "Angola",
        "CD": "DR Congo", "RW": "Rwanda", "LY": "Libya",
    },
    "🌏 Oceania": {
        "AU": "Australia", "NZ": "New Zealand", "FJ": "Fiji", "PG": "Papua New Guinea",
    },
}

with open("gui.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace the whole REGIONS block and ISO_TO_NAME block
target_start = 'REGIONS = {'
target_end = "ISO_TO_NAME['Unknown'] = \"Неизвестно\"\n"

start_idx = code.find(target_start)
end_idx = code.find(target_end) + len(target_end)

new_block = '''REGIONS = {
    "RU": ''' + json.dumps(REGIONS_RU, ensure_ascii=False, indent=4) + ''',
    "EN": ''' + json.dumps(REGIONS_EN, ensure_ascii=False, indent=4) + '''
}

ISO_TO_NAME = {
    "RU": {},
    "EN": {}
}
for lang in ["RU", "EN"]:
    for r, countries in REGIONS[lang].items():
        ISO_TO_NAME[lang].update(countries)
    ISO_TO_NAME[lang]['Unknown'] = "Unknown" if lang == "EN" else "Неизвестно"
'''

code = code[:start_idx] + new_block + code[end_idx:]

# Also fix the _select_region call for Europe button
code = code.replace('"🇪🇺 Европа"', 'list(REGIONS[self.current_lang].keys())[0]')

# Also fix minsize
code = code.replace('self.geometry("1280x860")', 'self.geometry("1280x860")\n        self.minsize(960, 680)')

with open("gui.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Patched!")
