import pytest
from .conftest import build_msg

from unittest.mock import Mock
from unittest.mock import patch

import sn


def test_passed_userdata(in_out_args, good_msg):
    def setup():
        return { "foo": "bar" }

    def teardown(userdata):
        assert userdata["foo"] == "bar"

    def process(envdata, userdata, msg_type, payload):
        assert userdata["foo"] == "bar"
        raise Exception()

    with patch("zmq.Socket.recv_multipart", return_value=good_msg):
        sn.sn_main("test",
                          setup=setup,
                          teardown=teardown,
                          process=process,
                          args=in_out_args)


def test_passed_name(in_out_args, good_msg):
    def process(envdata, userdata, msg_type, payload):
        assert envdata.name == "test"
        raise Exception()

    with patch("zmq.Socket.recv_multipart", return_value=good_msg):
        sn.sn_main("test",
                          process=process,
                          args=in_out_args)


def test_passed_logger(in_out_args, good_msg):
    def process(envdata, userdata, msg_type, payload):
        assert type(envdata.logger.getEffectiveLevel()) == int
        raise Exception()

    with patch("zmq.Socket.recv_multipart", return_value=good_msg):
        sn.sn_main("test",
                          process=process,
                          args=in_out_args)


def test_generator(out_only_args, good_msg):
    def generate(envdata, userdata):
        for i in range(5):
            yield "sentinel/test", { "foo": "bar" }

    with patch("zmq.Socket.send_multipart", return_value=None) as send_function:
        sn.sn_main("test",
                          process=generate,
                          args=out_only_args)

        assert send_function.called
        assert send_function.call_count == 5
        args, _ = send_function.call_args
        assert args[0] == build_msg("sentinel/test", { "foo": "bar" })
