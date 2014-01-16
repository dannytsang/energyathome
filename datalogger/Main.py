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

import Debug
import Core

# Instantiate Logger
LOGGER = Debug.getLogger("energyathome.datalogger.main")

def main():
    """Main function which starts the program"""
    
    global LOGGER
    
    LOGGER.info("Starting energy@home")
    
    try:
        # initialise
        Core.init()
        
        while True:
            # Capture and store data
            Core.run()
    # Catch ctrl+c
    except KeyboardInterrupt:
        LOGGER.info("Caught keyboard interrupt")
        Core.shutdown()
    
if __name__ == "__main__":
    sys.exit(main())
