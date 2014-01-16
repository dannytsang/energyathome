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
	
	// uncomment this to see plaintext output in your browser
	// header("Content-Type: text/plain");
	
	if (isset($_GET['graph']) && isset($_GET['parameter']))
	{
		$data = "";
		if ($_GET['graph'] == "Time")
		{
			include 'time.php';
			echo timeGraph();
		}
		elseif ($_GET['graph'] == "Hour")
		{
			include 'hour.php';
			echo hourGraph();
		}

		// get and print number of rows in resultset
		//echo "\n[" . mysql_num_rows($result) . " rows returned]\n";
	}
?>
