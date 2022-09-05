import argparse
import logging


class EnableVerbose(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)


def get_arg_parser():
    """ Creates own arguments parser and return it as an object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--resource',
                        action='append',
                        required=True,
                        help='resource format: sockname,[connect/bind],sock_type,ip_address,port'
                        )
    parser.add_argument('--disable-ipv6',
                        action='store_true',
                        help='Disable IPv6 mode of ZMQ sockets'
                        )
    parser.add_argument('-v', '--verbose',
                        nargs=0,
                        action=EnableVerbose,
                        help="Enables debug mode in logger"
                        )
    parser.add_argument('-n', '--name',
                    help="Name of the box",
                    required=True,
                    type=str,
                    )
    return parser
