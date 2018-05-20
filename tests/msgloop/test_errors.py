import pytest

from unittest.mock import patch

import sn

def test_empty_name():
    with pytest.raises(TypeError):
        sn.sn_main()


def test_at_least_one_socket(bad_socket_args):
    with pytest.raises(sn.LoopError) as e:
        sn.sn_main("test", args=bad_socket_args)
    assert str(e.value) == "Neither input nor output socket provided"


def test_no_process_function(in_out_args):
    with pytest.raises(sn.LoopError) as e:
        sn.sn_main("test",
                          setup=lambda: None,
                          teardown=lambda: None,
                          args=in_out_args)
    assert str(e.value) == "Missing 'process' callback"


def test_no_setup_without_teardown(in_out_args):
    with pytest.raises(sn.LoopError) as e:
        sn.sn_main("test",
                          teardown=lambda: None,
                          process=lambda: None,
                          args=in_out_args)
    assert str(e.value) == "There is teardown callback without setup"


def test_generator_needed(out_only_args):
    with pytest.raises(sn.LoopError) as e:
        sn.sn_main("test",
                          process=lambda: None,
                          args=out_only_args)
    assert str(e.value) == "Generator is expected for output-only box"


def test_unnecessary_output(in_only_args, good_msg):
    with pytest.raises(sn.LoopError) as e:
        with patch("zmq.Socket.recv_multipart", return_value=good_msg):
            sn.sn_main("test",
                              process=lambda e, u, t, p: ("foo", "bar"),
                              args=in_only_args)
    assert str(e.value) == "Box generated output but there is any output socket. Bad configuration?"


def test_generated_broken_message(in_out_args, good_msg):
    with pytest.raises(sn.LoopError) as e:
        with patch("zmq.Socket.recv_multipart", return_value=good_msg):
            sn.sn_main("test",
                              process=lambda e, u, t, p: ("foo", "bar"),
                              args=in_out_args)
    assert str(e.value) == "Box generates broken messages"
