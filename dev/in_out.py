#!/usr/bin/env python3

import zmq

import sn


def setup():
    return {
            "foo": "bar",
    }


def teardown(context):
    print("teardown")


def process(context, msg_type, payload):
    print(msg_type, payload)

    return msg_type, payload


if __name__ == "__main__":
    sn.sn_main("in_out", process, setup=setup, teardown=teardown)
