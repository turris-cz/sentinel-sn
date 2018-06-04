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


class LoopHardFail(Exception):
    pass


class LoopFail(Exception):
    pass


class SNBox():
    def __init__(self, box_name, argparser=None):
        # Important provided values into box
        self.name = box_name
        self.logger = logging.getLogger(box_name)
        # Internal context values
        self.zmq_ctx = zmq.Context.instance()
        self.sn_ctx = SN(self.zmq_ctx, argparser or get_arg_parser())
        self.args = self.sn_ctx.args
        # User data
        self.context = None
        # Error management
        self.loop_continue = True
        self.errors_in_row =  0

    # Core methods - Will be implemented in non-abstract boxes
    def check_configuration(self):
        raise NotImplementedError("check_configuration")

    def get_processed_message(self):
        raise NotImplementedError("get_processed_message")

    def process_result(self, result):
        raise NotImplementedError("process_result")

    # Public API for boxes - will be optionally implemented in final boxes
    def setup(self):
        return {}

    def teardown(self):
        pass

    def before_first_request(self):
        pass

    def process(self, msg_type, payload):
        raise NotImplementedError("process")

    # Provided functionality - should be final implementation
    def run(self):
        self.check_configuration()
        try:
            self.context = self.get_user_data()

            self.logger.info("SN main starting loop for %s box", self.name)
            self.register_signals()

            self.before_first_request()
            self.run_loop()

        except LoopHardFail as e:
            self.logger.error("Hard Fail of box: %s", self.name)
            self.logger.exception(e)
            # Finally will be called, because sys.exit() raises exception that will be uncaught.
            sys.exit(1)

        except KeyboardInterrupt:
            pass

        finally:
            self.teardown_box()
            self.teardown()

    def get_user_data(self):
        user_data = self.setup()

        if isinstance(user_data, dict):
            return SimpleNamespace(**user_data)
        else:
            raise SetupError("Setup function didn't return a dictionary")

    def register_signals(self):
        def signal_handler(signum, frame):
            self.logger.info("Signal %s received", signum)
            self.loop_continue = False

        for sig in [ signal.SIGHUP, signal.SIGTERM, signal.SIGQUIT, signal.SIGABRT ]:
            signal.signal(sig, signal_handler)

    def teardown_box(self):
        self.zmq_ctx.destroy()

    def run_loop(self):
        while self.loop_continue:
            try:
                result = self.get_processed_message()
                self.process_result(result)
                self.errors_in_row = 0

            except StopIteration:
                self.logger.info("Box %s raised StopIteration", self.name)
                break

            except (SetupError, NotImplementedError) as e:
                raise e

            except Exception as e:
                self.logger.error("Uncaught exception from loop: %s", type(e).__name__)
                self.logger.exception(e)

                self.errors_in_row += 1
                if self.errors_in_row > 10:
                    raise LoopHardFail("Many errors in row.")

    # Helper methods
    def get_socket(self, sock_name):
        socket = None
        try:
            socket = self.sn_ctx.get_socket(sock_name)

        except UndefinedSocketError as e:
            pass

        return socket


class SNPipelineBox(SNBox):
    def __init__(self, box_name, argparser=None):
        super().__init__(box_name, argparser)
        self.socket_recv = self.get_socket("in")
        self.socket_send = self.get_socket("out")

    def check_configuration(self):
        if not self.socket_recv and not self.socket_send:
            raise SetupError("Neither input nor output socket provided")

    def get_processed_message(self):
        msg = self.socket_recv.recv_multipart()
        msg_type, payload = parse_msg(msg)

        return self.process(msg_type, payload)

    def process_result(self, result):
        if not result:
            # The box hasn't any reasonable answer
            return

        try:
            msg_type, payload = result
            msg_out = encode_msg(msg_type, payload)
            self.socket_send.send_multipart(msg_out)

        except (ValueError, InvalidMsgError):
            raise LoopFail("Generated broken output message. Possibly bug in box.")


class SNGeneratorBox(SNBox):
    def __init__(self, box_name, argparser=None):
        super().__init__(box_name, argparser)
        self.socket_send = self.get_socket("out")

        # Ensure about process() method before try to get iterator
        self.check_configuration()

        self.process_iterator = self.process()

    def check_configuration(self):
        if not self.socket_send:
            raise SetupError("Output socket wasn't provided")
        if not inspect.isgeneratorfunction(self.process):
            raise SetupError("Generator is expected for output-only box")

    def get_processed_message(self):
        return next(self.process_iterator)

    def process_result(self, result):
        if not result:
            # The box hasn't any reasonable answer
            return

        try:
            msg_type, payload = result
            msg_out = encode_msg(msg_type, payload)
            self.socket_send.send_multipart(msg_out)

        except (ValueError, InvalidMsgError):
            raise LoopFail("Generated broken output message. Possibly bug in box.")


class SNTerminationBox(SNBox):
    def __init__(self, box_name, argparser=None):
        super().__init__(box_name, argparser)
        self.socket_recv = self.get_socket("in")

    def check_configuration(self):
        if not self.socket_recv:
            raise SetupError("Input socket wasn't provided")

    def get_processed_message(self):
        msg = self.socket_recv.recv_multipart()
        msg_type, payload = parse_msg(msg)

        return self.process(msg_type, payload)

    def process_result(self, result):
        if result:
            raise LoopFail("Input-only box generated output message. Possibly bug in box.")
