"""
Tests for the cash_rate module
"""

import pytest
import pandas as pd
from unittest.mock import patch, Mock
from datetime import datetime
from rbadata.cash_rate import read_cashrate
from rbadata.utils import get_pandas_freq_alias
from rbadata.exceptions import RBADataError


class TestReadCashRate:
    """Test the read_cashrate function."""
    
    @patch('rbadata.cash_rate.read_rba')
    def test_read_cashrate_target_default(self, mock_read_rba):
        """Test reading target cash rate (default)."""
        # Setup mock data
        mock_data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=5, freq=get_pandas_freq_alias("M")),
            'value': [3.10, 3.35, 3.60, 3.60, 3.85],
            'series': ['Cash Rate Target'] * 5,
            'series_id': ['FIRMMCRT'] * 5,
            'table_no': ['A2'] * 5
        })
        mock_read_rba.return_value = mock_data
        
        # Call function
        result = read_cashrate()
        
        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        assert list(result.columns) == ['date', 'value', 'series']
        mock_read_rba.assert_called_once_with(series_id='FIRMMCRT')
        
        # Check data
        assert result['value'].iloc[0] == 3.10
        assert result['value'].iloc[-1] == 3.85
    
    @patch('rbadata.cash_rate.read_rba')
    def test_read_cashrate_interbank(self, mock_read_rba):
        """Test reading interbank cash rate."""
        # Setup mock data
        mock_data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=5, freq='D'),
            'value': [3.08, 3.09, 3.11, 3.10, 3.12],
            'series': ['Interbank Overnight'] * 5,
            'series_id': ['FIRMMBAB30'] * 5,
            'table_no': ['F1'] * 5
        })
        mock_read_rba.return_value = mock_data
        
        # Call function
        result = read_cashrate(type='interbank')
        
        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        mock_read_rba.assert_called_once_with(series_id='FIRMMBAB30')
    
    def test_read_cashrate_invalid_type(self):
        """Test error with invalid cash rate type."""
        with pytest.raises(RBADataError, match="Invalid cash rate type: invalid"):
            read_cashrate(type='invalid')
    
    @patch('rbadata.cash_rate.read_rba')
    def test_read_cashrate_with_date_filter(self, mock_read_rba):
        """Test filtering by date range."""
        # Setup mock data
        mock_data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=12, freq=get_pandas_freq_alias("M")),
            'value': list(range(12)),
            'series': ['Cash Rate Target'] * 12,
            'series_id': ['FIRMMCRT'] * 12,
            'table_no': ['A2'] * 12
        })
        mock_read_rba.return_value = mock_data
        
        # Call with date filter
        result = read_cashrate(
            start_date='2023-03-01',
            end_date='2023-06-30'
        )
        
        # Verify filtering
        assert len(result) == 4  # March, April, May, June
        assert result['date'].min() >= pd.Timestamp('2023-03-01')
        assert result['date'].max() <= pd.Timestamp('2023-06-30')
    
    @patch('rbadata.cash_rate.read_rba')
    def test_read_cashrate_start_date_only(self, mock_read_rba):
        """Test filtering with only start date."""
        # Setup mock data
        mock_data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=12, freq=get_pandas_freq_alias("M")),
            'value': list(range(12)),
            'series': ['Cash Rate Target'] * 12,
            'series_id': ['FIRMMCRT'] * 12,
            'table_no': ['A2'] * 12
        })
        mock_read_rba.return_value = mock_data
        
        # Call with start date only
        result = read_cashrate(start_date='2023-06-01')
        
        # Verify filtering
        assert len(result) == 7  # June through December
        assert result['date'].min() >= pd.Timestamp('2023-06-01')
    
    @patch('rbadata.cash_rate.read_rba')
    def test_read_cashrate_end_date_only(self, mock_read_rba):
        """Test filtering with only end date."""
        # Setup mock data
        mock_data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=12, freq=get_pandas_freq_alias("M")),
            'value': list(range(12)),
            'series': ['Cash Rate Target'] * 12,
            'series_id': ['FIRMMCRT'] * 12,
            'table_no': ['A2'] * 12
        })
        mock_read_rba.return_value = mock_data
        
        # Call with end date only
        result = read_cashrate(end_date='2023-03-31')
        
        # Verify filtering
        assert len(result) == 3  # January, February, March
        assert result['date'].max() <= pd.Timestamp('2023-03-31')
    
    @patch('rbadata.cash_rate.read_rba')
    def test_read_cashrate_date_formats(self, mock_read_rba):
        """Test various date input formats."""
        # Setup mock data
        mock_data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=365, freq='D'),
            'value': list(range(365)),
            'series': ['Cash Rate Target'] * 365,
            'series_id': ['FIRMMCRT'] * 365,
            'table_no': ['A2'] * 365
        })
        mock_read_rba.return_value = mock_data
        
        # Test string date
        result1 = read_cashrate(start_date='2023-03-01', end_date='2023-03-31')
        assert len(result1) == 31
        
        # Test datetime object
        result2 = read_cashrate(
            start_date=datetime(2023, 3, 1),
            end_date=datetime(2023, 3, 31)
        )
        assert len(result2) == 31
        
        # Test pandas Timestamp
        result3 = read_cashrate(
            start_date=pd.Timestamp('2023-03-01'),
            end_date=pd.Timestamp('2023-03-31')
        )
        assert len(result3) == 31
    
    @patch('rbadata.cash_rate.read_rba')
    def test_read_cashrate_sorting(self, mock_read_rba):
        """Test that results are sorted by date."""
        # Setup mock data with unsorted dates
        dates = pd.date_range('2023-01-01', periods=5, freq='D')
        shuffled_dates = [dates[2], dates[0], dates[4], dates[1], dates[3]]
        
        mock_data = pd.DataFrame({
            'date': shuffled_dates,
            'value': [2, 0, 4, 1, 3],
            'series': ['Cash Rate Target'] * 5,
            'series_id': ['FIRMMCRT'] * 5,
            'table_no': ['A2'] * 5
        })
        mock_read_rba.return_value = mock_data
        
        # Call function
        result = read_cashrate()
        
        # Verify sorting
        assert list(result['value']) == [0, 1, 2, 3, 4]
        assert result['date'].is_monotonic_increasing
    
    @patch('rbadata.cash_rate.read_rba')
    def test_read_cashrate_empty_result(self, mock_read_rba):
        """Test handling of empty result after filtering."""
        # Setup mock data
        mock_data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=5, freq=get_pandas_freq_alias("M")),
            'value': list(range(5)),
            'series': ['Cash Rate Target'] * 5,
            'series_id': ['FIRMMCRT'] * 5,
            'table_no': ['A2'] * 5
        })
        mock_read_rba.return_value = mock_data
        
        # Call with date range that excludes all data
        result = read_cashrate(start_date='2024-01-01')
        
        # Verify empty result
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ['date', 'value', 'series']


class TestCashRateIntegration:
    """Integration tests for cash rate functionality."""
    
    @patch('rbadata.cash_rate.read_rba')
    def test_cashrate_real_world_scenario(self, mock_read_rba):
        """Test a realistic scenario with actual cash rate values."""
        # Setup realistic cash rate data
        dates = pd.date_range('2022-01-01', '2023-12-31', freq='MS')
        # Realistic cash rate progression during rate hike cycle
        values = [
            0.10, 0.10, 0.10, 0.10, 0.35,  # 2022 Jan-May
            0.85, 1.35, 1.85, 2.35, 2.60,  # 2022 Jun-Oct
            2.85, 3.10,                     # 2022 Nov-Dec
            3.10, 3.35, 3.60, 3.60, 3.85,  # 2023 Jan-May
            4.10, 4.10, 4.10, 4.10, 4.10,  # 2023 Jun-Oct
            4.35, 4.35                      # 2023 Nov-Dec
        ]
        
        mock_data = pd.DataFrame({
            'date': dates,
            'value': values,
            'series': ['Cash Rate Target'] * len(dates),
            'series_id': ['FIRMMCRT'] * len(dates),
            'table_no': ['A2'] * len(dates)
        })
        mock_read_rba.return_value = mock_data
        
        # Get cash rate for rate hike period
        result = read_cashrate(
            start_date='2022-05-01',
            end_date='2023-06-30'
        )
        
        # Verify rate hikes captured
        assert result['value'].iloc[0] == 0.35  # First hike in May 2022
        assert result['value'].iloc[-1] == 4.10  # Peak rate
        assert result['value'].max() == 4.10
        
        # Check monotonic increase (mostly)
        value_changes = result['value'].diff().dropna()
        assert (value_changes >= 0).sum() > len(value_changes) * 0.9  # Most changes are increases