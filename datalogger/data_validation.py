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

import logging
from config.Config import ConfigManager
from database.database_exception import ConnectionException

_LOGGER = logging.getLogger(__name__)


class CheckLiveData:
    
    def __init__(self):
        # Instantiate config manager
        self.CONFIG = ConfigManager()
        
    # Validate data captured from device
    def validate_data(self, historicalData):
        """Checks historical data fall within parameter which is customised in the config file.
        Returns results in a tuple size of 2.
        [0] = True or False depending if validation was successful or not
        [1] = HistoricalData.HistoricalData class of sanitised data"""
        
        valid = True
        
        # Get maximum appliance Id value
        max_app_id = self.CONFIG.get_int_config("Tolerence", "maxApplianceId")
        
        try:
            # If max app id is greater than 0 then checking for app id is enabled
            if max_app_id is not None and max_app_id >= 0:
                if self.check_appliance_id(historicalData) is False:
                    valid = False
            
            # Check device name matches in the config
            device_names = self.CONFIG.get_config("Tolerence", "allowedDeviceNames")
            # If device names are defined then perform a match
            if device_names is not None and device_names != "":
                if self.check_device_name(historicalData) is False:
                    valid = False
            
            if self.CONFIG.get_boolean_config("Tolerence", "allowNewAppliances") is False:
                # If it returns true then it's a new appliance and should be ignored
                if self.check_new_appliance(historicalData) is True:
                    valid = False
                    _LOGGER.info("Appliance ID " + str(historicalData.applianceId) + " was not stored due to allowNewAppliances = False")
                    
            # Check channel names
            if self.CONFIG.get_boolean_config("Tolerence", "allowBlankChannelNames") is False:
                test = self.check_channel_names(historicalData)
                # If test returned None then it failed validation.
                # Otherwise assign returned Historical Data because it may have changed some attributes
                if test is None:
                    valid = False
                    
                else:
                    historicalData = test
            
            # Check channels
            if self.CONFIG.get_boolean_config("Tolerence", "check_channels") is True and historicalData.applianceId is not None:
                test = self.check_channels(historicalData)
                # If test returned None then it failed validation.
                # Otherwise assign returned Historical Data because it may have changed some attributes
                if test is None:
                    valid = False
                else:
                    historicalData = test
        except ConnectionException as ce:
            raise ce
        
        return (valid, historicalData)
    
    def check_appliance_id(self, historicalData):
        """Checks if appliance ID falls within a set range"""
        
        # Get maximum appliance Id value
        max_app_id = self.CONFIG.get_int_config("Tolerence", "maxApplianceId")
        
        try:
            # Check if appliance number exceeds maximum
            if int(historicalData.applianceId) > max_app_id:
                _LOGGER.info("Appliance ID " + str(historicalData.applianceId) + " > " + str(max_app_id))
                return False
            
            else:
                return True
            
        except ValueError as ve:
            _LOGGER.info("Check max App ID failed: " + str(historicalData.applianceId) + " > " + str(max_app_id))
            return False
            
        except AttributeError as ae:
            _LOGGER.info("Check max App ID failed: No attribute Error:" + str(ae))
            return False
        except ConnectionException as ce:
            raise ce
    
    def check_device_name(self, historicalData):
        """Checks device name is in specified list"""
        
        # Get device names from config
        device_names = self.CONFIG.get_config("Tolerence", "allowedDeviceNames")
        
        # Convert string of device names into a list
        device_name_split = device_names.split(",")
        
        # Get case sensitive match from config
        case_sensitive_match = self.CONFIG.get_config("Tolerence", "caseSensitiveDeviceNames")
        
        match = False
        
        for device in device_name_split:
            if case_sensitive_match:
                if device.lower() == historicalData.name.lower():
                    match = True
                    break
                
            else:
                if device == historicalData.name:
                    match = True
                    break
        
        if match is False:
            _LOGGER.info("No matches found for device name '" + str(historicalData.name) + "'")
            return False
        
        else:
            return True
    
    def check_channel_names(self, historicalData):
        """Checks channel names are valid"""
        
        if None in historicalData.energy:
            # Remove None key value from energy
            _LOGGER.info("Found null channel name with value " + str(historicalData.energy[""]))
            del historicalData.energy[None]
            
        if "" in historicalData.energy:
            _LOGGER.info("Found blank channel name with value " + str(historicalData.energy[""]))
            del historicalData.energy[""]
            
        # Check there are energy values left after cleansing
        if len(historicalData.energy) <= 0:
            return None
        else:
            return historicalData
    
    def check_channels(self, historicalData):
        """Checks channels are within specified list"""
        
        # Get device containing appliances and related channels
        allowed_channels = self.CONFIG.get_config_category("device_" + historicalData.name)
        
        if allowed_channels is not None:
            # Store the channel (keys) which are invalid to remove safely rather than iterating from a mutable dictionary
            keysToRemove = []
            
            # Loop through all energy data to check if channel is valid
            for key, value in historicalData.energy.iteritems():
                try:
                    channels = allowed_channels["app_" + str(historicalData.applianceId)]
                    if channels is None and allowed_channels["allowundefined"] == "False":
                        # Add to removal list because non defined channels are not allowed
                        keysToRemove.append(key)
                        
                    elif key is not None and channels is not None and key not in channels:
                        # Remove invalid channel
                        keysToRemove.append(key)
                        _LOGGER.info("Found invalid channel '" + str(key) + "' for appliance " +
                                     str(historicalData.applianceId) + " containing " + str(historicalData.energy[key]))
                        
                except KeyError as ke:
                    # Appliance is not defined with a channel list. Check config for what to do
                    # For some reason getting the dictionary back of a config section returns all values as strings
                    if allowed_channels["allowundefined"] == "False":
                        # Add to removal list
                        keysToRemove.append(key)
            
            # Loop through list of keys which failed validation
            for key in keysToRemove:
                _LOGGER.info("Deleting " + str(key))
                del historicalData.energy[key]
                
            # Check there are energy values left after cleansing
            if len(historicalData.energy) <= 0:
                return None
            
            else:
                return historicalData
            
        else:
            return None
    
    def check_new_appliance(self, historicalData):
        """Checks if the data will append or insert a new appliance. False = not new True = new appliance"""
        
        import historical_data
        
        # Retrieve the device ID in the database if one exists
        device_id = historical_data.get_device_id(historicalData.name, historicalData.applianceId, historicalData.sensorType)
        
        if device_id is None:
            # No ID found and therefore one would be created on insert
            return True
        
        else:
            # Device ID found and data will be appended
            return False
    