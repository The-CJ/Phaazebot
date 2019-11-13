/*
DESCRIBE `discord_level`;

+-----------+--------------+------+-----+---------+----------------+
| Field     | Type         | Null | Key | Default | Extra          |
+-----------+--------------+------+-----+---------+----------------+
| id        | int(11)      | NO   | PRI | NULL    | auto_increment |
| guild_id  | varchar(128) | NO   | MUL | NULL    |                |
| member_id | varchar(128) | NO   |     | NULL    |                |
| edited    | tinyint(1)   | YES  |     | 0       |                |
| xp        | int(8)       | YES  |     | 0       |                |
| medals    | longtext     | YES  |     | '[]'    |                |
| on_server | tinyint(1)   | YES  |     | 1       |                |
+-----------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_level`;

CREATE TABLE `discord_level` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `member_id` varchar(128) NOT NULL,
  `edited` tinyint(1) DEFAULT 0,
  `xp` int(8) DEFAULT 0,
  `medals` longtext DEFAULT '[]',
  `on_server` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `guild_id` (`guild_id`,`member_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
