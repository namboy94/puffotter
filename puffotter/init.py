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
from typing import Callable, Optional, Union
from argparse import ArgumentParser, Namespace
from argcomplete import autocomplete


def cli_start(
        main_func: Union[
            Callable[[], None],
            Callable[[Namespace], None],
            Callable[[Namespace, logging.Logger], None]
        ],
        arg_parser: ArgumentParser,
        exit_msg: str = "Goodbye",
        package_name: Optional[str] = None,
        sentry_dsn: Optional[str] = None,
        release_name: Optional[str] = None
):
    """
    Starts a program and sets up logging, as well as sentry error tracking
    :param main_func: The main function to call
    :param arg_parser: The argument parser to use
    :param exit_msg: The message printed when the program's execution is
                     stopped using a keyboard interrupt
    :param package_name: The package name of the application
    :param sentry_dsn: The sentry DSN to use
    :param release_name: The name of the release
    :return: None
    """
    try:
        autocomplete(arg_parser)
        args = arg_parser.parse_args()

        if "quiet" in args and args.quiet:
            loglevel = logging.ERROR
        elif "verbose" in args and args.verbose:
            loglevel = logging.INFO
        elif "debug" in args and args.debug:
            loglevel = logging.DEBUG
        else:
            loglevel = logging.WARNING

        logging.basicConfig(level=loglevel)

        if release_name is None:
            if package_name is not None:
                import pkg_resources
                version = pkg_resources.get_distribution(package_name).version
                release_name = package_name + "-" + version
            else:
                release_name = "Unknown"
                package_name = "unknown"

        if sentry_dsn is not None:
            import sentry_sdk
            sentry_sdk.init(sentry_dsn, release=release_name)

        from inspect import signature
        sign = signature(main_func)
        if len(sign.parameters) == 0:
            main_func()
        elif len(sign.parameters) == 1:
            main_func(args)
        elif len(sign.parameters) == 2:
            logger = logging.getLogger(package_name)
            main_func(args, logger)
        else:
            print("Invalid amount of parameters for main function")
    except KeyboardInterrupt:
        print(exit_msg)


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
