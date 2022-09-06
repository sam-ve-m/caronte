# Standards
from enum import Enum


class CaronteStatus(Enum):
    SUCCESS = "success"
    FORBIDDEN = "unauthorized_token"
    TOKEN_NOT_FOUND = "token_not_found"
    UNEXPECTED_ERROR = "unexpected_error_has_occurred"

