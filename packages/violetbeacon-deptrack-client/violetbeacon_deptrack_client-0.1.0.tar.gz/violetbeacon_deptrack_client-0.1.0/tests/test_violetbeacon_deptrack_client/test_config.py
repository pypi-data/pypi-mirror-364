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
from os import environ

import pytest

import violetbeacon_deptrack_client.config as sut

def test_config_model_dump():
    """Test Config"""
    cfg = sut.Config(
        project_name="abcd",
        project_version="1.2.3",
        autocreate=True,
        dtrack_baseurl="myurl",
        dtrack_apikey="apikey"
    )
    assert cfg.model_dump() == {
        "project_name": "abcd",
        "project_version": "1.2.3",
        "autocreate": True,
        "dtrack_baseurl": "myurl",
        "dtrack_apikey": "apikey"
    }

def test_config_get_dtrack_baseurl_str():
    """Test Config.get_dtrack_baseurl()"""
    cfg = sut.Config(
        project_name="abcd",
        project_version="1.2.3",
        autocreate=True,
        dtrack_baseurl="myurl",
        dtrack_apikey="apikey"
    )
    assert cfg.get_dtrack_baseurl() == "myurl"

def test_config_get_dtrack_baseurl_env():
    """Test Config.get_dtrack_baseurl()"""
    environ["MYURL"] = "xyz"
    cfg = sut.Config(
        project_name="abcd",
        project_version="1.2.3",
        autocreate=True,
        dtrack_baseurl="env:MYURL",
        dtrack_apikey="apikey"
    )
    assert cfg.get_dtrack_baseurl() == "xyz"

def test_config_get_dtrack_baseurl_env_invalid():
    """Test Config.get_dtrack_baseurl()"""
    cfg = sut.Config(
        project_name="abcd",
        project_version="1.2.3",
        autocreate=True,
        dtrack_baseurl="env:JIWJFIPFIOPEWF",
        dtrack_apikey="apikey"
    )
    with pytest.raises(ValueError):
        cfg.get_dtrack_baseurl()

def test_config_get_dtrack_apikey_str():
    """Test Config.get_dtrack_apikey()"""
    cfg = sut.Config(
        project_name="abcd",
        project_version="1.2.3",
        autocreate=True,
        dtrack_baseurl="myurl",
        dtrack_apikey="apikey"
    )
    assert cfg.get_dtrack_apikey() == "apikey"

def test_config_get_dtrack_apikey_env():
    """Test Config.get_dtrack_apikey()"""
    environ["MYAPIKEY"] = "xyz"
    cfg = sut.Config(
        project_name="abcd",
        project_version="1.2.3",
        autocreate=True,
        dtrack_baseurl="myurl",
        dtrack_apikey="env:MYAPIKEY"
    )
    assert cfg.get_dtrack_apikey() == "xyz"

def test_config_get_dtrack_apikey_env_invalid():
    """Test Config.get_dtrack_apikey()"""
    cfg = sut.Config(
        project_name="abcd",
        project_version="1.2.3",
        autocreate=True,
        dtrack_baseurl="myurl",
        dtrack_apikey="env:QJIOFFJOPJPWFWE"
    )
    with pytest.raises(ValueError):
        cfg.get_dtrack_apikey()

def test_load_config(lazy_datadir):
    """Test load_config()"""
    cfg = sut.load_config(lazy_datadir / "deptrack-client.yaml")
    assert cfg.autocreate is False
    assert cfg.dtrack_apikey == "env:DTRACK_APIKEY"
    assert cfg.dtrack_baseurl == "env:DTRACK_BASEURL"
    assert cfg.project_name == "violetbeacon-deptrack-client"
    assert cfg.project_version == "0.1.0"

def test_load_config_invalid(lazy_datadir):
    """Test load_config()"""
    with pytest.raises(sut.ValidationError):
        sut.load_config(lazy_datadir / "deptrack-client-invalid.yaml")
