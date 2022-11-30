#!/usr/bin/env python3

import turris_sentinel_network


class MyBox(turris_sentinel_network.SNPipelineBox):
    def process(self, msg_type, payload):
        return msg_type, payload


if __name__ == "__main__":
    MyBox().run()
