# Caronte
from caronte.src.domain.exceptions.base_exceptions.exception import ServiceException


class TokenNotFoundInContent(ServiceException):
    msg = "Token not found in result content from exchange API"
    pass
