#!/usr/bin/env python3

import zmq
import sys
import sn
import time

from random import randint


ctx = zmq.Context.instance()
sctx = sn.SN(ctx)
# Resources are passed using internal argument parser:
# Socket "sock_cli" is enforced to be "REQ" type:
sock_cli = sctx.get_socket(("sock_cli","REQ"))


# Some work:
rand_ID = randint(10,99)
print("client ID (randomly generated)="+str(rand_ID))

for request in range(1, 4):
    message = randint(100, 999)
    print("(Client " + str(rand_ID) + "): Sending request["+str(message)+"]")

    sock_cli.send_multipart(sn.encode_msg("sn/test", str(rand_ID) + ":" + str(message)))
    msg_type, message = sn.parse_msg(sock_cli.recv_multipart())
    message = message.split(":")

    print("(Client " + str(rand_ID) + "): Received reply[" + message[1] + "] from server  " + message[0])


time.sleep(1)
