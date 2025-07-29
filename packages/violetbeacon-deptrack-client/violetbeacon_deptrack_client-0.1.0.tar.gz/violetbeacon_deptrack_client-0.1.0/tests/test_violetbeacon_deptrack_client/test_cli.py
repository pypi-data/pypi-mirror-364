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
import logging
from unittest.mock import patch

import pytest

import violetbeacon_deptrack_client.cli as sut

def test_main():
    """Test main()"""
    with pytest.raises(SystemExit) as e_info:
        sut.main(["-h"])
    assert e_info.value.code == 0

def test_version():
    """Test main() with a simple, stable command"""
    assert sut.main(["version"]) == 0

@patch('violetbeacon_deptrack_client.cli_command.version.action',
       side_effect=Exception("Unhandled exception"))
def test_version_unhandled_exception(mock_action):
    """Test main()
    mock_action is just used to inject an Exception
    """
    _ = mock_action  # mock_action is intentionally unused. Quash the pylint warning.
    result = sut.main(["version"])
    assert result == 127

def test_build_arg_parser():
    """Test build_arg_parser()"""
    parser = sut.build_arg_parser()
    assert isinstance(parser, sut.ArgumentParser)

def test_configure_logger():
    """Test configure_logger()"""
    logger = logging.getLogger(__name__)
    sut.configure_logger(0)
    assert logger.getEffectiveLevel() == logging.WARNING
    sut.configure_logger(1)
    assert logger.getEffectiveLevel() == logging.INFO
    sut.configure_logger(2)
    assert logger.getEffectiveLevel() == logging.DEBUG
    sut.configure_logger(3)
    assert logger.getEffectiveLevel() == logging.NOTSET
