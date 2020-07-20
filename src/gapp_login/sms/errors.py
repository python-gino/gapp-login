from typing import Optional


class SMSError(Exception):
    def __init__(self, code, error: Optional[str] = None) -> None:
        self.code = code
        self.error = error

    def __repr__(self) -> str:
        return f"SMSError(code={self.code}, error={self.error!r})"
