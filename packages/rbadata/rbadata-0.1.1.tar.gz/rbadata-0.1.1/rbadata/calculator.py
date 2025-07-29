"""
Inflation calculator functionality using RBA CPI data
"""

from typing import Union, Optional, Literal
import pandas as pd
from datetime import datetime
from .core import read_rba
from .exceptions import RBADataError


class InflationCalculator:
    """
    Calculate inflation and purchasing power changes using RBA CPI data.
    
    This calculator uses the Consumer Price Index (CPI) data to calculate
    the change in purchasing power of money over time in Australia.
    
    Examples
    --------
    >>> calc = InflationCalculator()
    >>> # Calculate how much $100 in 2000 is worth in 2023
    >>> calc.calculate_value(100, "2000", "2023")
    
    >>> # Calculate inflation rate between two periods
    >>> calc.calculate_inflation_rate("2020-Q1", "2023-Q1")
    """
    
    def __init__(self):
        """Initialize the calculator and load CPI data."""
        self._cpi_data = None
        self._load_cpi_data()
    
    def _load_cpi_data(self):
        """Load CPI data from RBA."""
        try:
            # Load CPI data from table G1
            df = read_rba(series_id="GCPIAG")
            
            # Ensure data is sorted by date
            df = df.sort_values("date")
            
            # Store as a series indexed by date
            self._cpi_data = df.set_index("date")["value"]
            
        except Exception as e:
            raise RBADataError(f"Failed to load CPI data: {str(e)}")
    
    def calculate_value(
        self,
        amount: float,
        from_period: Union[str, datetime],
        to_period: Union[str, datetime],
        round_result: bool = True
    ) -> float:
        """
        Calculate the equivalent value of money between two periods.
        
        Parameters
        ----------
        amount : float
            The amount of money in the from_period
        from_period : str or datetime
            The starting period (e.g., "2000", "2000-Q1", "2000-03-31")
        to_period : str or datetime
            The ending period (e.g., "2023", "2023-Q1", "2023-03-31")
        round_result : bool, default True
            Whether to round the result to 2 decimal places
            
        Returns
        -------
        float
            The equivalent value in the to_period
            
        Examples
        --------
        >>> calc = InflationCalculator()
        >>> # $100 in 2000 to 2023 dollars
        >>> calc.calculate_value(100, "2000", "2023")
        167.89
        """
        # Parse periods
        from_date = self._parse_period(from_period)
        to_date = self._parse_period(to_period)
        
        # Get CPI values
        from_cpi = self._get_cpi_value(from_date)
        to_cpi = self._get_cpi_value(to_date)
        
        # Calculate equivalent value
        result = amount * (to_cpi / from_cpi)
        
        if round_result:
            return round(result, 2)
        return result
    
    def calculate_inflation_rate(
        self,
        from_period: Union[str, datetime],
        to_period: Union[str, datetime],
        annualized: bool = True
    ) -> float:
        """
        Calculate the inflation rate between two periods.
        
        Parameters
        ----------
        from_period : str or datetime
            The starting period
        to_period : str or datetime
            The ending period
        annualized : bool, default True
            Whether to annualize the inflation rate
            
        Returns
        -------
        float
            The inflation rate as a percentage
            
        Examples
        --------
        >>> calc = InflationCalculator()
        >>> # Inflation rate from 2020 to 2023
        >>> calc.calculate_inflation_rate("2020", "2023")
        5.47
        """
        # Parse periods
        from_date = self._parse_period(from_period)
        to_date = self._parse_period(to_period)
        
        # Get CPI values
        from_cpi = self._get_cpi_value(from_date)
        to_cpi = self._get_cpi_value(to_date)
        
        # Calculate total inflation
        total_inflation = ((to_cpi / from_cpi) - 1) * 100
        
        if annualized and from_date != to_date:
            # Calculate years between dates
            years = (to_date - from_date).days / 365.25
            
            # Annualize the rate
            annualized_rate = ((to_cpi / from_cpi) ** (1 / years) - 1) * 100
            return round(annualized_rate, 2)
        
        return round(total_inflation, 2)
    
    def get_cpi_series(
        self,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None
    ) -> pd.Series:
        """
        Get the CPI series for a date range.
        
        Parameters
        ----------
        start_date : str or datetime, optional
            Start date for the series
        end_date : str or datetime, optional
            End date for the series
            
        Returns
        -------
        pd.Series
            CPI values indexed by date
        """
        series = self._cpi_data.copy()
        
        if start_date:
            start = self._parse_period(start_date)
            series = series[series.index >= start]
        
        if end_date:
            end = self._parse_period(end_date)
            series = series[series.index <= end]
        
        return series
    
    def _parse_period(self, period: Union[str, datetime]) -> pd.Timestamp:
        """Parse various period formats into a timestamp."""
        if isinstance(period, (datetime, pd.Timestamp)):
            return pd.Timestamp(period)
        
        # Handle year-only format (e.g., "2000")
        if len(str(period)) == 4 and str(period).isdigit():
            # Use Q4 (December) for year-only inputs
            return pd.Timestamp(f"{period}-12-31")
        
        # Handle quarter format (e.g., "2000-Q1")
        if "-Q" in str(period):
            year, quarter = period.split("-Q")
            quarter_month = {
                "1": "03-31",
                "2": "06-30", 
                "3": "09-30",
                "4": "12-31"
            }
            return pd.Timestamp(f"{year}-{quarter_month[quarter]}")
        
        # Try pandas parser
        try:
            return pd.Timestamp(period)
        except:
            raise RBADataError(f"Could not parse period: {period}")
    
    def _get_cpi_value(self, date: pd.Timestamp) -> float:
        """Get CPI value for a specific date, with interpolation if needed."""
        if date in self._cpi_data.index:
            return self._cpi_data[date]
        
        # Find nearest dates
        before_dates = self._cpi_data[self._cpi_data.index <= date]
        after_dates = self._cpi_data[self._cpi_data.index >= date]
        
        if len(before_dates) == 0:
            raise RBADataError(f"No CPI data available before {date}")
        
        if len(after_dates) == 0:
            # Use the last available value
            return before_dates.iloc[-1]
        
        # Linear interpolation between nearest points
        before_date = before_dates.index[-1]
        after_date = after_dates.index[0]
        before_value = before_dates.iloc[-1]
        after_value = after_dates.iloc[0]
        
        # Calculate interpolated value
        total_days = (after_date - before_date).days
        days_from_before = (date - before_date).days
        
        if total_days == 0:
            return before_value
        
        weight = days_from_before / total_days
        return before_value + (after_value - before_value) * weight


def inflation_calculator(
    amount: float,
    from_period: Union[str, datetime],
    to_period: Union[str, datetime]
) -> float:
    """
    Convenience function to calculate inflation-adjusted values.
    
    Parameters
    ----------
    amount : float
        The amount of money in the from_period
    from_period : str or datetime
        The starting period (e.g., "2000", "2000-Q1", "2000-03-31")
    to_period : str or datetime
        The ending period (e.g., "2023", "2023-Q1", "2023-03-31")
        
    Returns
    -------
    float
        The equivalent value in the to_period
        
    Examples
    --------
    >>> # $100 in 2000 to 2023 dollars
    >>> inflation_calculator(100, "2000", "2023")
    167.89
    """
    calc = InflationCalculator()
    return calc.calculate_value(amount, from_period, to_period)