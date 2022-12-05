#!/usr/bin/env python3

from turris_sentinel_network.msgloop import SNTerminationBox


class InOnlyBox(SNTerminationBox):
    def setup(self):
        print("setup")
        return {
            "foo": "bar",
        }

    def teardown(self):
        print("teardown")

    def process(self, msg_type, payload):
        print("process")
        print(msg_type, payload)


InOnlyBox().run()
