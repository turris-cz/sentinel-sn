#!/usr/bin/env python3

import time
import sn


class FeederBox(sn.SNGeneratorBox):
    def process(self):
        while True:
            time.sleep(0.01)
            t = time.time()
            print(t)
            yield "sentinel/bechmark", {"counter": t}


if __name__ == "__main__":
    FeederBox().run()
