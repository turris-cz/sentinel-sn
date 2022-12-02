#!/usr/bin/env python3

import turris_sentinel_network


class MonitorCollectorBox(turris_sentinel_network.SNTerminationBox):
    def process(self, msg_type, payload):
        print("process")
        print(msg_type, payload)


MonitorCollectorBox().run()
