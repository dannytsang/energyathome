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
from xml.dom import minidom, Node
from xml.parsers.expat import ExpatError

from historical_data import *


class Parser:

    def __init__(self):
        # Instantiate _LOGGER
        self._LOGGER = logging.getLogger(__name__)

    # Used for debugging with example files. May be used in the future
    def parse_xml_file(self, xml_file):
        """Parse XML file and return HistoricalData object.
        Expects file path in full or relative to this file."""

        try:
            xml_doc = minidom.parse(xml_file)
            self._LOGGER.info("XML parsed successfully")

            return self.process_data(xml_doc)

        except ExpatError:
            self._LOGGER.error("XML parse error with xml : " + xml_file)

            return None

    # Parse XML string and return HistoricalData class
    def parse_xml(self, xml_string):
        """Parse XML string and return HistoricalData object."""

        try:
            xml_doc = minidom.parseString(xml_string)
            self._LOGGER.info("XML parsed successfully")

            return self.process_data(xml_doc)

        except ExpatError:
            try:
                self._LOGGER.error("XML parse error with xml string: " + xml_string)
            except TypeError as te:
                self._LOGGER.error("XML parse error with xml string: " + chr(x) for x in xml_string)

            return None

    # Check which type of XML was received
    def process_data(self, xml_doc):
        """Determine how to handle the XML data that was received"""

        is_current_data = self.is_current_xml_data(xml_doc)

        if bool(is_current_data):
            return self.get_current_xml_data(xml_doc)

        else:
            return None

    # Checks if parsed XML is current data or historical data
    def is_current_xml_data(self, xml_doc):
        """Checks if the xml data is current or historical.
        CurrentCost CC128 sends current power and temperature data every 6 secs.
        Every 1 minute past the hour e.g 5:01 it sends historical data from the
        last hour which contains different xml nodes.
        Returns True if it's current data and false if it's historical."""

        if xml_doc is not None:
            # Find element which only appears in historical XML data
            check = xml_doc.getElementsByTagName('hist')

            if check.length > 0:
                self._LOGGER.info('Historical XML Data Found')

                return False
            else:
                self._LOGGER.info('Current XML Data Found')

                return True
        else:
            return None

    # Create HistoricalData object from parse XML document
    def get_current_xml_data(self, xml_doc):
        """Creates and populates HistoricalData from xml data."""

        # Instantiate HistoricalData object.
        data = HistoricalData()

        if xml_doc is not None:
            for msgNode in xml_doc.getElementsByTagName('msg'):
                # print msgNode.toxml()
                data_node = msgNode.childNodes
                # Populate object with data under the parent node
                for i in range(0, data_node.length):
                    try:
                        if data_node[i].nodeName == 'src':
                            self._LOGGER.info(str(i) + ': name=' + data_node[i].firstChild.nodeValue)
                            data.name = data_node[i].firstChild.nodeValue
                        elif data_node[i].nodeName == 'dsb':
                            self._LOGGER.info(str(i) + ': dsb=' + data_node[i].firstChild.nodeValue)
                            data.dsb = int(data_node[i].firstChild.nodeValue)
                        elif data_node[i].nodeName == 'id':
                            self._LOGGER.info(str(i) + ': appliance id=' + data_node[i].firstChild.nodeValue)
                            data.channel_frequency = int(data_node[i].firstChild.nodeValue)
                        elif data_node[i].nodeName == 'sensor':
                            self._LOGGER.info(str(i) + ': sensor=' + data_node[i].firstChild.nodeValue)
                            data.applianceId = data_node[i].firstChild.nodeValue
                        elif data_node[i].nodeName == 'type':
                            self._LOGGER.info(str(i) + ': type=' + data_node[i].firstChild.nodeValue)
                            data.sensorType = int(data_node[i].firstChild.nodeValue)
                        elif data_node[i].nodeName == 'time':
                            self._LOGGER.info(str(i) + ': time=' + str(data_node[i].firstChild.nodeValue))
                            data.time = data_node[i].firstChild.nodeValue
                        elif data_node[i].nodeName == 'tmpr':
                            self._LOGGER.info(str(i) + ': tmpr=' + data_node[i].firstChild.nodeValue)
                            data.temperature = float(data_node[i].firstChild.nodeValue)
                        # Match any channel
                        elif data_node[i].nodeName[:2] == 'ch':
                            self._LOGGER.info(str(i) + ': ch' + data_node[i].nodeName[2:] + '=' + self.get_xml_channel(
                                data_node[i].childNodes))
                            data.energy[data_node[i].nodeName] = int(self.get_xml_channel(data_node[i].childNodes))

                    except AttributeError:
                        self._LOGGER.error('Skipped due to data error: ' + str(data_node[i].nodeName))

                    except ValueError:
                        self._LOGGER.error('Skipped due to data error: ' + str(data_node[i].nodeName))

        return data

    # Currently unused
    def get_xml_channel(self, channel_node):

        for i in range(0, channel_node.length):
            try:
                if channel_node[i].nodeName == 'watts':
                    return channel_node[i].firstChild.nodeValue

            except AttributeError:
                self._LOGGER.error('skipped: ' + str(channel_node[i].nodeName))
        # Return node value in watts
        return 0
