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
