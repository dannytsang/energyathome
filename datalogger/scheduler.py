#
#	This file is part of Energy@Home.
#	Copyright (C) 2010 Danny Tsang
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
import threading

from config.Config import ConfigManager

_LOGGER = logging.getLogger(__name__)


class JobChecker(threading.Thread):
    """Scheduler which calls task function containing the jobs to run"""
    CONFIG = ConfigManager()

    def __init__(self):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        # Set delay interval in minutes
        self._interval = self.CONFIG.get_int_config("Scheduler", "checkInverval") * 60

    def setInterval(self, interval):
        """Set the number of seconds to sleep between tasks"""

        self._interval = interval

    def stop(self):
        """Stop this thread"""

        _LOGGER.info("Stopping Job Checker")
        self._finished.set()

    def run(self):
        """Main loop which calls the task function unless it is told to stop"""

        _LOGGER.info("Starting Job Checker")

        while 1:
            if self._finished.isSet(): return
            self.task()

            # sleep for interval or until shutdown
            self._finished.wait(self._interval)

    def task(self):
        """Task contains the code body which will be executed at specific intervals set in the config"""

        pass
