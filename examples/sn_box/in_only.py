#!/usr/bin/env python3

import turris_sentinel_network


class InOnlyBox(turris_sentinel_network.SNTerminationBox):
    def setup(self):
        return {
            "foo": "bar",
        }

    def teardown(self):
        print("teardown")

    def process(self, msg_type, payload):
        print(msg_type, payload)


if __name__ == "__main__":
    InOnlyBox().run()
