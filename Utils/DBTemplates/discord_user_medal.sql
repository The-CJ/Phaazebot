/*
DESCRIBE `discord_user_medal`;

+-----------+--------------+------+-----+---------+----------------+
| Field     | Type         | Null | Key | Default | Extra          |
+-----------+--------------+------+-----+---------+----------------+
| id        | int(11)      | NO   | PRI | NULL    | auto_increment |
| guild_id  | varchar(128) | NO   | MUL | NULL    |                |
| member_id | varchar(128) | NO   |     | NULL    |                |
| name      | varchar(512) | YES  |     | 0       |                |
+-----------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_user_medal`;

CREATE TABLE `discord_user_medal` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `member_id` varchar(128) NOT NULL,
  `name` varchar(512) DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `medal_key` (`guild_id`,`member_id`, `name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
