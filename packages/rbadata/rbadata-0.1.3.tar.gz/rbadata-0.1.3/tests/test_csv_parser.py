"""
Tests for CSV parser functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import requests

from rbadata.csv_parser import (
    download_rba_csv,
    parse_rba_csv,
    fetch_multiple_series_csv,
    _parse_rba_date,
    _extract_series_ids,
    _find_series_id_row,
)
from rbadata.exceptions import DownloadError, DataError, SeriesNotFoundError


class TestDownloadRBACSV:
    """Test CSV download functionality."""
    
    @patch('rbadata.csv_parser.requests.get')
    @patch('rbadata.csv_parser.get_cache')
    def test_download_csv_success(self, mock_cache, mock_get):
        """Test successful CSV download."""
        # Setup
        mock_cache.return_value.get_csv.return_value = None
        mock_response = Mock()
        mock_response.text = "Series ID,TEST1,TEST2\nDescription,Test 1,Test 2\n01-Jan-2023,1.5,2.5"
        mock_response.encoding = 'windows-1252'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Execute
        result = download_rba_csv('F1')
        
        # Assert
        assert "Series ID,TEST1,TEST2" in result
        assert mock_get.called
        assert mock_cache.return_value.set_csv.called
        
    @patch('rbadata.csv_parser.requests.get')
    def test_download_csv_http_error(self, mock_get):
        """Test CSV download with HTTP error."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 404
        
        # Create HTTPError with response attribute
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        
        mock_get.return_value = mock_response
        
        # Execute & Assert
        with pytest.raises(DownloadError) as exc_info:
            download_rba_csv('INVALID')
            
        assert "404" in str(exc_info.value)
        assert "may not exist" in str(exc_info.value)
        
    @patch('rbadata.csv_parser.requests.get')
    def test_download_csv_timeout(self, mock_get):
        """Test CSV download with timeout."""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(DownloadError) as exc_info:
            download_rba_csv('F1')
            
        assert "Timeout" in str(exc_info.value)
        assert "30 seconds" in str(exc_info.value)
        
    @patch('rbadata.csv_parser.get_cache')
    def test_download_csv_from_cache(self, mock_cache):
        """Test CSV retrieval from cache."""
        cached_content = "cached,data\n1,2"
        mock_cache.return_value.get_csv.return_value = cached_content
        
        result = download_rba_csv('F1')
        
        assert result == cached_content
        assert mock_cache.return_value.get_csv.called


class TestParseRBACSV:
    """Test CSV parsing functionality."""
    
    def test_parse_csv_basic(self):
        """Test basic CSV parsing."""
        csv_content = """
Title,Test Table
Description,Series 1,Series 2
Units,Percent,$ million
Series ID,TEST1,TEST2
01-Jan-2023,1.5,1000
02-Jan-2023,1.6,1100
"""
        
        df = parse_rba_csv(csv_content, 'TEST')
        
        assert len(df) == 4  # 2 dates × 2 series
        assert 'date' in df.columns
        assert 'series_id' in df.columns
        assert 'value' in df.columns
        assert 'description' in df.columns
        assert 'units' in df.columns
        
        # Check specific values
        test1_data = df[df['series_id'] == 'TEST1']
        assert test1_data['description'].iloc[0] == 'Series 1'
        assert test1_data['units'].iloc[0] == 'Percent'
        assert test1_data['value'].iloc[0] == 1.5
        
    def test_parse_csv_with_series_filter(self):
        """Test CSV parsing with series filter."""
        csv_content = """
Series ID,TEST1,TEST2,TEST3
01-Jan-2023,1.5,2.5,3.5
"""
        
        df = parse_rba_csv(csv_content, 'TEST', series_filter=['TEST1', 'TEST3'])
        
        assert len(df) == 2
        assert set(df['series_id'].unique()) == {'TEST1', 'TEST3'}
        
    def test_parse_csv_with_date_filter(self):
        """Test CSV parsing with date filtering."""
        csv_content = """
Series ID,TEST1
01-Jan-2023,1.0
01-Feb-2023,2.0
01-Mar-2023,3.0
01-Apr-2023,4.0
"""
        
        df = parse_rba_csv(
            csv_content, 
            'TEST',
            start_date='2023-02-01',
            end_date='2023-03-31'
        )
        
        assert len(df) == 2
        assert df['date'].min() >= pd.Timestamp('2023-02-01')
        assert df['date'].max() <= pd.Timestamp('2023-03-31')
        
    def test_parse_csv_missing_series(self):
        """Test parsing with missing series raises appropriate error."""
        csv_content = """
Series ID,TEST1,TEST2
01-Jan-2023,1.5,2.5
"""
        
        with pytest.raises(SeriesNotFoundError) as exc_info:
            parse_rba_csv(csv_content, 'TEST', series_filter=['TEST3', 'TEST4'])
            
        assert 'TEST3' in str(exc_info.value)
        assert 'TEST4' in str(exc_info.value)
        
    def test_parse_csv_no_header(self):
        """Test parsing CSV without Series ID header."""
        csv_content = """
Some random content
Without proper headers
"""
        
        with pytest.raises(DataError) as exc_info:
            parse_rba_csv(csv_content, 'TEST')
            
        assert "Could not find Series ID header" in str(exc_info.value)
        
    def test_parse_csv_with_na_values(self):
        """Test parsing CSV with 'na' values."""
        csv_content = """
Series ID,TEST1,TEST2
01-Jan-2023,1.5,na
02-Jan-2023,na,2.5
03-Jan-2023,1.7,2.7
"""
        
        df = parse_rba_csv(csv_content, 'TEST')
        
        # Should have 4 values (2 na values excluded)
        assert len(df) == 4
        assert df[df['series_id'] == 'TEST1']['value'].notna().all()
        assert df[df['series_id'] == 'TEST2']['value'].notna().all()


class TestDateParsing:
    """Test RBA date format parsing."""
    
    def test_parse_daily_date(self):
        """Test parsing daily date format."""
        date = _parse_rba_date('01-Jan-2023')
        assert date == pd.Timestamp('2023-01-01')
        
    def test_parse_monthly_date(self):
        """Test parsing monthly date format."""
        date = _parse_rba_date('Jan-2023')
        assert date == pd.Timestamp('2023-01-01')
        
    def test_parse_quarterly_date(self):
        """Test parsing quarterly date format."""
        # Q1
        date = _parse_rba_date('Q1 2023')
        assert date == pd.Timestamp('2023-01-01')
        
        # Q2
        date = _parse_rba_date('Q2 2023')
        assert date == pd.Timestamp('2023-04-01')
        
        # Q3
        date = _parse_rba_date('Q3 2023')
        assert date == pd.Timestamp('2023-07-01')
        
        # Q4
        date = _parse_rba_date('Q4 2023')
        assert date == pd.Timestamp('2023-10-01')
        
    def test_parse_annual_date(self):
        """Test parsing annual date format."""
        date = _parse_rba_date('2023')
        assert date == pd.Timestamp('2023-01-01')
        
    def test_parse_invalid_date(self):
        """Test parsing invalid date returns NaT."""
        date = _parse_rba_date('invalid-date')
        assert pd.isna(date)


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_find_series_id_row(self):
        """Test finding Series ID row."""
        lines = [
            "Title,Some Title",
            "Description,Desc 1,Desc 2",
            "Series ID,TEST1,TEST2",
            "01-Jan-2023,1.5,2.5"
        ]
        
        idx = _find_series_id_row(lines)
        assert idx == 2
        
    def test_find_series_id_row_not_found(self):
        """Test when Series ID row not found."""
        lines = ["No series", "ID here"]
        
        idx = _find_series_id_row(lines)
        assert idx is None
        
    def test_extract_series_ids(self):
        """Test extracting series IDs from header."""
        header = "Series ID,TEST1,TEST2,TEST3"
        series_ids = _extract_series_ids(header)
        
        assert series_ids == ['TEST1', 'TEST2', 'TEST3']
        
    def test_extract_series_ids_with_quotes(self):
        """Test extracting series IDs with quotes."""
        header = 'Series ID,"TEST1","TEST2","TEST3"'
        series_ids = _extract_series_ids(header)
        
        assert series_ids == ['TEST1', 'TEST2', 'TEST3']


class TestFetchMultipleSeriesCSV:
    """Test fetching multiple series efficiently."""
    
    @patch('rbadata.csv_parser.download_rba_csv')  
    @patch('rbadata.utils.tables_from_seriesid')
    def test_fetch_multiple_series(self, mock_tables, mock_download):
        """Test fetching multiple series from different tables."""
        # Setup
        mock_tables.return_value = {
            'F1': {'FIRMMCRTD', 'FCMYGBAG10'},
            'G1': {'GCPIAG'}
        }
        
        # Mock CSV content for each table
        f1_csv = """
Series ID,FIRMMCRTD,FCMYGBAG10,OTHER
01-Jan-2023,5.0,3.5,1.0
"""
        
        g1_csv = """
Series ID,GCPIAG,OTHER2
01-Jan-2023,130.0,100.0
"""
        
        mock_download.side_effect = [f1_csv, g1_csv]
        
        # Execute
        series_ids = ['FIRMMCRTD', 'FCMYGBAG10', 'GCPIAG']
        df = fetch_multiple_series_csv(series_ids)
        
        # Assert
        assert len(df) == 3  # 3 series requested
        assert set(df['series_id'].unique()) == set(series_ids)
        assert mock_download.call_count == 2  # 2 tables
        
    @patch('rbadata.csv_parser.download_rba_csv')
    @patch('rbadata.utils.tables_from_seriesid')
    def test_fetch_multiple_series_with_error(self, mock_tables, mock_download):
        """Test fetching multiple series with one table failing."""
        # Setup
        mock_tables.return_value = {
            'F1': {'TEST1'},
            'F2': {'TEST2'}
        }
        
        # First table succeeds, second fails
        mock_download.side_effect = [
            "Series ID,TEST1\n01-Jan-2023,1.0",
            DownloadError("Failed to download F2")
        ]
        
        # Execute
        df = fetch_multiple_series_csv(['TEST1', 'TEST2'])
        
        # Should still return data from successful table
        assert len(df) == 1
        assert df['series_id'].iloc[0] == 'TEST1'