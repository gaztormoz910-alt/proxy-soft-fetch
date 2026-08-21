"""Учёт «живых» и прогресса в чекере (AUDIT.md, COR-12, COR-15, REL-07)."""
import threading

import gui
from gui import ProxyHunterApp


# --------------------------------------------------- COR-12: что такое «живой»

def alive(value):
    return ProxyHunterApp._is_alive_cell(value)


def test_pending_placeholder_is_not_alive():
    """Начальное «⏳» стояло во всех строках сразу после запуска, и счётчик
    «Только живые» показывал весь список."""
    assert alive("⏳") is False


def test_real_ping_is_alive():
    for lang in ("RU", "EN"):
        assert alive(gui.LANG[lang]["chk_ping_ok"].format(123)) is True


def test_timeout_error_and_skip_are_not_alive():
    for lang in ("RU", "EN"):
        table = gui.LANG[lang]
        assert alive(table["chk_timeout"]) is False, lang
        assert alive(table["chk_error"]) is False, lang
        assert alive(table["chk_skip"]) is False, lang


def test_empty_cell_is_not_alive():
    assert alive("") is False


def test_predicate_is_language_independent():
    """Признак — сам символ, а не переведённый текст."""
    assert alive("⏳ Timeout") is False
    assert alive("⏳ Таймаут") is False
    assert alive("❌ Error") is False
    assert alive("❌ Ошибка") is False
    assert alive("— Skip") is False
    assert alive("— Пропуск") is False


def test_old_metrics_predicate_disagreed_with_the_filter():
    """Фиксирует само расхождение, ради которого предикат стал общим.

    Счётчик сравнивал значение с переводами chk_timeout/chk_skip/chk_error,
    фильтр искал символы ❌/⏳/—. На плейсхолдере «⏳» они расходились: счётчик
    считал строку живой, фильтр её прятал.
    """
    ru = gui.LANG["RU"]

    def old_metrics_predicate(ping):
        text = str(ping)
        return bool(text) and text not in (ru["chk_timeout"], ru["chk_skip"], ru["chk_error"])

    assert old_metrics_predicate("⏳") is True, "старый счётчик считал ожидание живым"
    assert ProxyHunterApp._is_alive_cell("⏳") is False, "теперь — нет"

    # на всех прочих статусах старое и новое поведение совпадают
    for status in (ru["chk_timeout"], ru["chk_skip"], ru["chk_error"], ru["chk_ping_ok"].format(42)):
        assert old_metrics_predicate(status) == ProxyHunterApp._is_alive_cell(status), status


# ------------------------------------------- COR-15 / REL-07: счётчик прогресса

class FakeChecker:
    """Минимальный носитель состояния для _update_check_row."""

    PROGRESS_COLUMNS = ProxyHunterApp.PROGRESS_COLUMNS
    _update_check_row = ProxyHunterApp._update_check_row

    def __init__(self, counted_columns):
        self._log_lock = threading.Lock()
        self._checker_pending_updates = {}
        self._checker_progress_columns = counted_columns
        self._checker_total = 100
        self._checker_done = 0


def test_only_enabled_columns_advance_the_progress():
    """COR-15: отключённые проверки заполняются «Пропуском» мгновенно.

    Если считать все пять шагов, полоса прыгает до ~80% и потом ползёт.
    """
    app = FakeChecker({"ping"})
    for col in ("ping", "anon", "bl", "speed", "smtp"):
        app._update_check_row("http://1.2.3.4:80", col, "x")
    assert app._checker_done == 1, "засчитан должен быть только включённый шаг"


def test_all_enabled_columns_advance_the_progress():
    app = FakeChecker({"ping", "anon", "bl", "speed", "smtp"})
    for col in ("ping", "anon", "bl", "speed", "smtp"):
        app._update_check_row("http://1.2.3.4:80", col, "x")
    assert app._checker_done == 5


def test_non_progress_columns_never_count():
    app = FakeChecker({"ping"})
    app._update_check_row("http://1.2.3.4:80", "country", "US")
    app._update_check_row("http://1.2.3.4:80", "category", "Datacenter")
    assert app._checker_done == 0


def test_counter_is_exact_under_concurrency():
    """REL-07, санити-проверка (не доказательство прежней гонки).

    `self._checker_done += 1` компилируется в LOAD_ATTR / ADD / STORE_ATTR и
    атомарным языком не гарантируется, хотя прежний комментарий в коде
    утверждал обратное. Воспроизвести потерю инкрементов на CPython 3.13 не
    удалось даже при sys.setswitchinterval(1e-6) — то есть на этой версии
    интерпретатора старый код, вероятно, тоже досчитывал верно.

    Инкремент всё равно перенесён под уже захваченный лок: это бесплатно и
    снимает зависимость от детали реализации. Тест фиксирует, что счётчик
    точен, но упасть на старом коде он не обязан.
    """
    app = FakeChecker({"ping"})
    app._checker_total = 10 ** 9
    threads_count, per_thread = 16, 500

    def worker(n):
        for i in range(per_thread):
            app._update_check_row(f"http://1.2.3.{n}:{i}", "ping", "10 ms")

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(threads_count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert app._checker_done == threads_count * per_thread
