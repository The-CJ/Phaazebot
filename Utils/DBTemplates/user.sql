/*
DESCRIBE `user`;

+------------------+--------------+------+-----+---------------------+----------------+
| Field            | Type         | Null | Key | Default             | Extra          |
+------------------+--------------+------+-----+---------------------+----------------+
| id               | int(11)      | NO   | PRI | NULL                | auto_increment |
| username         | varchar(64)  | YES  | UNI | NULL                |                |
| email            | varchar(128) | YES  | UNI | NULL                |                |
| verified         | tinyint(1)   | YES  |     | 0                   |                |
| password         | varchar(256) | NO   |     | NULL                |                |
| created_at       | datetime     | YES  |     | current_timestamp() |                |
| edited_at        | datetime     | YES  |     | NULL                |                |
| last_login       | datetime     | YES  |     | NULL                |                |
| username_changed | int(8)       | YES  |     | 0                   |                |
+------------------+--------------+------+-----+---------------------+----------------+
*/

-- SHOW CREATE TABLE `user`;

CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  `verified` tinyint(1) DEFAULT 0,
  `password` varchar(256) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `edited_at` datetime DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `username_changed` int(8) DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
