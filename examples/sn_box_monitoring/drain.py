#!/usr/bin/env python3

import sn


class DrainBox(sn.SNTerminationBox):
    def process(self, msg_type, payload):
        print(msg_type, payload)


if __name__ == "__main__":
    DrainBox().run()

