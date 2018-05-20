#!/usr/bin/env python3

import zmq

import sn


def setup():
    class ExampleResources:
        foo = "bar"

    return ExampleResources


def teardown(userdata):
    print("teardown")


def process(envdata, userdata, msg_type, payload):
    print(msg_type, payload)


if __name__ == "__main__":
    sn.sn_main("in_only", setup=setup, teardown=teardown, process=process)
