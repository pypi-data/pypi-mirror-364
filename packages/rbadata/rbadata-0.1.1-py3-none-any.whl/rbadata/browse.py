"""
Functions for browsing and searching RBA data
"""

from typing import Optional
import pandas as pd
from .data import get_table_list, get_series_list


def browse_rba_tables(
    search: Optional[str] = None,
    refresh: bool = False
) -> pd.DataFrame:
    """
    Browse available RBA tables.
    
    Parameters
    ----------
    search : str, optional
        Search string to filter tables
    refresh : bool, default False
        Whether to refresh the table list from the RBA website
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing table information
        
    Examples
    --------
    >>> # Get all tables
    >>> tables = browse_rba_tables()
    
    >>> # Search for inflation tables
    >>> inflation_tables = browse_rba_tables("inflation")
    """
    tables = get_table_list(refresh=refresh)
    
    if search:
        # Case-insensitive search in title
        mask = tables["title"].str.contains(search, case=False, na=False)
        tables = tables[mask]
    
    # Sort by table number
    tables = tables.sort_values("no")
    
    # Return the dataframe as-is
    return tables


def browse_rba_series(
    search: Optional[str] = None,
    table_no: Optional[str] = None,
    refresh: bool = False
) -> pd.DataFrame:
    """
    Browse available RBA data series.
    
    Parameters
    ----------
    search : str, optional
        Search string to filter series
    table_no : str, optional
        Filter by specific table number
    refresh : bool, default False
        Whether to refresh the series list
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing series information
        
    Examples
    --------
    >>> # Get all series
    >>> series = browse_rba_series()
    
    >>> # Search for unemployment series
    >>> unemployment = browse_rba_series("unemployment")
    
    >>> # Get all series from table G1
    >>> g1_series = browse_rba_series(table_no="G1")
    """
    series = get_series_list(refresh=refresh)
    
    if search:
        # Case-insensitive search in series name and description
        mask = (
            series["series"].str.contains(search, case=False, na=False) |
            series["description"].str.contains(search, case=False, na=False)
        )
        series = series[mask]
    
    if table_no:
        # Filter by table number
        series = series[series["table_no"] == table_no.upper()]
    
    # Sort by table number and series ID
    series = series.sort_values(["table_no", "series_id"])
    
    return series