# MySQL 8 and above optimisation script. Only works with MySQL 8+
# Script is designed to work as an upgrade or installed from the start.
CREATE INDEX date_time_desc_idx ON historical_data(date_time);
CREATE INDEX channel_id_date_time_desc_idx ON historical_data(date_time);
OPTIMIZE TABLE historical_data;
