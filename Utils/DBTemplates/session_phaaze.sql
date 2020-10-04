/*
DESCRIBE `session_phaaze`;

+------------+--------------+------+-----+---------------------+----------------+
| Field      | Type         | Null | Key | Default             | Extra          |
+------------+--------------+------+-----+---------------------+----------------+
| id         | int(11)      | NO   | PRI | NULL                | auto_increment |
| session    | varchar(128) | NO   | UNI | NULL                |                |
| created_at | datetime     | YES  |     | current_timestamp() |                |
| user_id    | int(11)      | YES  |     | NULL                |                |
+------------+--------------+------+-----+---------------------+----------------+
*/

-- SHOW CREATE TABLE `session_phaaze`;

CREATE TABLE `session_phaaze` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session` varchar(128) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session` (`session`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
