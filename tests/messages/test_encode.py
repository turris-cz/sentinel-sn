import sn

def test_encoding(good_type, good_dict, good_msg):
    encoded = sn.encode_msg(good_type, good_dict)
    assert encoded == good_msg
