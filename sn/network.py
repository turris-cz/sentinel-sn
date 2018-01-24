#!/usr/bin/env python3
import argparse

import msgpack
import zmq

from collections import namedtuple


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


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resource', nargs=1, action='append')
    return parser


def parse(aparser):
    args = aparser.parse_args()
    return args.resource


def resource_parser(config_list):
    """ Gets a tuple of command line arguments - each for one socket connection
    in the form {sockname,[conn/bind],SOCK_TYPE,IP,PORT}.
    Returns a dictionary filled with zmq socket configs in the form
    {name:[connection1, connection2,...]} as each ZMQ socket can handle
    multiple connections. Each connection is a namedtuple.
    """
    Connection_t = namedtuple(
            'Connection_t',
            'direction sock_type address port'
    )
    resources = dict()
    for config in config_list:
        config = config[0]
        splitted = config.split(",")
        if len(splitted) == 5:
            if not splitted[0] in resources:
                resources[splitted[0]] = list()
            resources[splitted[0]].append(Connection_t(*splitted[1:]))
        else:
            raise SockConfigError("Invalid resource: " + config)
    return resources


class SockConfigError(Exception):
    pass


class Resources:
    """ This class serves as a container for all resources. This class provides
    an API-like interface for requesting ZMQ sockets based on available
    resources.
    """
    def __init__(self, ctx, resources):
        self.context = ctx
        """ Gets a list of command line arguments - each for one socket
        connection and creates a dict of ZMQ socket configs.
        """
        self.sock_configs = dict()
        res_avail = resource_parser(resources)

        for res in res_avail:
            sc = None
            for connection in res_avail[res]:
                print("connection="+str(connection))
                if sc:
                    sc.add_connection(
                        connection.sock_type,
                        connection.direction,
                        connection.address,
                        connection.port
                    )
                else:
                    sc = SockConfig(
                        self.context,
                        connection.sock_type,
                        connection.direction,
                        connection.address,
                        connection.port
                    )
            self.sock_configs[res] = sc

    def get_socket(self, name):
        if name in self.sock_configs:
            if not self.sock_configs[name].socket:
                self.sock_configs[name].connect()
            return self.sock_configs[name].socket
        else:
            raise SockConfigError("Resource not provided: " + name)


class SockConfig:
    # a ZMQ feature: one socket can have a multiple connections
    class ZMQConnection:
        def __init__(self, addr, port):
            self.addr = addr
            self.port = port
            self.connection = self.get_connection_string()

        def get_connection_string(self):
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

    def __init__(self, context, socktype, direction, addr, port):
        """ Initilizes ZMQ Context, Socket and its first connection. List
        of all connection is stored for further checking of duplicate
        connections.
        """
        print("addr="+str(addr)+", port="+str(port))
        self.check_params_validity(socktype, direction, addr, port)

        zmq_connection = self.ZMQConnection(addr, port)
        self.connections = list()
        self.connections.append(zmq_connection)
        self.context = context
        self.socket = None

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

        if int(port) < 1 or int(port) > 65535:
            raise SockConfigError("Port number out of range", port)

    def connect(self):
        if not self.socket:
            self.socket = self.context.socket(self.socktype)
            self.socket.ipv6 = True

            for zmq_connection in self.connections:
                if self.direction == "bind":
                    self.socket.bind(zmq_connection.connection)
                elif self.direction == "connect":
                    self.socket.connect(zmq_connection.connection)
        else:
            raise SockConfigError("Socket already connected")
