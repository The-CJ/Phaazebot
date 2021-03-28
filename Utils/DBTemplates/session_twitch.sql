/*
DESCRIBE `session_twitch`;

+---------------+--------------+------+-----+---------------------+----------------+
| Field         | Type         | Null | Key | Default             | Extra          |
+---------------+--------------+------+-----+---------------------+----------------+
| id            | int(11)      | NO   | PRI | NULL                | auto_increment |
| session       | varchar(128) | YES  | UNI | NULL                |                |
| access_token  | varchar(128) | YES  |     | NULL                |                |
| created_at    | datetime     | YES  |     | current_timestamp() |                |
| refresh_token | varchar(128) | YES  |     | NULL                |                |
| scope         | varchar(512) | YES  |     | NULL                |                |
| token_type    | varchar(64)  | YES  |     | Bearer              |                |
| user_info     | longtext     | YES  |     | '{}'                |                |
+---------------+--------------+------+-----+---------------------+----------------+
*/

-- SHOW CREATE TABLE `session_twitch`;

CREATE TABLE `session_twitch` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session` varchar(128) DEFAULT NULL,
  `access_token` varchar(128) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `refresh_token` varchar(128) DEFAULT NULL,
  `scope` varchar(512) DEFAULT NULL,
  `token_type` varchar(64) DEFAULT 'Bearer',
  `user_info` longtext DEFAULT '{}',
  PRIMARY KEY (`id`),
  UNIQUE KEY `session` (`session`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
