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
from datetime import datetime, date

import historical_data
from database.MySQL import MySQL
from database.DatabaseException import ConnectionException
from config.Config import ConfigManager
from xmlhandler.XMLParser import Parser
from data_validation import CheckLiveData
from data_trigger import CheckLiveTriggers
from serial_comm import DeviceManager
from offline_handler import BackupRestore

# Configuration Manager
CONFIG = ConfigManager()
# Instantiate _LOGGER
_LOGGER = logging.getLogger(__name__)
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
OFFLINE_MODE = False


def run():
    """Reads, parses and stores data"""

    global CONFIG
    global _LOGGER
    global VALIDATOR
    global TRIGGER
    global DEVICE
    global OFFLINE
    global OFFLINE_MODE

    # Read data from USB/Serial
    data = DEVICE.read()
    # Instantiate parser
    xml_parser = Parser()
    # Parse xml data from device
    h_data = xml_parser.parse_xml(data)
    # valid data
    h_data_valid = True

    if h_data is not None:
        # Check time override
        if CONFIG.get_boolean_config("Application", "useSystemTime"):
            # Overriding device time with system date time
            h_data.time = datetime.now()
        else:
            try:
                # Parse time from device pre-pending system date
                temp_date = date.today().isoformat() + " " + h_data.time
                h_data.time = datetime.strptime(temp_date, "%Y-%m-%e %H:%M:%S")
            except ValueError:
                # Unable to parse time from device
                _LOGGER.error("Error parsing time from device '" + h_data.time + "'")

        # If error checking is enabled
        if VALIDATOR is not None and CONFIG.get_boolean_config("Tolerence", "enabled"):
            try:
                # Validate data
                validated_data = VALIDATOR.validate_data(h_data)

                # Retrieve validation result
                h_data_valid = validated_data[0]
                # If data is valid, retrieve the new valid data. The object may have
                # been cleansed e.g some channels may not meet validation parameters but
                # other channels might in the reading
                if h_data_valid is True:
                    h_data = validated_data[1]

            except ConnectionException as ce:
                # Gracefully shutdown if it was unable to validate the data due to
                # database connection
                if CONFIG.get_boolean_config("Application", "enableOffline"):
                    # Set mode to offline
                    OFFLINE_MODE = True
                    OFFLINE.backup(h_data)
                else:
                    shutdown()

        # Only check trigger conditions if it's enabled, not in offline mode and
        # data is valid after tolerence check
        if OFFLINE_MODE is False and h_data_valid and CONFIG.get_boolean_config("Trigger", "enabled"):
            # Check trigger conditions which return true or false if it's valid
            try:
                h_data_valid = TRIGGER.check_triggers(h_data)
            except ConnectionException as ce:
                # Gracefully shutdown if it was unable to check triggers due to database connection
                if CONFIG.get_boolean_config("Application", "enableOffline"):
                    # Set mode to offline
                    OFFLINE_MODE = True
                    OFFLINE.backup(h_data)
                else:
                    shutdown()

        # Insert data if it passed all checks and mode is not offline
        if OFFLINE_MODE is False:
            if h_data_valid:
                try:
                    historical_data.insert_data(h_data)
                except ConnectionException as ce:
                    # Gracefully shutdown if it was unable to check triggers due to database connection
                    if CONFIG.get_boolean_config("Application", "enableOffline"):
                        # Set mode to offline
                        OFFLINE_MODE = True
                        OFFLINE.backup(h_data)
                    else:
                        shutdown()
            else:
                _LOGGER.info("Skipped")
        else:
            _LOGGER.info("Offline mode: Active")


# Initialise
def init():
    """Initialises program.
    Inserts the 0 value for last date + 1 second and 0 value for current
    date time. Allows graph to draw 0 instead of tacking from last know value"""

    global CONFIG
    global SCHEDULER
    global VALIDATOR
    global TRIGGER
    global DATABASE
    global DEVICE
    global OFFLINE

    _LOGGER.info("Initialising")

    # Instantiate validation class if enabled
    if CONFIG.get_boolean_config("Tolerence", "enabled"):
        VALIDATOR = CheckLiveData()

    # Instantiate trigger class if enabled
    if CONFIG.get_boolean_config("Trigger", "enabled"):
        TRIGGER = CheckLiveTriggers()

    # Instantiate offline class handler if enabled
    if CONFIG.get_boolean_config("Application", "enableOffline"):
        OFFLINE = BackupRestore()

    # Connect to database
    try:
        _LOGGER.debug("Start DB connection")
        DATABASE.connect()
    except ConnectionException:
        _LOGGER.critical("Unable to connect to database. Exiting...")
        sys.exit(1)

    # If offline backup is enabled insert any data stored in file.
    _LOGGER.debug("Checking offline setting")
    if CONFIG.get_boolean_config("Application", "enableOffline"):
        _LOGGER.debug("Offline backup enabled")
        # Restore data
        try:
            OFFLINE.restore()
        except Exception as e:
            # Gracefully shutdown.
            shutdown()

    # Get last date time + 1 second for each channel and insert into DB
    _LOGGER.info("Inserting previous 0 records")
    sql = "INSERT INTO historical_data (date_time, channel_id, data, unit) " + \
          "SELECT (SELECT ADDDATE(MAX(date_time), INTERVAL 1 SECOND) FROM " + \
          "historical_data h WHERE h.channel_id = c.channel_id), c.channel_id, 0, " + \
          "CASE c.channel WHEN 'temp' THEN 'C' ELSE 'W' END FROM channel c"
    _LOGGER.debug(sql)
    try:
        DATABASE.execute_update(sql, None)
    except ConnectionException:
        _LOGGER.critical("Unable to connect to database. Exiting...")
        sys.exit(1)

    # Insert records for current time
    _LOGGER.info("Inserting current 0 records")
    sql = "INSERT INTO historical_data (date_time, channel_id, data, unit) " + \
          "SELECT NOW(), c.channel_id, 0, CASE c.channel WHEN 'temp' THEN 'C' ELSE 'W' END " + \
          "FROM channel c WHERE c.channel_id IN (SELECT DISTINCT h.channel_id FROM historical_data h)"
    _LOGGER.debug(sql)
    try:
        DATABASE.execute_update(sql, None)
    except ConnectionException:
        _LOGGER.critical("Database error. Exiting...")
        sys.exit(1)

    # Create new instance of scheduler
    _LOGGER.info("Checking scheduler setting")
    if CONFIG.get_boolean_config("Scheduler", "enabled"):
        _LOGGER.info("Scheduler enabled")
        # Import the module only if scheduler is enabled
        import scheduler
        # Instantiate and start the scheduler
        SCHEDULER = scheduler.JobChecker()
        SCHEDULER.start()

    # Open connection to serial device
    try:
        DEVICE = DeviceManager()
        DEVICE.open()
    except Exception as e:
        _LOGGER.critical("Unable to connect to device port.\n" + str(e))
        shutdown()


def shutdown():
    """Procedures to run before ending program"""

    global CONFIG
    global _LOGGER
    global SCHEDULER
    global DATABASE
    global DEVICE

    _LOGGER.info("Shutting down energyathome")

    # Close connection to serial port
    if DEVICE is not None:
        DEVICE.close()

    # Close database connection
    if DATABASE is not None:
        DATABASE.disconnect()

    # Stop scheduler
    if CONFIG.get_boolean_config("Scheduler", "enabled") and SCHEDULER is not None:
        SCHEDULER.stop()

    # Exit program
    _LOGGER.debug("Exit successfully")
    sys.exit(0)
