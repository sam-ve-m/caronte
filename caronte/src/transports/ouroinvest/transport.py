from aiohttp import ClientSession, ClientResponse
from http import HTTPStatus

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

    _data_hora_cliente = config("OUROINVEST_CONTROLE_DATAHORACLIENTE")
    _codigo = config("OUROINVEST_CONTROLE_RECURSO_CODIGO")
    _sigla = config("OUROINVEST_CONTROLE_RECURSO_SIGLA")
    _nome = config("OUROINVEST_CONTROLE_ORIGEM_NOME")
    _chave = config("OUROINVEST_CONTROLE_ORIGEM_CHAVE")
    _endereco = config("OUROINVEST_CONTROLE_ORIGEM_ENDERECO")

    @classmethod
    def _get_control(cls):
        controle = {"controle": {
            "dataHoraCliente": cls._data_hora_cliente,  # TODO: Estudar se será um datetime.now()
            "recurso": {
                "codigo": cls._codigo,
                "sigla": cls._sigla
            },
            "origem": {
                "nome": cls._nome,
                "chave": cls._chave,
                "endereco": cls._endereco
            }
        }}
        return controle

    @staticmethod
    def _get_auth(token) -> dict:
        return {"Authorization": f"Bearer {token}"}

    _base_tokens_cache_folder = config("OUROINVEST_BASE_TOKENS_CACHE_FOLDER")
    _default_token_cache_key = _base_tokens_cache_folder + config("OUROINVEST_DEFAULT_TOKEN_CACHE_KEY")
    _user_token_cache_key_format = _base_tokens_cache_folder + config("OUROINVEST_USER_TOKEN_CACHE_KEY")

    @classmethod
    async def _get_token(cls) -> str:
        if not (token := await cls.cache.get(cls._default_token_cache_key)):
            await cls.cache.delete_folder(cls._base_tokens_cache_folder)
            token = await cls.__request_new_token()
            await cls.cache.set(cls._default_token_cache_key, token, 12 * 60 * 60)
        return token

    @classmethod
    async def _get_user_token(cls, client_code: int) -> str:
        user_token_cache_key = cls._user_token_cache_key_format.format(client_code)
        default_token = await cls._get_token()
        if not (user_token := await cls.cache.get(user_token_cache_key)):
            user_token = await cls.__request_new_user_token(client_code, default_token)
            await cls.cache.set(user_token_cache_key, user_token, 12 * 60 * 60)
        return user_token

    __ouroinvest_system_user = config("OUROINVEST_SYSTEM_USER")
    __ouroinvest_system_pwd = config("OUROINVEST_SYSTEM_PWD")
    _ouroinvest_default_token_url = config("OUROINVEST_DEFAULT_TOKEN_URL")
    _ouroinvest_user_token_url = config("OUROINVEST_USER_TOKEN_URL")

    @classmethod
    async def __request_new_token(cls) -> str:
        body = {
            "chave": cls.__ouroinvest_system_user, "senha": cls.__ouroinvest_system_pwd,
            **cls._get_control()
        }
        response = await cls._request_method_post(cls._ouroinvest_default_token_url, body=body)
        token_json = await response.json()
        token = token_json.get("tokenAcesso").get("token")
        return token

    @classmethod
    async def __request_new_user_token(cls, client_code: int, token: str) -> str:
        body = {"codigoCliente": client_code, **cls._get_control()}
        response = await cls._request_method_post(cls._ouroinvest_user_token_url,
                                                  body=body, headers=cls._get_auth(token))
        user_token_json = await response.json()
        user_token = user_token_json.get("tokenAcesso").get("token")
        return user_token

    @classmethod
    async def _get_session(cls) -> ClientSession:
        if cls.session is None:
            cls.session = ClientSession()
        return cls.session

    MAX_RETRY = config("CARONTE_MAX_RETRY")

    @classmethod
    async def _request_method_get(cls, url: str, headers: dict, body: dict = None,
                                  user_id: int = None, retry: int = 0) -> ClientResponse:
        session = await cls._get_session()
        response = await session.get(url, headers=headers, json=body)
        if response.status == HTTPStatus.FORBIDDEN and retry < int(cls.MAX_RETRY):
            await cls.cache.delete(cls._default_token_cache_key)
            token = await cls._get_user_token(user_id) if user_id is not None else await cls._get_token()
            return await cls._request_method_get(url, cls._get_auth(token), body, user_id, retry + 1)
        await cls._raise_for_status(response)
        return response

    @classmethod
    async def _request_method_post(cls, url: str, body: dict, headers: dict = None,
                                   user_id: int = None, retry: int = 0) -> ClientResponse:
        session = await cls._get_session()
        response = await session.post(url, headers=headers, json=body)
        if response.status == HTTPStatus.FORBIDDEN and retry < int(cls.MAX_RETRY):
            await cls.cache.delete(cls._default_token_cache_key)
            token = await cls._get_user_token(user_id) if user_id is not None else await cls._get_token()
            return await cls._request_method_post(url, body, cls._get_auth(token), user_id, retry + 1)
        await cls._raise_for_status(response)
        return response

    @staticmethod
    async def _raise_for_status(response: ClientResponse):
        if not response.ok:
            message = await response.content.read()
            raise OuroInvestErrorReturn(f"Status: {response.status};\n"
                                        f"Reason: {response.reason};\n"
                                        f"Content: {message.decode()}.")
