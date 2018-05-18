import pytest

import argparse
import zmq

import sn

def test_empty_args(arg_parser):
    with pytest.raises(SystemExit):
        arg_parser.parse_args([])


def test_empty_args_native(zmq_context):
    with pytest.raises(SystemExit):
        ctx = sn.SN(zmq_context)


@pytest.mark.parametrize("bad_arg", [
    "--resource",
    "--resource BAD",
    "--resource res,connect,PUSH,,",
    "--resource res,connect,PUSH,sentinel.cz,",
    "--resource res,connect,PULL,,7700",
    "--resource ,connect,PUSH,sentinel.cz,7700",
    "--resource connect,PUSH,sentinel.cz,7700",
    "--resource res,connect,PUSh,sentinel.cz,7700",
    "--resource res,connect,FOO,sentinel.cz,7700",
    "--resource res,connect,FOO,sentinel.cz,7700",
    "--resource res,connect,PUSH,sentinel.cz,0",
    "--resource res,connect,PUSH,*,8800",
    "--resource res,conn,PUSH,127.0.0.1,8800",
    "--resource res,connect,PUSH,localhost,8800"
        " --resource res,connect,PUSH,localhost,8800",
    "--resource res,bind,PULL,localhost,8800"
        " --resource res,bind,PULL,localhost,8800",

])
def test_bad_args(zmq_context, arg_parser, bad_arg):
    with pytest.raises((SystemExit, sn.SockConfigError, zmq.error.ZMQError)):
        ctx = sn.SN(zmq_context, arg_parser, args=bad_arg.split(" "))
        assert ctx.get_socket("res")


@pytest.mark.parametrize("conn_arg", [
    "--resource res,connect,PUSH,127.0.0.1,8800",
    "--resource res,connect,PUSH,setinel.turris.cz,8800",
])
def test_connect_args(zmq_context, arg_parser, conn_arg):
    ctx = sn.SN(zmq_context, arg_parser, args=conn_arg.split(" "))
    assert ctx.get_socket("res")


@pytest.mark.parametrize("bind_arg", [
    "--resource res,bind,PUSH,*,8800",
    "--resource res,bind,PULL,*,8801",
    "--resource res,bind,PULL,127.0.0.1,8802",
])
def test_bind_args(zmq_context, arg_parser, bind_arg):
    ctx = sn.SN(zmq_context, arg_parser, args=bind_arg.split(" "))
    assert ctx.get_socket("res")


@pytest.mark.parametrize("multisock_arg", [
    "--resource res1,connect,PUSH,localhost,8800"
        " --resource res2,connect,PUSH,localhost,8800",
    "--resource res1,connect,PUSH,localhost,8800"
        " --resource res1,connect,PUSH,localhost,8801"
        " --resource res2,connect,PUB,localhost,8802",
    "--resource res1,connect,PUB,localhost,8800"
        " --resource res1,connect,PUB,localhost,8801"
        " --resource res2,connect,PUB,localhost,8802",
])
def test_multisock_args(zmq_context, arg_parser, multisock_arg):
    ctx = sn.SN(zmq_context, arg_parser, args=multisock_arg.split(" "))
    assert ctx
    r1, r2 = ctx.get_socket("res1", "res2")
    assert r1
    assert r2


def test_required_type_accept(zmq_context, arg_parser, required_type_arg):
    ctx = sn.SN(zmq_context, arg_parser, args=required_type_arg)
    assert ctx
    assert ctx.get_socket(("res", "PUSH"))


def test_required_type_decline(zmq_context, arg_parser, required_type_arg):
    with pytest.raises(sn.SockConfigError):
        ctx = sn.SN(zmq_context, arg_parser, args=required_type_arg)
        assert ctx
        assert ctx.get_socket(("res", "PUB"))
