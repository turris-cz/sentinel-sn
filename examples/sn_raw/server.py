#!/usr/bin/env python3

import time
from random import randint

import zmq

import turris_sentinel_network

ctx = zmq.Context.instance()
# Resources are passed using internal argument parser:
sctx = turris_sentinel_network.SN(ctx)
sock_srv = sctx.get_socket("sock_srv")

# Some work:
rand_ID = randint(10, 99)
print("server ID (randomly generated)=" + str(rand_ID))

while True:
    #  Wait for next request from client
    msg_type, message = turris_sentinel_network.parse_msg(sock_srv.recv_multipart())
    message = message.split(":")
    print(
        "(Server "
        + str(rand_ID)
        + "): Received request["
        + message[1]
        + "] from client "
        + message[0]
    )
    time.sleep(1)

    sock_srv.send_multipart(
        turris_sentinel_network.encode_msg("sn/test", str(rand_ID) + ":" + str(message[1]))
    )
