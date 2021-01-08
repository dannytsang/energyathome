USE energyathome;

-- Convert row type to default. This is required to convert to InnoDB engine because it does not support fixed_row. Depending on your data size, this may take a long time.

ALTER TABLE `historical_data` ROW_FORMAT = DEFAULT;

-- Change the database engine to InnoDB. This is done on a per table.
ALTER TABLE `channel` ENGINE=InnoDB;
ALTER TABLE `device` ENGINE=InnoDB;
ALTER TABLE `historical_data` ENGINE=InnoDB;

