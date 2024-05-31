import network
import usocket
import ujson
from _consts import SSID, PW
from status_codes import StatusCode
from endpoint import Endpoint


class Server:
    endpoints = {}

    def __init__(self, essid: str = SSID, password: str = PW):
        """Initializes AP

        :param essid: Ap's ssid, defaults to SSID
        :type essid: str, optional
        :param password: Ap's password, defaults to PW
        :type password: str, optional
        """
        print("Initializing...")
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(
            essid=essid,
            authmode=network.AUTH_WPA_WPA2_PSK,
            password=password,
        )

        while not self.ap.active():
            pass

        print("Access point initialized")
        print(self.ap.ifconfig())
        print("# ==================== #")

        self.socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        self.socket.bind(("", 80))
        self.socket.listen(5)

    def add_endpoint(
        self,
        path: str,
        default_success_status_code: str = "200 OK",
        content_type: str = "application/json",
    ) -> Endpoint:
        """Adds a new endpoint

        :param path: Path of the endpoint
        :type path: str
        :param default_success_status_code: Default status code of the response, defaults to "200 OK"
        :type default_success_status_code: str, optional
        :param content_type: Default content type of the response, defaults to "application/json"
        :type content_type: str, optional

        :return: Returns a new Endpoint instance to customize
        :rtype: Endpoint
        """
        endpoint = Endpoint(path, default_success_status_code, content_type)
        self.endpoints.update({path: endpoint})
        return endpoint

    def find_req_endpoint(self, request: str) -> tuple[str, dict]:
        """Gets request endpoint and arguments

        :param request: Request
        :type request: str
        :return: A tuple containing the endpoint requested and kwargs dictionary
        :rtype: tuple[str, dict]
        """

        request = request.decode()
        request = request.replace("GET ", "")
        endpoint = request.split("HTTP")[0].replace(" ", "")
        kw = {}
        if "/?" in endpoint:
            endpoint, args = endpoint.split("?")
            args = args.split("&")
            for arg in args:
                k, v = arg.split("=")
                kw.update({k: v})

        kw = None if kw == {} else kw
        return (endpoint, kw)

    def manage_request(self, request: str):
        """Manages the request, executing endpoint if found

        :param request: Request
        :type request: str
        """
        try:
            endpoint, kw = self.find_req_endpoint(request)

            if endpoint not in self.endpoints.keys():
                return StatusCode._404, "{}"

            endpoint = self.endpoints.get(endpoint)

            status_code, body, on_finished = endpoint.run(**kw)
            return (
                f"HTTP/1.0 {status_code}\r\nContent-type: {endpoint.content_type}\r\n\r\n",
                body,
                on_finished,
            )
        except Exception:
            return (
                f"HTTP/1.0 {StatusCode._500}\r\nContent-type: application/json\r\n\r\n",
                "{}",
                None,
            )

    def start(self):
        """Starts the server"""
        print("Listening...")
        while True:
            conn, addr = self.socket.accept()
            request = conn.recv(1024)
            header, body, on_finish = self.manage_request(request)
            conn.write(header)
            conn.write(body)
            conn.close()
            if on_finish:
                on_finish()
