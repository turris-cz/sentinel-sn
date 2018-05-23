class SentinelError(Exception):
    pass


class InvalidMsgError(SentinelError):
    pass


class InvalidMsgTypeError(InvalidMsgError):
    pass


class SockConfigError(SentinelError):
    pass


class UndefinedSocketError(SentinelError):
    pass


class SetupError(SentinelError):
    pass
