import pytest

from fetch_proxy import ProxyHunter


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def make_hunter(tmp_path, monkeypatch, db_reader=None, downloads=False):
    hunter = ProxyHunter(threads=1, output_dir=str(tmp_path))
    hunter.db_reader = db_reader
    monkeypatch.setattr(hunter, "_download_mmdb_if_needed", lambda: None)

    called = []
    for name in ("collect", "validate", "advanced_filter", "save"):
        monkeypatch.setattr(hunter, name,
                            lambda *a, _n=name, **k: called.append(_n))
    return hunter, called


def test_country_is_unknown_without_a_database():
    hunter = ProxyHunter(threads=1)
    hunter.db_reader = None
    assert hunter._get_country("8.8.8.8") == "Unknown"


def test_unknown_never_passes_the_default_country_filter():
    hunter = ProxyHunter(threads=1)
    assert "UNKNOWN" not in hunter.countries
    assert hunter.countries, "фильтр стран непустой всегда — отсюда и полный отсев"


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


def test_run_proceeds_normally_when_a_database_is_present(isolated, monkeypatch):
    class FakeReader:
        def get(self, ip):
            return {"country": {"iso_code": "US"}}

        def close(self):
            pass

    hunter, called = make_hunter(isolated, monkeypatch)

    def fake_open():
        hunter.db_reader = FakeReader()
        return True

    monkeypatch.setattr(hunter, "open_geoip", fake_open)

    hunter.run()
    assert called[:3] == ["collect", "validate", "advanced_filter"]
    assert "save" in called
