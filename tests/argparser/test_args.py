import pytest

import argparse

import sn

def test_empty_args(arg_parser, empty_args):
    with pytest.raises(SystemExit):
        arg_parser.parse_args(empty_args)

def test_bad_args(arg_parser, bad_args):
    with pytest.raises(SystemExit):
        arg_parser.parse_args(bad_args)
