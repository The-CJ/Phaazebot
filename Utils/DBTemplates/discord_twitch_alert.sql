/*
DESCRIBE `discord_twitch_alert`;

+--------------------+---------------+------+-----+---------+----------------+
| Field              | Type          | Null | Key | Default | Extra          |
+--------------------+---------------+------+-----+---------+----------------+
| id                 | int(11)       | NO   | PRI | NULL    | auto_increment |
| discord_guild_id   | varchar(128)  | NO   |     | NULL    |                |
| discord_channel_id | varchar(128)  | NO   |     | NULL    |                |
| twitch_channel_id  | varchar(128)  | NO   |     | NULL    |                |
| custom_msg         | varchar(1750) | YES  |     | NULL    |                |
+--------------------+---------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_twitch_alert`;

CREATE TABLE `discord_twitch_alert` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `discord_guild_id` varchar(128) NOT NULL,
  `discord_channel_id` varchar(128) NOT NULL,
  `twitch_channel_id` varchar(128) NOT NULL,
  `custom_msg` varchar(1750) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `alert_key` (`discord_channel_id`,`twitch_channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
