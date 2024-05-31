class InternalServerError(Exception):
    """Internal Server Error"""

    def __init__(self, data: str):
        """Internal Server Error"""

        message = f"InternalServerError: {data}"
        super().__init__(message)
