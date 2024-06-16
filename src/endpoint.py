from status_codes import StatusCode


class Endpoint:
    exceptions = {}
    _on_finished = None
    inner_function = None

    def __init__(
        self,
        endpoint: str,
        default_success_status_code: str = StatusCode._200,
        content_type: str = "application/json",
    ):
        """Creates a new endpoint for the server

        :param endpoint: The endpoint of the request
        :type endpoint: str
        :param default_success_status_code: The default status code if function call is successful,
        defaults to StatusCode._200
        :type default_success_status_code: str, optional
        :param content_type: Content type of ther response, defaults to "application/json"
        :type content_type: str, optional
        """

        self.endpoint = endpoint
        self.content_type = content_type
        self.default_status_code = default_success_status_code

    def __call__(self, function):
        """Decorator to quickly add the function to execute when the endpoint is requestes

        :Example usage:
        >>> e = Endpoint("/test_endpoint/")
        >>> @e
        >>> def inner_function(**kwargs):
        >>>     print(kwargs)
        >>>     return "200 OK", {}
        >>>     # or
        >>>     return None, None
        :NOTE: The exception callback created needs to return a tuple (str, dict)
            * The first element of the tuple will be the response status code
            * The second element of the tuple will be the body of the response


        :param function: The function to execute
        :type function: Function"""

        self.inner_function = function

    def on_exception(self, exception: Exception):
        """Decorator to quickly add an exception so there's no need to handle
        exception dictionary update

        :Example usage:
        >>> e = Endpoint("/test_endpoint/")
        >>>
        >>> @e.on_exception(CustomException)
        >>> def exception_handler():
        >>>     print("An exception occurred")
        >>>     return some_status_code, some_dictionary

        :NOTE: The exception callback created needs to return a tuple (str, dict)
            * The first element of the tuple will be the response status code
            * The second element of the tuple will be the body of the response

        :param exception: The exception to handle
        :type exception: Exception"""

        def inner(function):
            def wrapper(*args, **kwargs):
                result = function(*args, **kwargs)
                return result

            self.exceptions.update({exception: wrapper})
            return wrapper

        return inner

    def on_finished(self, function):
        """Decorator to quickly add a function to call after the response is sent

        :Example usage:

        >>> e = Endpoint("/test_endpoint/")
        >>>
        >>> @e.on_finished()
        >>> def success():
        >>>     print("Response sent successfully")

        :NOTE: In this case the on_finished function doesn't need to return anyting"""

        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)
            return result

        self._on_finished = wrapper
        return wrapper

    def run(self, *args, **kwargs):
        """Function to perform all the needed operations whenever the endpoint is requested

        :return: tuple like (status_code, response_body, on_finished_function)
        :rtype: tuple
        """
        try:
            status_code, body = self.inner_function(*args, **kwargs)
            return status_code, body, self._on_finished
        except Exception as e:
            func = None
            for exception in self.exceptions.keys():
                if isinstance(e, exception):
                    func = self.exceptions.get(exception)
                    break

            if not func:
                return StatusCode._500, {}, self._on_finished

            status_code, body = func()
            return status_code, body, self._on_finished
