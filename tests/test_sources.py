from collections import Counter

import pytest

import fetch_proxy
from fetch_proxy import SOURCES


def test_sources_is_not_empty():
    assert len(SOURCES) > 1000


def test_no_duplicate_entries():
    dupes = {item: n for item, n in Counter(SOURCES).items() if n > 1}
    assert dupes == {}, f"дублирующихся записей: {len(dupes)}"


def test_deduplication_preserves_order():
    assert SOURCES[0][0].startswith("https://api.openproxylist.xyz/")


@pytest.mark.parametrize("field", [0, 1])
def test_every_entry_is_a_url_protocol_pair(field):
    for item in SOURCES:
        assert isinstance(item, tuple) and len(item) == 2, item
        assert isinstance(item[field], str) and item[field], item


def test_every_url_has_a_scheme():
    bad = [u for u, _ in SOURCES if not u.startswith(("http://", "https://"))]
    assert bad == [], f"без схемы: {bad[:5]}"


def test_protocols_are_from_the_known_set():
    known = {"http", "https", "socks4", "socks5", "all",
             "vless", "vmess", "ss", "ssr", "trojan", "tuic", "hysteria2", "mtproto"}
    unknown = sorted({p for _, p in SOURCES} - known)
    assert unknown == [], f"неизвестные протоколы: {unknown}"


def test_module_level_helpers_did_not_leak_into_sources():
    assert not any(isinstance(item, list) for item in SOURCES)


def test_sources_object_identity_is_preserved_after_dedup():
    assert fetch_proxy.SOURCES is SOURCES


def test_no_url_contains_an_unsubstituted_placeholder():
    bad = [u for u, _ in SOURCES if "{" in u or "}" in u]
    assert bad == [], f"URL с плейсхолдерами: {bad}"


def test_paginated_sources_expand_to_real_page_numbers():
    pages = sorted(int(u.rsplit("page=", 1)[1])
                   for u, _ in SOURCES if "freeproxy.world" in u)
    assert pages == list(range(1, 31))


def test_sources_that_ignore_pagination_appear_once():
    hits = [u for u, _ in SOURCES if "proxyhub.me" in u]
    assert len(hits) == 1
    assert "page=" not in hits[0]
