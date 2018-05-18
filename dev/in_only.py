#!/usr/bin/env python3

import zmq

import sn


def main():
    """Plain lib version"""
    ctx = sn.SN(zmq.Context.instance())

    socket = ctx.get_socket("in")

    while True:
        msg = socket.recv_multipart()
        mtype, data = sn.parse_msg(msg)

        print(mtype, data)


if __name__ == "__main__":
    main()
