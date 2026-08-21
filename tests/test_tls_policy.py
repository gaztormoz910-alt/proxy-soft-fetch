"""Тесты политики проверки TLS при загрузке источников (AUDIT.md, SEC-02).

Раньше fetch_url() ходил во все 1710 источников с verify=False, то есть любой
посредник мог подменить список прокси. Теперь сертификат проверяется, а обход
возможен только при явно включённом флаге и только при SSLError.
"""
import pytest
import requests
import responses

from fetch_proxy import ProxyHunter, ProxyUtils


@pytest.fixture(autouse=True)
def strict_by_default():
    """Каждый тест стартует с безопасной политикой и не протекает в соседние."""
    saved = ProxyUtils.ALLOW_INSECURE_SOURCES
    ProxyUtils.ALLOW_INSECURE_SOURCES = False
    ProxyUtils._insecure_hosts_logged.clear()
    yield
    ProxyUtils.ALLOW_INSECURE_SOURCES = saved
    ProxyUtils._insecure_hosts_logged.clear()


def _fake_response(url, body):
    """requests.Response с уже прочитанным телом.

    _content_consumed обязателен: без него iter_content() уходит в пустой
    self.raw и fetch_url возвращает пустую строку.
    """
    resp = requests.Response()
    resp.status_code = 200
    resp._content = body.encode()
    resp._content_consumed = True
    resp.url = url
    resp.headers["Content-Type"] = "text/plain"
    return resp


class FakeCookies:
    def __init__(self):
        self.cleared = 0

    def clear(self):
        self.cleared += 1


class Recorder:
    """Подменяет сессию ProxyUtils и запоминает, с каким verify её звали.

    Патчим именно сессию, а не requests.get: fetch_url ходит через
    потоко-локальную requests.Session ради переиспользования соединений.
    """

    def __init__(self, monkeypatch, fail_first_with_ssl_error=False, body="8.8.8.8:8080"):
        self.calls = []
        self.fail_first = fail_first_with_ssl_error
        self.body = body
        self.cookies = FakeCookies()
        monkeypatch.setattr(ProxyUtils, "_session", classmethod(lambda cls: self))

    def get(self, url, **kwargs):
        self.calls.append(kwargs.get("verify", "default"))
        if self.fail_first and len(self.calls) == 1:
            raise requests.exceptions.SSLError("certificate verify failed")
        return _fake_response(url, self.body)


def test_verification_is_on_by_default(monkeypatch):
    rec = Recorder(monkeypatch)
    ProxyUtils.fetch_url("https://example.test/list.txt", timeout=5)
    # 'default' означает, что verify не передавался — requests проверяет сертификат
    assert rec.calls == ["default"]


def test_tls_failure_is_not_silently_bypassed(monkeypatch):
    rec = Recorder(monkeypatch, fail_first_with_ssl_error=True)
    assert ProxyUtils.fetch_url("https://broken.test/list.txt", timeout=5) == ""
    assert rec.calls == ["default"], "не должно быть повторной попытки без проверки"


def test_flag_enables_a_single_insecure_retry(monkeypatch, capsys):
    ProxyUtils.ALLOW_INSECURE_SOURCES = True
    rec = Recorder(monkeypatch, fail_first_with_ssl_error=True)
    body = ProxyUtils.fetch_url("https://broken.test/list.txt", timeout=5)
    assert body == "8.8.8.8:8080"
    assert rec.calls == ["default", False]
    assert "broken.test" in capsys.readouterr().out


def test_insecure_warning_is_printed_once_per_host(monkeypatch, capsys):
    ProxyUtils.ALLOW_INSECURE_SOURCES = True

    # Оба запроса к одному хосту падают по SSL и оба уходят в повтор,
    # но предупреждение должно быть напечатано ровно один раз.
    class TwoFailures(Recorder):
        def get(self, url, **kwargs):
            self.calls.append(kwargs.get("verify", "default"))
            if kwargs.get("verify", "default") == "default":
                raise requests.exceptions.SSLError("certificate verify failed")
            return _fake_response(url, "8.8.8.8:8080")

    TwoFailures(monkeypatch)
    ProxyUtils.fetch_url("https://broken.test/a.txt", timeout=5)
    ProxyUtils.fetch_url("https://broken.test/b.txt", timeout=5)
    assert capsys.readouterr().out.count("broken.test") == 1


def test_non_ssl_errors_are_never_retried(monkeypatch):
    calls = []

    class Timeout:
        cookies = FakeCookies()

        def get(self, url, **kwargs):
            calls.append(kwargs.get("verify", "default"))
            raise requests.exceptions.ConnectTimeout("timeout")

    ProxyUtils.ALLOW_INSECURE_SOURCES = True
    monkeypatch.setattr(ProxyUtils, "_session", classmethod(lambda cls: Timeout()))
    assert ProxyUtils.fetch_url("https://slow.test/list.txt", timeout=5) == ""
    assert calls == ["default"], "таймаут — не повод отключать проверку сертификата"


# ------------------------------------------------- проброс флага из ProxyHunter

def test_hunter_sets_the_policy_when_asked():
    ProxyHunter(threads=1, allow_insecure_sources=True)
    assert ProxyUtils.ALLOW_INSECURE_SOURCES is True
    ProxyHunter(threads=1, allow_insecure_sources=False)
    assert ProxyUtils.ALLOW_INSECURE_SOURCES is False


def test_hunter_leaves_the_policy_alone_by_default():
    """Вспомогательный ProxyHunter(threads=1) из чекера не должен сбрасывать
    флаг, выставленный запущенным сбором."""
    ProxyUtils.ALLOW_INSECURE_SOURCES = True
    ProxyHunter(threads=1)
    assert ProxyUtils.ALLOW_INSECURE_SOURCES is True


# ---------------------------------------------------------------- integration

@responses.activate
def test_fetch_url_still_returns_body_over_plain_http():
    """Регрессия: включение проверки TLS не должно ломать http:// источники."""
    responses.add(responses.GET, "http://plain.test/list.txt",
                  body="8.8.8.8:8080\n1.1.1.1:3128\n", status=200,
                  content_type="text/plain")
    body = ProxyUtils.fetch_url("http://plain.test/list.txt", timeout=5)
    assert sorted(ProxyUtils.parse_proxies(body)) == ["1.1.1.1:3128", "8.8.8.8:8080"]


# ------------------------------------------- PERF-03: переиспользование соединений

def test_session_is_reused_within_a_thread():
    """Пул соединений имеет смысл, только если сессия одна на поток."""
    ProxyUtils._thread_state.__dict__.pop("session", None)
    first = ProxyUtils._session()
    assert ProxyUtils._session() is first


def test_each_thread_gets_its_own_session():
    """requests.Session не потокобезопасна, а сбор идёт из пула на 50 воркеров."""
    import threading

    ProxyUtils._thread_state.__dict__.pop("session", None)
    main_session = ProxyUtils._session()
    other = {}

    def grab():
        other["session"] = ProxyUtils._session()

    t = threading.Thread(target=grab)
    t.start()
    t.join()

    assert other["session"] is not main_session


def test_session_mounts_a_pooled_adapter():
    ProxyUtils._thread_state.__dict__.pop("session", None)
    session = ProxyUtils._session()
    for prefix in ("http://", "https://"):
        adapter = session.get_adapter(prefix + "example.test")
        assert adapter._pool_maxsize >= 20, prefix


def test_cookies_do_not_leak_between_sources(monkeypatch):
    """requests.get() куки не хранил — сессия не должна менять это поведение."""
    rec = Recorder(monkeypatch)
    ProxyUtils.fetch_url("https://a.test/list.txt", timeout=5)
    ProxyUtils.fetch_url("https://b.test/list.txt", timeout=5)
    assert rec.cookies.cleared == 2, "куки должны сбрасываться перед каждым запросом"
