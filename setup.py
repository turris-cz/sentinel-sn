#!/usr/bin/env python

from distutils.core import setup

setup(name = "sn",
    version = "0.1",
    description = "Sentinel networking library",
    author = "Martin Prudek",
    author_email = "martin.prudek@nic.cz",
    url = "https://gitlab.labs.nic.cz/turris/sentinel/sn",
    packages = ['sn'],
    install_requires=["msgpack", "zmq"]
)
