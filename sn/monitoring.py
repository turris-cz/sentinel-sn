import threading
import time
import os
import logging

from .messages import encode_msg


RUN_EVERY = 10
HB_RATE = 5


class BaseMetric:
    def __init__(self, name, lock):
        self.name = name
        self.lock = lock
        self.value = 0

    def reset(self):
        self.value = 0


class Counter(BaseMetric):
    def count(self):
        with self.lock:
            self.value += 1


class MonitoringBase:
    def __init__(self, box_name):
        self.name = box_name
        self.id = os.getenv("SENTINEL_ID", box_name)

        self.metrics = {}
        self.lock = threading.Lock()

        self.stats_thread = threading.Thread(target=self.stats_thread_worker,
                                             daemon=True
                                             )
        self.hb_thread = threading.Thread(target=self.hb_thread_worker,
                                          daemon=True
                                          )
        self.stats_thread.start()
        self.hb_thread.start()

    def stats_thread_worker(self):
        while True:
            start_at = time.time()

            # DO WORK
            with self.lock:
                msg = self._get_counters()
                self._reset_counters()

            if msg:
                msg["ts"] = int(time.time())
                msg["box"] = self.name
                msg["id"] = self.id
                self._store_msg("sentinel/monitoring/stats", msg)

            # WORK DONE
            done_at = time.time()
            time.sleep(RUN_EVERY - (done_at - start_at))

    def hb_thread_worker(self):
        msg = {
            "box": self.name,
            "id": self.id,
        }
        while True:
            msg["ts"] = int(time.time())
            self._store_msg("sentinel/monitoring/heartbeat", msg)
            time.sleep(HB_RATE)

    def _reset_counters(self):
        for m in self.metrics.values():
            m.reset()

    def _get_counters(self):
        return {k: v.value for k, v in self.metrics.items()}

    def _store_msg(self, msg_type, payload):
        raise NotImplementedError("_store_msg")

    def get_counter(self, name):
        if name in self.metrics:
            raise ValueError("Trying to define metrics with duplicate name")

        self.metrics[name] = m = Counter(name, self.lock)
        return m

    def message(self, msg_subtype, payload):
        if "box" not in payload:
            payload["box"] = self.name
        if "ts" not in payload:
            payload["ts"] = int(time.time())

        msg_type = "sentinel/monitoring/" + msg_subtype
        self._store_msg(msg_type, payload)


class LogMonitoring(MonitoringBase):
    def __init__(self, box_name):
        self.logger = logging.getLogger(box_name)
        super().__init__(box_name)

    def _store_msg(self, msg_type, payload):
        self.logger.debug("%s: %s", msg_type, payload)


class SentinelMonitoring(MonitoringBase):
    def __init__(self, box_name, socket):
        self.socket = socket
        super().__init__(box_name)

    def _store_msg(self, msg_type, payload):
        msg = encode_msg(msg_type, payload)
        self.socket.send_multipart(msg)


def Monitoring(box_name, socket=None):
    if socket:
        return SentinelMonitoring(box_name, socket)
    else:
        return LogMonitoring(box_name)
