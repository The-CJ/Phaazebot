/*
DESCRIBE `setting`;

+------------+--------------+------+-----+---------------------+-------+
| Field      | Type         | Null | Key | Default             | Extra |
+------------+--------------+------+-----+---------------------+-------+
| key        | varchar(128) | NO   | PRI | NULL                |       |
| value      | text         | YES  |     | NULL                |       |
+------------+--------------+------+-----+---------------------+-------+
*/

-- SHOW CREATE TABLE `setting`;

CREATE TABLE `setting` (
  `key` varchar(128) NOT NULL,
  `value` text DEFAULT NULL,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
