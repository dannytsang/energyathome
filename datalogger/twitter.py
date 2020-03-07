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

import sys
import os

from datetime import datetime
from datetime import timedelta

import debug
from database import MySQL
from config.Config import ConfigManager

class Twitter:
    
    def __init__(self):
        # Instantiate logger
        self.LOGGER = debug.getLogger("energyathome.datalogger.twitter")
        # Configuration Manager
        self.CONFIG = ConfigManager()
        
        self.LOGGER.debug("Adding to system path: " + os.path.dirname(os.path.abspath(__file__)) + os.sep + "python-twitter")
        sys.path.append(os.path.dirname(os.path.abspath(__file__)) + os.sep + "python-twitter")
        
        currentTime = datetime.now()
        
        self.LAST_HOURLY_POST = currentTime.strftime("%H")
        
        self.TWITTER = __import__("twitter")

    def postHourlySummary(self):
        '''Posts an hourly summary to Twitter'''
        
        # Get current system time
        currentTime = datetime.now()
        # create time difference to be used to work out time period
        timeDiff = timedelta(hours=1)
        # Get current hour
        currentHour = currentTime.strftime("%H")
        # If current hour does not match last post hour then it's been a new hour since last post
        if(currentHour != self.LAST_HOURLY_POST):
            debug.writeOut("Hourly condtion met (" + currentHour + " != " + self.LAST_HOURLY_POST + "). Posting to Twitter")
            # Create SQL to get data for tweet
            sql = "SELECT COALESCE(ROUND(AVG(energy), 2), 0), " +\
            "COALESCE(MAX(energy), 0), COALESCE(ROUND(AVG(temperature), 1), 0) " +\
            "FROM historical_data WHERE date_time >= ADDDATE(NOW(), INTERVAL -1 HOUR)"
            self.LOGGER.debug(sql)
            
            # Get statistics from DB
            stats = MySQL.executeOneUpdate(sql, None)
            # Create tweet
            message = (currentTime - timeDiff).strftime("%H:%M") + "-" + currentTime.strftime("%H:%M") +\
            " Summary: " + str(stats[0]) + "w was used." +\
            " Energy usage peaked at " + str(stats[1]) + "w" +\
            ". The average temperature was " + str(stats[2]) + "c."
            
            # Check if tweet should be a Direct Message or just a tweet
            if self.CONFIG.getBooleanConfig("Twitter", "directMessagePost"):
                self.postDirectMessage(self.CONFIG.getBooleanConfig("Twitter", "directMessageUser"), message)
            else:
                # Post message to twitter
                self.tweet(message)
                
            # Set last hourly post to current hour
            self.LAST_HOURLY_POST = currentHour

    def postDailySummary(self):
        '''Posts a daily summary to Twitter'''
        
        # Get current minutes from system time
        currentTime = datetime.now()
        # create time difference to be used to work out time period
        timeDiff = timedelta(days=1)
        # Get current minutes
        currentHour = currentTime.strftime("%H")
        # Check if the hours of the time is 00 which means midnight and the current day
        # has changed
        if(currentHour == "00" and (self.LAST_DAY_POST == "" or currentTime.strftime("%d") != self.LAST_DAY_POST)):
            debug.writeOut("Daily condition met (hour of day:" + currentHour + " == 00 && day:" + currentTime.strftime("%d") + " == " + self.LAST_DAY_POST + "). Posting to Twitter")
            # Create SQL to get data for tweet
            sql = " SELECT COALESCE(ROUND(AVG(energy), 2), 0), COALESCE(MAX(energy), 0), COALESCE(ROUND(AVG(temperature), 1), 0) FROM historical_data WHERE date_time >= ADDDATE(NOW(), INTERVAL -1 DAY)"
            self.LOGGER.debug(sql)
            
            # Get statistics from DB
            stats = MySQL.executeOneUpdate(sql, None)
            # Create tweet
            message = (currentTime - timeDiff).strftime("%d-%b-%Y") + " Summary: " + str(stats[0]) +\
            "w was used. " +\
            "Energy usage peaked at " + str(stats[1]) + "w. " +\
            "The average temperature was " + str(stats[2]) + "c."
            
            # Save new day of tweet
            self.LAST_DAY_POST = currentTime.strftime("%d")
            
            # Check if tweet should be a Direct Message or just a tweet
            if self.CONFIG.getBooleanConfig("Twitter", "directMessagePost"):
                self.postDirectMessage(self.CONFIG.getBooleanConfig("Twitter", "directMessageUser"), message)
            else:
                # Post message to twitter
                self.tweet(message)
                
    def tweet(self, message):
        '''Tweet a message'''
        
        # Connect to Twitter
        twit = self.TWITTER.Api(username=self.CONFIG.getBooleanConfig("Twitter", "username"), 
                                password=self.CONFIG.getBooleanConfig("Twitter", "password"))
        return twit.PostUpdate(message)
        
    def postDirectMessage(self, user, message):
        '''Direct Message a user'''
        
        twit = self.TWITTER.Api(username=self.CONFIG.getBooleanConfig("Twitter", "username", 
                                password=self.CONFIG.getBooleanConfig("Twitter", "password")))
                                
        return twit.PostDirectMessage(user, message)
    
    def getTweets(self):
        '''Get tweet @ replies from account'''
        
        twit = self.TWITTER.Api(username=self.CONFIG.getBooleanConfig("Twitter", "username", 
                                password=self.CONFIG.getBooleanConfig("Twitter", "password")))
        
        return twit.GetReplies()
    
    def getDirectMessages(self):
        '''Get tweet @ replies from account'''
        
        twit = self.TWITTER.Api(username=self.CONFIG.getBooleanConfig("Twitter", "username", 
                                password=self.CONFIG.getBooleanConfig("Twitter", "password")))
        
        return twit.GetDirectMessages()