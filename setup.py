#!/usr/bin/env python

from setuptools import setup

setup(name="sn",
      version="0.3.1",
      description="Sentinel networking library",
      author="CZ.NIC, z.s.p.o.",
      author_email="admin@turris.cz",
      url="https://gitlab.labs.nic.cz/turris/sentinel/sn",
      packages=[
          "sn",
      ],
      install_requires=[
          "msgpack",
          "zmq",
      ],
      extras_require={
          "tests": [
              "pytest",
              "coverage",
              "pytest-cov",
          ],
          "docs": [
              "Sphinx",
              "sphinx-rtd-theme",
              "recommonmark",
          ]
      }
      )
