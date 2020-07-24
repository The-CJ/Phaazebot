/*
DESCRIBE `discord_regular`;

+-----------+--------------+------+-----+---------+----------------+
| Field     | Type         | Null | Key | Default | Extra          |
+-----------+--------------+------+-----+---------+----------------+
| id        | int(11)      | NO   | PRI | NULL    | auto_increment |
| guild_id  | varchar(128) | NO   | MUL | NULL    |                |
| member_id | varchar(128) | NO   |     | NULL    |                |
+-----------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_regular`;

CREATE TABLE `discord_regular` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `member_id` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_key` (`guild_id`,`member_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
