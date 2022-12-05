#!/usr/bin/env python3

from turris_sentinel_network.msgloop import SNPipelineBox


class InOutBox(SNPipelineBox):
    def setup(self):
        print("setup")
        return {
            "fee": "beer",
        }

    def teardown(self):
        print("teardown")

    def process(self, msg_type, payload):
        print("process")
        payload["fee"] = self.ctx.fee
        print(msg_type, payload)
        return msg_type, payload


InOutBox().run()
