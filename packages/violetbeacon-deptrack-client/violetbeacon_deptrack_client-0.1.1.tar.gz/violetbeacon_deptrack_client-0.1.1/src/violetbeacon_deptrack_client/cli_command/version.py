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
import logging
from importlib.metadata import version
from typing import Any

from ..config import Config

logger = logging.getLogger(__name__)

def build_subparser(subparsers: _SubParsersAction):
    """Build subparser for version"""
    parser = subparsers.add_parser("version", help="Print version information")
    parser.set_defaults(init_func=init)
    parser.set_defaults(func=action)

def init(cfg: Config, args: Any):
    """Override config with command-line options.
    No actions necessary
    """
    _ = (cfg, args)  # arguments are unused but required for API compatibility

def action(cfg: Config, args: Any) -> int:
    """Handle the version action"""
    _ = (cfg, args)  # arguments are unused but required for API compatibility
    print(version('violetbeacon_deptrack_client'))
    return 0
