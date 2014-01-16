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

try:
    import ConfigParser as configParser
except:
    import configparser as configParser
    
import os
import logging, logging.config

class ConfigManager:
    '''Load and stores configuration values.'''
    PARSER = None
    
    CONFIG_DIR = ""
    
    def __init__(self):
        
        global CONFIG_DIR
        
        self.CONFIG_FILENAME = "energyathome.ini"
        
        # Instantiate logging
        logConfigPath = os.path.dirname(__file__) + os.sep + "energyathome.ini"
        print logConfigPath
        logging.config.fileConfig(logConfigPath)
        self.LOGGER = logging.getLogger("energyathome.datalogger.config.config")
        
        try:
            # Get the parent directory of this file and append the config file name
            CONFIG_DIR = os.path.dirname(__file__)
            # If there is no parent directory then do not add a file path separator
            if(os.path.dirname(__file__) != ""):
                CONFIG_DIR += os.sep
            CONFIG_DIR += self.CONFIG_FILENAME
            
            # Initialized config parser
            self.PARSER = configParser.SafeConfigParser(defaults = None)
            # Config file is required. Get Config.py file directory location
            self.PARSER.readfp(open(CONFIG_DIR))
            
        except(IOError), ie:
            self.LOGGER.error("Config File '" + CONFIG_DIR + "' not found")
            self.LOGGER.error("Details: " + str(ie.args))

    def getConfigFilePath(self):
        ''' Returns the absolute path to the config file being used'''
        
        global CONFIG_DIR
        
        return CONFIG_DIR

    def getConfig(self, category, key):
        '''category = section of the config e.g Database, Twitter, etc
        key = the name of the configuration item e.g username, password'''
        
        try:
            # Ensure PARSER object has been instantiated
            if self.PARSER is not None:
                # Return value
                return self.PARSER.get(category, key)
            else:
                self.LOGGER.error("Error: PARSER has not been instantiated")
                return None
            
        except(configParser.NoSectionError), nse:
            self.LOGGER.error("No configuration category of '" + str(category) + "' was found.")
            return None
        
        except(configParser.NoOptionError), nse:
            self.LOGGER.error("No configuration '" + key + "' was found in '" + str(category) + "'category.")
            return None
        
        except ValueError as ve:
            self.LOGGER.error("Configuration '" + key + "' in '" + str(category) + "' has an invalid value.")
            self.LOGGER.error(str(ve))
            return None
    
    def getIntConfig(self, category, key):
        '''category = section of the config e.g Database, Twitter, etc
        key = the name of the configuration item e.g username, password'''
        
        try:
            # Ensure PARSER object has been instantiated
            if self.PARSER is not None:
                # Return value
                return self.PARSER.getint(category, key)
            else:
                self.LOGGER.error("Error: PARSER has not been instantiated")
                return None
            
        except(configParser.NoSectionError), nse:
            self.LOGGER.error("No configuration category of '" + str(category) + "' was found.")
            return None
        
        except(configParser.NoOptionError), nse:
            self.LOGGER.error("No configuration '" + key + "' was found in '" + str(category) + "'category.")
            return None
        
        except ValueError as ve:
            self.LOGGER.error("Configuration '" + key + "' in '" + str(category) + "' has an invalid value.")
            self.LOGGER.error(str(ve))
            return None
    
    def getFloatConfig(self, category, key):
        '''category = section of the config e.g Database, Twitter, etc
        key = the name of the configuration item e.g username, password'''
        
        try:
            # Ensure PARSER object has been instantiated
            if self.PARSER is not None:
                # Return value
                return self.PARSER.getfloat(category, key)
            else:
                self.LOGGER.error("Error: PARSER has not been instantiated")
                return None
            
        except(configParser.NoSectionError), nse:
            self.LOGGER.error("No configuration category of '" + str(category) + "' was found.")
            return None
        
        except(configParser.NoOptionError), nse:
            self.LOGGER.error("No configuration '" + key + "' was found in '" + str(category) + "'category.")
            return None
        
        except ValueError as ve:
            self.LOGGER.error("Configuration '" + key + "' in '" + str(category) + "' has an invalid value.")
            self.LOGGER.error(str(ve))
            return None
    
    def getBooleanConfig(self, category, key):
        '''category = section of the config e.g Database, Twitter, etc
        key = the name of the configuration item e.g username, password'''
        
        try:
            # Ensure PARSER object has been instantiated
            if self.PARSER is not None:
                # Return value
                return self.PARSER.getboolean(category, key)
            else:
                self.LOGGER.error("Error: PARSER has not been instantiated")
                return None
            
        except(configParser.NoSectionError), nse:
            self.LOGGER.error("No configuration category of '" + str(category) + "' was found.")
            return None
        
        except(configParser.NoOptionError), nse:
            self.LOGGER.error("No configuration '" + key + "' was found in '" + str(category) + "'category.")
            return None
        
        except ValueError as ve:
            self.LOGGER.error("Configuration '" + key + "' in '" + str(category) + "' has an invalid value.")
            self.LOGGER.error(str(ve))
            return None
        
    def getListConfig(self, category, key):
        '''Returns a config item which is comma separated into a list'''
        
        value = self.getConfig(category, key)
        
        if value is not None and len(value) > 0:
            return value.split(",")
        
        else:
            return None
    
    def setConfig(self, category, key, value):
        '''Expects an instance of a defined class below'''
        
    def getConfigCategory(self, category):
        '''category = section of the config e.g Database, Twitter, etc
        returns: dictionary of all the settings.'''
        
        try:
            # Ensure PARSER object has been instantiated
            if self.PARSER is not None:
                allConfig = self.PARSER._sections
                
                # Return value
                if(category in allConfig):
                    return allConfig[category]
                else:
                    return None
            else:
                self.LOGGER.error("Error: PARSER has not been instantiated")
                return None
        except(configParser.NoSectionError), nse:
            self.LOGGER.error("No configuration category of '" + str(category) + "' was found.")
            return None
        
        except(configParser.NoOptionError), nse:
            self.LOGGER.error("No configuration '" + key + "' was found in '" + str(category) + "'category.")
            return None
        
        except ValueError as ve:
            self.LOGGER.error("Configuration '" + key + "' in '" + str(category) + "' has an invalid value.")
            self.LOGGER.error(str(ve))
            return None
