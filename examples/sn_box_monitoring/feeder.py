#!/usr/bin/env python3

import time
import turris_sentinel_network


class FeederBox(turris_sentinel_network.SNGeneratorBox):
    def process(self):
        while True:
            time.sleep(0.01)
            t = time.time()
            print(t)
            yield "sentinel/bechmark", {"counter": t}


if __name__ == "__main__":
    FeederBox().run()
