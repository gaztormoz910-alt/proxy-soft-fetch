"""«Машина времени» GitHub: разбор URL источника (AUDIT.md, SEC-05).

fetch_github_commits раскладывает URL источника на owner/repo/path и
подставляет их в обращение к api.github.com — с токеном пользователя в
заголовке. Раньше path подставлялся без экранирования.
"""
import urllib.parse

import responses

from fetch_proxy import ProxyUtils

API = "https://api.github.com/repos/"


def query_of(request_url):
    return urllib.parse.parse_qs(urllib.parse.urlsplit(request_url).query)


# --------------------------------------------------------------- разбор URL

@responses.activate
def test_raw_githubusercontent_url_is_parsed():
    responses.add(responses.GET, API + "TheSpeedX/PROXY-List/commits", json=[], status=200)
    ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt", "тк", 24)

    assert query_of(responses.calls[0].request.url)["path"] == ["http.txt"]


@responses.activate
def test_jsdelivr_url_is_parsed():
    responses.add(responses.GET, API + "proxifly/free-proxy-list/commits", json=[], status=200)
    ProxyUtils.fetch_github_commits(
        "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.txt", "тк", 24)

    assert query_of(responses.calls[0].request.url)["path"] == ["proxies/all/data.txt"]


@responses.activate
def test_commit_shas_become_raw_urls():
    responses.add(responses.GET, API + "o/r/commits",
                  json=[{"sha": "abc123"}, {"sha": "def456"}], status=200)
    urls, _ = ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/list.txt", "тк", 24)

    assert urls == ["https://raw.githubusercontent.com/o/r/abc123/list.txt",
                    "https://raw.githubusercontent.com/o/r/def456/list.txt"]


def test_non_github_url_is_ignored():
    assert ProxyUtils.fetch_github_commits("https://example.test/list.txt", "тк", 24) == ([], {})


# ------------------------------------------------------------------ SEC-05

@responses.activate
def test_query_characters_in_the_path_cannot_inject_api_parameters():
    """'?' и '&' в пути не должны становиться параметрами запроса к API."""
    responses.add(responses.GET, API + "o/r/commits", json=[], status=200)
    ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/dir/file.txt?per_page=1&foo=bar", "тк", 24)

    params = query_of(responses.calls[0].request.url)
    assert params["path"] == ["dir/file.txt?per_page=1&foo=bar"], "путь должен остаться одним параметром"
    assert params["per_page"] == ["100"], "per_page обязан остаться нашим"
    assert "foo" not in params


@responses.activate
def test_path_separators_are_preserved():
    responses.add(responses.GET, API + "o/r/commits", json=[], status=200)
    ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/a/b/c.txt", "тк", 24)
    assert query_of(responses.calls[0].request.url)["path"] == ["a/b/c.txt"]


def test_malformed_owner_or_repo_is_rejected():
    for url in ("https://raw.githubusercontent.com/o..%2f/r/main/f.txt",
                "https://raw.githubusercontent.com/o/r%20evil/main/f.txt"):
        assert ProxyUtils.fetch_github_commits(url, "тк", 24) == ([], {})


@responses.activate
def test_token_is_sent_in_the_header_not_the_url():
    responses.add(responses.GET, API + "o/r/commits", json=[], status=200)
    ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/f.txt", "ghp_секрет", 24)

    request = responses.calls[0].request
    assert request.headers["Authorization"] == "token ghp_секрет"
    assert "ghp_секрет" not in request.url


@responses.activate
def test_api_failure_is_swallowed():
    responses.add(responses.GET, API + "o/r/commits", status=401)
    assert ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/f.txt", "тк", 24)[0] == []
