/*
    This file is part of Energy@Home.
	Copyright (C) 2011 Danny Tsang

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

// Generate time based graph with energy and temp
function getTimeOptions()
{
	// Set display options for graphs
	if(document.getElementById('timeScale').value == "Hour")
	{
		options = { selection: { mode: "x" },
				grid: { hoverable: true, clickable: true, autoHighlight: true, backgroundColor: "#313030" , tickColor: "#545454" },
				series: { lines: { show: true } },
				legend: { show: document.getElementById('ShowLegend').checked, position: "ne", backgroundColor: "#FFFFFF" },
				yaxis: { min: 0, 
						tickFormatter: (function formatter(val, axis) { return val + "W"}) },
				xaxis: { mode: "time", labelWidth: 10, tickFormatter: (function formatter(val, axis) { return new Date(val).format(TIME_FORMAT)}) },
				y2axis: { minTickSize: 1, autoscaleMargin: 2,
						tickFormatter: (function formatter(val, axis) { return val.toFixed(1) + "C"}) },
				canvas: true
				};
	}
	else if(document.getElementById('timeScale').value == "Day")
	{
		options = { selection: { mode: "x" },
				grid: { hoverable: true, clickable: true, autoHighlight: true, backgroundColor: "#313030" , tickColor: "#545454" },
				series: { lines: { show: true } },
				legend: { show: document.getElementById('ShowLegend').checked, position: "ne", backgroundColor: "#FFFFFF" },
				yaxis: { min: 0, 
						tickFormatter: (function formatter(val, axis) { return val + "W"}) },
				xaxis: { mode: "time", labelWidth: 10, tickFormatter: (function formatter(val, axis) { return new Date(val).format(DATE_FORMAT)}) },
				y2axis: { minTickSize: 1, autoscaleMargin: 2,
						tickFormatter: (function formatter(val, axis) { return val.toFixed(1) + "C"}) },
				canvas: true
				};
	}
	else
	{
		options = { selection: { mode: "x" },
				grid: { hoverable: true, clickable: true, autoHighlight: true, backgroundColor: "#313030" , tickColor: "#545454" },
				series: { lines: { show: true } },
				legend: { show: document.getElementById('ShowLegend').checked, position: "ne", backgroundColor: "#FFFFFF" },
				yaxis: { min: 0, 
						tickFormatter: (function formatter(val, axis) { return val + "W"}) },
				xaxis: { mode: "time", labelWidth: 10, tickFormatter: (function formatter(val, axis) { return new Date(val).format(DATE_FORMAT)}) },
				y2axis: { minTickSize: 1, autoscaleMargin: 2,
						tickFormatter: (function formatter(val, axis) { return val.toFixed(1) + "C"}) },
				canvas: true
				};
	}
	
	return options;
}

// Get time data via http request
function getTime(callBack)
{
	// Create parameters for calling server side page
	var arguments = "graph=" + document.getElementById('graphType').value +
					"&parameter=" + document.getElementById('timeScale').value +
					"&displayRange=" + document.getElementById('displayRange').value;
	
	arguments += "&constantEnergyUsage=true";
	
	// Send GET request to server
	getAjaxRequest(arguments, callBack);
}

// Updates time graph using last known date time as point of reference.
// All series data are updated at the same time so that all series are more or less in sync.
function getTimeUpdate(graphData, callBack)
{
	if(!ajaxRequestBusy())
	{
		// Display loading icon
		$('#ajaxLoadImg').html('<img src="images/ajax-loader_small.gif" />');
		var arguments = "graph=" + document.getElementById('graphType').value +
						"&parameter=" + document.getElementById('timeScale').value +
						"&displayRange=" + document.getElementById('displayRange').value;
			arguments += "&lastEnergyDataPoint=true";
			
		// Get last datapoint for each appliance id which are energy
		for(s in graphData)
		{
			if(graphData[s].data.length > 0)
			{
				// Sort the array by date
				graphData[s].data.sort();
				// Set last time point in data as a parameter to be sent to the server.
				// Append the appliance ID and channel ID so that each appliance last known point can be sent and deciphered
				arguments += "&lastEnergyDataPoint_" + graphData[s].chId + "=" + graphData[s].data[graphData[s].data.length - 1][0];
			}
		}
		
		// Send GET request to server
		getAjaxRequest(arguments, callBack);
	}
}
