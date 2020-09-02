/*
DESCRIBE `discord_log`;

+--------------+---------------+------+-----+---------------------+----------------+
| Field        | Type          | Null | Key | Default             | Extra          |
+--------------+---------------+------+-----+---------------------+----------------+
| id           | int(11)       | NO   | PRI | NULL                | auto_increment |
| guild_id     | varchar(128)  | NO   | MUL | NULL                |                |
| event_value  | bigint(20)    | NO   |     | NULL                |                |
| created_at   | datetime      | YES  |     | current_timestamp() |                |
| initiator_id | varchar(128)  | YES  |     | NULL                |                |
| content      | varchar(1750) | YES  |     | NULL                |                |
+--------------+---------------+------+-----+---------------------+----------------+
*/

-- SHOW CREATE TABLE `discord_log`;

CREATE TABLE `discord_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `event_value` bigint(20) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `initiator_id` varchar(128) DEFAULT NULL,
  `content` varchar(1750) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index_guild_id` (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
