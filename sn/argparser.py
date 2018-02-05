import argparse


def get_arg_parser():
    """ Creates own arguments parser and return it as an object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--resource', nargs=1, action='append', required=True,
        help='resource format: sockname,[conn/bind],sock_type,ip_address,port')
    parser.add_argument('--disable-ipv6', action='store_true')
    return parser


def parse(aparser):
    return aparser.parse_args()
