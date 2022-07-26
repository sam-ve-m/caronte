from aiohttp import ClientSession, ClientResponse

from caronte import OuroInvestErrorReturn
from caronte.src.infrastructures.env_config import config
from caronte.src.repositories.cache.repository import Cache


class OuroInvestApiTransport:
    cache = Cache
    session = None

    @classmethod
    async def execute_get_with_default_token(cls, url: str) -> ClientResponse:
        token = await cls._get_token()
        headers = cls._get_auth(token)
        response = await cls._request_method_get(url, headers)
        return response

    @classmethod
    async def execute_get_with_user_token(cls, url: str, user_id: int, body: dict = None) -> ClientResponse:
        if body:  # Note: In one endpoint of the supplier, it requires a JSON body in an HTTP GET.
            body.update(cls._get_control())
        token = await cls._get_user_token(user_id)
        headers = cls._get_auth(token)
        response = await cls._request_method_get(url, headers, body, user_id)
        return response

    @classmethod
    async def execute_post_with_default_token(cls, url: str, body: dict) -> ClientResponse:
        body.update(cls._get_control())
        token = await cls._get_token()
        headers = cls._get_auth(token)
        response = await cls._request_method_post(url, body, headers)
        return response

    @classmethod
    async def execute_post_with_user_token(cls, url: str, user_id: int, body: dict) -> ClientResponse:
        body.update(cls._get_control())
        token = await cls._get_user_token(user_id)
        headers = cls._get_auth(token)
        response = await cls._request_method_post(url, body, headers, user_id)
        return response

    @staticmethod
    def _get_control():
        controle = {"controle": {
            "dataHoraCliente": config("OUROINVEST_CONTROLE_DATAHORACLIENTE"),  # TODO: Estudar se será um datetime.now()
            "recurso": {
                "codigo": config("OUROINVEST_CONTROLE_RECURSO_CODIGO"),
                "sigla": config("OUROINVEST_CONTROLE_RECURSO_SIGLA")
            },
            "origem": {
                "nome": config("OUROINVEST_CONTROLE_ORIGEM_NOME"),
                "chave": config("OUROINVEST_CONTROLE_ORIGEM_CHAVE"),
                "endereco": config("OUROINVEST_CONTROLE_ORIGEM_ENDERECO")
            }
        }}
        return controle

    @staticmethod
    def _get_auth(token) -> dict:
        return {"Authorization": f"Bearer {token}"}

    @classmethod
    async def _get_token(cls) -> str:
        base_tokens_cache_folder = config("OUROINVEST_BASE_TOKENS_CACHE_FOLDER")
        default_token_cache_key = base_tokens_cache_folder + config("OUROINVEST_DEFAULT_TOKEN_CACHE_KEY")
        if not (token := await cls.cache.get(default_token_cache_key)):
            await cls.cache.delete_folder(base_tokens_cache_folder)
            token = await cls.__request_new_token()
            await cls.cache.set(default_token_cache_key, token, 12 * 60 * 60)
        return token

    @classmethod
    async def _get_user_token(cls, client_code: int) -> str:
        base_tokens_cache_folder = config("OUROINVEST_BASE_TOKENS_CACHE_FOLDER")
        user_token_cache_key = base_tokens_cache_folder + config("OUROINVEST_USER_TOKEN_CACHE_KEY").format(client_code)
        default_token = await cls._get_token()
        if not (user_token := await cls.cache.get(user_token_cache_key)):
            user_token = await cls.__request_new_user_token(client_code, default_token)
            await cls.cache.set(user_token_cache_key, user_token, 12 * 60 * 60)
        return user_token

    @classmethod
    async def __request_new_token(cls) -> str:
        body = {
            "chave": config("OUROINVEST_SYSTEM_USER"), "senha": config("OUROINVEST_SYSTEM_PWD"),
            **cls._get_control()
        }
        url = config("OUROINVEST_DEFAULT_TOKEN_URL")
        response = await cls._request_method_post(url, body=body)
        token_json = await response.json()
        token = token_json.get("tokenAcesso").get("token")
        return token

    @classmethod
    async def __request_new_user_token(cls, client_code: int, token: str) -> str:
        body = {"codigoCliente": client_code, **cls._get_control()}
        url = config("OUROINVEST_USER_TOKEN_URL")
        response = await cls._request_method_post(url, body=body, headers=cls._get_auth(token))
        user_token_json = await response.json()
        user_token = user_token_json.get("tokenAcesso").get("token")
        return user_token

    @classmethod
    async def _get_session(cls) -> ClientSession:
        if cls.session is None:
            cls.session = ClientSession()
        return cls.session

    @classmethod
    async def _request_method_get(cls, url: str, headers: dict,
                                  body: dict = None, user_id: int = None) -> ClientResponse:
        session = await cls._get_session()
        response = await session.get(url, headers=headers, json=body)
        if response.status == 403:
            token_cache_key = config("OUROINVEST_BASE_TOKENS_CACHE_FOLDER")+config("OUROINVEST_DEFAULT_TOKEN_CACHE_KEY")
            await cls.cache.delete(token_cache_key)
            token = await cls._get_user_token(user_id) if user_id is not None else await cls._get_token()
            return await cls._request_method_get(url, cls._get_auth(token), body)
        await cls._raise_for_status(response)
        return response

    @classmethod
    async def _request_method_post(cls, url: str, body: dict,
                                   headers: dict = None, user_id: int = None) -> ClientResponse:
        session = await cls._get_session()
        response = await session.post(url, headers=headers, json=body)
        if response.status == 403:
            token_cache_key = config("OUROINVEST_BASE_TOKENS_CACHE_FOLDER")+config("OUROINVEST_DEFAULT_TOKEN_CACHE_KEY")
            await cls.cache.delete(token_cache_key)
            token = await cls._get_user_token(user_id) if user_id is not None else await cls._get_token()
            return await cls._request_method_post(url, body, cls._get_auth(token))
        await cls._raise_for_status(response)
        return response

    @staticmethod
    async def _raise_for_status(response):
        if not response.ok:
            message = await response.content.read()
            raise OuroInvestErrorReturn(f"Status: {response.status};\n"
                                        f"Reason: {response.reason};\n"
                                        f"Content: {message.decode()}.")

