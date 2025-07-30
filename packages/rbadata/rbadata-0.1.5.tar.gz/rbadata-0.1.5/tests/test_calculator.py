"""
Tests for inflation calculator functionality
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from rbadata import InflationCalculator, inflation_calculator
from rbadata.utils import get_pandas_freq_alias
from rbadata.exceptions import RBADataError


class TestInflationCalculator:
    """Test the InflationCalculator class."""
    
    @patch('rbadata.calculator.read_rba')
    def test_calculator_init(self, mock_read_rba):
        """Test calculator initialization loads CPI data."""
        # Mock CPI data
        mock_cpi_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=12, freq=get_pandas_freq_alias("Q")),
            'value': [100.0 + i for i in range(12)],
            'series_id': ['GCPIAG'] * 12
        })
        mock_read_rba.return_value = mock_cpi_data
        
        # Create calculator
        calc = InflationCalculator()
        
        # Verify data was loaded
        mock_read_rba.assert_called_once_with(series_id="GCPIAG")
        assert len(calc._cpi_data) == 12
    
    @patch('rbadata.calculator.read_rba')
    def test_calculate_value(self, mock_read_rba):
        """Test value calculation between periods."""
        # Mock CPI data
        dates = [
            pd.Timestamp('2020-12-31'),
            pd.Timestamp('2021-12-31'),
            pd.Timestamp('2022-12-31'),
            pd.Timestamp('2023-12-31')
        ]
        mock_cpi_data = pd.DataFrame({
            'date': dates,
            'value': [100.0, 105.0, 110.0, 115.0],
            'series_id': ['GCPIAG'] * 4
        })
        mock_read_rba.return_value = mock_cpi_data
        
        calc = InflationCalculator()
        
        # Test calculation
        result = calc.calculate_value(100, "2020", "2023")
        assert result == 115.0  # 100 * (115/100)
        
        # Test with different amount
        result = calc.calculate_value(1000, "2021", "2022")
        assert result == 1047.62  # 1000 * (110/105) rounded to 2 decimals
    
    @patch('rbadata.calculator.read_rba')
    def test_calculate_inflation_rate(self, mock_read_rba):
        """Test inflation rate calculation."""
        # Mock CPI data
        dates = [
            pd.Timestamp('2020-12-31'),
            pd.Timestamp('2023-12-31')
        ]
        mock_cpi_data = pd.DataFrame({
            'date': dates,
            'value': [100.0, 115.0],
            'series_id': ['GCPIAG'] * 2
        })
        mock_read_rba.return_value = mock_cpi_data
        
        calc = InflationCalculator()
        
        # Test total inflation (not annualized)
        result = calc.calculate_inflation_rate("2020", "2023", annualized=False)
        assert result == 15.0  # ((115/100) - 1) * 100
        
        # Test annualized inflation
        result = calc.calculate_inflation_rate("2020", "2023", annualized=True)
        # Should be approximately 4.77% annualized over 3 years
        assert 4.5 < result < 5.0
    
    @patch('rbadata.calculator.read_rba')
    def test_parse_period_formats(self, mock_read_rba):
        """Test parsing of various period formats."""
        # Mock minimal CPI data
        mock_cpi_data = pd.DataFrame({
            'date': [pd.Timestamp('2020-03-31'), pd.Timestamp('2020-06-30')],
            'value': [100.0, 101.0],
            'series_id': ['GCPIAG'] * 2
        })
        mock_read_rba.return_value = mock_cpi_data
        
        calc = InflationCalculator()
        
        # Test year format
        result = calc._parse_period("2020")
        assert result == pd.Timestamp("2020-12-31")
        
        # Test quarter format
        result = calc._parse_period("2020-Q1")
        assert result == pd.Timestamp("2020-03-31")
        
        result = calc._parse_period("2020-Q2")
        assert result == pd.Timestamp("2020-06-30")
        
        # Test full date format
        result = calc._parse_period("2020-03-31")
        assert result == pd.Timestamp("2020-03-31")
    
    @patch('rbadata.calculator.read_rba')
    def test_get_cpi_series(self, mock_read_rba):
        """Test getting CPI series with date filtering."""
        # Mock CPI data
        mock_cpi_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=12, freq=get_pandas_freq_alias("Q")),
            'value': [100.0 + i for i in range(12)],
            'series_id': ['GCPIAG'] * 12
        })
        mock_read_rba.return_value = mock_cpi_data
        
        calc = InflationCalculator()
        
        # Get full series
        series = calc.get_cpi_series()
        assert len(series) == 12
        
        # Get filtered series
        series = calc.get_cpi_series(
            start_date="2020-07-01",
            end_date="2021-12-31"
        )
        assert len(series) < 12
        assert series.index[0] >= pd.Timestamp("2020-07-01")
    
    @patch('rbadata.calculator.read_rba')
    def test_interpolation(self, mock_read_rba):
        """Test CPI value interpolation for missing dates."""
        # Mock CPI data with quarterly values
        dates = [
            pd.Timestamp('2020-03-31'),
            pd.Timestamp('2020-06-30'),
        ]
        mock_cpi_data = pd.DataFrame({
            'date': dates,
            'value': [100.0, 102.0],
            'series_id': ['GCPIAG'] * 2
        })
        mock_read_rba.return_value = mock_cpi_data
        
        calc = InflationCalculator()
        
        # Get interpolated value for mid-quarter date
        mid_date = pd.Timestamp('2020-05-15')
        value = calc._get_cpi_value(mid_date)
        
        # Should be between 100 and 102
        assert 100.0 < value < 102.0
        # Roughly in the middle
        assert 100.5 < value < 101.5


class TestInflationCalculatorConvenience:
    """Test convenience functions."""
    
    @patch('rbadata.calculator.InflationCalculator')
    def test_inflation_calculator_function(self, mock_calculator_class):
        """Test the convenience function."""
        # Mock calculator instance
        mock_instance = MagicMock()
        mock_instance.calculate_value.return_value = 150.0
        mock_calculator_class.return_value = mock_instance
        
        # Call convenience function
        result = inflation_calculator(100, "2000", "2020")
        
        # Verify
        assert result == 150.0
        mock_instance.calculate_value.assert_called_once_with(100, "2000", "2020")