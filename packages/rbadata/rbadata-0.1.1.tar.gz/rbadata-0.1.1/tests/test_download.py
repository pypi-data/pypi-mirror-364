"""
Tests for the download module
"""

import pytest
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch, MagicMock, mock_open
import requests
from rbadata.download import download_rba, _download_file, url_exists
from rbadata.exceptions import RBADataError


class TestDownloadRBA:
    """Test the download_rba function."""
    
    @patch('rbadata.download._download_file')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_success(self, mock_file, mock_download):
        """Test successful file download."""
        # Setup mocks
        mock_response = Mock()
        mock_response.content = b'Excel file content'
        mock_download.return_value = mock_response
        
        # Call function
        result = download_rba('https://example.com/table.xlsx', 'G1')
        
        # Verify
        assert isinstance(result, Path)
        assert 'rba_table_G1.xlsx' in str(result)
        mock_download.assert_called_once_with('https://example.com/table.xlsx')
        mock_file().write.assert_called_once_with(b'Excel file content')
    
    @patch('rbadata.download._download_file')
    @patch('rbadata.download.time.sleep')
    def test_download_with_retry(self, mock_sleep, mock_download):
        """Test download with retry on failure."""
        # First two attempts fail, third succeeds
        mock_response = Mock()
        mock_response.content = b'Excel content'
        mock_download.side_effect = [
            Exception("Network error"),
            Exception("Timeout"),
            mock_response
        ]
        
        with patch('builtins.open', mock_open()):
            result = download_rba('https://example.com/table.xlsx', 'G1')
        
        # Verify retries
        assert mock_download.call_count == 3
        assert mock_sleep.call_count == 2  # Sleep between retries
        assert isinstance(result, Path)
    
    @patch('rbadata.download._download_file')
    @patch('rbadata.download.time.sleep')
    def test_download_failure_after_retries(self, mock_sleep, mock_download):
        """Test download failure after all retries."""
        # All attempts fail
        mock_download.side_effect = Exception("Network error")
        
        with pytest.raises(RBADataError, match="Failed to download file after 3 attempts"):
            download_rba('https://example.com/table.xlsx', 'G1')
        
        assert mock_download.call_count == 3
        assert mock_sleep.call_count == 2
    
    @patch('rbadata.download._download_file')
    def test_download_creates_directory(self, mock_download):
        """Test that download creates temp directory if needed."""
        mock_response = Mock()
        mock_response.content = b'content'
        mock_download.return_value = mock_response
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            with patch('builtins.open', mock_open()):
                download_rba('https://example.com/table.xlsx', 'G1')
            
            mock_mkdir.assert_called_once_with(exist_ok=True)


class TestDownloadFile:
    """Test the _download_file function."""
    
    @patch('requests.get')
    @patch('rbadata.download.get_headers')
    def test_download_file_success(self, mock_get_headers, mock_get):
        """Test successful file download."""
        # Setup mocks
        mock_headers = {'User-Agent': 'rbadata'}
        mock_get_headers.return_value = mock_headers
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'File content'
        mock_get.return_value = mock_response
        
        # Call function
        result = _download_file('https://example.com/file.xlsx')
        
        # Verify
        assert result == mock_response
        mock_get.assert_called_once_with(
            'https://example.com/file.xlsx',
            headers=mock_headers,
            timeout=30
        )
    
    @patch('requests.get')
    @patch('rbadata.download.get_headers')
    def test_download_file_http_error(self, mock_get_headers, mock_get):
        """Test HTTP error handling."""
        mock_get_headers.return_value = {}
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("Not found")
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.HTTPError):
            _download_file('https://example.com/missing.xlsx')
    
    @patch('requests.get')
    @patch('rbadata.download.get_headers')
    @patch('rbadata.download.get_download_method')
    def test_download_file_with_custom_method(self, mock_get_method, mock_get_headers, mock_get):
        """Test download with custom method (wininet)."""
        mock_get_method.return_value = 'wininet'
        mock_get_headers.return_value = {}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = _download_file('https://example.com/file.xlsx')
        
        # Verify custom method was checked
        mock_get_method.assert_called_once()
        assert result == mock_response


class TestUrlExists:
    """Test the url_exists function."""
    
    @patch('requests.head')
    def test_url_exists_true(self, mock_head):
        """Test when URL exists."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response
        
        assert url_exists('https://example.com/file.xlsx') is True
        mock_head.assert_called_once_with(
            'https://example.com/file.xlsx',
            timeout=5,
            allow_redirects=True
        )
    
    @patch('requests.head')
    def test_url_exists_false_404(self, mock_head):
        """Test when URL returns 404."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_head.return_value = mock_response
        
        assert url_exists('https://example.com/missing.xlsx') is False
    
    @patch('requests.head')
    def test_url_exists_false_exception(self, mock_head):
        """Test when request raises exception."""
        mock_head.side_effect = requests.RequestException("Network error")
        
        assert url_exists('https://example.com/error.xlsx') is False
    
    @patch('requests.head')
    def test_url_exists_redirect(self, mock_head):
        """Test URL with redirect."""
        mock_response = Mock()
        mock_response.status_code = 200  # After redirect
        mock_head.return_value = mock_response
        
        assert url_exists('https://example.com/redirect.xlsx') is True