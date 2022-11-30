from unittest.mock import patch

import pytest
import zmq


@pytest.fixture
def monitoring_socket():
    ctx = zmq.Context.instance()
    return ctx.socket(zmq.PUSH)


@pytest.fixture
def send_multipart_mock():
    with patch("zmq.Socket.send_multipart") as m:
        yield m
