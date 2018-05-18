import pytest

import sn

@pytest.fixture
def required_type_arg():
    return "--resource res,connect,PUSH,127.0.0.1,8800".split(" ")
