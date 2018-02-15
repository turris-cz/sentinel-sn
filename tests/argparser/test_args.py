import pytest

import argparse
import zmq

import sn

def test_empty_args(arg_parser, empty_args):
    with pytest.raises(SystemExit):
        arg_parser.parse_args(empty_args)

def test_empty_args_native(zmq_context):
    with pytest.raises(SystemExit):
        ctx = sn.SN(zmq_context)

def test_bad_args(zmq_context, arg_parser, bad_args):
    with pytest.raises((SystemExit, sn.SockConfigError, zmq.error.ZMQError)):
        ctx = sn.SN(zmq_context, arg_parser, args=bad_args)
        assert ctx.get_socket("res")

def test_connect_args(zmq_context, arg_parser, conn_args):
    ctx = sn.SN(zmq_context, arg_parser, args=conn_args)
    assert ctx.get_socket("res")

def test_bind_args(zmq_context, arg_parser, bind_args):
    ctx = sn.SN(zmq_context, arg_parser, args=bind_args)
    assert ctx.get_socket("res")

def test_multisock_args(zmq_context, arg_parser, multisock_args):
    ctx = sn.SN(zmq_context, arg_parser, args=multisock_args)
    assert ctx
    r1, r2 = ctx.get_socket("res1", "res2")
    assert r1
    assert r2

def test_required_accept(zmq_context, arg_parser, required_args):
    ctx = sn.SN(zmq_context, arg_parser, args=required_args)
    assert ctx
    assert ctx.get_socket(("res", "PUSH"))

def test_required_decline(zmq_context, arg_parser, required_args):
    with pytest.raises(sn.SockConfigError):
        ctx = sn.SN(zmq_context, arg_parser, args=required_args)
        assert ctx
        assert ctx.get_socket(("res", "PUB"))
