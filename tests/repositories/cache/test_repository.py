from unittest.mock import patch, AsyncMock, MagicMock
from decouple import Config, RepositoryEnv

import orjson
import pytest

from tests.test_utils.utils import create_async_iterable_object

with patch.object(RepositoryEnv, "__init__", return_value=None):
    with patch.object(Config, "__init__", return_value=None):
        from caronte.src.repositories.cache.repository import Cache


dummy_key = "key"
dummy_value = "value"
dummy_prefix = "prefix"
dummy_prefix_key = "prefixkey"
dummy_prefix_folder = "prefixkey:*"

fake_redis = AsyncMock()


@pytest.mark.asyncio
@patch.object(Cache, "get_redis", return_value=fake_redis)
@patch.object(orjson, "dumps", return_value=dummy_value)
async def test_set(mocked_orjson, mocked_get_redis, monkeypatch):
    monkeypatch.setattr(Cache, "prefix", dummy_prefix)
    await Cache.set(dummy_key, dummy_value)
    fake_redis.set.assert_called_once_with(name=dummy_prefix_key, value=dummy_value, ex=None)
    mocked_get_redis.assert_called_once_with()
    mocked_orjson.assert_called_once_with(dummy_value)


@pytest.mark.asyncio
@patch.object(Cache, "get_redis", return_value=fake_redis)
@patch.object(orjson, "loads", return_value=dummy_value)
async def test_get(mocked_orjson, mocked_get_redis, monkeypatch):
    monkeypatch.setattr(Cache, "prefix", dummy_prefix)
    fake_redis.get.return_value = dummy_value
    response = await Cache.get(dummy_key)
    fake_redis.get.assert_called_once_with(name=dummy_prefix_key)
    mocked_get_redis.assert_called_once_with()
    mocked_orjson.assert_called_once_with(dummy_value)
    assert dummy_value == response


@pytest.mark.asyncio
@patch.object(Cache, "get_redis", return_value=fake_redis)
@patch.object(orjson, "loads", return_value=dummy_value)
async def test_get_empty(mocked_orjson, mocked_get_redis, monkeypatch):
    monkeypatch.setattr(Cache, "prefix", dummy_prefix)
    fake_redis.get.return_value = None
    response = await Cache.get(dummy_key)
    fake_redis.get.assert_called_with(name=dummy_prefix_key)
    mocked_get_redis.assert_called_once_with()
    mocked_orjson.assert_not_called()
    assert response is None


@pytest.mark.asyncio
@patch.object(Cache, "get_redis", return_value=fake_redis)
async def test_delete(mocked_get_redis, monkeypatch):
    monkeypatch.setattr(Cache, "prefix", dummy_prefix)
    await Cache.delete(dummy_key)
    mocked_get_redis.assert_called_once_with()
    fake_redis.delete.assert_called_with(dummy_prefix_key)


@pytest.mark.asyncio
@patch.object(Cache, "get_redis", return_value=fake_redis)
@patch.object(Cache, "delete")
async def test_delete_folder(mocked_delete, mocked_get_redis, monkeypatch):
    monkeypatch.setattr(Cache, "prefix", dummy_prefix)
    fake_redis.scan_iter = MagicMock(return_value=create_async_iterable_object([dummy_key]))
    await Cache.delete_folder(dummy_key)
    mocked_get_redis.assert_called_once_with()
    fake_redis.scan_iter.assert_called_once_with(match=dummy_prefix_folder)
    mocked_delete.assert_called_once_with(dummy_key)
