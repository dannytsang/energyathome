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

function dataGridInit()
{
	// Attach view to controller
	attachUpdateView(updateDataGrid);
	
	var graphData = getModel();
	// Draw initial grid
	if (document.getElementById('graphType') != null && document.getElementById('graphType').value == "Time")
	{
		drawTimeGrid(graphData);
	}
	else if (document.getElementById('graphType') != null && document.getElementById('graphType').value == "Hour")
	{
		drawHourGrid(graphData);
	}
}

// Update view from model change
function updateDataGrid()
{
	// Get models
	var fullModel = getModel();
	var graphData = getChanges();
	
	// Updates to model do not include all attributes of the original model so it requires merging of the two models to make it complete
	for(series in graphData)
	{
		var found = false;
		
		for(series2 in fullModel)
		{
			// If channel ID matches
			if(graphData[series].chId == fullModel[series2].chId)
			{
				// Set label of update model from full model
				graphData[series].label = fullModel[series2].label;
				found = true;
				
				break;
			}
		}
		
		// If update model data is not in full model then set some label info
		if(!found)
		{
			graphData[series].label = "Unknown (" + graphData[series].chId + ")";
		}
	}
	
	if (document.getElementById('graphType') != null && document.getElementById('graphType').value == "Time")
	{
		updateTimeGrid(graphData);
	}
	else if (document.getElementById('graphType') != null && document.getElementById('graphType').value == "Hour")
	{
		updateHourGrid(graphData);
	}
}

function drawTimeGrid(graphData)
{
	// Unload grid prior to reload. Without doing so the data will be appened to the old grid and no changes will be made to the columns
	$("#energyTable").GridUnload();
	// Ensure there are data to put in the grid
	columns = ['Date', 'Name', 'Value', 'Unit'];
	columnModel = [{
						name:'displayDate',
						index:'Date', 
						width:150,
						sorttype:"date"
					},
					{
						name:'name',
						index:'Name',
						width:150,
						align:"right",
						sorttype:"float"
					},
					{
						name:'dataValue',
						index:'Value',
						width:50,
						align:"right",
						sorttype:"float"
					},
					{
						name:'unit',
						index:'Unit',
						width:30,
						align:"right",
						sorttype:"float"
					}
				];
	// Setup grid
	drawDataGrid(columns, columnModel);
	// Ensure grid data has been loaded
	if(graphData !== null)
	{
		gridData = formatTimeGridData(graphData);
		addRow(gridData, "energyTable")
	}
}

function updateTimeGrid(graphData)
{
	// Ensure grid data has been loaded
	if(graphData !== null)
	{
		gridData = formatTimeGridData(graphData);
		// Append data to grid
		addRow(gridData, "energyTable");
	}
}

function updateHourGrid(graphData)
{
	// Ensure grid data has been loaded
	if(graphData !== null)
	{
		gridData = formatHourGridData(graphData);
		// Append data to grid
		addRow(gridData, "energyTable");
	}
}

function drawHourGrid(graphData)
{
	// Unload grid prior to reload. Without doing so the data will be appened to the old grid and no changes will be made to the columns
	$("#energyTable").GridUnload();
	// Ensure there are data to put in the grid
	columns = ['Hour', 'Name', 'Value', 'Unit'];
	columnModel = [{
						name:'displayDate',
						index:'Hour', 
						width:150,
						sortable: true,
						sorttype:"date"
					},
					{
						name:'name',
						index:'Name',
						width:150,
						align:"right",
						sortable: true,
						sorttype:"text"
					},
					{
						name:'dataValue',
						index:'Value',
						width:50,
						align:"right",
						sortable: true,
						sorttype:"float"
					},
					{
						name:'unit',
						index:'Unit',
						width:30,
						align:"right",
						sortable: true,
						sorttype:"text"
					}
				];
	// Setup grid
	drawDataGrid(columns, columnModel);
	// Ensure grid data has been loaded
	if(graphData !== null)
	{
		gridData = formatHourGridData(graphData);
		addRow(gridData, "energyTable")
	}
}

function formatTimeGridData(seriesData)
{
	var gridRows = new Array();
	
	// Search for energy and temperature data
	for (i=0; i < seriesData.length; i++)
	{
		// Construct rows for grid. The loop cannot assume the first and main loop is either energy or temperature
		for (j=0; j < seriesData[i].data.length; j++)
		{
			// Variable to hold the newly constructed row
			var row = new Object();
			row.displayDate = dateFormat(new Date(parseInt(seriesData[i].data[j][0])), "yyyy-mm-dd HH:MM:ss");
			row.name = seriesData[i].label;
			row.dataValue = seriesData[i].data[j][1];
			row.unit = seriesData[i].data[j][2];
			
			gridRows.push(row);
		}
	}
	
	return gridRows;
}

function formatHourGridData(seriesData)
{
	var gridRows = new Array();
	
	// Search for energy and temperature data
	for (i=0; i < seriesData.length; i++)
	{
		// Construct rows for grid. The loop cannot assume the first and main loop is either energy or temperature
		for (j=0; j < seriesData[i].data.length; j++)
		{
			// Variable to hold the newly constructed row
			var row = new Object();
			row.displayDate = seriesData[i].data[j][0] + "h";
			row.name = seriesData[i].label;
			row.dataValue = seriesData[i].data[j][1];
			row.unit = seriesData[i].data[j][2];
			
			gridRows.push(row);
		}
	}
	
	return gridRows;
}

function drawDataGrid(columnNames, columnModel)
{
	// Set grid layout
	jQuery("#energyTable").jqGrid({
		datatype: "local",
		height: 250,
		width: 400,
		colNames:columnNames,
		colModel:columnModel,
		multiselect: true,
		pager: "#energyTablePager",
		// Disable paging
		pgbuttons: false,
		pgtext: false,
		pginput:false,
		sortname: 'date',
		viewrecords: true,
		sortorder: 'desc',
		caption: "Graph Data"
	});
	jQuery("#energyTable").jqGrid('navGrid','#energyTablePager',{add:false,edit:false,del:false});
	jQuery("#energyTable").jqGrid('sortableRows');
}

function addRow(data, tableName)
{
	// Add each row to the grid
	for(var i=0;i<=data.length;i++) jQuery("#" + tableName).jqGrid('addRowData',i+1,data[i]); 
}