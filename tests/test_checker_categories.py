"""Определение категорий в чекере: строка не должна застревать в «⏳».

На скриншоте пользователя из 1394 проверенных прокси категорию получили 457,
остальные навсегда остались с песочными часами. Две причины:

  1. Фоновая функция не была обёрнута ни в один try/except. Любое исключение
     убивало поток молча, и все необработанные строки оставались в ожидании.
  2. Адреса, по которым ip-api ничего не вернул, отсеивались через
     `if not ip_info: continue` — и тоже висели «⏳» до конца сеанса.

Плюс полоса прогресса вставала на 100% и цикл обновления останавливался,
пока категории ещё грузились, — со стороны это выглядело как зависание.
"""
import threading

import pytest

import requests

import gui
from gui import ProxyHunterApp


class FakeHunter:
    def __init__(self, ip_cache=None, asn_cache=None):
        self.ip_cache = dict(ip_cache or {})
        self.asn_cache = dict(asn_cache or {})
        self._lock = threading.Lock()
        self._cancel_event = threading.Event()


class FakeApp:
    """Носитель состояния без Tk: методы работают с обычными атрибутами."""

    IPAPI_CHUNK = ProxyHunterApp.IPAPI_CHUNK
    IPAPI_COOLDOWN = 0                      # в тестах не спим
    _category_for = ProxyHunterApp._category_for
    _lookup_categories = ProxyHunterApp._lookup_categories
    _update_check_row = ProxyHunterApp._update_check_row
    PROGRESS_COLUMNS = ProxyHunterApp.PROGRESS_COLUMNS

    def __init__(self):
        self._log_lock = threading.Lock()
        self._checker_pending_updates = {}
        self._checker_total = 0
        self._checker_done = 0
        self._category_stage_total = 0
        self._category_stage_done = 0
        self.flushes = 0

    def _t(self, key):
        return gui.LANG["RU"].get(key, key)

    def after(self, delay, fn=None, *a):
        self.flushes += 1

    def _flush_checker_updates(self):
        pass

    # то, что реально увидел бы пользователь в колонке «Категория»
    def categories(self):
        return {p: cols.get("category")
                for p, cols in self._checker_pending_updates.items()}


PROXIES = ["http://1.1.1.1:80", "http://1.1.1.1:8080", "socks5://9.9.9.9:1080"]


@pytest.fixture(autouse=True)
def no_network_no_waiting(monkeypatch):
    """Тесты не ходят в сеть и не спят.

    _lookup_categories делает requests.get к ipinfo.io за типом ASN и
    time.sleep(2) между попытками — без этой заглушки набор шёл 19 c вместо 6
    и зависел от доступности стороннего сайта.
    """
    import time as _time

    def forbidden_get(*a, **kw):
        raise AssertionError("тест не должен ходить в сеть: " + str(a[:1]))

    monkeypatch.setattr(requests, "get", forbidden_get)
    monkeypatch.setattr(_time, "sleep", lambda *_: None)


@pytest.fixture
def app():
    return FakeApp()


def batch_returning(payload, calls=None):
    """Подменяет requests.post так, будто ip-api вернул payload."""
    class Resp:
        status_code = 200

        def json(self):
            return payload

    def post(url, **kw):
        if calls is not None:
            calls.append(kw.get("json"))
        return Resp()

    return post


# ------------------------------------------- ни одна строка не остаётся в «⏳»

def test_every_proxy_gets_a_category_when_the_api_answers(app, monkeypatch):
    monkeypatch.setattr(requests, "post", batch_returning([
        {"query": "1.1.1.1", "hosting": True, "mobile": False, "as": "AS15169 Google"},
        {"query": "9.9.9.9", "hosting": False, "mobile": True, "as": "AS1234 Telco"},
    ]))

    app._lookup_categories(PROXIES, FakeHunter())

    cats = app.categories()
    assert set(cats) == set(PROXIES), "категория должна быть проставлена каждому прокси"
    assert cats["http://1.1.1.1:80"] == gui.LANG["RU"]["checker_only_dc"]
    assert cats["http://1.1.1.1:8080"] == gui.LANG["RU"]["checker_only_dc"]
    assert cats["socks5://9.9.9.9:1080"] == gui.LANG["RU"]["checker_only_mob"]


def test_address_the_api_skipped_is_marked_unknown_not_left_waiting(app, monkeypatch):
    """Главный баг: ip-api вернул не все адреса — остальные висели «⏳» навсегда."""
    monkeypatch.setattr(requests, "post", batch_returning([
        {"query": "1.1.1.1", "hosting": True, "mobile": False, "as": ""},
    ]))

    app._lookup_categories(PROXIES, FakeHunter())

    cats = app.categories()
    assert cats["socks5://9.9.9.9:1080"] == gui.LANG["RU"]["chk_unknown"]
    assert None not in cats.values()


def test_total_api_failure_still_resolves_every_row(app, monkeypatch):
    def boom(url, **kw):
        raise ConnectionError("сети нет")

    monkeypatch.setattr(requests, "post", boom)

    app._lookup_categories(PROXIES, FakeHunter())

    cats = app.categories()
    assert set(cats) == set(PROXIES)
    assert set(cats.values()) == {gui.LANG["RU"]["chk_unknown"]}


def test_unexpected_exception_does_not_leave_rows_waiting(app, monkeypatch):
    """Раньше это убивало поток молча и оставляло «⏳» до конца сеанса."""
    def explode(url, **kw):
        raise RuntimeError("что угодно неожиданное")

    monkeypatch.setattr(requests, "post", explode)

    app._lookup_categories(PROXIES, FakeHunter())
    assert set(app.categories()) == set(PROXIES)


def test_malformed_payload_does_not_leave_rows_waiting(app, monkeypatch):
    monkeypatch.setattr(requests, "post",
                        batch_returning({"unexpected": "не список"}))

    app._lookup_categories(PROXIES, FakeHunter())
    assert set(app.categories()) == set(PROXIES)


def test_cancelling_midway_still_resolves_the_remaining_rows(app, monkeypatch):
    hunter = FakeHunter()
    hunter._cancel_event.set()
    monkeypatch.setattr(requests, "post", batch_returning([]))

    app._lookup_categories(PROXIES, hunter)
    assert set(app.categories()) == set(PROXIES)


# ------------------------------------------------------------ кэш и сеть

def test_already_known_addresses_skip_the_network(app, monkeypatch):
    called = []
    monkeypatch.setattr(requests, "post",
                        batch_returning([], calls=called))

    hunter = FakeHunter(ip_cache={
        "1.1.1.1": {"datacenter": True, "mobile": False, "asn": ""},
        "9.9.9.9": {"datacenter": False, "mobile": True, "asn": ""},
    })
    app._lookup_categories(PROXIES, hunter)

    assert called == [], "всё уже в кэше — запросов быть не должно"
    assert app.categories()["socks5://9.9.9.9:1080"] == gui.LANG["RU"]["checker_only_mob"]


def test_addresses_are_batched_by_the_api_limit(app, monkeypatch):
    called = []
    monkeypatch.setattr(requests, "post",
                        batch_returning([], calls=called))

    many = [f"http://10.0.{i // 256}.{i % 256}:80" for i in range(250)]
    app._lookup_categories(many, FakeHunter())

    assert [len(c) for c in called] == [100, 100, 50], "чанки по лимиту ip-api"


# ----------------------------------------------------- индикация этапа

def test_stage_counters_advance_and_clear(app, monkeypatch):
    seen = []

    def post(url, **kw):
        seen.append(app._category_stage_done)

        class R:
            status_code = 200

            def json(self):
                return []
        return R()

    monkeypatch.setattr(requests, "post", post)

    many = [f"http://10.0.{i // 256}.{i % 256}:80" for i in range(250)]
    app._lookup_categories(many, FakeHunter())

    assert seen == [0, 1, 2], "счётчик обработанных чанков должен расти"
    assert app._category_stage_total == 0, "после завершения этап обязан обнулиться"


def test_stage_total_is_set_while_running(app, monkeypatch):
    totals = []

    def post(url, **kw):
        totals.append(app._category_stage_total)

        class R:
            status_code = 200

            def json(self):
                return []
        return R()

    monkeypatch.setattr(requests, "post", post)
    app._lookup_categories(PROXIES, FakeHunter())
    assert totals == [1], "во время работы этап должен объявлять свой объём"


# --------------------------------------------------------- _category_for

@pytest.mark.parametrize("info,asn,expected_key", [
    ({"datacenter": False, "mobile": True, "asn": ""}, {}, "checker_only_mob"),
    ({"datacenter": True, "mobile": False, "asn": ""}, {}, "checker_only_dc"),
    ({"datacenter": False, "mobile": False, "asn": "AS1 X"}, {"AS1": "isp"}, "checker_only_res"),
    ({"datacenter": False, "mobile": False, "asn": "AS1 X"}, {"AS1": "hosting"}, "checker_only_dc"),
    ({"datacenter": False, "mobile": False, "asn": "AS1 X"}, {"AS1": "business"}, "checker_only_dc"),
    ({"datacenter": False, "mobile": False, "asn": ""}, {}, "checker_only_res"),
])
def test_category_rules(app, info, asn, expected_key):
    assert app._category_for(info, asn) == gui.LANG["RU"][expected_key]


def test_category_is_empty_without_api_data(app):
    """Пустая строка — сигнал «данных нет», а не молчаливое «Датацентр»."""
    assert app._category_for({}, {}) == ""
    assert app._category_for({"mobile": True}, {}) == ""


def test_a_failing_ui_update_does_not_abandon_the_remaining_chunks(app, monkeypatch):
    """Исключение при обновлении интерфейса раньше обрывало весь цикл,
    и сотни адресов оставались без категории."""
    calls = []

    def post(url, **kw):
        calls.append(kw.get("json"))

        class R:
            status_code = 200

            def json(self):
                return [{"query": ip, "hosting": True, "mobile": False, "as": ""}
                        for ip in kw.get("json", [])]
        return R()

    monkeypatch.setattr(requests, "post", post)

    boom = {"n": 0}

    def flaky_after(delay, fn=None, *a):
        boom["n"] += 1
        if boom["n"] == 1:
            raise RuntimeError("Tk уже закрыт")

    app.after = flaky_after

    many = [f"http://10.0.0.{i}:80" for i in range(250)]
    app._lookup_categories(many, FakeHunter())

    assert len(calls) == 3, "все три чанка обязаны быть запрошены"
    cats = app.categories()
    assert len(cats) == 250
    assert gui.LANG["RU"]["chk_unknown"] not in cats.values(), (
        "категории получены — «неизвестно» здесь быть не должно")
