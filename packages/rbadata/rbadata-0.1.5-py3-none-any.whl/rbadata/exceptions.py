"""
Custom exceptions for rbadata with enhanced error messages
"""

from typing import Optional


class RBADataError(Exception):
    """
    Base exception for all rbadata errors.

    Provides detailed context about what went wrong and potential solutions.
    """

    def __init__(self, message: str, context: Optional[dict] = None):
        """
        Initialize the exception with a message and optional context.

        Parameters
        ----------
        message : str
            The error message
        context : dict, optional
            Additional context information (e.g., table_no, series_id, url)
        """
        self.context = context or {}

        # Build detailed message
        detailed_message = message
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            detailed_message = f"{message} (Context: {context_str})"

        super().__init__(detailed_message)


class DownloadError(RBADataError):
    """
    Raised when a download fails.

    Provides information about:
    - The URL that failed
    - The HTTP status code (if available)
    - Network errors
    - Suggestions for resolution
    """

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialize download error with specific details.

        Parameters
        ----------
        message : str
            Error message
        url : str, optional
            The URL that failed to download
        status_code : int, optional
            HTTP status code if available
        """
        context = kwargs.get("context", {})
        if url:
            context["url"] = url
        if status_code:
            context["status_code"] = status_code

        # Add helpful suggestions based on status code
        if status_code == 404:
            message += " (The requested table may not exist or URL may have changed)"
        elif status_code == 403:
            message += " (Access denied - check if RBA website is accessible)"
        elif status_code == 500:
            message += " (RBA server error - try again later)"
        elif status_code and status_code >= 400:
            message += f" (HTTP error {status_code})"

        super().__init__(message, context)


class DataError(RBADataError):
    """
    Raised when data cannot be parsed or is invalid.

    Provides information about:
    - The specific parsing issue
    - The table/series affected
    - Expected vs actual format
    """

    def __init__(
        self,
        message: str,
        table_no: Optional[str] = None,
        series_id: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize data parsing error.

        Parameters
        ----------
        message : str
            Error message
        table_no : str, optional
            Table number where error occurred
        series_id : str, optional
            Series ID where error occurred
        """
        context = kwargs.get("context", {})
        if table_no:
            context["table_no"] = table_no
        if series_id:
            context["series_id"] = series_id

        super().__init__(message, context)


class ConnectionError(RBADataError):
    """
    Raised when connection to RBA cannot be established.

    Provides information about:
    - Network connectivity issues
    - Proxy/firewall problems
    - DNS resolution failures
    """

    def __init__(self, message: str = "Cannot connect to RBA website", **kwargs):
        """Initialize connection error."""
        suggestions = [
            "Check your internet connection",
            "Verify https://www.rba.gov.au is accessible",
            "Check if you're behind a corporate proxy",
            "Try setting custom headers or download method",
        ]

        full_message = f"{message}. Suggestions: {'; '.join(suggestions)}"
        super().__init__(full_message, kwargs.get("context"))


class SeriesNotFoundError(DataError):
    """
    Raised when requested series IDs are not found.

    Provides:
    - List of missing series
    - Available series in the table
    - Suggestions for similar series
    """

    def __init__(
        self,
        missing_series: list,
        table_no: Optional[str] = None,
        available_series: Optional[list] = None,
    ):
        """
        Initialize series not found error.

        Parameters
        ----------
        missing_series : list
            List of series IDs that were not found
        table_no : str, optional
            Table where series were searched
        available_series : list, optional
            List of available series in the table
        """
        message = f"Series not found: {', '.join(missing_series)}"

        if table_no:
            message += f" in table {table_no}"

        if available_series:
            # Find similar series (simple string matching)
            suggestions = []
            for missing in missing_series:
                similar = [
                    s for s in available_series if missing[:3].upper() in s.upper()
                ]
                if similar:
                    suggestions.append(f"{missing} -> {', '.join(similar[:3])}")

            if suggestions:
                message += f". Did you mean: {'; '.join(suggestions)}"

        super().__init__(message, table_no=table_no)


class CacheError(RBADataError):
    """Raised when cache operations fail."""

    pass


class ValidationError(RBADataError):
    """
    Raised when input validation fails.

    Provides clear information about:
    - What parameter failed validation
    - What was expected
    - How to fix it
    """

    def __init__(self, param_name: str, value, expected: str):
        """
        Initialize validation error.

        Parameters
        ----------
        param_name : str
            Name of the parameter that failed validation
        value : any
            The invalid value
        expected : str
            Description of what was expected
        """
        message = f"Invalid {param_name}: '{value}'. Expected: {expected}"
        super().__init__(message, context={"param": param_name, "value": value})
