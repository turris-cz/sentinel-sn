from unittest.mock import patch

import sn


def test_send(zmq_context, socket_binded):
    with patch("sys.argv", ["prog", "--resource", "res,connect,PUSH,127.0.0.1,8800"]):
        msg = b"ping"
        ctx = sn.SN(zmq_context)
        s = ctx.get_socket("res")
        assert s
        s.send(msg)
        m = socket_binded.recv()
        assert m == msg
        s.close()
        ctx.context.destroy()


def test_recv(zmq_context, socket_connected):
    with patch("sys.argv", ["prog", "--resource", "res,bind,PULL,127.0.0.1,8800"]):
        msg = b"ping"
        ctx = sn.SN(zmq_context)
        s = ctx.get_socket("res")
        assert s
        socket_connected.send(msg)
        m = s.recv()
        assert m == msg
        s.close()
        ctx.context.destroy()
