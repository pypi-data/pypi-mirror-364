class APIException(Exception):
    def __init__(self, status_code, message):
        super().__init__(f"Code {status_code}: {message}")
        self.status_code = status_code
        self.message = message


class MapHubException(Exception):
    def __init__(self, message):
        super().__init__(message)