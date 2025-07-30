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
from os import environ

from yaml import safe_load
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class Config(BaseModel):
    """Config data"""
    project_name: str = ""
    project_version: str = ""
    autocreate: bool = False
    dtrack_baseurl: str = "env:DTRACK_BASEURL"
    dtrack_apikey: str = "env:DTRACK_APIKEY"

    def get_dtrack_baseurl(self) -> str:
        """Parse dtrack_baseurl and return the relevant result (env variable value if value
        starts with `env:` or directly stored value)"""
        base_url = self.dtrack_baseurl
        if base_url.lower().startswith("env:"):
            logger.debug("Retrieving environment variable for dtrack_baseurl %s", base_url)
            base_url = environ.get(base_url[base_url.find(":")+1:], "")
        if base_url == "":
            raise ValueError(
                f"dtrack_baseurl [{base_url}] is not a valid value. The DTRACK_BASEURL " \
                f"environment variable must be set or the -H parameter is required.")
        return base_url

    def get_dtrack_apikey(self) -> str:
        """Parse dtrack_apikey and return the relevant result (env variable value if value
        starts with `env:` or directly stored value)"""
        api_key = self.dtrack_apikey
        if api_key.lower().startswith("env:"):
            logger.debug("Retrieving environment variable for api_key %s", api_key)
            api_key = environ.get(api_key[api_key.find(":")+1:], "")
        if api_key == "":
            raise ValueError(
                f"dtrack_apikey [{api_key}] is not a valid value. . The DTRACK_APIKEY " \
                f"environment variable must be set or the -A parameter is required.")
        return api_key

def load_config(file_path: str) -> Config:
    """Load configuration file and return populated Config object"""
    config_obj = None
    with open(file_path, encoding="utf-8") as fh:
        config = safe_load(fh)
    try:
        config_obj = Config(**config)
    except ValidationError as e:
        logger.fatal("config file failed validation", exc_info=True)
        raise e
    return config_obj
