class DomainException(Exception):
    def __init__(self, msg, code, *args, **kwargs):
        self.msg = msg
        self.code = code
        super().__init__(args, kwargs)


class RepositoryException(Exception):
    def __init__(self, msg, code, *args, **kwargs):
        self.msg = msg
        self.code = code
        super().__init__(args, kwargs)


class ServiceException(Exception):
    def __init__(self, msg, code, *args, **kwargs):
        self.msg = msg
        self.code = code
        super().__init__(args, kwargs)


class TransportException(Exception):
    def __init__(self, msg, code, *args, **kwargs):
        self.msg = msg
        self.code = code
        super().__init__(args, kwargs)
