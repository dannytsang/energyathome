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

import math
import sys
from datetime import datetime, timedelta, date

import SerialComm
import HistoricalData
import Debug
from database.MySQL import MySQL
from database.DatabaseException import ConnectionException
from config.Config import ConfigManager
from xmlhandler.XMLParser import Parser
from DataValidation import CheckLiveData
from DataTrigger import CheckLiveTriggers
from SerialComm import DeviceManager
from OfflineHandler import BackupRestore

# Configuration Manager
CONFIG = ConfigManager()

# Instantiate Logger
LOGGER = Debug.getLogger("energyathome.datalogger.core")

# Instantiate DB
DATABASE = MySQL()

SCHEDULER = None

# Data validation
VALIDATOR = None

# Data trigger
TRIGGER = None

# Serial Devices
DEVICE = None

# Offline handler
OFFLINE = None

# Offline Mode
OFFLINEMODE = False

def run():
    '''Reads, parses and stores data'''
    
    global CONFIG
    global LOGGER
    global VALIDATOR
    global TRIGGER
    global DEVICE
    global OFFLINE
    global OFFLINEMODE
    
    # Read data from USB/Serial
    data = DEVICE.read()
    # Instantiate parser
    xmlParser = Parser()
    # Parse xml data from device
    hData = xmlParser.parseXML(data)
    #valid data
    hDataValid = True
    
    if hData is not None:
        # Check time override
        if CONFIG.getBooleanConfig("Application", "useSystemTime"):
            # Overriding device time with system date time
            hData.time = datetime.now()
        else:
            try:
                # Parse time from device pre-pending system date
                tempDate = date.today().isoformat() + " " + hData.time
                hData.time = datetime.strptime(tempDate, "%Y-%m-%e %H:%M:%S")
            except ValueError:
                # Unable to parse time from device
                LOGGER.error("Error parsing time from device '" + hData.time + "'")
        
        # If error checking is enabled
        if VALIDATOR is not None and CONFIG.getBooleanConfig("Tolerence", "enabled"):
            try:
                # Validate data
                validatedData = VALIDATOR.validateData(hData)
                
                # Retrieve validation result
                hDataValid = validatedData[0]
                # If data is valid, retrieve the new valid data. The object may have
                # been cleansed e.g some channels may not meet validation parameters but
                # other channels might in the reading
                if hDataValid is True:
                    hData = validatedData[1]
                    
            except ConnectionException as ce:
                # Gracefully shutdown if it was unable to validate the data due to
                # database connection
                if CONFIG.getBooleanConfig("Application", "enableOffline"):
                    # Set mode to offline
                    OFFLINEMODE = True
                    OFFLINE.backup(hData)
                else:
                    shutdown()
                
        # Only check trigger conditions if it's enabled, not in offline mode and
        # data is valid after tolerence check
        if OFFLINEMODE is False and hDataValid and CONFIG.getBooleanConfig("Trigger", "enabled"):
            # Check trigger conditions which return true or false if it's valid
            try:
                hDataValid = TRIGGER.checkTriggers(hData)
            except ConnectionException as ce:
                # Gracefully shutdown if it was unable to check triggers due to database connection
                if CONFIG.getBooleanConfig("Application", "enableOffline"):
                    # Set mode to offline
                    OFFLINEMODE = True
                    OFFLINE.backup(hData)
                else:
                    shutdown()
        
        # Insert data if it passed all checks and mode is not offline
        if OFFLINEMODE is False:
            if hDataValid:
                try:
                    HistoricalData.insertData(hData)
                except ConnectionException as ce:
                    # Gracefully shutdown if it was unable to check triggers due to database connection
                    if CONFIG.getBooleanConfig("Application", "enableOffline"):
                        # Set mode to offline
                        OFFLINEMODE = True
                        OFFLINE.backup(hData)
                    else:
                        shutdown()
            else:
                LOGGER.info("Skipped")
        else:
            LOGGER.info("Offline mode: Active")

# Initialise
def init():
    '''Initialises program.
    Inserts the 0 value for last date + 1 second and 0 value for current
    date time. Allows graph to draw 0 instead of tacking from last know value'''
    
    global CONFIG
    global LOGGER
    global SCHEDULER
    global VALIDATOR
    global TRIGGER
    global DATABASE
    global DEVICE
    global OFFLINE
    
    LOGGER.info("Initialising")
    
    # Instantiate validation class if enabled
    if CONFIG.getBooleanConfig("Tolerence", "enabled"):
        VALIDATOR = CheckLiveData()
    
    # Instantiate trigger class if enabled
    if CONFIG.getBooleanConfig("Trigger", "enabled"):
        TRIGGER = CheckLiveTriggers()
        
    # Instantiate offline class handler if enabled
    if CONFIG.getBooleanConfig("Application", "enableOffline"):
        OFFLINE = BackupRestore()
    
    # Connect to database
    try:
        LOGGER.debug("Start DB connection")
        DATABASE.connect()
    except ConnectionException:
        LOGGER.critical("Unable to connect to database. Exiting...")
        sys.exit(1)
    
    # If offline backup is enabled insert any data stored in file.
    LOGGER.debug("Checking offline setting")
    if CONFIG.getBooleanConfig("Application", "enableOffline"):
        LOGGER.debug("Offline backup enabled")
        # Restore data
        try:
            OFFLINE.restore()
        except:
            # Gracefully shutdown.
            shutdown()
    
    # Get last date time + 1 second for each channel and insert into DB
    LOGGER.info("Inserting previous 0 records")
    sql = "INSERT INTO historical_data (date_time, channel_id, data, unit) " +\
    "SELECT (SELECT ADDDATE(MAX(date_time), INTERVAL 1 SECOND) FROM " +\
    "historical_data h WHERE h.channel_id = c.channel_id), c.channel_id, 0, " +\
    "CASE c.channel WHEN 'temp' THEN 'C' ELSE 'W' END FROM channel c"
    LOGGER.debug(sql)
    try:
        DATABASE.executeUpdate(sql, None)
    except ConnectionException:
        LOGGER.critical("Unable to connect to database. Exiting...")
        sys.exit(1)
    
    # Insert records for current time
    LOGGER.info("Inserting current 0 records")
    sql = "INSERT INTO historical_data (date_time, channel_id, data, unit) " +\
    "SELECT NOW(), c.channel_id, 0, CASE c.channel WHEN 'temp' THEN 'C' ELSE 'W' END " +\
    "FROM channel c WHERE c.channel_id IN (SELECT DISTINCT h.channel_id FROM historical_data h)"
    LOGGER.debug(sql)
    try:
        DATABASE.executeUpdate(sql, None)
    except ConnectionException:
        LOGGER.critical("Database error. Exiting...")
        sys.exit(1)
        
    # Create new instance of scheduler
    LOGGER.info("Checking scheduler setting")
    if CONFIG.getBooleanConfig("Scheduler", "enabled"):
        LOGGER.info("Scheduler enabled")
        # Import the module only if scheduler is enabled
        import Scheduler
        # Instantiate and start the scheduler
        SCHEDULER = Scheduler.JobChecker()
        SCHEDULER.start()
    
    # Open connection to serial device
    try:
        DEVICE = DeviceManager()
        DEVICE.open()
        
    except Exception, e:
        LOGGER.critical("Unable to connect to device port.\n" + str(e))
        shutdown()
        
def shutdown():
    '''Procedures to run before ending program'''
    
    global CONFIG
    global LOGGER
    global SCHEDULER
    global DATABASE
    global DEVICE
    
    LOGGER.info("Shutting down energyathome")
    
    # Close connection to serial port
    if DEVICE is not None:
        DEVICE.close()
    
    # Close database connection
    if DATABASE is not None:
        DATABASE.disconnect()
    
    # Stop scheduler
    if CONFIG.getBooleanConfig("Scheduler", "enabled") and SCHEDULER is not None:
        SCHEDULER.stop()
    
    # Exit program
    LOGGER.debug("Exit 0")
    sys.exit(0)
