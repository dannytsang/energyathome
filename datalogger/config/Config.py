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

import configparser as configParser
import logging
import logging.config
import os


class ConfigManager:
    """Load and stores configuration values."""
    PARSER = None

    _CONFIG_DIR = ""

    def __init__(self):

        self._LOGGER = logging.getLogger(__name__)
        self.CONFIG_FILENAME = "energyathome.ini"
        # Instantiate logging
        log_config_path = os.path.dirname(__file__) + os.sep + self.CONFIG_FILENAME
        self._LOGGER.debug(log_config_path)

        try:
            # Get the parent directory of this file and append the config file name
            self._CONFIG_DIR = os.path.dirname(__file__)
            # If there is no parent directory then do not add a file path separator
            if os.path.dirname(__file__) != "":
                self._CONFIG_DIR += os.sep
            self._CONFIG_DIR += self.CONFIG_FILENAME

            # Initialized config parser
            self.PARSER = configParser.ConfigParser(defaults=None)
            # Config file is required. Get Config.py file directory location
            self.PARSER.read_file(open(self._CONFIG_DIR))

        except IOError as ie:
            self._LOGGER.error("Config File '" + self._CONFIG_DIR + "' not found")
            self._LOGGER.error("Details: " + str(ie.args))

    def get_config_file_path(self):
        """Returns the absolute path to the config file being used"""

        return self._CONFIG_DIR

    def get_config(self, category, key):
        """category = section of the config e.g Database, Twitter, etc
        key = the name of the configuration item e.g username, password"""

        try:
            # Ensure PARSER object has been instantiated
            if self.PARSER is not None:
                # Return value
                return self.PARSER.get(category, key)
            else:
                self._LOGGER.error("Error: PARSER has not been instantiated")
                return None

        except configParser.NoSectionError as nse:
            self._LOGGER.error("No configuration category of '" + str(category) + "' was found.")
            return None
        except configParser.NoOptionError as nse:
            self._LOGGER.error("No configuration '" + key + "' was found in '" + str(category) + "'category.")
            return None

        except ValueError as ve:
            self._LOGGER.error("Configuration '" + key + "' in '" + str(category) + "' has an invalid value.")
            self._LOGGER.error(str(ve))
            return None

    def get_int_config(self, category, key):
        """category = section of the config e.g Database, Twitter, etc
        key = the name of the configuration item e.g username, password"""

        try:
            # Ensure PARSER object has been instantiated
            if self.PARSER is not None:
                # Return value
                return self.PARSER.getint(category, key)
            else:
                self._LOGGER.error("Error: PARSER has not been instantiated")
                return None

        except configParser.NoSectionError as nse:
            self._LOGGER.error("No configuration category of '" + str(category) + "' was found.")
            return None
        except configParser.NoOptionError as nse:
            self._LOGGER.error("No configuration '" + key + "' was found in '" + str(category) + "'category.")
            return None
        except ValueError as ve:
            self._LOGGER.error("Configuration '" + key + "' in '" + str(category) + "' has an invalid value.")
            self._LOGGER.error(str(ve))
            return None

    def get_float_config(self, category, key):
        """category = section of the config e.g Database, Twitter, etc
        key = the name of the configuration item e.g username, password"""

        try:
            # Ensure PARSER object has been instantiated
            if self.PARSER is not None:
                # Return value
                return self.PARSER.getfloat(category, key)
            else:
                self._LOGGER.error("Error: PARSER has not been instantiated")
                return None

        except configParser.NoSectionError as nse:
            self._LOGGER.error("No configuration category of '" + str(category) + "' was found.")
            return None
        except configParser.NoOptionError as nse:
            self._LOGGER.error("No configuration '" + key + "' was found in '" + str(category) + "'category.")
            return None
        except ValueError as ve:
            self._LOGGER.error("Configuration '" + key + "' in '" + str(category) + "' has an invalid value.")
            self._LOGGER.error(str(ve))
            return None

    def get_boolean_config(self, category, key):
        """category = section of the config e.g Database, Twitter, etc
        key = the name of the configuration item e.g username, password"""

        try:
            # Ensure PARSER object has been instantiated
            if self.PARSER is not None:
                # Return value
                return self.PARSER.getboolean(category, key)
            else:
                self._LOGGER.error("Error: PARSER has not been instantiated")
                return None

        except configParser.NoSectionError as nse:
            self._LOGGER.error("No configuration category of '" + str(category) + "' was found.")
            return None
        except configParser.NoOptionError as nse:
            self._LOGGER.error("No configuration '" + key + "' was found in '" + str(category) + "'category.")
            return None
        except ValueError as ve:
            self._LOGGER.error("Configuration '" + key + "' in '" + str(category) + "' has an invalid value.")
            self._LOGGER.error(str(ve))
            return None

    def get_list_config(self, category, key):
        """Returns a config item which is comma separated into a list"""

        value = self.get_config(category, key)

        if value is not None and len(value) > 0:
            return value.split(",")

        else:
            return None

    def set_config(self, category, key, value):
        """Expects an instance of a defined class below"""

    def get_config_category(self, category):
        """category = section of the config e.g Database, Twitter, etc
        returns: dictionary of all the settings."""

        try:
            # Ensure PARSER object has been instantiated
            if self.PARSER is not None:
                all_config = self.PARSER._sections

                # Return value
                if category in all_config:
                    return all_config[category]
                else:
                    return None
            else:
                self._LOGGER.error("Error: PARSER has not been instantiated")
                return None
        except configParser.NoSectionError as nse:
            self._LOGGER.error("No configuration category of '" + str(category) + "' was found.")
            return None
        except configParser.NoOptionError as nse:
            self._LOGGER.error("No configuration '" + category + "' was found in '" + str(category) + "'category.")
            return None
        except ValueError as ve:
            self._LOGGER.error("Configuration '" + category + "' in '" + str(category) + "' has an invalid value.")
            self._LOGGER.error(str(ve))
            return None
