"""Разбор HTML-таблиц с прокси (AUDIT.md, дополнение к COR-09).

TABLE_RE требовал, чтобы IP и порт лежали непосредственно внутри <td>. У части
источников значение обёрнуто в <span> или <a>, и такие страницы давали ноль
прокси при полностью корректном HTML.
"""
import time

import pytest

from fetch_proxy import ProxyUtils


def parse(html):
    return sorted(ProxyUtils.parse_proxies(html))


# ------------------------------------------------- формы, которые работали

def test_plain_cells():
    html = "<table><tr><td>8.8.8.8</td><td>8080</td></tr></table>"
    assert parse(html) == ["8.8.8.8:8080"]


def test_cells_with_attributes():
    html = '<tr><td class="ip">8.8.8.8</td><td class="port">8080</td></tr>'
    assert parse(html) == ["8.8.8.8:8080"]


def test_cells_with_surrounding_whitespace_and_newlines():
    html = "<tr><td>\n   8.8.8.8\n  </td>\n<td>\n 8080 \n</td></tr>"
    assert parse(html) == ["8.8.8.8:8080"]


# --------------------------------------------- формы, которые не работали

def test_value_wrapped_in_span():
    """Форма proxyhub.me."""
    html = ('<td class="ip-cell" data-label="IP">\n'
            '    <span class="ip-text" title="8.8.8.8">8.8.8.8</span>\n'
            '</td>\n'
            '<td class="port-cell" data-label="Port">\n'
            '    <span class="port-text">1080</span>\n'
            '</td>')
    assert parse(html) == ["8.8.8.8:1080"]


def test_port_wrapped_in_link():
    """Форма freeproxy.world."""
    html = ('<td style="font-weight: 500;">185.148.104.179</td>\n'
            '<td><a href="/?port=80">80</a></td>')
    assert parse(html) == ["185.148.104.179:80"]


def test_both_cells_wrapped_in_links():
    html = '<td><a href="/ip">8.8.8.8</a></td><td><a href="/port">3128</a></td>'
    assert parse(html) == ["8.8.8.8:3128"]


def test_nested_wrappers():
    html = "<td><div><b>8.8.8.8</b></div></td><td><div><b>1080</b></div></td>"
    assert parse(html) == ["8.8.8.8:1080"]


# ------------------------------------------------------- фильтрация мусора

def test_reserved_addresses_in_tables_are_still_dropped():
    html = ('<td><span>10.0.0.1</span></td><td><span>8080</span></td>'
            '<td><span>8.8.8.8</span></td><td><span>3128</span></td>')
    assert parse(html) == ["8.8.8.8:3128"]


def test_out_of_range_port_in_a_table_is_dropped():
    html = "<td><span>8.8.8.8</span></td><td><span>99999</span></td>"
    assert parse(html) == []


# ------------------------------------------- отсутствие катастрофического бэктрекинга

@pytest.mark.parametrize("depth,repeats", [(200, 400)])
def test_deeply_nested_tags_do_not_blow_up(depth, repeats):
    """Группы повторения не могут совпасть с пустой строкой, поэтому разбор
    линеен. Без этого свойства такой вход вешал бы процесс."""
    adversarial = ("<td>" + "<b>" * depth + "не-ip" + "</b>" * depth) * repeats
    start = time.perf_counter()
    ProxyUtils.parse_proxies(adversarial)
    assert time.perf_counter() - start < 5.0
