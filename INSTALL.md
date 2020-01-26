Setup testet on:
  + Ubuntu 18.04.2 LTS
  + Ubuntu 18.04.3 LTS
  + MariaDB 10 (Other SQL may work, not sure)

Requires always the newest Python Version (3.8)
[Because why should you stay on a lower one?]

```
apt-get update
apt-get install python3.8
apt-get install python3-pip
apt-get install python3.8-dev
python3.8 -m pip install -r requirement.txt
```

Create Database
```sql
CREATE DATABASE `phaaze` DEFAULT CHARACTER SET utf8mb4;
```
```
# To generate the db strukture
cat Utils/DBTemplates/* | mysql phaaze
```
```sql
GRANT ALL PRIVILEGES ON `phaaze`.* TO "phaazebot"@"localhost" IDENTIFIED BY "your_password";
```
