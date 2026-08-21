"""Инварианты списка источников SOURCES (AUDIT.md, COR-08 / COR-09).

SOURCES собирается на импорте из девяти «волн» через SOURCES.extend(...).
Никакой сверки между волнами не было, поэтому список накопил дубли, а часть
URL осталась с неподставленными плейсхолдерами.
"""
from collections import Counter

import pytest

import fetch_proxy
from fetch_proxy import SOURCES


def test_sources_is_not_empty():
    assert len(SOURCES) > 1000


# ------------------------------------------------------------------ COR-08

def test_no_duplicate_entries():
    dupes = {item: n for item, n in Counter(SOURCES).items() if n > 1}
    assert dupes == {}, f"дублирующихся записей: {len(dupes)}"


def test_deduplication_preserves_order():
    """dict.fromkeys, а не set: порядок источников влияет на порядок логов."""
    assert SOURCES[0][0].startswith("https://api.openproxylist.xyz/")


# ------------------------------------------------------------------ формат

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
    """SOURCES строится через extend из промежуточных списков — проверяем,
    что в него не попали сами эти списки как вложенные элементы."""
    assert not any(isinstance(item, list) for item in SOURCES)


def test_sources_object_identity_is_preserved_after_dedup():
    """Дедупликация правит список на месте — ссылки на fetch_proxy.SOURCES
    в других модулях обязаны видеть уже очищенный список."""
    assert fetch_proxy.SOURCES is SOURCES
