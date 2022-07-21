from typing import Optional, Union

import orjson
from caronte.src.infrastructures.redis.infrastructure import RedisInfrastructure


class Cache(RedisInfrastructure):
    prefix = "caronte:"

    @classmethod
    async def set(cls, key: str, value: Union[dict, str], ttl: int = None):
        redis = cls.get_redis()
        key = f"{cls.prefix}{key}"
        json_payload = orjson.dumps(value)
        await redis.set(name=key, value=json_payload, ex=ttl)

    @classmethod
    async def get(cls, key: str) -> Optional[str]:
        redis = cls.get_redis()
        key = f"{cls.prefix}{key}"
        if value := await redis.get(name=key):
            value = orjson.loads(value)
        return value

    @classmethod
    async def delete(cls, key: str):
        redis = cls.get_redis()
        await redis.delete(f"{cls.prefix}{key}")

    @classmethod
    async def delete_folder(cls, folder: str):
        redis = cls.get_redis()
        keys_in_folder = redis.scan_iter(match=f"{cls.prefix}{folder}:*")
        async for key in keys_in_folder:
            await cls.delete(key)
