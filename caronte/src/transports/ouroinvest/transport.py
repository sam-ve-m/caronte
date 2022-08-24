from aiohttp import ClientSession, ClientResponse
from http import HTTPStatus

from caronte.src.domain.enum import HTTPMethods
from caronte.src.infrastructures.env_config import config
from caronte.src.domain.exceptions import OuroInvestUnauthorizedToken, OuroInvestErrorReturn


class HTTPTransport:
    session = None

    @classmethod
    async def request_method(cls, method: HTTPMethods, url: str, body: dict, headers: dict = None) -> ClientResponse:
        if body:
            body.update(cls._get_control())
        session = await cls._get_session()
        response = await session.request(method.value, url, headers=headers, json=body)
        await cls._raise_for_status(response)
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

    @classmethod
    async def _get_session(cls) -> ClientSession:
        if cls.session is None:
            cls.session = ClientSession()
        return cls.session

    @staticmethod
    async def _raise_for_status(response: ClientResponse):
        if response.status == HTTPStatus.FORBIDDEN:
            raise OuroInvestUnauthorizedToken()
        if not response.ok:
            message = await response.content.read()
            raise OuroInvestErrorReturn(f"Status: {response.status};\n"
                                        f"Reason: {response.reason};\n"
                                        f"Content: {message.decode()}.")
