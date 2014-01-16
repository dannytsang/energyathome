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

import Debug
from config.Config import ConfigManager
from database.DatabaseException import ConnectionException

class CheckLiveData:
    
    def __init__(self):
        # Instantiate config manager
        self.CONFIG = ConfigManager()
        # Get logger instance
        self.LOGGER = Debug.getLogger("energyathome.datalogger.datavalidation")
        
    # Validate data captured from device
    def validateData(self, historicalData):
        '''Checks historical data fall within parameter which is customised in the config file.
        Returns results in a tuple size of 2.
        [0] = True or False depending if validation was successful or not
        [1] = HistoricalData.HistoricalData class of sanitised data'''
        
        valid = True
        
        # Get maximum appliance Id value
        maxAppId = self.CONFIG.getIntConfig("Tolerence", "maxApplianceId")
        
        try:
            # If max app id is greater than 0 then checking for app id is enabled
            if maxAppId is not None and maxAppId >= 0:
                if self.checkApplianceId(historicalData) is False:
                    valid = False
            
            # Check device name matches in the config
            deviceNames = self.CONFIG.getConfig("Tolerence", "allowedDeviceNames")
            # If device names are defined then perform a match
            if deviceNames is not None and deviceNames != "":
                if self.checkDeviceName(historicalData) is False:
                    valid = False
            
            if self.CONFIG.getBooleanConfig("Tolerence", "allowNewAppliances") is False:
                # If it returns true then it's a new appliance and should be ignored
                if self.checkNewAppliance(historicalData) is True:
                    valid = False
                    self.LOGGER.info("Appliance ID " + str(historicalData.applianceId) + " was not stored due to allowNewAppliances = False")
                    
            # Check channel names
            if self.CONFIG.getBooleanConfig("Tolerence", "allowBlankChannelNames") is False:
                test = self.checkChannelNames(historicalData)
                # If test returned None then it failed validation.
                # Otherwise assign returned Historical Data because it may have changed some attributes
                if test is None:
                    valid = False
                    
                else:
                    historicalData = test
            
            # Check channels
            if self.CONFIG.getBooleanConfig("Tolerence", "checkChannels") is True and historicalData.applianceId is not None:
                test = self.checkChannels(historicalData)
                # If test returned None then it failed validation.
                # Otherwise assign returned Historical Data because it may have changed some attributes
                if test is None:
                    valid = False
                else:
                    historicalData = test
        except ConnectionException as ce:
            raise ce
        
        return (valid, historicalData)
    
    def checkApplianceId(self, historicalData):
        '''Checks if appliance ID falls within a set range'''
        
        # Get maximum appliance Id value
        maxAppId = self.CONFIG.getIntConfig("Tolerence", "maxApplianceId")
        
        try:
            # Check if appliance number exceeds maximum
            if int(historicalData.applianceId) > maxAppId:
                self.LOGGER.info("Appliance ID " + str(historicalData.applianceId) + " > " + str(maxAppId))
                return False
            
            else:
                return True
            
        except ValueError, ve:
            self.LOGGER.info("Check max App ID failed: " + str(historicalData.applianceId) + " > " + str(maxAppId))
            return False
            
        except AttributeError as ae:
            self.LOGGER.info("Check max App ID failed: No attribute Error:" + str(ae))
            return False
        except ConnectionException as ce:
            raise ce
    
    def checkDeviceName(self, historicalData):
        '''Checks device name is in specified list'''
        
        # Get device names from config
        deviceNames = self.CONFIG.getConfig("Tolerence", "allowedDeviceNames")
        
        # Convert string of device names into a list
        deviceNameSplit = deviceNames.split(",")
        
        # Get case sensitive match from config
        caseSensitiveMatch = self.CONFIG.getConfig("Tolerence", "caseSensitiveDeviceNames")
        
        match = False
        
        for device in deviceNameSplit:
            if caseSensitiveMatch:
                if device.lower() == historicalData.name.lower():
                    match = True
                    break
                
            else:
                if device == historicalData.name:
                    match = True
                    break
        
        if match is False:
            self.LOGGER.info("No matches found for device name '" + str(historicalData.name) + "'")
            return False
        
        else:
            return True
    
    def checkChannelNames(self, historicalData):
        '''Checks channel names are valid'''
        
        if None in historicalData.energy:
            # Remove None key value from energy
            self.LOGGER.info("Found null channel name with value " + str(historicalData.energy[""]))
            del historicalData.energy[None]
            
        if "" in historicalData.energy:
            self.LOGGER.info("Found blank channel name with value " + str(historicalData.energy[""]))
            del historicalData.energy[""]
            
        # Check there are energy values left after cleansing
        if len(historicalData.energy) <= 0:
            return None
        else:
            return historicalData
    
    def checkChannels(self, historicalData):
        '''Checks channels are within specified list'''
        
        # Get device containing appliances and related channels
        allowedChannels = self.CONFIG.getConfigCategory("device_" + historicalData.name)
        
        if allowedChannels is not None:
            # Store the channel (keys) which are invalid to remove safely rather than iterating from a mutable dictionary
            keysToRemove = []
            
            # Loop through all energy data to check if channel is valid
            for key, value in historicalData.energy.iteritems():
                try:
                    channels = allowedChannels["app_" + str(historicalData.applianceId)]
                    if channels is None and allowedChannels["allowundefined"] == "False":
                        # Add to removal list because non defined channels are not allowed
                        keysToRemove.append(key)
                        
                    elif key is not None and channels is not None and key not in channels:
                        # Remove invalid channel
                        keysToRemove.append(key)
                        self.LOGGER.info("Found invalid channel '" + str(key) + "' for appliance " + str(historicalData.applianceId) +\
                        " containing " + str(historicalData.energy[key]))
                        
                except KeyError as ke:
                    # Appliance is not defined with a channel list. Check config for what to do
                    # For some reason getting the dictionary back of a config section returns all values as strings
                    if allowedChannels["allowundefined"] == "False":
                        # Add to removal list
                        keysToRemove.append(key)
            
            # Loop through list of keys which failed validation
            for key in keysToRemove:
                self.LOGGER.info("Deleting " + str(key))
                del historicalData.energy[key]
                
            # Check there are energy values left after cleansing
            if len(historicalData.energy) <= 0:
                return None
            
            else:
                return historicalData
            
        else:
            return None
    
    def checkNewAppliance(self, historicalData):
        '''Checks if the data will append or insert a new appliance. False = not new True = new appliance'''
        
        import HistoricalData
        
        # Retrieve the device ID in the database if one exists
        deviceId = HistoricalData.getDeviceId(historicalData.name, historicalData.applianceId, historicalData.sensorType)
        
        if deviceId is None:
            # No ID found and therefore one would be created on insert
            return True
        
        else:
            # Device ID found and data will be appended
            return False
    