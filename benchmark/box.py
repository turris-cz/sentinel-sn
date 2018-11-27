#!/usr/bin/env python3

import sn


class MyBox(sn.SNPipelineBox):
    def process(self, msg_type, payload):
        return msg_type, payload


if __name__ == "__main__":
    MyBox("benchmark_box").run()
