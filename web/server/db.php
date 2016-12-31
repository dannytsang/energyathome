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
	
	function executeQuery($queryString)
	{
		// Reference config file
		include 'config.php';
		// open connection to database
		$connection = mysqli_connect($DB_HOST, $DB_USER, $DB_PASSWORD) or die ("Unable to connect!");
		
		// select database
		mysqli_select_db($connection, $DB_SCHEMA) or die ("Unable to select database!");
		
		// Execute query
		$result = mysqli_query($connection, $queryString) or die ("Error in query: '" . $queryString . "'. Error: " . mysqli_error($connection));
		
		// Close database connection
		mysqli_close($connection);
		
		return $result;
	}
	
	/*
	 * $data MySQL array of data.
	 */
	function convertResultToArray($data)
	{
		$num_rows = mysqli_num_rows($data);
		$result = array();
		if ($num_rows > 0)
		{
			while ($row = mysqli_fetch_row($data))
			{
				array_push($result, array(strval($row[0]), strval($row[1]), strval($row[2])));
			}
			
			
		}
		
		return $result;
	}
?>
