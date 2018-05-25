import pytest

import sn

def test_empty_name():
    with pytest.raises(TypeError):
        sn.sn_main()


def test_no_process():
    with pytest.raises(TypeError):
        sn.sn_main("test")


def test_at_least_one_socket(bad_socket_args_mock):
    with pytest.raises(sn.SetupError) as e:
        sn.sn_main("test", lambda: None)
    assert str(e.value) == "Neither input nor output socket provided"


def test_generator_needed(out_only_args_mock):
    def process(u, t, p):
        return t, p

    with pytest.raises(sn.SetupError) as e:
        sn.sn_main("test", process)
    assert str(e.value) == "Generator is expected for output-only box"


def test_setup_dictionary(out_only_args_mock):
    def setup():
        return 42

    with pytest.raises(sn.SetupError) as e:
        sn.sn_main("test", lambda: None, setup=setup)
    assert str(e.value) == "Setup function didn't return a dictionary"


def test_setup_reserved_word(out_only_args_mock):
    def setup():
        return { "name": "foo" }

    with pytest.raises(sn.SetupError) as e:
        sn.sn_main("test", lambda: None, setup=setup)
    assert "Used reserved word in user_data" in str(e.value)


def test_unnecessary_output(in_only_args_mock, recv_multipart_mock):
    with pytest.raises(sn.SetupError) as e:
        sn.sn_main("test", lambda u, t, p: ("foo", "bar"))
    assert str(e.value) == "Box generated output but there is any output socket. Bad configuration?"
