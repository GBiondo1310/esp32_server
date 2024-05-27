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
    ampy -p PORT put src/server.py
    ```
4. You're good to go

## Example


```boot.py```
```py
from server import Server

server = Server()

def callback1(**kw):
    """Example function"""

    for k, v in kw.items():
        print(f"{k} : {v}")

    # NOTE: The return value if provided, will be the body of the response; if not provided, the body will be created (empty) according to the content type

    return {"esit":"ok"} 

def on_finish(**kw):
    """Example of a function that is called after the response is sent to the client"""
    print("This happens after the response is sent to the client")
    for k, v in kw.items():
        print(f"{k} : {v})


server.add_endpoint("/test_callback/", callback1, "200 OK", "application/json", on_finish)
server.start()
```

To test that the server is running correctly:

1. Connect to the newly created network

2. Open up your browser and search for this URL: ```http://192.168.4.1/test_callback/?k1=v1&k2=v2&k3=v3&of_k4=v4&of_k5=v5```

3. You should receive back ```{"esit":"ok"}``` from the callback1 function

4. If you are running a repl on your ESP32, you should see a similar output:
    ```
    Type [C-a] [C-h] to see available commands
    Terminal ready
    ets Jun  8 2016 00:22:57

    rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
    configsip: 0, SPIWP:0xee
    clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00
    mode:DIO, clock div:2
    load:0x3fff0030,len:4540
    ho 0 tail 12 room 4
    load:0x40078000,len:12344
    ho 0 tail 12 room 4
    load:0x40080400,len:4124
    entry 0x40080680
    MicroPython v1.19.1 on 2022-06-18; ESP32 module with ESP32
    Type "help()" for more information.

    k1 : v1
    k2 : v2
    k3 : v3
    This happens after the response is sent to the client
    k4 : v4
    k5 : v5
    ```
    - The first 3 lines are printed by the callback1 print statement
    - The last 3 lines are printed by the on_finished print statements

## NOTES

* This package is currently under developement and is not intended for handling complex requests
* This package currently handles only GET requests, you can implement it on your own to handle other kinds of request
* The src directory contains both two versions of both _consts and server files:
    * A documented version:
        * _consts_documented.py
        * server_documented.py

    * A lightweight not documented version which also does not have print statements in order to save some memory on the board.
        * _const.py
        * server.py

## In future updates

* Status codes quick references: To quickly pick a status code for the response
* on_error function callback
* on_not_found function callback

---

## Bonus
If you're using an IDE with autocompletion for Micropython developement, you can check out my library [micropython_libraries](https://github.com/GBiondo1310/micropython_libraries.git)