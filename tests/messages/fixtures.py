import pytest

import msgpack

@pytest.fixture
def good_type():
    return "sentinel/tests/good_string"

@pytest.fixture(params=[
                        "sentinel",
                        "sentinel/tests",
                        "sentinel/tests/goodstring",
                        "sentinel/tests/good/string",
                        "sentinel/tests/good_string",
                        "sentinel/tests/good_string_123",
                        "sentinel/tests/box1",
                        "sentinel/tests/box/1",
                        "s/t/b",
                        "a/b/c/s/d/g",
                        ])
def good_types(request):
    return request.param

@pytest.fixture(params=[
                        "/sentinel/tests/broken",
                        "sentinel/tests/broken/",
                        "/sentinel/tests/broken/",
                        "sentinel/tests/bro ken",
                        "sentinel/tests/bro-ken",
                        "sentinel/tests/Broken",
                        "sentinel/tests/břoken",
                        "sentinel/tests/bro?ken",
                        "sentinel/tests/bro@ken",
                        "sentinel//broken",
                        "sentinel//broken",
                        "s//b",
                        "sentinel/",
                        "/sentinel",
                        ""
                        ])
def bad_types(request):
    return request.param

@pytest.fixture
def good_payload():
    return {
        "key1": "val1",
        "key2": 2,
        "key3": True,
        "key4": "ěščřžýáíé",
    }

@pytest.fixture
def good_msg(good_type, good_payload):
    t = bytes(good_type, encoding="UTF-8")
    p = msgpack.packb(good_payload, encoding="UTF-8")

    return (t, p)

@pytest.fixture
def good_long(good_type, good_payload):
    t = bytes(good_type, encoding="UTF-8")
    p = msgpack.packb(good_payload, encoding="UTF-8")
    x = msgpack.packb(good_payload, encoding="UTF-8")

    return (t, p, x)

@pytest.fixture(params=[1, 5, 7, 9, 12, 15, 18, 20])
def broken_msg(request, good_msg):
    # Parameters are tested by eye, but it generates several different
    # exception from msgpack. So, the test should be sufficient
    pos = request.param

    # Swap "random" bytes
    ba = bytearray(good_msg[1])
    ba[0], ba[pos] = ba[pos], ba[0]

    msg = bytes(ba)

    return (good_msg[0], msg)

@pytest.fixture
def good_type_msg(good_types, good_msg):
    t = bytes(good_types, encoding="UTF-8")
    return (t, good_msg[1])

@pytest.fixture
def broken_type_msg(bad_types, good_msg):
    t = bytes(bad_types, encoding="UTF-8")
    return (t, good_msg[1])
