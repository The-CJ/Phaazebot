/*
DESCRIBE `twitch_punish_linkwhitelist`;

+------------+--------------+------+-----+---------+----------------+
| Field      | Type         | Null | Key | Default | Extra          |
+------------+--------------+------+-----+---------+----------------+
| id         | int(11)      | NO   | PRI | NULL    | auto_increment |
| channel_id | varchar(128) | NO   |     | NULL    |                |
| link       | varchar(512) | NO   |     | NULL    |                |
+------------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `twitch_punish_linkwhitelist`;

CREATE TABLE `twitch_punish_linkwhitelist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `channel_id` varchar(128) NOT NULL,
  `link` varchar(512) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
