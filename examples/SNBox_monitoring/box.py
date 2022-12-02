#!/usr/bin/env python3

from turris_sentinel_network import SNPipelineBox


class MyBox(SNPipelineBox):
    def process(self, msg_type, payload):
        print("process")
        print(msg_type, payload)
        return msg_type, payload


MyBox().run()
