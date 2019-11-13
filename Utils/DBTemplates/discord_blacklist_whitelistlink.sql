/*
DESCRIBE `discord_blacklist_whitelistlink`;

+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| id       | int(11)      | NO   | PRI | NULL    | auto_increment |
| guild_id | varchar(128) | NO   | MUL | NULL    |                |
| link     | varchar(512) | NO   |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_blacklist_whitelistlink`;

CREATE TABLE `discord_blacklist_whitelistlink` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `link` varchar(512) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
