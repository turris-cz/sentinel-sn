#!/usr/bin/env python3

import turris_sentinel_network


class InMultipleOutBox(turris_sentinel_network.SNMultipleOutputPipelineBox):
    def setup(self):
        return {
                "foo": "bar",
        }

    def teardown(self):
        print("teardown")

    def process(self, msg_type, payload):
        print(msg_type, payload)

        payload2 = payload.copy()

        payload.pop("fee")
        payload2.pop("foo")

        return [(msg_type + "/fee", payload2), (msg_type + "/foo", payload)]


if __name__ == "__main__":
    InMultipleOutBox().run()
