/*
DESCRIBE `discord_blacklist_whitelistrole`;

+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| id       | int(11)      | NO   | PRI | NULL    | auto_increment |
| guild_id | varchar(128) | NO   | MUL | NULL    |                |
| role_id  | varchar(128) | NO   |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_blacklist_whitelistrole`;

CREATE TABLE `discord_blacklist_whitelistrole` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `role_id` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `entry_key` (`guild_id`,`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
