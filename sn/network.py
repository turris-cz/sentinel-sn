#!/usr/bin/env python3

import zmq

from collections import namedtuple

from .argparser import get_arg_parser, parse

class SentinelError(Exception):
    pass


class InvalidMsgError(SentinelError):
    pass


class SockConfigError(Exception):
    pass


def resource_parser(config_list):
    """ Gets a tuple of command line arguments - each for one socket connection
    in the form {sockname,[conn/bind],SOCK_TYPE,IP,PORT}.
    Returns a dictionary filled with zmq socket configs in the form
    {name:[connection1, connection2,...]} as each ZMQ socket can handle
    multiple connections. Each connection is a namedtuple.
    """
    Connection = namedtuple(
            'Connection',
            ['direction', 'sock_type', 'address', 'port']
    )
    resources = dict()
    for config in config_list:
        config = config[0]
        splitted = config.split(",")
        if len(splitted) == 5:
            if not splitted[0] in resources:
                resources[splitted[0]] = list()
            resources[splitted[0]].append(Connection(*splitted[1:]))
        else:
            raise SockConfigError("Resource {} is invalid.".format(config))
    return resources


class SN:
    """ This class serves as a container for all resources. This class provides
    an API-like interface for requesting ZMQ sockets based on available
    resources.
    """
    def __init__(self, ctx, args=get_arg_parser().parse_args()):
        """ Gets a list of command line arguments - each for one socket
        connection and creates a dict of ZMQ socket configs.
        """
        self.context = ctx
        self.sock_configs = dict()
        res_avail = resource_parser(args.resource)

        for res in res_avail:
            sc = None
            for connection in res_avail[res]:
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
                        connection.port,
                        ipv6=not args.disable_ipv6
                    )
            self.sock_configs[res] = sc

    def get_socket(self, *sockets):
        """ Gets multiple socket names in 'get_socket(name1, name2,...)'
        or 'get_socket((name1, TYPE1), name2, (name3,TYPE3),...)' or any of
        their combinations. Returns list of all available ZMQ sockets with the
        required names. Exception is risen when there is no socket with the
        desired name or when the socket is of another type.
        """
        ret = list()
        for socket in sockets:
            if type(socket) == tuple:
                sock_name = socket[0]
            else:
                sock_name = socket
            if sock_name in self.sock_configs:
                if (
                    type(socket) == tuple
                    and not self.sock_configs[sock_name].is_type(socket[1])
                ):
                    raise SockConfigError("Socket type does not match required value!")
                if not self.sock_configs[sock_name].socket:
                    self.sock_configs[sock_name].connect()
                ret.append(self.sock_configs[sock_name].socket)
            else:
                raise SockConfigError("Resource {} not provided.".format(sock_name))
        if len(ret) == 1:
            return ret[0]
        else:
            return ret


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

    def __init__(self, context, socktype, direction, addr, port, ipv6):
        """ Adds socket configuruation. List
        of all connection is stored for further checking of duplicate
        connections.
        """
        self.check_params_validity(socktype, direction, addr, port)

        self.socktype = SockConfig.SOCKET_TYPE_MAP[socktype]
        self.direction = direction

        zmq_connection = self.ZMQConnection(addr, port)
        self.connections = list()
        self.connections.append(zmq_connection)
        self.context = context
        self.socket = None
        self.ipv6 = ipv6

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

        if socktype not in SockConfig.SOCKET_TYPE_MAP:
            raise SockConfigError("Unknown socket option", socktype)

        if direction not in SockConfig.DIRECTIONS:
            raise SockConfigError("Unknown direction option", direction)

        if int(port) < 1 or int(port) > 65535:
            raise SockConfigError("Port number out of range", port)

    def is_type(self, socktype):
        """ Checks whether the socket type of this socket is equal to
        'socktype' string argument.
        """
        return (
            socktype in SockConfig.SOCKET_TYPE_MAP
            and self.socktype == SockConfig.SOCKET_TYPE_MAP[socktype]
        )

    def connect(self):
        """ Connects or binds unconnected/unbound zmq socket. An exception
        is risen when the socket is already connected.
        """
        if not self.socket:
            self.socket = self.context.socket(self.socktype)
            self.socket.ipv6 = self.ipv6

            for zmq_connection in self.connections:
                if self.direction == "bind":
                    self.socket.bind(zmq_connection.connection)
                elif self.direction == "connect":
                    self.socket.connect(zmq_connection.connection)
                else:
                    raise SockConfigError("Wrong socket direction")
        else:
            raise SockConfigError("Socket already connected")
