from typing import  Any

class AppException(RuntimeError):
    def __init__(self, code: int=400, status_code: int=400, msg: str="application error", data: Any=None):
        self.code = code
        self.status_code = status_code
        self.msg = msg
        self.data = data
        super().__init__()

class BadRequestError(AppException):
    def __init__(self, msg: str = "client request error"):
        super().__init__(status_code=400, code=400, msg=msg)


class NotFoundError(AppException):


    def __init__(self, msg: str = "resource not found"):
        super().__init__(status_code=404, code=404, msg=msg)

class ValidationError(AppException):

    def __init__(self, msg: str = "parameter validation error"):
        super().__init__(status_code=422, code=422, msg=msg)


class TooManusRequestsError(AppException):

    def __init__(self, msg: str = "too many requests, please try again later"):
        super().__init__(status_code=429, code=429, msg=msg)


class ServerRequestsError(AppException):

    def __init__(self, msg: str = "internal server error"):
        super().__init__(status_code=500, code=500, msg=msg)
