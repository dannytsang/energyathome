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

from xml.dom import minidom, Node
from xml.parsers.expat import ExpatError

import Debug
from HistoricalData import *

class Parser:
    
    def __init__(self):
        # Instantiate Logger
        self.LOGGER = Debug.getLogger("energyathome.datalogger.xmlparser")

    # Used for debugging with example files. May be used in the future
    def parseXMLFile(self, xmlFile):
        '''Parse XML file and return HistoricalData object.
        Expects file path in full or relative to this file.'''

        try:
            xmlDoc = minidom.parse(xmlFile)
            self.LOGGER.info("XML parsed successfully")
            
            return self.processData(xmlDoc)
        
        except ExpatError:
            self.LOGGER.error("XML parse error with xml : " + xmlFile)
            
            return None

    # Parse XML string and return HistoricalData class
    def parseXML(self, xmlString):
        '''Parse XML string and return HistoricalData object.'''

        try:
            xmlDoc = minidom.parseString(xmlString)
            self.LOGGER.info("XML parsed successfully")
            
            return self.processData(xmlDoc)
        
        except ExpatError:
            self.LOGGER.error("XML parse error with xml string: " + xmlString)
            
            return None
        
    # Check which type of XML was received
    def processData(self, xmlDoc):
        '''Determine how to handle the XML data that was received'''

        isCurrentData = self.isCurrentXMLData(xmlDoc)

        if bool(isCurrentData):
            return self.getCurrentXMLData(xmlDoc)
        
        else:
            return None

    # Checks if parsed XML is current data or historical data
    def isCurrentXMLData(self, xmlDoc):
        '''Checks if the xml data is current or historical.
        CurrentCost CC128 sends current power and temperature data every 6 secs.
        Every 1 minute past the hour e.g 5:01 it sends historical data from the
        last hour which contains different xml nodes.
        Returns True if it's current data and false if it's historical.'''

        if xmlDoc is not None:
            # Find element which only appears in historical XML data
            check = xmlDoc.getElementsByTagName('hist')

            if check.length > 0:
                self.LOGGER.info('Historical XML Data Found')
                
                return False
            else:
                self.LOGGER.info('Current XML Data Found')
                
                return True
        else:
            return None
        
    # Create HistoricalData object from parse XML document
    def getCurrentXMLData(self, xmlDoc):
        '''Creates and populates HistoricalData from xml data.'''
        
        # Instantiate HistoricalData object.
        data = HistoricalData()
        
        if xmlDoc is not None:
            for msgNode in xmlDoc.getElementsByTagName('msg'):
                #print msgNode.toxml()
                dataNode = msgNode.childNodes
                # Populate object with data under the parent node
                for i in range(0, dataNode.length):
                    try:
                        if dataNode[i].nodeName == 'src':
                            self.LOGGER.info(str(i) + ': name=' + dataNode[i].firstChild.nodeValue)
                            data.name = dataNode[i].firstChild.nodeValue
                        elif dataNode[i].nodeName == 'dsb':
                            self.LOGGER.info(str(i) + ': dsb=' + dataNode[i].firstChild.nodeValue)
                            data.dsb = int(dataNode[i].firstChild.nodeValue)
                        elif dataNode[i].nodeName == 'id':
                            self.LOGGER.info(str(i) + ': appliance id=' + dataNode[i].firstChild.nodeValue)
                            data.channel_frequency = int(dataNode[i].firstChild.nodeValue)
                        elif dataNode[i].nodeName == 'sensor':
                            self.LOGGER.info(str(i) + ': sensor=' + dataNode[i].firstChild.nodeValue)
                            data.applianceId = dataNode[i].firstChild.nodeValue
                        elif dataNode[i].nodeName == 'type':
                            self.LOGGER.info(str(i) + ': type=' + dataNode[i].firstChild.nodeValue)
                            data.sensorType = int(dataNode[i].firstChild.nodeValue)
                        elif dataNode[i].nodeName == 'time':
                            self.LOGGER.info(str(i) + ': time=' + str(dataNode[i].firstChild.nodeValue))
                            data.time = dataNode[i].firstChild.nodeValue
                        elif dataNode[i].nodeName == 'tmpr':
                            self.LOGGER.info(str(i) + ': tmpr=' + dataNode[i].firstChild.nodeValue)
                            data.temperature = float(dataNode[i].firstChild.nodeValue)
                        # Match any channel
                        elif dataNode[i].nodeName[:2] == 'ch':
                            self.LOGGER.info(str(i) + ': ch' + dataNode[i].nodeName[2:] + '=' + self.getXMLChannel(dataNode[i].childNodes))
                            data.energy[dataNode[i].nodeName] = int(self.getXMLChannel(dataNode[i].childNodes))
                    
                    except AttributeError:
                        self.LOGGER.error('Skipped due to data error: ' + str(dataNode[i].nodeName))
                    
                    except ValueError:
                        self.LOGGER.error('Skipped due to data error: ' + str(dataNode[i].nodeName))
        
        return data

    # Currently unused
    def getXMLChannel(self, channelNode):
        
        for i in range(0, channelNode.length):
            try:
                if channelNode[i].nodeName == 'watts':
                    return channelNode[i].firstChild.nodeValue
                
            except AttributeError:
                self.LOGGER.error('skipped: ' + str(channelNode[i].nodeName))
        # Return node value in watts
        return 0
    