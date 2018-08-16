#!/usr/bin/env python3

import time

import sn


class MyBox(sn.SNGeneratorBox):
    def setup(self):
        return {
                "foo": "bar",
        }

    def teardown(self):
        print("teardown")

    def process(self):
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
            time.sleep(1)


if __name__ == "__main__":
    MyBox("out_only").run()
