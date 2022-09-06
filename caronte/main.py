# Caronte
from caronte.src.domain.enums.http_methods import AllowedHTTPMethods
from caronte.src.domain.enums.response import CaronteStatus
from caronte.src.domain.exceptions.base_exceptions.exception import ServiceException
from caronte.src.domain.exceptions.service.exception import TokenNotFoundInContent
from caronte.src.domain.models.authentication.response.model import CaronteStatusResponse
from caronte.src.service.token import TokenService
from caronte.src.transports.ouroinvest.transport import HTTPTransport

# Third party
from etria_logger import Gladsheim


class ExchangeCompanyApi:
    @classmethod
    async def request_as_company(
        cls,
        method: AllowedHTTPMethods,
        url: str,
        body: dict = None
    ) -> CaronteStatusResponse:
        try:
            headers = await TokenService.get_company_token()
            response = await HTTPTransport.request_method(
                method=method,
                url=url,
                body=body,
                headers=headers
            )
            return response
        except ServiceException as ex:
            Gladsheim.info(message=ex.msg)
            return CaronteStatusResponse((False, ex.code, None))
        except Exception as ex:
            Gladsheim.error(error=ex)
            return CaronteStatusResponse((False, CaronteStatus.UNEXPECTED_ERROR, None))

    @classmethod
    async def request_as_client(
        cls,
        method: AllowedHTTPMethods,
        url: str,
        exchange_account_id: int,
        body: dict = None,
    ) -> CaronteStatusResponse:
        try:
            headers = await TokenService.get_user_token(
                exchange_account_id=exchange_account_id
            )
            response = await HTTPTransport.request_method(
                method=method, url=url, body=body, headers=headers
            )
            return response
        except ServiceException as ex:
            Gladsheim.info(message=ex.msg)
            return CaronteStatusResponse((False, ex.code, None))
        except Exception as ex:
            Gladsheim.error(error=ex)
            return CaronteStatusResponse((False, CaronteStatus.UNEXPECTED_ERROR, None))
