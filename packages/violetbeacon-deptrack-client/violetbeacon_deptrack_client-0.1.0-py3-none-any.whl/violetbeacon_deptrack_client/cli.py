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
from argparse import ArgumentParser

from . import config
from .cli_command import create_config
from .cli_command import upload_bom
from .cli_command import version

logger = logging.getLogger(__name__)

DEFAULT_V = 0

def main(argv=None) -> int:
    """Entrypoint for CLI"""
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    configure_logger(args.v if 'v' in args else DEFAULT_V)
    logger.debug("args: %s", args)

    cfg = config.Config()
    if 'config' in args:
        cfg = config.load_config(args.config)

    try:
        args.init_func(cfg, args)
        result = args.func(cfg, args)
    except Exception:  # pylint: disable=broad-except
        # Allow broad exception since we're logging and exiting the program
        logger.fatal("Exception thrown", exc_info=True)
        return 127
    return result

def build_arg_parser() -> ArgumentParser:
    """Create parser"""
    parser = ArgumentParser(description="Dependency-Track Client")
    subparsers = parser.add_subparsers(help="Commands")

    create_config.build_subparser(subparsers)
    upload_bom.build_subparser(subparsers)
    version.build_subparser(subparsers)

    return parser

def configure_logger(level: int):
    """Configure logger based on the provided level"""
    log_levels = [logging.WARNING, logging.INFO, logging.DEBUG, logging.NOTSET]
    logging_level = log_levels[min(level, len(log_levels)-1)]
    logging.basicConfig(level=log_levels[min(level, len(log_levels)-1)])
    logging.getLogger().setLevel(logging_level)
