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
| currency_name              | varchar(64)  | YES  |     | NULL    |                |
| currency_name_multi        | varchar(64)  | YES  |     | NULL    |                |
| gain_currency              | int(8)       | YES  |     | 1       |                |
| gain_currency_active_multi | float        | YES  |     | 1       |                |
| gain_currency_message      | int(8)       | YES  |     | 1       |                |
| osurequestformat_osu       | varchar(475) | YES  |     | NULL    |                |
| osurequestformat_twtich    | varchar(475) | YES  |     | NULL    |                |
| owner_disable_level        | tinyint(1)   | YES  |     | 0       |                |
| owner_disable_mod          | tinyint(1)   | YES  |     | 0       |                |
| owner_disable_normal       | tinyint(1)   | YES  |     | 0       |                |
| owner_disable_regular      | tinyint(1)   | YES  |     | 0       |                |
| punish_msg_caps            | varchar(475) | YES  |     | NULL    |                |
| punish_msg_copypasta       | varchar(475) | YES  |     | NULL    |                |
| punish_msg_emotes          | varchar(475) | YES  |     | NULL    |                |
| punish_msg_links           | varchar(475) | YES  |     | NULL    |                |
| punish_msg_unicode         | varchar(475) | YES  |     | NULL    |                |
| punish_msg_words           | varchar(475) | YES  |     | NULL    |                |
| punish_notify              | tinyint(1)   | YES  |     | 1       |                |
| punish_option_caps         | tinyint(1)   | YES  |     | 0       |                |
| punish_option_copypasta    | tinyint(1)   | YES  |     | 0       |                |
| punish_option_emotes       | tinyint(1)   | YES  |     | 0       |                |
| punish_option_links        | tinyint(1)   | YES  |     | 0       |                |
| punish_option_unicode      | tinyint(1)   | YES  |     | 0       |                |
| punish_option_words        | tinyint(1)   | YES  |     | 0       |                |
| punish_timeout             | int(8)       | YES  |     | 30      |                |
+----------------------------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `twitch_setting`;

CREATE TABLE `twitch_setting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `channel_id` varchar(128) NOT NULL,
  `active_game` tinyint(1) DEFAULT 0,
  `active_level` tinyint(1) DEFAULT 0,
  `active_quote` tinyint(1) DEFAULT 0,
  `currency_name` varchar(64) DEFAULT NULL,
  `currency_name_multi` varchar(64) DEFAULT NULL,
  `gain_currency` int(8) DEFAULT 1,
  `gain_currency_active_multi` float DEFAULT 1,
  `gain_currency_message` int(8) DEFAULT 1,
  `osurequestformat_osu` varchar(475) DEFAULT NULL,
  `osurequestformat_twtich` varchar(475) DEFAULT NULL,
  `owner_disable_level` tinyint(1) DEFAULT 0,
  `owner_disable_mod` tinyint(1) DEFAULT 0,
  `owner_disable_normal` tinyint(1) DEFAULT 0,
  `owner_disable_regular` tinyint(1) DEFAULT 0,
  `punish_msg_caps` varchar(475) DEFAULT NULL,
  `punish_msg_copypasta` varchar(475) DEFAULT NULL,
  `punish_msg_emotes` varchar(475) DEFAULT NULL,
  `punish_msg_links` varchar(475) DEFAULT NULL,
  `punish_msg_unicode` varchar(475) DEFAULT NULL,
  `punish_msg_words` varchar(475) DEFAULT NULL,
  `punish_notify` tinyint(1) DEFAULT 1,
  `punish_option_caps` tinyint(1) DEFAULT 0,
  `punish_option_copypasta` tinyint(1) DEFAULT 0,
  `punish_option_emotes` tinyint(1) DEFAULT 0,
  `punish_option_links` tinyint(1) DEFAULT 0,
  `punish_option_unicode` tinyint(1) DEFAULT 0,
  `punish_option_words` tinyint(1) DEFAULT 0,
  `punish_timeout` int(8) DEFAULT 30,
  PRIMARY KEY (`id`),
  UNIQUE KEY `channel_id` (`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
