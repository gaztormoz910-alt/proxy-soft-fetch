"""Устойчивость parse_proxies к повреждённым источникам (AUDIT.md, COR-06).

Две отдельные проблемы:
  1. Одна битая запись в JSON обнуляла результат всего источника.
  2. Regex-фолбэк не умел читать JSON-подобный текст, потому что регулярки
     JSON_IP_FIRST / JSON_PORT_FIRST были объявлены, но нигде не подключены.
"""
from fetch_proxy import ProxyUtils


def parse(content):
    return sorted(ProxyUtils.parse_proxies(content))


# ------------------------------- битая запись не должна ронять весь источник

def test_broken_record_does_not_discard_the_healthy_ones():
    """'²'.isdigit() истинно, но int('²') бросает ValueError.

    Раньше это исключение всплывало из extract_from_json до внешнего
    `except Exception: pass` и обнуляло весь источник.
    """
    content = ('{"data":[{"ip":"².1.1.1","port":"80"},'
               '{"ip":"8.8.8.8","port":"3128"}]}')
    assert parse(content) == ["8.8.8.8:3128"]


def test_record_with_null_fields_is_skipped_not_fatal():
    content = ('{"data":[{"ip":null,"port":null},'
               '{"ip":"8.8.8.8","port":"3128"}]}')
    assert parse(content) == ["8.8.8.8:3128"]


def test_record_with_wrong_types_is_skipped_not_fatal():
    content = ('{"data":[{"ip":{"nested":"object"},"port":[1,2]},'
               '{"ip":"8.8.8.8","port":"3128"}]}')
    assert parse(content) == ["8.8.8.8:3128"]


# ------------------------------------- оборванный / невалидный JSON-фолбэк

def test_truncated_json_still_yields_the_complete_records():
    """Стрим обрывается по лимиту 20 МБ или по таймауту — хвост теряется."""
    content = '{"data":[{"ip":"1.2.3.4","port":"8080"},{"ip":"5.6.7.8","por'
    assert parse(content) == ["1.2.3.4:8080"]


def test_truncated_json_with_two_complete_records():
    content = ('{"data":[{"ip":"1.2.3.4","port":"8080"},'
               '{"ip":"5.6.7.8","port":"3128"},{"ip":"9.9.9')
    assert parse(content) == ["1.2.3.4:8080", "5.6.7.8:3128"]


def test_invalid_json_with_trailing_comma():
    content = '{"data":[{"ip":"1.2.3.4","port":"8080"},]}'
    assert parse(content) == ["1.2.3.4:8080"]


def test_json_fallback_reads_port_before_ip():
    content = '{"broken": [{"port": 1080, "ip": "9.9.9.9"},'
    assert parse(content) == ["9.9.9.9:1080"]


def test_json_fallback_reads_host_key():
    content = '{"broken": [{"host": "9.9.9.9", "port": "1080"},'
    assert parse(content) == ["9.9.9.9:1080"]


def test_json_fallback_still_filters_reserved_addresses():
    content = '{"data":[{"ip":"10.0.0.1","port":"8080"},{"ip":"127.0.0.1","port":"3128"},'
    assert parse(content) == []


def test_json_fallback_rejects_out_of_range_port():
    content = '{"data":[{"ip":"8.8.8.8","port":"99999"},'
    assert parse(content) == []


# ------------------------------------------------------------- не регрессии

def test_valid_json_still_takes_the_fast_path():
    """Полностью валидный JSON по-прежнему разбирается структурно."""
    content = '{"data":[{"ip":"1.2.3.4","port":"8080"},{"ip":"5.6.7.8","port":"3128"}]}'
    assert parse(content) == ["1.2.3.4:8080", "5.6.7.8:3128"]


def test_geolocation_metadata_is_still_skipped_in_valid_json():
    content = ('{"proxies":[{"ip":"8.8.8.8","port":"8080",'
               '"geolocation":{"ip":"1.2.3.4","port":"9999"}}]}')
    assert parse(content) == ["8.8.8.8:8080"]


def test_plain_text_source_is_unaffected():
    assert parse("1.2.3.4:8080\n5.6.7.8:3128\n") == ["1.2.3.4:8080", "5.6.7.8:3128"]
