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
from unittest.mock import patch

import pytest

import violetbeacon_deptrack_client.dependency_track.api as sut

@patch('violetbeacon_deptrack_client.dependency_track.api.put')
def test_put_bom(mock_put, lazy_datadir):
    """test put_bom()"""
    data = sut.PutBomData(
        base_url="http://localhost",
        api_key="apikey",
        project_name="name",
        project_version="0.0.0",
        autocreate=True,
        bom_filepath=lazy_datadir / "test_put_bom.bom.json"
    )
    sut.put_bom(data)
    mock_put.assert_called_once()

def test_put_bom_file_not_exist():
    """test put_bom()"""
    data = sut.PutBomData(
        base_url="http://localhost",
        api_key="apikey",
        project_name="name",
        project_version="0.0.0",
        autocreate=True,
        bom_filepath="nofile.json"
    )
    with pytest.raises(FileNotFoundError):
        sut.put_bom(data)

# Note: the patches apply in inner-to-outer order
@patch('violetbeacon_deptrack_client.dependency_track.api.put')
@patch('requests.Response')
def test_put_bom_returns_error(mock_response, mock_put, lazy_datadir):
    """test put_bom()"""
    data = sut.PutBomData(
        base_url="http://localhost",
        api_key="apikey",
        project_name="name",
        project_version="0.0.0",
        autocreate=True,
        bom_filepath=lazy_datadir / "test_put_bom.bom.json"
    )

    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.reason = "Error"
    mock_response.content = "Error"

    mock_put.return_value = mock_response

    with pytest.raises(RuntimeError):
        sut.put_bom(data)
    mock_put.assert_called_once()
