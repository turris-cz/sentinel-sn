import sn

def test_encoding(good_type, good_payload, good_msg):
    encoded = sn.encode_msg(good_type, good_payload)
    assert encoded == good_msg
