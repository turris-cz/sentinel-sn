#!/usr/bin/env python3


from sn import SNTerminationBox


class Dumper(SNTerminationBox):
    def process(self, msg_type, payload):
        print(f"{msg_type}: {payload}")


Dumper("dumper").run()
