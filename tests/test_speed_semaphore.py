import asyncio

import pytest

from fetch_proxy import ProxyHunter


def run_in_fresh_loop(coro_factory):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro_factory())
    finally:
        loop.close()
        asyncio.set_event_loop(None)


def test_semaphore_starts_unset():
    assert ProxyHunter(threads=1)._speed_sem is None


def test_reset_gives_each_loop_its_own_semaphore():
    hunter = ProxyHunter(threads=1)
    seen = []

    async def body():
        hunter._reset_speed_semaphore()
        seen.append(hunter._speed_sem)

        async def worker():
            async with hunter._speed_sem:
                await asyncio.sleep(0)

        await asyncio.gather(*[worker() for _ in range(hunter.SPEED_TEST_CONCURRENCY * 2)])

    run_in_fresh_loop(body)
    run_in_fresh_loop(body)

    assert len(seen) == 2
    assert seen[0] is not seen[1], "на второй цикл должен быть создан новый семафор"


def test_reusing_a_semaphore_across_loops_really_does_raise():
    hunter = ProxyHunter(threads=1)

    async def body():
        if hunter._speed_sem is None:
            hunter._reset_speed_semaphore()

        async def worker():
            async with hunter._speed_sem:
                await asyncio.sleep(0)

        await asyncio.gather(*[worker() for _ in range(hunter.SPEED_TEST_CONCURRENCY * 2)])

    run_in_fresh_loop(body)
    with pytest.raises(RuntimeError, match="different event loop"):
        run_in_fresh_loop(body)


def test_semaphore_capacity_matches_the_declared_limit():
    hunter = ProxyHunter(threads=1)

    async def body():
        hunter._reset_speed_semaphore()
        return hunter._speed_sem._value

    assert run_in_fresh_loop(body) == hunter.SPEED_TEST_CONCURRENCY
