Setup testet on:
  + Ubuntu 18.04.2 LTS
  + Ubuntu 18.04.3 LTS
  + MariaDB 10 (Other SQL may work, not sure)

Requires always the newest Python Version (3.8)
[Because why should you stay on a lower one?]

## Base installation
```sh
# before we start
apt-get update
apt-get dist-upgrade

# only if not already installed
# apt-get install vim
# apt-get install git

# python
apt-get install python3.8
apt-get install python3-pip
apt-get install python3.8-dev
python3.8 -m pip install -r requirement.txt

# mariadb
curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | sudo bash
apt-get install mariadb-server
```

## Create Database
```sql
CREATE DATABASE `phaaze` DEFAULT CHARACTER SET utf8mb4;
```
```sh
# To generate the db strukture
cat Utils/DBTemplates/* | mysql phaaze
```
```sql
GRANT ALL PRIVILEGES ON `phaaze`.* TO "phaazebot"@"localhost" IDENTIFIED BY "your_password";
FLUSH PRIVILEGES;
```

## SSL Setup
```sh
apt-get install certbot
certbot certonly
# then follow instructions
```

## Create file for systemd (/etc/systemd/system/phaaze.service)
```
[Unit]
Description=phaaze

[Service]
ExecStart=/usr/bin/python3.8 /path/to/folder/main.py --http=test --debug=
WorkingDirectory=/path/to/folder/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```
## Active systemd files
```sh
systemctl enable phaaze.service
systemctl start phaaze.service
```

## Crontab entrys (/etc/crontab)
```
# renew ssl
0 1 * * * root certbot renew > /dev/null 2>&1

# keep system up to date
0 2 * * * root apt-get update -y > /dev/null 2>&1
0 3 * * * root apt-get dist-upgrade -y > /dev/null 2>&1

# restart server on sunday morning
0 4 * * 0 root systemctl reboot > /dev/null 2>&1
```
