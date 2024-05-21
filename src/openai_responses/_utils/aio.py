import asyncio
from typing import AsyncGenerator, Generator, TypeVar

T = TypeVar("T")

__all__ = ["make_async_generator"]


async def make_async_generator(
    sync_gen: Generator[T, None, None]
) -> AsyncGenerator[T, None]:
    for value in sync_gen:
        await asyncio.sleep(0)
        yield value
