#!/usr/bin/env python3


import random
from time import sleep

from sn import SNGeneratorBox


class Dustman(SNGeneratorBox):
    def process(self):
        while True:
            sleep(1)
            yield "msg/i/should/care/about", {"field": random.randint(0, 10000)}


Dustman("feeder").run()
