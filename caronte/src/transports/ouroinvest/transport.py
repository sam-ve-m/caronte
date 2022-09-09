# Caronte
from caronte.src.domain.models.authentication.response.model import (
    CaronteStatusResponse,
)
from caronte.src.domain.enums.http_methods import AllowedHTTPMethods
from caronte.src.domain.enums.response import CaronteStatus
from caronte.src.infrastructures.env_config import config

# Standards
from http import HTTPStatus

# Third party
from aiohttp import ClientSession, ClientResponse
from etria_logger import Gladsheim


class HTTPTransport:
    __session = None

    @classmethod
    async def request_method(
        cls, method: AllowedHTTPMethods, url: str, body: dict, headers: dict = None
    ) -> CaronteStatusResponse:
        if body:
            body.update(cls.__get_control())
        session = await cls.__get_session()
        response = await session.request(method.value, url, headers=headers, json=body)
        result = await cls.__map_response(response=response)
        return result

    @staticmethod
    def __get_control():
        control = {
            "controle": {
                "dataHoraCliente": config(
                    "OUROINVEST_CONTROLE_DATAHORACLIENTE"
                ),  # TODO: Estudar se será um datetime.now()
                "recurso": {
                    "codigo": config("OUROINVEST_CONTROLE_RECURSO_CODIGO"),
                    "sigla": config("OUROINVEST_CONTROLE_RECURSO_SIGLA"),
                },
                "origem": {
                    "nome": config("OUROINVEST_CONTROLE_ORIGEM_NOME"),
                    "chave": config("OUROINVEST_CONTROLE_ORIGEM_CHAVE"),
                    "endereco": config("OUROINVEST_CONTROLE_ORIGEM_ENDERECO"),
                },
            }
        }
        return control

    @classmethod
    async def __get_session(cls) -> ClientSession:
        if cls.__session is None:
            cls.__session = ClientSession()
        return cls.__session

    @classmethod
    async def __map_response(cls, response: ClientResponse) -> CaronteStatusResponse:
        possibilities_response_map = {
            HTTPStatus.OK: cls.__when_success_status,
            HTTPStatus.BAD_REQUEST: cls.__when_forbidden_status,
            CaronteStatus.UNEXPECTED_ERROR: cls.__when_unexpected_error,
        }
        response_function = possibilities_response_map.get(
            response.status, possibilities_response_map.get(CaronteStatus.UNEXPECTED_ERROR)
        )
        result = await response_function(response=response)
        return result

    @staticmethod
    async def __when_success_status(response: ClientResponse) -> CaronteStatusResponse:
        content = await response.json()
        return CaronteStatusResponse((True, CaronteStatus.SUCCESS, content))

    @staticmethod
    async def __when_forbidden_status(response: ClientResponse) -> CaronteStatusResponse:
        message = await response.content.read()
        Gladsheim.info(
            status=response.status, reason=response.reason, content=message.decode()
        )
        return CaronteStatusResponse((False, CaronteStatus.BAD_REQUEST, None))

    @staticmethod
    async def __when_unexpected_error(response: ClientResponse) -> CaronteStatusResponse:
        message = await response.content.read()
        Gladsheim.error(
            status=response.status, reason=response.reason, content=message.decode()
        )
        return CaronteStatusResponse((False, CaronteStatus.UNEXPECTED_ERROR, None))
