<?php
	/*
		This file is part of Energy@Home.
		Copyright (C) 2017 Danny Tsang
		
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
	 * Returns SQL queries required for graph parameters.
	 *
	 * $range select range to display e.g "1" day, "20" hours
	 * $timeScale units of range e.g "day", "month"
	 */
	function getTimeSql($channelId, $range, $timeScale)
	{
		include 'config.php';
		include 'constants.php';
		
		$sql = "";

		if ($timeScale == "Hour")
		{
			$sql = "SELECT UNIX_TIMESTAMP(date_time) * 1000, data, unit FROM historical_data " . getChannelWhereClause($channelId, $range, $timeScale) . " ORDER BY " . $DATE_TIME_FIELD_NAME . ", " . $DATA_FIELD_NAME . ", " . $UNIT_FIELD_NAME;
		}		
		elseif ($timeScale == "Day")
		{
			# Get SQL returning data every 10 minutes 
			$sql = "SELECT TRUNCATE(UNIX_TIMESTAMP(CONCAT(DATE_FORMAT(date_time, '%Y-%m-%d'), ' ', time_hour, ':', time_minute, ':00')) * 1000, 0) AS date_time, data, unit FROM " .
			"(SELECT DATE(date_time) AS date_time, HOUR(date_time) AS time_hour, MINUTE(date_time) - (MINUTE(date_time) % 10) AS time_minute, AVG(data) AS data, unit FROM historical_data " . getChannelWhereClause($channelId, $range, $timeScale) . " GROUP BY DATE(" . $DATE_TIME_FIELD_NAME . "), HOUR(" . $DATE_TIME_FIELD_NAME . "), MINUTE(" . $DATE_TIME_FIELD_NAME . ") - (MINUTE(" . $DATE_TIME_FIELD_NAME . ") % 10), " . $UNIT_FIELD_NAME . ") AS hdata ORDER BY date_time, data, unit";
		}
		elseif ($timeScale == "Week")
		{
			$sql = "SELECT TRUNCATE(UNIX_TIMESTAMP(date_time) * 1000, 0) AS date_time, data, unit FROM " .
"(SELECT DATE(" . $DATE_TIME_FIELD_NAME . ") AS date_time, AVG(data) AS data, " . $UNIT_FIELD_NAME . " FROM historical_data " . getChannelWhereClause($channelId, $range, $timeScale) . " GROUP BY DATE(" . $DATE_TIME_FIELD_NAME . "), " . $UNIT_FIELD_NAME . ") AS hdata ORDER BY date_time, data, unit";
		}
		elseif ($timeScale == "Month")
		{
			$sql = "SELECT TRUNCATE(UNIX_TIMESTAMP(date_time) * 1000, 0) AS date_time, data, unit FROM " .
"(SELECT DATE(" . $DATE_TIME_FIELD_NAME . ") AS date_time, AVG(data) AS data, " . $UNIT_FIELD_NAME . " FROM historical_data " . getChannelWhereClause($channelId, $range, $timeScale) . " GROUP BY DATE(" . $DATE_TIME_FIELD_NAME . "), " . $UNIT_FIELD_NAME . ") AS hdata ORDER BY date_time, data, unit";
		}
		elseif ($timeScale == "Year")
		{
			$sql = "SELECT TRUNCATE(UNIX_TIMESTAMP(date_time) * 1000, 0) AS date_time, data, unit FROM " .
"(SELECT DATE(" . $DATE_TIME_FIELD_NAME . ") AS date_time, AVG(data) AS data, " . $UNIT_FIELD_NAME . " FROM historical_data " . getChannelWhereClause($channelId, $range, $timeScale) . " GROUP BY DATE(" . $DATE_TIME_FIELD_NAME . "), " . $UNIT_FIELD_NAME . ") AS hdata ORDER BY date_time, data, unit";
		}
		
		return $sql;
	}

	function getChannelWhereClause($channelId, $range, $timeScale)
	{
		include 'config.php';

		$where = "";

		if ($timeScale == "Hour")
		{
			$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -" . $range . " HOUR)";
		}
		elseif ($timeScale == "Day")
		{
			$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -1 Day)";
		}
		elseif ($timeScale == "Week")
		{
			$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -1 Week)";
		}
		elseif ($timeScale == "Month")
		{
			$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -1 Month)";
		}
		elseif ($timeScale == "Year")
		{
			$where = "WHERE " . $DATE_TIME_FIELD_NAME . " >= ADDDATE(NOW(), INTERVAL -1 Year)";
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
?>
