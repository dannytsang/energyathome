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

import logging

from database.MySQL import MySQL
from database.database_exception import ConnectionException

# Instantiate _LOGGER
_LOGGER = logging.getLogger(__name__)

# Instantiate DB
DATABASE = MySQL()


# Historical data class used to store device data
class HistoricalData:

    def __init__(self):
        # CC name
        self.name = ""
        # Days Since Birth
        self.dsb = 0
        # Time reported by device
        self.time = ""
        # In degrees celcius
        self.temperature = 0.0
        # Appliance sensor number as displayed on CCD
        self.applianceId = 0
        # Type of sensor the data is related to
        # 1 = electrical
        self.sensorType = 0
        # Energy
        self.energy = {}


# Insert a new device into DB
def insert_data(historical_data):
    """Insert historical data into the database with the current data held in
    this class but ignores the datetime field and uses current server time"""

    global DATABASE

    if historical_data is not None:
        # Get device id
        device_id = get_device_id(historical_data.name, historical_data.applianceId, historical_data.sensorType)

        # If device / channel does not exist
        if device_id is None:
            # Create new device
            device_id = create_device(historical_data)
        else:
            # Need to get device ID from tuple
            device_id = device_id[0]

        if device_id is not None:
            # Iterate all channels and store the values
            for key, value in historical_data.energy.items():
                # Get channel ID
                channel_id = get_channel_id(device_id, key)

                if channel_id is None:
                    channel_id = create_channel(device_id, key)

                # Build SQL statement to store data
                sql = "INSERT INTO historical_data (date_time, channel_id, " + \
                      "data, unit) VALUES (%s, %s, %s, %s)"
                _LOGGER.debug(sql)

                # Build values
                values = [historical_data.time.isoformat(' '), channel_id, value, "W"]
                _LOGGER.debug(values)

                DATABASE.execute_non_update(sql, values)

            # Insert temperature
            # Get channel ID
            channel_id = get_channel_id(None, "temp")

            if channel_id is None:
                channel_id = create_channel(device_id, "temp")

            # Build SQL statement to store data
            sql = "INSERT INTO historical_data (date_time, channel_id, " + \
                  "data, unit) VALUES (%s, %s, %s, %s)"
            _LOGGER.debug(sql)

            # Build values
            values = [historical_data.time.isoformat(' '), channel_id, historical_data.temperature, "C"]
            _LOGGER.debug(values)

            DATABASE.execute_non_update(sql, values)

            _LOGGER.info("data stored successfully")
        else:
            _LOGGER.info("failed to store data")
    else:
        _LOGGER.info("No data to store")


def create_device(historical_data):
    """Creates a new device record"""

    global _LOGGER
    global DATABASE

    _LOGGER.info("Device name: " + historical_data.name + ", app ID: " + \
                 str(historical_data.applianceId) + ", sensor type: " + \
                 str(historical_data.sensorType) + ", does not exists")

    # Insert new device
    sql = "INSERT INTO device (name, appliance_id, sensor_type)" + \
          "VALUES (%s, %s, %s)"
    _LOGGER.debug(sql)

    values = [historical_data.name, historical_data.applianceId, historical_data.sensorType]
    _LOGGER.debug(values)

    return DATABASE.execute_non_update(sql, values)


def create_channel(device_id, channel):
    """Creates new channel record"""

    global _LOGGER
    global DATABASE

    _LOGGER.info("Device : " + str(device_id) + ", channel: " + \
                 str(channel) + ", does not exists")

    # Insert new device
    sql = "INSERT INTO channel (device_id, channel) VALUES (%s, %s)"
    _LOGGER.debug(sql)

    values = [device_id, channel]
    _LOGGER.debug(values)

    return DATABASE.execute_non_update(sql, values)


def get_device_id(name, appliance_id, sensor_type):
    """Retrieves the Device ID form the database"""

    global _LOGGER
    global DATABASE

    sql = "SELECT device_id FROM device WHERE name = %s " + \
          "AND appliance_id = %s AND sensor_type = %s ORDER BY device_id"
    _LOGGER.debug(sql)

    values = [name, appliance_id, sensor_type]
    _LOGGER.debug(values)

    return DATABASE.execute_one_update(sql, values)


def get_channel_id(device_id, channel):
    """Retrieves the channel ID from the database"""

    global _LOGGER
    global DATABASE

    sql = "SELECT c.channel_id FROM channel c WHERE"
    if device_id is not None:
        sql += " c.device_id = %s AND "
        values = [device_id, channel]
    else:
        values = [channel]

    sql += " c.channel = %s ORDER BY c.channel_id LIMIT 1"
    _LOGGER.debug(sql)
    _LOGGER.debug(values)

    channel_id = DATABASE.execute_one_update(sql, values)

    if channel_id is not None:
        return channel_id[0]
    else:
        return None


def get_last_historical_data(historical_data):
    """Retrieve the last data saved for particular device, application id, sensor type.
    All conditions must match in order to get last data point back.
    Expects a HistoricalData object with those values populated and will return
    date time, energy and temperature values back"""

    global _LOGGER
    global DATABASE

    # Instantiate return variable
    last_historical_data = HistoricalData()

    # Set common variables from data received
    last_historical_data.name = historical_data.name
    last_historical_data.applianceId = historical_data.applianceId
    last_historical_data.sensorType = historical_data.sensorType

    # Retrieve last data point for appliance
    # for key, value in historicalData.energy.items():

    # Build SQL statement
    sql = "SELECT c.channel_id, c.channel, max(h.date_time), h.data FROM device d INNER JOIN " + \
          "channel c ON c.device_id = d.device_id INNER JOIN (SELECT h1.date_time, h1.channel_id, h1.data " + \
          "FROM historical_data h1 , (SELECT MAX(date_time) date_time, channel_id " + \
          "FROM historical_data WHERE date_time < %s GROUP BY channel_id) h2 " + \
          "WHERE h1.date_time = h2.date_time AND h1.channel_id = h2.channel_id ) h ON " + \
          "h.channel_id = c.channel_id WHERE d.name = %s AND d.appliance_id = %s AND " + \
          "d.sensor_type = %s"

    try:
        # Check channel data exists
        if historical_data.energy is not None and len(historical_data.energy) > 0:
            channel_sql = ""
            # Insert all the channels in device
            for key, value in historical_data.energy.items():
                # Check if a prepend is needed
                if len(channel_sql) > 0:
                    channel_sql += " OR"

                channel_sql += " c.channel = '" + key + "'"

            sql += " AND (" + channel_sql + ")"

        sql += " GROUP BY c.channel_id, c.channel, h.data ORDER BY h.date_time, c.channel, c.channel_id, h.data"
        _LOGGER.debug(sql)

        # Build values
        values = [historical_data.time, historical_data.name, historical_data.applianceId, historical_data.sensorType]
        _LOGGER.debug(values)

        # Execute query and store results
        results = DATABASE.execute_update(sql, values)

        # Set the time to the first record (the ealiest date in results)
        # Only if there is a previous record
        if results is not None and len(results) > 0:
            last_historical_data.time = results[0][2]

            # If previous record was found. Retrieve energy data
            for result in results:
                last_historical_data.energy[result[1]] = result[3]
        else:
            # Unable to find last datapoint. Exit function
            return None

        # Get temperature (if any)
        if last_historical_data is not None:
            sql = "SELECT h.data FROM channel c INNER JOIN " + \
                  "historical_data h ON h.channel_id = c.channel_id WHERE c.channel = 'temp' AND h.date_time = " + \
                  "(SELECT h2.date_time FROM historical_data h2 WHERE h2.channel_id = c.channel_id ORDER BY " \
                  "h2.date_time desc LIMIT 1) LIMIT 1 "
            _LOGGER.debug(sql)

            results = DATABASE.execute_one_update(sql, None)

            if results is not None:
                last_historical_data.temperature = float(results[0])
            else:
                last_historical_data.temperature = None

    except ConnectionException as ce:
        raise ce

    # Return record
    return last_historical_data
