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

import serial
import logging

from config.Config import ConfigManager

_LOGGER = logging.getLogger(__name__)


class DeviceManager():
    INSTANCE = None

    # Singleton pattern
    def __new__(cls, *args, **kwargs):
        if not cls.INSTANCE:
            cls.INSTANCE = super(DeviceManager, cls).__new__(
                cls, *args, **kwargs)

        return cls.INSTANCE

    def __init__(self):

        self.COMM = serial.Serial()

        # Create Config manager
        self.CONFIG = ConfigManager()

    # Open serial connection
    def open(self):
        """Open connection to USB to serial port"""

        self.COMM.port = self.CONFIG.getConfig("SerialConnection", "serialport")
        self.COMM.baudrate = self.CONFIG.getIntConfig("SerialConnection", "baudrate")
        self.COMM.parity = self.CONFIG.getConfig("SerialConnection", "parity")
        self.COMM.timeout = None
        self.COMM.bytesize = self.CONFIG.getIntConfig("SerialConnection", "bytesize")

        if not self.COMM.isOpen():
            _LOGGER.info('Establishing connection to device')
            self.COMM.open()
        else:
            _LOGGER.info('Connection already opened')

        _LOGGER.info('Device connected:' + str(self.COMM.isOpen()))

    # Close serial connection
    def close(self):
        """Close connection to USB to Serial port"""

        if (self.COMM.isOpen):
            _LOGGER.info('Closing device connection')
            self.COMM.close()

        _LOGGER.info('Device connection closed')

    # Get data from serial connection
    def read(self):
        """Read data from USB to Serial device. Connection must be established."""

        data = self.COMM.readline()
        if len(data) > 0:
            _LOGGER.debug('serial data: ' + data)
            return data
