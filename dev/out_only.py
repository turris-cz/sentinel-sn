#!/usr/bin/env python3

import time

import zmq

import sn


def setup():
    return {
            "foo": "bar",
    }


def teardown(context):
    print("teardown")


def process(context):
    serial = 0
    while True:
        data = {
            "foo": context.foo,
            "serial": serial,
            "ts": int(time.time()),
        }

        serial += 1

        yield "sentinel/dev/sn", data

        print("PUB", data)
        time.sleep(1)


if __name__ == "__main__":
    sn.sn_main("out_only", process, setup=setup, teardown=teardown)
