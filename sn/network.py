import re

import zmq

from .argparser import get_arg_parser
from .exceptions import *


class Resource:
    NAME = re.compile("[a-z0-9_-]+")
    ADDRESS = re.compile("[a-z0-9_-]+") #TODO Use something better
    DIRECTIONS = [
        "connect",
        "bind"
    ]
    SOCK_TYPES = [
        "REQ",
        "REP",
        "DEALER",
        "ROUTER",
        "PUB",
        "SUB",
        "PUSH",
        "PULL",
        "PAIR",
    ]

    def __init__(self, name, direction, sock_type, address, port):
        if not Resource.NAME.match(name):
            raise SockConfigError("Inadmissible characters in resource name")

        if direction not in Resource.DIRECTIONS:
            raise SockConfigError("Inadmissible or empty value for direction (use connect or bind)")

        if sock_type not in Resource.SOCK_TYPES:
            raise SockConfigError("Inadmissible or empty socket type")

        if not Resource.ADDRESS.match(address) and address != "*":
            raise SockConfigError("Inadmissible characters in resource address")

        try:
            port_number = int(port)
        except ValueError:
            raise SockConfigError("Port must be a number")

        if port_number < 1 or port_number > 65535:
            raise SockConfigError("Port number is out of range (0-65535)")

        # This is a little bit higher logic
        if address == "*" and direction == "connect":
            raise SockConfigError("On '*' is only bind operation permitted")

        self.name = name
        self.direction = direction
        self.sock_type = sock_type
        self.address = address
        self.port = port_number


    def get_connection_string(self):
        return "tcp://{}:{}".format(self.address, self.port)


    @classmethod
    def from_string(cls, arg):
        splitted = arg.split(",")

        if len(splitted) != 5:
            raise SockConfigError("Bad count of resource string items")

        return cls(*splitted)


    def __eq__(self, other):
        if self.name == other.name and \
               self.direction == other.direction and \
               self.sock_type == other.sock_type and \
               self.address == other.address and \
               self.port == other.port:
            return True

        return False


    def __ne__(self, other):
        return not self.__eq__(other)


class Socket:
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

    def __init__(self, name, **configuration):
        self.name = name
        self.resources = []
        self.my_type = None
        self.my_direction = None
        self.configuration = configuration
        self.setup_done = False


    def check_resource(self, resource):
        if self.name != resource.name:
            raise SockConfigError("Putting bad resource to socket")

        if not self.my_type:
            self.my_type = resource.sock_type

        if self.my_type != resource.sock_type:
            raise SockConfigError("New resource is different type than current Socket type")

        if not self.my_direction:
            self.my_direction = resource.direction

        if self.setup_done and self.my_direction == "bind":
            raise SockConfigError("Socket can have only one bind operation")

        if resource in self.resources:
            raise SockConfigError("Resource duplication")


    def add_resource(self, resource):
        self.check_resource(resource)

        self.resources.append(resource)

        self.setup_done = True


    def build(self, ctx, name, sock_type=None):
        if self.name != name:
            raise SockConfigError("Name of requested resource is invalid")

        if sock_type and self.my_type != sock_type:
            raise SockConfigError("Unmatched socket type with requested one")

        socket = ctx.socket(Socket.SOCKET_TYPE_MAP[self.my_type])

        if self.my_direction == "bind":
            socket.bind(self.resources[0].get_connection_string())

        else:
            for resource in self.resources:
                socket.connect(resource.get_connection_string())

        self.configure(socket)

        return socket


    def configure(self, socket):
        if "ipv6" in self.configuration:
            socket.ipv6 = self.configuration["ipv6"]


class SN:
    """ This class serves as a container for all resources. This class provides
    an API-like interface for requesting ZMQ sockets based on available
    resources.
    """
    def __init__(self, ctx, argparser=None):
        ## Gather data
        self.context = ctx

        if argparser:
            self.args = argparser.parse_args()
        else:
            self.args = get_arg_parser().parse_args()

        ## Build all necessary configuration
        self.build_global_configuration()
        self.parse_resources()
        self.build_sockets()


    def build_global_configuration(self):
        self.global_configuration = {
            "ipv6": not self.args.disable_ipv6,
        }


    def parse_resources(self):
        ## Currently I don't know why but resources is array of arrays
        self.resources = [ Resource.from_string(res[0]) for res in self.args.resource ]


    def build_sockets(self):
        self.sockets = {}

        for resource in self.resources:
            if resource.name not in self.sockets:
                self.sockets[resource.name] = Socket(resource.name, **self.global_configuration)

            self.sockets[resource.name].add_resource(resource)


    def get_socket(self, *requested_sockets):
        """ Gets multiple socket names in 'get_socket(name1, name2,...)'
        or 'get_socket((name1, TYPE1), name2, (name3,TYPE3),...)' or any of
        their combinations. Returns list of all available ZMQ sockets with the
        required names. Exception is risen when there is no socket with the
        desired name or when the socket is of another type.
        """
        ret = []

        for request in requested_sockets:
            if type(request) == tuple:
                sock_name, sock_type = request
            else:
                sock_name, sock_type = request, None

            if sock_name not in self.sockets:
                raise UndefinedSocketError("Requesting undefined socket")

            socket = self.sockets[sock_name]
            ret.append(socket.build(self.context, sock_name, sock_type))

        if len(ret) == 1:
            return ret[0]
        else:
            return ret
