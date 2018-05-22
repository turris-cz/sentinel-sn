import sys
import logging
import inspect
import signal

from types import SimpleNamespace

import zmq

from .network import SN
from .network import get_arg_parser
from .messages import encode_msg, parse_msg
from .exceptions import *


logger = logging.getLogger("sn_main")


class LoopHardFail(Exception):
    pass


def sn_main(box_name, process, setup=None, teardown=None, argparser=None, args=None):
    zmq_ctx = zmq.Context.instance()
    sn_ctx = SN(zmq_ctx, argparser or get_arg_parser(), args=args)
    socket_recv = get_socket(sn_ctx, "in")
    socket_send = get_socket(sn_ctx, "out")

    if not socket_recv and not socket_send:
        raise LoopError("Neither input nor output socket provided")
    if not socket_recv and not inspect.isgeneratorfunction(process):
        raise LoopError("Generator is expected for output-only box")

    logger.info("SN main starting loop for %s box", box_name)

    data_for_context = {
        "zmq_ctx": zmq_ctx,
        "sn_ctx": sn_ctx,
        "args": sn_ctx.args,
        "socket_recv": socket_recv,
        "socket_send": socket_send,
    }

    context = None

    try:
        user_data = get_user_data(setup)
        context = build_context(box_name, data_for_context, user_data)

        register_signals(context)

        _sn_main_loop(context, process)

    except LoopHardFail as e:
        logger.error("Hard Fail of box: %s", context.name)
        sys.exit(1)

    except KeyboardInterrupt:
        pass

    finally:
        if context:
            # Is possible that context wasn't built yet (e.g. error in setup callback)
            if teardown:
                teardown(context)
            teardown_context(context)


def get_socket(context, sock_name):
    socket = None
    try:
        socket = context.get_socket(sock_name)

    except UndefinedSocketError as e:
        pass

    return socket


def get_user_data(setup):
    if setup:
        user_data = setup()
        if isinstance(user_data, dict):
            return user_data
        else:
            raise LoopError("Setup function didn't return a dictionary")

    return {}


def build_context(box_name, context_data, user_data):
    ctx = {
        "name": box_name,
        "logger": logging.getLogger(box_name),
        "loop_continue": True,
        "errors_in_row": 0,
    }

    ctx.update(context_data)

    for k, v in user_data.items():
        if k in ctx:
            raise LoopError("Used reserved word in user_data: %s", k)
        else:
            ctx[k] = v

    return SimpleNamespace(**ctx)


def teardown_context(ctx):
    if ctx.socket_recv:
        ctx.socket_recv.close()
    if ctx.socket_send:
        ctx.socket_send.close()
    ctx.zmq_ctx.destroy()


def _sn_main_loop(context, process):
    if inspect.isgeneratorfunction(process):
        generate_output_message = process(context)
    else:
        generate_output_message = generate_processed_msg(context, process)

    while context.loop_continue:
        try:
            result = next(generate_output_message)
            process_result(context.socket_send, result)
            context.errors_in_row = 0

        except StopIteration as e:
            context.logger.warning("Box %s raised StopIteration - unexpected behavior", context.name)
            break

        except Exception as e:
            logger.error("Uncaught exception from loop")
            logger.exception(e)

            context.errors_in_row += 1
            if context.errors_in_row > 10:
                raise LoopHardFail("Many errors in row.")


def generate_processed_msg(context, process):
    while True:
        msg = context.socket_recv.recv_multipart()
        msg_type, payload = parse_msg(msg)

        result = process(context, msg_type, payload)

        yield result


def process_result(socket_send, result):
    if not result:
        # The box is output-only or it hasn't any reasonable answer
        return

    if not socket_send:
        # TODO: Hard fail?
        raise LoopError("Box generated output but there is any output socket. Bad configuration?")

    msg_type, payload = result
    msg_out = encode_msg(msg_type, payload)
    socket_send.send_multipart(msg_out)
    # TODO: Hard fail on InvalidMsgError in box output?


def register_signals(ctx):
    def signal_handler(signum, frame):
        ctx.logger.info("Signal %s received", signum)
        ctx.loop_continue = False

    for sig in [ signal.SIGHUP, signal.SIGTERM, signal.SIGQUIT, signal.SIGABRT ]:
        signal.signal(sig, signal_handler)
