/*
DESCRIBE `discord_setting`;

+-----------------------+---------------+------+-----+---------+----------------+
| Field                 | Type          | Null | Key | Default | Extra          |
+-----------------------+---------------+------+-----+---------+----------------+
| id                    | int(11)       | NO   | PRI | NULL    | auto_increment |
| guild_id              | varchar(128)  | NO   | UNI | NULL    |                |
| autorole_id           | varchar(128)  | YES  |     | NULL    |                |
| blacklist_ban_links   | tinyint(1)    | YES  |     | 0       |                |
| blacklist_punishment  | varchar(32)   | YES  |     | delete  |                |
| currency_name         | varchar(256)  | YES  |     | NULL    |                |
| currency_name_multi   | varchar(256)  | YES  |     | NULL    |                |
| leave_chan            | varchar(128)  | YES  |     | NULL    |                |
| leave_msg             | varchar(1750) | YES  |     | NULL    |                |
| level_announce_chan   | varchar(128)  | YES  |     | NULL    |                |
| level_custom_msg      | varchar(1750) | YES  |     | NULL    |                |
| owner_disable_level   | tinyint(1)    | YES  |     | 0       |                |
| owner_disable_mod     | tinyint(1)    | YES  |     | 0       |                |
| owner_disable_normal  | tinyint(1)    | YES  |     | 0       |                |
| track_channel         | varchar(128)  | YES  |     | NULL    |                |
| welcome_chan          | varchar(128)  | YES  |     | NULL    |                |
| welcome_msg           | varchar(1750) | YES  |     | NULL    |                |
| welcome_msg_priv      | varchar(1750) | YES  |     | NULL    |                |
| owner_disable_regular | tinyint(1)    | YES  |     | 0       |                |
+-----------------------+---------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_setting`;

CREATE TABLE `discord_setting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `autorole_id` varchar(128) DEFAULT NULL,
  `blacklist_ban_links` tinyint(1) DEFAULT 0,
  `blacklist_punishment` varchar(32) DEFAULT 'delete',
  `currency_name` varchar(256) DEFAULT NULL,
  `currency_name_multi` varchar(256) DEFAULT NULL,
  `leave_chan` varchar(128) DEFAULT NULL,
  `leave_msg` varchar(1750) DEFAULT NULL,
  `level_announce_chan` varchar(128) DEFAULT NULL,
  `level_custom_msg` varchar(1750) DEFAULT NULL,
  `owner_disable_level` tinyint(1) DEFAULT 0,
  `owner_disable_mod` tinyint(1) DEFAULT 0,
  `owner_disable_regular` tinyint(1) DEFAULT 0,
  `owner_disable_normal` tinyint(1) DEFAULT 0,
  `track_channel` varchar(128) DEFAULT NULL,
  `welcome_chan` varchar(128) DEFAULT NULL,
  `welcome_msg` varchar(1750) DEFAULT NULL,
  `welcome_msg_priv` varchar(1750) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `guild_id` (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
