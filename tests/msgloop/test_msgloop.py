import pytest
from unittest.mock import Mock, patch

import turris_sentinel_network


def test_context_data_passed(in_out_args_mock, recv_multipart_mock, send_multipart_mock, good_msg):
    def side_effect():
        yield good_msg
        yield good_msg
        yield StopIteration()

    recv_multipart_mock.side_effect = side_effect()

    class TestBox(turris_sentinel_network.SNPipelineBox):
        pass

    tb = TestBox()
    tb.setup = mock_setup = Mock(return_value={"foo": "bar"})
    tb.teardown = mock_teardown = Mock()
    tb.process = mock_process = Mock(return_value=("sentinel/test", {"foo": "bar"}))

    tb.run()

    assert mock_setup.called
    assert mock_setup.call_count == 1

    assert mock_teardown.called
    assert mock_teardown.call_count == 1

    assert mock_process.called
    assert mock_process.call_count == 2

    assert send_multipart_mock.called
    assert send_multipart_mock.call_count == 2

    assert tb.name == "test"
    assert isinstance(tb.logger.getEffectiveLevel(), int)
    assert tb.ctx.foo == "bar"


def test_regulraly_processed(in_out_args_mock, recv_multipart_mock, send_multipart_mock, good_msg):
    def side_effect():
        yield good_msg
        yield good_msg
        yield StopIteration()

    recv_multipart_mock.side_effect = side_effect()

    class TestBox(turris_sentinel_network.SNPipelineBox):
        def process(self, msg_type, payload):
            return "processed", payload

    TestBox().run()

    assert send_multipart_mock.called
    assert send_multipart_mock.call_count == 2
    assert send_multipart_mock.call_args[0][0][0] == b"processed"


def test_processed_from_generator(out_only_args_mock, send_multipart_mock):
    msg_num = 5

    class TestBox(turris_sentinel_network.SNGeneratorBox):
        def process(self):
            for i in range(msg_num):
                yield "sentinel/test", {"foo": "bar"}

    TestBox().run()

    assert send_multipart_mock.called
    assert send_multipart_mock.call_count == msg_num
    assert send_multipart_mock.call_args[0][0][0] == b"sentinel/test"


def test_many_errors_in_row(out_only_args_mock, send_multipart_mock):
    class TestBox(turris_sentinel_network.SNGeneratorBox):
        def process(self):
            while True:
                yield "šentinel/test", {"foo": "bar"}

    tb = TestBox()

    with pytest.raises(SystemExit) as se:
        tb.run()

    assert se.type == SystemExit
    assert se.value.code == 1

    assert not send_multipart_mock.called


def test_resetable_error_counter(out_only_args_mock, send_multipart_mock):
    class TestBox(turris_sentinel_network.SNGeneratorBox):
        def process(self):
            for i in range(10):
                yield "šentinel/test", {"foo": "bar"}
            yield "sentinel/test", {"foo": "bar"}

    TestBox().run()

    assert send_multipart_mock.called


def test_before_first_request_processed(out_only_args_mock, send_multipart_mock):
    class TestBox(turris_sentinel_network.SNGeneratorBox):
        def before_first_request(self):
            return "sentinel/test/bfr", {"foo": "bar"}

        def process(self):
            yield "sentinel/test", {"foo": "bar"}

    tb = TestBox()
    tb.run()

    assert send_multipart_mock.called
    assert send_multipart_mock.call_count == 2

    assert send_multipart_mock.call_args_list[0][0][0][0] == b"sentinel/test/bfr"
    assert send_multipart_mock.call_args_list[1][0][0][0] == b"sentinel/test"


def test_set_signal_handlers(out_only_args_mock, send_multipart_mock):
    class TestBox(turris_sentinel_network.SNGeneratorBox):
        def process(self):
            yield "sentinel/test", {"foo": "bar"}

    with patch("signal.signal") as signal:
        tb = TestBox()
        tb.run()

        assert signal.called


def test_signal_handler_stops_loop(in_out_args_mock, recv_multipart_mock, send_multipart_mock):
    class TestBox(turris_sentinel_network.SNPipelineBox):
        pass

    def se(t, p):
        # I will be happy for better solution...
        import signal
        sh = signal.getsignal(signal.SIGTERM)
        sh(None, None)
        return t, p

    tb = TestBox()
    tb.process = Mock(side_effect=se)
    tb.run()

    assert send_multipart_mock.called
    assert send_multipart_mock.call_count == 1
