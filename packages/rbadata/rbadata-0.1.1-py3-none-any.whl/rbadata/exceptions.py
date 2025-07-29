"""
Custom exceptions for rbadata
"""


class RBADataError(Exception):
    """Base exception for all rbadata errors."""
    pass


class DownloadError(RBADataError):
    """Raised when a download fails."""
    pass


class DataError(RBADataError):
    """Raised when data cannot be parsed or is invalid."""
    pass


class ConnectionError(RBADataError):
    """Raised when connection to RBA cannot be established."""
    pass