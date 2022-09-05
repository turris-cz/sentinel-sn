#!/usr/bin/env python3

import sn


class MyBox(sn.SNTerminationBox):
    def setup(self):
        return {
                "foo": "bar",
        }

    def teardown(self):
        print("teardown")

    def process(self, msg_type, payload):
        print(msg_type, payload)


if __name__ == "__main__":
    MyBox().run()
