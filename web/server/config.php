<?php
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

	/** Database username */
	$DB_USER = "energyathome";

	/** Database password */
	$DB_PASSWORD = "";

	/** hostname */
	$DB_HOST = "localhost";
	
	/** Schema where all the tables are to be held */
	$DB_SCHEMA = "energyathome";
	
	/** If database schema is different to default */
	$DATA_TABLE_FIELD_NAME = "historical_data";
	$DATE_TIME_FIELD_NAME = "date_time";
	$CHANNEL_ID_FK_FIELD_NAME = "channel_id";
	$DATA_FIELD_NAME = "data";
	$UNIT_FIELD_NAME = "unit";
	
	$CHANNEL_TABLE_FIELD_NAME = "channel";
	$CHANNEL_ID_PK_FIELD_NAME = "channel_id";
	$CHANNEL_FIELD_NAME = "channel";
	$APPLIANCE_ID_FK_FIELD_NAME = "device_id";
	
	$APPLIANCE_ID_FIELD_NAME = "device_id";
	$APPLIANCE_APP_ID_FIELD_NAME = "appliance_id";
	$APPLIANCE_DISPLAY_NAME_FIELD_NAME = "display_name";
	$APPLIANCE_TABLE_FIELD_NAME = "device";
?>
