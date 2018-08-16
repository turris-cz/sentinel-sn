import pytest

import sn


def test_parse(good_type, good_payload, good_msg):
    (t, p) = sn.parse_msg(good_msg)
    assert t == good_type
    assert p == good_payload


def test_longer(good_type, good_payload, good_long):
    (t, p) = sn.parse_msg(good_long)
    assert t == good_type
    assert p == good_payload


def test_missing_type(good_msg):
    with pytest.raises(sn.InvalidMsgError):
        (t, p) = sn.parse_msg(good_msg[1])


def test_missing_payload(good_msg):
    with pytest.raises(sn.InvalidMsgError):
        data = (good_msg[0],)
        (t, p) = sn.parse_msg(data)


def test_broken_payload(broken_msg):
    with pytest.raises(sn.InvalidMsgError):
        (t, p) = sn.parse_msg(broken_msg)


def test_good_type(good_type_msg):
    (t, p) = sn.parse_msg(good_type_msg)
    assert t
    assert p


def test_invalid_type(broken_type_msg):
    with pytest.raises(sn.InvalidMsgTypeError):
        (t, p) = sn.parse_msg(broken_type_msg)
