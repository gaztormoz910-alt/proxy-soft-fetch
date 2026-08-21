"""Отмена сбора источников (AUDIT.md, COR-05).

collect() ставит в пул на 50 воркеров все 1710 источников. Раньше пул был
`with ThreadPoolExecutor(...)`, то есть выход из блока делал shutdown(wait=True)
без отмены очереди: после нажатия «Отмена» программа продолжала честно
скачивать все оставшиеся источники по 15 с таймаута каждый.

Тесты подменяют SOURCES и fetch_url_with_error, сеть не используется.
"""
import threading
import time

import pytest

import fetch_proxy
from fetch_proxy import ProxyHunter, ProxyUtils


@pytest.fixture
def fake_sources(monkeypatch):
    """200 источников, каждый «скачивается» 0.2 с."""
    sources = [(f"https://src{i}.test/list.txt", "http") for i in range(200)]
    monkeypatch.setattr(fetch_proxy, "SOURCES", sources)
    return sources


@pytest.fixture
def slow_fetch(monkeypatch):
    started = []

    def fetch(url, timeout=10):
        started.append(url)
        time.sleep(0.2)
        return "8.8.8.8:8080", ""

    monkeypatch.setattr(ProxyUtils, "fetch_url_with_error", staticmethod(fetch))
    return started


def test_cancel_returns_quickly_instead_of_draining_the_queue(fake_sources, slow_fetch):
    hunter = ProxyHunter(threads=1)

    # отменяем почти сразу после старта
    threading.Timer(0.3, hunter.cancel).start()

    t0 = time.perf_counter()
    hunter.collect()
    elapsed = time.perf_counter() - t0

    # 200 источников / 50 воркеров * 0.2 c = ~0.8 c на полный проход.
    # После отмены должны выйти заметно раньше.
    assert elapsed < 0.75, f"collect() не прервался: {elapsed:.2f} c"


def test_queued_sources_are_not_fetched_after_cancel(fake_sources, slow_fetch):
    hunter = ProxyHunter(threads=1)
    threading.Timer(0.3, hunter.cancel).start()
    hunter.collect()
    time.sleep(0.4)   # даём шанс «протечь» уже стоящим в очереди задачам

    assert len(slow_fetch) < len(fake_sources), (
        f"скачаны все {len(slow_fetch)} источников, отмена не сработала")


def test_worker_skips_the_network_when_cancelled_before_it_starts(monkeypatch, fake_sources):
    """Задача, простоявшая в очереди, не должна уходить в сеть."""
    calls = []
    monkeypatch.setattr(ProxyUtils, "fetch_url_with_error",
                        staticmethod(lambda url, timeout=10: (calls.append(url) or "", "")))

    hunter = ProxyHunter(threads=1)
    hunter.cancel()          # отменено ещё до старта
    hunter.collect()

    assert calls == [], "ни один источник не должен быть запрошен"


def test_collect_without_cancel_still_processes_everything(monkeypatch):
    monkeypatch.setattr(fetch_proxy, "SOURCES",
                        [(f"https://src{i}.test/list.txt", "http") for i in range(20)])
    monkeypatch.setattr(ProxyUtils, "fetch_url_with_error",
                        staticmethod(lambda url, timeout=10: ("8.8.8.8:8080\n1.1.1.1:3128", "")))

    hunter = ProxyHunter(threads=1)
    hunter.collect()

    assert set(hunter.proxy_protocols) == {"8.8.8.8:8080", "1.1.1.1:3128"}
    assert hunter.candidate_total == 2


# ------------------------ один URL — одно скачивание, даже под двумя протоколами

def test_url_listed_under_two_protocols_is_fetched_once(monkeypatch):
    """32 URL перечислены в SOURCES дважды с разными протоколами.

    Скачивать один и тот же файл дважды бессмысленно: содержимое одинаковое,
    отличается только метка протокола.
    """
    monkeypatch.setattr(fetch_proxy, "SOURCES", [
        ("https://both.test/list.txt", "http"),
        ("https://both.test/list.txt", "socks5"),
    ])
    fetched = []
    monkeypatch.setattr(ProxyUtils, "fetch_url_with_error",
                        staticmethod(lambda url, timeout=10: (fetched.append(url) or "8.8.8.8:8080", "")))

    hunter = ProxyHunter(threads=1)
    hunter.collect()

    assert fetched == ["https://both.test/list.txt"], "источник скачан больше одного раза"
    assert hunter.proxy_protocols["8.8.8.8:8080"] == {"http", "socks5"}, (
        "оба протокола обязаны сохраниться")


def test_protocol_all_still_expands_to_three(monkeypatch):
    monkeypatch.setattr(fetch_proxy, "SOURCES", [("https://a.test/list.txt", "all")])
    monkeypatch.setattr(ProxyUtils, "fetch_url_with_error",
                        staticmethod(lambda url, timeout=10: ("8.8.8.8:8080", "")))

    hunter = ProxyHunter(threads=1)
    hunter.collect()
    assert hunter.proxy_protocols["8.8.8.8:8080"] == {"http", "socks4", "socks5"}


def test_all_combines_with_an_explicit_protocol_from_the_same_url(monkeypatch):
    monkeypatch.setattr(fetch_proxy, "SOURCES", [
        ("https://a.test/list.txt", "all"),
        ("https://a.test/list.txt", "vless"),
    ])
    monkeypatch.setattr(ProxyUtils, "fetch_url_with_error",
                        staticmethod(lambda url, timeout=10: ("8.8.8.8:8080", "")))

    hunter = ProxyHunter(threads=1)
    hunter.collect()
    assert hunter.proxy_protocols["8.8.8.8:8080"] == {"http", "socks4", "socks5", "vless"}
