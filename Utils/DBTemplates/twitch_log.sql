/*
DESCRIBE `twitch_log`;

+----------------+--------------+------+-----+---------------------+----------------+
| Field          | Type         | Null | Key | Default             | Extra          |
+----------------+--------------+------+-----+---------------------+----------------+
| id             | int(11)      | NO   | PRI | NULL                | auto_increment |
| channel_id     | varchar(128) | NO   | MUL | NULL                |                |
| content        | longtext     | YES  |     | NULL                |                |
| created_at     | datetime     | YES  |     | current_timestamp() |                |
| event_value    | bigint(20)   | NO   |     | NULL                |                |
| initiator_id   | varchar(128) | YES  |     | NULL                |                |
| initiator_name | varchar(256) | YES  |     | NULL                |                |
+----------------+--------------+------+-----+---------------------+----------------+
*/

-- SHOW CREATE TABLE `twitch_log`;

CREATE TABLE `twitch_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `channel_id` varchar(128) NOT NULL,
  `content` longtext DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `event_value` bigint(20) NOT NULL,
  `initiator_id` varchar(128) DEFAULT NULL,
  `initiator_name` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index_channel_id` (`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
