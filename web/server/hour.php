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
	function hourGraph()
	{
		include 'config.php';
		include 'db.php';
		
		// Get energy data
		$data = hourGraphEnergy($_GET['parameter']);
		
		return json_encode($data);
	}
	
	/*
	 * $timeScale Time frame the user has selected e.g Today, Yesterday, Week, Month, etc
	 */
	function hourGraphEnergy($timeScale)
	{
		include 'config.php';
		include 'general.php';
		
		// Get all the appliances to retrieve data for
		$applianceChannels = getDeviceChannels();
		$applianceArray = array();
		
		$count = 0;
		
		// Array to store the number channels each appliance has
		//$applianceChannelCount = countChannelsPerAppliance($applianceChannels);
		
		// Loop through results again to build data to be returned
		while ($row = mysql_fetch_array($applianceChannels))
		{
			$where = getHourSqlWhereClause($row[$CHANNEL_ID_PK_FIELD_NAME], $timeScale);
			$group = getHourSqlGroupByClause();
			
			$query = "SELECT HOUR(" . $DATE_TIME_FIELD_NAME . "), AVG(" . $DATA_FIELD_NAME . "), " . $UNIT_FIELD_NAME . " " .
						"FROM " . $DATA_TABLE_FIELD_NAME . " " . $where . $group;
			
			$result = executeQuery($query);
			
			$seriesArray = array("chId" => $row[$CHANNEL_ID_PK_FIELD_NAME], "label" => $row[$APPLIANCE_DISPLAY_NAME_FIELD_NAME], 
							"color" => $count, "data" => convertResultToArray($result));
			
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
	
	function getHourSqlWhereClause($channelId, $timeScale)
	{
		// Reference config file
		include 'config.php';
		
		$where = "";
		
		// Add channel ID to where clause if it's set
		if (isset($channelId))
		{
			// Check if an And is needed if the $where variable length is greater than 0
			if(strlen($where) > 0)
			{
				$where .= " AND ";
			}
			
			$where .= $CHANNEL_ID_FK_FIELD_NAME . " = " . $channelId . " ";
		}
		
		// Only displays midnight to the current hour.
		if ($timeScale == "Today")
		{
			// Check if an And is needed if the $where variable length is greater than 0
			if(strlen($where) > 0)
			{
				$where .= " AND ";
			}
			
			$where .= " DATE(" . $DATE_TIME_FIELD_NAME . ") = CURDATE() ";
		}
		// Displays the last full day
		elseif ($timeScale == "Yesterday")
		{
			// Check if an And is needed if the $where variable length is greater than 0
			if(strlen($where) > 0)
			{
				$where .= " AND ";
			}
			
			$where .= " DATE(" . $DATE_TIME_FIELD_NAME . ") = (CURDATE() - INTERVAL 1 DAY) ";
		}
		else
		{
			// Check if an And is needed if the $where variable length is greater than 0
			if(strlen($where) > 0)
			{
				$where .= " AND ";
			}
			
			$where .= " " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -1 " . $timeScale . ") ";
		}
		
		return " WHERE " . $where;
	}
	
	function getHourSqlGroupByClause()
	{
		// Reference config file
		include 'config.php';
		
		return " GROUP BY HOUR(" . $DATE_TIME_FIELD_NAME . ")";
	}
	
	/*
	 * Returns a list of devices and channels.
	 */
	function getDeviceChannels()
	{
		include 'config.php';
		
		$query = "SELECT c." . $CHANNEL_ID_PK_FIELD_NAME . ", c." . $CHANNEL_FIELD_NAME . ", CONCAT(d." . $APPLIANCE_DISPLAY_NAME_FIELD_NAME . 
				", CASE (SELECT COUNT(c2." . $CHANNEL_ID_PK_FIELD_NAME . ") FROM " . 
				$CHANNEL_TABLE_FIELD_NAME . " c2 WHERE c2." . 
				$APPLIANCE_ID_FK_FIELD_NAME . " = d." . $APPLIANCE_ID_FIELD_NAME . " AND c2.channel <> 'temp') WHEN 1 THEN '' ELSE CONCAT(' (', c." . $CHANNEL_FIELD_NAME . 
				", ')') END) AS display_name" . " FROM " . $APPLIANCE_TABLE_FIELD_NAME . " d LEFT JOIN " . $CHANNEL_TABLE_FIELD_NAME . 
				" c ON c." . $APPLIANCE_ID_FK_FIELD_NAME . " = d." . $APPLIANCE_ID_FIELD_NAME . " WHERE c." . $CHANNEL_FIELD_NAME . " <> 'temp' " .
				" ORDER BY d." . $APPLIANCE_APP_ID_FIELD_NAME;
		
		$result = executeQuery($query);
		
		return $result;
	}
?>
