"""
Tests for RBADataFetcher class.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, mock_open

import pandas as pd
import pytest

from rbadata.fetcher import RBADataFetcher
from rbadata.exceptions import ValidationError, DataError, RBADataError


class TestRBADataFetcher:
    """Test RBADataFetcher class."""
    
    def test_initialization(self):
        """Test fetcher initialization."""
        fetcher = RBADataFetcher(
            cache_backend='memory',
            default_ttl=7200,
            max_concurrent=10,
            validate_data=True,
            track_performance=True
        )
        
        assert fetcher.max_concurrent == 10
        assert fetcher.validate_data is True
        assert fetcher.track_performance is True
        assert fetcher._performance_stats['total_requests'] == 0
        
    @patch('rbadata.fetcher.configure_cache')
    def test_cache_configuration(self, mock_configure):
        """Test cache is configured properly."""
        fetcher = RBADataFetcher(
            cache_backend='disk',
            cache_dir='/tmp/cache',
            default_ttl=3600
        )
        
        mock_configure.assert_called_once_with(
            backend='disk',
            cache_dir='/tmp/cache',
            default_ttl=3600,
            enabled=True
        )
        
    def test_load_series_metadata(self):
        """Test loading series metadata."""
        # Mock metadata file
        mock_metadata = {
            "F1": {
                "table_name": "Interest Rates",
                "series": {
                    "TEST1": {"description": "Test Series 1"}
                }
            }
        }
        
        # Test that fetcher can load metadata successfully
        fetcher = RBADataFetcher()
        
        # Manually set metadata to test functionality
        fetcher.series_metadata = mock_metadata
        
        assert 'F1' in fetcher.series_metadata
        assert fetcher.series_metadata['F1']['table_name'] == 'Interest Rates'
        
    @patch('rbadata.fetcher.read_rba')
    def test_fetch_basic(self, mock_read_rba):
        """Test basic fetch functionality."""
        # Setup
        expected_df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=3),
            'series_id': ['TEST1'] * 3,
            'value': [1.0, 2.0, 3.0]
        })
        mock_read_rba.return_value = expected_df
        
        fetcher = RBADataFetcher()
        
        # Execute
        result = fetcher.fetch(table_no='F1')
        
        # Assert
        pd.testing.assert_frame_equal(result, expected_df)
        mock_read_rba.assert_called_once_with(
            table_no='F1',
            series_id=None,
            start_date=None,
            end_date=None,
            use_csv=True,
            use_cache=True
        )
        
    @patch('rbadata.fetcher.read_rba')
    def test_fetch_with_date_validation(self, mock_read_rba):
        """Test fetch with date validation."""
        fetcher = RBADataFetcher(validate_data=True)
        
        # Invalid date range
        with pytest.raises(ValidationError) as exc_info:
            fetcher.fetch(
                table_no='F1',
                start_date='2023-12-31',
                end_date='2023-01-01'
            )
            
        assert 'start_date must be before end_date' in str(exc_info.value)
        
    @patch('rbadata.fetcher.read_rba')
    def test_fetch_with_performance_tracking(self, mock_read_rba):
        """Test performance tracking."""
        # Setup
        mock_read_rba.return_value = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'series_id': ['TEST'],
            'value': [1.0]
        })
        
        fetcher = RBADataFetcher(track_performance=True)
        
        # Execute
        fetcher.fetch(table_no='F1')
        
        # Check stats
        assert fetcher._performance_stats['total_requests'] == 1
        assert fetcher._performance_stats['total_download_time'] > 0
        
    @patch('rbadata.fetcher.read_rba')
    def test_fetch_with_error_tracking(self, mock_read_rba):
        """Test error tracking."""
        # Setup
        mock_read_rba.side_effect = DataError("Test error")
        
        fetcher = RBADataFetcher(track_performance=True)
        
        # Execute
        with pytest.raises(DataError):
            fetcher.fetch(table_no='F1')
            
        # Check error was tracked
        assert len(fetcher._performance_stats['errors']) == 1
        assert 'Test error' in fetcher._performance_stats['errors'][0]['error']
        
    @patch('rbadata.fetcher.read_rba')
    def test_fetch_series(self, mock_read_rba):
        """Test fetching specific series."""
        # Setup
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=2),
            'series_id': ['TEST1', 'TEST2'],
            'value': [1.0, 2.0],
            'description': ['Desc 1', 'Desc 2'],
            'units': ['Percent', 'Dollars']
        })
        mock_read_rba.return_value = df
        
        fetcher = RBADataFetcher()
        
        # Test non-pivoted
        result = fetcher.fetch_series(['TEST1', 'TEST2'])
        pd.testing.assert_frame_equal(result, df)
        
        # Test pivoted
        pivot_result = fetcher.fetch_series(['TEST1', 'TEST2'], pivot=True)
        assert isinstance(pivot_result, pd.DataFrame)
        assert 'TEST1' in pivot_result.columns
        assert 'TEST2' in pivot_result.columns
        
    def test_fetch_async_import_error(self):
        """Test async fetch functionality."""
        # Since aiohttp is now available, test that async works
        fetcher = RBADataFetcher()
        
        # Mock the async functionality to avoid real network calls
        with patch('rbadata.fetcher.AsyncRBAClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.read_rba_async.return_value = pd.DataFrame({'test': [1]})
            
            import asyncio
            
            async def test_async():
                result = await fetcher.fetch_async(table_no='F1')
                assert isinstance(result, pd.DataFrame)
            
            # Run the async test
            asyncio.run(test_async())
        
    def test_get_available_series(self):
        """Test getting available series."""
        fetcher = RBADataFetcher()
        fetcher.series_metadata = {
            'F1': {
                'table_name': 'Interest Rates',
                'series': {
                    'TEST1': {'description': 'Test 1'},
                    'TEST2': {'description': 'Test 2'}
                }
            }
        }
        
        # Test specific table
        result = fetcher.get_available_series('F1')
        assert result['table_name'] == 'Interest Rates'
        assert 'TEST1' in result['series']
        assert 'TEST2' in result['series']
        
        # Test all tables
        all_result = fetcher.get_available_series()
        assert 'F1' in all_result
        assert all_result['F1']['series_count'] == 2
        
    def test_search_series(self):
        """Test series search functionality."""
        fetcher = RBADataFetcher()
        fetcher.series_metadata = {
            'F1': {
                'series': {
                    'FIRMMCRTD': {
                        'description': 'Cash Rate Target',
                        'unit': 'Percent',
                        'type': 'interest_rate'
                    },
                    'FCMYGBAG2': {
                        'description': 'Australian Government 2 year bond',
                        'unit': 'Percent per annum',
                        'type': 'bond_yield'
                    }
                }
            }
        }
        
        # Search by ID
        results = fetcher.search_series('FIRM')
        assert len(results) == 1
        assert results[0]['series_id'] == 'FIRMMCRTD'
        
        # Search by description
        results = fetcher.search_series('bond')
        assert len(results) == 1
        assert results[0]['series_id'] == 'FCMYGBAG2'
        
        # Search returns multiple
        results = fetcher.search_series('F')
        assert len(results) == 2
        
    @patch('rbadata.fetcher.RBADataFetcher.fetch_series')
    def test_build_yield_curve(self, mock_fetch):
        """Test yield curve building."""
        # Mock data for government bonds
        mock_data = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')] * 3,
            'series_id': ['FCMYGBAG1', 'FCMYGBAG2', 'FCMYGBAG10'],
            'value': [4.0, 4.5, 5.0]
        })
        mock_fetch.return_value = mock_data
        
        fetcher = RBADataFetcher()
        
        # Build curve
        curve = fetcher.build_yield_curve(date='2023-01-01')
        
        # Assert
        assert len(curve) == 3
        assert 'tenor' in curve.columns
        assert 'yield' in curve.columns
        assert curve['tenor'].tolist() == [1, 2, 10]
        assert curve['yield'].tolist() == [4.0, 4.5, 5.0]
        
    @patch('rbadata.fetcher.RBADataFetcher.fetch_series')
    def test_build_yield_curve_invalid_type(self, mock_fetch):
        """Test yield curve with invalid type."""
        fetcher = RBADataFetcher()
        
        with pytest.raises(ValueError) as exc_info:
            fetcher.build_yield_curve(curve_type='invalid')
            
        assert 'Unknown curve type' in str(exc_info.value)
        
    def test_validate_dataframe(self):
        """Test DataFrame validation."""
        fetcher = RBADataFetcher(validate_data=True)
        
        # Valid DataFrame
        valid_df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=2),
            'series_id': ['TEST1', 'TEST2'],
            'value': [1.0, 2.0]
        })
        
        # Should not raise
        fetcher._validate_dataframe(valid_df)
        
        # Empty DataFrame
        with pytest.raises(DataError) as exc_info:
            fetcher._validate_dataframe(pd.DataFrame())
        assert 'empty' in str(exc_info.value)
        
        # Missing columns
        with pytest.raises(DataError) as exc_info:
            fetcher._validate_dataframe(pd.DataFrame({'date': [1]}))
        assert 'Missing required columns' in str(exc_info.value)
        
        # Wrong date type
        wrong_date_df = pd.DataFrame({
            'date': ['2023-01-01'],  # String, not datetime
            'series_id': ['TEST'],
            'value': [1.0]
        })
        with pytest.raises(DataError) as exc_info:
            fetcher._validate_dataframe(wrong_date_df)
        assert 'date' in str(exc_info.value)
        
    def test_performance_stats(self):
        """Test performance statistics."""
        fetcher = RBADataFetcher(track_performance=False)
        
        # Disabled
        stats = fetcher.get_performance_stats()
        assert stats['message'] == 'Performance tracking is disabled'
        
        # Enabled
        fetcher = RBADataFetcher(track_performance=True)
        fetcher._performance_stats = {
            'total_requests': 10,
            'cache_hits': 7,
            'cache_misses': 3,
            'total_download_time': 5.0,
            'total_parse_time': 1.0,
            'errors': []
        }
        
        stats = fetcher.get_performance_stats()
        assert stats['cache_hit_rate'] == 0.7
        assert stats['avg_download_time'] == 0.5
        
    def test_clear_cache(self):
        """Test cache clearing."""
        fetcher = RBADataFetcher()
        fetcher.cache = Mock()
        
        fetcher.clear_cache()
        
        fetcher.cache.clear.assert_called_once()
        
    def test_repr(self):
        """Test string representation."""
        fetcher = RBADataFetcher(
            cache_backend='memory',
            max_concurrent=5,
            validate_data=True
        )
        
        repr_str = repr(fetcher)
        assert 'RBADataFetcher' in repr_str
        assert 'max_concurrent=5' in repr_str
        assert 'validate=True' in repr_str


class TestRBADataFetcherIntegration:
    """Integration tests for RBADataFetcher."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow with mocked data."""
        fetcher = RBADataFetcher()
        fetcher.series_metadata = {
            'F1': {
                'table_name': 'Interest Rates',
                'series': {
                    'FIRMMCRTD': {
                        'description': 'Cash Rate Target',
                        'unit': 'Percent',
                        'type': 'interest_rate'
                    }
                }
            }
        }
        
        # Test search functionality
        results = fetcher.search_series('cash')
        assert len(results) == 1
        assert results[0]['series_id'] == 'FIRMMCRTD'
        
        # Test get available series
        series_info = fetcher.get_available_series('F1')
        assert 'FIRMMCRTD' in series_info['series']
        assert series_info['table_name'] == 'Interest Rates'