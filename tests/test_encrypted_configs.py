"""Зашифрованные конфиги в validate() (vless / vmess / trojan / mtproto).

Раньше такой конфиг попадал в «Рабочие» вообще без сетевой проверки: сверялась
только извлекаемость IPv4 и страна, после чего шёл безусловный return. То есть
счётчик «Рабочие» включал записи, про которые не было известно ровным счётом
ничего, кроме страны.

Полностью проверить vless/trojan без реализации самого протокола нельзя, но
подтвердить, что endpoint принимает соединения, — можно, и это та же нижняя
планка, что у http/socks.
"""
import base64
import json

import pytest

from fetch_proxy import ProxyHunter, ProxyUtils


VLESS = "vless://uuid@8.8.8.8:443?type=tcp#remark"
TROJAN = "trojan://pass@9.9.9.9:8443"


def vmess(host="8.8.8.8", port=443):
    cfg = json.dumps({"add": host, "port": port})
    return "vmess://" + base64.b64encode(cfg.encode()).decode().rstrip("=")


@pytest.fixture
def hunter(monkeypatch):
    h = ProxyHunter(threads=1, timeout=1)
    h.db_reader = None
    h.countries = set()                       # гео-фильтр выключен
    monkeypatch.setattr(ProxyHunter, "_get_country", lambda self, ip: "US")
    return h


def make_worker(hunter):
    """Прогоняет один элемент через validate() с подставным TCP-пингом.

    async_worker — замыкание внутри validate(), напрямую его не достать,
    поэтому идём публичным путём.
    """
    def check(item, tcp_ok):
        async def fake_ping(ip, port, timeout):
            return tcp_ok
        original = ProxyUtils.async_tcp_ping
        ProxyUtils.async_tcp_ping = staticmethod(fake_ping)
        try:
            hunter.live_results = []
            hunter.candidate_generator = iter([item])
            hunter.candidate_total = 1
            hunter.validate()
            return list(hunter.live_results)
        finally:
            ProxyUtils.async_tcp_ping = staticmethod(original)

    return check


# ----------------------------------- endpoint должен быть хотя бы достижим

@pytest.mark.parametrize("uri,expected_port", [
    (VLESS, 443),
    (TROJAN, 8443),
])
def test_reachable_config_is_accepted(hunter, uri, expected_port):
    check = make_worker(hunter)
    assert check((uri, ["vless"]), tcp_ok=True) == [uri.split("://")[0] + "://" + uri.split("://", 1)[1]]


@pytest.mark.parametrize("uri", [VLESS, TROJAN])
def test_unreachable_config_is_rejected(hunter, uri):
    """Главный баг: такой конфиг раньше попадал в «Рабочие» без проверки."""
    check = make_worker(hunter)
    assert check((uri, ["vless"]), tcp_ok=False) == []


def test_the_extracted_port_is_the_one_probed(hunter):
    """Проверять надо порт из конфига, а не какой-нибудь подставленный."""
    probed = {}

    async def fake_ping(ip, port, timeout):
        probed["value"] = (ip, port)
        return True

    original = ProxyUtils.async_tcp_ping
    ProxyUtils.async_tcp_ping = staticmethod(fake_ping)
    try:
        hunter.live_results = []
        hunter.candidate_generator = iter([(TROJAN, ["trojan"])])
        hunter.candidate_total = 1
        hunter.validate()
    finally:
        ProxyUtils.async_tcp_ping = staticmethod(original)

    assert probed["value"] == ("9.9.9.9", 8443)


def test_vmess_port_comes_from_the_decoded_payload(hunter):
    probed = {}

    async def fake_ping(ip, port, timeout):
        probed["value"] = (ip, port)
        return True

    original = ProxyUtils.async_tcp_ping
    ProxyUtils.async_tcp_ping = staticmethod(fake_ping)
    try:
        hunter.live_results = []
        hunter.candidate_generator = iter([(vmess("1.1.1.1", 2053), ["vmess"])])
        hunter.candidate_total = 1
        hunter.validate()
    finally:
        ProxyUtils.async_tcp_ping = staticmethod(original)

    assert probed["value"] == ("1.1.1.1", 2053)


def test_missing_port_falls_back_to_443(hunter):
    """Совпадает с подстановкой в async_run_single_filter — поведение
    двух путей не должно расходиться."""
    probed = {}

    async def fake_ping(ip, port, timeout):
        probed["value"] = (ip, port)
        return True

    original = ProxyUtils.async_tcp_ping
    ProxyUtils.async_tcp_ping = staticmethod(fake_ping)
    try:
        hunter.live_results = []
        hunter.candidate_generator = iter([("trojan://pass@9.9.9.9", ["trojan"])])
        hunter.candidate_total = 1
        hunter.validate()
    finally:
        ProxyUtils.async_tcp_ping = staticmethod(original)

    assert probed["value"] == ("9.9.9.9", 443)


# ------------------------------- прежние фильтры продолжают работать

def test_config_without_an_ipv4_host_is_still_rejected(hunter):
    check = make_worker(hunter)
    assert check(("vless://uuid@example.com:443", ["vless"]), tcp_ok=True) == []


def test_country_filter_still_applies_before_the_network(hunter, monkeypatch):
    """Гео-фильтр обязан отсекать ДО соединения — иначе он бессмыслен."""
    monkeypatch.setattr(ProxyHunter, "_get_country", lambda self, ip: "RU")
    pinged = []

    async def fake_ping(ip, port, timeout):
        pinged.append(ip)
        return True

    original = ProxyUtils.async_tcp_ping
    ProxyUtils.async_tcp_ping = staticmethod(fake_ping)
    try:
        hunter.live_results = []
        hunter.candidate_generator = iter([(VLESS, ["vless"])])
        hunter.candidate_total = 1
        hunter.validate()
    finally:
        ProxyUtils.async_tcp_ping = staticmethod(original)

    assert hunter.live_results == []
    assert pinged == [], "к заблокированной стране соединяться незачем"
