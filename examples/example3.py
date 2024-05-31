"""Example3: on_finished function"""

from new_server import Server
from endpoint import Endpoint
from status_codes import StatusCode
from exceptions import InternalServerError
import ujson as json

server = Server()


endpoint = server.add_endpoint("/test_endpoint/")


@endpoint
def callback(value, **kw):
    print(value)
    print(kw)

    1 / 0

    return StatusCode._200, {"esit": "ok"}


@endpoint.on_exception(ZeroDivisionError)
def handle_zero_division():
    print("Zero division catched")

    return StatusCode._400, None


# Sometimes you neeed to execute functions after the connection with the client is closed and response is sent.
# You can implement an on_finished function which will be executed efter the connection is closed


@endpoint.on_finished()
def conn_closed_function():
    print("Connection is now closed, you can leave")

    # This function can return anything or None and will be executed after conn.close() function of the server


# To manually test out this function with requests you can:
# >>> import requests
# >>> response = requests.get("http://192.168.4.1/test_endpoint/?value=4&additional_param=5")
# >>> print(response.json())
