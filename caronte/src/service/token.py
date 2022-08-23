
from caronte.src.domain.enum import HTTPMethods
from caronte.src.infrastructures.env_config import config
from caronte.src.transports.ouroinvest.transport import HTTPTransport
from caronte.src.repositories.cache.repository import Cache


class TokenService:
    cache = Cache

    @classmethod
    async def get_default_token(cls) -> dict:
        if not (token := await cls.cache.get(cls._default_token_cache_key())):
            await cls.cache.delete_folder(cls._base_tokens_cache_folder())
            token = await cls._request_new_token()
            await cls.cache.set(cls._default_token_cache_key(), token, 12 * 60 * 60)
        return token

    @classmethod
    async def get_user_token(cls, client_code: int) -> dict:
        user_token_cache_key = cls._user_token_cache_key_format().format(client_code)
        default_token = await cls.get_default_token()
        if not (user_token := await cls.cache.get(user_token_cache_key)):
            user_token = await cls._request_new_user_token(client_code, default_token)
            await cls.cache.set(user_token_cache_key, user_token, 12 * 60 * 60)
        return user_token

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
    def _user_token_cache_key_format(cls):
        return cls._base_tokens_cache_folder() + config("OUROINVEST_USER_TOKEN_CACHE_KEY")

    @staticmethod
    def _get_auth(token) -> dict:
        return {"Authorization": f"Bearer {token}"}