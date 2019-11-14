/*
DESCRIBE `discord_level_medal`;

+-----------+--------------+------+-----+---------+----------------+
| Field     | Type         | Null | Key | Default | Extra          |
+-----------+--------------+------+-----+---------+----------------+
| id        | int(11)      | NO   | PRI | NULL    | auto_increment |
| guild_id  | varchar(128) | NO   | MUL | NULL    |                |
| member_id | varchar(128) | NO   |     | NULL    |                |
| edited    | tinyint(1)   | YES  |     | 0       |                |
| exp       | int(8)       | YES  |     | 0       |                |
| on_server | tinyint(1)   | YES  |     | 1       |                |
+-----------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_level_medal`;

CREATE TABLE `discord_level_medal` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `member_id` varchar(128) NOT NULL,
  `name` varchar(512) DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `guild_id` (`guild_id`,`member_id`, `name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
