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
import logging
from datetime import datetime, timedelta, date

import historical_data
from config.Config import ConfigManager
from database.database_exception import ConnectionException

# Instantiate _LOGGER
_LOGGER = logging.getLogger(__name__)


class CheckLiveTriggers:

    def __init__(self):
        # Instantiate config manager
        self.CONFIG = ConfigManager()

    def check_triggers(self, data):
        """Check if data received meets any one trigger conditions.
        Returns true if it's met"""
        trigger = False

        # Get last recorded data point. Used for trigger information
        try:
            previous_data_point = historical_data.get_last_historical_data(data)
        except ConnectionException as ce:
            raise ce

        # Check if there was data in DB
        if previous_data_point is not None:
            try:
                # Get all channel data
                channel = ""
                for key, value in previous_data_point.energy.items():
                    channel += key + "=" + str(value) + "w "

                _LOGGER.info("Last data point for " + previous_data_point.name + \
                             " app_id=" + str(previous_data_point.applianceId) + " type=" + \
                             str(previous_data_point.sensorType) + " " + "at " + \
                             str(previous_data_point.time) + " was " + channel + \
                             str(previous_data_point.temperature) + "c")

                # Check timeout
                timeout = self.check_time_trigger(previous_data_point)
                if timeout is True:
                    trigger = True

                # Check energy variation
                energy = self.check_energy_trigger(data, previous_data_point)
                if energy is True:
                    trigger = True

                # Check temperature variation
                temp = self.check_temperature_trigger(data, previous_data_point)
                if temp is True:
                    trigger = True

            except AttributeError as ae:
                _LOGGER.error("Error checking trigger", ae)
                trigger = False

        else:
            # No previous data point found
            _LOGGER.info("No data history for device " + data.name + \
                         " on app_id=" + str(data.applianceId) + \
                         " type=" + str(data.sensorType))
            trigger = True

        # Historical data existed but no conditions were met.
        return trigger

    def check_time_trigger(self, previous_data_point):
        """Returns true if time from last datapoint exceeded the maximum"""

        # Check timeout trigger condition first as it's most common condition to
        # trigger a save point. Ignoring device time so using system time
        if (datetime.today() - previous_data_point.time) >= timedelta(
                seconds=self.CONFIG.get_int_config("Trigger", "timeout")):
            _LOGGER.info("Timeout trigger condition met with " + str(datetime.today() - previous_data_point.time) +\
                         " delta")
            return True

        else:
            _LOGGER.info("Timeout trigger condition not met with " + str(datetime.today() - previous_data_point.time) +\
                         "delta")
            return False

    def check_energy_trigger(self, data, previous_data_point):
        """Returns true if the energy difference from the previous value is exceeded"""

        # Check energy variation. Get absolute value regardless of positive / negative value
        # Must loop through each channel
        for key, value in data.energy.items():
            if previous_data_point.energy.get(key, None) is not None:
                # Calculate the difference from last data point and the new one
                energy_diff = math.fabs(value) - previous_data_point.energy[key]

                if energy_diff >= self.CONFIG.get_float_config("Trigger", "energyvariation"):
                    _LOGGER.info("Energy trigger condition met with " + str(key) + " " + str(energy_diff) + "w delta")
                    return True

            else:
                # energy value did not exist in previous reading
                _LOGGER.debug("Energy trigger condition met. No previous energy value found")
                return True

        # Deliberate fall through to return false
        _LOGGER.debug("Energy trigger condition not met.")
        return False

    def check_temperature_trigger(self, data, previous_data_point):
        """Returns true if the temperature difference from the previous value is exceeded"""

        # Check temperature variation. Get absolute value regardless of positive / negative value
        temp_diff = math.fabs(data.temperature - previous_data_point.temperature)

        if temp_diff > self.CONFIG.get_float_config("Trigger", "temperatureVariation"):
            _LOGGER.info("Temperature trigger condition met with " + str(temp_diff) + "c delta")
            return True

        else:
            _LOGGER.debug("Temperature trigger condition not met with " + str(temp_diff) + "c delta")
            return False
