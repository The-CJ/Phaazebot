/*
DESCRIBE `twitch_known_bot`;

+--------+--------------+------+-----+---------+----------------+
| Field  | Type         | Null | Key | Default | Extra          |
+--------+--------------+------+-----+---------+----------------+
| id     | int(11)      | NO   | PRI | NULL    | auto_increment |
| name   | varchar(128) | YES  | UNI | NULL    |                |
| bot_id | varchar(128) | YES  | UNI | NULL    |                |
+--------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `twitch_known_bot`;

CREATE TABLE `twitch_known_bot` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) DEFAULT NULL,
  `bot_id` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `bot_id` (`bot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
