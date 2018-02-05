class SentinelError(Exception):
    pass


class InvalidMsgError(SentinelError):
    pass


class SockConfigError(SentinelError):
    pass
