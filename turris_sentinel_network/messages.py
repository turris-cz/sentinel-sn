import re

import msgpack

from .exceptions import InvalidMsgError, InvalidMsgTypeError

SN_MSG_REGEXP = "^([a-z0-9_]+/)*[a-z0-9_]+$"
SN_MSG = re.compile(SN_MSG_REGEXP)


def parse_msg(data):
    """Gets a Sentinel-type ZMQ message and parses message type and its
    payload.
    """
    try:
        msg_type = str(data[0], encoding="UTF-8")
        if not SN_MSG.match(msg_type):
            raise InvalidMsgTypeError("Bad message type definition")
        payload = msgpack.unpackb(data[1], raw=False)

    except IndexError:
        raise InvalidMsgError("Not enough parts in message")

    except (ValueError, TypeError, msgpack.exceptions.UnpackException, UnicodeDecodeError):
        raise InvalidMsgError("Broken message")

    return msg_type, payload


def encode_msg(msg_type, data):
    """Gets string message type and its's string data. Then, both of them are
    packed to be prepared for zmg.send_multipart().
    """

    if not SN_MSG.match(msg_type or ""):
        raise InvalidMsgTypeError("Bad message type definition")

    if not data or type(data) != dict:
        raise InvalidMsgError("Empty payload parameter")

    b = bytes(msg_type, encoding="UTF-8")
    msg = msgpack.packb(data, use_bin_type=True)

    return (b, msg)
