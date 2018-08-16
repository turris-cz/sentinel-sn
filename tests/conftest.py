import sys

import pytest

import zmq

sys.path.append("..")


@pytest.fixture
def zmq_context():
    return zmq.Context.instance()
