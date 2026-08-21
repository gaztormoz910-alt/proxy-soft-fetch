"""Пакетный запрос гео/ASN-данных (AUDIT.md, PERF-01).

_batch_ip_info режет множество IP на пачки по 100 и опрашивает ip-api.com.
Раньше нарезка была квадратичной, потому что list(ips) пересоздавался на
каждой итерации генератора.
"""
import time

import pytest
import responses

from fetch_proxy import ProxyHunter

API = "http://ip-api.com/batch"


def make_ips(n):
    return {f"8.{(i >> 16) & 255}.{(i >> 8) & 255}.{i & 255}" for i in range(n)}


@pytest.fixture
def hunter(monkeypatch):
    h = ProxyHunter(threads=1)
    h.db_reader = None
    # убираем кулдаун между пачками, чтобы тесты не спали
    monkeypatch.setattr("fetch_proxy.time.sleep", lambda s: None)
    return h


# --------------------------------------------------------------- нарезка

@responses.activate
def test_all_ips_are_requested_exactly_once(hunter):
    ips = make_ips(250)
    responses.add(responses.POST, API, json=[], status=200)

    hunter._batch_ip_info(ips)

    sent = []
    for call in responses.calls:
        sent.extend(__import__("json").loads(call.request.body))
    assert sorted(sent) == sorted(ips)
    assert len(responses.calls) == 3, "250 IP = три пачки по 100"


@responses.activate
def test_chunks_never_exceed_the_api_limit(hunter):
    responses.add(responses.POST, API, json=[], status=200)
    hunter._batch_ip_info(make_ips(1000))

    import json
    for call in responses.calls:
        assert len(json.loads(call.request.body)) <= 100


@responses.activate
def test_empty_input_sends_nothing(hunter):
    hunter._batch_ip_info(set())
    assert len(responses.calls) == 0


# ----------------------------------------------------------- наполнение кэша

@responses.activate
def test_response_fields_land_in_the_cache(hunter):
    responses.add(responses.POST, API, status=200, json=[{
        "query": "8.8.8.8", "countryCode": "US", "hosting": True,
        "mobile": False, "isp": "Google LLC", "as": "AS15169 Google LLC",
    }])

    hunter._batch_ip_info({"8.8.8.8"})

    assert hunter.ip_cache["8.8.8.8"] == {
        "country": "US", "datacenter": True, "mobile": False,
        "isp": "google llc", "asn": "AS15169 Google LLC",
    }


@responses.activate
def test_malformed_entries_are_skipped_without_losing_the_batch(hunter):
    responses.add(responses.POST, API, status=200, json=[
        "не словарь",
        {"нет": "query"},
        {"query": "8.8.8.8", "countryCode": "US"},
    ])

    hunter._batch_ip_info({"8.8.8.8"})
    assert hunter.ip_cache["8.8.8.8"]["country"] == "US"


@responses.activate
def test_non_list_payload_does_not_raise(hunter):
    responses.add(responses.POST, API, status=200, json={"error": "rate limited"})
    hunter._batch_ip_info({"8.8.8.8"})
    assert hunter.ip_cache == {}


@responses.activate
def test_server_error_is_skipped_quietly(hunter):
    responses.add(responses.POST, API, status=500)
    hunter._batch_ip_info({"8.8.8.8"})
    assert hunter.ip_cache == {}


@responses.activate
def test_cancellation_stops_before_the_next_chunk(hunter):
    responses.add(responses.POST, API, json=[], status=200)
    hunter.cancel()
    hunter._batch_ip_info(make_ips(500))
    assert len(responses.calls) == 0


# ------------------------------------------------------------ характеристика

@responses.activate
def test_chunking_is_linear_not_quadratic(hunter):
    """Прямой замер: удвоение объёма не должно учетверять время нарезки."""
    responses.add(responses.POST, API, json=[], status=200)

    def elapsed(n):
        ips = make_ips(n)
        start = time.perf_counter()
        hunter._batch_ip_info(ips)
        return time.perf_counter() - start

    elapsed(2000)                     # прогрев
    small = min(elapsed(4000) for _ in range(3))
    large = min(elapsed(8000) for _ in range(3))

    # при O(n^2) отношение было бы около 4; берём запас на шум и на сеть-мок
    assert large < small * 3.0, f"нарезка похожа на квадратичную: {small:.4f} -> {large:.4f}"
