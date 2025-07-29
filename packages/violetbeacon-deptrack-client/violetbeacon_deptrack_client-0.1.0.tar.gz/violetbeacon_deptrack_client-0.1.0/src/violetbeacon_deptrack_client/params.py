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

def add_generic_params(parser: ArgumentParser, config_required=False):
    """Add params that are relevant to all CLI actions"""
    parser.add_argument(
        "-v", action="count", default=0,
        help="Increase logging verbosity. Can be provided multiple times.")
    parser.add_argument(
        "-c", "--config", type=str, required=config_required,
        default="deptrack-client.yaml",
        help="Path to configuration file. Default: %(default)s")
    parser.add_argument(
        "-H", "--dtrack-baseurl", type=str, default="env:DTRACK_BASEURL",
        help="Base URL of Dependency-Track API instance (excluding /api/v1/...). " \
        "If prefixed with `env:` this is the name of the environment variable which " \
        "contains the hostname. Default=%(default)s")
    parser.add_argument(
        "-A", "--api-key", type=str, default="env:DTRACK_APIKEY",
        help="API key for the Dependency-Track API. " \
        "If prefixed with `env:` this is the name of the environment variable which " \
        "contains the API key. Default=%(default)s")
