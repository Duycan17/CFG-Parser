"""Custom exceptions for the application."""

from typing import Any


class CFGParserException(Exception):
    """Base exception for CFG Parser errors."""

    def __init__(self, message: str, details: Any = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)


class JavaParseError(CFGParserException):
    """Raised when Java code parsing fails."""

    pass


class CFGBuildError(CFGParserException):
    """Raised when CFG construction fails."""

    pass


class DDGBuildError(CFGParserException):
    """Raised when DDG construction fails."""

    pass


class FileTooLargeError(CFGParserException):
    """Raised when uploaded file exceeds size limit."""

    pass


class InvalidJavaCodeError(CFGParserException):
    """Raised when the provided code is not valid Java."""

    pass
