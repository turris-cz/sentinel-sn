#!/usr/bin/env python3

import turris_sentinel_network


class InOutBox(turris_sentinel_network.SNPipelineBox):
    def setup(self):
        return {
                "fee": "beer",
        }

    def teardown(self):
        print("teardown")

    def process(self, msg_type, payload):
        payload["fee"] = self.ctx.fee
        print(msg_type, payload)
        return msg_type, payload


if __name__ == "__main__":
    InOutBox().run()
