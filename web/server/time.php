<?php
	/*
		This file is part of Energy@Home.
		Copyright (C) 2009 Danny Tsang
		
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
	
	// Get data based on time.
	function timeGraph()
	{
		include 'db.php';
		
		// Instantiate array in case energy data was not requested
		$data = array();
		
		// Check if an update was requested
		if (isset($_GET['lastEnergyDataPoint']))
		{
			$data = updateTimeGraphEnergy($_GET['displayRange'], $_GET['parameter']);
		}
		else
		{
			$data = timeGraphEnergy($_GET['displayRange'], $_GET['parameter']);
		}
		
		// Encode array to JSON format
		return json_encode($data);
	}
	
	/*
	 * $range select range to display e.g "1" day, "20" hours
	 * $timeScale units of range e.g "day", "month"
	 */
	function timeGraphEnergy($range, $timeScale)
	{
		include 'config.php';
		include 'general.php';
		include 'time_sql.php';
		
		// Get all the appliances and channels per appliance to retrieve data for
		$applianceChannels = getDeviceChannels();
		$applianceArray = array();
		
		$count = 0;
		
		while ($row = mysqli_fetch_array($applianceChannels))
		{
			// Get channel ID
			$channelId = $row[$CHANNEL_ID_PK_FIELD_NAME];
			
			/* Only average data if time frame is not for an hour.
			 * Hour times return raw data and therefore are not grouped
			 * and averaged to reduce data when AJAX 'GET' request is sent
			 */
			$query = getTimeSql($channelId, $range, $timeScale, null);
			
			$result = executeQuery($query);
			
			$seriesArray;
			
			if ($row[$CHANNEL_FIELD_NAME] != "temp")
			{
				$seriesArray = array("chId" => $channelId, "label" => $row[$APPLIANCE_DISPLAY_NAME_FIELD_NAME], 
								"lines" => array("fill" => true), "color" => $count, "data" => convertResultToArray($result));
			}
			else
			{
				$seriesArray = array("chId" => $row[$CHANNEL_ID_PK_FIELD_NAME], "label" => 'Temperature', "yaxis" => 2, 
						"color" => 1, "data" => convertResultToArray($result));
			}
			
			array_push($applianceArray, $seriesArray);
			
			$count++;
			// Ensure 1 is always the temperature colour because it's blue
			if ($count == 1)
			{
				$count++;
			}
		}
		
		return $applianceArray;
	}
	
	/*
	 * $range select range to display e.g "1" day, "20" hours
	 * $timeScale units of range e.g "day", "month"
	 */
	function updateTimeGraphEnergy($range, $timeScale)
	{
		include 'config.php';
		include 'general.php';
		include 'time_sql.php';
		
		// Get all the appliances to retrieve data for
		$applianceChannels = getDeviceChannels();
		$applianceArray = array();
		
		while ($row = mysqli_fetch_array($applianceChannels))
		{
			// Get channel ID
			$channelId = $row[$CHANNEL_ID_PK_FIELD_NAME];
			// Check if the appliance last datapoint was passed
			if(isset($_GET["lastEnergyDataPoint_" . $channelId]))
			{
				// Get datapoint for channel
				$lastDataPoint = $_GET["lastEnergyDataPoint_" . $row[$CHANNEL_ID_PK_FIELD_NAME ]];
				
				// Get SQL query
				$query = getTimeSql($channelId, $range, $timeScale, $lastDataPoint);
				$result = executeQuery($query);
				
				$seriesArray = array("chId" => $channelId, "data" => convertResultToArray($result));
				
				array_push($applianceArray, $seriesArray);
			}
		}
		
		return $applianceArray;
	}
?>
