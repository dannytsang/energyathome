USE energyathome;

CREATE OR REPLACE
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`%` 
    SQL SECURITY DEFINER
VIEW `compiled_historical_data` AS
    SELECT 
        `h`.`id` AS `id`,
        `h`.`date_time` AS `date_time`,
        `h`.`data` AS `data`,
        `h`.`unit` AS `unit`,
        `d`.`device_id` AS `device_id`,
        `d`.`appliance_id` AS `appliance_id`,
        `d`.`sensor_type` AS `sensor_type`,
        `d`.`name` AS `name`,
        `d`.`display_name` AS `display_name`,
        `c`.`channel_id` AS `channel_id`
    FROM
        ((`historical_data` `h`
        JOIN `channel` `c` ON ((`c`.`channel_id` = `h`.`channel_id`)))
        JOIN `device` `d` ON ((`d`.`device_id` = `c`.`device_id`)))
