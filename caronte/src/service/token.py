# Caronte
from caronte.src.domain.enums.http_methods import AllowedHTTPMethods
from caronte.src.domain.exceptions.service.exception import TokenNotFoundInContent
from caronte.src.domain.models.authentication.response.model import (
    LockAuthenticationStatus,
)
from caronte.src.infrastructures.env_config import config
from caronte.src.repositories.authentication.distribuited_lock_manager.repository import (
    AuthenticationLockManagerRepository,
)
from caronte.src.transports.ouroinvest.transport import HTTPTransport
from caronte.src.repositories.cache.repository import Cache

# Standards
import asyncio
from contextlib import asynccontextmanager

# Third party
from etria_logger import Gladsheim


class TokenService:
    cache = Cache

    @classmethod
    async def get_company_token(cls) -> dict:
        default_token_cache_key = cls._default_token_cache_key()
        token = await cls.cache.get(default_token_cache_key)
        if not token:
            hash = "default_token"
            async with cls._lock_token_generation(hash=hash, cache_key=default_token_cache_key) as lock:
                if lock:
                    await cls.cache.delete_folder(cls._base_tokens_cache_folder())
                    token = await cls._request_new_token()
                    await cls.cache.set(default_token_cache_key, token, 12 * 60 * 60)
            token = await cls.cache.get(default_token_cache_key)
        return token

    @classmethod
    async def get_user_token(cls, exchange_account_id: int) -> dict:
        user_token_cache_key = cls._user_token_cache_key_format(exchange_account_id)
        default_token = await cls.get_company_token()
        user_token = await cls.cache.get(user_token_cache_key)
        if not user_token:
            hash = f"cliente:{exchange_account_id}"
            async with cls._lock_token_generation(hash=hash, cache_key=user_token_cache_key) as lock:
                if lock:
                    user_token = await cls._request_new_user_token(
                        exchange_account_id, default_token
                    )
                    await cls.cache.set(user_token_cache_key, user_token, 12 * 60 * 60)
            user_token = await cls.cache.get(user_token_cache_key)
        return user_token

    @classmethod
    @asynccontextmanager
    async def _lock_token_generation(cls, hash: str, cache_key: str):
        lock = None
        try:
            while True:
                if await cls.cache.get(cache_key):
                    yield lock
                    break
                (
                    call_status,
                    status,
                    lock,
                ) = await AuthenticationLockManagerRepository.lock_authentication(
                    hash=hash
                )
                if status == LockAuthenticationStatus.SUCCESS:
                    yield lock
                    break
                await asyncio.sleep(1)
        except Exception as err:
            message = f"{cls.__class__}:validate_token_redis:Error - {err}"
            Gladsheim.error(error=err, message=message)
        finally:
            if lock:
                await AuthenticationLockManagerRepository.unlock_authentication(
                    lock=lock
                )

    # @classmethod
    # async def delete_default_token(cls):
    #     await cls.cache.delete(cls._default_token_cache_key())  # TODO: Validar necessidade

    @classmethod
    async def _request_new_token(cls) -> dict:
        body = {
            "chave": config("OUROINVEST_SYSTEM_USER"),
            "senha": config("OUROINVEST_SYSTEM_PWD"),
        }
        success, caronte_status, content = await HTTPTransport.request_method(
            method=AllowedHTTPMethods.POST,
            url=config("OUROINVEST_DEFAULT_TOKEN_URL"),
            body=body,
        )

        token = content.get("tokenAcesso", {}).get("token")
        if not token:
            raise TokenNotFoundInContent
        return cls._get_auth(token)

    @classmethod
    async def _request_new_user_token(cls, client_code: int, auth: dict) -> dict:
        body = {"codigoCliente": client_code}
        success, caronte_status, content = await HTTPTransport.request_method(
            method=AllowedHTTPMethods.POST,
            url=config("OUROINVEST_USER_TOKEN_URL"),
            body=body,
            headers=auth,
        )
        user_token = content.get("tokenAcesso", {}).get("token")
        if not user_token:
            raise TokenNotFoundInContent
        return cls._get_auth(user_token)

    @staticmethod
    def _base_tokens_cache_folder():
        return config("OUROINVEST_BASE_TOKENS_CACHE_FOLDER")

    @classmethod
    def _default_token_cache_key(cls):
        return cls._base_tokens_cache_folder() + config(
            "OUROINVEST_DEFAULT_TOKEN_CACHE_KEY"
        )

    @classmethod
    def _user_token_cache_key_format(cls, client_code: int):
        url = cls._base_tokens_cache_folder() + config(
            "OUROINVEST_USER_TOKEN_CACHE_KEY"
        )
        url = url.format(client_code)
        return url

    @staticmethod
    def _get_auth(token) -> dict:
        return {"Authorization": f"Bearer {token}"}
