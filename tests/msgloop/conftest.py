import pytest

import msgpack


def build_msg(msg_type, payload):
    t = bytes(msg_type, encoding="UTF-8")
    p = msgpack.packb(payload, encoding="UTF-8")

    return (t, p)


@pytest.fixture
def in_only_args():
    return "--resource in,bind,PULL,*,8801".split(" ")


@pytest.fixture
def out_only_args():
    return "--resource out,connect,PUSH,127.0.0.1,8802".split(" ")


@pytest.fixture
def in_out_args():
    return "--resource in,connect,PULL,127.0.0.1,8801 --resource out,connect,PUSH,127.0.0.1,8802".split(" ")


@pytest.fixture
def bad_socket_args():
    return "--resource bad_name,connect,PUSH,127.0.0.1,8802".split(" ")


@pytest.fixture
def good_msg():
    return build_msg("sentinel/test", { "foo": "bar" })
