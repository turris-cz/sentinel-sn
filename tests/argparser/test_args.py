import pytest

import argparse
import zmq

import sn

def test_empty_args(arg_parser, empty_args):
    with pytest.raises(SystemExit):
        arg_parser.parse_args(empty_args)

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
    r1, r2 = ctx.get_socket("res1", "res2")
    assert r1
    assert r2
