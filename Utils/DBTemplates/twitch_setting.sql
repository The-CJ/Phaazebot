/*
DESCRIBE `twitch_setting`;

+----------------------------+--------------+------+-----+---------+----------------+
| Field                      | Type         | Null | Key | Default | Extra          |
+----------------------------+--------------+------+-----+---------+----------------+
| id                         | int(11)      | NO   | PRI | NULL    | auto_increment |
| channel_id                 | varchar(128) | NO   | UNI | NULL    |                |
| active_game                | tinyint(1)   | YES  |     | 0       |                |
| active_level               | tinyint(1)   | YES  |     | 0       |                |
| active_quote               | tinyint(1)   | YES  |     | 0       |                |
| blacklist_ban_links        | tinyint(1)   | YES  |     | 0       |                |
| blacklist_link_msg         | varchar(475) | YES  |     | NULL    |                |
| blacklist_notify           | tinyint(1)   | YES  |     | 0       |                |
| blacklist_msg              | varchar(475) | YES  |     | NULL    |                |
| blacklist_punishment       | tinyint(1)   | YES  |     | 0       |                |
| currency_name              | varchar(64)  | YES  |     | NULL    |                |
| currency_name_multi        | varchar(64)  | YES  |     | NULL    |                |
| gain_currency              | int(8)       | YES  |     | 1       |                |
| gain_currency_message      | int(8)       | YES  |     | 1       |                |
| gain_currency_active_multi | float        | YES  |     | 1       |                |
| owner_disable_mod          | tinyint(1)   | YES  |     | 0       |                |
| owner_disable_normal       | tinyint(1)   | YES  |     | 0       |                |
| osurequestformat_osu       | varchar(475) | YES  |     | NULL    |                |
| osurequestformat_twtich    | varchar(475) | YES  |     | NULL    |                |
+----------------------------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `twitch_setting`;

CREATE TABLE `twitch_setting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `channel_id` varchar(128) NOT NULL,
  `active_game` tinyint(1) DEFAULT 0,
  `active_level` tinyint(1) DEFAULT 0,
  `active_quote` tinyint(1) DEFAULT 0,
  `blacklist_ban_links` tinyint(1) DEFAULT 0,
  `blacklist_link_msg` varchar(475) DEFAULT NULL,
  `blacklist_notify` tinyint(1) DEFAULT 0,
  `blacklist_msg` varchar(475) DEFAULT NULL,
  `blacklist_punishment` tinyint(1) DEFAULT 0,
  `currency_name` varchar(64) DEFAULT NULL,
  `currency_name_multi` varchar(64) DEFAULT NULL,
  `gain_currency` int(8) DEFAULT 1,
  `gain_currency_message` int(8) DEFAULT 1,
  `gain_currency_active_multi` float DEFAULT 1,
  `owner_disable_mod` tinyint(1) DEFAULT 0,
  `owner_disable_normal` tinyint(1) DEFAULT 0,
  `osurequestformat_osu` varchar(475) DEFAULT NULL,
  `osurequestformat_twtich` varchar(475) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `channel_id` (`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
