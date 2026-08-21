"""Пауза в асинхронных воркерах (AUDIT.md, REL-02).

Корутины звали синхронный _wait_if_paused с time.sleep(0.5) внутри. Первый же
вставший на паузу воркер блокировал ВЕСЬ event loop: замирали и остальные
воркеры, и обновление прогресса, а таймауты уже открытых соединений при этом
продолжали тикать.
"""
import asyncio
import time

import pytest

from fetch_proxy import ProxyHunter


@pytest.fixture
def hunter():
    h = ProxyHunter(threads=1)
    h.db_reader = None
    return h


# ------------------------------------------------------ синхронный вариант

def test_sync_pause_returns_immediately_when_not_paused(hunter):
    start = time.perf_counter()
    assert hunter._wait_if_paused() is False
    assert time.perf_counter() - start < 0.1


def test_sync_pause_reports_cancellation(hunter):
    hunter.pause()
    hunter.cancel()          # cancel() снимает паузу
    assert hunter._wait_if_paused() is True


# ---------------------------------------------------- асинхронный вариант

async def test_async_pause_returns_immediately_when_not_paused(hunter):
    assert await hunter._await_if_paused() is False


async def test_async_pause_reports_cancellation(hunter):
    hunter.pause()
    hunter.cancel()
    assert await hunter._await_if_paused() is True


async def test_paused_worker_does_not_freeze_the_event_loop(hunter):
    """Ключевое свойство: пока один воркер на паузе, цикл продолжает крутиться."""
    hunter.pause()
    ticks = []

    async def ticker():
        for _ in range(10):
            ticks.append(1)
            await asyncio.sleep(0.01)

    paused = asyncio.create_task(hunter._await_if_paused())
    running = asyncio.create_task(ticker())

    await asyncio.sleep(0.15)
    ticks_during_pause = len(ticks)
    hunter.resume()

    assert await asyncio.wait_for(paused, timeout=2) is False
    await running

    # с синхронным time.sleep(0.5) тиков за это время не было бы вовсе
    assert ticks_during_pause >= 5, (
        f"цикл заморожен на время паузы: тиков {ticks_during_pause}")


async def test_resume_releases_the_worker_promptly(hunter):
    hunter.pause()
    task = asyncio.create_task(hunter._await_if_paused())
    await asyncio.sleep(0.05)
    assert not task.done()

    start = time.perf_counter()
    hunter.resume()
    await asyncio.wait_for(task, timeout=2)
    # шаг ожидания 0.1 c, а не 0.5 c как в синхронном варианте
    assert time.perf_counter() - start < 0.5


async def test_many_paused_workers_all_resume(hunter):
    hunter.pause()
    tasks = [asyncio.create_task(hunter._await_if_paused()) for _ in range(200)]
    await asyncio.sleep(0.05)
    hunter.resume()
    results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=3)
    assert results == [False] * 200
