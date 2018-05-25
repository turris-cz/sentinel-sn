from .conftest import build_msg

import pytest
from unittest.mock import Mock

import sn


def test_regulraly_processed(in_out_args_mock, recv_multipart_mock, send_multipart_mock, good_msg):
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
    assert mock_teardown.call_count == 1  # Should be called right one
    assert mock_teardown.call_args[0][0].name == "box_name"  # Passed context data
    assert isinstance(mock_teardown.call_args[0][0].logger.getEffectiveLevel(), int)
    assert mock_teardown.call_args[0][0].foo == "bar"  # Passed user data

    assert mock_process.called
    assert mock_process.call_args[0][0].name == "box_name"  # Passed context data
    assert isinstance(mock_process.call_args[0][0].logger.getEffectiveLevel(), int)
    assert mock_process.call_args[0][0].foo == "bar"  # Passed user data


def test_processed_from_generator(out_only_args_mock, send_multipart_mock):
    msg_num = 5

    def process(userdata):
        for i in range(msg_num):
            yield "sentinel/test", { "foo": "bar" }

    mock_setup = Mock(return_value={ "foo": "bar" })
    mock_teardown = Mock()

    sn.sn_main("box_name", process, setup=mock_setup, teardown=mock_teardown)

    assert mock_setup.called
    assert mock_setup.call_count == 1

    assert mock_teardown.called
    assert mock_teardown.call_count == 1  # Should be called right one
    assert mock_teardown.call_args[0][0].name == "box_name"  # Passed context data
    assert isinstance(mock_teardown.call_args[0][0].logger.getEffectiveLevel(), int)
    assert mock_teardown.call_args[0][0].foo == "bar"  # Passed user data

    assert send_multipart_mock.called
    assert send_multipart_mock.call_count == msg_num


def test_many_errors_in_row(out_only_args_mock, send_multipart_mock):
    def process(userdata):
        while True:
            yield "šentinel/test", { "foo": "bar" }

    mock_setup = Mock(return_value={ "foo": "bar" })
    mock_teardown = Mock()

    with pytest.raises(SystemExit) as se:
        sn.sn_main("box_name", process, setup=mock_setup, teardown=mock_teardown)

    assert se.type == SystemExit
    assert se.value.code == 1

    assert mock_setup.called
    assert mock_setup.call_count == 1

    assert mock_teardown.called
    assert mock_teardown.call_count == 1  # Should be called right one
    assert mock_teardown.call_args[0][0].name == "box_name"  # Passed context data
    assert isinstance(mock_teardown.call_args[0][0].logger.getEffectiveLevel(), int)
    assert mock_teardown.call_args[0][0].foo == "bar"  # Passed user data

    assert not send_multipart_mock.called


# I'm not going to test setup and teardown anymore. I tested all available
# versions.

def test_resetable_error_counter(out_only_args_mock, send_multipart_mock):
    def process(_):
        for i in range(10):
            yield "šentinel/test", { "foo": "bar"}
        yield "sentinel/test", { "foo": "bar" }

    sn.sn_main("box_name", process)

    assert send_multipart_mock.called
