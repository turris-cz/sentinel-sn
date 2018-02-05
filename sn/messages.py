import msgpack

from .exceptions import *

def parse_msg(data):
    """ Gets a Sentinel-type ZMQ message and parses message type and its
    payload.
    """
    try:
        msg_type = str(data[0], encoding="UTF-8")
        payload = msgpack.unpackb(data[1], encoding="UTF-8")

    except IndexError:
        raise InvalidMsgError("Not enough parts in message")

    return msg_type, payload


def encode_msg(msg_type, data):
    """ Gets string message type and its's string data. Then, both of them are
    packed to be prepared for zmg.send_multipart().
    """
    b = bytes(msg_type, encoding="UTF-8")
    msg = msgpack.packb(data)

    return (b, msg)
