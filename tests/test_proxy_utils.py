"""Характеризующие тесты для ProxyUtils.

Фиксируют ТЕКУЩЕЕ поведение парсера и валидатора, чтобы поймать регрессии при
последующих правках. Ничего из проверяемого здесь меняться не должно.
"""
import pytest

from fetch_proxy import ProxyUtils


# ---------------------------------------------------------------- is_valid

@pytest.mark.parametrize("ip,port", [
    ("8.8.8.8", 53),
    ("1.1.1.1", 1),
    ("203.0.113.7", 65535),
    ("172.15.0.1", 8080),     # 172.15 — вне 172.16/12, значит публичный
    ("172.32.0.1", 8080),     # 172.32 — тоже вне диапазона
])
def test_is_valid_accepts_public_addresses(ip, port):
    assert ProxyUtils.is_valid(ip, port) is True


@pytest.mark.parametrize("ip,port,why", [
    ("10.0.0.1", 8080, "private 10/8"),
    ("127.0.0.1", 8080, "loopback"),
    ("0.0.0.0", 8080, "this network"),
    ("172.16.0.1", 8080, "private 172.16/12"),
    ("172.31.255.254", 8080, "private 172.16/12 upper bound"),
    ("192.168.1.1", 8080, "private 192.168/16"),
    ("169.254.1.1", 8080, "link-local"),
    ("224.0.0.1", 8080, "multicast"),
    ("255.255.255.255", 8080, "broadcast"),
    ("8.8.8.8", 0, "port 0"),
    ("8.8.8.8", 65536, "port out of range"),
    ("8.8.8.8", -1, "negative port"),
    ("256.1.1.1", 80, "octet > 255"),
    ("1.2.3", 80, "too few octets"),
    ("1.2.3.4.5", 80, "too many octets"),
    ("", 80, "empty"),
    ("a.b.c.d", 80, "not numeric"),
])
def test_is_valid_rejects(ip, port, why):
    assert ProxyUtils.is_valid(ip, port) is False, why


# ----------------------------------------------------------- parse_proxies

def test_parse_plain_text_list():
    content = "8.8.8.8:8080\n1.1.1.1:3128\n# комментарий\n9.9.9.9:1080\n"
    assert sorted(ProxyUtils.parse_proxies(content)) == [
        "1.1.1.1:3128", "8.8.8.8:8080", "9.9.9.9:1080",
    ]


def test_parse_deduplicates():
    content = "8.8.8.8:8080\n8.8.8.8:8080\n8.8.8.8:8080\n"
    assert ProxyUtils.parse_proxies(content) == ["8.8.8.8:8080"]


def test_parse_skips_reserved_addresses():
    content = "10.0.0.1:8080\n127.0.0.1:3128\n8.8.8.8:1080\n"
    assert ProxyUtils.parse_proxies(content) == ["8.8.8.8:1080"]


def test_parse_html_table():
    content = (
        "<table><tr><td>8.8.8.8</td><td>8080</td><td>US</td></tr>"
        "<tr><td>1.1.1.1</td><td>3128</td><td>DE</td></tr></table>"
    )
    assert sorted(ProxyUtils.parse_proxies(content)) == ["1.1.1.1:3128", "8.8.8.8:8080"]


def test_parse_json_object_with_ip_and_port():
    content = '{"data":[{"ip":"8.8.8.8","port":"8080"},{"ip":"1.1.1.1","port":3128}]}'
    assert sorted(ProxyUtils.parse_proxies(content)) == ["1.1.1.1:3128", "8.8.8.8:8080"]


def test_parse_json_uses_host_key_as_fallback():
    content = '{"proxies":[{"host":"8.8.8.8","port":"1080"}]}'
    assert ProxyUtils.parse_proxies(content) == ["8.8.8.8:1080"]


def test_parse_json_list_of_uri_strings():
    content = '["http://8.8.8.8:8080","socks5://1.1.1.1:1080"]'
    assert sorted(ProxyUtils.parse_proxies(content)) == ["1.1.1.1:1080", "8.8.8.8:8080"]


def test_parse_json_skips_geolocation_metadata():
    """Вложенные метаданные не должны давать ложных прокси (защита от monosans-подобных API)."""
    content = (
        '{"proxies":[{"ip":"8.8.8.8","port":"8080",'
        '"geolocation":{"ip":"1.2.3.4","port":"9999"}}]}'
    )
    assert ProxyUtils.parse_proxies(content) == ["8.8.8.8:8080"]


def test_parse_base64_encoded_body():
    import base64
    payload = "8.8.8.8:8080\n1.1.1.1:3128\n"
    encoded = base64.b64encode(payload.encode()).decode()
    assert sorted(ProxyUtils.parse_proxies(encoded)) == ["1.1.1.1:3128", "8.8.8.8:8080"]


def test_parse_plain_text_is_not_mistaken_for_base64():
    """M-04: длинный текст без разделителей не должен уходить в base64-декодер."""
    content = "8.8.8.8:8080"
    assert ProxyUtils.parse_proxies(content) == ["8.8.8.8:8080"]


def test_parse_encrypted_uris_are_kept_verbatim():
    """Зашифрованные конфиги сохраняются целиком.

    Характеризующий тест: помимо самого URI парсер дополнительно достаёт из него
    «голый» ip:port обычной регуляркой PROXY_RE. Это текущее поведение, и оно
    осознанно зафиксировано здесь — validate() умеет обрабатывать оба варианта.
    """
    content = "vless://uuid@8.8.8.8:443?type=tcp#remark\ntrojan://pass@1.1.1.1:443"
    got = sorted(ProxyUtils.parse_proxies(content))
    assert got == [
        "1.1.1.1:443",
        "8.8.8.8:443",
        "trojan://pass@1.1.1.1:443",
        "vless://uuid@8.8.8.8:443?type=tcp#remark",
    ]


def test_parse_empty_input():
    assert ProxyUtils.parse_proxies("") == []
    assert ProxyUtils.parse_proxies("   \n\n  ") == []


def test_parse_ignores_version_like_numbers():
    """Строки вида 1.2.3.4 без порта не должны попадать в результат."""
    assert ProxyUtils.parse_proxies("version 1.2.3.4 released") == []


# -------------------------------------------------------- extract_ip_port

def test_extract_ip_port_vless():
    assert ProxyUtils.extract_ip_port("vless://uuid@8.8.8.8:443?type=tcp") == ("8.8.8.8", "443")


def test_extract_ip_port_vmess_strips_remark_fragment():
    """BUG-FP07: #remark после base64 не должен ломать декодирование."""
    import base64
    import json
    cfg = json.dumps({"add": "8.8.8.8", "port": 443})
    uri = "vmess://" + base64.b64encode(cfg.encode()).decode().rstrip("=") + "#мой-сервер"
    assert ProxyUtils.extract_ip_port(uri) == ("8.8.8.8", "443")


def test_extract_ip_port_telegram_proxy():
    uri = "https://t.me/proxy?server=8.8.8.8&port=443&secret=ff"
    assert ProxyUtils.extract_ip_port(uri) == ("8.8.8.8", "443")


def test_extract_ip_port_plain_uri():
    assert ProxyUtils.extract_ip_port("http://8.8.8.8:8080") == ("8.8.8.8", "8080")


def test_extract_ip_port_returns_placeholder_on_garbage():
    """Без распознаваемого хоста возвращается ('Config', 'N/A') — сигнал «не IP»."""
    assert ProxyUtils.extract_ip_port("не-является-uri") == ("Config", "N/A")
    assert ProxyUtils.extract_ip_port("vmess://%%%нечитаемо%%%") == ("Config", "N/A")


# ------------------------------------------------- COR-07: Unicode-цифры

@pytest.mark.parametrize("ip", [
    "\u0663.1.1.1",          # арабо-индийская тройка
    "1.\u0663.1.1",
    "\uff11.1.1.1",          # полноширинная единица
    "\u06f1.1.1.1",          # персидская единица
])
def test_is_valid_rejects_non_ascii_digits(ip):
    """str.isdigit() пропускал такие «адреса» как настоящие."""
    assert ProxyUtils.is_valid(ip, 80) is False


@pytest.mark.parametrize("ip", ["\u00b2.1.1.1", "1.1.1.\u00b2"])
def test_is_valid_does_not_raise_on_digits_int_cannot_parse(ip):
    """'\u00b2'.isdigit() истинно, но int('\u00b2') бросает ValueError."""
    assert ProxyUtils.is_valid(ip, 80) is False


@pytest.mark.parametrize("ip", ["010.1.1.1", "1.01.1.1", "8.8.8.08", "00.1.1.1"])
def test_is_valid_rejects_leading_zero_octets(ip):
    """inet_aton читает '010' как восьмеричное — это другой адрес.

    Через такую запись можно было обойти проверку приватных диапазонов.
    """
    assert ProxyUtils.is_valid(ip, 80) is False


def test_is_valid_still_accepts_a_bare_zero_octet():
    assert ProxyUtils.is_valid("8.0.0.1", 80) is True


def test_is_valid_rejects_octet_longer_than_three_digits():
    assert ProxyUtils.is_valid("1111.1.1.1", 80) is False


def test_parse_proxies_drops_non_ascii_digit_addresses():
    content = "\u0663.1.1.1:8080\n8.8.8.8:3128\n"
    assert ProxyUtils.parse_proxies(content) == ["8.8.8.8:3128"]
