/*
DESCRIBE `discord_track_option`;

+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| id       | int(11)      | NO   | PRI | NULL    | auto_increment |
| guild_id | varchar(128) | NO   | MUL | NULL    |                |
| option   | varchar(64)  | NO   |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_track_option`;

CREATE TABLE `discord_track_option` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `option` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `entry_key` (`guild_id`,`option`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
