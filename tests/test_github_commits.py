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
    urls, _, error = ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/list.txt", "тк", 24)
    assert error == "", "успешный ответ не должен нести причину отказа"

    assert urls == ["https://raw.githubusercontent.com/o/r/abc123/list.txt",
                    "https://raw.githubusercontent.com/o/r/def456/list.txt"]


def test_non_github_url_is_ignored():
    urls, limits, error = ProxyUtils.fetch_github_commits("https://example.test/list.txt", "тк", 24)
    assert (urls, limits) == ([], {})
    assert error == "не распознан как ссылка на GitHub"


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
        urls, limits, error = ProxyUtils.fetch_github_commits(url, "тк", 24)
        assert (urls, limits) == ([], {})
        assert error == "недопустимое имя owner/repo"


@responses.activate
def test_token_is_sent_in_the_header_not_the_url():
    responses.add(responses.GET, API + "o/r/commits", json=[], status=200)
    ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/f.txt", "ghp_секрет", 24)

    request = responses.calls[0].request
    assert request.headers["Authorization"] == "token ghp_секрет"
    assert "ghp_секрет" not in request.url


@responses.activate
def test_api_failure_yields_no_urls():
    responses.add(responses.GET, API + "o/r/commits", status=401)
    assert ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/f.txt", "тк", 24)[0] == []


# ------------------------------------ диагностика отказов GitHub API (REL-09)
#
# Раньше любой не-200 просто не добавлял ничего в результат, поэтому
# протухший токен, исчерпанный лимит и «за период коммитов не было»
# сводились к одному и тому же «Найдено 0 исторических файлов». Именно
# поэтому истёкший токен три месяца оставался незамеченным.

@responses.activate
def test_expired_token_is_named_not_swallowed():
    responses.add(responses.GET, API + "o/r/commits", status=401)
    urls, _, error = ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/f.txt", "протухший", 24)
    assert urls == []
    assert error == ProxyUtils.GITHUB_TOKEN_REJECTED


@responses.activate
def test_exhausted_rate_limit_is_distinguishable_from_forbidden():
    """403 у GitHub — это и «кончился лимит», и «нет доступа»."""
    responses.add(responses.GET, API + "o/r/commits", status=403,
                  headers={"X-RateLimit-Remaining": "0"})
    assert ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/f.txt", "тк", 24)[2] == \
        ProxyUtils.GITHUB_RATE_LIMITED


@responses.activate
def test_forbidden_with_quota_left_is_not_reported_as_rate_limit():
    responses.add(responses.GET, API + "o/r/commits", status=403,
                  headers={"X-RateLimit-Remaining": "4321"})
    assert ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/f.txt", "тк", 24)[2] == "доступ запрещён (403)"


@responses.activate
def test_missing_repository_is_named():
    responses.add(responses.GET, API + "o/r/commits", status=404)
    assert ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/f.txt", "тк", 24)[2] == \
        "репозиторий или файл не найден (404)"


@responses.activate
def test_empty_result_from_a_healthy_repo_is_not_an_error():
    """Ключевое различие: «коммитов не было» — это не отказ."""
    responses.add(responses.GET, API + "o/r/commits", json=[], status=200)
    urls, _, error = ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/f.txt", "тк", 24)
    assert urls == []
    assert error == ""


@responses.activate
def test_network_failure_is_classified():
    responses.add(responses.GET, API + "o/r/commits",
                  body=__import__("requests").exceptions.ConnectTimeout("slow"))
    assert ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/f.txt", "тк", 24)[2] == "таймаут"


@responses.activate
def test_failure_midway_through_pagination_keeps_the_first_page():
    """Первая страница уже получена — отдаём её и называем причину обрыва."""
    responses.add(responses.GET, API + "o/r/commits",
                  json=[{"sha": "aaa"}], status=200,
                  headers={"Link": f'<{API}o/r/commits?page=2>; rel="next"'})
    responses.add(responses.GET, API + "o/r/commits?page=2", status=403,
                  headers={"X-RateLimit-Remaining": "0"})

    urls, _, error = ProxyUtils.fetch_github_commits(
        "https://raw.githubusercontent.com/o/r/main/f.txt", "тк", 24)
    assert urls == ["https://raw.githubusercontent.com/o/r/aaa/f.txt"]
    assert error == ProxyUtils.GITHUB_RATE_LIMITED


# ------------------------------------------- предварительная проверка токена

@responses.activate
def test_token_check_passes_for_a_healthy_token():
    responses.add(responses.GET, "https://api.github.com/rate_limit",
                  json={"resources": {"core": {"remaining": 4999, "limit": 5000}}}, status=200)
    ok, reason, remaining = ProxyUtils.check_github_token("тк")
    assert (ok, reason, remaining) == (True, "", 4999)


@responses.activate
def test_token_check_rejects_an_expired_token():
    responses.add(responses.GET, "https://api.github.com/rate_limit", status=401)
    ok, reason, _ = ProxyUtils.check_github_token("протухший")
    assert ok is False
    assert reason == ProxyUtils.GITHUB_TOKEN_REJECTED


@responses.activate
def test_token_check_rejects_an_exhausted_quota():
    responses.add(responses.GET, "https://api.github.com/rate_limit",
                  json={"resources": {"core": {"remaining": 0, "limit": 5000}}}, status=200)
    ok, reason, remaining = ProxyUtils.check_github_token("тк")
    assert (ok, reason, remaining) == (False, ProxyUtils.GITHUB_RATE_LIMITED, 0)


@responses.activate
def test_token_check_survives_a_network_failure():
    responses.add(responses.GET, "https://api.github.com/rate_limit",
                  body=__import__("requests").exceptions.ConnectionError("dns"))
    ok, reason, _ = ProxyUtils.check_github_token("тк")
    assert ok is False
    assert reason == "соединение"


@responses.activate
def test_token_check_costs_exactly_one_request():
    """Смысл проверки — не отправить 407 обречённых запросов."""
    responses.add(responses.GET, "https://api.github.com/rate_limit", status=401)
    ProxyUtils.check_github_token("тк")
    assert len(responses.calls) == 1


# ---------------------------------------- поведение collect() целиком

def _hunter_with_token(monkeypatch, token="ghp_тест"):
    import fetch_proxy
    from fetch_proxy import ProxyHunter, ProxyUtils

    monkeypatch.setattr(fetch_proxy, "SOURCES", [
        ("https://raw.githubusercontent.com/o/r/main/a.txt", "http"),
        ("https://raw.githubusercontent.com/o/r/main/b.txt", "http"),
        ("https://cdn.jsdelivr.net/gh/o/r@main/c.txt", "http"),
    ])
    monkeypatch.setattr(ProxyUtils, "fetch_url_with_error",
                        staticmethod(lambda url, timeout=10: ("8.8.8.8:8080", "")))

    hunter = ProxyHunter(threads=1, github_token=token, github_tm_enabled=True, github_tm_days=1)
    return hunter


def test_rejected_token_skips_the_time_machine_entirely(monkeypatch, capsys):
    from fetch_proxy import ProxyUtils

    hunter = _hunter_with_token(monkeypatch)
    monkeypatch.setattr(ProxyUtils, "check_github_token",
                        staticmethod(lambda t, timeout=10: (False, ProxyUtils.GITHUB_TOKEN_REJECTED, None)))

    called = []
    monkeypatch.setattr(ProxyUtils, "fetch_github_commits",
                        staticmethod(lambda *a, **kw: called.append(a) or ([], {}, "")))

    hunter.collect()

    assert called == [], "при отклонённом токене не должно быть ни одного запроса истории"
    out = capsys.readouterr().out
    assert ProxyUtils.GITHUB_TOKEN_REJECTED in out
    assert "github.com/settings/tokens" in out, "подсказка, что делать, обязана быть в логе"


def test_exhausted_quota_skips_the_time_machine_with_its_own_hint(monkeypatch, capsys):
    from fetch_proxy import ProxyUtils

    hunter = _hunter_with_token(monkeypatch)
    monkeypatch.setattr(ProxyUtils, "check_github_token",
                        staticmethod(lambda t, timeout=10: (False, ProxyUtils.GITHUB_RATE_LIMITED, 0)))
    monkeypatch.setattr(ProxyUtils, "fetch_github_commits",
                        staticmethod(lambda *a, **kw: ([], {}, "")))

    hunter.collect()
    out = capsys.readouterr().out
    assert ProxyUtils.GITHUB_RATE_LIMITED in out
    assert "раз в час" in out


def test_healthy_token_still_runs_the_time_machine(monkeypatch):
    from fetch_proxy import ProxyUtils

    hunter = _hunter_with_token(monkeypatch)
    monkeypatch.setattr(ProxyUtils, "check_github_token",
                        staticmethod(lambda t, timeout=10: (True, "", 5000)))

    called = []
    monkeypatch.setattr(ProxyUtils, "fetch_github_commits",
                        staticmethod(lambda *a, **kw: called.append(a[0]) or ([], {}, "")))

    hunter.collect()
    assert len(called) == 3, "все три GitHub-источника должны быть опрошены"


def test_per_source_failures_are_summarised(monkeypatch, capsys):
    from fetch_proxy import ProxyUtils

    hunter = _hunter_with_token(monkeypatch)
    monkeypatch.setattr(ProxyUtils, "check_github_token",
                        staticmethod(lambda t, timeout=10: (True, "", 5000)))
    monkeypatch.setattr(ProxyUtils, "fetch_github_commits",
                        staticmethod(lambda *a, **kw: ([], {}, "репозиторий или файл не найден (404)")))

    hunter.collect()
    out = capsys.readouterr().out
    assert "Не удалось прочитать историю: 3" in out
    assert "404" in out


def test_a_repo_without_recent_commits_is_not_reported_as_a_failure(monkeypatch, capsys):
    """Разница, ради которой всё делалось: пусто — это не отказ."""
    from fetch_proxy import ProxyUtils

    hunter = _hunter_with_token(monkeypatch)
    monkeypatch.setattr(ProxyUtils, "check_github_token",
                        staticmethod(lambda t, timeout=10: (True, "", 5000)))
    monkeypatch.setattr(ProxyUtils, "fetch_github_commits",
                        staticmethod(lambda *a, **kw: ([], {}, "")))

    hunter.collect()
    assert "Не удалось прочитать историю" not in capsys.readouterr().out
