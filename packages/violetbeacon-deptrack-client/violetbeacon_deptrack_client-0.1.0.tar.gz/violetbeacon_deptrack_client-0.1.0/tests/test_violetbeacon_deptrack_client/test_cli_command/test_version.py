"""
This file is part of Dependency-Track Client by VioletBeacon
Copyright (C) 2025  VioletBeacon, Limited.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from argparse import ArgumentParser
from collections import namedtuple
from unittest.mock import patch

from tests.test_violetbeacon_deptrack_client.fixtures import config_fixture

import violetbeacon_deptrack_client.cli_command.version as sut

@patch('argparse._SubParsersAction.add_parser')
def test_build_subparser(mock_add_parser):
    """Test build_subparser(). This code is similar for all CLI commands"""
    # pylint: disable=duplicate-code
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    sut.build_subparser(subparsers)
    mock_add_parser.assert_called()
    # pylint: enable=duplicate-code

def test_init():
    """init() is a no- op"""
    assert True

def test_action(config_fixture):
    """test build_subparser()"""
    Args = namedtuple("Args", [])
    args = Args()
    result = sut.action(config_fixture, args)
    assert result == 0
