<?php
	/*
		This file is part of Energy@Home.
		Copyright (C) 2011 Danny Tsang
		
		Energy@Home is free software: you can redistribute it and/or modify
		it under the terms of the GNU General Public License as published by
		the Free Software Foundation, either version 3 of the License, or
		(at your option) any later version.

		Energy@Home is distributed in the hope that it will be useful,
		but WITHOUT ANY WARRANTY; without even the implied warranty of
		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
		GNU General Public License for more details.

		You should have received a copy of the GNU General Public License
		along with Energy@Home.  If not, see <http://www.gnu.org/licenses/>.
	*/
	
	/*
	 * Returns a list of all the known appliances
	 */
	function getAllAppliances()
	{
		include 'config.php';
		
		$query = "SELECT * FROM " . $APPLIANCE_TABLE_FIELD_NAME . " ORDER BY " . $APPLIANCE_ID_FK_FIELD_NAME;
		
		$result = executeQuery($query);
		
		return $result;
	}
	
	/*
	 * Loops and counts the number of channels per appliance. The appliance ID is the key and the value holds the number of channels
	 */
	function countChannelsPerAppliance($results)
	{
		include 'config.php';
		
		// Array to store the number channels each appliance has
		$applianceChannelCount = array();
		
		// Loop through result to find appliances with multiple channels
		while ($row = mysql_fetch_array($results))
		{
			// If appliance does not exist, create a count of 1 channel.
			// Must convert appliance ID to string otherwise PHP will interpret it as an index instead of a key
			if(!array_key_exists(strval($row[$APPLIANCE_ID_FIELD_NAME]), $applianceChannelCount))
			{
				$applianceChannelCount[strval($row[$APPLIANCE_ID_FIELD_NAME])] = 1;
			}
			else
			{
				// Increment the number of channels for appliance
				$applianceChannelCount[strval($row[$APPLIANCE_ID_FIELD_NAME])] = $applianceChannelCount[strval($row[$APPLIANCE_ID_FIELD_NAME])] + 1;
			}
		}
		
		// Reset cursor to 0 record again
		mysql_data_seek($results, 0);
		
		return $applianceChannelCount;
	}
?>