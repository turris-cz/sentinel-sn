#!/usr/bin/env python3

import time

from turris_sentinel_network import SNGeneratorBox


class OutOnlyBox(SNGeneratorBox):
    def setup(self):
        print("setup")
        return {
            "foo": "boor",
        }

    def teardown(self):
        print("teardown")

    def process(self):
        print("process")
        serial = 0
        while True:
            data = {
                "foo": self.ctx.foo,
                "serial": serial,
                "ts": int(time.time()),
            }

            serial += 1

            yield "sentinel/dev/sn", data

            print("PUB", data)
            time.sleep(2)


OutOnlyBox().run()
