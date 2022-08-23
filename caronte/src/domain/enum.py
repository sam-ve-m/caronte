from enum import Enum


class HTTPMethods(Enum):
    CONNECT: str = "CONNECT"
    HEAD: str = "HEAD"
    GET: str = "GET"
    DELETE: str = "DELETE"
    OPTIONS: str = "OPTIONS"
    PATCH: str = "PATCH"
    POST: str = "POST"
    PUT: str = "PUT"
    TRACE: str = "TRACE"

