"""Example 1: basic endpoint creation"""

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

    # Now we need to return:
    # - A status code which you can easily pick from StatusCode class
    # - A json parsed dictionary used as the body of the response,
    #   alternatively None can be returned and the body will automatically be set to "{}"

    return StatusCode._200, {"esit": "ok"}

    # or
    # return StatusCode._200, None


# To manually test out this function with requests you can:
# >>> import requests
# >>> response = requests.get("http://192.168.4.1/test_endpoint/?value=4&additional_param=5")
# >>> print(response.json())
