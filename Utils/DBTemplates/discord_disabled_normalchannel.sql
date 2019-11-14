/*
DESCRIBE `discord_disabled_normalchannel`;

+------------+--------------+------+-----+---------+----------------+
| Field      | Type         | Null | Key | Default | Extra          |
+------------+--------------+------+-----+---------+----------------+
| id         | int(11)      | NO   | PRI | NULL    | auto_increment |
| guild_id   | varchar(128) | NO   | MUL | NULL    |                |
| channel_id | varchar(128) | NO   |     | NULL    |                |
+------------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_disabled_normalchannel`;

CREATE TABLE `discord_disabled_normalchannel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `channel_id` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `guild_id` (`guild_id`,`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;