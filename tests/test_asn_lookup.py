"""Определение типа ASN через ipinfo.io (AUDIT.md, PERF-02).

_batch_asn_type опрашивал ipinfo.io строго последовательно и спал 0.5 c после
каждого ASN. Тот же самый запрос в gui.py давно распараллелен на 20 воркеров.
"""
import threading
import time

import pytest
import responses

from fetch_proxy import ProxyHunter

PAGE = '<div>ASN type</div><span class="value">{}</span>'


@pytest.fixture
def hunter():
    h = ProxyHunter(threads=1)
    h.db_reader = None
    return h


def seed(hunter, count, asn_type="ISP"):
    for i in range(count):
        hunter.ip_cache[f"8.8.8.{i}"] = {"asn": f"AS{1000 + i} Example Networks"}
        responses.add(responses.GET, f"https://ipinfo.io/AS{1000 + i}",
                      body=PAGE.format(asn_type), status=200)


# ------------------------------------------------------------- корректность

@responses.activate
def test_asn_types_are_cached(hunter):
    seed(hunter, 3)
    hunter._batch_asn_type()
    assert hunter.asn_cache == {"AS1000": "isp", "AS1001": "isp", "AS1002": "isp"}


@responses.activate
def test_each_asn_is_requested_once_even_with_many_ips(hunter):
    for i in range(50):
        hunter.ip_cache[f"8.8.8.{i}"] = {"asn": "AS15169 Google LLC"}
    responses.add(responses.GET, "https://ipinfo.io/AS15169", body=PAGE.format("Hosting"), status=200)

    hunter._batch_asn_type()
    assert len(responses.calls) == 1
    assert hunter.asn_cache == {"AS15169": "hosting"}


@responses.activate
def test_already_cached_asns_are_not_requested_again(hunter):
    seed(hunter, 2)
    hunter.asn_cache["AS1000"] = "hosting"
    hunter._batch_asn_type()
    assert [c.request.url for c in responses.calls] == ["https://ipinfo.io/AS1001"]


@responses.activate
def test_page_without_the_marker_leaves_no_entry(hunter):
    hunter.ip_cache["8.8.8.8"] = {"asn": "AS1 Something"}
    responses.add(responses.GET, "https://ipinfo.io/AS1", body="<html>ничего</html>", status=200)
    hunter._batch_asn_type()
    assert hunter.asn_cache == {}


@responses.activate
def test_http_error_leaves_no_entry(hunter):
    hunter.ip_cache["8.8.8.8"] = {"asn": "AS1 Something"}
    responses.add(responses.GET, "https://ipinfo.io/AS1", status=503)
    hunter._batch_asn_type()
    assert hunter.asn_cache == {}


@responses.activate
def test_one_failing_asn_does_not_lose_the_others(hunter):
    hunter.ip_cache["8.8.8.1"] = {"asn": "AS1 Bad"}
    hunter.ip_cache["8.8.8.2"] = {"asn": "AS2 Good"}
    responses.add(responses.GET, "https://ipinfo.io/AS1", status=500)
    responses.add(responses.GET, "https://ipinfo.io/AS2", body=PAGE.format("Business"), status=200)

    hunter._batch_asn_type()
    assert hunter.asn_cache == {"AS2": "business"}


@responses.activate
def test_entries_without_an_asn_are_ignored(hunter):
    hunter.ip_cache["8.8.8.1"] = {"country": "US"}
    hunter.ip_cache["8.8.8.2"] = {"asn": "неправильный формат"}
    hunter._batch_asn_type()
    assert len(responses.calls) == 0


@responses.activate
def test_cancellation_stops_the_lookup(hunter):
    seed(hunter, 40)
    hunter.cancel()
    hunter._batch_asn_type()
    assert hunter.asn_cache == {}


# ------------------------------------------------------- параллельность

def test_lookups_run_in_parallel(hunter, monkeypatch):
    """Ключевое свойство: 40 ASN по 0.1 c не должны занимать 4 секунды."""
    seen = set()
    lock = threading.Lock()

    class Resp:
        status_code = 200
        text = PAGE.format("ISP")

    def slow_get(url, **kwargs):
        with lock:
            seen.add(url)
        time.sleep(0.1)
        return Resp()

    monkeypatch.setattr("fetch_proxy.requests.get", slow_get)
    for i in range(40):
        hunter.ip_cache[f"8.8.8.{i}"] = {"asn": f"AS{2000 + i} Net"}

    start = time.perf_counter()
    hunter._batch_asn_type()
    elapsed = time.perf_counter() - start

    assert len(seen) == 40
    assert len(hunter.asn_cache) == 40
    # последовательно было бы >= 4 c (плюс прежние 0.5 c сна на каждый ASN)
    assert elapsed < 1.5, f"похоже на последовательный опрос: {elapsed:.2f} c"
