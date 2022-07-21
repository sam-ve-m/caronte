# OUTSIDE LIBRARIES
import aioredis


class RedisInfrastructure:
    __redis = None
    redis_host = None
    redis_db = None

    @classmethod
    def get_redis(cls):
        if cls.__redis is None:
            url = f"{cls.redis_host}?db={cls.redis_db}"
            cls.__redis = aioredis.from_url(url)
        return cls.__redis
