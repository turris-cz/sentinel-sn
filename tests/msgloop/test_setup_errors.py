import pytest

import turris_sentinel_network


def test_no_process(in_out_args_mock, recv_multipart_mock):
    class TestBox(turris_sentinel_network.SNPipelineBox):
        pass

    with pytest.raises(NotImplementedError):
        TestBox().run()


def test_missing_in_socket_pipeline(out_only_args_mock):
    class TestBox(turris_sentinel_network.SNPipelineBox):
        pass

    with pytest.raises(turris_sentinel_network.SetupError) as e:
        TestBox().run()

    assert str(e.value) == "Input socket wasn't provided"


def test_missing_out_socket_pipeline(in_only_args_mock):
    class TestBox(turris_sentinel_network.SNPipelineBox):
        pass

    with pytest.raises(turris_sentinel_network.SetupError) as e:
        TestBox().run()

    assert str(e.value) == "Output socket wasn't provided"


def test_missing_out_socket_generator(bad_socket_args_mock):
    class TestBox(turris_sentinel_network.SNGeneratorBox):
        def process(self):
            yield None

    with pytest.raises(turris_sentinel_network.SetupError) as e:
        TestBox().run()

    assert str(e.value) == "Output socket wasn't provided"


def test_missing_in_socket_termination(bad_socket_args_mock):
    class TestBox(turris_sentinel_network.SNTerminationBox):
        pass

    with pytest.raises(turris_sentinel_network.SetupError) as e:
        TestBox().run()

    assert str(e.value) == "Input socket wasn't provided"


def test_generator_needed(out_only_args_mock):
    class TestBox(turris_sentinel_network.SNGeneratorBox):
        def process(self, msg_type, payload):
            return msg_type, payload

    with pytest.raises(turris_sentinel_network.SetupError) as e:
        TestBox().run()

    assert str(e.value) == "Generator is expected for output-only box"


def test_setup_dictionary(in_out_args_mock):
    class TestBox(turris_sentinel_network.SNPipelineBox):
        def setup(self):
            return 42

    with pytest.raises(turris_sentinel_network.SetupError) as e:
        TestBox().run()

    assert str(e.value) == "Setup function didn't return a dictionary"


def test_unnecessary_output(in_only_args_mock, recv_multipart_mock):
    class TestBox(turris_sentinel_network.SNTerminationBox):
        def process(self, msg_type, payload):
            return msg_type, payload

    with pytest.raises(turris_sentinel_network.SetupError) as e:
        TestBox().run()

    assert str(e.value) == "Input-only box generated output message. Possibly bug in box."
