import pytest

import zmq

import sn

# This test proof that SN class is really able to generate working sockets.
# More input brutal test is in module argparser.

@pytest.fixture
def socket_binded():
    ctx = zmq.Context.instance()
    s = ctx.socket(zmq.PULL)
    s.bind("tcp://127.0.0.1:8800")
    s.ipv6 = True
    yield s
    s.close()
    ctx.destroy()

@pytest.fixture
def socket_connected():
    ctx = zmq.Context.instance()
    s = ctx.socket(zmq.PUSH)
    s.connect("tcp://127.0.0.1:8800")
    s.ipv6 = True
    yield s
    s.close()
    ctx.destroy()
