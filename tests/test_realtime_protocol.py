"""Характеризующие тесты протокола [REALTIME_*] между fetch_proxy и gui.

Backend печатает строки-маркеры в stdout, GUI разбирает их в
ProxyHunterApp._parse_stats(). Контракт нигде не задокументирован и не
версионируется, поэтому фиксируем его тестами.

_parse_stats обращается только к обычным атрибутам self, поэтому его можно
вызывать на подставном объекте без создания окна Tk.
"""
import pytest

import gui
from gui import ProxyHunterApp


class FakeApp:
    """Минимальный носитель состояния, достаточный для _parse_stats."""

    def __init__(self):
        self._is_cancelling = False
        self._stat_updates = {}
        self._base_total_persistent = 0
        self._gen_total_persistent = 0
        self._seen_proxies = set()
        self._proxy_queue = []

    def _t(self, key):
        return gui.LANG["RU"].get(key, key)


def parse(text):
    app = FakeApp()
    ProxyHunterApp._parse_stats(app, text)
    return app


# ------------------------------------------------ форматы строк из backend
# Эталоны взяты дословно из fetch_proxy.py, чтобы тест ловил рассинхрон.

LIVE_LINE = "    [REALTIME_NEW_LIVE] 8.8.8.8|8080|HTTP|US"
ELITE_LINE = "    [REALTIME_NEW_ELITE] 8.8.8.8|8080|http|US|Datacenter"
CATEGORY_LINE = "    [REALTIME_NEW_CATEGORY] 8.8.8.8|8080|HTTP|US|Residential"
TOTAL_LINE = "[REALTIME_TOTAL] 1234"


def test_total_marker_updates_base_counter():
    app = parse(TOTAL_LINE)
    assert app._base_total_persistent == 1234
    assert app._stat_updates["total"] == "1234"


def test_total_marker_adds_generated_counter():
    app = FakeApp()
    app._gen_total_persistent = 500
    ProxyHunterApp._parse_stats(app, TOTAL_LINE)
    assert app._stat_updates["total"] == "1734"


def test_unique_ip_port_log_line_is_parsed():
    app = parse("    Уникальных IP:PORT: 999")
    assert app._base_total_persistent == 999


def test_new_live_marker():
    app = parse(LIVE_LINE)
    assert app._proxy_queue == [
        ({"ip": "8.8.8.8", "port": "8080", "protocol": "HTTP", "country": "US"}, "live"),
    ]
    assert "live:HTTP:8.8.8.8:8080" in app._seen_proxies


def test_new_elite_marker_carries_category():
    app = parse(ELITE_LINE)
    data, source = app._proxy_queue[0]
    assert source == "elite"
    assert data["category"] == "Datacenter"
    assert (data["ip"], data["port"], data["protocol"]) == ("8.8.8.8", "8080", "http")


def test_new_category_marker_routes_by_category():
    app = parse(CATEGORY_LINE)
    _, source = app._proxy_queue[0]
    assert source == "residential"


def test_duplicate_markers_are_ignored():
    app = FakeApp()
    ProxyHunterApp._parse_stats(app, LIVE_LINE)
    ProxyHunterApp._parse_stats(app, LIVE_LINE)
    assert len(app._proxy_queue) == 1


def test_cancelling_flag_suppresses_all_parsing():
    app = FakeApp()
    app._is_cancelling = True
    ProxyHunterApp._parse_stats(app, LIVE_LINE)
    ProxyHunterApp._parse_stats(app, TOTAL_LINE)
    assert app._proxy_queue == []
    assert app._stat_updates == {}


def test_unrelated_line_is_ignored():
    app = parse("[+] ШАГ 2: Базовая проверка 100 прокси на живость...")
    assert app._proxy_queue == []


@pytest.mark.parametrize("garbage", [
    "    [REALTIME_NEW_LIVE] мусор",
    "    [REALTIME_NEW_ELITE] 8.8.8.8|8080",       # не хватает полей
    "    [REALTIME_TOTAL] не-число",
])
def test_malformed_markers_do_not_raise(garbage):
    """Битый маркер не должен ронять поток разбора логов."""
    parse(garbage)


# ------------------------------------------------------------- локализация

def test_regions_cover_the_same_countries_in_both_languages():
    def isos(lang):
        out = set()
        for countries in gui.REGIONS[lang].values():
            out |= set(countries)
        return out

    assert isos("RU") == isos("EN")


# ------------------------------------------------ COR-04: удаление из «живых»

# Backend печатает этот маркер иначе, чем остальные: с ЛИДИРУЮЩИМ '|'.
# Строка скопирована дословно из fetch_proxy.py — если формат там изменится,
# тест ниже об этом сообщит.
REMOVE_LINE = "    [REALTIME_REMOVE_LIVE]|http|1.2.3.4|8080"


def test_remove_live_marker_fields_are_not_shifted():
    app = parse(REMOVE_LINE)
    assert app._proxy_queue == [
        ({"protocol": "http", "ip": "1.2.3.4", "port": "8080"}, "remove_live"),
    ]


def test_remove_live_key_matches_the_key_used_when_adding():
    """Ключ удаления обязан совпадать с ключом, под которым прокси добавлялся.

    Именно это и было сломано: удаление строилось из сдвинутых полей и не
    попадало ни в одну существующую запись.
    """
    added = parse("    [REALTIME_NEW_LIVE] 1.2.3.4|8080|HTTP|US")._proxy_queue[0][0]
    removed = parse(REMOVE_LINE)._proxy_queue[0][0]

    add_key = (added["protocol"].lower(), added["ip"], str(added["port"]))
    del_key = (removed["protocol"].lower(), removed["ip"], str(removed["port"]))
    assert add_key == del_key


def test_backend_still_emits_the_leading_pipe_format():
    """Ловит рассинхрон, если формат в fetch_proxy.py поменяют."""
    import inspect
    import fetch_proxy
    src = inspect.getsource(fetch_proxy.ProxyHunter)
    assert '[REALTIME_REMOVE_LIVE]|{proto}|{ip}|{port}' in src, (
        "формат маркера в fetch_proxy.py изменился — поправьте разбор в gui._parse_stats"
    )


# ------------------------------------------- COR-10: полнота словарей LANG

def test_lang_dicts_have_identical_key_sets():
    """Пропущенный ключ виден пользователю буквально: _t() возвращает сам ключ,
    и .format() его не меняет — на кнопке появляется текст вроде 'countries_n'."""
    ru, en = set(gui.LANG["RU"]), set(gui.LANG["EN"])
    assert ru - en == set(), f"нет в EN: {sorted(ru - en)}"
    assert en - ru == set(), f"нет в RU: {sorted(en - ru)}"


def test_no_translation_leaks_its_own_key_as_the_value():
    for lang, table in gui.LANG.items():
        for key, value in table.items():
            assert value != key, f"{lang}['{key}'] — значение совпадает с ключом"


@pytest.mark.parametrize("key", ["countries_n", "protocols_n"])
def test_filter_button_labels_exist_in_both_languages(key):
    for lang in ("RU", "EN"):
        assert key in gui.LANG[lang], f"{key} отсутствует в LANG['{lang}']"
