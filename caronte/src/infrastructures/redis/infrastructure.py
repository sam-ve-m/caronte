import aioredis
from caronte.src.infrastructures.env_config import config


class RedisInfrastructure:
    __redis = None
    __url = f'{config("CARONTE_REDIS_HOST")}?db={config("CARONTE_REDIS_DB")}'

    @classmethod
    def get_redis(cls):
        if cls.__redis is None:
            cls.__redis = aioredis.from_url(cls.__url)
        return cls.__redis
