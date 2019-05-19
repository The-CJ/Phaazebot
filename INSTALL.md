Setup only testet on Ubuntu 18.04.2 LTS
Requires python3.7+
```
wget -qO - 'https://bintray.com/user/downloadSubjectPublicKey?username=bintray' | apt-key add -
echo "deb http://dl.bintray.com/mosquito/cysystemd bionic main" > /etc/apt/sources.list.d/cysystemd.list
apt-get update
apt-get install python-cysystemd python3-cysystemd
apt-get install python3.7-dev
apt-get install libsystemd-dev python3-systemd
python3.7 -m pip install -r requirement.txt

```
