"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of puffotter.

puffotter is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

puffotter is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with puffotter.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import logging
import pkg_resources
import sentry_sdk
from typing import Callable, Optional
from argparse import ArgumentParser


def cli_start(
        main_func: Callable,
        logging_error: bool = False,
        logging_warning: bool = False,
        logging_info: bool = False,
        logging_debug: bool = False,
        package_name: Optional[str] = None,
        sentry_dsn: Optional[str] = None,
        release_name: Optional[str] = None,
):
    """
    Starts a program and sets up loggign, as well as sentry error tracking
    :param main_func: The main function to call
    :param logging_error: Sets the logging level to error
    :param logging_warning: Sets the logging level to warning
    :param logging_info: Sets the logging level to info
    :param logging_debug: Sets the logging level to debug
    :param package_name: The package name of the application
    :param sentry_dsn: The sentry DSN to use
    :param release_name: The name of the release
    :return: None
    """
    try:
        loglevel = logging.WARNING
        if logging_error:
            loglevel = logging.ERROR
        if logging_warning:
            loglevel = logging.WARNING
        if logging_info:
            loglevel = logging.INFO
        if logging_debug:
            loglevel = logging.DEBUG
        logging.basicConfig(level=loglevel)

        version = pkg_resources.get_distribution(package_name).version
        if sentry_dsn is not None:
            if release_name is None:
                if package_name is not None:
                    release_name = package_name + "-" + version
                else:
                    release_name = "Unknown"

            sentry_sdk.init(sentry_dsn, release=release_name)

        main_func()
    except KeyboardInterrupt:
        pass


def argparse_add_verbosity(parser: ArgumentParser):
    """
    Adds --quiet, --verbose and --debug parameters to an ArgumentParser
    :param parser: the parser to which to add those flags
    :return: None
    """
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Sets the verbosity level of the program to "
                             "'quiet'")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Sets the verbosity level of the program to "
                             "'verbose'")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Sets the verbosity level of the program to "
                             "'debug'")