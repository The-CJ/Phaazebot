/*
DESCRIBE `discord_user`;

+-----------+--------------+------+-----+---------+----------------+
| Field     | Type         | Null | Key | Default | Extra          |
+-----------+--------------+------+-----+---------+----------------+
| id        | int(11)      | NO   | PRI | NULL    | auto_increment |
| guild_id  | varchar(128) | NO   | MUL | NULL    |                |
| member_id | varchar(128) | NO   |     | NULL    |                |
| username  | varchar(512) | YES  |     | NULL    |                |
| nickname  | varchar(512) | YES  |     | NULL    |                |
| edited    | tinyint(1)   | YES  |     | 0       |                |
| exp       | int(8)       | YES  |     | 0       |                |
| currency  | int(11)      | YES  |     | 0       |                |
| on_server | tinyint(1)   | YES  |     | 1       |                |
+-----------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_user`;

CREATE TABLE `discord_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `member_id` varchar(128) NOT NULL,
  `username` varchar(512) DEFAULT NULL,
  `nickname` varchar(512) DEFAULT NULL,
  `edited` tinyint(1) DEFAULT 0,
  `exp` int(8) DEFAULT 0,
  `currency` int(11) DEFAULT 0,
  `on_server` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_key` (`guild_id`,`member_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
