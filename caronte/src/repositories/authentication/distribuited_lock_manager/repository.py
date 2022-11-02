from asyncio import Lock
from uuid import uuid4

from aioredlock import LockError, Aioredlock, LockAcquiringError, LockRuntimeError


from etria_logger import Gladsheim

from caronte.src.domain.models.authentication.response.model import (
    LockAuthenticationResponse,
    LockAuthenticationStatus,
    UnlockAuthenticationResponse,
    UnlockAuthenticationStatus,
)
from caronte.src.infrastructures.env_config import config
from caronte.src.infrastructures.redis.distribuited_lock_manager.infrastructure import (
    RedLockManagerInfrastructure,
)


class AuthenticationLockManagerRepository(RedLockManagerInfrastructure):

    redis_urls = config("CARONTE_CLIENT_LOCK_MANAGER_REDIS_URLS")
    retry_count = config("CARONTE_CLIENT_AUTHENTICATION_RETRY_COUNT")
    retry_delay_min = config("CARONTE_CLIENT_AUTHENTICATION_RETRY_DELAY_MIN")
    retry_delay_max = config("CARONTE_CLIENT_AUTHENTICATION_RETRY_DELAY_MAX")
    lock_time_out = config("CARONTE_CLIENT_AUTHENTICATION_LOCK_MANAGER_TIMEOUT")
    distributed_lock_manager_identifier = f"{config('CARONTE_CLIENT_AUTHENTICATION_LOCK_MANAGER_IDENTIFIER')}-{str(uuid4())}"

    @classmethod
    async def lock_authentication(cls, hash: str) -> LockAuthenticationResponse:
        lock_balance = (
            False,
            LockAuthenticationStatus.INTERNAL_SERVER_ERROR.value,
            None,
        )
        red_lock_manager: Aioredlock = cls.get_red_lock_manager()
        lock_balance_key = None

        try:
            lock = await red_lock_manager.lock(
                resource=f"caronte:ouroinvest:{hash}",
                lock_timeout=int(cls.lock_time_out),
                lock_identifier=cls.distributed_lock_manager_identifier,
            )
            lock_balance = (True, LockAuthenticationStatus.SUCCESS, lock)

        except LockAcquiringError as error:
            Gladsheim.error(
                message=f"Lock_balance::'Error in acquiring the lock balance resource during normal operation",
                lock_balance_key=lock_balance_key,
                error=error,
            )
            lock_balance = (False, LockAuthenticationStatus.ACQUIRING_LOCK_ERROR, None)

        except LockRuntimeError as error:
            Gladsheim.error(
                message=f"Lock_balance::Error in acquiring the balance resource lock due to an unexpected event",
                lock_balance_key=lock_balance_key,
                error=error,
            )
            lock_balance = (False, LockAuthenticationStatus.RUNTIME_LOCK_ERROR, None)

        except LockError as error:
            Gladsheim.error(
                message=f"{cls.__class__}::lock_balance::Error in acquiring the balance resource"
                f" lock",
                lock_balance_key=lock_balance_key,
                error=error,
            )
            lock_balance = (False, LockAuthenticationStatus.INTERNAL_LOCK_ERROR, None)

        except Exception as error:
            Gladsheim.error(
                message=f"{cls.__class__}::lock_balance::Error in acquiring the balance resource",
                lock_balance_key=lock_balance_key,
                error=error,
            )
            lock_balance = (False, LockAuthenticationStatus.INTERNAL_SERVER_ERROR, None)
        finally:
            return LockAuthenticationResponse(lock_balance)

    @classmethod
    async def unlock_authentication(cls, lock: Lock) -> UnlockAuthenticationResponse:
        unlock_balance_response = (
            False,
            UnlockAuthenticationStatus.INTERNAL_LOCK_ERROR,
        )
        try:
            red_lock_manager: Aioredlock = cls.get_red_lock_manager()
            await red_lock_manager.unlock(lock)
            unlock_balance_response = (True, UnlockAuthenticationStatus.SUCCESS)

        except LockRuntimeError as error:
            Gladsheim.error(
                message=f"{cls.__class__}::unlock_balance::Error in releasing the balance resource"
                f" lock due to an unexpected event",
                error=error,
            )
            unlock_balance_response = (
                False,
                UnlockAuthenticationStatus.RUNTIME_LOCK_ERROR,
            )

        except LockError as error:
            Gladsheim.error(
                message=f"{cls.__class__}::unlock_balance::Error in releasing the balance resource"
                f" lock",
                error=error,
            )
            unlock_balance_response = (
                False,
                UnlockAuthenticationStatus.INTERNAL_LOCK_ERROR,
            )

        except Exception as error:
            Gladsheim.error(
                message=f"{cls.__class__}::unlock_balance::Error in releasing the balance resource",
                error=error,
            )
            unlock_balance_response = (
                False,
                UnlockAuthenticationStatus.INTERNAL_SERVER_ERROR,
            )

        finally:
            return UnlockAuthenticationResponse(unlock_balance_response)
