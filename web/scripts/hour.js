/*
    This file is part of Energy@Home.
	Copyright (C) 2010 Danny Tsang

    This file is part of Energy@Home.

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
function getHourOptions()
{
	// Set display options for graphs
	options = { selection: { mode: "x" },
			grid: { hoverable: true, clickable: true, autoHighlight: true, backgroundColor: "#313030" , tickColor: "#545454" },
			series: { bars: { show: true, fill: true, align: "center" } },
			legend: { show: document.getElementById('ShowLegend').checked, position: "ne", backgroundColor: "#FFFFFF" },
			yaxis: { min: 0, 
					tickFormatter: (function formatter(val, axis) { return val + "Wh"}) },
			xaxis: { tickSize: 1, 
					tickFormatter: (function formatter(val, axis) { return val + "h"})},
			canvas: true
			};
			
	return options;
}

// Get time data via http request
function getHour(callBack)
{
	var arguments = "graph=" + document.getElementById('graphType').value +
					"&parameter=" + document.getElementById('timeScale').value;
	
	// Send GET request to server
	getAjaxRequest(arguments, callBack);
}