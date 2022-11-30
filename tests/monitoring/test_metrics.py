import threading

import turris_sentinel_network


def test_counter():
    c = turris_sentinel_network.monitoring.Counter("test", threading.Lock())
    assert c.value == 0

    c.count()
    assert c.value == 1

    c.reset()
    assert c.value == 0
