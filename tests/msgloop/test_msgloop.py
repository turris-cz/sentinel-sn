from .conftest import build_msg

import pytest
from unittest.mock import Mock

import sn


def test_passed_userdata(in_out_args_mock, recv_multipart_mock, send_multipart_mock, good_msg):
    def side_effect():
        yield good_msg
        yield good_msg
        raise StopIteration()

    recv_multipart_mock.side_effect = side_effect()

    mock_setup = Mock(return_value={ "foo": "bar" })
    mock_process = Mock(return_value=("sentinel/test", { "foo": "bar" }))
    mock_teardown = Mock()

    sn.sn_main("box_name", mock_process, setup=mock_setup, teardown=mock_teardown)

    assert mock_setup.called
    assert mock_setup.call_count == 1

    assert mock_teardown.called
    assert mock_teardown.call_count == 1
    assert mock_teardown.call_args[0][0].name == "box_name"
    assert mock_teardown.call_args[0][0].foo == "bar"

    assert mock_process.called
    assert mock_process.call_args[0][0].name == "box_name"
    assert mock_process.call_args[0][0].foo == "bar"


@pytest.mark.skip
def test_passed_name(in_out_args, good_msg):
    def process(envdata, userdata, msg_type, payload):
        assert envdata.name == "test"
        raise Exception()

    with patch("zmq.Socket.recv_multipart", return_value=good_msg):
        sn.sn_main("test",
                          process=process,
                          args=in_out_args)


@pytest.mark.skip
def test_passed_logger(in_out_args, good_msg):
    def process(envdata, userdata, msg_type, payload):
        assert type(envdata.logger.getEffectiveLevel()) == int
        raise Exception()

    with patch("zmq.Socket.recv_multipart", return_value=good_msg):
        sn.sn_main("test",
                          process=process,
                          args=in_out_args)


@pytest.mark.skip
def test_generator(out_only_args, good_msg):
    def generate(envdata, userdata):
        for i in range(5):
            yield "sentinel/test", { "foo": "bar" }

    with patch("zmq.Socket.send_multipart", return_value=None) as send_function:
        sn.sn_main("test",
                          process=generate,
                          args=out_only_args)

        assert send_function.called
        assert send_function.call_count == 5
        args, _ = send_function.call_args
        assert args[0] == build_msg("sentinel/test", { "foo": "bar" })


@pytest.mark.skip
def test_generated_broken_message(in_out_args, good_msg):
    with pytest.raises(sn.LoopError) as e:
        with patch("zmq.Socket.recv_multipart", return_value=good_msg):
            sn.sn_main("test",
                              process=lambda e, u, t, p: ("foo", "bar"),
                              args=in_out_args)
    assert str(e.value) == "Box generates broken messages"
