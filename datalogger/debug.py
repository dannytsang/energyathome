#
#	This file is part of Energy@Home.
#	Copyright (C) 2011 Danny Tsang
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

import sys, os
import logging, logging.config

from config.Config import ConfigManager

# Configuration Manager
CONFIG = ConfigManager()

def getLogger(moduleName):
    '''Lazy instantiation of logger'''
    
    global CONFIG
    
    print CONFIG.getConfigFilePath()
    logging.config.fileConfig(CONFIG.getConfigFilePath())
    logger = logging.getLogger(moduleName)
    
    return logger
