"""
Tests for the data module
"""

import pytest
import pandas as pd
import json
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from rbadata.data import get_table_list, get_series_list, _build_series_list


class TestGetTableList:
    """Test the get_table_list function."""
    
    @patch('rbadata.data._table_cache', None)
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_table_list_from_file(self, mock_file, mock_exists):
        """Test loading table list from JSON file."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Mock JSON data
        table_data = [
            {
                "no": "A1",
                "title": "Australian Credit Aggregates",
                "url": "https://www.rba.gov.au/statistics/tables/xls/a01.xls",
                "current_or_historical": "current"
            },
            {
                "no": "G1",
                "title": "Consumer Price Inflation",
                "url": "https://www.rba.gov.au/statistics/tables/xls/g01.xls",
                "current_or_historical": "current"
            }
        ]
        mock_file.return_value.read.return_value = json.dumps(table_data)
        
        # Call function
        result = get_table_list(refresh=False)
        
        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result['no']) == ['A1', 'G1']
        assert 'title' in result.columns
        assert 'url' in result.columns
        
        # Check that file was opened
        mock_file.assert_called_once()
    
    @patch('rbadata.data._table_cache', None)
    @patch('pathlib.Path.exists')
    @patch('rbadata.data.scrape_table_list')
    def test_get_table_list_scrape(self, mock_scrape, mock_exists):
        """Test scraping table list when file doesn't exist."""
        # Setup mocks
        mock_exists.return_value = False
        
        # Mock scraped data
        scraped_data = pd.DataFrame({
            'no': ['A1', 'B1', 'C1'],
            'title': ['Table A', 'Table B', 'Table C'],
            'url': ['url_a', 'url_b', 'url_c'],
            'current_or_historical': ['current'] * 3
        })
        mock_scrape.return_value = scraped_data
        
        # Call function
        result = get_table_list(refresh=False)
        
        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result['no']) == ['A1', 'B1', 'C1']
        mock_scrape.assert_called_once()
    
    def test_get_table_list_from_cache(self):
        """Test returning cached table list."""
        # Set up cache directly
        import rbadata.data
        cached_data = pd.DataFrame({
            'no': ['X1', 'Y1'],
            'title': ['Cached X', 'Cached Y'],
            'url': ['url_x', 'url_y'],
            'current_or_historical': ['current'] * 2
        })
        rbadata.data._table_cache = cached_data
        
        # Call function (should not hit file or scrape)
        with patch('pathlib.Path.exists') as mock_exists:
            with patch('rbadata.data.scrape_table_list') as mock_scrape:
                result = get_table_list(refresh=False)
        
        # Verify cache was used
        assert len(result) == 2
        assert list(result['no']) == ['X1', 'Y1']
        mock_exists.assert_not_called()
        mock_scrape.assert_not_called()
    
    @patch('rbadata.data._table_cache', None)
    @patch('pathlib.Path.exists')
    @patch('rbadata.data.scrape_table_list')
    def test_get_table_list_refresh(self, mock_scrape, mock_exists):
        """Test forcing refresh of table list."""
        # Setup mocks
        mock_exists.return_value = True  # File exists
        
        # Mock scraped data
        scraped_data = pd.DataFrame({
            'no': ['NEW1'],
            'title': ['Fresh Data'],
            'url': ['new_url'],
            'current_or_historical': ['current']
        })
        mock_scrape.return_value = scraped_data
        
        # Call with refresh=True
        result = get_table_list(refresh=True)
        
        # Verify scrape was called despite file existing
        assert len(result) == 1
        assert result['no'].iloc[0] == 'NEW1'
        mock_scrape.assert_called_once()
    
    @patch('rbadata.data._table_cache', None)
    @patch('pathlib.Path.exists')
    @patch('rbadata.data.scrape_table_list')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_table_list_save_error(self, mock_file, mock_scrape, mock_exists):
        """Test handling of save errors."""
        # Setup mocks
        mock_exists.return_value = False
        mock_scrape.return_value = pd.DataFrame({'no': ['A1']})
        
        # Make save fail
        mock_file.side_effect = IOError("Cannot write")
        
        # Call function - should not raise
        result = get_table_list()
        
        # Verify function still returns data
        assert len(result) == 1


class TestGetSeriesList:
    """Test the get_series_list function."""
    
    @patch('rbadata.data._series_cache', None)
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_series_list_from_file(self, mock_file, mock_exists):
        """Test loading series list from JSON file."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Mock JSON data
        series_data = [
            {
                "series_id": "GCPIAG",
                "series": "CPI All Groups",
                "table_no": "G1",
                "frequency": "Quarterly",
                "units": "Index"
            },
            {
                "series_id": "FIRMMCRT",
                "series": "Cash Rate Target",
                "table_no": "F1",
                "frequency": "Daily",
                "units": "Per cent"
            }
        ]
        mock_file.return_value.read.return_value = json.dumps(series_data)
        
        # Call function
        result = get_series_list(refresh=False)
        
        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result['series_id']) == ['GCPIAG', 'FIRMMCRT']
        assert 'table_no' in result.columns
        assert 'frequency' in result.columns
    
    @patch('rbadata.data._series_cache', None)
    @patch('pathlib.Path.exists')
    @patch('rbadata.data._build_series_list')
    def test_get_series_list_build(self, mock_build, mock_exists):
        """Test building series list when file doesn't exist."""
        # Setup mocks
        mock_exists.return_value = False
        
        # Mock built data
        built_data = pd.DataFrame({
            'series_id': ['TEST1', 'TEST2'],
            'series': ['Test Series 1', 'Test Series 2'],
            'table_no': ['T1', 'T2']
        })
        mock_build.return_value = built_data
        
        # Call function
        result = get_series_list(refresh=False)
        
        # Verify
        assert len(result) == 2
        assert list(result['series_id']) == ['TEST1', 'TEST2']
        mock_build.assert_called_once()
    
    def test_get_series_list_from_cache(self):
        """Test returning cached series list."""
        # Set up cache directly
        import rbadata.data
        cached_data = pd.DataFrame({
            'series_id': ['CACHED1'],
            'series': ['Cached Series'],
            'table_no': ['C1']
        })
        rbadata.data._series_cache = cached_data
        
        # Call function
        with patch('pathlib.Path.exists') as mock_exists:
            with patch('rbadata.data._build_series_list') as mock_build:
                result = get_series_list(refresh=False)
        
        # Verify cache was used
        assert len(result) == 1
        assert result['series_id'].iloc[0] == 'CACHED1'
        mock_exists.assert_not_called()
        mock_build.assert_not_called()
    
    @patch('rbadata.data._series_cache', None)
    @patch('pathlib.Path.exists')
    @patch('rbadata.data._build_series_list')
    def test_get_series_list_refresh(self, mock_build, mock_exists):
        """Test forcing refresh of series list."""
        # Setup mocks
        mock_exists.return_value = True  # File exists
        
        # Mock built data
        built_data = pd.DataFrame({
            'series_id': ['FRESH1'],
            'series': ['Fresh Series'],
            'table_no': ['F1']
        })
        mock_build.return_value = built_data
        
        # Call with refresh=True
        result = get_series_list(refresh=True)
        
        # Verify build was called despite file existing
        assert len(result) == 1
        assert result['series_id'].iloc[0] == 'FRESH1'
        mock_build.assert_called_once()


class TestBuildSeriesList:
    """Test the _build_series_list function."""
    
    def test_build_series_list_structure(self):
        """Test the structure of built series list."""
        result = _build_series_list()
        
        # Verify structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        
        # Check required columns
        required_cols = ['series_id', 'series', 'table_no', 'frequency', 'units']
        for col in required_cols:
            assert col in result.columns
        
        # Check specific series
        assert 'GCPIAG' in result['series_id'].values
        assert 'GLFSURSA' in result['series_id'].values
        assert 'FIRMMCRT' in result['series_id'].values
    
    def test_build_series_list_content(self):
        """Test the content of built series list."""
        result = _build_series_list()
        
        # Check CPI series
        cpi_row = result[result['series_id'] == 'GCPIAG'].iloc[0]
        assert cpi_row['table_no'] == 'G1'
        assert 'consumer price' in cpi_row['series'].lower()
        assert cpi_row['frequency'] == 'Quarterly'
        assert cpi_row['units'] == 'Index'
        
        # Check unemployment series
        unemp_row = result[result['series_id'] == 'GLFSURSA'].iloc[0]
        assert unemp_row['table_no'] == 'H3'
        assert 'unemployment' in unemp_row['series'].lower()
        assert unemp_row['frequency'] == 'Monthly'
        assert unemp_row['units'] == 'Per cent'
        
        # Check cash rate series
        cash_row = result[result['series_id'] == 'FIRMMCRT'].iloc[0]
        assert cash_row['table_no'] == 'F1.1'
        assert 'cash rate' in cash_row['series'].lower()
        assert cash_row['frequency'] == 'Daily'


class TestDataModuleIntegration:
    """Integration tests for data module."""
    
    @patch('rbadata.data._table_cache', None)
    @patch('rbadata.data._series_cache', None)
    def test_cache_persistence(self):
        """Test that cache persists between calls."""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('rbadata.data.scrape_table_list') as mock_scrape:
                with patch('rbadata.data._build_series_list') as mock_build:
                    # Setup mocks
                    mock_scrape.return_value = pd.DataFrame({'no': ['A1']})
                    mock_build.return_value = pd.DataFrame({'series_id': ['S1']})
                    
                    # First calls should scrape/build
                    table1 = get_table_list()
                    series1 = get_series_list()
                    
                    assert mock_scrape.call_count == 1
                    assert mock_build.call_count == 1
                    
                    # Second calls should use cache
                    table2 = get_table_list()
                    series2 = get_series_list()
                    
                    assert mock_scrape.call_count == 1  # Not called again
                    assert mock_build.call_count == 1  # Not called again
                    
                    # Data should be the same
                    pd.testing.assert_frame_equal(table1, table2)
                    pd.testing.assert_frame_equal(series1, series2)