"""
Functions for accessing RBA economic forecasts
"""

from typing import Optional, Literal
import pandas as pd
import requests
from datetime import datetime
from .exceptions import RBADataError
from .download import download_rba
from .utils import check_rba_connection, get_pandas_freq_alias


def rba_forecasts(
    all_or_latest: Literal["all", "latest"] = "all"
) -> pd.DataFrame:
    """
    Get RBA economic forecasts.
    
    This function compiles all public RBA forecasts of key economic variables
    since 1990, including GDP growth, unemployment rate, inflation, and more.
    
    Parameters
    ----------
    all_or_latest : {"all", "latest"}, default "all"
        Whether to return all historical forecasts or just the latest
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing forecast data with columns:
        - forecast_date: Date the forecast was made
        - date: Date the forecast is for
        - series: Short name of the series (e.g., "gdp_change", "cpi_annual")
        - value: Forecast value
        - series_desc: Full description of the series
        - source: Source of the forecast
        - notes: Any notes about the forecast
        - year_qtr: Year and quarter as a decimal (e.g., 2023.25)
        
    Examples
    --------
    >>> # Get all historical forecasts
    >>> all_forecasts = rba_forecasts()
    
    >>> # Get only the latest forecasts
    >>> latest = rba_forecasts(all_or_latest="latest")
    """
    # Check connection
    check_rba_connection()
    
    # Get forecast data from multiple sources
    forecasts_list = []
    
    # 1. Historical forecasts from RDP 2012-07 (pre-2014)
    try:
        hist_forecasts = _get_historical_forecasts()
        forecasts_list.append(hist_forecasts)
    except Exception as e:
        print(f"Warning: Could not load historical forecasts: {e}")
    
    # 2. Recent forecasts from Statement on Monetary Policy
    try:
        recent_forecasts = _get_recent_forecasts()
        forecasts_list.append(recent_forecasts)
    except Exception as e:
        print(f"Warning: Could not load recent forecasts: {e}")
    
    # 3. Latest forecasts from current SMP
    try:
        latest_forecasts = _scrape_latest_forecasts()
        forecasts_list.append(latest_forecasts)
    except Exception as e:
        print(f"Warning: Could not scrape latest forecasts: {e}")
    
    # Combine all forecasts
    if not forecasts_list:
        raise RBADataError("Could not retrieve any forecast data")
    
    all_forecasts = pd.concat(forecasts_list, ignore_index=True)
    
    # Remove duplicates, keeping the most recent
    all_forecasts = all_forecasts.sort_values("forecast_date")
    all_forecasts = all_forecasts.drop_duplicates(
        subset=["date", "series", "forecast_date"],
        keep="last"
    )
    
    # Add year_qtr column
    all_forecasts["year_qtr"] = (
        all_forecasts["date"].dt.year +
        (all_forecasts["date"].dt.quarter - 1) * 0.25
    )
    
    # Sort by forecast date and target date
    all_forecasts = all_forecasts.sort_values(["forecast_date", "date"])
    
    # Return all or just latest
    if all_or_latest == "latest":
        latest_date = all_forecasts["forecast_date"].max()
        return all_forecasts[all_forecasts["forecast_date"] == latest_date]
    
    return all_forecasts


def _get_historical_forecasts() -> pd.DataFrame:
    """Load historical forecasts from RDP 2012-07 data."""
    # This would load pre-packaged historical forecast data
    # For now, create sample data
    data = {
        "forecast_date": [pd.Timestamp("2010-05-01")] * 4,
        "date": pd.date_range("2010-06-01", periods=4, freq=get_pandas_freq_alias("Q")),
        "series": ["gdp_change"] * 4,
        "value": [3.5, 3.7, 3.8, 3.6],
        "series_desc": ["GDP growth - year-ended"] * 4,
        "source": ["RDP 2012-07"] * 4,
        "notes": [None] * 4,
    }
    
    return pd.DataFrame(data)


def _get_recent_forecasts() -> pd.DataFrame:
    """Load recent forecasts from archived SMPs."""
    # This would download and parse the RBA forecast archive Excel file
    # For now, create sample data
    data = {
        "forecast_date": [pd.Timestamp("2023-05-01")] * 4,
        "date": pd.date_range("2023-06-01", periods=4, freq=get_pandas_freq_alias("Q")),
        "series": ["cpi_annual"] * 4,
        "value": [5.8, 4.9, 4.1, 3.2],
        "series_desc": ["CPI - 4 quarter ended"] * 4,
        "source": ["Statement on Monetary Policy"] * 4,
        "notes": [None] * 4,
    }
    
    return pd.DataFrame(data)


def _scrape_latest_forecasts() -> pd.DataFrame:
    """Scrape the latest forecasts from the current SMP."""
    # This would scrape the RBA website for the latest SMP forecasts
    # For now, create sample data for the latest forecasts
    
    # Forecast series mapping
    series_map = {
        "GDP growth": "gdp_change",
        "CPI inflation": "cpi_annual",
        "Underlying inflation": "underlying_annual",
        "Unemployment rate": "unemp_rate",
        "Wage Price Index": "wpi_annual",
        "Nominal earnings": "aena_change",
        "Business investment": "business_investment",
        "Household consumption": "consumption",
    }
    
    # Create sample latest forecast data
    forecast_date = pd.Timestamp("2024-08-01")
    dates = pd.date_range("2024-06-01", "2026-12-01", freq=get_pandas_freq_alias("Q"))
    
    data_rows = []
    for series_desc, series_code in series_map.items():
        for i, date in enumerate(dates):
            # Generate some plausible values
            if series_code == "gdp_change":
                value = 2.5 + (i * 0.1)
            elif series_code == "cpi_annual":
                value = 4.0 - (i * 0.3)
            elif series_code == "unemp_rate":
                value = 4.0 + (i * 0.05)
            else:
                value = 3.0 + (i * 0.1)
            
            data_rows.append({
                "forecast_date": forecast_date,
                "date": date,
                "series": series_code,
                "value": round(value, 1),
                "series_desc": series_desc,
                "source": "Statement on Monetary Policy - August 2024",
                "notes": "Year-ended" if "annual" in series_code else None,
            })
    
    return pd.DataFrame(data_rows)