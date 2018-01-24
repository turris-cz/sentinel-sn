#!/usr/bin/env python3

import zmq
import sys
import time
from random import randint

import sn

aparser = sn.get_arg_parser()
args = sn.parse(aparser)
print(args)

ctx = zmq.Context.instance()
sctx = sn.Resources(ctx, args)
sock_srv = sctx.get_socket("sock_srv")

rand_ID = randint(10,99)
print("server ID (randomly generated)="+str(rand_ID))

while True:
    #  Wait for next request from client
    msg_type, message = sn.parse_msg(sock_srv.recv_multipart())
    #message = sock_srv.recv()
    message = message.split(":")
    print("(Server " + str(rand_ID) + "): Received request[" + message[1]
            + "] from client " + message[0])
    time.sleep(1)

    sock_srv.send_multipart(sn.encode_msg("sn/test", str(rand_ID) + ":"
            + str(message[1])))
    #sock_srv.send(str(rand_ID) + ":" + str(message[1]))
