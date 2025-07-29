"""
Tests for core functionality
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from rbadata import read_rba, read_rba_seriesid
from rbadata.utils import get_pandas_freq_alias
from rbadata.exceptions import RBADataError


class TestReadRBA:
    """Test the main read_rba function."""
    
    def test_read_rba_requires_input(self):
        """Test that read_rba requires either table_no or series_id."""
        with pytest.raises(RBADataError, match="Either 'table_no' or 'series_id' must be specified"):
            read_rba()
    
    def test_read_rba_not_both_inputs(self):
        """Test that read_rba doesn't accept both table_no and series_id."""
        with pytest.raises(RBADataError, match="Only one of 'table_no' or 'series_id' should be specified"):
            read_rba(table_no="g1", series_id="GCPIAG")
    
    @patch('rbadata.core.check_rba_connection')
    @patch('rbadata.core.get_rba_urls')
    @patch('rbadata.core.download_rba')
    @patch('rbadata.core.tidy_rba')
    def test_read_rba_single_table(self, mock_tidy, mock_download, mock_urls, mock_check):
        """Test reading a single table."""
        # Setup mocks
        mock_check.return_value = None
        mock_urls.return_value = ["https://example.com/g1.xlsx"]
        mock_download.return_value = "/tmp/g1.xlsx"
        
        # Create sample tidy data
        sample_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=3, freq=get_pandas_freq_alias("Q")),
            'series': ['CPI'] * 3,
            'series_id': ['GCPIAG'] * 3,
            'value': [100.0, 101.0, 102.0]
        })
        mock_tidy.return_value = sample_data
        
        # Call function
        result = read_rba(table_no="g1")
        
        # Verify calls
        mock_check.assert_called_once()
        mock_urls.assert_called_once_with(["g1"], "current")
        mock_download.assert_called_once_with("https://example.com/g1.xlsx", "g1")
        mock_tidy.assert_called_once()
        
        # Check result
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ['date', 'series', 'series_id', 'value']
    
    @patch('rbadata.core.check_rba_connection')
    @patch('rbadata.core.tables_from_seriesid')
    @patch('rbadata.core.get_rba_urls')
    @patch('rbadata.core.download_rba')
    @patch('rbadata.core.tidy_rba')
    def test_read_rba_by_series_id(self, mock_tidy, mock_download, mock_urls, mock_tables, mock_check):
        """Test reading data by series ID."""
        # Setup mocks
        mock_check.return_value = None
        mock_tables.return_value = {"G1": ["GCPIAG"]}
        mock_urls.return_value = ["https://example.com/g1.xlsx"]
        mock_download.return_value = "/tmp/g1.xlsx"
        
        # Create sample data with multiple series
        sample_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=6, freq=get_pandas_freq_alias("Q")),
            'series': ['CPI'] * 3 + ['Other'] * 3,
            'series_id': ['GCPIAG'] * 3 + ['OTHER'] * 3,
            'value': [100.0, 101.0, 102.0, 200.0, 201.0, 202.0]
        })
        mock_tidy.return_value = sample_data
        
        # Call function
        result = read_rba(series_id="GCPIAG")
        
        # Verify it filtered to just the requested series
        assert len(result) == 3
        assert result['series_id'].unique()[0] == 'GCPIAG'


class TestReadRBASeriesID:
    """Test the convenience function read_rba_seriesid."""
    
    @patch('rbadata.core.read_rba')
    def test_read_rba_seriesid(self, mock_read_rba):
        """Test that read_rba_seriesid calls read_rba correctly."""
        # Setup mock
        mock_read_rba.return_value = pd.DataFrame({'data': [1, 2, 3]})
        
        # Call function
        result = read_rba_seriesid("GCPIAG")
        
        # Verify
        mock_read_rba.assert_called_once_with(series_id="GCPIAG")
        assert isinstance(result, pd.DataFrame)