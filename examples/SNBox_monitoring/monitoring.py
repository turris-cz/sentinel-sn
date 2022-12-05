#!/usr/bin/env python3

from turris_sentinel_network.msgloop import SNTerminationBox


class MonitorCollectorBox(SNTerminationBox):
    def process(self, msg_type, payload):
        print("process")
        print(msg_type, payload)


MonitorCollectorBox().run()
