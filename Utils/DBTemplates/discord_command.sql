/*
DESCRIBE `discord_command`;

+-------------------+---------------+------+-----+---------+----------------+
| Field             | Type          | Null | Key | Default | Extra          |
+-------------------+---------------+------+-----+---------+----------------+
| id                | int(11)       | NO   | PRI | NULL    | auto_increment |
| guild_id          | varchar(128)  | NO   | MUL | NULL    |                |
| trigger           | varchar(64)   | NO   |     | NULL    |                |
| active            | tinyint(64)   | NO   |     | 1       |                |
| content           | varchar(1750) | YES  |     | NULL    |                |
| function          | varchar(256)  | NO   |     | NULL    |                |
| complex           | tinyint(1)    | YES  |     | 0       |                |
| hidden            | tinyint(1)    | YES  |     | 0       |                |
| require           | int(4)        | YES  |     | 0       |                |
| required_currency | int(8)        | YES  |     | 0       |                |
| uses              | int(8)        | YES  |     | 0       |                |
| cooldown          | int(8)        | YES  |     | 10      |                |
+-------------------+---------------+------+-----+---------+----------------+
*/

-- SHOW CREATE TABLE `discord_command`;

CREATE TABLE `discord_command` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_id` varchar(128) NOT NULL,
  `trigger` varchar(64) NOT NULL,
  `active` tinyint(1) DEFAULT 1,
  `content` varchar(1750) DEFAULT NULL,
  `function` varchar(256) NOT NULL,
  `complex` tinyint(1) DEFAULT 0,
  `hidden` tinyint(1) DEFAULT 0,
  `require` int(4) DEFAULT 0,
  `required_currency` int(8) DEFAULT 0,
  `uses` int(8) DEFAULT 0,
  `cooldown` int(8) DEFAULT 10,
  PRIMARY KEY (`id`),
  UNIQUE KEY `command_key` (`guild_id`,`trigger`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
