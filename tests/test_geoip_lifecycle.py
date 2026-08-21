"""Жизненный цикл открытой базы GeoIP (AUDIT.md, REL-01).

База открывалась в ProxyHunter.__init__, а потом ещё раз в run() и в потоке
чекера — старая ссылка просто перезаписывалась. Каждый такой вызов оставлял
открытый mmap на 8.4 МБ и файловый дескриптор; на Windows незакрытый хэндл
вдобавок мешает os.replace() подменить сам файл базы при обновлении.
"""
import pytest

import fetch_proxy
from fetch_proxy import ProxyHunter


class FakeReader:
    def __init__(self, registry):
        self.closed = False
        registry.append(self)

    def get(self, ip):
        return {"country": {"iso_code": "US"}}

    def close(self):
        self.closed = True


@pytest.fixture
def readers(monkeypatch, tmp_path):
    """Подменяет maxminddb и делает вид, что файл базы существует."""
    opened = []

    class FakeMaxmind:
        @staticmethod
        def open_database(path):
            return FakeReader(opened)

    monkeypatch.setitem(__import__("sys").modules, "maxminddb", FakeMaxmind)
    monkeypatch.setattr(fetch_proxy.os.path, "exists", lambda p: True)
    return opened


def test_constructor_opens_the_database_once(readers):
    ProxyHunter(threads=1)
    assert len(readers) == 1
    assert readers[0].closed is False


def test_reopening_closes_the_previous_reader(readers):
    hunter = ProxyHunter(threads=1)
    hunter.open_geoip()
    hunter.open_geoip()

    assert len(readers) == 3, "три открытия"
    assert [r.closed for r in readers] == [True, True, False], (
        "каждый предыдущий reader должен быть закрыт")


def test_close_is_idempotent(readers):
    hunter = ProxyHunter(threads=1)
    hunter.close_geoip()
    hunter.close_geoip()
    assert readers[0].closed is True
    assert hunter.db_reader is None


def test_close_survives_a_reader_that_raises(readers):
    hunter = ProxyHunter(threads=1)

    def boom():
        raise OSError("файл уже закрыт")

    hunter.db_reader.close = boom
    hunter.close_geoip()          # не должно бросить наружу
    assert hunter.db_reader is None


def test_open_reports_success(readers):
    hunter = ProxyHunter(threads=1)
    assert hunter.open_geoip() is True


def test_open_reports_failure_when_the_file_is_absent(monkeypatch):
    monkeypatch.setattr(fetch_proxy.os.path, "exists", lambda p: False)
    hunter = ProxyHunter(threads=1)
    assert hunter.open_geoip() is False
    assert hunter.db_reader is None


def test_country_lookup_after_close_does_not_raise(readers):
    hunter = ProxyHunter(threads=1)
    hunter.close_geoip()
    assert hunter._get_country("8.8.8.8") == "Unknown"
