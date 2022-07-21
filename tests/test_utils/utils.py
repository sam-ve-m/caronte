from contextlib import asynccontextmanager
from unittest.mock import MagicMock, AsyncMock


def create_fake_async_context_yielding_value(value):
    async_mock = AsyncMock()
    async_mock.__anext__.side_effect = [value, StopAsyncIteration()] * 3
    fake_async_context = asynccontextmanager(MagicMock(return_value=async_mock))
    return fake_async_context


def create_async_iterable_object(values):
    async def gen(self):
        for item in values:
            yield item

    stub_async_iterable = AsyncMock(__aiter__=gen)
    return stub_async_iterable
