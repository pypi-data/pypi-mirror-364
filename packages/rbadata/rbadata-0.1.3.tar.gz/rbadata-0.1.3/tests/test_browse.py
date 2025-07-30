"""
Tests for browse functionality
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from rbadata import browse_rba_tables, browse_rba_series


class TestBrowseTables:
    """Test browse_rba_tables function."""
    
    @patch('rbadata.browse.get_table_list')
    def test_browse_all_tables(self, mock_get_tables):
        """Test browsing all tables."""
        # Create sample table data
        sample_tables = pd.DataFrame({
            'title': ['Consumer Price Inflation', 'Labour Force'],
            'no': ['G1', 'H3'],
            'url': ['https://example.com/g1.xlsx', 'https://example.com/h3.xlsx'],
            'current_or_historical': ['current', 'current'],
            'readable': [True, True]
        })
        mock_get_tables.return_value = sample_tables
        
        # Call function
        result = browse_rba_tables()
        
        # Verify
        mock_get_tables.assert_called_once_with(refresh=False)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ['title', 'no', 'url', 'current_or_historical', 'readable']
    
    @patch('rbadata.browse.get_table_list')
    def test_browse_tables_with_search(self, mock_get_tables):
        """Test browsing tables with search filter."""
        # Create sample table data
        sample_tables = pd.DataFrame({
            'title': ['Consumer Price Inflation', 'Labour Force', 'Inflation Expectations'],
            'no': ['G1', 'H3', 'G3'],
            'url': ['https://example.com/g1.xlsx', 'https://example.com/h3.xlsx', 'https://example.com/g3.xlsx'],
            'current_or_historical': ['current', 'current', 'current'],
            'readable': [True, True, True]
        })
        mock_get_tables.return_value = sample_tables
        
        # Call function with search
        result = browse_rba_tables(search="inflation")
        
        # Verify - should return only inflation-related tables
        assert len(result) == 2
        assert all('inflation' in title.lower() for title in result['title'])
    
    @patch('rbadata.browse.get_table_list')
    def test_browse_tables_refresh(self, mock_get_tables):
        """Test browsing tables with refresh."""
        sample_tables = pd.DataFrame({
            'title': ['Test Table'],
            'no': ['T1'],
            'url': ['https://example.com/t1.xlsx'],
            'current_or_historical': ['current'],
            'readable': [True]
        })
        mock_get_tables.return_value = sample_tables
        
        # Call with refresh
        result = browse_rba_tables(refresh=True)
        
        # Verify refresh was passed through
        mock_get_tables.assert_called_once_with(refresh=True)


class TestBrowseSeries:
    """Test browse_rba_series function."""
    
    @patch('rbadata.browse.get_series_list')
    def test_browse_all_series(self, mock_get_series):
        """Test browsing all series."""
        # Create sample series data
        sample_series = pd.DataFrame({
            'series_id': ['GCPIAG', 'GLFSURSA'],
            'series': ['Consumer price index', 'Unemployment rate'],
            'table_no': ['G1', 'H3'],
            'description': ['CPI all groups', 'Unemployment rate SA'],
            'frequency': ['Quarterly', 'Monthly'],
            'units': ['Index', 'Per cent']
        })
        mock_get_series.return_value = sample_series
        
        # Call function
        result = browse_rba_series()
        
        # Verify
        mock_get_series.assert_called_once_with(refresh=False)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
    
    @patch('rbadata.browse.get_series_list')
    def test_browse_series_with_search(self, mock_get_series):
        """Test browsing series with search filter."""
        # Create sample series data
        sample_series = pd.DataFrame({
            'series_id': ['GCPIAG', 'GLFSURSA', 'GCPITCF'],
            'series': ['Consumer price index', 'Unemployment rate', 'Trimmed mean inflation'],
            'table_no': ['G1', 'H3', 'G1'],
            'description': ['CPI all groups', 'Unemployment rate SA', 'Trimmed mean CPI'],
            'frequency': ['Quarterly', 'Monthly', 'Quarterly'],
            'units': ['Index', 'Per cent', 'Per cent']
        })
        mock_get_series.return_value = sample_series
        
        # Call function with search
        result = browse_rba_series(search="inflation")
        
        # Verify - should return only inflation-related series
        assert len(result) == 1
        assert 'inflation' in result.iloc[0]['series'].lower()
    
    @patch('rbadata.browse.get_series_list')
    def test_browse_series_by_table(self, mock_get_series):
        """Test browsing series filtered by table number."""
        # Create sample series data
        sample_series = pd.DataFrame({
            'series_id': ['GCPIAG', 'GLFSURSA', 'GCPITCF'],
            'series': ['Consumer price index', 'Unemployment rate', 'Trimmed mean inflation'],
            'table_no': ['G1', 'H3', 'G1'],
            'description': ['CPI all groups', 'Unemployment rate SA', 'Trimmed mean CPI'],
            'frequency': ['Quarterly', 'Monthly', 'Quarterly'],
            'units': ['Index', 'Per cent', 'Per cent']
        })
        mock_get_series.return_value = sample_series
        
        # Call function filtering by table
        result = browse_rba_series(table_no="G1")
        
        # Verify - should return only G1 series
        assert len(result) == 2
        assert all(row['table_no'] == 'G1' for _, row in result.iterrows())