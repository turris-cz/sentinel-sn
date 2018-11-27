#!/usr/bin/env python3

import time

import zmq

import sn


def main():
    ctx = sn.SN(zmq.Context.instance())
    s = ctx.get_socket("drain")

    start = time.time()

    avg_sum = 0
    avg_cnt = 0

    while True:
        msg = s.recv_multipart()
        msg_type, payload = sn.parse_msg(msg)

        c = payload["counter"]

        if (c % 10000) == 0:
            time_diff = time.time() - start
            start = time.time()
            avg_sum += time_diff
            avg_cnt += 1
            print(c, time_diff, "/", avg_sum/avg_cnt)


if __name__ == "__main__":
    main()
