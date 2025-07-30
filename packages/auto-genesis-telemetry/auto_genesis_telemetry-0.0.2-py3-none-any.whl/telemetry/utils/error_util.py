from typing import Optional


class TelemetryError(Exception):
    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause
        self.name = "TelemetryError"
