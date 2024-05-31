# ESP32 Server

Easily set up a simple server on your ESP32

## Pre-requisites

* Flash Micropython on your ESP32
    * Install esptool.py with ```pip install esptool``` to flash Micropython firmware
    * Check [esptool documentation](https://docs.espressif.com/projects/esptool/en/latest/esp32/) to find out how to flash Micropython firmware

* Install ampy with ```pip install ampy``` to be able to upload files to the board
    * You can upload files with ```ampy -p PORT put filename```

## Upload files

1. Connect your board and set it to BOOT mode;
2. Modify SSID and PASSWORD in consts file
3. Upload the two required files with:
    ```
    ampy -p PORT put src/_consts.py
    ampy -p PORT put src/endpoint.py
    ampy -p PORT put src/exceptions.py
    ampy -p PORT put src/server.py
    ampy -p PORT put src/status_codes.py
    ```
4. You're good to go

## Example

```boot.py```
```py
import ujson as json

from new_server import Server
from endpoint import Endpoint
from status_codes import StatusCode
from exceptions import InternalServerError

server = Server()
test_endpoint = server.add_endpoint("/test_endpoint/")

@test1
def endpoint_function(value, **kw):
    if int(value)>5:
        raise InternalServerError("Should raise InternalServerError")

    return StatusCode._200, json.dumps({"esit":str(value)})

@test1.on_exception(InternalServerError)
def onInternalServerError():
    print("Internal server error raised")
    return None, None


@test1.on_finished()
def onFinished():
    print("Finished")

server.start()
```

To test that the server is running correctly:

1. Connect to the newly created network

2. Open up your browser and search for this URL: ```http://192.168.4.1/test_endpoint/?value=4```

3. You should receive back ```{"esit":"4"}``` from the callback1 function

If the query parameter "value" is greater than 5, InternalServerError will be raised and status code 500 will be returned.
Check out example folder for more examples

## NOTES

* This package is currently under developement and is not intended for handling complex requests
* This package currently handles only GET requests, you can implement it on your own to handle other kinds of request
* The src directory contains two versions of every file, one is documented and the other is not in order to save space on the board

---

## Bonus
If you're using an IDE with autocompletion for Micropython developement, you can check out my library [micropython_libraries](https://github.com/GBiondo1310/micropython_libraries.git)