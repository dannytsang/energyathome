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

import math
from datetime import datetime, timedelta, date

import HistoricalData
import Debug
from database import MySQL
from config.Config import ConfigManager
from database.DatabaseException import ConnectionException

class CheckLiveTriggers:

    def __init__(self):
        # Instantiate config manager
        self.CONFIG = ConfigManager()
        # Get logger instance
        self.LOGGER = Debug.getLogger("energyathome.datalogger.datatrigger")
    
    def checkTriggers(self, historicalData):
        '''Check if data received meets any one trigger conditions.
        Returns true if it's met'''
        
        trigger = False
           
        # Get last recorded data point. Used for trigger information
        try:
            previousDataPoint = HistoricalData.getLastHistoricalData(historicalData)
            
        except ConnectionException as ce:
            raise ce
        
        # Check if there was data in DB
        if previousDataPoint is not None:
            try:
                # Get all channel data
                channel = ""
                for key, value in previousDataPoint.energy.iteritems():
                    channel += key + "=" + str(value) + "w "
                
                self.LOGGER.info("Last data point for " + previousDataPoint.name +\
                " app_id=" + str(previousDataPoint.applianceId) + " type=" +\
                str(previousDataPoint.sensorType) + " " + "at " +\
                str(previousDataPoint.time) + " was " + channel +\
                str(previousDataPoint.temperature) + "c")
                
                # Check timeout
                timeout = self.checkTimeTrigger(previousDataPoint)
                if timeout is True:
                    trigger = True
                
                # Check energy variation
                energy = self.checkEnergyTrigger(historicalData, previousDataPoint)
                if energy is True:
                    trigger = True
                
                # Check temperature variation
                temp = self.checkTemperatureTrigger(historicalData, previousDataPoint)
                if temp is True:
                    trigger = True
                
            except AttributeError as ae:
                self.LOGGER.error("Caught Error:" + str(ae))
                trigger = False
            
        else:
            # No previous data point found
            self.LOGGER.info("No data history for device " + historicalData.name +\
            " on app_id=" + str(historicalData.applianceId) +\
            " type=" + str(historicalData.sensorType))
            trigger = True
        
        # Historial data existed but no conditions were met.
        return trigger
    
    def checkTimeTrigger(self, previousDataPoint):
        '''Returns true if time from last datapoint exceeded the maximum'''
        
        # Check timeout trigger condition first as it's most common condition to
        # trigger a save point. Ignoring device time so using system time
        if (datetime.today() - previousDataPoint.time) >= timedelta(seconds = self.CONFIG.getIntConfig("Trigger", "timeout")):
            self.LOGGER.info("Timeout trigger condition met with " +\
            str(datetime.today() - previousDataPoint.time) + " delta")
            return True
        
        else:
            return False
    
    def checkEnergyTrigger(self, historicalData, previousDataPoint):
        '''Returns true if the energy difference from the previous value is exceeded'''
        
        # Check energy variation. Get absolute value reguardless of positive / negative value
        # Must loop through each channel
        for key, value in historicalData.energy.iteritems():
            if previousDataPoint.energy.get(key, None) is not None:
                # Calculate the difference from last data point and the new one
                energyDiff = math.fabs(value) - previousDataPoint.energy[key]
                
                if energyDiff >= self.CONFIG.getFloatConfig("Trigger", "energyvariation"):
                    self.LOGGER.info("Energy trigger condition met with " + str(key) + " " +\
                    str(energyDiff) + "w delta")
                    return True
                
            else:
                # energy value did not exist in previous reading
                return True
        
        # Deliberate fall through to return false
        return False
    
    def checkTemperatureTrigger(self, historicalData, previousDataPoint):
        '''Returns true if the temperature difference from the previous value is exceeded'''
        
        # Check temperature variation. Get absolute value reguardless of positive / negative value
        tempDiff = math.fabs(historicalData.temperature - previousDataPoint.temperature)
        
        if tempDiff > self.CONFIG.getFloatConfig("Trigger", "temperatureVariation"):
            self.LOGGER.info("Temperature trigger condition met with " +\
            str(tempDiff) + "c delta")
            return True
        
        else:
            return False
    