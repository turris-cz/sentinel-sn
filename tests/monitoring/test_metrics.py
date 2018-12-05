import threading

import sn


def test_counter():
    c = sn.monitoring.Counter("test", threading.Lock())
    assert c.value == 0

    c.count()
    assert c.value == 1

    c.reset()
    assert c.value == 0
