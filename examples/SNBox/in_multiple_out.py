#!/usr/bin/env python3

from turris_sentinel_network.msgloop import SNMultipleOutputPipelineBox


class InMultipleOutBox(SNMultipleOutputPipelineBox):
    def setup(self):
        print("setup")
        return {
            "foo": "bar",
        }

    def teardown(self):
        print("teardown")

    def process(self, msg_type, payload):
        print("procces")
        print(msg_type, payload)

        payload2 = payload.copy()

        payload.pop("fee")
        payload2.pop("foo")

        return [(msg_type + "/fee", payload2), (msg_type + "/foo", payload)]


InMultipleOutBox().run()
