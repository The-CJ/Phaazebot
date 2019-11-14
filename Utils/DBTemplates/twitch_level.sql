/*
DESCRIBE `twitch_level`;

+-------------------+--------------+------+-----+---------+----------------+
| Field             | Type         | Null | Key | Default | Extra          |
+-------------------+--------------+------+-----+---------+----------------+
| id                | int(11)      | NO   | PRI | NULL    | auto_increment |
| channel_id        | varchar(128) | NO   | MUL | NULL    |                |
| user_id           | varchar(128) | NO   |     | NULL    |                |
| active            | tinyint(1)   | YES  |     | 0       |                |
| amount_currency   | int(32)      | YES  |     | 0       |                |
| amount_time       | int(16)      | YES  |     | 0       |                |
| user_name         | varchar(128) | YES  |     | NULL    |                |
| user_display_name | varchar(128) | YES  |     | NULL    |                |
+-------------------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `twitch_level`;

CREATE TABLE `twitch_level` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `channel_id` varchar(128) NOT NULL,
  `user_id` varchar(128) NOT NULL,
  `active` tinyint(1) DEFAULT 0,
  `amount_currency` int(32) DEFAULT 0,
  `amount_time` int(16) DEFAULT 0,
  `user_name` varchar(128) DEFAULT NULL,
  `user_display_name` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `channel_id` (`channel_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;