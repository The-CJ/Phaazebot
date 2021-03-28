/*
DESCRIBE `web_user+web_role`;

+---------+---------+------+-----+---------+----------------+
| Field   | Type    | Null | Key | Default | Extra          |
+---------+---------+------+-----+---------+----------------+
| id      | int(11) | NO   | PRI | NULL    | auto_increment |
| user_id | int(11) | NO   | MUL | NULL    |                |
| role_id | int(11) | NO   |     | NULL    |                |
+---------+---------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `web_user+web_role`;

CREATE TABLE `web_user+web_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_key` (`user_id`, `role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
