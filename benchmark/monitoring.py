#!/usr/bin/env python3

import time

import zmq

import sn


def main():
    ctx = sn.SN(zmq.Context.instance())
    s = ctx.get_socket("mon")

    while True:
        msg = s.recv_multipart()
        msg_type, payload = sn.parse_msg(msg)

        if msg_type == "sentinel/monitoring/stats":
            print(payload)


if __name__ == "__main__":
    main()
