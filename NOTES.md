## Programm call variables:

`python3.8 main.py`

### args

* -no-args
    * allows start without configuration

### kwargs

* --logging=
    * console *(default)*

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
