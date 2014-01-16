--
-- Create schema energyathome
--

CREATE DATABASE IF NOT EXISTS energyathome;
USE energyathome;

--
-- Definition of table `energyathome`.`channel`
--

DROP TABLE IF EXISTS `energyathome`.`channel`;
CREATE TABLE  `energyathome`.`channel` (
  `channel_id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL,
  `channel` varchar(10) NOT NULL,
  PRIMARY KEY (`channel_id`),
  KEY `device_id_idx` (`device_id`)
) ENGINE=MyISAM AUTO_INCREMENT=35 DEFAULT CHARSET=latin1;

--
-- Definition of table `energyathome`.`devices`
--

DROP TABLE IF EXISTS `energyathome`.`device`;
CREATE TABLE  `energyathome`.`device` (
  `device_id` int(11) NOT NULL auto_increment,
  `name` varchar(20) default NULL,
  `appliance_id` int(11) default '0',
  `sensor_type` int(11) default '0',
  `display_name` VARCHAR(100),
  PRIMARY KEY  USING BTREE (`device_id`)
) ENGINE=MyISAM AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;

--
-- Definition of table `energyathome`.`historical_data`
--

DROP TABLE IF EXISTS `energyathome`.`historical_data`;
CREATE TABLE  `energyathome`.`historical_data` (
  `date_time` datetime NOT NULL,
  `channel_id` int(11) NOT NULL,
  `data` float DEFAULT NULL,
  `unit` varchar(10) DEFAULT NULL,
  KEY `devices_datetime_idx` (`date_time`) USING BTREE,
  KEY `channel_id_idx` (`channel_id`),
  KEY `historical_data_idx` (`channel_id`,`date_time`, `data`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=FIXED;

