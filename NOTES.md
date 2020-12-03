## Programm call variables:

`python3.8 main.py`

### args

* -no-args
    * allows start without configuration

* -no-start
    * reads in all configurations, but doesn't actually start the bot

  -log-sql
    * prints all SQL Statements with inserted values to the console

  -show-configs
    * prints all successfully found config entrys

  -no-twitch-join
    * TwitchIRC only joins Client.nickname and no other channels

### kwargs

* --config_path=
    * set Custom path to configs file

* --config_type=
    * what filetype is used in config_path, default is 'phzcf'

* --debug=
    * all
        * Shows everything
    * "" (None / Empty) *(default)*
        * Shows nothing
    * Everything else can be found inside the code at the debug functions

* --http=
    * "" (None / Empty) *(default)*
        * Testing setup | Port 9001
    * live
        * Live HTTPS | Port 443 | Requires a SSL File
    * unsecure
        * Non SSL | Port 80
    * error_ssl
        * Forces Port 443 without loading SSL File
