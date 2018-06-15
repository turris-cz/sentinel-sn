import pytest

import argparse
import zmq

import sn

def test_empty_args(zmq_context, empty_args_mock):
    with pytest.raises(SystemExit):
        ctx = sn.SN(zmq_context)


def test_undefined_resource(zmq_context, one_resource_mock):
    with pytest.raises(sn.UndefinedSocketError):
        ctx = sn.SN(zmq_context)
        assert ctx.get_socket("in")

def test_bad_args(zmq_context, bad_resources_mock):
    with pytest.raises((SystemExit, sn.SockConfigError, zmq.error.ZMQError)):
        ctx = sn.SN(zmq_context)
        assert ctx.get_socket("res")


def test_connect_args(zmq_context, connect_resources_mock):
    ctx = sn.SN(zmq_context)
    assert ctx.get_socket("res")


def test_bind_args(zmq_context, bind_resources_mock):
    ctx = sn.SN(zmq_context)
    assert ctx.get_socket("res")


def test_multisock_args(zmq_context, multisock_resources_mock):
    ctx = sn.SN(zmq_context)
    assert ctx
    r1, r2 = ctx.get_socket("res1", "res2")
    assert r1
    assert r2


def test_required_type_accept(zmq_context, one_resource_mock):
    ctx = sn.SN(zmq_context)
    assert ctx
    assert ctx.get_socket(("res", "PUSH"))


def test_required_type_decline(zmq_context, one_resource_mock):
    with pytest.raises(sn.SockConfigError):
        ctx = sn.SN(zmq_context)
        assert ctx
        assert ctx.get_socket(("res", "PUB"))


def test_verbose(zmq_context, verbose_args_mock):
    ctx = sn.SN(zmq_context)

    import logging

    logger = logging.getLogger("tests")
    assert logger.getEffectiveLevel() == logging.DEBUG
