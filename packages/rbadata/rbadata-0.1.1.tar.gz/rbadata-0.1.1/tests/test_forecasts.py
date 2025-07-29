"""
Tests for the forecasts module
"""

import pytest
import pandas as pd
from unittest.mock import patch, Mock
from datetime import datetime
from rbadata.forecasts import (
    rba_forecasts,
    _get_historical_forecasts,
    _get_recent_forecasts,
    _scrape_latest_forecasts
)
from rbadata.utils import get_pandas_freq_alias
from rbadata.exceptions import RBADataError


class TestRBAForecasts:
    """Test the main rba_forecasts function."""
    
    @patch('rbadata.forecasts.check_rba_connection')
    @patch('rbadata.forecasts._get_historical_forecasts')
    @patch('rbadata.forecasts._get_recent_forecasts')
    @patch('rbadata.forecasts._scrape_latest_forecasts')
    def test_rba_forecasts_all(self, mock_scrape, mock_recent, mock_hist, mock_check):
        """Test getting all forecasts."""
        # Setup mocks
        mock_check.return_value = None
        
        # Mock historical forecasts
        hist_data = pd.DataFrame({
            'forecast_date': [pd.Timestamp('2010-05-01')] * 2,
            'date': pd.date_range('2010-06-01', periods=2, freq=get_pandas_freq_alias("Q")),
            'series': ['gdp_change'] * 2,
            'value': [3.5, 3.7],
            'series_desc': ['GDP growth'] * 2,
            'source': ['RDP'] * 2,
            'notes': [None] * 2
        })
        mock_hist.return_value = hist_data
        
        # Mock recent forecasts
        recent_data = pd.DataFrame({
            'forecast_date': [pd.Timestamp('2023-05-01')] * 2,
            'date': pd.date_range('2023-06-01', periods=2, freq=get_pandas_freq_alias("Q")),
            'series': ['cpi_annual'] * 2,
            'value': [5.8, 4.9],
            'series_desc': ['CPI'] * 2,
            'source': ['SMP'] * 2,
            'notes': [None] * 2
        })
        mock_recent.return_value = recent_data
        
        # Mock latest forecasts
        latest_data = pd.DataFrame({
            'forecast_date': [pd.Timestamp('2024-08-01')] * 2,
            'date': pd.date_range('2024-06-01', periods=2, freq=get_pandas_freq_alias("Q")),
            'series': ['gdp_change'] * 2,
            'value': [2.5, 2.6],
            'series_desc': ['GDP'] * 2,
            'source': ['SMP Aug 2024'] * 2,
            'notes': [None] * 2
        })
        mock_scrape.return_value = latest_data
        
        # Call function
        result = rba_forecasts(all_or_latest='all')
        
        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 6  # 2 + 2 + 2 forecasts
        assert 'year_qtr' in result.columns
        assert 'forecast_date' in result.columns
        assert 'series' in result.columns
        
        # Check that all three sources were called
        mock_hist.assert_called_once()
        mock_recent.assert_called_once()
        mock_scrape.assert_called_once()
    
    @patch('rbadata.forecasts.check_rba_connection')
    @patch('rbadata.forecasts._get_historical_forecasts')
    @patch('rbadata.forecasts._get_recent_forecasts')
    @patch('rbadata.forecasts._scrape_latest_forecasts')
    def test_rba_forecasts_latest_only(self, mock_scrape, mock_recent, mock_hist, mock_check):
        """Test getting only latest forecasts."""
        # Setup mocks with different forecast dates
        mock_check.return_value = None
        
        # Historical - old forecast date
        hist_data = pd.DataFrame({
            'forecast_date': [pd.Timestamp('2010-05-01')] * 2,
            'date': pd.date_range('2010-06-01', periods=2, freq=get_pandas_freq_alias("Q")),
            'series': ['gdp_change'] * 2,
            'value': [3.5, 3.7],
            'series_desc': ['GDP'] * 2,
            'source': ['RDP'] * 2,
            'notes': [None] * 2
        })
        mock_hist.return_value = hist_data
        
        # Recent - more recent forecast date
        recent_data = pd.DataFrame({
            'forecast_date': [pd.Timestamp('2023-05-01')] * 2,
            'date': pd.date_range('2023-06-01', periods=2, freq=get_pandas_freq_alias("Q")),
            'series': ['cpi_annual'] * 2,
            'value': [5.8, 4.9],
            'series_desc': ['CPI'] * 2,
            'source': ['SMP'] * 2,
            'notes': [None] * 2
        })
        mock_recent.return_value = recent_data
        
        # Latest - most recent forecast date
        latest_data = pd.DataFrame({
            'forecast_date': [pd.Timestamp('2024-08-01')] * 3,
            'date': pd.date_range('2024-06-01', periods=3, freq=get_pandas_freq_alias("Q")),
            'series': ['gdp_change'] * 3,
            'value': [2.5, 2.6, 2.7],
            'series_desc': ['GDP'] * 3,
            'source': ['SMP Aug 2024'] * 3,
            'notes': [None] * 3
        })
        mock_scrape.return_value = latest_data
        
        # Call function
        result = rba_forecasts(all_or_latest='latest')
        
        # Verify - should only return the latest forecasts
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3  # Only the latest 3 forecasts
        assert all(result['forecast_date'] == pd.Timestamp('2024-08-01'))
    
    @patch('rbadata.forecasts.check_rba_connection')
    @patch('rbadata.forecasts._get_historical_forecasts')
    @patch('rbadata.forecasts._get_recent_forecasts')
    @patch('rbadata.forecasts._scrape_latest_forecasts')
    def test_rba_forecasts_with_failures(self, mock_scrape, mock_recent, mock_hist, mock_check):
        """Test behavior when some sources fail."""
        # Setup mocks
        mock_check.return_value = None
        
        # Historical fails
        mock_hist.side_effect = Exception("Historical data unavailable")
        
        # Recent works
        recent_data = pd.DataFrame({
            'forecast_date': [pd.Timestamp('2023-05-01')] * 2,
            'date': pd.date_range('2023-06-01', periods=2, freq=get_pandas_freq_alias("Q")),
            'series': ['cpi_annual'] * 2,
            'value': [5.8, 4.9],
            'series_desc': ['CPI'] * 2,
            'source': ['SMP'] * 2,
            'notes': [None] * 2
        })
        mock_recent.return_value = recent_data
        
        # Latest fails
        mock_scrape.side_effect = Exception("Scraping failed")
        
        # Call function - should still work with just recent data
        result = rba_forecasts()
        
        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # Only recent data
        assert all(result['series'] == 'cpi_annual')
    
    @patch('rbadata.forecasts.check_rba_connection')
    @patch('rbadata.forecasts._get_historical_forecasts')
    @patch('rbadata.forecasts._get_recent_forecasts')
    @patch('rbadata.forecasts._scrape_latest_forecasts')
    def test_rba_forecasts_all_sources_fail(self, mock_scrape, mock_recent, mock_hist, mock_check):
        """Test error when all sources fail."""
        # Setup mocks
        mock_check.return_value = None
        
        # All sources fail
        mock_hist.side_effect = Exception("Historical failed")
        mock_recent.side_effect = Exception("Recent failed")
        mock_scrape.side_effect = Exception("Scraping failed")
        
        # Should raise error
        with pytest.raises(RBADataError, match="Could not retrieve any forecast data"):
            rba_forecasts()
    
    @patch('rbadata.forecasts.check_rba_connection')
    @patch('rbadata.forecasts._get_historical_forecasts')
    @patch('rbadata.forecasts._get_recent_forecasts')
    @patch('rbadata.forecasts._scrape_latest_forecasts')
    def test_rba_forecasts_duplicate_handling(self, mock_scrape, mock_recent, mock_hist, mock_check):
        """Test that duplicates are handled correctly."""
        # Setup mocks
        mock_check.return_value = None
        
        # Create overlapping data
        base_date = pd.date_range('2023-06-01', periods=2, freq=get_pandas_freq_alias("Q"))
        
        # Historical - older forecast for same date/series
        hist_data = pd.DataFrame({
            'forecast_date': [pd.Timestamp('2023-02-01')] * 2,
            'date': base_date,
            'series': ['gdp_change'] * 2,
            'value': [3.0, 3.1],  # Old forecast values
            'series_desc': ['GDP'] * 2,
            'source': ['SMP Feb'] * 2,
            'notes': [None] * 2
        })
        mock_hist.return_value = hist_data
        
        # Recent - newer forecast for same date/series
        recent_data = pd.DataFrame({
            'forecast_date': [pd.Timestamp('2023-05-01')] * 2,
            'date': base_date,
            'series': ['gdp_change'] * 2,
            'value': [3.2, 3.3],  # Updated forecast values
            'series_desc': ['GDP'] * 2,
            'source': ['SMP May'] * 2,
            'notes': [None] * 2
        })
        mock_recent.return_value = recent_data
        
        # Latest - empty
        mock_scrape.return_value = pd.DataFrame()
        
        # Call function
        result = rba_forecasts()
        
        # The function doesn't deduplicate by default based on forecast_date
        # It only deduplicates exact matches of date, series, and forecast_date
        # So we'll have all 4 rows
        assert len(result) == 4
        
        # Check that we have both old and new forecasts
        assert len(result[result['forecast_date'] == pd.Timestamp('2023-02-01')]) == 2
        assert len(result[result['forecast_date'] == pd.Timestamp('2023-05-01')]) == 2


class TestGetHistoricalForecasts:
    """Test the _get_historical_forecasts function."""
    
    def test_get_historical_forecasts(self):
        """Test getting historical forecasts."""
        result = _get_historical_forecasts()
        
        # Verify structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
        assert list(result.columns) == ['forecast_date', 'date', 'series', 'value', 'series_desc', 'source', 'notes']
        assert all(result['series'] == 'gdp_change')
        assert all(result['source'] == 'RDP 2012-07')
        
        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(result['forecast_date'])
        assert pd.api.types.is_datetime64_any_dtype(result['date'])
        assert pd.api.types.is_numeric_dtype(result['value'])


class TestGetRecentForecasts:
    """Test the _get_recent_forecasts function."""
    
    def test_get_recent_forecasts(self):
        """Test getting recent forecasts."""
        result = _get_recent_forecasts()
        
        # Verify structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
        assert all(result['series'] == 'cpi_annual')
        assert all(result['source'] == 'Statement on Monetary Policy')
        
        # Check values are reasonable
        assert all(result['value'] > 0)
        assert all(result['value'] < 10)  # Inflation shouldn't be > 10%


class TestScrapeLatestForecasts:
    """Test the _scrape_latest_forecasts function."""
    
    def test_scrape_latest_forecasts(self):
        """Test scraping latest forecasts."""
        result = _scrape_latest_forecasts()
        
        # Verify structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'forecast_date' in result.columns
        assert 'series' in result.columns
        assert 'value' in result.columns
        
        # Check we have multiple series
        unique_series = result['series'].unique()
        assert len(unique_series) > 1
        assert 'gdp_change' in unique_series
        assert 'cpi_annual' in unique_series
        assert 'unemp_rate' in unique_series
        
        # Check date range
        assert result['date'].min() >= pd.Timestamp('2024-01-01')
        assert result['date'].max() <= pd.Timestamp('2030-01-01')
        
        # Check values are reasonable
        gdp_values = result[result['series'] == 'gdp_change']['value']
        assert all(gdp_values > 0)
        assert all(gdp_values < 10)
        
        unemp_values = result[result['series'] == 'unemp_rate']['value']
        assert all(unemp_values > 0)
        assert all(unemp_values < 15)


class TestYearQtrCalculation:
    """Test year_qtr calculation."""
    
    @patch('rbadata.forecasts.check_rba_connection')
    @patch('rbadata.forecasts._get_historical_forecasts')
    @patch('rbadata.forecasts._get_recent_forecasts')
    @patch('rbadata.forecasts._scrape_latest_forecasts')
    def test_year_qtr_calculation(self, mock_scrape, mock_recent, mock_hist, mock_check):
        """Test that year_qtr is calculated correctly."""
        # Setup mocks
        mock_check.return_value = None
        mock_hist.return_value = pd.DataFrame()
        mock_scrape.return_value = pd.DataFrame()
        
        # Create data with known dates
        test_data = pd.DataFrame({
            'forecast_date': [pd.Timestamp('2023-05-01')] * 4,
            'date': [
                pd.Timestamp('2023-03-31'),  # Q1
                pd.Timestamp('2023-06-30'),  # Q2
                pd.Timestamp('2023-09-30'),  # Q3
                pd.Timestamp('2023-12-31'),  # Q4
            ],
            'series': ['test'] * 4,
            'value': [1, 2, 3, 4],
            'series_desc': ['Test'] * 4,
            'source': ['Test'] * 4,
            'notes': [None] * 4
        })
        mock_recent.return_value = test_data
        
        # Call function
        result = rba_forecasts()
        
        # Verify year_qtr values
        expected_year_qtr = [2023.0, 2023.25, 2023.5, 2023.75]
        assert list(result['year_qtr']) == expected_year_qtr