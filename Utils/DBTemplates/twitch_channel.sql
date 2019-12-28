/*
DESCRIBE `twitch_channel`;

+------------+--------------+------+-----+---------+----------------+
| Field      | Type         | Null | Key | Default | Extra          |
+------------+--------------+------+-----+---------+----------------+
| id         | int(11)      | NO   | PRI | NULL    | auto_increment |
| channel_id | varchar(128) | NO   | UNI | NULL    |                |
| game_id    | varchar(128) | YES  |     | NULL    |                |
| live       | tinyint(1)   | YES  |     | 0       |                |
| managed    | tinyint(1)   | YES  |     | 0       |                |
+------------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `twitch_channel`;

CREATE TABLE `twitch_channel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `channel_id` varchar(128) NOT NULL,
  `game_id` varchar(128) DEFAULT NULL,
  `live` tinyint(1) DEFAULT 0,
  `managed` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `channel_id` (`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
