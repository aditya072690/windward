from fastapi import HTTPException


class OutOfWindowError(HTTPException):
    def __init__(self, detail: str = "Date outside decision window"):
        super().__init__(status_code=400, detail=detail)


class NoDataError(HTTPException):
    def __init__(self, detail: str = "No data available"):
        super().__init__(status_code=404, detail=detail)
