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


class LoopFail(Exception):
    pass


def sn_main(box_name, process, setup=None, teardown=None, argparser=None, args=None):
    sn_ctx = SN(zmq.Context.instance(), argparser or get_arg_parser(), args=args)

    context = None
    try:
        user_data = get_user_data(setup)

        context = build_context(box_name, sn_ctx,  user_data)
        check_configuration(context, process)

        logger.info("SN main starting loop for %s box", box_name)
        register_signals(context)
        _sn_main_loop(context, process)

    except LoopHardFail as e:
        logger.error("Hard Fail of box: %s", context.name)
        logger.exception(e)
        # Finally will be called, because sys.exit() raises exception that will be uncaught.
        sys.exit(1)

    except KeyboardInterrupt:
        pass

    finally:
        if context:
            # Is possible that context wasn't built yet (e.g. error in setup callback)
            if teardown:
                teardown(context)
            teardown_context(context)


def get_user_data(setup):
    if setup:
        user_data = setup()
        if isinstance(user_data, dict):
            return user_data
        else:
            raise SetupError("Setup function didn't return a dictionary")

    return {}


def build_context(box_name, sn_ctx, user_data):
    socket_recv = get_socket(sn_ctx, "in")
    socket_send = get_socket(sn_ctx, "out")

    ctx = {
        "name": box_name,
        "logger": logging.getLogger(box_name),
        "loop_continue": True,
        "errors_in_row": 0,
        "sn_ctx": sn_ctx,
        "zmq_ctx": sn_ctx.context,
        "args": sn_ctx.args,
        "socket_recv": socket_recv,
        "socket_send": socket_send,
    }

    for k, v in user_data.items():
        if k in ctx:
            raise SetupError("Used reserved word in user_data: %s", k)
        else:
            ctx[k] = v

    return SimpleNamespace(**ctx)


def get_socket(context, sock_name):
    socket = None
    try:
        socket = context.get_socket(sock_name)

    except UndefinedSocketError as e:
        pass

    return socket


def check_configuration(context, process):
    if not context.socket_recv and not context.socket_send:
        raise SetupError("Neither input nor output socket provided")
    if not context.socket_recv and not inspect.isgeneratorfunction(process):
        raise SetupError("Generator is expected for output-only box")


def teardown_context(context):
    if context.socket_recv:
        context.socket_recv.close()
    if context.socket_send:
        context.socket_send.close()
    context.zmq_ctx.destroy()


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

        except StopIteration:
            context.logger.warning("Box %s raised StopIteration - unexpected behavior", context.name)
            break

        except SetupError as e:
            raise e

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
        raise SetupError("Box generated output but there is any output socket. Bad configuration?")

    try:
        msg_type, payload = result
        msg_out = encode_msg(msg_type, payload)
        socket_send.send_multipart(msg_out)

    except (ValueError, InvalidMsgError):
        raise LoopFail("Generated broken output message. Possibly bug in box.")


def register_signals(context):
    def signal_handler(signum, frame):
        context.logger.info("Signal %s received", signum)
        context.loop_continue = False

    for sig in [ signal.SIGHUP, signal.SIGTERM, signal.SIGQUIT, signal.SIGABRT ]:
        signal.signal(sig, signal_handler)
