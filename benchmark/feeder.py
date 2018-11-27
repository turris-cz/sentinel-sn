#!/usr/bin/env python3

import time

import zmq

import sn


def main():
    ctx = sn.SN(zmq.Context.instance())
    s = ctx.get_socket("feeder")

    start = time.time()

    for c in range(100000000000):
        if (c % 10000) == 0:
            print(c, time.time() - start)
            start = time.time()

        msg = sn.encode_msg("sentinel/bechmark", {"counter": c})
        s.send_multipart(msg)


if __name__ == "__main__":
    main()
