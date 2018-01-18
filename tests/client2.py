#!/usr/bin/env python3

import sys
import sn
import time

from random import randint

(sock_cli, sock_cli2) = sn.socket_builder(("sock_cli", "sock_cli2"), sys.argv[1:])

rand_ID = randint(10,99)
print("client ID (randomly generated)="+str(rand_ID))

for request in range(1, 4):
    message = randint(100, 999)
    print("(Client " + str(rand_ID) + "): Sending request["+str(message)+"]")

    #sock_cli.send(str(rand_ID) + ":" + str(message))
    sock_cli.send_multipart(sn.encode_msg("sn/test", str(rand_ID) + ":" + str(message)))

    msg_type, message = sn.parse_msg(sock_cli.recv_multipart())
    #message = sock_cli.recv()

    message = message.split(":")

    print("(Client " + str(rand_ID) + "): Received reply[" + message[1] + "] from server  " + message[0])

    message = randint(100, 999)
    print("(Client " + str(rand_ID) + "): Sending request["+str(message)+"]")

    #sock_cli.send(str(rand_ID) + ":" + str(message))
    sock_cli2.send_multipart(sn.encode_msg("sn/test", str(rand_ID) + ":" + str(message)))

    msg_type, message = sn.parse_msg(sock_cli2.recv_multipart())
    #message = sock_cli.recv()

    message = message.split(":")

    print("(Client " + str(rand_ID) + "): Received reply[" + message[1] + "] from server  " + message[0])

time.sleep(1)
