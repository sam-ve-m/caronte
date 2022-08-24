from enum import Enum


class HTTPMethods(Enum):
    CONNECT = "CONNECT"
    HEAD = "HEAD"
    GET = "GET"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"
    TRACE = "TRACE"

