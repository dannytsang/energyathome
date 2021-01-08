USE energyathome;

-- Convert row type to default. This is required to convert to InnoDB engine because it does not support fixed_row. Depending on your data size, this may take a long time.

ALTER TABLE `historical_data` ROW_FORMAT = DEFAULT;

-- Change the database engine to InnoDB. This is done on a per table.
ALTER TABLE `channel` ENGINE=InnoDB;
ALTER TABLE `device` ENGINE=InnoDB;

-- Rename table
ALTER TABLE `historical_data` RENAME TO `historical_data2`;

-- Create new table with the new engine
CREATE TABLE  `energyathome`.`historical_data` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `date_time` datetime NOT NULL,
  `channel_id` int NOT NULL,
  `data` float DEFAULT NULL,
  `unit` varchar(10) DEFAULT NULL,
  KEY `devices_datetime_idx` (`date_time`) USING BTREE,
  KEY `channel_id_idx` (`channel_id`),
  KEY `historical_data_idx` (`channel_id`,`date_time`, `data`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Insert data from the old table and insert them into the new table
INSERT INTO historical_data (date_time,channel_id,`data`,unit)
SELECT date_time,channel_id,`data`,unit
FROM historical_data2;

-- Remove old table
DROP TABLE IF EXIST ALTER TABLE `historical_data2`;
