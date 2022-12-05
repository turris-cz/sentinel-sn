import pytest

from turris_sentinel_network.exceptions import InvalidMsgError
from turris_sentinel_network.messages import encode_msg


def test_encoding(good_type, good_payload, good_msg):
    encoded = encode_msg(good_type, good_payload)
    assert encoded == good_msg


def test_empty_type(good_payload):
    with pytest.raises(InvalidMsgError):
        encode_msg(None, good_payload)


def test_empty_payload(good_type):
    with pytest.raises(InvalidMsgError):
        encode_msg(good_type, None)


def test_bad_payload(good_type):
    with pytest.raises(InvalidMsgError):
        encode_msg(good_type, ("I", "am", "a", "tuple"))


def test_good_type(good_types, good_payload):
    (t, p) = encode_msg(good_types, good_payload)
    assert t
    assert p


def test_invalid_type(bad_types, good_payload):
    with pytest.raises(InvalidMsgError):
        (t, p) = encode_msg(bad_types, good_payload)
