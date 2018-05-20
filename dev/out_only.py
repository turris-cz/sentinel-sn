#!/usr/bin/env python3

import time

import zmq

import sn


def setup():
    class ExampleResources:
        foo = "bar"

    return ExampleResources


def teardown(userdata):
    print("teardown")


def process(envdata, userdata):
    while True:
        data = {
            "foo": userdata.foo,
            "ts": int(time.time()),
        }

        yield "sentinel/dev/sn", data

        print("PUB", data)
        time.sleep(1)


if __name__ == "__main__":
    sn.sn_main("out_only", setup=setup, teardown=teardown, process=process)
