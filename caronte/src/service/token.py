import asyncio
from contextlib import asynccontextmanager

from etria_logger import Gladsheim

from caronte.src.domain.enum import HTTPMethods
from caronte.src.domain.models.authentication.response.model import LockAuthenticationStatus
from caronte.src.infrastructures.env_config import config
from caronte.src.repositories.authentication.distribuited_lock_manager.repository import \
    AuthenticationLockManagerRepository
from caronte.src.transports.ouroinvest.transport import HTTPTransport
from caronte.src.repositories.cache.repository import Cache


class TokenService:
    cache = Cache

    @classmethod
    async def get_default_token(cls) -> dict:
        default_token_cache_key = cls._default_token_cache_key()
        token = await cls.cache.get(default_token_cache_key)
        if not token:
            hash = "default_token"
            async with cls._lock_token_generation(cls, hash=hash) as _:
                await cls.cache.delete_folder(cls._base_tokens_cache_folder())
                token = await cls._request_new_token()
                await cls.cache.set(default_token_cache_key, token, 12 * 60 * 60)
        return token

    @classmethod
    async def get_user_token(cls, client_code: int) -> dict:
        user_token_cache_key = cls._user_token_cache_key_format(client_code)
        default_token = await cls.get_default_token()
        user_token = await cls.cache.get(user_token_cache_key)
        if not user_token:
            hash = f"cleinte:{client_code}"
            async with cls._lock_token_generation(cls, hash=hash) as _:
                user_token = await cls._request_new_user_token(client_code, default_token)
                await cls.cache.set(user_token_cache_key, user_token, 12 * 60 * 60)
        return user_token

    @classmethod
    @asynccontextmanager
    async def _lock_token_generation(cls, hash: str):
        lock = None
        try:
            while True:
                call_status, status, lock = await AuthenticationLockManagerRepository.lock_authentication(hash=hash)
                if status == LockAuthenticationStatus.SUCCESS:
                    yield lock
                    break
                await asyncio.sleep(1)
        except Exception as err:
            message = f"{cls.__class__}:validate_token_redis:Error - {err}"
            Gladsheim.error(error=err, message=message)
        finally:
            if lock:
                await AuthenticationLockManagerRepository.unlock_authentication(lock=lock)

    @classmethod
    async def delete_default_token(cls):
        await cls.cache.delete(cls._default_token_cache_key())

    @classmethod
    async def _request_new_token(cls) -> dict:
        body = {
            "chave": config("OUROINVEST_SYSTEM_USER"), "senha": config("OUROINVEST_SYSTEM_PWD")}
        response = await HTTPTransport.request_method(
            method=HTTPMethods.POST,
            url=config("OUROINVEST_DEFAULT_TOKEN_URL"),
            body=body
        )
        token_json = await response.json()
        token = token_json.get("tokenAcesso").get("token")
        return cls._get_auth(token)

    @classmethod
    async def _request_new_user_token(cls, client_code: int, auth: dict) -> dict:
        body = {"codigoCliente": client_code}
        response = await HTTPTransport.request_method(
            method=HTTPMethods.POST,
            url=config("OUROINVEST_USER_TOKEN_URL"),
            body=body,
            headers=auth
        )
        user_token_json = await response.json()
        user_token = user_token_json.get("tokenAcesso").get("token")
        return cls._get_auth(user_token)

    @staticmethod
    def _base_tokens_cache_folder():
        return config("OUROINVEST_BASE_TOKENS_CACHE_FOLDER")

    @classmethod
    def _default_token_cache_key(cls):
        return cls._base_tokens_cache_folder() + config("OUROINVEST_DEFAULT_TOKEN_CACHE_KEY")

    @classmethod
    def _user_token_cache_key_format(cls, client_code: int):
        url = cls._base_tokens_cache_folder() + config("OUROINVEST_USER_TOKEN_CACHE_KEY")
        url = url.format(client_code)
        return url

    @staticmethod
    def _get_auth(token) -> dict:
        return {"Authorization": f"Bearer {token}"}
    