#!/usr/bin/env python3

import time

from turris_sentinel_network.msgloop import SNGeneratorBox


class FeederBox(SNGeneratorBox):
    def process(self):
        print("process")
        while True:
            time.sleep(2)
            t = time.time()
            print(t)
            yield "sentinel/bechmark", {"counter": t}


FeederBox().run()
