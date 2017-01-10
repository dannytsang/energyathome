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

import Debug
from database.MySQL import MySQL
from database.DatabaseException import ConnectionException

# Instantiate Logger
LOGGER = Debug.getLogger("energyathome.datalogger.historicaldata")

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
def insertData(historicalData):
    '''Insert historical data into the database with the current data held in
    this class but ignores the datetime field and uses current server time'''

    global LOGGER
    global DATABASE

    if historicalData is not None:
        # Get device id
        deviceId = getDeviceId(historicalData.name, historicalData.applianceId, historicalData.sensorType)
        
        # If device / channel does not exist
        if deviceId is None:
            # Create new device
            deviceId = createDevice(historicalData)
        else:
            # Need to get device ID from tuple
            deviceId = deviceId[0]
        
        if  deviceId is not None:
            # Interate all channels and store the values
            for key, value in historicalData.energy.iteritems():
                # Get channel ID
                channelId = getChannelId(deviceId, key)
                
                if channelId is None:
                    channelId = createChannel(deviceId, key)
                
                # Build SQL statement to store data
                sql = "INSERT INTO historical_data (date_time, channel_id, " +\
                "data, unit) VALUES (%s, %s, %s, %s)"
                LOGGER.debug(sql)
                
                # Build values
                values = [historicalData.time.isoformat(' '), channelId, value, "W"]
                LOGGER.debug(values)
                
                DATABASE.executeNonUpdate(sql, values)
            
            # Insert temperature
            # Get channel ID
            channelId = getChannelId(None, "temp")
            
            if channelId is None:
                channelId = createChannel(deviceId, "temp")
            
            # Build SQL statement to store data
            sql = "INSERT INTO historical_data (date_time, channel_id, " +\
            "data, unit) VALUES (%s, %s, %s, %s)"
            LOGGER.debug(sql)
            
            # Build values
            values = [historicalData.time.isoformat(' '), channelId, historicalData.temperature, "C"]
            LOGGER.debug(values)
            
            DATABASE.executeNonUpdate(sql, values)
            
            LOGGER.info("data stored successfully")
        else:
            LOGGER.info("failed to store data")
    else:
        LOGGER.info("No data to store")

def createDevice(historicalData):
    '''Creates a new device record'''
    
    global LOGGER
    global DATABASE
    
    LOGGER.info("Device name: " + historicalData.name + ", app ID: " +\
    str(historicalData.applianceId) + ", sensor type: " +\
    str(historicalData.sensorType) + ", does not exists")
    
    # Insert new device
    sql = "INSERT INTO device (name, appliance_id, sensor_type)" +\
    "VALUES (%s, %s, %s)"
    LOGGER.debug(sql)
    
    values = [historicalData.name, historicalData.applianceId, historicalData.sensorType]
    LOGGER.debug(values)
    
    return DATABASE.executeNonUpdate(sql, values)

def createChannel(deviceId, channel):
    '''Creates new channel record'''
    
    global LOGGER
    global DATABASE
    
    LOGGER.info("Device : " + str(deviceId) + ", channel: " +\
    str(channel) + ", does not exists")
    
    # Insert new device
    sql = "INSERT INTO channel (device_id, channel) VALUES (%s, %s)"
    LOGGER.debug(sql)
    
    values = [deviceId, channel]
    LOGGER.debug(values)
    
    return DATABASE.executeNonUpdate(sql, values)

def getDeviceId(name, applianceId, sensorType):
    '''Retrieves the Device ID form the database'''
    
    global LOGGER
    global DATABASE
    
    sql = "SELECT device_id FROM device WHERE name = %s " +\
    "AND appliance_id = %s AND sensor_type = %s ORDER BY device_id"
    LOGGER.debug(sql)
    
    values = [name, applianceId, sensorType]
    LOGGER.debug(values)
    
    return DATABASE.executeOneUpdate(sql, values)

def getChannelId(deviceId, channel):
    '''Retrieves the channel ID from the database'''
    
    global LOGGER
    global DATABASE
    
    sql = "SELECT c.channel_id FROM channel c WHERE"
    if deviceId is not None:
        sql += " c.device_id = %s AND "
        values = [deviceId, channel]
    else:
        values = [channel]
    
    sql += " c.channel = %s ORDER BY c.channel_id LIMIT 1"
    LOGGER.debug(sql)
    LOGGER.debug(values)
    
    channelId = DATABASE.executeOneUpdate(sql, values)
    
    if channelId is not None:
        return channelId[0]
    else:
        return None

def getLastHistoricalData(historicalData):
    '''Retrieve the last data saved for particular device, application id, sensor type.
    All conditions must match in order to get last data point back.
    Expects a HistoricalData object with those values populated and will return
    date time, energy and temperature values back'''
    
    global LOGGER
    global DATABASE
    
    # Instantiate return variable
    lastHistoricalData = HistoricalData()
    
    # Set common variables from data received
    lastHistoricalData.name = historicalData.name
    lastHistoricalData.applianceId = historicalData.applianceId
    lastHistoricalData.sensorType = historicalData.sensorType
    
    # Retrieve last data point for appliance
    #for key, value in historicalData.energy.iteritems():
    
    # Build SQL statement
    sql = "SELECT c.channel_id, c.channel, max(h.date_time), h.data FROM device d INNER JOIN " +\
    "channel c ON c.device_id = d.device_id INNER JOIN (SELECT h1.date_time, h1.channel_id, h1.data " +\
    "FROM historical_data h1 , (SELECT MAX(date_time) date_time, channel_id " +\
    "FROM historical_data WHERE date_time < %s GROUP BY channel_id) h2 " +\
    "WHERE h1.date_time = h2.date_time AND h1.channel_id = h2.channel_id ) h ON " +\
    "h.channel_id = c.channel_id WHERE d.name = %s AND d.appliance_id = %s AND " +\
    "d.sensor_type = %s"
    
    try:
        # Check channel data exists
        if historicalData.energy is not None and len(historicalData.energy) > 0:
            channelSql = ""
            # Insert all the channels in device
            for key, value in historicalData.energy.iteritems():
                # Check if a prepender is needed
                if len(channelSql) > 0:
                    channelSql += " OR"
                
                channelSql += " c.channel = '" + key + "'"
            
            sql+= " AND (" + channelSql + ")"
        
        sql += " GROUP BY c.channel_id, c.channel, h.data ORDER BY h.date_time, c.channel, c.channel_id, h.data"
        LOGGER.debug(sql)
        
        # Build values
        values = [historicalData.time, historicalData.name, historicalData.applianceId, historicalData.sensorType]
        LOGGER.debug(values)
        
        # Execute query and store results
        results = DATABASE.executeUpdate(sql, values)
        
        # Set the time to the first record (the ealiest date in results)
        # Only if there is a previous record
        if results is not None and len(results) > 0:
            lastHistoricalData.time = results[0][2]
        
            # If previous record was found. Retrieve energy data
            for result in results:
                lastHistoricalData.energy[result[1]] = result[3]
        else:
            # Unable to find last datapoint. Exit function
            return None
        
        # Get temperature (if any)
        if lastHistoricalData is not None:
            sql = "SELECT h.data FROM channel c INNER JOIN " +\
            "historical_data h ON h.channel_id = c.channel_id WHERE c.channel = 'temp' AND h.date_time = " +\
            "(SELECT h2.date_time FROM historical_data h2 WHERE h2.channel_id = c.channel_id ORDER BY h2.date_time desc LIMIT 1) LIMIT 1"
            LOGGER.debug(sql)
            
            results = DATABASE.executeOneUpdate(sql, None)
            
            if results is not None:
                lastHistoricalData.temperature = float(results[0])
            else:
                lastHistoricalData.temperature = None
                
    except ConnectionException as ce:
        raise ce
    
    # Return record
    return lastHistoricalData

