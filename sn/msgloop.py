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
    """SNBox is abstract box providing basic message loop functionality.

    This box provides interface for non-abstract and final-box classes.  It
    holds whole loop mechanism, protects process from unexpected errors and
    contains some basic magic with signals.

    It is missing some important parts that are necessary for full
    functionality like receiving and sending messages itself.

    :param box_name: Unique identification of the box in Sentinel network.
    :param argparser: Enriched argparser - see :func:`sn.get_arg_parser`
    """
    def __init__(self, box_name, argparser=None):
        """Initialize common Box resources.

        The most important resources:

        * ZMQ context
        * SN context
        * Logger
        * Parsed arguments
        """

        # Local contexts for dependencies
        self.zmq_ctx = zmq.Context.instance()
        self.sn_ctx = SN(self.zmq_ctx, argparser or get_arg_parser())
        # Important values provided to box
        self.name = box_name
        self.logger = logging.getLogger(box_name)
        self.args = self.sn_ctx.args
        # Error management of the loop
        self.loop_continue = True
        self.errors_in_row =  0
        # User data
        # Data generated by setup function are placed into separate variable
        # Final box shouldn't use "self" - we want to isolate its values
        self.ctx = None

    # Core methods - Will be implemented in non-abstract boxes
    def check_configuration(self):
        """Check configuration of the box.

        Check if box is able to start according to non-abstract box
        requirements.

        Method is called at least at the beginning of :meth:`run` method but
        You can call it additionally at every place you want to (e.g. last step
        of :meth:`__init__`).
        """
        raise NotImplementedError("check_configuration")

    def get_processed_message(self):
        """Return message that will be processed in loop.

        There is expected that the message is already processed and not only
        received. It provides variability in obtaining messages.
        """
        raise NotImplementedError("get_processed_message")

    def process_result(self, result):
        """Process generated message.

        It usually means send to the Sentinel network. This method provides
        variability in result format.
        """
        raise NotImplementedError("process_result")

    # Public API for boxes - will be optionally implemented in final boxes
    def setup(self):
        """Setup all user's data.

        This method is considered as a "constructor" for final-box. You can
        allocate resources here or initialize important variables.

        Final-box is not allowed to store its data as member variables (self.*).
        It is considered as security mechanism. Every final-box must return a
        dictionary. Variables will be available as ``self.ctx.dict_key`` in
        another callbacks trough ``types.SimpleNamespace()``.

        Setup is called at the beginning of :meth:`run` method, so there should be
        all the box resources available.

        Default implementation is pass.
        """

        return {}

    def teardown(self):
        """Destroy allocated resources.

        This is place to release allocated resources if needed. Namesace
        ``self.ctx`` is still available at this point.

        Default implementation is pass.
        """
        pass

    def before_first_request(self):
        """Generate message or do some other pre-run thing.

        At this point is box fully set up but there is no message received.
        With return value is treated in the same manner as :meth:`process` does.

        It is useful for some initialisation message.

        Default implementation is pass.
        """
        pass

    def process(self, msg_type, payload):
        """Process message callback.

        This method is called as a part of :meth:`process_result`.
        """
        raise NotImplementedError("process")

    # Provided functionality - should be final implementation
    def run(self):
        """Main method for all boxes.

        Every existing box should be used in 2 steps:

        * Initialization
        * Call :meth:`run`

        Nothing more or less. I recommend to run boxes as one-liner:
        ``FinalBox("box_name").run()``
        """

        # This is the only way to be sure that check will be called.
        # Constructors will be overwritten in non-abstract boxes
        self.check_configuration()

        try:
            self.ctx = self.get_user_data()

            self.logger.info("SNBox starting loop for %s box", self.name)
            self.register_signals()

            self.before_loop()
            self.run_loop()

        except LoopHardFail as e:
            self.logger.error("Hard Fail of box: %s", self.name)
            self.logger.exception(e)
            # Finally will be called, because sys.exit() raises exception that will be uncaught.
            sys.exit(1)

        except KeyboardInterrupt:
            pass

        finally:
            self.teardown()  # Clean-up data generated by setup()
            self.teardown_box()  # Clean-up my local contexts

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

        for sig in [ signal.SIGTERM, signal.SIGQUIT, signal.SIGABRT ]:
            signal.signal(sig, signal_handler)

    def before_loop(self):
        result = self.before_first_request()
        if result:
            self.process_result(result)

    def teardown_box(self):
        """Destroy box specific resources allocated in :meth:`__init__`.

        E.g. destroy ZMQ contex.
        """

        self.zmq_ctx.destroy()
        self.logger.info("SNBox shutting down box %s", self.name)

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
                # These error are considered as show-stopper.
                # It means programmer error ans there is no reason for trying to recover
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
    """SNPipelineBox is implementation of **in-out** box.

    It expects 2 specified resources called *in* and *out*. Then receives
    messages from *in* resource, process message and sends the result to *out*
    resource.
    """
    def __init__(self, box_name, argparser=None):
        """Initializes *in* and *out* resources."""
        super().__init__(box_name, argparser)
        self.socket_recv = self.get_socket("in")
        self.socket_send = self.get_socket("out")

    def check_configuration(self):
        """Check if *in* and *out* are provided by arguments."""
        if not self.socket_recv:
            raise SetupError("Input socket wasn't provided")
        if not self.socket_send:
            raise SetupError("Output socket wasn't provided")

    def teardown_box(self):
        """Explicitly closes *in* and *out* sockets and calls method of ancestor."""
        self.socket_recv.close()
        self.socket_send.close()
        super().teardown_box()

    def get_processed_message(self):
        """Receive message from *in* socket, parse it by :func:`parse_msg` and
        call :meth:`process` method.
        """
        msg = self.socket_recv.recv_multipart()
        msg_type, payload = parse_msg(msg)

        return self.process(msg_type, payload)

    def process_result(self, result):
        """Check if :meth:`process` provided any answer and sent it to *out*
        socket.
        """
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
    """SNGeneratorBox is implementation of **out-only** box.

    It expects only *out* resource.

    There is one big difference: :meth:`process` doesn't take ``msg_type`` and
    ``payload`` arguments and it must be a Python *generator*. (So it
    yields  it's results and doesn't return them.

    **Warning**: ``SNBox`` is not able to provide it's standard protection
    because Python generators automatically raises ``StopIteration`` after
    uncatched exceptions.
    """
    def __init__(self, box_name, argparser=None):
        """Initializes *out* resource."""
        super().__init__(box_name, argparser)
        self.socket_send = self.get_socket("out")

        # Ensure about process() method before try to get iterator
        self.check_configuration()

        self.process_iterator = self.process()

    def check_configuration(self):
        """Check *out* resource and check if :meth:`process` is a generator."""
        if not self.socket_send:
            raise SetupError("Output socket wasn't provided")
        if not inspect.isgeneratorfunction(self.process):
            raise SetupError("Generator is expected for output-only box")

    def teardown_box(self):
        """Explicitly closes *out* socket and calls method of ancestor."""
        self.socket_send.close()
        super().teardown_box()

    def get_processed_message(self):
        """Calls ``next()`` on :meth:`process` generator."""
        return next(self.process_iterator)

    def process_result(self, result):
        """Check if :meth:`process` provided any answer and sent it to *out*
        socket.
        """
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
    """SNTerminationBox is implementation of **in-only** box.

    It expects only *in* resource and raises :exc:`sn.SetupError` if
    :meth:`process` has any result.
    """
    def __init__(self, box_name, argparser=None):
        """Initializes *in* resource."""
        super().__init__(box_name, argparser)
        self.socket_recv = self.get_socket("in")

    def check_configuration(self):
        """Check *in* resource."""
        if not self.socket_recv:
            raise SetupError("Input socket wasn't provided")

    def teardown_box(self):
        """Explicitly closes *in* socket and calls method of ancestor."""
        self.socket_recv.close()
        super().teardown_box()

    def get_processed_message(self):
        """Receive message from *in* socket, parse it by :func:`parse_msg` and
        call :meth:`process` method.
        """
        msg = self.socket_recv.recv_multipart()
        msg_type, payload = parse_msg(msg)

        return self.process(msg_type, payload)

    def process_result(self, result):
        """Raises :exc:`sn.SetupError` because there is no resutl expected."""
        if result:
            raise SetupError("Input-only box generated output message. Possibly bug in box.")


class SNMultipleOutputPipelineBox(SNPipelineBox):
    """SNMultipleOutputPipelineBox is implementation of **in-out** box.

    Its based on :class:`SNPipelineBox`. The only difference that it expects
    not only one result but a ``list`` of results.
    """
    def process_result(self, result):
        """Checks if :meth:`process` returned result, iterates over result and
        call :meth:`process_result` of ancestor for each sub-result.
        """
        if result:
            for single_result in result:
                super().process_result(single_result)
