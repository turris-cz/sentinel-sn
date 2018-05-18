#!/usr/bin/env python3

import time

import zmq

import sn


def main():
    """Plain lib version"""
    ctx = sn.SN(zmq.Context.instance())

    socket = ctx.get_socket("out")

    while True:
        data = {
            "foo": "bar",
            "ts": int(time.time()),
        }
        msg = sn.encode_msg("sentinel/dev/sn", data)
        socket.send_multipart(msg)
        print("PUB", data)

        time.sleep(1)


if __name__ == "__main__":
    main()
