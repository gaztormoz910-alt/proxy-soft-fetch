import asyncio
import sys
import threading
import types

import pytest

from fetch_proxy import ProxyHunter, ProxyUtils

WATCHDOG_SECONDS = 20


def run_guarded(fn):
    box = {}

    def target():
        try:
            box["result"] = fn()
        except BaseException as exc:
            box["error"] = exc

    worker = threading.Thread(target=target, daemon=True)
    worker.start()
    worker.join(WATCHDOG_SECONDS)
    if worker.is_alive():
        pytest.fail(f"воркер не завершился за {WATCHDOG_SECONDS} c — queue.join() завис")
    if "error" in box:
        raise box["error"]
    return box.get("result")


class ExplodingBar:

    updates = 0

    def __init__(self, *a, **kw):
        pass

    def update(self, n=1):
        type(self).updates += 1
        raise RuntimeError("main thread is not in main loop")

    def close(self):
        pass


async def _alive():
    return {"http"}


@pytest.fixture
def hunter(monkeypatch):
    h = ProxyHunter(threads=2, timeout=1, min_speed=0.0, max_ping=0.0)
    h.db_reader = None
    h.countries = set()
    monkeypatch.setattr(ProxyUtils, "async_check_proxy",
                        staticmethod(lambda ip, port, protos, timeout: _alive()))
    monkeypatch.setattr(ProxyHunter, "_get_country", lambda self, ip: "US")
    return h


@pytest.fixture
def exploding_tqdm(monkeypatch):
    ExplodingBar.updates = 0
    monkeypatch.setitem(sys.modules, "tqdm", types.SimpleNamespace(tqdm=ExplodingBar))
    return ExplodingBar


def test_validate_finishes_even_if_the_progress_bar_raises(hunter, exploding_tqdm):
    hunter.candidate_generator = iter([("8.8.8.8:8080", ["http"]), ("1.1.1.1:3128", ["http"])])
    hunter.candidate_total = 2

    run_guarded(hunter.validate)

    assert exploding_tqdm.updates > 0, "падающий прогресс-бар не был задействован — тест вхолостую"
    assert sorted(hunter.live_results) == ["http://1.1.1.1:3128", "http://8.8.8.8:8080"], (
        "результаты обязаны сохраниться, несмотря на сломанный прогресс-бар")


def test_advanced_filter_finishes_even_if_the_progress_bar_raises(hunter, exploding_tqdm):
    hunter.live_results = ["http://8.8.8.8:8080", "http://1.1.1.1:3128"]
    hunter.max_ping = 0.0
    hunter.min_speed = 0.0
    hunter.check_smtp = False
    hunter._batch_ip_info = lambda ips: None
    hunter._batch_asn_type = lambda: None

    run_guarded(lambda: hunter.advanced_filter())

    assert exploding_tqdm.updates > 0
    assert sorted(hunter.elite_results) == ["http://1.1.1.1:3128", "http://8.8.8.8:8080"]


def test_validate_finishes_when_the_worker_body_raises(hunter, monkeypatch):
    monkeypatch.setattr(ProxyHunter, "_get_country",
                        lambda self, ip: (_ for _ in ()).throw(ValueError("сломанный geoip")))

    hunter.candidate_generator = iter([("8.8.8.8:8080", ["http"])])
    hunter.candidate_total = 1

    run_guarded(hunter.validate)
    assert hunter.live_results == []


def test_cancelled_items_are_still_marked_done(hunter):
    hunter.candidate_generator = iter([(f"8.8.8.{i}:8080", ["http"]) for i in range(1, 20)])
    hunter.candidate_total = 19
    hunter.cancel()

    run_guarded(hunter.validate)
    assert hunter.live_results == []


def test_queue_join_completes_only_when_task_done_is_in_finally():
    async def scenario(task_done_in_finally):
        queue = asyncio.Queue()
        for i in range(3):
            queue.put_nowait(i)

        async def worker():
            while True:
                await queue.get()
                try:
                    raise RuntimeError("что угодно")
                except Exception:
                    pass
                finally:
                    if task_done_in_finally:
                        queue.task_done()

        task = asyncio.create_task(worker())
        try:
            await asyncio.wait_for(queue.join(), timeout=1)
            return True
        except asyncio.TimeoutError:
            return False
        finally:
            task.cancel()

    assert asyncio.run(scenario(True)) is True
    assert asyncio.run(scenario(False)) is False, "без finally очередь обязана зависнуть"
