import orjson
from typing import Optional, Union
from caronte.src.infrastructures.env_config import config
from caronte.src.infrastructures.redis.infrastructure import RedisInfrastructure


class Cache(RedisInfrastructure):
    redis_host = config("CARONTE_REDIS_HOST")
    redis_db = config("CARONTE_REDIS_DB")
    prefix = "caronte:"

    @classmethod
    async def set(cls, key: str, value: Union[dict, str], ttl: int = 0) -> None:
        redis = cls.get_redis()
        key = f"{cls.prefix}{key}"
        json_payload = orjson.dumps(value)
        if ttl > 0:
            await redis.set(name=key, value=json_payload, ex=ttl)
        else:
            await redis.set(name=key, value=json_payload)

    @classmethod
    async def get(cls, key: str) -> Optional[dict]:
        redis = cls.get_redis()
        if type(key) != str:
            return
        key = f"{cls.prefix}{key}"
        value = await redis.get(name=key)
        if value:
            dict_payload = orjson.loads(value)
            return dict_payload

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
