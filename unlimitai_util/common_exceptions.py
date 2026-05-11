class NetworkError(Exception):
    pass

class LocalNetworkError(NetworkError):
    pass

class ApiServerError(NetworkError):
    pass

class ProcessingInterrupted(Exception):
    pass

class UnlimitAIError(Exception):
    def __init__(self, message, status_code=None, response_body=None):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)

class ValidationError(UnlimitAIError):
    pass
