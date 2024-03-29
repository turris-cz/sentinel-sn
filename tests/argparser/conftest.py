from unittest.mock import patch

import pytest


def args_from_string(s):
    args = ["prog"]
    args.extend([a for a in s.split(" ") if a])

    return args


@pytest.fixture
def one_resource_mock():
    with patch(
        "sys.argv", args_from_string("--name test --resource res,connect,PUSH,127.0.0.1,8800")
    ) as m:
        yield m


@pytest.fixture
def verbose_args_mock():
    with patch(
        "sys.argv", args_from_string("--name test --resource res,connect,PUSH,127.0.0.1,8800 -v")
    ) as m:
        yield m


@pytest.fixture
def empty_args_mock():
    with patch("sys.argv", args_from_string("")) as m:
        yield m


@pytest.fixture(
    params=[
        "--resource",
        "--resource BAD",
        "--resource res,connect,PUSH,,",
        "--resource res,connect,PUSH,sentinel.cz,",
        "--resource res,connect,PULL,,7700",
        "--resource ,connect,PUSH,sentinel.cz,7700",
        "--resource connect,PUSH,sentinel.cz,7700",
        "--resource res,connect,PUSh,sentinel.cz,7700",
        "--resource res,connect,FOO,sentinel.cz,7700",
        "--resource res,connect,FOO,sentinel.cz,7700",
        "--resource res,connect,PUSH,sentinel.cz,0",
        "--resource res,connect,PUSH,*,8800",
        "--resource res,conn,PUSH,127.0.0.1,8800",
        "--resource res,connect,PUSH,localhost,8800"
        "     --resource res,connect,PUSH,localhost,8800",
        "--resource res,bind,PULL,localhost,8800" "     --resource res,bind,PULL,localhost,8800",
        "--resource res,bind,PULL,localhost,8800" "     --resource res,bind,PUSH,localhost,8800",
    ]
)
def bad_resources_mock(request):
    with patch("sys.argv", args_from_string(request.param)) as m:
        yield m


@pytest.fixture(
    params=[
        "--name 'test' --resource res,connect,PUSH,127.0.0.1,8800",
        "--name 'test' --resource res,connect,PUSH,setinel.turris.cz,8800",
        "--name 'test' --resource res,connect,PUSH,[::1],8800",
    ]
)
def connect_resources_mock(request):
    with patch("sys.argv", args_from_string(request.param)) as m:
        yield m


@pytest.fixture(
    params=[
        "--name 'test' --resource res,bind,PUSH,*,8800",
        "--name 'test' --resource res,bind,PULL,*,8801",
        "--name 'test' --resource res,bind,PULL,127.0.0.1,8802",
        "--name 'test' --resource res,bind,PULL,::1,8802",
        "--name 'test' --resource res,bind,PULL,[::1],8803",
    ]
)
def bind_resources_mock(request):
    with patch("sys.argv", args_from_string(request.param)) as m:
        yield m


@pytest.fixture(
    params=[
        "--name 'test' --resource res1,connect,PUSH,localhost,8800"
        "     --resource res2,connect,PUSH,localhost,8800",
        "--name 'test' --resource res1,connect,PUSH,localhost,8800"
        "     --resource res1,connect,PUSH,localhost,8801"
        "     --resource res2,connect,PUB,localhost,8802",
        "--name 'test' --resource res1,connect,PUB,localhost,8800"
        "     --resource res1,connect,PUB,localhost,8801"
        "     --resource res2,connect,PUB,localhost,8802",
    ]
)
def multisock_resources_mock(request):
    with patch("sys.argv", args_from_string(request.param)) as m:
        yield m
