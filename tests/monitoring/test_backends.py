from unittest.mock import Mock

from turris_sentinel_network.monitoring import Monitoring


def test_sentinel_backend(monitoring_socket, send_multipart_mock):
    b = Monitoring("test", monitoring_socket)
    b.message("test", {"some": "data"})

    assert send_multipart_mock.called
    assert send_multipart_mock.call_args[0][0][0] == b"sentinel/monitoring/test"


def test_log_backend():
    b = Monitoring("test")

    # OK, This is stupid and ugly, but I need to test that the backend does something
    b.logger = Mock()

    b.message("test", {"some": "data"})

    assert b.logger.debug.called
    assert b.logger.debug.call_args[0][1] == "sentinel/monitoring/test"
