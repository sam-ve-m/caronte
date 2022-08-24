from aiohttp import ClientResponse
from caronte.src.domain.enum import HTTPMethods
from caronte.src.service.token import TokenService
from caronte.src.infrastructures.env_config import config
from caronte.src.transports.ouroinvest.transport import HTTPTransport
from caronte.src.domain.exceptions import OuroInvestUnauthorizedToken, OuroInvestErrorReturn


class OuroInvestApiTransport:

    @classmethod
    async def request(cls, method: HTTPMethods, url: str, user_id: int = None, body: dict = None) -> ClientResponse:
        counter, max_counter = 0, int(config("CARONTE_MAX_RETRY"))
        while counter < max_counter:
            try:
                auth = (
                    await TokenService.get_user_token(user_id)
                    if user_id else
                    await TokenService.get_default_token()
                )
                response = await HTTPTransport.request_method(method, url, body, auth)
                return response
            except OuroInvestUnauthorizedToken:
                await TokenService.delete_default_token()
                counter += 1
        raise OuroInvestUnauthorizedToken()


if __name__ == "__main__":
    import asyncio

    asyncio.run(
        OuroInvestApiTransport.request(
            method=HTTPMethods.POST,
            url="https://teste",
            user_id=123,
            body={}
        )
    )

__all__ = [OuroInvestErrorReturn, OuroInvestUnauthorizedToken, HTTPMethods, OuroInvestApiTransport]
