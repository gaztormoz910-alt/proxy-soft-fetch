"""Сохранение результатов (AUDIT.md, REL-04).

run() начинался с shutil.rmtree(results) — старые результаты уничтожались до
того, как получены новые. Упавший, отменённый или безрезультатный прогон
оставлял пользователя и без старых данных, и без новых.
"""
import os

import pytest

from fetch_proxy import ProxyHunter


@pytest.fixture
def hunter(tmp_path):
    h = ProxyHunter(threads=1, output_dir=str(tmp_path))
    h.db_reader = None
    return h


def results_dir(tmp_path):
    return tmp_path / "results"


def read(path):
    return path.read_text(encoding="utf-8").splitlines()


# ------------------------------------------------------------- запись файлов

def test_saves_every_category(hunter, tmp_path):
    hunter.live_results = ["http://1.1.1.1:80"]
    hunter.elite_results = ["http://2.2.2.2:80"]
    hunter.results_datacenter = ["http://3.3.3.3:80"]
    hunter.results_residential = ["http://4.4.4.4:80"]
    hunter.results_mobile = ["http://5.5.5.5:80"]

    hunter.save()

    d = results_dir(tmp_path)
    assert sorted(p.name for p in d.iterdir()) == [
        "alive.txt", "datacenter.txt", "elite.txt", "mobile.txt", "residential.txt"]


def test_file_starts_with_a_count_header(hunter, tmp_path):
    hunter.live_results = ["http://1.1.1.1:80", "http://2.2.2.2:80"]
    hunter.save()

    lines = read(results_dir(tmp_path) / "alive.txt")
    assert lines[0].startswith("#") and lines[0].endswith(": 2")
    assert lines[1:] == ["http://1.1.1.1:80", "http://2.2.2.2:80"]


def test_empty_categories_produce_no_file(hunter, tmp_path):
    hunter.live_results = ["http://1.1.1.1:80"]
    hunter.save()
    assert not (results_dir(tmp_path) / "elite.txt").exists()


# --------------------------------------------------------- атомарная подмена

def test_previous_results_survive_until_the_new_ones_are_written(hunter, tmp_path):
    d = results_dir(tmp_path)
    d.mkdir()
    (d / "alive.txt").write_text("# старое: 1\nhttp://9.9.9.9:80\n", encoding="utf-8")

    hunter.live_results = ["http://1.1.1.1:80"]
    hunter.save()

    assert read(d / "alive.txt")[1:] == ["http://1.1.1.1:80"]


def test_stale_files_from_the_previous_run_are_gone(hunter, tmp_path):
    d = results_dir(tmp_path)
    d.mkdir()
    (d / "elite.txt").write_text("# старое: 1\nhttp://9.9.9.9:80\n", encoding="utf-8")

    hunter.live_results = ["http://1.1.1.1:80"]
    hunter.save()

    assert not (d / "elite.txt").exists(), "результаты прошлого прогона не должны смешиваться"


def test_no_staging_or_backup_directory_is_left_behind(hunter, tmp_path):
    hunter.live_results = ["http://1.1.1.1:80"]
    hunter.save()

    leftovers = [p.name for p in tmp_path.iterdir() if p.name != "results"]
    assert leftovers == [], f"остались временные папки: {leftovers}"


def test_a_leftover_staging_directory_is_reused_cleanly(hunter, tmp_path):
    stale = tmp_path / "results.new"
    stale.mkdir()
    (stale / "мусор.txt").write_text("хлам", encoding="utf-8")

    hunter.live_results = ["http://1.1.1.1:80"]
    hunter.save()

    assert not (results_dir(tmp_path) / "мусор.txt").exists()


def test_run_does_not_delete_results_before_collecting(hunter, tmp_path, monkeypatch):
    """Ключевое свойство REL-04: неудачный прогон не должен стирать прошлые данные."""
    d = results_dir(tmp_path)
    d.mkdir()
    (d / "alive.txt").write_text("# старое: 1\nhttp://9.9.9.9:80\n", encoding="utf-8")

    monkeypatch.setattr(hunter, "_download_mmdb_if_needed", lambda: None)
    monkeypatch.setattr(hunter, "open_geoip", lambda: False)   # прогон прервётся

    hunter.run()

    assert (d / "alive.txt").exists(), "прошлые результаты уничтожены неудачным прогоном"
    assert read(d / "alive.txt")[1:] == ["http://9.9.9.9:80"]


def test_output_directory_is_created_if_missing(tmp_path):
    target = tmp_path / "новая" / "папка"
    h = ProxyHunter(threads=1, output_dir=str(target))
    h.db_reader = None
    h.live_results = ["http://1.1.1.1:80"]
    h.save()
    assert (target / "results" / "alive.txt").exists()


def test_results_directory_is_replaced_not_merged(hunter, tmp_path):
    hunter.live_results = ["http://1.1.1.1:80"]
    hunter.elite_results = ["http://2.2.2.2:80"]
    hunter.save()

    hunter.elite_results = []
    hunter.live_results = ["http://3.3.3.3:80"]
    hunter.save()

    d = results_dir(tmp_path)
    assert sorted(p.name for p in d.iterdir()) == ["alive.txt"]
    assert read(d / "alive.txt")[1:] == ["http://3.3.3.3:80"]


def test_save_reports_where_results_are_when_the_swap_fails(hunter, tmp_path, monkeypatch, capsys):
    hunter.live_results = ["http://1.1.1.1:80"]

    def refuse(src, dst):
        raise OSError("папка занята другим процессом")

    monkeypatch.setattr(os, "rename", refuse)
    hunter.save()

    out = capsys.readouterr().out
    assert "results.new" in out, "пользователю нужно сказать, где лежат данные"
    assert (tmp_path / "results.new" / "alive.txt").exists()
