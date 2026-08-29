class DomainError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        httpStatus: int = 400,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.httpStatus = httpStatus
