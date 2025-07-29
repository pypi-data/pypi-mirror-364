"""
Core functions for reading RBA data
"""

from typing import List, Optional, Union
import pandas as pd
from .download import download_rba
from .tidy import tidy_rba
from .utils import get_rba_urls, check_rba_connection, tables_from_seriesid
from .exceptions import RBADataError


def read_rba(
    table_no: Optional[Union[str, List[str]]] = None,
    series_id: Optional[Union[str, List[str]]] = None,
    cur_hist: str = "current",
) -> pd.DataFrame:
    """
    Download and tidy data from the Reserve Bank of Australia.
    
    Parameters
    ----------
    table_no : str or list of str, optional
        RBA table number(s) to download (e.g., "a1", "g1", ["a1", "g1"])
    series_id : str or list of str, optional
        RBA series ID(s) to download (e.g., "GCPIAG")
    cur_hist : str, default "current"
        Whether to download "current" or "historical" tables
        
    Returns
    -------
    pd.DataFrame
        A tidy DataFrame containing the requested RBA data
        
    Raises
    ------
    RBADataError
        If neither table_no nor series_id is provided
        If the requested data cannot be downloaded
        
    Examples
    --------
    >>> # Read a single table
    >>> df = read_rba(table_no="g1")
    
    >>> # Read multiple tables
    >>> df = read_rba(table_no=["a1", "g1"])
    
    >>> # Read by series ID
    >>> df = read_rba(series_id="GCPIAG")
    """
    # Check internet connection
    check_rba_connection()
    
    # Validate inputs
    if table_no is None and series_id is None:
        raise RBADataError("Either 'table_no' or 'series_id' must be specified")
    
    if table_no is not None and series_id is not None:
        raise RBADataError("Only one of 'table_no' or 'series_id' should be specified")
    
    # Handle series_id input
    if series_id is not None:
        # Convert series_id to list if string
        if isinstance(series_id, str):
            series_id = [series_id]
        
        # Map series IDs to table numbers
        table_mapping = tables_from_seriesid(series_id)
        table_no = list(table_mapping.keys())
        
    # Convert table_no to list if string
    if isinstance(table_no, str):
        table_no = [table_no]
    
    # Get URLs for each table
    urls = get_rba_urls(table_no, cur_hist)
    
    # Download and tidy each table
    all_data = []
    for table, url in zip(table_no, urls):
        # Download the Excel file
        excel_path = download_rba(url, table)
        
        # Tidy the data
        df = tidy_rba(excel_path, table, url, cur_hist)
        
        # Filter by series_id if provided
        if series_id is not None:
            df = df[df["series_id"].isin(series_id)]
        
        all_data.append(df)
    
    # Combine all DataFrames
    result = pd.concat(all_data, ignore_index=True)
    
    # Sort by date
    result = result.sort_values(["date", "series_id"])
    
    return result


def read_rba_seriesid(series_id: Union[str, List[str]]) -> pd.DataFrame:
    """
    Convenience function to download RBA data by series ID.
    
    This is equivalent to calling read_rba(series_id=series_id).
    
    Parameters
    ----------
    series_id : str or list of str
        RBA series ID(s) to download
        
    Returns
    -------
    pd.DataFrame
        A tidy DataFrame containing the requested RBA data
        
    Examples
    --------
    >>> df = read_rba_seriesid("GCPIAG")
    >>> df = read_rba_seriesid(["GCPIAG", "GLFSURSA"])
    """
    return read_rba(series_id=series_id)