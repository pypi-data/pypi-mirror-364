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

import violetbeacon_deptrack_client.cli_command.upload_bom as sut

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
    # pylint: disable duplicate-code
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
    # pylint: enable duplicate-code

@patch('violetbeacon_deptrack_client.dependency_track.api.put_bom')
def test_action(mock_put_bom, lazy_datadir):
    """test action()"""
    cfg = sut.Config(project_name="test",
        project_version="0.0.0",
        autocreate=True,
        dtrack_baseurl="https://localhost",
        dtrack_apikey="apikey"
        )
    Args = namedtuple("Args", [
        "config",
        "bom_file"
    ])
    args = Args(
        config=None,
        bom_file=lazy_datadir / "test_action.bom.json"
    )
    result = sut.action(cfg, args)
    assert result == 0
    mock_put_bom.assert_called_once()
