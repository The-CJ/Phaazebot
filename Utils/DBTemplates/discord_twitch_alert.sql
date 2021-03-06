/*
DESCRIBE `discord_twitch_alert`;

+---------------------+---------------+------+-----+---------+----------------+
| Field               | Type          | Null | Key | Default | Extra          |
+---------------------+---------------+------+-----+---------+----------------+
| id                  | int(11)       | NO   | PRI | NULL    | auto_increment |
| discord_channel_id  | varchar(128)  | NO   | MUL | NULL    |                |
| twitch_channel_id   | varchar(128)  | NO   | MUL | NULL    |                |
| custom_msg          | varchar(1750) | YES  |     | NULL    |                |
| discord_guild_id    | varchar(128)  | NO   | MUL | NULL    |                |
| suppress_gamechange | tinyint(1)    | NO   |     | 0       |                |
+---------------------+---------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_twitch_alert`;

CREATE TABLE `discord_twitch_alert` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `discord_channel_id` varchar(128) NOT NULL,
  `custom_msg` varchar(1750) DEFAULT NULL,
  `discord_guild_id` varchar(128) NOT NULL,
  `twitch_channel_id` varchar(128) NOT NULL,
  `suppress_gamechange` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `alert_key` (`discord_channel_id`,`twitch_channel_id`),
  KEY `index_discord_channel_id` (`discord_channel_id`),
  KEY `index_discord_guild_id` (`discord_guild_id`),
  KEY `index_twitch_channel_id` (`twitch_channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
