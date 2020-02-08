/*
DESCRIBE `twitch_user_name`;

+--------------+--------------+------+-----+---------+----------------+
| Field        | Type         | Null | Key | Default | Extra          |
+--------------+--------------+------+-----+---------+----------------+
| id           | int(11)      | NO   | PRI | NULL    | auto_increment |
| user_id      | varchar(128) | NO   | UNI | NULL    |                |
| user_name    | varchar(128) | YES  |     | NULL    |                |
| display_name | varchar(128) | YES  |     | NULL    |                |
+--------------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `twitch_user_name`;

CREATE TABLE `twitch_user_name` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(128) NOT NULL,
  `user_name` varchar(128) DEFAULT NULL,
  `user_display_name` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
