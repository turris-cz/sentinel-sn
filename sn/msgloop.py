import logging
import inspect
import signal

from collections import namedtuple

import zmq

import sn


logger = logging.getLogger("sn_main")

EnvData = namedtuple("EnvData", [
                                 "name",
                                 "logger",
                                ])


class SignalReceived(Exception):
    pass


def signal_handler(signum, frame):
    raise SignalReceived()


def sn_main(box_name, setup=None, process=None, teardown=None, argparser=None):
    ctx = sn.SN(zmq.Context.instance(), argparser or sn.get_arg_parser())
    socket_recv, socket_send = detect_and_get_sockets(ctx)

    if not socket_recv and not socket_send:
        raise sn.LoopError("Neither input nor output socket provided")
    if teardown and not setup:
        raise sn.LoopError("There is teardown callback without setup")
    if not process:
        raise sn.LoopError("Missing 'process' callback")
    if not socket_recv and not inspect.isgeneratorfunction(process):
        raise sn.LoopError("Generator is expected for output-only box")

    logger.info("SN main starting loop for %s box", box_name)

    for sig in [ signal.SIGHUP, signal.SIGTERM, signal.SIGQUIT, signal.SIGABRT ]:
        signal.signal(sig, signal_handler)

    try:
        user_data = setup() if setup else None
        _sn_main_loop(box_name, user_data, socket_recv, socket_send, setup, process, teardown)

    except SignalReceived as e:
        logger.info("Box %s stopped by signal", box_name)

    except sn.LoopError as e:
        raise e

    except Exception as e:
        logger.error("Uncaught exception from loop")
        logger.exception(e)

    finally:
        if teardown:
            teardown(user_data)
        ctx.context.destroy()


def _sn_main_loop(box_name, user_data, socket_recv, socket_send, setup=None, process=None, teardown=None):
    env_data = EnvData(
                       name = box_name,
                       logger = logging.getLogger(box_name)
                       )

    while True:
        try:
            if socket_recv:
                msg_in = socket_recv.recv_multipart()
                msg_type, payload = sn.parse_msg(msg_in)

                result = process(env_data, user_data, msg_type, payload)
                process_result(socket_send, result)
            else:
                for result in process(env_data, user_data):
                    process_result(socket_send, result)

        except sn.InvalidMsgError as e:
            logger.error("Received broken message")


def process_result(socket_send, result):
    if not result:
        # The box is output-only or it hasn't any reasonable answer
        return

    if not socket_send:
        raise sn.LoopError("Box generated output but there is any output socket. Bad configuration?")

    try:
        msg_type, payload = result
        msg_out = sn.encode_msg(msg_type, payload)
        socket_send.send_multipart(msg_out)

    except (ValueError, sn.InvalidMsgError) as e:
        # Invalid message on input means that a received some bad message and I
        # just want to not fail. Invalid message on output means a
        # programmer error of the box author and I need to distinguish between
        # them.
        raise sn.LoopError("Box generates broken messages")


def detect_and_get_sockets(context):
    socket_recv = None
    socket_send = None

    try:
        socket_recv = context.get_socket("in")
    except sn.UndefinedSocketError as e:
        pass

    try:
        socket_send = context.get_socket("out")
    except sn.UndefinedSocketError as e:
        pass

    return socket_recv, socket_send
