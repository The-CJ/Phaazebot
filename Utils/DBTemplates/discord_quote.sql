/*
DESCRIBE `discord_quote`;

+----------+---------------+------+-----+---------+----------------+
| Field    | Type          | Null | Key | Default | Extra          |
+----------+---------------+------+-----+---------+----------------+
| id       | int(11)       | NO   | PRI | NULL    | auto_increment |
| guild_id | varchar(128)  | NO   |     | NULL    |                |
| content  | varchar(1750) | YES  |     | NULL    |                |
+----------+---------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_quote`;

CREATE TABLE `discord_quote` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `content` varchar(1750) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
