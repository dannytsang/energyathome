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

import time, sys, os
import logging, logging.config

import pymysql

from config.Config import ConfigManager
from .database_exception import ConnectionException


class MySQL(object):
    
    INSTANCE = None
    # Instantiate self._LOGGER
    _LOGGER = logging.getLogger(__name__)
    
    def __new__(cls, *args, **kwargs):
        if not cls.INSTANCE:
            cls.INSTANCE = super(MySQL, cls).__new__(
                                cls, *args, **kwargs)
        
        return cls.INSTANCE

    def __init__(self):
        """Check all global variables have been initialized"""
        
        # Configuration Manager
        self.CONFIG = ConfigManager()

        # Connection variable
        self.CONNECTION = None

        # Number of transaction retries before failing
        self.RETRIES = self.CONFIG.get_int_config("Database", "retries")

        # Number in seconds to wait before re-attempting failed transaction
        self.WAIT = self.CONFIG.get_float_config("Database", "wait")

        sys.path.append("..")
        
        if self.CONFIG is None:
            self._LOGGER.critical("Unable to get configuration manager. Exit")
            sys.exit(1)
        
        if self.RETRIES is None:
            self._LOGGER.info("No DB retry value set. Using default value")
            self.RETRIES = 3
        
        if self.WAIT is None:
            self._LOGGER.info("No DB wait value set. Using default value")
            self.WAIT = 60

    # Connect to MySQL using settings from DatabaseConfig.py
    def connect(self):
        """Connect to database"""
        
        attempts = 1
        
        database_settings = self.CONFIG.get_config_category("Database")
        
        if self._LOGGER is None:
            self.__init__()
        
        while attempts <= self.CONFIG.get_int_config("Database", "retries") and self.CONNECTION is None:
            
            try:
                self._LOGGER.info("Attempting DB connection")
                self.CONNECTION = pymysql.connect(database_settings["url"], database_settings["username"],
                                                  database_settings["password"], database_settings["database"])
                # Turn ping on to automatically connect to DB when idle and disconnects
                self.CONNECTION.ping(True)
                self._LOGGER.info("DB connection successful")
                
            except Exception as e:
                # Failed to connect
                self._LOGGER.error("Unable to connect to database:'" + str(database_settings["url"]) + "|" + str(e.args[0]))
                self._LOGGER.error("Attempt " + str(attempts) + " failed. Retrying in " + str(database_settings["wait"]) + " secs")
                # Wait for n seconds before attempting to reconnect
                time.sleep(self.WAIT)
                # Continue in loop
                pass
            # Increment number of times it tried to connect
            attempts += 1
        # If CONNECTION is None then it was unable to connect
        if self.CONNECTION is None:
            raise ConnectionException("Database connection error")

    # Close DB CONNECTION
    def disconnect(self):
        """Close CONNECTION to database"""
        
        try:
            # Only close CONNECTION if CONNECTION exists
            if self.CONNECTION is not None:
                self._LOGGER.info("Attempting to close DB connection")
                self.CONNECTION.close()
                self.CONNECTION = None
                
                self._LOGGER.info("Close DB connection successful")
                
                return True
        except Exception as e:
            self._LOGGER.error("Unable to disconnect from DB:")
            self._LOGGER.error(e.args[0], e.args[1])
            
        return False

    # Execute query with no return results
    def execute_non_update(self, statement, values):
        """Execute SQL with no return results.
        Accepts an SQL statement with %s parameters which will be replaced with
        the values parameter. If no %s is used, values should be set to None.
        Returns last inserted row ID reguardless of SQL type."""
        
        id = None
        attempts = 1
        
        while attempts <= self.RETRIES:
            try:
                cursor = self.CONNECTION.cursor()
                # Check if values need replacing in SQL statement
                if values is None:
                    cursor.execute(statement)
                else:
                    cursor.execute(statement, values)
                    
                self.CONNECTION.commit()
                id = cursor.lastrowid
                cursor.close()
                # Exit retry loop and return value
                break
            
            except Exception as e:
                self._LOGGER.error(e, exc_info=True)
                self._LOGGER.debug(cursor._last_executed)
                
                self._LOGGER.error("Retrying in " + str(self.WAIT) + " secs")
                # Increment number of times it has tried to execute this function
                attempts += 1
                time.sleep(self.WAIT)
                
                try:
                    # Try disconnecting first to avoid holding a CONNECTION open
                    self.disconnect()
                    # Try reconnecting to DB
                    self.connect()
                    
                except Exception as e:
                    # Ignore connect error and gracefully exit function
                    self._LOGGER.error("DB reconnect failed:")
                    self._LOGGER.error(e, exc_info=True)
                    raise
                pass
                
            except AttributeError as ae:
                # Caught when an object such as the connection has not been instantiated.
                # This may happen if connection is lost whils trying to get a cursor
                raise ConnectionException("Attribute error in DB")
        # return id from insert
        return id

    # Execute query and return results
    def execute_update(self, statement, values):
        """Execute query and return all results."""
        
        attempts = 1
        
        while attempts <= self.RETRIES:
            try:
                cursor = self.CONNECTION.cursor()
                # Check if values need replacing in SQL statement
                if values is None:
                    cursor.execute(statement)
                else:
                    cursor.execute(statement, values)
                
                results = cursor.fetchall()
                cursor.close()
                
                return results
            
            except Exception as e:
                self._LOGGER.error(e, exc_info=True)
                self._LOGGER.debug(cursor._last_executed)
                
                self._LOGGER.error("Retrying in " + str(self.WAIT) + " secs")
                # Increment number of times it has tried to execute this function
                attempts += 1
                time.sleep(self.WAIT)
                
                try:
                    # Try disconnecting first to avoid holding a CONNECTION open
                    self.disconnect()
                    # Try reconnecting to DB
                    self.connect()
                except ConnectionException as ce:
                    self._LOGGER.error(ce, exc_info=True)
                    raise ce
                pass
                
            except AttributeError as ae:
                # Caught when an object such as the connection has not been instantiated.
                # This may happen if connection is lost whils trying to get a cursor
                raise ConnectionException("Attribute error in DB")
        # Fail after retry
        return None

    # Execute query and return one result
    def execute_one_update(self, statement, values):
        """Execute SQL and returns one result.
        Accepts an SQL statement with %s parameters which will be replaced with
        the values parameter. If no %s is used, values should be set to None.
        Returns the first result only."""
        
        attempts = 1
        
        while attempts <= self.RETRIES:
            try:
                cursor = self.CONNECTION.cursor()
                # Check if values need replacing in SQL statement
                if values is None:
                    cursor.execute(statement)
                else:
                    cursor.execute(statement, values)
                    
                result = cursor.fetchone()
                cursor.close()
                
                return result
            
            except Exception as e:
                self._LOGGER.error(e, exc_info=True)
                
                self._LOGGER.error("Retrying in " + str(self.WAIT) + " secs")
                
                self._LOGGER.error("Retrying in " + str(self.WAIT) + " secs")
                # Increment number of times it has tried to execute this function
                attempts += 1
                time.sleep(self.WAIT)
                
                try:
                    # Try disconnecting first to avoid holding a CONNECTION open
                    self.disconnect()
                    # Try reconnecting to DB
                    self.connect()
                    
                except ConnectionException as ce:
                    # Ignore connect error and gracefully exit function
                    self._LOGGER.error("DB reconnect failed:")
                    self._LOGGER.error(ce, exc_info=True)
                    raise ce
                
            except AttributeError as ae:
                # Caught when an object such as the connection has not been instantiated.
                # This may happen if connection is lost whils trying to get a cursor
                raise ConnectionException("Attribute error in DB")
                
        # Fail after retry
        return None
