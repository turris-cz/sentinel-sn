#!/usr/bin/env python3

import sys
import sn
import time
import zmq

from random import randint

# Custom argument parser is created here
aparser = sn.get_arg_parser()

ctx = zmq.Context.instance()
sctx = sn.SN(ctx, args)
args = sctx.args
sock_cli, sock_cli2 = sctx.get_socket("sock_cli", ("sock_cli2", "REQ"))

rand_ID = randint(10,99)
print("client ID (randomly generated)="+str(rand_ID))

for request in range(1, 4):
    message = randint(100, 999)
    print("(Client " + str(rand_ID) + "): Sending request["+str(message)+"]")

    sock_cli.send_multipart(sn.encode_msg("sn/test", str(rand_ID) + ":" + str(message)))
    msg_type, message = sn.parse_msg(sock_cli.recv_multipart())
    message = message.split(":")

    print("(Client " + str(rand_ID) + "): Received reply[" + message[1] + "] from server  " + message[0])

    message = randint(100, 999)
    print("(Client " + str(rand_ID) + "): Sending request["+str(message)+"]")

    sock_cli2.send_multipart(sn.encode_msg("sn/test", str(rand_ID) + ":" + str(message)))
    msg_type, message = sn.parse_msg(sock_cli2.recv_multipart())
    message = message.split(":")

    print("(Client " + str(rand_ID) + "): Received reply[" + message[1] + "] from server  " + message[0])
time.sleep(1)
