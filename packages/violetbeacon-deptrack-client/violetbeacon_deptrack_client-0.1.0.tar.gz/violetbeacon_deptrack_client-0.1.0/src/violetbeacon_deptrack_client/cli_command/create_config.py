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
from argparse import _SubParsersAction
from pathlib import Path
import logging
from typing import Any

from yaml import safe_dump

from ..params import add_generic_params
from ..config import Config

logger = logging.getLogger(__name__)

def build_subparser(subparsers: _SubParsersAction):
    """Build subparser for create-config"""
    parser = subparsers.add_parser("create-config", help="Create configuration file")
    add_generic_params(parser, config_required=True)
    parser.add_argument(
        "-a", "--autocreate", action="store_true", default=False,
        help="Tell Dependency-Track to autocreate the project if it does not exist")
    parser.add_argument(
        "-p", "--project-name", type=str, required=True, help="Project name")
    parser.add_argument(
        "-q", "--project-version", type=str, required=True, help="Project ID")
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
    """Handle the create-config action"""
    if Path(args.config).exists():
        logger.fatal("Config file already exists. Refusing to overwrite it.")
        raise FileExistsError("Config file already exists. Refusing to overwrite it.")
    logger.debug("Dumping data to config file")
    with open(args.config, "w", encoding="utf-8") as fh:
        safe_dump(cfg.model_dump(), fh)
    return 0
