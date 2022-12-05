#!/usr/bin/env python3

import time
from random import randint

import zmq

from turris_sentinel_network.messages import encode_msg, parse_msg
from turris_sentinel_network.network import SN

# Setup SN
sctx = SN(zmq.Context.instance())
sock_cli = sctx.get_socket("sock_cli")

# Do some work
client_ID = randint(10, 99)
print("client ID (randomly generated)=" + str(client_ID))

topic = "sn/request"

while True:
    # Send
    data = {"client_id": client_ID, "request": randint(100, 999)}
    sn_mesg = encode_msg(topic, data)
    sock_cli.send_multipart(sn_mesg)
    print(f"Following data with topic: {topic} were sent:\n", data)

    # Receive
    received = sock_cli.recv_multipart()
    msg_type, payload = parse_msg(received)
    print(f"Following data with topic: {msg_type} were received:\n", payload)

    time.sleep(2)
