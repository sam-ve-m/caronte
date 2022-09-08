# Caronte
from caronte.src.domain.enums.response import CaronteStatus
from caronte.src.domain.exceptions.base_exceptions.exception import ServiceException


class TokenNotFoundInContent(ServiceException):
    def __init__(self, *args, **kwargs):
        self.msg = "Token not found in result content from exchange API"
        self.code = CaronteStatus.TOKEN_NOT_FOUND
        super().__init__(self.msg, self.code, args, kwargs)
