import pytest

import sn


def test_encoding(good_type, good_payload, good_msg):
    encoded = sn.encode_msg(good_type, good_payload)
    assert encoded == good_msg


def test_empty_type(good_payload):
    with pytest.raises(sn.InvalidMsgError):
        sn.encode_msg(None, good_payload)


def test_empty_payload(good_type):
    with pytest.raises(sn.InvalidMsgError):
        sn.encode_msg(good_type, None)


def test_bad_payload(good_type):
    with pytest.raises(sn.InvalidMsgError):
        sn.encode_msg(good_type, ("I", "am", "a", "tuple"))


def test_good_type(good_types, good_payload):
    (t, p) = sn.encode_msg(good_types, good_payload)
    assert t
    assert p


def test_invalid_type(bad_types, good_payload):
    with pytest.raises(sn.InvalidMsgError):
        (t, p) = sn.encode_msg(bad_types, good_payload)
