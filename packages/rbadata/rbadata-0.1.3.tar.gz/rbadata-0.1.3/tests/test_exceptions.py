"""
Tests for enhanced exception handling.
"""

import pytest

from rbadata.exceptions import (
    RBADataError,
    DownloadError,
    DataError,
    ConnectionError,
    SeriesNotFoundError,
    CacheError,
    ValidationError,
)


class TestRBADataError:
    """Test base exception class."""
    
    def test_basic_error(self):
        """Test basic error without context."""
        error = RBADataError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.context == {}
        
    def test_error_with_context(self):
        """Test error with context information."""
        context = {'table_no': 'F1', 'series_id': 'TEST1'}
        error = RBADataError("Failed to fetch data", context)
        
        assert "Failed to fetch data" in str(error)
        assert "Context: table_no=F1, series_id=TEST1" in str(error)
        assert error.context == context


class TestDownloadError:
    """Test download error handling."""
    
    def test_download_error_404(self):
        """Test 404 error message."""
        error = DownloadError(
            "Download failed",
            url="https://example.com/data.csv",
            status_code=404
        )
        
        assert "Download failed" in str(error)
        assert "may not exist" in str(error)
        assert error.context['url'] == "https://example.com/data.csv"
        assert error.context['status_code'] == 404
        
    def test_download_error_403(self):
        """Test 403 error message."""
        error = DownloadError("Access denied", status_code=403)
        
        assert "Access denied" in str(error)
        assert "check if RBA website is accessible" in str(error)
        
    def test_download_error_500(self):
        """Test 500 error message."""
        error = DownloadError("Server error", status_code=500)
        
        assert "Server error" in str(error)
        assert "try again later" in str(error)
        
    def test_download_error_generic_http(self):
        """Test generic HTTP error."""
        error = DownloadError("HTTP error", status_code=418)
        
        assert "HTTP error" in str(error)
        assert "HTTP error 418" in str(error)
        
    def test_download_error_no_status(self):
        """Test download error without status code."""
        error = DownloadError("Network timeout", url="https://example.com")
        
        assert "Network timeout" in str(error)
        assert error.context['url'] == "https://example.com"
        assert 'status_code' not in error.context


class TestDataError:
    """Test data parsing error."""
    
    def test_data_error_with_table(self):
        """Test data error with table information."""
        error = DataError(
            "Invalid data format",
            table_no='F1'
        )
        
        assert "Invalid data format" in str(error)
        assert error.context['table_no'] == 'F1'
        
    def test_data_error_with_series(self):
        """Test data error with series information."""
        error = DataError(
            "Cannot parse series",
            series_id='TEST1'
        )
        
        assert "Cannot parse series" in str(error)
        assert error.context['series_id'] == 'TEST1'
        
    def test_data_error_with_both(self):
        """Test data error with both table and series."""
        error = DataError(
            "Parse error",
            table_no='F1',
            series_id='TEST1'
        )
        
        assert error.context['table_no'] == 'F1'
        assert error.context['series_id'] == 'TEST1'


class TestConnectionError:
    """Test connection error."""
    
    def test_default_connection_error(self):
        """Test default connection error message."""
        error = ConnectionError()
        
        assert "Cannot connect to RBA website" in str(error)
        assert "Check your internet connection" in str(error)
        assert "Verify https://www.rba.gov.au is accessible" in str(error)
        assert "corporate proxy" in str(error)
        assert "custom headers" in str(error)
        
    def test_custom_connection_error(self):
        """Test custom connection error message."""
        error = ConnectionError(
            "DNS resolution failed",
            context={'dns_server': '8.8.8.8'}
        )
        
        assert "DNS resolution failed" in str(error)
        assert "Suggestions:" in str(error)
        assert error.context['dns_server'] == '8.8.8.8'


class TestSeriesNotFoundError:
    """Test series not found error."""
    
    def test_basic_series_not_found(self):
        """Test basic series not found."""
        error = SeriesNotFoundError(['TEST1', 'TEST2'])
        
        assert "Series not found: TEST1, TEST2" in str(error)
        
    def test_series_not_found_with_table(self):
        """Test series not found with table."""
        error = SeriesNotFoundError(
            ['TEST1'],
            table_no='F1'
        )
        
        assert "Series not found: TEST1 in table F1" in str(error)
        
    def test_series_not_found_with_suggestions(self):
        """Test series not found with similar series suggestions."""
        error = SeriesNotFoundError(
            ['TES1', 'TES2'],
            table_no='F1',
            available_series=['TEST1', 'TEST2', 'OTHER']
        )
        
        assert "Series not found: TES1, TES2" in str(error)
        assert "Did you mean:" in str(error)
        assert "TES1 -> TEST1, TEST2" in str(error)
        assert "TES2 -> TEST1, TEST2" in str(error)
        
    def test_series_not_found_no_suggestions(self):
        """Test series not found without matching suggestions."""
        error = SeriesNotFoundError(
            ['XYZ'],
            available_series=['TEST1', 'TEST2']
        )
        
        assert "Series not found: XYZ" in str(error)
        assert "Did you mean:" not in str(error)


class TestCacheError:
    """Test cache error."""
    
    def test_cache_error(self):
        """Test basic cache error."""
        error = CacheError("Cache write failed")
        assert str(error) == "Cache write failed"
        
    def test_cache_error_with_context(self):
        """Test cache error with context."""
        error = CacheError(
            "Disk full",
            context={'cache_dir': '/tmp/cache', 'size': '1GB'}
        )
        
        assert "Disk full" in str(error)
        assert "cache_dir=/tmp/cache" in str(error)


class TestValidationError:
    """Test validation error."""
    
    def test_validation_error(self):
        """Test validation error message."""
        error = ValidationError(
            'start_date',
            '2023-13-01',
            'valid date format (YYYY-MM-DD)'
        )
        
        assert "Invalid start_date: '2023-13-01'" in str(error)
        assert "Expected: valid date format (YYYY-MM-DD)" in str(error)
        assert error.context['param'] == 'start_date'
        assert error.context['value'] == '2023-13-01'
        
    def test_validation_error_types(self):
        """Test validation error with different value types."""
        # String value
        error1 = ValidationError('table_no', 'invalid!', 'alphanumeric table number')
        assert "'invalid!'" in str(error1)
        
        # Numeric value
        error2 = ValidationError('max_retries', -1, 'positive integer')
        assert "'-1'" in str(error2)
        
        # None value
        error3 = ValidationError('series_id', None, 'non-empty series ID')
        assert "'None'" in str(error3)


class TestExceptionHierarchy:
    """Test exception inheritance hierarchy."""
    
    def test_inheritance(self):
        """Test all exceptions inherit from RBADataError."""
        # Create instances
        errors = [
            DownloadError("test"),
            DataError("test"),
            ConnectionError("test"),
            SeriesNotFoundError([]),
            CacheError("test"),
            ValidationError("param", "value", "expected")
        ]
        
        # All should be instances of RBADataError
        for error in errors:
            assert isinstance(error, RBADataError)
            assert isinstance(error, Exception)
            
    def test_specific_inheritance(self):
        """Test specific inheritance relationships."""
        # SeriesNotFoundError inherits from DataError
        error = SeriesNotFoundError(['TEST'])
        assert isinstance(error, DataError)
        assert isinstance(error, RBADataError)