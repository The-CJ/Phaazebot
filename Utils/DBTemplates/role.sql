/*
DESCRIBE `web_role`;

+----------------+--------------+------+-----+---------+----------------+
| Field          | Type         | Null | Key | Default | Extra          |
+----------------+--------------+------+-----+---------+----------------+
| id             | int(11)      | NO   | PRI | NULL    | auto_increment |
| can_be_removed | tinyint(1)   | YES  |     | 0       |                |
| description    | varchar(512) | YES  |     | NULL    |                |
| name           | varchar(64)  | YES  | UNI | NULL    |                |
+----------------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `web_role`;

CREATE TABLE `web_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `can_be_removed` tinyint(1) DEFAULT 0,
  `description` varchar(512) DEFAULT NULL,
  `name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
