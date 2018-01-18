#!/usr/bin/env python3
import argparse

import msgpack
import zmq


class InvalidMsgError(Exception):
    pass

def parse_msg(data):
    """ Gets a Sentinel-type ZMQ message and parses message type and its
    payload.
    """
    try:
        msg_type = str(data[0], encoding="UTF-8")
        payload = msgpack.unpackb(data[1], encoding="UTF-8")

    except IndexError:
        raise InvalidMsgError("Not enough parts in message")

    return msg_type, payload


def encode_msg(msg_type, data):
    b = bytes(msg_type, encoding="UTF-8")
    msg = msgpack.packb(data)

    return (b, msg)

def socket_builder(res_expected, config_list):
    """ Gets a tuple of command line arguments - each for one socket connection
    and returns a list of ZMQ sockets in the same order.
    """
    sockets = list()
    sock_configs = dict()
    res_avail = resource_parser(config_list)
    if set(res_avail).difference(res_expected):
        raise SockConfigError(
                "Unexpected resource provided: "
                + str(set(res_avail).difference(res_expected))
        )
    for res in res_expected:
        sc = None
        if res in res_avail:
            for config in res_avail[res]:
                if sc:
                    sc.add_connection(
                        config[1], config[0], config[2], config[3])
                else:
                    sc = SockConfig(config[1], config[0], config[2], config[3])
                    sockets.append(sc.socket)
        else:
           raise SockConfigError("Resource not provided: " + res)
    return tuple(sockets)


def resource_parser(config_list):
    """ Gets a tuple of command line arguments - each for one socket connection
    in the form {sockname,[conn/bind],SOCK_TYPE,IP,PORT}.
    Returns a dictionary filled with zmq socket configs in the form
    {name:[connection1, connection2,...]} as each ZMQ socket can handle
    multiple connections.
    """
    resources = dict()
    for config in config_list:
        splitted = config.split(",")
        if len(splitted) == 5:
            if not splitted[0] in resources:
                resources[splitted[0]] = list()
            resources[splitted[0]].append(splitted[1:])
        else:
            raise SockConfigError("Invalid resource: " + config)
    return resources


class SockConfigError(Exception):
    pass


class SockConfig:
    # a ZMQ feature: one socket can have a multiple connections
    class ZMQConnection:
        def __init__(self, addr, port):
            self.addr = addr
            self.port = port
            self.connection = self.get_connection()
        def get_connection(self):
            return "tcp://{}:{}".format(self.addr, self.port)


    SOCKET_TYPE_MAP = {
        "REQ": zmq.REQ,
        "REP": zmq.REP,
        "DEALER": zmq.DEALER,
        "ROUTER": zmq.ROUTER,
        "PUB": zmq.PUB,
        "SUB": zmq.SUB,
        "PUSH": zmq.PUSH,
        "PULL": zmq.PULL,
        "PAIR": zmq.PAIR,
    }

    DIRECTIONS = [
        "connect",
        "bind",
    ]

    def __init__(self, socktype, direction, addr, port):
        """ Initilizes ZMQ Context, Socket and its first connection. List
        of all connection is stored for further checking of duplicate
        connections.
        """
        self.check_params_validity(socktype, direction, addr, port)

        zmq_connection = self.ZMQConnection(addr, port)
        self.connections = list()
        self.connections.append(zmq_connection)

        ctx = zmq.Context.instance()
        self.socket = ctx.socket(self.socktype)
        self.socket.ipv6 = True

        if self.direction == "bind":
            self.socket.bind(zmq_connection.connection)
        elif self.direction == "connect":
            self.socket.connect(zmq_connection.connection)

    def add_connection(self, socktype, direction, addr, port):
        """ Adds another ZMQ connection to an existing ZMQ socket.
        """
        self.check_params_validity(socktype, direction, addr, port)

        if self.socktype != SockConfig.SOCKET_TYPE_MAP[socktype]:
            raise SockConfigError("Socket type does not match")

        if self.direction == "bind" or direction == "bind":
            raise SockConfigError("Socket direction mismatch")

        for con in self.connections:
            if con.addr == addr and con.port == port:
                raise SockConfigError("Creating duplicate connection")

        zmq_connection = self.ZMQConnection(addr, port)
        self.connections.append(zmq_connection)

        self.socket.connect(zmq_connection.connection)

    def check_params_validity(self, socktype, direction, addr, port):
        """ Checks whether all the params are present and ZMQ-compliant
        """
        if not socktype:
            raise SockConfigError("Missing socket type")
        if not direction:
            raise SockConfigError("Missing socket direction")
        if not addr:
            raise SockConfigError("Missing address")
        if not port:
            raise SockConfigError("Missing port")

        if socktype in SockConfig.SOCKET_TYPE_MAP:
            self.socktype = SockConfig.SOCKET_TYPE_MAP[socktype]
        else:
            raise SockConfigError("Unknown socket option", socktype)

        if direction in SockConfig.DIRECTIONS:
            self.direction = direction
        else:
            raise SockConfigError("Unknown direction option", direction)


