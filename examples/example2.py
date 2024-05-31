"""Example2: Custom error handling"""

from new_server import Server
from endpoint import Endpoint
from status_codes import StatusCode
from exceptions import InternalServerError
import ujson as json

server = Server()


endpoint = server.add_endpoint("/test_endpoint/")


# Endpoint callback creation:
@endpoint
def callback(value, **kw):
    print(value)
    print(kw)

    # Let's make the function to raise ZeroDivisionError:

    1 / 0

    return StatusCode._200, {"esit": "ok"}


# If the error is left unhandled, the response status code will automatically be 500 Internal server error


# To handle the specific error:
@endpoint.on_exception(ZeroDivisionError)
def handle_zero_division():
    print("Zero division catched")

    # Functions that are created with this method will have to return a status code AND a json parsed dictionary or None
    return StatusCode._400, None


# Now the specific error ZeroDivisionError is handled, and when it occurs, the response status_code will be 400

# To manually test out this function with requests you can:
# >>> import requests
# >>> response = requests.get("http://192.168.4.1/test_endpoint/?value=4&additional_param=5")
# >>> print(response.json())
