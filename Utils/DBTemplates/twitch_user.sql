/*
DESCRIBE `twitch_user`;

+-------------------+--------------+------+-----+---------+----------------+
| Field             | Type         | Null | Key | Default | Extra          |
+-------------------+--------------+------+-----+---------+----------------+
| id                | int(11)      | NO   | PRI | NULL    | auto_increment |
| channel_id        | varchar(128) | NO   | MUL | NULL    |                |
| user_id           | varchar(128) | NO   |     | NULL    |                |
| active            | tinyint(1)   | YES  |     | 0       |                |
| amount_currency   | int(32)      | YES  |     | 0       |                |
| amount_time       | int(16)      | YES  |     | 0       |                |
+-------------------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `twitch_user`;

CREATE TABLE `twitch_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `channel_id` varchar(128) NOT NULL,
  `user_id` varchar(128) NOT NULL,
  `active` tinyint(1) DEFAULT 0,
  `amount_currency` int(32) DEFAULT 0,
  `amount_time` int(16) DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_key` (`channel_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
