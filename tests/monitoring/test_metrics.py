import threading

from turris_sentinel_network.monitoring import Counter


def test_counter():
    c = Counter("test", threading.Lock())
    assert c.value == 0

    c.count()
    assert c.value == 1

    c.reset()
    assert c.value == 0
