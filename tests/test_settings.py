"""Тесты загрузки/сохранения настроек (AUDIT.md, SEC-01).

Токен GitHub раньше хранился только в settings.json, который был закоммичен
в репозиторий. Теперь его можно передать через переменную окружения
GITHUB_TOKEN, и в этом случае он не должен попадать на диск.

_load_settings / _save_settings не обращаются к виджетам Tk, поэтому их можно
вызывать на подставном объекте.
"""
import json
import os

import pytest

from gui import ProxyHunterApp


class Var:
    """Заглушка tk.StringVar / BooleanVar."""

    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value


class FakeApp:
    # Обе функции работают только с обычными атрибутами и файловой системой,
    # виджеты Tk им не нужны — переиспользуем реальные реализации.
    _load_settings = ProxyHunterApp._load_settings
    _save_settings = ProxyHunterApp._save_settings

    def __init__(self, token="", out_dir="C:/out", tm_enabled=True, tm_days="7"):
        self.output_dir = Var(out_dir)
        self.github_token_var = Var(token)
        self.github_tm_enabled = Var(tm_enabled)
        self.github_tm_days_var = Var(tm_days)


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    """Изолированная рабочая директория: settings.json ищется относительно CWD."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    return tmp_path


def load():
    return ProxyHunterApp._load_settings(object())


def save(app):
    ProxyHunterApp._save_settings(app)


# ------------------------------------------------------------ _load_settings

def test_load_returns_empty_dict_when_file_absent(workdir):
    assert load() == {}


def test_load_reads_file(workdir):
    (workdir / "settings.json").write_text(
        json.dumps({"output_dir": "D:/proxies", "github_tm_days": 5}), encoding="utf-8")
    assert load() == {"output_dir": "D:/proxies", "github_tm_days": 5}


def test_load_survives_corrupted_json(workdir):
    (workdir / "settings.json").write_text("{не json", encoding="utf-8")
    assert load() == {}


def test_load_survives_json_that_is_not_an_object(workdir):
    """Раньше список вместо объекта ронял _save_settings на присваивании по ключу."""
    (workdir / "settings.json").write_text("[1, 2, 3]", encoding="utf-8")
    assert load() == {}


def test_env_token_overrides_file(workdir, monkeypatch):
    (workdir / "settings.json").write_text(
        json.dumps({"github_token": "из-файла"}), encoding="utf-8")
    monkeypatch.setenv("GITHUB_TOKEN", "из-окружения")
    assert load()["github_token"] == "из-окружения"


def test_env_token_works_without_any_file(workdir, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    assert load() == {"github_token": "ghp_test"}


def test_blank_env_token_does_not_shadow_file(workdir, monkeypatch):
    (workdir / "settings.json").write_text(
        json.dumps({"github_token": "из-файла"}), encoding="utf-8")
    monkeypatch.setenv("GITHUB_TOKEN", "   ")
    assert load()["github_token"] == "из-файла"


# ------------------------------------------------------------ _save_settings

def test_save_writes_all_fields(workdir):
    save(FakeApp(token="ghp_ручной", out_dir="D:/out", tm_enabled=False, tm_days="9"))
    written = json.loads((workdir / "settings.json").read_text(encoding="utf-8"))
    assert written == {
        "output_dir": "D:/out",
        "github_token": "ghp_ручной",
        "github_tm_enabled": False,
        "github_tm_days": 9,
    }


def test_save_never_persists_a_token_that_came_from_the_environment(workdir, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_секрет_из_окружения")
    # github_token_var инициализируется из _load_settings, т.е. значением из env
    save(FakeApp(token="ghp_секрет_из_окружения"))
    written = json.loads((workdir / "settings.json").read_text(encoding="utf-8"))
    assert "github_token" not in written
    assert "ghp_секрет_из_окружения" not in (workdir / "settings.json").read_text(encoding="utf-8")


def test_save_still_persists_a_token_typed_by_hand_even_if_env_is_set(workdir, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_из_окружения")
    save(FakeApp(token="ghp_введён_руками"))
    written = json.loads((workdir / "settings.json").read_text(encoding="utf-8"))
    assert written["github_token"] == "ghp_введён_руками"


def test_save_clamps_time_machine_days(workdir):
    save(FakeApp(tm_days="999"))
    assert json.loads((workdir / "settings.json").read_text(encoding="utf-8"))["github_tm_days"] == 30
    save(FakeApp(tm_days="0"))
    assert json.loads((workdir / "settings.json").read_text(encoding="utf-8"))["github_tm_days"] == 1


def test_save_falls_back_to_one_day_on_non_numeric_input(workdir):
    save(FakeApp(tm_days="абв"))
    assert json.loads((workdir / "settings.json").read_text(encoding="utf-8"))["github_tm_days"] == 1


def test_save_strips_newlines_from_pasted_token(workdir):
    save(FakeApp(token="  ghp_abc\r\n  "))
    written = json.loads((workdir / "settings.json").read_text(encoding="utf-8"))
    assert written["github_token"] == "ghp_abc"


# --------------------------------------------------------------- репозиторий

def test_settings_json_is_not_tracked_by_git():
    """Регрессия на SEC-01: файл с секретами не должен возвращаться в индекс."""
    import subprocess
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tracked = subprocess.run(
        ["git", "ls-files", "settings.json"],
        cwd=root, capture_output=True, text=True).stdout.strip()
    assert tracked == "", "settings.json снова попал под контроль версий"


# ---------------------------------------- SEC-04: определение своей страны

class CountryApp:
    _get_my_country = ProxyHunterApp._get_my_country
    _detect_my_country = ProxyHunterApp._detect_my_country

    def __init__(self):
        self._my_country = None
        self._my_country_resolved = False


def test_country_detection_is_lazy_and_cached(monkeypatch):
    """Раньше это делалось в __init__ синхронно, до отрисовки окна."""
    calls = []
    monkeypatch.setattr(CountryApp, "_detect_my_country",
                        lambda self: calls.append(1) or "DE")

    app = CountryApp()
    assert calls == [], "до первого обращения определять ничего не нужно"

    assert app._get_my_country() == "DE"
    assert app._get_my_country() == "DE"
    assert calls == [1], "определение должно выполняться ровно один раз"


def test_none_result_is_cached_too(monkeypatch):
    calls = []
    monkeypatch.setattr(CountryApp, "_detect_my_country",
                        lambda self: calls.append(1) or None)
    app = CountryApp()
    assert app._get_my_country() is None
    assert app._get_my_country() is None
    assert calls == [1], "неудачное определение не должно повторяться при каждом клике"


def test_locale_is_preferred_over_the_network(monkeypatch):
    """Локаль бесплатна, работает офлайн и не отправляет IP на сторону."""
    import locale as locale_mod
    import requests as requests_mod

    monkeypatch.setattr(locale_mod, "getlocale", lambda *a: ("de_DE", "UTF-8"))

    def must_not_be_called(*a, **kw):
        raise AssertionError("сеть не должна использоваться, когда локаль известна")

    monkeypatch.setattr(requests_mod, "get", must_not_be_called)
    assert CountryApp()._detect_my_country() == "DE"


def test_network_is_used_only_when_the_locale_says_nothing(monkeypatch):
    import locale as locale_mod
    import requests as requests_mod

    monkeypatch.setattr(locale_mod, "getlocale", lambda *a: (None, None))

    class Resp:
        status_code = 200
        text = "fr\n"

    monkeypatch.setattr(requests_mod, "get", lambda url, **kw: Resp())
    assert CountryApp()._detect_my_country() == "FR"


def test_detection_returns_none_when_everything_fails(monkeypatch):
    import locale as locale_mod
    import requests as requests_mod

    monkeypatch.setattr(locale_mod, "getlocale", lambda *a: (None, None))
    monkeypatch.setattr(requests_mod, "get",
                        lambda url, **kw: (_ for _ in ()).throw(OSError("нет сети")))
    assert CountryApp()._detect_my_country() is None
