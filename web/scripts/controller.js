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

// Model
var energyData = new Array();

// Last update to model
var energyDataUpdates;

// Auto fetch timer ID
var modelUpdateIntervalID;

// Attached Views which wants to be notified of model changes
var views = new Array();

// Initialises the controller
function controllerInit()
{
	// Initialise view. This must come first in order to get view parameters
	graphInit();
	
	// Initialise data model
	refreshData();
	
	// Set auto update model
	autoUpdateModel("updateData()");
}

// Attaches the view function to call when model has been updated
function attachUpdateView(functionName)
{
	// Ensure function has been defined
	if(functionName)
	{
		var found = false;
		// Check if function is already in view list
		for(f in views)
		{
			if(views[f] == functionName)
			{
				found = true;
				break;
			}
		}
		// Only add function if it does not exist
		if(!found)
		{
			views.push(functionName);
		}
	}
}

// Removes an function from an attached view
function detachUpdateView(functionName)
{
	// Ensure function has been defined
	if(functionName)
	{
		for(f in views)
		{
			if(views[f] == functionName)
			{
				// Remove from list
				views.splice(f, 1);
				break;
			}
		}
	}
}

// Clears existing data and get new fresh copy
function refreshData()
{
	// Clear model data
	energyData = new Array();
	
	// Cancel any outstanding AJAX requests
	abortAjaxRequest();
	
	// Notify view of reset of model
	modelReset();
	
	// Get data from server and draw graph
	if (document.getElementById('graphType') != null && document.getElementById('graphType').value == "Time")
	{
		// Retrieve data from server
		getTime("saveData");
	}
	else if (document.getElementById('graphType') != null &&  document.getElementById('graphType').value == "Hour")
	{
		// Retrieve data from server
		getHour("saveData");
	}
}

function updateData()
{
	// Get data from server and draw graph
	if (document.getElementById('graphType') != null && document.getElementById('graphType').value == "Time")
	{
		// Update graph if there are no ajax request in progress
		if(!ajaxRequestBusy())
		{
			// Notify view an update is to be started
			modelUpdate();
			
			// Check if graph has any data to update. If not then fresh the whole dataset.
			if(graphDataPointExist(energyData))
			{
				// Update model
				getTimeUpdate(energyData, "saveData");
			}
			else
			{
				// Get new model
				refreshData();
			}
		}
	}
	// TODO: implement update for hour graph
}

// Creates data in the model or updates the model
function saveData()
{
	// Ensure the request has a finised state
	if(httpObject.readyState == 4)
	{
		var raw = httpObject.responseText;
		var results = eval("(" + httpObject.responseText + ")");
		
		// Store changes to variable
		energyDataUpdates = clone(results);
		
		// For each series of data returned
		for(var i = (results.length - 1); i >= 0; i--)
		{
			// Get first record and remove it from results array
			result = results.shift();
			var found = false;
			// Loop results to find existing series in current array
			for(s in energyData)
			{
				// Channel ID must match
				if(energyData[s].chId == result.chId)
				{
					// Found matching record
					found = true;
					// Append data to series
					energyData[s].data = energyData[s].data.concat(result.data);
					// Series found, move to next series
					break;
				}
			}
			
			// If data series was not found in current model then add it
			if(!found)
			{
				energyData.push(result);
			}
		}
		
		// Notify view the model has changed
		for(v in views)
		{
			views[v]();
		}
	}
}

function autoUpdateModel(method)
{
	modelUpdateIntervalID = setInterval("updateData()", 10000);
}

// Returns true if there are at least 1 graph datapoint
function graphDataPointExist(graphData)
{
	var graphDataExist = false;
	// Loop through all the series data
	for(s in graphData)
	{
		if(graphData[s].data && graphData[s].data.length > 0)
		{
			// Set data to exist
			graphDataExist = true;
			// Exist loop
			break;
		}
	}
	
	return graphDataExist;
}

// Returns the whole model
function getModel()
{
	// Always return a clone copy of data so changes are not made to the original model
	return clone(energyData);
}

// Returns only the updates to the model
function getChanges()
{
	// Always return a clone copy of data so changes are not made to the original model
	return clone(energyDataUpdates);
}
