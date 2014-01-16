/*
    This file is part of Energy@Home.
	Copyright (C) 2009 Danny Tsang

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

var stopWatchTimer;
var startStopwatch = false;
var stopWatchCount = 0;

var PERIOD_OF_TIME = new Array ("Hour", "Day", "Week", "Month", "Year");
var HOURS_OF_THE_DAY = new Array ("Today", "Yesterday", "Week", "Month", "Year");
var LOAD_TIMEOUT = 100;
// Default date format
var DATE_FORMAT = "dd-mmm-yyyy HH:MM:ss";
var TIME_FORMAT = "HH:MM:ss";

// Initialises graph and page. Always displays loading image
function graphInit()
{
	// Attach view to controller on model update
	attachUpdateView(updateGraph);
	
	// Add graph bindings
	var previousPoint = null;
	$("#placeholder").bind("plothover", graphHover);

	$("#placeholder").bind("plotclick", graphClick);
	
	$("#placeholder").bind("plotselected", function (event, ranges) {
		// Only zoom if tick box is true
		if(document.getElementById('ZoomSelect').checked)
		{
			// re-plot zooming
			$.plot($("#placeholder"), graphData,
				$.extend(true, {}, getTimeOptions(), {
					xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to }
			}));
			document.getElementById('AutoRefresh').checked = false;
		}
	});
	
	// Populate range dropdown box
	populateDisplayRange();
	
	// Display loading graph
	$('#placeholder').html('<p><img src="images/ajax-loader.gif" width="220" height="19" /></p>');
}

// Model has been updated
function updateGraph()
{
	// Retrieve data
	graphData = getModel();
	
	// Get graph options
	options = getOptions();
	
	// Set graph
	setGraph(graphData, options)
	
	// Update raw grid data
	//drawGrid();
	
	// Call post load function
	modelChangeComplete();
}

function modelReset()
{
	// Stop the stop watch if it's currently running
	startStopwatch = false;
	
	// Display loading graph
	$('#placeholder').html('<p><img src="images/ajax-loader.gif" width="220" height="19" /></p>');
	
	// Change graph to loading image
	$('#lastUpdated').html('<p><img src="images/ajax-loader_small.gif" /> Loading... <span id="timeElapsed"></span></p>');
	
	// Clear clicked data points
	$("#clickdata").text("");
	$("#clickoverlay").text("");
	
	// Reset count
	stopWatchCount = 0;
	
	// Display time taken on page
	$('#timeElapsed').html(stopWatchCount + "ms");
	
	// Start timer to count how long the request took
	startStopwatch = true;
	stopWatch();
}

// Notify view a data update has started
function modelUpdate()
{
	// Stop the stop watch if it's currently running
	startStopwatch = false;
	// Change graph to loading image
	$('#ajaxLoadImg').html('<img src="images/ajax-loader_small.gif" />');
	// Clear clicked data points
	$("#clickdata").text("");
	$("#clickoverlay").text("");
	// Reset count
	stopWatchCount = 0;
	// Display time taken on page
	//$('#timeTaken').html(stopWatchCount + "ms");
	// Start timer to count how long the request took
	startStopwatch = true;
	stopWatch();
}

// Notify view data model changes have been complete
function modelChangeComplete()
{
	// Stop the timer
	startStopwatch = false;
	// Change the last updated text
	$('#lastUpdated').html('<span id="ajaxLoadImg"></span><i>Last Updated: ' + new Date().toLocaleString() + ' and took <span id="timeTaken"></span></i>');
	// Add time taken to load into the text
	$('#timeTaken').html(stopWatchCount + "ms");
}

// Count time taken for AJAX request
function stopWatch()
{
	if (startStopwatch)
	{
		// Increment time taken
		stopWatchCount+= LOAD_TIMEOUT;
		// Display time taken on page
		$('#timeElapsed').html(stopWatchCount + "ms");
		// Call recursive loop
		stopWatchTimer = setTimeout("stopWatch()", LOAD_TIMEOUT);
	}
	else
	{
		if (stopWatchTimer)
		{
			clearTimeout(stopWatchTimer);
		}
	}
}

// Graph type change event
function graphTypeChange()
{
	// Change view options depending on graph type
	populateDisplayRange();
	
	// Notify controller of graph type change request
	refreshData();
}

// Change in graph parameter
function graphParameterChange()
{
	// Check input is valid
	// Ensure display range is set before generating new graph
	var range = parseInt(document.getElementById('displayRange').value);
	if(!document.getElementById('displayRange').value.match(/\D/g) && document.getElementById('displayRange').value.length > 0)
	{
		// Reset the background colour of the display range text box
		document.getElementById('displayRange').style.background = "#FFFFFF";
		
		// Notify controller of graph type change request
		refreshData();
	}
	else // Invalid entry
	{
		// Set the background colour of the display range text box to red
		document.getElementById('displayRange').style.background = "#FC0000";
	}
}

// Get graph options depending on select graph parameters
function getOptions()
{
	// Get graph options
	var options;
	if (document.getElementById('graphType') != null && document.getElementById('graphType').value == "Time")
	{
		options = getTimeOptions();
	}
	else if (document.getElementById('graphType') != null &&  document.getElementById('graphType').value == "Hour")
	{
		options = getHourOptions();
	}
	
	return options;
}

// Populates display range dropdown with necessary values and sets other options on graph form
function populateDisplayRange()
{
	if (document.getElementById('graphType') != null && document.getElementById('graphType').value == "Time")
	{
		// Repopulate time frame drop down with new values
		loadTimeFrame(PERIOD_OF_TIME);
		// Enable range textbox
		document.getElementById('displayRange').disabled = false;
		// Set textbox background colour to white
		document.getElementById('displayRange').style.backgroundColor="#fff";
		// Set display range if it's empty
		if(document.getElementById('displayRange').value.match(/\d/g) == null)
		{
			document.getElementById('displayRange').value = "1";
		}
		// Enable auto refresh
		document.getElementById('AutoRefresh').checked = true;
	}
	else if (document.getElementById('graphType') != null && document.getElementById('graphType').value == "Hour")
	{
		// Repopulate time fram drop down with new values
		loadTimeFrame(HOURS_OF_THE_DAY);
		// Disable range textbox
		document.getElementById('displayRange').disabled = true;
		// Make disabled textbox grey
		document.getElementById('displayRange').style.backgroundColor="#c0c0c0";
		// Disable auto refresh
		document.getElementById('AutoRefresh').checked = false;
	}
	else if (document.getElementById('graphType') != null && document.getElementById('graphType').value == "Distribution")
	{
		// Repopulate time fram drop down with new values
		loadTimeFrame(PERIOD_OF_TIME);
		// Enable range textbox
		document.getElementById('displayRange').disabled = false;
		// Make disabled textbox grey
		document.getElementById('displayRange').style.backgroundColor="#c0c0c0";
		// Disable auto refresh
		document.getElementById('AutoRefresh').checked = false;
	}
}

// Populates a dropdown with list which is passed in as parameter
function loadTimeFrame(list)
{
	// Get drop down list
	var dropdown = document.getElementById("timeScale");
	
	// Clear drop down
	dropdown.options.length = 0;
	
	// Load drop down with array
	for (var i = 0; i < list.length; i++)
	{
		dropdown.options[dropdown.options.length] = new Option(list[i], list[i]);
	}
}

// Build time graph once data request response is returned
function setGraph(graphData, options)
{
	$.plot($("#placeholder"),
			graphData
		   , options);
}

// Show / hide legend
function showLegendChange()
{
	// Get model data
	var graphData = getModel();
	
	// Get graph options
	var options = getOptions();
	
	$.plot($("#placeholder"),
			graphData
		   , options);
}

// Enable / disable zoom
function zoomOnSelectChange()
{
	// Get model data
	var graphData = getModel();
	
	// Get graph options
	var options = getOptions();
	
	// Re-draw graph
	$.plot($("#placeholder"),
			graphData
		   , options);
}

// Resets the zoom
function resetZoom()
{
	// Get model data
	var graphData = getModel();
	
	// Get graph options
	var options = getOptions();
	
	$.plot($("#placeholder"),
			graphData
		   , options);

	document.getElementById('AutoRefresh').checked = true;
}

// Enables / disables auto refresh
function autoRefreshChange(enabled)
{
	if(enabled)
	{
		// Add
		attachUpdateView(updateGraph);
	}
	else
	{
		// Remove
		detachUpdateView(updateGraph);
	}
}

// Graph click event
function graphClick(event, pos, item)
{
	if (item) {
		// Check what type of graph is showing. For future use
		if (document.getElementById('graphType').value == "Time")
		{
			//$("#clickdata").text("You clicked point " + item.dataIndex + " in " + item.series.label + ".");
			if(item.series.label == "Energy Used")
			{
				$("#clickdata").text("Current: " + parseInt(item.datapoint[1].toFixed(2)) + " Watts was used on " +
						new Date(parseInt(item.datapoint[0].toFixed(2))).toGMTString() + ".");
			}
			else if(item.series.label == "Temperature")
			{
				$("#clickdata").text("Current: It was " + item.datapoint[1].toFixed(1) + " degrees celsius at " +
						new Date(parseInt(item.datapoint[0].toFixed(2))).toGMTString() + ".");
			}
			else if(item.series.label == "Energy Overlay")
			{
				// Get offset time
				var subtrackTime = getSubtrackOverlay(document.getElementById('timeScale').value);
				
				$("#clickoverlay").text("Overlay: " + parseInt(item.datapoint[1].toFixed(2)) + " Watts was used on " +
						new Date(parseInt(item.datapoint[0].toFixed(2)) - subtrackTime).toGMTString() + ".");
			}
			else if(item.series.label == "Temperature Overlay")
			{
				// Get offset time
				var subtrackTime = getSubtrackOverlay(document.getElementById('timeScale').value);
				
				$("#clickoverlay").text("Overlay: It was " + item.datapoint[1].toFixed(1) + " degrees celsius at " +
						new Date(parseInt(item.datapoint[0].toFixed(2)) - subtrackTime).toGMTString() + ".");
			}
		}
	}
}

// Graph hover event
function graphHover(event, pos, item)
{
	// Tooltip displayed on the graph
	if (item)
	{
		if (previousPoint == undefined || (previousPoint != item.datapoint))
		{
			previousPoint = item.datapoint;
			
			$("#tooltip").remove();
			var x = 0, y = new Date();
			// Check what type of graph is showing. For future use
			if (document.getElementById('graphType').value == "Time")
			{
				if(item.series.channel != "temp")
				{
					x = parseInt(item.datapoint[1].toFixed(2)),
					y = new Date(parseInt(item.datapoint[0].toFixed(2)));
					
					showTooltip(item.pageX, item.pageY,
							"<span>" + item.series.label + "</span><br/><span class=\"energyvalue\" style=\"color:" + item.series.color + "\">" + x + " " + item.series.data[item.dataIndex][2] + "</span><br/><span>" + y.format(DATE_FORMAT) + "</span>");
				}
				else
				{
					x = item.datapoint[1].toFixed(1),
					y = new Date(parseInt(item.datapoint[0].toFixed(2)));
					
					showTooltip(item.pageX, item.pageY,
							"<span>" + item.series.label + "</span><br/><span class=\"temperaturevalue\" style=\"color:" + item.series.color + "\">" + x + "&deg; " + item.series.data[item.dataIndex][2] + "</span><br/><span>" + y.format(DATE_FORMAT) + "</span>");
				}
			}
			else if (document.getElementById('graphType').value == "Hour")
			{
				x = item.datapoint[1].toFixed(0);
				var y1 = item.datapoint[0];
				var y2 = item.datapoint[0] + 1;
				// Pad time with leading 0
				if(y1 < 10)
				{
					y1 = "0" + y1;
				}
				if(y2 < 10)
				{
					y2 = "0" + y2;
				}
				
				showTooltip(item.pageX, item.pageY,
							"<span>" + item.series.label + "</span><br/><span class=\"energyvalue\" style=\"color:" + item.series.color + "\">" + x + " Watt(s)</span><br/><span>were used between " + y1 + ":00 - " + y2 + ":00</span>");
			}
		}
	}
	else
	{
		$("#tooltip").remove();
		previousPoint = null;            
	}
}

// Tooltip look
function showTooltip(x, y, contents)
{
	$('<div id="tooltip">' + contents + '</div>').css( {
		position: 'absolute',
		display: 'none',
		top: y + 20,
		left: x + 5,
		border: '1px solid #fdd',
		padding: '2px',
		'background-color': '#FFFCEF',
		opacity: 0.95
	}).appendTo("body").fadeIn(100);
}
