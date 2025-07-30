import asyncio

from smooth_criminal.core import moonwalk


@moonwalk
async def async_add(x, y):
    await asyncio.sleep(0.01)
    return x + y


@moonwalk
def sync_add(x, y):
    return x + y


def test_moonwalk_with_async_function():
    result = asyncio.run(async_add(1, 2))
    assert result == 3


def test_moonwalk_with_sync_function():
    result = asyncio.run(sync_add(3, 4))
    assert result == 7

