class SentinelError(Exception):
    pass


class InvalidMsgError(SentinelError):
    pass


class InvalidMsgTypeError(InvalidMsgError):
    pass


class SockConfigError(SentinelError):
    pass
