import pytest
import zmq


@pytest.fixture
def zmq_context():
    return zmq.Context.instance()
