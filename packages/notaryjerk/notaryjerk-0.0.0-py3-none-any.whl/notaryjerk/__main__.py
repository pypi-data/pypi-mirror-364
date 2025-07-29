#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# notaryjerk -tools for codesigning, notarization,...
#
# Copyright © 2023, IOhannes m zmölnig, forum::für::umläute
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Main entry point"""

import logging

log = logging.getLogger("notaryjerk")
logging.basicConfig()

from . import notarize
from . import staple


def _verbosity_test(args):
    print("verbosity: %d (loglevel: %d)" % (args.verbosity, log.level))
    log.fatal("FATAL[%d]" % (logging.FATAL,))
    log.error("ERROR[%d]" % (logging.ERROR,))
    log.warning("WARNING[%d]" % (logging.WARNING,))
    log.info("INFO[%d]" % (logging.INFO,))
    log.debug("DEBUG[%d]" % (logging.DEBUG,))


def _main():
    import argparse

    parser_args = {
        "description": "Notarization toolkit",
    }
    if __name__ == "__main__":
        import os
        import sys

        pkg = __package__ or "notaryjerk"
        parser_args["prog"] = "%s -m %s" % (os.path.basename(sys.executable), pkg)

    parser = argparse.ArgumentParser(**parser_args)

    parser.set_defaults(func=None)

    group = parser.add_argument_group("verbosity")
    group.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="raise verbosity (can be given multiple times)",
    )
    group.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="lower verbosity (can be given multiple times)",
    )

    subparsers = parser.add_subparsers()

    parser_v = subparsers.add_parser("verbosity-test", help="run a verbosity test")
    parser_v.set_defaults(func=_verbosity_test)

    notarize._subArgparser(
        subparsers.add_parser("notarize", help="submit a container for notarization")
    )
    staple._subArgparser(
        subparsers.add_parser("staple", help="staple notarization ticket within bundle")
    )

    args = parser.parse_args()
    # verbosity handling
    args.verbosity = 0 + args.verbose - args.quiet
    del args.verbose
    del args.quiet
    loglevel = logging.WARNING - (10 * args.verbosity)
    if loglevel < 1:
        loglevel = 1
    log.setLevel(loglevel)

    if args.func is None:
        parser.error("no sub-command given")

    args.func(args)


if __name__ == "__main__":
    args = _main()
