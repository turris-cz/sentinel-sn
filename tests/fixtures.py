import pytest

import zmq

import sn

@pytest.fixture
def zmq_context():
    return zmq.Context.instance()

@pytest.fixture
def arg_parser():
    return sn.get_arg_parser()
