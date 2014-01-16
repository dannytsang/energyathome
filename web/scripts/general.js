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

// Server page address
var SERVER = "server/server.php";

// httpObject for calling webservice
var httpObject;

// Get the HTTP Object for AJAX request
function getHTTPObject()
{
	if (window.ActiveXObject) return new ActiveXObject("Microsoft.XMLHTTP");
	else if (window.XMLHttpRequest) return new XMLHttpRequest();
	else
	{
		alert("Your browser does not support the technology used on this page (AJAX).");
		return null;
	}
}

// Get AJAX request
function getAjaxRequest(parameters, callbackMethod)
{
	httpObject = getHTTPObject();
	
	if(parameters.length > 0)
	{
		httpObject.open("GET", SERVER + "?" + parameters, true);
	}
	else
	{
		httpObject.open("GET", SERVER, true);
	}
	httpObject.onreadystatechange = eval(callbackMethod);
	httpObject.send(null);
}

// Cancels a request that has not completed yet
function abortAjaxRequest()
{
	if(httpObject)
	{
		httpObject.onreadystatechange = function () {}
		httpObject.abort();
	}
}

// Returns true if an AJAX request is in progress
function ajaxRequestBusy()
{
	if(httpObject && httpObject.readyState != 4)
	{
		return true;
	}
	else
	{
		return false;
	}
}

// Clones a object of complex type and returns a clone
function clone(item) {
    if (!item) { return item; } // null, undefined values check

    var types = [ Number, String, Boolean ], 
        result;

    // normalizing primitives if someone did new String('aaa'), or new Number('444');
    types.forEach(function(type) {
        if (item instanceof type) {
            result = type( item );
        }
    });

    if (typeof result == "undefined") {
        if (Object.prototype.toString.call( item ) === "[object Array]") {
            result = [];
            item.forEach(function(child, index, array) { 
                result[index] = clone( child );
            });
        } else if (typeof item == "object") {
            // testign that this is DOM
            if (item.nodeType && typeof item.cloneNode == "function") {
                var result = item.cloneNode( true );    
            } else if (!item.prototype) { // check that this is a literal
                // it is an object literal
                result = {};
                for (var i in item) {
                    result[i] = clone( item[i] );
                }
            } else {
                // depending what you would like here,
                // just keep the reference, or create new object
                if (false && item.constructor) {
                    // would not advice to do that, reason? Read below
                    result = new item.constructor();
                } else {
                    result = item;
                }
            }
        } else {
            result = item;
        }
    }

    return result;
}
