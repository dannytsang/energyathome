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
			$query = "";			
			
			/* Only average data if time frame is not for an hour.
			 * Hour times return raw data and therefore are not grouped
			 * and averaged to reduce data when AJAX 'GET' request is sent
			 */
			$query = getTimeSql($row[$CHANNEL_ID_PK_FIELD_NAME], $range, $timeScale);
			
			$result = executeQuery($query);
			
			$seriesArray;
			
			if ($row[$CHANNEL_FIELD_NAME] != "temp")
			{
				$seriesArray = array("chId" => $row[$CHANNEL_ID_PK_FIELD_NAME], "label" => $row[$APPLIANCE_DISPLAY_NAME_FIELD_NAME], 
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
		
		// Get all the appliances to retrieve data for
		$applianceChannels = getDeviceChannels();
		$applianceArray = array();
		
		while ($row = mysqli_fetch_array($applianceChannels))
		{
			// Check if the appliance last datapoint was passed
			if(isset($_GET["lastEnergyDataPoint_" . $row[$CHANNEL_ID_PK_FIELD_NAME ]]))
			{
				$lastDataPoint = $_GET["lastEnergyDataPoint_" . $row[$CHANNEL_ID_PK_FIELD_NAME ]];
				$where = updateSqlWhereClause($row[$CHANNEL_ID_PK_FIELD_NAME], $lastDataPoint);
				$group = getTimeSqlGroupClause($timeScale);
				$order = getTimeSqlOrderClause();
				
				$query = "SELECT UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000, ";
				/* Only average data if time frame is not for an hour.
				 * Hour times return raw data and therefore are not grouped
				 * and averaged to reduce data when AJAX 'GET' request is sent
				 */
				if ($timeScale != "Hour")
				{
					$query .= "AVG(" . $DATA_FIELD_NAME . ")";
				}
				else
				{
					$query .= $DATA_FIELD_NAME;
				}
				$query .= ", " . $UNIT_FIELD_NAME . " FROM " . $DATA_TABLE_FIELD_NAME . $where . $group . $order;
				$result = executeQuery($query);
				
				$seriesArray = array("chId" => $row[$CHANNEL_ID_PK_FIELD_NAME], "data" => convertResultToArray($result));
				
				array_push($applianceArray, $seriesArray);
			}
		}
		
		return $applianceArray;
	}
	
	/*
	 * $range select range to display e.g "1" day, "20" hours
	 * $timeScale units of range e.g "day", "month"
	 */
	function timeGraphEnergyOverlay($range, $timeScale)
	{
		include 'config.php';
		include 'constants.php';
		//include 'general.php';
		
		// Get all the appliances to retrieve data for
		$appliances = getAllAppliances();
		$applianceArray = array();
		
		$count = 0;
		
		while ($row = mysqli_fetch_array($appliances))
		{
			$where = "";
			$group = getTimeSqlGroupClause($timeScale);
			$order = getTimeSqlOrderClause();
			$hourDiff = 0;
			
			if ($timeScale == "Hour")
			{
				$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . ((int)$range * 2) . " HOUR) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " HOUR)";
				$hourDiff = $SECONDS_IN_HOUR * (int)$range;
			}
			elseif ($timeScale == "Day")
			{
				$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . ((int)$range * 2) . " Day) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Day) ";
				$hourDiff = $SECONDS_IN_DAY * (int)$range;
			}
			elseif ($timeScale == "Week")
			{
				$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . ((int)$range * 2) . " Week) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Week) ";
				$hourDiff = $SECONDS_IN_WEEK * (int)$range;
			}
			elseif ($timeScale == "Month")
			{
				$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . ((int)$range * 2) . " Month) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Month)";
				$hourDiff = $SECONDS_IN_MONTH * (int)$range;
			}
			elseif ($timeScale == "Year")
			{
				$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . ((int)$range * 2) . " Year) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Year) ";
				$hourDiff = $SECONDS_IN_YEAR * (int)$range;
			}
			else
			{
				echo "";
				return;
			}
			// execute query
			$query = "SELECT (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) + " . $hourDiff . ", ";
			if($timeScale != "Hour")
			{
				$query .= "AVG(" . $ENERGY_FIELD_NAME . ") ";
			}
			else
			{
				$query .= $ENERGY_FIELD_NAME . " ";
			}
			$query .= "FROM " . $DATA_TABLE_FIELD_NAME . " " . $where . $group . $order;
			$result = executeQuery($query);
			
			$seriesArray = array("appId" => "o" . $row[$APPLIANCE_ID_FIELD_NAME], "label" => 'Energy Overlay', "lines" => array("show" => true), "color" => $count * 2, "data" => convertResultToArray($result));
			
			array_push($applianceArray, $seriesArray);
			
			$count++;
			// Ensure 1 is always the temperature colour because it's blue
			if ($count == 1)
			{
				$count++;
			}
		}
		
		return $seriesArray;
	}
	
	/*
	 * $range select range to display e.g "1" day, "20" hours
	 * $timeScale units of range e.g "day", "month"
	 * $lastDataPoint Last timestamp in received in Unix timestamp
	 */
	function updateTimeGraphEnergyOverlay($range, $timeScale, $lastDataPoint)
	{
		include 'config.php';
		include 'constants.php';
		
		$where = "";
		$group = getTimeSqlGroupClause($timeScale);
		$order = getTimeSqlOrderClause();
		$hourDiff = 0;
		
		if ($timeScale == "Hour")
		{
			$where = "WHERE (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) >= (" . $lastDataPoint . " - (" . $SECONDS_IN_HOUR . " * " . $range . ")) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " HOUR)";
			$hourDiff = $SECONDS_IN_HOUR * (int)$range;
		}
		elseif ($timeScale == "Day")
		{
			$where = "WHERE (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) >= (" . $lastDataPoint . " - (" . $SECONDS_IN_DAY . " * " . $range . ")) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Day) ";
			$hourDiff = $SECONDS_IN_DAY * (int)$range;
		}
		elseif ($timeScale == "Week")
		{
			$where = "WHERE (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) >= (" . $lastDataPoint . " - (" . $SECONDS_IN_WEEK . " * " . $range . ")) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Week) ";
			$hourDiff = $SECONDS_IN_WEEK * (int)$range;
		}
		elseif ($timeScale == "Month")
		{
			$where = "WHERE (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) >= (" . $lastDataPoint . " - (" . $SECONDS_IN_MONTH . " * " . $range . ")) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Month)";
			$hourDiff = $SECONDS_IN_MONTH * (int)$range;
		}
		elseif ($timeScale == "Year")
		{
			$where = "WHERE (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) >= (" . $lastDataPoint . " - (" . $SECONDS_IN_YEAR . " * " . $range . ")) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Year) ";
			$hourDiff = $SECONDS_IN_YEAR * (int)$range;
		}
		else
		{
			echo "";
			return;
		}
		
		// execute query
		$query = "SELECT (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) + " . $hourDiff . ", ";
		if($timeScale != "Hour")
		{
			$query .= "AVG(" . $ENERGY_FIELD_NAME . ") ";
		}
		else
		{
			$query .= $ENERGY_FIELD_NAME . " ";
		}
		$query .= "FROM " . $DATA_TABLE_FIELD_NAME . " " . $where . $group . $order;
		$result = executeQuery($query);
		
		$seriesArray = array("label" => 'Energy Overlay', "data" => convertResultToArray($result));
		
		return $seriesArray;
	}
	
	/*
	 * $range select range to display e.g "1" day, "20" hours
	 * $timeScale units of range e.g "day", "month"
	 */
	function timeGraphTemperatureOverlay($range, $timeScale)
	{
		include 'config.php';
		include 'constants.php';
		
		$where = "";
		$group = getTimeSqlGroupClause($timeScale);
		$order = getTimeSqlOrderClause();
		$hourDiff = 0;
		
		if ($timeScale == "Hour")
		{
			$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . ((int)$range * 2) . " HOUR) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " HOUR)";
			$hourDiff = $SECONDS_IN_HOUR * (int)$range;
		}
		elseif ($timeScale == "Day")
		{
			$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . ((int)$range * 2) . " Day) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Day) ";
			$hourDiff = $SECONDS_IN_DAY * (int)$range;
		}
		elseif ($timeScale == "Week")
		{
			$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . ((int)$range * 2) . " Week) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Week) ";
			$hourDiff = $SECONDS_IN_WEEK * (int)$range;
		}
		elseif ($timeScale == "Month")
		{
			$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . ((int)$range * 2) . " Month) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Month)";
			$hourDiff = $SECONDS_IN_MONTH * (int)$range;
		}
		elseif ($timeScale == "Year")
		{
			$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . ((int)$range * 2) . " Year) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Year) ";
			$hourDiff = $SECONDS_IN_YEAR * (int)$range;
		}
		else
		{
			echo "";
			return;
		}
		// execute query
		$query = "SELECT (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) + " . $hourDiff . ", ";
		if($timeScale != "Hour")
		{
			$query .= "AVG(" . $TEMPERATURE_FIELD_NAME . ") ";
		}
		else
		{
			$query .= $TEMPERATURE_FIELD_NAME . " ";
		}
		$query .= "FROM " . $DATA_TABLE_FIELD_NAME . " " . $where . $group . $order;
		$result = executeQuery($query);
		
		$seriesArray = array("label" => 'Temperature Overlay', "yaxis" => 2, "lines" => array("show" => true), "color" => 3, "data" => convertResultToArray($result));
		
		return $seriesArray;
	}
	
	/*
	 * $range select range to display e.g "1" day, "20" hours
	 * $timeScale units of range e.g "day", "month"
	 * $lastDataPoint Last timestamp in received in Unix timestamp
	 */
	function updateTimeGraphTemperatureOverlay($range, $timeScale, $lastDataPoint)
	{
		include 'config.php';
		include 'constants.php';
		
		$where = "";
		$group = getTimeSqlGroupClause($timeScale);
		$order = getTimeSqlOrderClause();
		$hourDiff = 0;
		
		if ($timeScale == "Hour")
		{
			$where = "WHERE (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) >= (" . $lastDataPoint . " - (" . $SECONDS_IN_HOUR . " * " . $range . ")) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " HOUR)";
			$hourDiff = $SECONDS_IN_HOUR * (int)$range;
		}
		elseif ($timeScale == "Day")
		{
			$where = "WHERE (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) >= (" . $lastDataPoint . " - (" . $SECONDS_IN_DAY . " * " . $range . ")) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Day) ";
			$hourDiff = $SECONDS_IN_DAY * (int)$range;
		}
		elseif ($timeScale == "Week")
		{
			$where = "WHERE (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) >= (" . $lastDataPoint . " - (" . $SECONDS_IN_WEEK . " * " . $range . ")) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Week) ";
			$hourDiff = $SECONDS_IN_WEEK * (int)$range;
		}
		elseif ($timeScale == "Month")
		{
			$where = "WHERE (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) >= (" . $lastDataPoint . " - (" . $SECONDS_IN_MONTH . " * " . $range . ")) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Month)";
			$hourDiff = $SECONDS_IN_MONTH * (int)$range;
		}
		elseif ($timeScale == "Year")
		{
			$where = "WHERE (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) >= (" . $lastDataPoint . " - (" . $SECONDS_IN_YEAR . " * " . $range . ")) AND " . $DATE_TIME_FIELD_NAME . " < ADDDATE(NOW(), INTERVAL -" . $range . " Year) ";
			$hourDiff = $SECONDS_IN_YEAR * (int)$range;
		}
		else
		{
			echo "";
			return;
		}
		
		// execute query
		$query = "SELECT (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) + " . $hourDiff . ", ";
		if($timeScale != "Hour")
		{
			$query .= "AVG(" . $TEMPERATURE_FIELD_NAME . ") ";
		}
		else
		{
			$query .= $TEMPERATURE_FIELD_NAME . " ";
		}
		$query .= "FROM " . $DATA_TABLE_FIELD_NAME . " " . $where . $group . $order;
		$result = executeQuery($query);
		
		$seriesArray = array("appId" => "ot", "label" => 'Temperature Overlay', "data" => convertResultToArray($result));
		
		return $seriesArray;
	}
	
	/*
	 * $range select range to display e.g "1" day, "20" hours
	 * $timeScale units of range e.g "day", "month"
	 */
	function getTimeSqlWhereClause($channelId, $range, $timeScale)
	{
		include 'config.php';
		
		$where = "";
		// Cast string to int to check it's a valid integer
		$intRange = (int)$range;
		// Check range value. Default value if not set
		if ($range <= 0)
		{
			$range = 1;
		}
		
		if ($timeScale == "Hour")
		{
			$where = " WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . $range . " HOUR)";
		}
		elseif ($timeScale == "Day")
		{
			$where = " WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . $range . " Day) ";
		}
		elseif ($timeScale == "Week")
		{
			$where = " WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . $range . " Week) ";
		}
		elseif ($timeScale == "Month")
		{
			$where = " WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . $range . " Month) ";
		}
		elseif ($timeScale == "Year")
		{
			$where = " WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . $range . " Year) ";
		}
		
		if (isset($channelId))
		{
			if (strlen($where) > 0)
			{
				$where .= " AND ";
			}
			else
			{
				$where .= " WHERE ";
			}
			
			$where .= "channel_id = " . $channelId . " ";
		}
		
		return $where;
	}
	
	/*
	 * $timeScale units of range e.g "day", "month"
	 */
	function getTimeSqlGroupClause($timeScale)
	{
		include 'config.php';
		
		$group = "";
		
		if ($timeScale == "Day")
		{
			$group = " GROUP BY DATE(" . $DATE_TIME_FIELD_NAME . "), HOUR(" . $DATE_TIME_FIELD_NAME . "), MINUTE(" . $DATE_TIME_FIELD_NAME . ") - (MINUTE(" . $DATE_TIME_FIELD_NAME . ") % 10), " . $UNIT_FIELD_NAME;
		}
		elseif ($timeScale == "Week")
		{
			$group = " GROUP BY DATE(" . $DATE_TIME_FIELD_NAME . "), HOUR(" . $DATE_TIME_FIELD_NAME . ") - (HOUR(" . $DATE_TIME_FIELD_NAME . ") % 6), " . $UNIT_FIELD_NAME;
		}
		elseif ($timeScale == "Month")
		{
			$group = " GROUP BY YEAR(" . $DATE_TIME_FIELD_NAME . "), MONTH(" . $DATE_TIME_FIELD_NAME . "), DAY(" . $DATE_TIME_FIELD_NAME . ") - (DAY(" . $DATE_TIME_FIELD_NAME . ") % 1), " . $UNIT_FIELD_NAME;
		}
		elseif ($timeScale == "Year")
		{
			$group = " GROUP BY YEAR(" . $DATE_TIME_FIELD_NAME . "), MONTH(" . $DATE_TIME_FIELD_NAME . ") - (MONTH(" . $DATE_TIME_FIELD_NAME . ") % 1), " . $UNIT_FIELD_NAME;
		}
		
		return $group;
	}
	
	function getTimeSqlOrderClause()
	{
		include 'config.php';
		
		return " ORDER BY " . $DATE_TIME_FIELD_NAME;
	}
	
	// Check if update or full data set is required.
	// Update only returns datasets from a date where as
	// no update returns the full dataset for parameters.
	function updateSqlWhereClause($channelId, $lastDataPoint)
	{
		include 'config.php';
		
		// Full data required if left empty
		$where = "";
		
		// Add channel ID to where clause if it's set
		if (isset($channelId))
		{
			// Check if an And is needed if the $where variable length is greater than 0
			if(strlen($where) > 0)
			{
				$where .= " AND";
			}
			
			$where .= " " . $CHANNEL_ID_PK_FIELD_NAME . " = " . $channelId;
		}
		
		if (isset($lastDataPoint))
		{
			// Check if an And is needed if the $where variable length is greater than 0
			if(strlen($where) > 0)
			{
				$where .= " AND";
			}
			
			$where .=  " (UNIX_TIMESTAMP(" . $DATE_TIME_FIELD_NAME . ") * 1000) > " . $lastDataPoint . " ";
		}
		
		return " WHERE " . $where;
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
				" c ON c." . $APPLIANCE_ID_FK_FIELD_NAME . " = d." . $APPLIANCE_ID_FIELD_NAME . " ORDER BY d." . $APPLIANCE_APP_ID_FIELD_NAME;
		
		$result = executeQuery($query);
		
		return $result;
	}
?>
