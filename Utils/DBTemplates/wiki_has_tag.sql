/*
DESCRIBE `wiki_has_tag`;

+---------+--------------+------+-----+---------+----------------+
| Field   | Type         | Null | Key | Default | Extra          |
+---------+--------------+------+-----+---------+----------------+
| id      | int(11)      | NO   | PRI | NULL    | auto_increment |
| wiki_id | int(11)      | NO   | MUL | NULL    |                |
| tag     | varchar(128) | NO   |     | NULL    |                |
+---------+--------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `wiki_has_tag`;

CREATE TABLE `wiki_has_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `wiki_id` int(11) NOT NULL,
  `tag` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tag_key` (`wiki_id`, `tag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
