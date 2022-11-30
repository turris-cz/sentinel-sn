#!/usr/bin/env python3

from random import randint

import zmq

from turris_sentinel_network import SN, encode_msg, parse_msg

# Setup SN
sctx = SN(zmq.Context.instance())
sock_srv = sctx.get_socket("sock_srv")

# Do some work
server_ID = randint(10, 99)
print("server ID (randomly generated)=" + str(server_ID))

topic = "sn/response"

while True:
    # Receive
    recv = sock_srv.recv_multipart()
    msg_type, payload = parse_msg(recv)
    print(f"Following data with topic: {msg_type} were received:\n", payload)

    # Send
    data = {"server_id": server_ID, "response": randint(100, 999)}
    sn_mesg = encode_msg(topic, data)
    sock_srv.send_multipart(sn_mesg)
    print(f"Following data with topic: {topic} were sent:\n", data)
