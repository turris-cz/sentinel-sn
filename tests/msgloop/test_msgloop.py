import pytest

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
