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

import os
import core
import logging

import pickle

import historical_data
from config.Config import ConfigManager
from data_validation import CheckLiveData
from data_trigger import CheckLiveTriggers

_LOGGER = logging.getLogger(__name__)


class BackupRestore:

    def __init__(self):
        # Configuration Manager
        self.CONFIG = ConfigManager()
        # Data validation class
        self.VALIDATOR = CheckLiveData()
        # Data trigger class
        self.TRIGGER = CheckLiveTriggers()

    def backup(self, historical_data):
        """Writes historical data to file"""

        # If true exit due to exception
        exit = False
        # Get file path from config
        location = self.CONFIG.get_config("Application", "offlineFile")
        # Check if config is empty
        if len(location) == 0:
            # Use current directory
            location = os.path.join(os.getcwd(), "backup.p")
            _LOGGER.warning("offlineFile is empty. Using default: '" + location + "'")

        try:
            # Append to file
            path = file(location, "a")

            # Ensure object has data
            if historical_data is not None:
                _LOGGER.info("Writing data to file:" + str(historical_data.__dict__))
                pickle.dump(historical_data, path)
        except IOError:
            # Debug.writeOut("Unable to write to backup file: '" + location + "'")
            # No point running program if it's unable to write to file
            exit = True
        finally:
            # Close file
            try:
                path.close()
            except UnboundLocalError:
                # File was not opened
                pass
        # Check to exit
        if exit:
            core.shutdown()

    def restore(self):
        """Starts the restore process from a file."""

        backup = self.restore_from_file()
        record_count = len(backup)

        if record_count > 0:
            _LOGGER.info(str(record_count) + " record(s) found. Saving to DB")
            for record in backup:
                # Set data as valid by default
                h_data_valid = True
                # Get backup record
                h_data = record

                if self.VALIDATOR is not None and self.CONFIG.get_boolean_config("Tolerence", "enabled"):
                    try:
                        validatedData = self.VALIDATOR.validate_data(h_data)
                    except Exception as e:
                        raise e

                    h_data_valid = validatedData[0]
                    if h_data_valid is True:
                        h_data = validatedData[1]

                if h_data_valid and self.CONFIG.get_boolean_config("Trigger", "enabled"):
                    # Check trigger conditions which return true or false if it's valid
                    try:
                        h_data_valid = self.TRIGGER.check_triggers(h_data)
                    except Exception as e:
                        raise e

                # Insert the first element in list and remove it
                if h_data_valid:
                    _LOGGER.info("Inserting: " + str(record.__dict__))
                    # HistoricalData.insert_data(record)
                    historical_data.insert_data(h_data)
                else:
                    _LOGGER.info("Skipped backup record")

            # Remove backup file to prevent duplicate data from being restored.
            _LOGGER.info("Restore from backup complete.")
            _LOGGER.info("Removing backup file.")
            _LOGGER.info("File deleted? " + str(self.delete_backup_file()))

    def restore_from_file(self):
        """Reads a file and returns an array of objects."""

        # List to store restored objects
        file_list = []
        # Get file path from config
        location = self.CONFIG.get_config("Application", "offlineFile")
        # Check if config is empty
        if len(location) == 0:
            # Use current directory
            location = os.path.join(os.getcwd(), "backup.p")
            _LOGGER.info("offlineFile is empty. Using default: '" + location + "'")
        # Check file exists before deleting
        if os.path.exists(location):
            # Create file object
            path = file(location, "r")
            # Read file till end of file
            try:
                while True:
                    file_list.append(pickle.load(path))
            except EOFError:
                # Ignore end of file error
                pass
            finally:
                # Close file
                path.close()

        _LOGGER.info("Found " + str(len(file_list)) + " record(s) in '" + location + "'")
        return file_list

    def delete_backup_file(self):
        """Removed backup file if it exists."""

        success = False

        # Get file path from config
        location = self.CONFIG.get_config("Application", "offlineFile")
        # Check if config is empty
        if len(location) == 0:
            # Use current directory
            location = os.path.join(os.getcwd(), "backup.p")
            _LOGGER.info("offlineFile is empty. Using default: '" + location + "'")
        # Check file exists before deleting
        if os.path.exists(location):
            # Delete file
            try:
                os.remove(location)
                success = True
            except OSError:
                _LOGGER.error("Unable to remove file: '" + location + "'")

        return success
