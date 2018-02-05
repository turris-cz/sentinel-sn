import pytest

import sn

@pytest.fixture
def arg_parser():
    return sn.get_arg_parser()

@pytest.fixture
def empty_args():
    return []

@pytest.fixture(params=[
                        "--resource",
                        ])
def bad_args(request):
    return request.param.split(" ")
