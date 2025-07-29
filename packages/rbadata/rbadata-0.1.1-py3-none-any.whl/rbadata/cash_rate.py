"""
Functions for accessing RBA cash rate data
"""

import pandas as pd
from datetime import datetime, timedelta
from .core import read_rba
from .exceptions import RBADataError


def read_cashrate(
    type: str = "target",
    start_date: pd.Timestamp = None,
    end_date: pd.Timestamp = None
) -> pd.DataFrame:
    """
    Read the RBA cash rate.
    
    Parameters
    ----------
    type : str, default "target"
        Type of cash rate to retrieve:
        - "target": RBA target cash rate
        - "interbank": Interbank overnight cash rate
    start_date : pd.Timestamp, optional
        Start date for the data
    end_date : pd.Timestamp, optional
        End date for the data
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing cash rate data with columns:
        - date: Date
        - value: Cash rate value (percent)
        - series: Description of the series
        
    Examples
    --------
    >>> # Get target cash rate
    >>> cash_rate = read_cashrate()
    
    >>> # Get interbank rate for 2023
    >>> interbank = read_cashrate(
    ...     type="interbank",
    ...     start_date="2023-01-01",
    ...     end_date="2023-12-31"
    ... )
    """
    # Map type to series ID
    if type == "target":
        series_id = "FIRMMCRT"  # Target cash rate
    elif type == "interbank":
        series_id = "FIRMMBAB30"  # Interbank overnight rate
    else:
        raise RBADataError(f"Invalid cash rate type: {type}")
    
    # Read the data
    df = read_rba(series_id=series_id)
    
    # Filter by date range if provided
    if start_date is not None:
        start_date = pd.to_datetime(start_date)
        df = df[df["date"] >= start_date]
    
    if end_date is not None:
        end_date = pd.to_datetime(end_date)
        df = df[df["date"] <= end_date]
    
    # Select relevant columns
    result = df[["date", "value", "series"]].copy()
    
    # Sort by date
    result = result.sort_values("date")
    
    return result