import pytest

from turris_sentinel_network.monitoring import Monitoring


def test_managing_multiple_counters(monitoring_socket, send_multipart_mock):
    m = Monitoring("test", monitoring_socket)
    c1 = m.get_counter("counter1")
    c2 = m.get_counter("counter2")

    counters = m._get_counters()
    assert counters["counter1"] == 0
    assert counters["counter2"] == 0

    c1.count()
    c2.count()

    counters = m._get_counters()
    assert counters["counter1"] == 1
    assert counters["counter2"] == 1

    m._reset_counters()

    counters = m._get_counters()
    assert counters["counter1"] == 0
    assert counters["counter2"] == 0


def test_unique_names(monitoring_socket, send_multipart_mock):
    m = Monitoring("test", monitoring_socket)
    m.get_counter("counter")
    with pytest.raises(ValueError):
        m.get_counter("counter")
