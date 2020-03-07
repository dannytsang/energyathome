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

import cPickle as pickle

import debug
import historical_data
from database import MySQL
from config.Config import ConfigManager
from data_validation import CheckLiveData
from data_trigger import CheckLiveTriggers

class BackupRestore:
    
    def __init__(self):
        # Instantiate Logger
        self.LOGGER = debug.getLogger("energyathome.datalogger.offlinehandler")
        # Configuration Manager
        self.CONFIG = ConfigManager()
        # Data validation class
        self.VALIDATOR = CheckLiveData()
        # Data trigger class
        self.TRIGGER = CheckLiveTriggers()
        
    def backup(self, historicalData):
        '''Writes historical data to file'''
        
        #If true exit due to exception
        exit = False
        # Get file path from config
        location = self.CONFIG.getConfig("Application", "offlineFile")
        #Check if config is empty
        if len(location) == 0:
            # Use current directory
            location = os.path.join(os.getcwd(), "backup.p")
            self.LOGGER.warning("offlineFile is empty. Using default: '" + location + "'")
        
        try:
            # Append to file
            path = file(location, "a")

            # Ensure object has data
            if historicalData is not None:
                self.LOGGER.info("Writing data to file:" + str(historicalData.__dict__))
                pickle.dump(historicalData, path)
        except IOError:
            #Debug.writeOut("Unable to write to backup file: '" + location + "'")
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
        '''Starts the restore process from a file.'''
        
        backup = self.restoreFromFile()
        recordCount = len(backup)
        
        if(recordCount > 0):
            self.LOGGER.info(str(recordCount) + " record(s) found. Saving to DB")
            for record in backup:
                # Set data as valid by default
                hDataValid = True
                # Get backup record
                hData = record
                
                if self.VALIDATOR is not None and self.CONFIG.getBooleanConfig("Tolerence", "enabled"):
                    try:
                        validatedData = self.VALIDATOR.validateData(hData)
                    except Exception as e:
                        raise e
                    
                    hDataValid = validatedData[0]
                    if hDataValid is True:
                        hData = validatedData[1]
                
                if hDataValid and self.CONFIG.getBooleanConfig("Trigger", "enabled"):
                    # Check trigger conditions which return true or false if it's valid
                    try:
                        hDataValid = self.TRIGGER.checkTriggers(hData)
                    except Exception as e:
                        raise e
                
                # Insert the first element in list and remove it
                if hDataValid:
                    self.LOGGER.info("Inserting: " + str(record.__dict__))
                    #HistoricalData.insertData(record)
                    historical_data.insertData(hData)
                else:
                    self.LOGGER.info("Skipped backup record")
                
            # Remove backup file to prevent duplicate data from being restored.
            self.LOGGER.info("Restore from backup complete.")
            self.LOGGER.info("Removing backup file.")
            self.LOGGER.info("File deleted? " + str(self.deleteBackupFile()))

    def restoreFromFile(self):
        '''Reads a file and returns an array of objects.'''
        
        # List to store restored objects
        list = []
        # Get file path from config
        location = self.CONFIG.getConfig("Application", "offlineFile")
        #Check if config is empty
        if len(location) == 0:
            # Use current directory
            location = os.path.join(os.getcwd(), "backup.p")
            self.LOGGER.info("offlineFile is empty. Using default: '" + location + "'")
        # Check file exists before deleting
        if os.path.exists(location):
            # Create file object
            path = file(location, "r")
            # Read file till end of file
            try:
                while True:
                    list.append(pickle.load(path))
            except EOFError:
                # Ignore end of file error
                pass
            finally:
                # Close file
                path.close()
                
        self.LOGGER.info("Found " + str(len(list)) + " record(s) in '" + location + "'")
        return list

    def deleteBackupFile(self):
        '''Removed backup file if it exists.'''
        
        success = False;
        
        # Get file path from config
        location = self.CONFIG.getConfig("Application", "offlineFile")
        #Check if config is empty
        if len(location) == 0:
            # Use current directory
            location = os.path.join(os.getcwd(), "backup.p")
            self.LOGGER.info("offlineFile is empty. Using default: '" + location + "'")
        # Check file exists before deleting
        if os.path.exists(location):
            # Delete file
            try:
                os.remove(location)
                success = True;
            except OSError:
                self.LOGGER.error("Unable to remove file: '" + location + "'")
        
        return success;
