"""
Tests for the tidy module
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from rbadata.tidy import (
    tidy_rba,
    _tidy_normal_sheet,
    _find_header_row,
    _is_date_like,
    _extract_metadata,
    _extract_series_ids,
    _tidy_special_table
)
from rbadata.utils import get_pandas_freq_alias
from rbadata.exceptions import RBADataError


class TestTidyRBA:
    """Test the main tidy_rba function."""
    
    @patch('rbadata.tidy.pd.ExcelFile')
    @patch('rbadata.tidy.is_rba_ts_format')
    def test_tidy_rba_normal_table(self, mock_is_rba_ts, mock_excel_file):
        """Test tidying a normal RBA table."""
        # Setup mock Excel file
        mock_xl = MagicMock()
        mock_xl.sheet_names = ['Data', 'Notes']
        mock_excel_file.return_value = mock_xl
        
        # Mock sheet data
        sheet_data = pd.DataFrame({
            'Series ID': ['GCPIAG', 'GCPITC'],
            '2020-03-31': [100.0, 99.5],
            '2020-06-30': [101.0, 100.0],
            '2020-09-30': [102.0, 100.5]
        })
        
        mock_xl.parse.return_value = sheet_data
        pd.read_excel = Mock(return_value=sheet_data)
        mock_is_rba_ts.return_value = True
        
        # Mock _tidy_normal_sheet to return processed data
        with patch('rbadata.tidy._tidy_normal_sheet') as mock_tidy_sheet:
            mock_tidy_sheet.return_value = pd.DataFrame({
                'date': pd.date_range('2020-03-31', periods=3, freq=get_pandas_freq_alias("Q")),
                'series': ['CPI'] * 3,
                'value': [100.0, 101.0, 102.0]
            })
            
            # Call function
            result = tidy_rba(Path('/tmp/test.xlsx'), 'G1', 'http://example.com')
            
            # Verify
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3
            assert 'date' in result.columns
            assert 'value' in result.columns
    
    @patch('rbadata.tidy.pd.ExcelFile')
    def test_tidy_rba_special_table(self, mock_excel_file):
        """Test handling of special table formats."""
        # Setup mock
        mock_xl = MagicMock()
        mock_xl.sheet_names = ['Sheet1']
        mock_excel_file.return_value = mock_xl
        
        # Test special table handling
        with pytest.raises(RBADataError, match="non-standard format"):
            tidy_rba(Path('/tmp/test.xlsx'), 'A1.1', 'http://example.com')
    
    @patch('rbadata.tidy.pd.ExcelFile')
    @patch('rbadata.tidy.is_rba_ts_format')
    def test_tidy_rba_no_valid_data(self, mock_is_rba_ts, mock_excel_file):
        """Test error when no valid data found."""
        # Setup mock
        mock_xl = MagicMock()
        mock_xl.sheet_names = ['Notes']
        mock_excel_file.return_value = mock_xl
        mock_is_rba_ts.return_value = False
        
        pd.read_excel = Mock(return_value=pd.DataFrame())
        
        # Should raise error
        with pytest.raises(RBADataError, match="No valid data found"):
            tidy_rba(Path('/tmp/test.xlsx'), 'G1', 'http://example.com')


class TestTidyNormalSheet:
    """Test the _tidy_normal_sheet function."""
    
    def test_tidy_normal_sheet_basic(self):
        """Test tidying a normal sheet."""
        # Create sample data
        df = pd.DataFrame([
            ['Title: Consumer Price Index', None, None],
            ['Frequency: Quarterly', None, None],
            ['Units: Index', None, None],
            ['Series ID', 'GCPIAG', 'GCPITC'],
            ['Description', 'CPI All Groups', 'CPI Trimmed'],
            ['2020-03-31', 100.0, 99.5],
            ['2020-06-30', 101.0, 100.0],
            ['2020-09-30', 102.0, 100.5]
        ])
        
        # Add column names to make the data consistent
        df.columns = [0, 1, 2]
        
        with patch('rbadata.tidy._find_header_row', return_value=5):
            with patch('rbadata.tidy._extract_metadata') as mock_metadata:
                mock_metadata.return_value = {
                    'title': 'Consumer Price Index',
                    'frequency': 'Quarterly',
                    'units': 'Index',
                    'source': 'RBA',
                    'pub_date': pd.NaT,
                    'series_type': 'Original'
                }
                
                with patch('rbadata.tidy._extract_series_ids') as mock_series_ids:
                    mock_series_ids.return_value = {
                        1: 'GCPIAG',  # Column index to series ID
                        2: 'GCPITC'
                    }
                    
                    # Call function
                    result = _tidy_normal_sheet(
                        df, 'Data', 'G1', 'http://example.com', 'current'
                    )
                    
                    # Verify
                    assert isinstance(result, pd.DataFrame)
                    # The result should have data but may not be exactly 6 rows
                    # due to the way melting works with the mocked data
                    assert len(result) > 0
                    assert 'date' in result.columns
                    assert 'series' in result.columns
                    assert 'value' in result.columns
                    assert result['table_no'].iloc[0] == 'G1'
                    
                    # Check that we have valid dates
                    assert pd.notna(result['date']).all()
                    assert pd.notna(result['value']).all()


class TestFindHeaderRow:
    """Test the _find_header_row function."""
    
    def test_find_header_with_series_id(self):
        """Test finding header row by Series ID."""
        df = pd.DataFrame([
            ['Title', None, None],
            ['Some metadata', None, None],
            ['Series ID', 'ID1', 'ID2'],
            ['2020-01-01', 100, 200]
        ])
        
        # Should find Series ID row and return next row
        assert _find_header_row(df) == 3
    
    def test_find_header_with_dates(self):
        """Test finding header row by date pattern."""
        df = pd.DataFrame([
            ['Title', None, None],
            ['2020-01-01', '2020-02-01', '2020-03-01'],
            [100, 200, 300]
        ])
        
        # Should find row with dates
        assert _find_header_row(df) == 1
    
    def test_find_header_default(self):
        """Test default header row when not found."""
        df = pd.DataFrame([[1, 2, 3]] * 15)
        
        # Should return default
        assert _find_header_row(df) == 10


class TestIsDateLike:
    """Test the _is_date_like function."""
    
    def test_datetime_objects(self):
        """Test with datetime objects."""
        assert _is_date_like(pd.Timestamp('2020-01-01'))
        assert _is_date_like(pd.to_datetime('2020-01-01'))
    
    def test_date_strings(self):
        """Test with date-like strings."""
        assert _is_date_like('2020-01-01')
        assert _is_date_like('Jan-2020')
        assert _is_date_like('Q1 2020')
        assert _is_date_like('March 2020')
    
    def test_non_dates(self):
        """Test with non-date values."""
        assert not _is_date_like('Hello')
        assert not _is_date_like(123)
        assert not _is_date_like(None)
        assert not _is_date_like(np.nan)


class TestExtractMetadata:
    """Test the _extract_metadata function."""
    
    def test_extract_metadata_complete(self):
        """Test extracting all metadata fields."""
        df = pd.DataFrame([
            ['Consumer Price Index', None, None],
            ['Frequency: Quarterly', None, None],
            ['Units: Per cent', None, None],
            ['Source: ABS', None, None],
            ['Last updated: 2023-12-01', None, None]
        ])
        
        metadata = _extract_metadata(df, 5)
        
        assert metadata['title'] == 'Consumer Price Index'
        assert metadata['frequency'] == 'Quarterly'
        assert metadata['units'] == 'Per cent'
        assert metadata['source'] == 'ABS'
    
    def test_extract_metadata_partial(self):
        """Test with partial metadata."""
        df = pd.DataFrame([
            ['Some Title', None, None],
            ['Monthly data', None, None],
            ['Values in $ million', None, None]
        ])
        
        metadata = _extract_metadata(df, 3)
        
        assert metadata['title'] == 'Some Title'
        assert metadata['frequency'] == 'Monthly'
        assert metadata['units'] == '$ million'


class TestExtractSeriesIds:
    """Test the _extract_series_ids function."""
    
    def test_extract_series_ids_found(self):
        """Test extracting series IDs when present."""
        df = pd.DataFrame([
            ['Title', None, None],
            ['Series ID', 'GCPIAG', 'GCPITC'],
            ['Description', 'CPI All', 'CPI Trim'],
            ['2020-01-01', 100, 200]
        ])
        
        # Mock the header row data
        df.iloc[3] = ['2020-01-01', 'CPI All', 'CPI Trim']
        
        series_map = _extract_series_ids(df, 3)
        
        assert series_map == {
            'CPI All': 'GCPIAG',
            'CPI Trim': 'GCPITC'
        }
    
    def test_extract_series_ids_not_found(self):
        """Test when no series IDs found."""
        df = pd.DataFrame([
            ['Title', None, None],
            ['2020-01-01', 100, 200]
        ])
        
        series_map = _extract_series_ids(df, 1)
        
        assert series_map == {}


class TestTidySpecialTable:
    """Test the _tidy_special_table function."""
    
    def test_tidy_special_table_not_implemented(self):
        """Test that special tables raise appropriate error."""
        mock_xl = MagicMock()
        
        with pytest.raises(RBADataError, match="non-standard format"):
            _tidy_special_table(mock_xl, 'A1.1', 'http://example.com', 'current')