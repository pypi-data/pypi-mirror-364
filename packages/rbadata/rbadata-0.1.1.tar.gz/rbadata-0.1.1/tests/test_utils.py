"""
Tests for the utils module
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import requests
from rbadata.utils import (
    get_pandas_freq_alias,
    get_rba_urls,
    check_rba_connection,
    tables_from_seriesid,
    parse_date_string,
    is_rba_ts_format,
    _is_potential_date
)
from rbadata.exceptions import RBADataError


class TestGetRBAUrls:
    """Test the get_rba_urls function."""
    
    @patch('rbadata.utils.get_table_list')
    def test_get_rba_urls_success(self, mock_get_table_list):
        """Test successful URL retrieval."""
        # Mock table list
        mock_table_list = pd.DataFrame({
            'no': ['G1', 'A1', 'F1'],
            'url': [
                'https://www.rba.gov.au/statistics/tables/xls/g01.xls',
                'https://www.rba.gov.au/statistics/tables/xls/a01.xls',
                'https://www.rba.gov.au/statistics/tables/xls/f01.xls'
            ],
            'current_or_historical': ['current', 'current', 'current']
        })
        mock_get_table_list.return_value = mock_table_list
        
        # Test single table
        urls = get_rba_urls(['G1'], 'current')
        assert urls == ['https://www.rba.gov.au/statistics/tables/xls/g01.xls']
        
        # Test multiple tables
        urls = get_rba_urls(['G1', 'A1'], 'current')
        assert len(urls) == 2
    
    @patch('rbadata.utils.get_table_list')
    def test_get_rba_urls_not_found(self, mock_get_table_list):
        """Test error when table not found."""
        mock_table_list = pd.DataFrame({
            'no': ['G1'],
            'url': ['https://example.com'],
            'current_or_historical': ['current']
        })
        mock_get_table_list.return_value = mock_table_list
        
        with pytest.raises(RBADataError, match="Table 'XYZ' not found"):
            get_rba_urls(['XYZ'], 'current')
    
    @patch('rbadata.utils.get_table_list')
    def test_get_rba_urls_historical(self, mock_get_table_list):
        """Test getting historical URLs."""
        mock_table_list = pd.DataFrame({
            'no': ['A1', 'A1'],
            'url': ['https://current.com', 'https://historical.com'],
            'current_or_historical': ['current', 'historical']
        })
        mock_get_table_list.return_value = mock_table_list
        
        urls = get_rba_urls(['A1'], 'historical')
        assert urls == ['https://historical.com']


class TestCheckRBAConnection:
    """Test the check_rba_connection function."""
    
    @patch('requests.head')
    def test_connection_success(self, mock_head):
        """Test successful connection."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response
        
        # Should not raise
        check_rba_connection()
        mock_head.assert_called_once()
    
    @patch('requests.head')
    def test_connection_failure_status(self, mock_head):
        """Test connection failure with bad status."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_head.return_value = mock_response
        
        with pytest.raises(RBADataError, match="Cannot connect to RBA website"):
            check_rba_connection()
    
    @patch('requests.head')
    def test_connection_failure_exception(self, mock_head):
        """Test connection failure with exception."""
        mock_head.side_effect = requests.RequestException("Network error")
        
        with pytest.raises(RBADataError, match="No internet connection"):
            check_rba_connection()


class TestTablesFromSeriesId:
    """Test the tables_from_seriesid function."""
    
    @patch('rbadata.utils.get_series_list')
    def test_tables_from_seriesid_success(self, mock_get_series_list):
        """Test successful series to table mapping."""
        mock_series_list = pd.DataFrame({
            'series_id': ['GCPIAG', 'GLFSURSA', 'GCPITC'],
            'table_no': ['G1', 'H3', 'G1']
        })
        mock_get_series_list.return_value = mock_series_list
        
        # Single series
        result = tables_from_seriesid(['GCPIAG'])
        assert result == {'G1': ['GCPIAG']}
        
        # Multiple series, same table
        result = tables_from_seriesid(['GCPIAG', 'GCPITC'])
        assert result == {'G1': ['GCPIAG', 'GCPITC']}
        
        # Multiple series, different tables
        result = tables_from_seriesid(['GCPIAG', 'GLFSURSA'])
        assert result == {'G1': ['GCPIAG'], 'H3': ['GLFSURSA']}
    
    @patch('rbadata.utils.get_series_list')
    def test_tables_from_seriesid_not_found(self, mock_get_series_list):
        """Test error when series not found."""
        mock_series_list = pd.DataFrame({
            'series_id': ['GCPIAG'],
            'table_no': ['G1']
        })
        mock_get_series_list.return_value = mock_series_list
        
        with pytest.raises(RBADataError, match="Series ID 'INVALID' not found"):
            tables_from_seriesid(['INVALID'])


class TestParseDateString:
    """Test the parse_date_string function."""
    
    def test_parse_standard_formats(self):
        """Test parsing standard date formats."""
        # Test various formats
        assert parse_date_string('01-Jan-2020') == datetime(2020, 1, 1)
        assert parse_date_string('01 January 2020') == datetime(2020, 1, 1)
        assert parse_date_string('Jan-2020') == datetime(2020, 1, 1)
        assert parse_date_string('January 2020') == datetime(2020, 1, 1)
        assert parse_date_string('2020-01-01') == datetime(2020, 1, 1)
        assert parse_date_string('01/01/2020') == datetime(2020, 1, 1)
    
    def test_parse_with_pandas(self):
        """Test fallback to pandas parser."""
        # Should use pandas parser for non-standard formats
        result = parse_date_string('2020-Q1')
        assert result is not None
        assert result.year == 2020
    
    def test_parse_invalid(self):
        """Test parsing invalid date string."""
        assert parse_date_string('not a date') is None
        # Empty string may return NaT from pandas
        result = parse_date_string('')
        assert result is None or pd.isna(result)


class TestIsRBATsFormat:
    """Test the is_rba_ts_format function."""
    
    def test_valid_ts_format(self):
        """Test with valid time series format."""
        df = pd.DataFrame({
            'Date': pd.date_range('2020-01-01', periods=10, freq=get_pandas_freq_alias("M")),
            'Series1': np.random.rand(10),
            'Series2': np.random.rand(10)
        })
        
        assert is_rba_ts_format(df) is True
    
    def test_valid_ts_format_string_dates(self):
        """Test with string dates."""
        df = pd.DataFrame({
            'Date': ['Jan-2020', 'Feb-2020', 'Mar-2020', 'Apr-2020', 'May-2020'],
            'Value': [100, 101, 102, 103, 104]
        })
        
        assert is_rba_ts_format(df) is True
    
    def test_invalid_ts_format_empty(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        assert is_rba_ts_format(df) is False
    
    def test_invalid_ts_format_no_dates(self):
        """Test with no date-like values."""
        df = pd.DataFrame({
            'Col1': ['A', 'B', 'C', 'D'],
            'Col2': [1, 2, 3, 4]
        })
        
        assert is_rba_ts_format(df) is False
    
    def test_invalid_ts_format_single_column(self):
        """Test with single column."""
        df = pd.DataFrame({'Col1': [1, 2, 3]})
        assert is_rba_ts_format(df) is False


class TestIsPotentialDate:
    """Test the _is_potential_date function."""
    
    def test_datetime_objects(self):
        """Test with datetime objects."""
        assert _is_potential_date(datetime(2020, 1, 1)) is True
        assert _is_potential_date(pd.Timestamp('2020-01-01')) is True
    
    def test_year_patterns(self):
        """Test with year patterns."""
        assert _is_potential_date('2020') is True
        assert _is_potential_date('1999') is True
        assert _is_potential_date('2020-01-01') is True
    
    def test_month_patterns(self):
        """Test with month names."""
        assert _is_potential_date('January') is True
        assert _is_potential_date('Jan-2020') is True
        assert _is_potential_date('2020-Jan') is True
        assert _is_potential_date('December 2020') is True
    
    def test_quarter_patterns(self):
        """Test with quarter patterns."""
        assert _is_potential_date('Q1') is True
        assert _is_potential_date('Q4 2020') is True
        assert _is_potential_date('2020-Q2') is True
    
    def test_non_dates(self):
        """Test with non-date values."""
        assert _is_potential_date('Hello') is False
        assert _is_potential_date('123') is False
        assert _is_potential_date(None) is False
        assert _is_potential_date(np.nan) is False
        assert _is_potential_date('') is False