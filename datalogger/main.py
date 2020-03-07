#!/usr/bin/python

#
#	This file is part of Energy@Home.
#	Copyright (C) 2009 Danny Tsang
#	
#	This file is part of Energy@Home.
#	
#	Energy@Home is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#	
#	Energy@Home is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with Energy@Home.  If not, see <http://www.gnu.org/licenses/>.
#

__author__ = 'Danny Tsang <danny@dannytsang.co.uk>'

import sys
import logging

import core

# Instantiate Logger
_LOGGER = logging.getLogger(__name__)


def main():
    """Main function which starts the program"""

    _LOGGER.info("Starting energy@home")

    try:
        # initialise
        core.init()

        while True:
            # Capture and store data
            core.run()
    # Catch ctrl+c
    except KeyboardInterrupt:
        _LOGGER.info("Caught keyboard interrupt")
        core.shutdown()


if __name__ == "__main__":
    sys.exit(main())
