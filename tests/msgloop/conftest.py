from unittest.mock import patch

import msgpack
import pytest


def gen_args(*extra_args):
    args = ["prog", "--name", "test"]
    args.extend(extra_args)
    return args


def build_msg(msg_type, payload):
    t = bytes(msg_type, encoding="UTF-8")
    p = msgpack.packb(payload, use_bin_type=True)

    return (t, p)


@pytest.fixture
def in_only_args():
    return gen_args("--resource", "in,bind,PULL,*,8801")


@pytest.fixture
def out_only_args():
    return gen_args("--resource", "out,connect,PUSH,127.0.0.1,8802")


@pytest.fixture
def in_out_args():
    return gen_args(
        "--resource",
        "in,connect,PULL,127.0.0.1,8801",
        "--resource",
        "out,connect,PUSH,127.0.0.1,8802",
    )


@pytest.fixture
def bad_socket_args():
    return gen_args("--resource", "bad_name,connect,PUSH,127.0.0.1,8802")


@pytest.fixture
def in_only_args_mock(in_only_args):
    with patch("sys.argv", in_only_args) as m:
        yield m


@pytest.fixture
def out_only_args_mock(out_only_args):
    with patch("sys.argv", out_only_args) as m:
        yield m


@pytest.fixture
def in_out_args_mock(in_out_args):
    with patch("sys.argv", in_out_args) as m:
        yield m


@pytest.fixture
def bad_socket_args_mock(bad_socket_args):
    with patch("sys.argv", bad_socket_args) as m:
        yield m


@pytest.fixture
def good_msg():
    return build_msg("sentinel/test", {"foo": "bar"})


@pytest.fixture
def recv_multipart_mock(good_msg):
    with patch("zmq.Socket.recv_multipart", return_value=good_msg) as m:
        yield m


@pytest.fixture
def send_multipart_mock():
    with patch("zmq.Socket.send_multipart") as m:
        yield m
