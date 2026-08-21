"""Проверка RDNS и DNSBL (AUDIT.md, PERF-06).

_check_rdns_and_bl вызывается по одному разу на IP из потоков чекера.
Все сетевые обращения в тестах подменены — реального DNS здесь нет.
"""
import dns.resolver
import pytest

from fetch_proxy import ProxyHunter, ProxyUtils


class Answer:
    """Запись ответа DNS. Код читает PTR через str(), а A-записи — через to_text()."""

    def __init__(self, text):
        self._text = text

    def to_text(self):
        return self._text

    def __str__(self):
        return self._text


class FakeResolver:
    """Резолвер с заранее заданными ответами; всё остальное — NXDOMAIN."""

    def __init__(self, answers=None):
        self.answers = answers or {}
        self.queries = []
        self.timeout = None
        self.lifetime = None

    def resolve(self, name, rdtype):
        name = str(name)
        self.queries.append((name, rdtype))
        if name in self.answers:
            return self.answers[name]
        raise dns.resolver.NXDOMAIN(f"нет записи для {name}")


@pytest.fixture
def hunter():
    h = ProxyHunter(threads=1)
    h.db_reader = None
    return h


@pytest.fixture
def resolver(monkeypatch):
    holder = {}

    def make(answers=None):
        r = FakeResolver(answers)
        holder["r"] = r
        monkeypatch.setattr(dns.resolver, "Resolver", lambda *a, **kw: r)
        return r

    return make


# ------------------------------------------------------------- результат

def test_clean_ip(hunter, resolver):
    resolver()
    res = hunter._check_rdns_and_bl("8.8.8.8")
    assert res["dnsbl"] is False
    assert res["rdns_dirty"] is False
    assert res["rdns"] == ""


def test_listed_ip_is_flagged(hunter, resolver):
    resolver({"8.8.8.8.zen.spamhaus.org": [Answer("127.0.0.2")]})
    assert hunter._check_rdns_and_bl("8.8.8.8")["dnsbl"] is True


def test_public_dns_blocked_response_is_not_a_listing(hunter, resolver):
    """Spamhaus отвечает 127.255.255.x на запросы с публичных резолверов —
    это отказ в обслуживании, а не запись в списке."""
    resolver({"8.8.8.8.zen.spamhaus.org": [Answer("127.255.255.254")]})
    assert hunter._check_rdns_and_bl("8.8.8.8")["dnsbl"] is False


def test_reverse_name_is_built_correctly(hunter, resolver):
    r = resolver()
    hunter._check_rdns_and_bl("1.2.3.4")
    assert ("4.3.2.1.zen.spamhaus.org", "A") in r.queries


def test_suspicious_rdns_is_flagged(hunter, resolver):
    resolver({"8.8.8.8.in-addr.arpa.": [Answer("tor-exit.example.com.")]})
    res = hunter._check_rdns_and_bl("8.8.8.8")
    assert res["rdns_dirty"] is True


def test_ordinary_rdns_is_not_flagged(hunter, resolver):
    resolver({"8.8.8.8.in-addr.arpa.": [Answer("dns.google.")]})
    assert hunter._check_rdns_and_bl("8.8.8.8")["rdns_dirty"] is False


# --------------------------------------------------------------- кэш

def test_result_is_cached(hunter, resolver):
    r = resolver()
    hunter._check_rdns_and_bl("8.8.8.8")
    queries_after_first = len(r.queries)
    hunter._check_rdns_and_bl("8.8.8.8")
    assert len(r.queries) == queries_after_first, "повторный вызов не должен ходить в DNS"


def test_cache_returns_a_copy(hunter, resolver):
    resolver()
    res = hunter._check_rdns_and_bl("8.8.8.8")
    res["dnsbl"] = "испорчено"
    assert hunter._check_rdns_and_bl("8.8.8.8")["dnsbl"] is False


def test_existing_cache_entry_is_preserved(hunter, resolver):
    resolver()
    hunter.ip_cache["8.8.8.8"] = {"country": "US"}
    res = hunter._check_rdns_and_bl("8.8.8.8")
    assert res["country"] == "US"


# ------------------------------------------------------------- PERF-06

def test_no_ports_are_scanned(hunter, resolver, monkeypatch):
    """Скан шести портов занимал 6.04 c из 8.7 c на IP, а его результат
    ('bad_ports') не читался ни одним потребителем."""
    pings = []
    monkeypatch.setattr(ProxyUtils, "tcp_ping",
                        staticmethod(lambda ip, port, timeout: pings.append(port) or False))
    resolver()
    hunter._check_rdns_and_bl("8.8.8.8")
    assert pings == [], f"порты всё ещё сканируются: {pings}"


def test_cancellation_stops_the_blacklist_queries(hunter, resolver):
    r = resolver()
    hunter.cancel()
    hunter._check_rdns_and_bl("8.8.8.8")
    bl_queries = [q for q, _ in r.queries if "spamhaus" in q or "sorbs" in q]
    assert bl_queries == []
