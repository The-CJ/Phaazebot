/*
DESCRIBE `discord_blacklist_blacklistword`;

+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| id       | int(11)      | NO   | PRI | NULL    | auto_increment |
| guild_id | varchar(128) | NO   | MUL | NULL    |                |
| word     | varchar(512) | NO   |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_blacklist_blacklistword`;

CREATE TABLE `discord_blacklist_blacklistword` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `word` varchar(512) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
