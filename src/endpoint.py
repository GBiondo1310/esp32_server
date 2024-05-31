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

        :param endpoint: The endpoint for the request
        :type endpoint: str
        :param default_success_status_code: The default status code if function call is successfull,
        defaults to StatusCode._200
        :type default_success_status_code: str, optional
        :param content_type: Content type of the response, defaults to "application/json"
        :type content_type: str, optional
        """

        self.endpoint = endpoint
        self.content_type = content_type
        self.default_status_code = default_success_status_code

    def __call__(self, function: object):
        """Decorator to quickly add the function to execute when the endpoint is requestes

        :Example usage:
        >>> e = Endpoint("/test_endpoint/")
        >>> @e
        >>> def inner_function(**kwargs):
        >>>     print(kwargs)
        >>>     return "200 OK", {}
        >>>     # or
        >>>     return None, None
        :NOTE: The inner function created needs to return wether
        a tuple (str, dict) or a tuple (None, None) or a combination of them
            * The first element of the tuple will be the response status code
            * The second element of the tuple will be the body of the response

        :param function: The function to execute
        :type function: Function"""
        self.inner_function = function

    def add_exception(self, exception: Exception, callback: object):
        """Adds a new handable exception

        :param exception: The exception to handle
        :type exception: Exception
        :param callback: The function to call in case this exception happens
        :type callback: object
        """

        self.exceptions.update({exception: callback})

    def on_exception(self, exception: Exception):
        """Decorator to quickly add an exception so there's no need to handle
        exception dictionary update

        :Example usage:
        >>> e = Endpoint("/test_endpoint/")
        >>>
        >>> @e.on_exception(CustomException)
        >>> def exception_handler():
        >>>     print("An exceptio occurred")
        >>>     return None, None
        >>>     # or
        >>>     return some_status_code, some_dictionary

        :NOTE: The exception callback created needs to return wether
        a tuple (str, dict) or a tuple (None, None) or a combination of them
            * The first element of the tuple will be the response status code
            * The second element of the tuple will be the body of the response

        :param exception: The exception to handle
        :type exception: Exception"""

        def decorator(function):
            def wrapper(*args, **kwargs):
                return function(*args, **kwargs)

            self.add_exception(exception, wrapper)
            return wrapper

        return decorator

    def on_finished(self):
        """Decorator to quickly add a function to call after the response is sent

        :Example usage:

        >>> e = Endpoint("/test_endpoint/")
        >>>
        >>> @e.on_finished()
        >>> def success():
        >>>     print("Response sent successfully")

        :NOTE: In this case the on_finished function doesn't need to return anyting"""

        def decorator(function):
            def wrapper(*args, **kwargs):
                return function(*args, **kwargs)

            self._on_finished = wrapper
            return wrapper

        return decorator

    def run(self, *args, **kwargs):
        """Function to perform all the needed operations whenever the endpoint is requested

        :return: tuple like (a_status_code, response_body, on_finished_function)
        :rtype: tuple
        """
        if not self.inner_function:
            raise NotImplementedError()

        try:
            print(self._on_finished)
            status_code, body = self.inner_function(*args, **kwargs)
            status_code = status_code if status_code else self.default_status_code
            body = body if body else {}
            return status_code, body, self._on_finished

        except Exception as e:
            for exception in self.exceptions.keys():
                if isinstance(e, exception):
                    on_error_func = self.exceptions.get(exception)
                    status_code, body = on_error_func()
                    status_code = (
                        status_code if status_code else "500 INTERNAL SERVER ERROR"
                    )
                    body = body if body else {}
                    return status_code, body, None
