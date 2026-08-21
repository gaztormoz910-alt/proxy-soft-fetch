"""Поведение при недоступной базе GeoLite2 (AUDIT.md, COR-02).

Без базы _get_country() отдаёт 'Unknown', а фильтр стран в validate() никогда
не пуст (в __init__ есть список по умолчанию из 30 стран), поэтому 'UNKNOWN'
не проходит и отбрасывается КАЖДЫЙ кандидат. Раньше прогон просто заканчивался
нулём без единого сообщения об ошибке.
"""
import pytest

from fetch_proxy import ProxyHunter


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    """Пустая рабочая директория: GeoLite2-Country.mmdb рядом нет."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def make_hunter(tmp_path, monkeypatch, db_reader=None, downloads=False):
    hunter = ProxyHunter(threads=1, output_dir=str(tmp_path))
    hunter.db_reader = db_reader
    # Не ходим в сеть за базой
    monkeypatch.setattr(hunter, "_download_mmdb_if_needed", lambda: None)

    called = []
    for name in ("collect", "validate", "advanced_filter", "save"):
        monkeypatch.setattr(hunter, name,
                            lambda *a, _n=name, **k: called.append(_n))
    return hunter, called


# ------------------------------------------- предпосылка: почему это критично

def test_country_is_unknown_without_a_database():
    hunter = ProxyHunter(threads=1)
    hunter.db_reader = None
    assert hunter._get_country("8.8.8.8") == "Unknown"


def test_unknown_never_passes_the_default_country_filter():
    hunter = ProxyHunter(threads=1)
    assert "UNKNOWN" not in hunter.countries
    assert hunter.countries, "фильтр стран непустой всегда — отсюда и полный отсев"


# ------------------------------------------------------ остановка вместо нуля

def test_run_stops_before_collecting_when_the_database_is_missing(isolated, monkeypatch, capsys):
    hunter, called = make_hunter(isolated, monkeypatch)
    hunter.run()
    assert called == [], "сбор не должен стартовать без базы"


def test_run_prints_an_actionable_error(isolated, monkeypatch, capsys):
    hunter, _ = make_hunter(isolated, monkeypatch)
    hunter.run()
    out = capsys.readouterr().out
    assert "GeoLite2-Country.mmdb" in out
    assert "ОСТАНОВЛЕНО" in out


def test_error_message_is_translated(isolated, monkeypatch, capsys):
    hunter, _ = make_hunter(isolated, monkeypatch)
    hunter.lang = "EN"
    hunter.run()
    out = capsys.readouterr().out
    assert "STOPPED" in out
    assert "db_required" not in out, "ключ перевода не должен утекать в вывод"


# ------------------------------------------- с базой прогон идёт как обычно

def test_run_proceeds_normally_when_a_database_is_present(isolated, monkeypatch):
    class FakeReader:
        def get(self, ip):
            return {"country": {"iso_code": "US"}}

        def close(self):
            pass

    hunter, called = make_hunter(isolated, monkeypatch)

    # run() сам переоткрывает базу через open_geoip() — подменяем именно его,
    # присваивать db_reader снаружи бессмысленно: close_geoip() его обнулит.
    def fake_open():
        hunter.db_reader = FakeReader()
        return True

    monkeypatch.setattr(hunter, "open_geoip", fake_open)

    hunter.run()
    assert called[:3] == ["collect", "validate", "advanced_filter"]
    assert "save" in called
