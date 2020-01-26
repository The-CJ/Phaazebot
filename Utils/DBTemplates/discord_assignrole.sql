/*
DESCRIBE `discord_assignrole`;

+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| id       | int(11)      | NO   | PRI | NULL    | auto_increment |
| guild_id | varchar(128) | NO   | MUL | NULL    |                |
| trigger  | varchar(128) | NO   |     | NULL    |                |
| role_id  | varchar(128) | NO   |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_assignrole`;

CREATE TABLE `discord_assignrole` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `trigger` varchar(128) NOT NULL,
  `role_id` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_key` (`guild_id`,`trigger`,`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
