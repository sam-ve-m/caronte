import aioredis
from caronte.src.infrastructures.env_config import config


class RedisInfrastructure:
    __redis = None

    @classmethod
    def get_redis(cls):
        if cls.__redis is None:
            url = f'{config("CARONTE_REDIS_HOST")}?db={config("CARONTE_REDIS_DB")}'
            cls.__redis = aioredis.from_url(url)
        return cls.__redis
