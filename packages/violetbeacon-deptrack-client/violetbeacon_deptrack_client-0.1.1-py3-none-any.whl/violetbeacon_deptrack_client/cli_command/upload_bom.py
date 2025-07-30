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
from argparse import _SubParsersAction
from typing import Any

from ..params import add_generic_params
from ..config import Config
from ..dependency_track import api

logger = logging.getLogger(__name__)

def build_subparser(subparsers: _SubParsersAction):
    """Build subparser for upload-bom"""
    parser = subparsers.add_parser("upload-bom", help="Upload BOM")
    add_generic_params(parser)
    parser.add_argument(
        "-a", "--autocreate", action="store_true", default=False,
        help="Autocreate the project if it does not exist")
    parser.add_argument(
        "-p", "--project-name", type=str, required=True, help="Project name")
    parser.add_argument(
        "-q", "--project-version", type=str, required=True, help="Project ID")
    parser.add_argument(
        "-f", "--bom-file", type=str, required=True, help="Path to BOM file")
    parser.set_defaults(init_func=init)
    parser.set_defaults(func=action)

def init(cfg: Config, args: Any):
    """Override config with command-line options.
    This section is purposely excluded from pylint R0801
    since the arguments are explicitly relevant to this cli command
    """
    # pylint: disable=duplicate-code
    cfg.project_name = args.project_name
    cfg.project_version = args.project_version
    cfg.autocreate = args.autocreate
    cfg.dtrack_baseurl = args.dtrack_baseurl
    cfg.dtrack_apikey = args.api_key
    # pylint: enable=duplicate-code

def action(cfg: Config, args: Any) -> int:
    """Handle the upload-bom action"""
    # Resolve the host if the value it starts with `env:`
    data = api.PutBomData(
        base_url=cfg.get_dtrack_baseurl(),
        api_key=cfg.get_dtrack_apikey(),
        project_name=cfg.project_name,
        project_version=cfg.project_version,
        autocreate=cfg.autocreate,
        bom_filepath=args.bom_file,
    )
    api.put_bom(data)
    print("BOM uploaded successfully")
    return 0
