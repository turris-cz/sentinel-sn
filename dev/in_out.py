#!/usr/bin/env python3

import zmq

import sn


def main():
    """Plain lib version"""
    ctx = sn.SN(zmq.Context.instance())

    socket_in = ctx.get_socket("in")
    socket_out = ctx.get_socket("out")

    while True:
        msg = socket_in.recv_multipart()
        socket_out.send_multipart(msg)


if __name__ == "__main__":
    main()
