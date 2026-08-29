class AppException(Exception):
    """Base exception app"""
    status_code = 500
    detail = "Internal error"

    def __init__(self, detail: str | None = None):
        super().__init__(detail or self.detail)
        if detail:
            self.detail = detail

class NotFoundError(AppException):
    status_code = 404
    detail = "Resource not found"

class ConflictError(AppException):
    status_code = 409
    detail = "Resource conflict"

class BadRequestError(AppException):
    status_code = 400
    detail = "Bad request"