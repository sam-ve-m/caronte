from aioredlock import Aioredlock

# Jotunheimr
from etria_logger import Gladsheim


class RedLockManagerInfrastructure:
    red_lock_manager = None

    redis_urls = None
    retry_count = None
    retry_delay_min = None
    retry_delay_max = None
    internal_lock_timeout = None

    @classmethod
    def get_red_lock_manager(cls) -> Aioredlock:
        if not cls.redis_urls:
            raise Exception("You are crazy!? redis_urls variable can't be None")

        if cls.red_lock_manager is None:
            try:
                cls.red_lock_manager = Aioredlock(
                    eval(cls.redis_urls),
                    retry_count=cls.retry_count,
                    retry_delay_min=cls.retry_delay_min,
                    retry_delay_max=cls.retry_delay_max,
                )

            except Exception as exception:
                Gladsheim.error(
                    message=f"RedisInfrastructure::_get_client::Error on client connection for the giving url",
                    error=exception,
                )
        return cls.red_lock_manager
