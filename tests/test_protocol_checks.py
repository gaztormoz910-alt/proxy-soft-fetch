"""Проверка живости прокси по каждому протоколу.

async_http_check содержала ветки только для http, socks4 и socks5. Прокси с
меткой `https` проваливался мимо всех условий, функция возвращала None — то
есть «не работает» ВСЕГДА, каким бы живым он ни был. В SOURCES такой меткой
помечены 104 источника, и пришедшие только оттуда прокси не могли попасть
в «Рабочие» в принципе.

Сеть не используется: asyncio.open_connection подменяется парой
reader/writer, которая отвечает заранее заданными байтами.
"""
import asyncio

import pytest

import fetch_proxy
from fetch_proxy import ProxyUtils


class FakeWriter:
    def __init__(self, sent):
        self._sent = sent

    def write(self, data):
        self._sent.append(data)

    async def drain(self):
        pass

    def close(self):
        pass

    async def wait_closed(self):
        pass


class FakeReader:
    """Отдаёт заготовленные ответы по одному на каждое чтение."""

    def __init__(self, replies):
        self._replies = list(replies)

    async def read(self, n):
        return self._replies.pop(0) if self._replies else b""

    async def readexactly(self, n):
        return self._replies.pop(0) if self._replies else b"\x00" * n


@pytest.fixture
def wire(monkeypatch):
    """Подменяет соединение; возвращает то, что прокси «отправил»."""
    sent = []

    def connect_with(*replies):
        async def fake_open(ip, port):
            return FakeReader(replies), FakeWriter(sent)
        # async_http_check делает `import asyncio` внутри себя, поэтому
        # достаточно подменить атрибут в самом модуле asyncio
        monkeypatch.setattr(asyncio, "open_connection", fake_open)
        return sent

    return connect_with


def check(proto):
    return asyncio.run(ProxyUtils.async_http_check("1.2.3.4", 8080, proto, 1))


# --------------------------------------------------------------- https

def test_https_proxy_accepting_connect_is_alive(wire):
    """«https» в списках — это HTTP-прокси, умеющий CONNECT."""
    sent = wire(b"HTTP/1.1 200 Connection established\r\n\r\n")
    assert check("https") is True
    assert sent[0].startswith(b"CONNECT gstatic.com:443"), "должен уйти CONNECT"


def test_https_proxy_refusing_connect_is_not_alive(wire):
    wire(b"HTTP/1.1 403 Forbidden\r\n\r\n")
    assert check("https") is False


def test_https_proxy_returning_407_is_not_alive(wire):
    """407 — прокси требует авторизацию, пользоваться им нельзя."""
    wire(b"HTTP/1.1 407 Proxy Authentication Required\r\n\r\n")
    assert check("https") is False


def test_https_check_ignores_200_appearing_later_in_the_body(wire):
    """Смотрим только статусную строку, иначе тело подделает результат."""
    wire(b"HTTP/1.1 502 Bad Gateway\r\n\r\n<html>error 200 ok</html>")
    assert check("https") is False


def test_https_garbage_response_is_not_alive(wire):
    wire(b"\x00\x01\x02 200 \xff")
    assert check("https") is False


def test_https_empty_response_is_not_alive(wire):
    wire(b"")
    assert check("https") is False


# ------------------------------------------- остальные протоколы не сломаны

def test_http_still_checks_generate_204(wire):
    sent = wire(b"HTTP/1.1 204 No Content\r\n\r\n")
    assert check("http") is True
    assert b"GET http://gstatic.com/generate_204" in sent[0]


def test_http_without_204_is_not_alive(wire):
    wire(b"HTTP/1.1 200 OK\r\n\r\n")
    assert check("http") is False


def test_socks4_handshake(wire):
    sent = wire(b"\x00\x5a\x00\x00\x00\x00\x00\x00", b"HTTP/1.1 204 No Content\r\n\r\n")
    assert check("socks4") is True
    assert sent[0][:2] == b"\x04\x01", "SOCKS4 CONNECT"


def test_socks4_rejected_handshake(wire):
    wire(b"\x00\x5b\x00\x00\x00\x00\x00\x00")
    assert check("socks4") is False


def test_socks5_handshake(wire):
    sent = wire(b"\x05\x00",                       # метод «без авторизации»
                b"\x05\x00\x00\x01",               # ответ на CONNECT
                b"\x00" * 6,                       # адрес IPv4 + порт
                b"HTTP/1.1 204 No Content\r\n\r\n")
    assert check("socks5") is True
    assert sent[0] == b"\x05\x01\x00", "приветствие SOCKS5"


def test_socks5_auth_required_is_not_alive(wire):
    wire(b"\x05\x02")          # прокси требует логин/пароль
    assert check("socks5") is False


# ------------------------------------------------------ контракт функции

def test_unknown_protocol_returns_false_not_none(wire):
    """Именно неявный None и маскировал отсутствие ветки для https."""
    wire(b"HTTP/1.1 204 No Content\r\n\r\n")
    assert check("совсем-не-протокол") is False


@pytest.mark.parametrize("proto", ["http", "https", "socks4", "socks5"])
def test_every_protocol_in_sources_has_a_branch(proto):
    """Каждая метка, встречающаяся в SOURCES, обязана проверяться."""
    import inspect
    src = inspect.getsource(ProxyUtils.async_http_check)
    assert f"'{proto}'" in src, f"нет ветки для протокола {proto}"


def test_all_source_labels_are_covered_or_deliberately_encrypted():
    """Ловит появление новой метки, для которой забыли написать проверку."""
    labels = {p for _, p in fetch_proxy.SOURCES}
    checked = {"http", "https", "socks4", "socks5"}
    # 'all' разворачивается в три протокола ещё при сборе;
    # зашифрованные конфиги проверяются отдельным путём в validate()
    encrypted = {"vless", "vmess", "ss", "ssr", "trojan", "tuic", "hysteria2", "mtproto"}
    unknown = labels - checked - encrypted - {"all"}
    assert unknown == set(), f"метки без проверки живости: {sorted(unknown)}"
