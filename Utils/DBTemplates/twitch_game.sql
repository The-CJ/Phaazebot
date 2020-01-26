/*
DESCRIBE `twitch_game`;

+---------+--------------+------+-----+---------+----------------+
| Field   | Type         | Null | Key | Default | Extra          |
+---------+--------------+------+-----+---------+----------------+
| id      | int(11)      | NO   | PRI | NULL    | auto_increment |
| game_id | varchar(128) | NO   | UNI | NULL    |                |
| name    | varchar(128) | NO   |     | NULL    |                |
+---------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `twitch_game`;

CREATE TABLE `twitch_game` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `game_id` varchar(128) NOT NULL,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `game_id` (`game_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
