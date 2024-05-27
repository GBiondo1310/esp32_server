import network
import usocket
import ujson

from _consts import SSID, PW, NOT_FOUND, INTERNAL_SERVER_ERROR


class Server:
    endpoints = {}

    def __init__(self, essid: str = SSID, password: str = PW):
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(
            essid=essid, authmode=network.AUTH_WPA_WPA2_PSK, password=password
        )

        while not self.ap.active():
            pass

        self.socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        self.socket.bind(("", 80))
        self.socket.listen(5)

    def add_endpoint(
        self,
        endpoint: str,
        callback: object,
        status_code: str,
        content_type: str,
        on_finish: object = None,
    ) -> None:
        self.endpoints.update(
            {
                endpoint: {
                    "callback": callback,
                    "status_code": status_code,
                    "content_type": content_type,
                    "on_finish": on_finish,
                }
            }
        )

    def find_req_endpoint(self, request: str):
        request = request.decode()
        request = request.replace("GET ", "")
        endpoint = request.split("HTTP")[0].replace(" ", "")
        kw = {}
        of_kw = {}  #: On finished kwargs
        if "/?" in endpoint:
            endpoint, args = endpoint.split("?")
            args = args.split("&")
            for arg in args:
                if "of_" in arg:
                    k, v = arg.split("=")
                    k = k.replace("of_", "")
                    of_kw.update({k: v})
                    continue
                k, v = arg.split("=")
                kw.update({k: v})

        kw = None if kw == {} else kw
        return (endpoint, kw, of_kw)

    def manage_request(self, request: str):
        try:
            endpoint, kw, of_kw = self.find_req_endpoint(request)
            if endpoint not in self.endpoints.keys():
                return (
                    NOT_FOUND,
                    ujson.dumps({"Esit": f"Endpoint not found: {endpoint}"}),
                    None,
                    None,
                )

            callback = self.endpoints.get(endpoint).get("callback")
            on_finish = self.endpoints.get(endpoint).get("on_finish")

            if kw:
                response_body = callback(**kw)
            else:
                response_body = callback()
            content_type = self.endpoints.get(endpoint).get("content_type")
            status_code = self.endpoints.get(endpoint).get("status_code")
            if content_type == "application/json":
                response_body = ujson.dumps(response_body) if response_body else "{}"
            else:
                response_body = str(response_body) if response_body else ""

            return (
                f"HTTP/1.0 {status_code}\r\nContent-type: {content_type}\r\n\r\n",
                response_body,
                on_finish,
                of_kw,
            )
        except Exception:
            return (
                INTERNAL_SERVER_ERROR,
                ujson.dumps({"esit": "Internal server error"}),
                None,
                None,
            )

    def start(self):
        while True:
            conn, addr = self.socket.accept()
            request = conn.recv(1024)
            print(request)  # DEBUG
            header, body, on_finish, on_finish_kw = self.manage_request(request)
            conn.write(header)
            conn.write(body)
            conn.close()
            if on_finish:
                on_finish(**on_finish_kw)
