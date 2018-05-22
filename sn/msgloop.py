import logging
import inspect
import signal

from collections import namedtuple

import zmq

from .network import SN
from .network import get_arg_parser
from .messages import encode_msg, parse_msg
from .exceptions import *


logger = logging.getLogger("sn_main")

EnvData = namedtuple("EnvData", [
                                 "name",
                                 "logger",
                                ])


class SignalReceived(Exception):
    pass


def signal_handler(signum, frame):
    raise SignalReceived()


def sn_main(box_name, process, setup=None, teardown=None, argparser=None, args=None):
    ctx = SN(zmq.Context.instance(), argparser or get_arg_parser(), args=args)
    socket_recv, socket_send = detect_and_get_sockets(ctx)

    if not socket_recv and not socket_send:
        raise LoopError("Neither input nor output socket provided")
    if not socket_recv and not inspect.isgeneratorfunction(process):
        raise LoopError("Generator is expected for output-only box")

    logger.info("SN main starting loop for %s box", box_name)

    env_data = init_env_data(box_name)

    for sig in [ signal.SIGHUP, signal.SIGTERM, signal.SIGQUIT, signal.SIGABRT ]:
        signal.signal(sig, signal_handler)

    try:
        user_data = setup() if setup else None
        _sn_main_loop(env_data, user_data, socket_recv, socket_send, setup, process, teardown)

    except SignalReceived as e:
        logger.info("Box %s stopped by signal", box_name)

    except LoopError as e:
        raise e

    except AssertionError as e:
        # For pytest
        raise e

    except Exception as e:
        logger.error("Uncaught exception from loop")
        logger.exception(e)

    finally:
        if teardown:
            teardown(user_data)
        ctx.context.destroy()


def init_env_data(box_name):
    return EnvData(
                   name = box_name,
                   logger = logging.getLogger(box_name)
                   )


def _sn_main_loop(env_data, user_data, socket_recv, socket_send, setup=None, process=None, teardown=None):
    if socket_recv:
        try:
            while True:
                msg_in = socket_recv.recv_multipart()
                msg_type, payload = parse_msg(msg_in)

                result = process(env_data, user_data, msg_type, payload)
                process_result(socket_send, result)

        except InvalidMsgError as e:
            logger.error("Received broken message")

    else:
        for result in process(env_data, user_data):
            process_result(socket_send, result)


def process_result(socket_send, result):
    if not result:
        # The box is output-only or it hasn't any reasonable answer
        return

    if not socket_send:
        raise LoopError("Box generated output but there is any output socket. Bad configuration?")

    try:
        msg_type, payload = result
        msg_out = encode_msg(msg_type, payload)
        socket_send.send_multipart(msg_out)

    except (ValueError, InvalidMsgError) as e:
        # Invalid message on input means that a received some bad message and I
        # just want to not fail. Invalid message on output means a
        # programmer error of the box author and I need to distinguish between
        # them.
        raise LoopError("Box generates broken messages")


def detect_and_get_sockets(context):
    socket_recv = None
    socket_send = None

    try:
        socket_recv = context.get_socket("in")
    except UndefinedSocketError as e:
        pass

    try:
        socket_send = context.get_socket("out")
    except UndefinedSocketError as e:
        pass

    return socket_recv, socket_send
