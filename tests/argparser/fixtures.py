import pytest

import sn

@pytest.fixture
def empty_args():
    return []

@pytest.fixture(params=[
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
                            " --resource res,connect,PUSH,localhost,8800",
                        "--resource res,bind,PULL,localhost,8800"
                            " --resource res,bind,PULL,localhost,8800",
                        ])
def bad_args(request):
    return request.param.split(" ")

@pytest.fixture(params=[
                        "--resource res,connect,PUSH,127.0.0.1,8800",
                        "--resource res,connect,PUSH,setinel.turris.cz,8800",
                        ])
def conn_args(request):
    return request.param.split(" ")

@pytest.fixture(params=[
                        "--resource res,bind,PUSH,*,8800",
                        "--resource res,bind,PULL,*,8801",
                        "--resource res,bind,PULL,127.0.0.1,8802",
                        ])
def bind_args(request):
    return request.param.split(" ")

@pytest.fixture(params=[
                        "--resource res1,connect,PUSH,localhost,8800"
                            " --resource res2,connect,PUSH,localhost,8800",
                        "--resource res1,connect,PUSH,localhost,8800"
                            " --resource res1,connect,PUSH,localhost,8801"
                            " --resource res2,connect,PUB,localhost,8802",
                        "--resource res1,connect,PUB,localhost,8800"
                            " --resource res1,connect,PUB,localhost,8801"
                            " --resource res2,connect,PUB,localhost,8802",
                        ])
def multisock_args(request):
    return request.param.split(" ")

@pytest.fixture
def required_args():
    return "--resource res,connect,PUSH,127.0.0.1,8800".split(" ")
