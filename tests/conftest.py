import sys
sys.path.append("..")

import pytest

import zmq
import sn


@pytest.fixture
def zmq_context():
    return zmq.Context.instance()
