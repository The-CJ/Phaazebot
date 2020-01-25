/*
DESCRIBE `wiki`;

+------------+--------------+------+-----+---------------------+----------------+
| Field      | Type         | Null | Key | Default             | Extra          |
+------------+--------------+------+-----+---------------------+----------------+
| id         | int(11)      | NO   | PRI | NULL                | auto_increment |
| title      | varchar(128) | YES  |     | NULL                |                |
| content    | longtext     | YES  |     | ''                  |                |
| url_id     | varchar(64)  | YES  | UNI | NULL                |                |
| mod_only   | tinyint(1)   | YES  |     | 0                   |                |
| created_at | datetime     | NO   |     | current_timestamp() |                |
| created_by | int(8)       | NO   |     | NULL                |                |
| edited_at  | datetime     | YES  |     | NULL                |                |
| edited_by  | int(8)       | YES  |     | NULL                |                |
+------------+--------------+------+-----+---------------------+----------------+
*/

-- SHOW CREATE TABLE `wiki`;

CREATE TABLE `wiki` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(128) DEFAULT NULL,
  `content` longtext DEFAULT '',
  `url_id` varchar(64) DEFAULT NULL,
  `mod_only` tinyint(1) DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `created_by` int(8) NOT NULL,
  `edited_at` datetime DEFAULT NULL,
  `edited_by` int(8) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url_id` (`url_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
