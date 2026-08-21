"""Тесты fetch_url + parse_proxies на реальных формах ответов источников.

Ключевой случай — AUDIT.md COR-01: JSON-источники теряли ВСЕ прокси, потому
что fetch_url сплющивал ответ через str(resp.json()).
"""
import json

import responses

from fetch_proxy import ProxyUtils


def fetch_and_parse(url):
    return sorted(ProxyUtils.parse_proxies(ProxyUtils.fetch_url(url, timeout=5)))


# ------------------------------------------------------------------- COR-01

@responses.activate
def test_json_api_response_yields_proxies():
    """Форма ответа Geonode: объект с массивом data, Content-Type application/json."""
    body = json.dumps({"data": [
        {"_id": "x1", "ip": "184.178.172.28", "port": "4145", "country": "US"},
        {"_id": "x2", "ip": "8.8.8.8", "port": "8080", "country": "US"},
    ], "total": 2})
    responses.add(responses.GET, "https://proxylist.test/api/proxy-list",
                  body=body, status=200, content_type="application/json; charset=utf-8")
    assert fetch_and_parse("https://proxylist.test/api/proxy-list") == [
        "184.178.172.28:4145", "8.8.8.8:8080",
    ]


@responses.activate
def test_url_ending_in_json_yields_proxies():
    """Ветка `url.endswith('.json')` срабатывала даже при text/plain."""
    body = json.dumps([{"ip": "1.1.1.1", "port": 3128}, {"ip": "9.9.9.9", "port": 1080}])
    responses.add(responses.GET, "https://raw.test/proxies.json",
                  body=body, status=200, content_type="text/plain")
    assert fetch_and_parse("https://raw.test/proxies.json") == ["1.1.1.1:3128", "9.9.9.9:1080"]


@responses.activate
def test_json_list_of_uri_strings_still_works():
    """Регрессия: этот формат работал и до фикса, не должен сломаться."""
    body = json.dumps(["http://1.1.1.1:8080", "socks5://9.9.9.9:1080"])
    responses.add(responses.GET, "https://raw.test/list.json",
                  body=body, status=200, content_type="application/json")
    assert fetch_and_parse("https://raw.test/list.json") == ["1.1.1.1:8080", "9.9.9.9:1080"]


@responses.activate
def test_json_with_port_before_ip():
    body = json.dumps({"result": [{"port": 8080, "ip": "1.1.1.1"}]})
    responses.add(responses.GET, "https://api.test/v1.json",
                  body=body, status=200, content_type="application/json")
    assert fetch_and_parse("https://api.test/v1.json") == ["1.1.1.1:8080"]


# --------------------------------------------------- прочие формы источников

@responses.activate
def test_plain_text_list():
    responses.add(responses.GET, "https://raw.test/http.txt",
                  body="1.1.1.1:8080\n9.9.9.9:1080\n", status=200, content_type="text/plain")
    assert fetch_and_parse("https://raw.test/http.txt") == ["1.1.1.1:8080", "9.9.9.9:1080"]


@responses.activate
def test_html_table_source():
    body = ("<html><table><tr><td>1.1.1.1</td><td>8080</td></tr>"
            "<tr><td>9.9.9.9</td><td>1080</td></tr></table></html>")
    responses.add(responses.GET, "https://freeproxy.test/",
                  body=body, status=200, content_type="text/html")
    assert fetch_and_parse("https://freeproxy.test/") == ["1.1.1.1:8080", "9.9.9.9:1080"]


@responses.activate
def test_telegram_channel_is_stripped_of_html():
    body = ('<div class="tgme_widget_message_text js-message_text">'
            '<b>Fresh</b> 1.1.1.1:8080<br>9.9.9.9:1080</div>')
    responses.add(responses.GET, "https://t.me/s/proxy_channel",
                  body=body, status=200, content_type="text/html")
    assert fetch_and_parse("https://t.me/s/proxy_channel") == ["1.1.1.1:8080", "9.9.9.9:1080"]


@responses.activate
def test_csv_source():
    responses.add(responses.GET, "https://api.test/list?format=csv",
                  body="ip,port,country\n1.1.1.1,8080,US\n9.9.9.9,1080,DE\n",
                  status=200, content_type="text/csv")
    assert fetch_and_parse("https://api.test/list?format=csv") == ["1.1.1.1:8080", "9.9.9.9:1080"]


# ------------------------------------------------------------ отказоустойчивость

@responses.activate
def test_http_error_returns_empty_string():
    responses.add(responses.GET, "https://dead.test/list.txt", status=404)
    assert ProxyUtils.fetch_url("https://dead.test/list.txt", timeout=5) == ""


@responses.activate
def test_empty_body_returns_empty_string():
    responses.add(responses.GET, "https://empty.test/list.txt", body="", status=200)
    assert ProxyUtils.fetch_url("https://empty.test/list.txt", timeout=5) == ""


@responses.activate
def test_invalid_utf8_bytes_do_not_raise():
    responses.add(responses.GET, "https://binary.test/list.txt",
                  body=b"\xff\xfe1.1.1.1:8080\xff", status=200, content_type="text/plain")
    assert fetch_and_parse("https://binary.test/list.txt") == ["1.1.1.1:8080"]
