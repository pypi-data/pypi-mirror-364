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
import pytest

import violetbeacon_deptrack_client.config as vbcc

@pytest.fixture
def config_fixture():
    """Returns populated Config"""
    return vbcc.Config(
        project_name="test",
        project_version="0.0.0",
        autocreate=True,
        dtrack_baseurl="http://localhost",
        dtrack_apikey="apikey"
    )
