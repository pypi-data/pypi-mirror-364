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

import pytest

from tests.test_violetbeacon_deptrack_client.fixtures import config_fixture

import violetbeacon_deptrack_client.cli_command.create_config as sut

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
    """Test init(). This code is similar for all CLI commands"""
    # pylint: disable=duplicate-code
    cfg = sut.Config()
    Args = namedtuple("Args", [
        "project_name",
        "project_version",
        "autocreate",
        "dtrack_baseurl",
        "api_key"
    ])

    sut.init(cfg, Args(
        project_name="test",
        project_version="0.0.0",
        autocreate=True,
        dtrack_baseurl="baseurl",
        api_key="apikey"
    ))
    assert cfg.project_name == "test"
    assert cfg.project_version == "0.0.0"
    assert cfg.autocreate is True
    assert cfg.dtrack_baseurl == "baseurl"
    assert cfg.dtrack_apikey == "apikey"
    # pylint: enable=duplicate-code

def test_action(tmp_path):
    """test action()"""
    cfg = sut.Config(project_name="test",
        project_version="0.0.0",
        autocreate=True,
        dtrack_baseurl="baseurl",
        dtrack_apikey="apikey"
        )
    Args = namedtuple("Args", [
        "config",
    ])
    p = tmp_path / "test_violetbeacon_deptrack_client"
    p.mkdir()
    f = p / "test_action.yaml"
    args = Args(config=f)
    result = sut.action(cfg, args)
    assert result == 0

    # Read the file and compare it to the expected result
    assert f.read_text(encoding="utf-8") == \
        "autocreate: true\n" \
        "dtrack_apikey: apikey\n" \
        "dtrack_baseurl: baseurl\n" \
        "project_name: test\n" \
        "project_version: 0.0.0\n" \

def test_action_refuse_to_overwrite(tmp_path, config_fixture):
    """test action()"""
    Args = namedtuple("Args", [
        "config",
    ])
    p = tmp_path / "test_violetbeacon_deptrack_client"
    p.mkdir()
    f = p / "test_action_refuse_to_overwrite.yaml"
    f.touch()
    args = Args(config=f)

    with pytest.raises(FileExistsError):
        sut.action(config_fixture, args)
