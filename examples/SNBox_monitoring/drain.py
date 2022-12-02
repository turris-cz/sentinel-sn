#!/usr/bin/env python3

from turris_sentinel_network import SNTerminationBox


class DrainBox(SNTerminationBox):
    def process(self, msg_type, payload):
        print("process")
        print(msg_type, payload)


DrainBox().run()
