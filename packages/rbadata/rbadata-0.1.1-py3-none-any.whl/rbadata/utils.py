"""
Utility functions for rbadata
"""

from typing import Dict, List, Optional, Union
import re
from datetime import datetime
import pandas as pd
import requests
from .exceptions import RBADataError
from .data import get_table_list, get_series_list


def get_rba_urls(table_nos: List[str], cur_hist: str = "current") -> List[str]:
    """
    Get URLs for RBA tables.
    
    Parameters
    ----------
    table_nos : list of str
        Table numbers to get URLs for
    cur_hist : str
        Whether to get "current" or "historical" URLs
        
    Returns
    -------
    list of str
        URLs for each table
    """
    table_list = get_table_list()
    
    # Filter by current/historical
    table_list = table_list[table_list["current_or_historical"] == cur_hist]
    
    urls = []
    for table_no in table_nos:
        # Normalize table number
        table_no = table_no.upper()
        
        # Find matching table
        matches = table_list[table_list["no"] == table_no]
        
        if len(matches) == 0:
            raise RBADataError(f"Table '{table_no}' not found in RBA table list")
        
        url = matches.iloc[0]["url"]
        urls.append(url)
    
    return urls


def check_rba_connection():
    """
    Check if we can connect to the RBA website.
    
    Raises
    ------
    RBADataError
        If connection cannot be established
    """
    try:
        response = requests.head("https://www.rba.gov.au", timeout=5)
        if response.status_code >= 400:
            raise RBADataError("Cannot connect to RBA website")
    except requests.RequestException:
        raise RBADataError(
            "No internet connection or RBA website is unreachable. "
            "Please check your internet connection."
        )


def tables_from_seriesid(series_ids: List[str]) -> Dict[str, List[str]]:
    """
    Map series IDs to their corresponding table numbers.
    
    Parameters
    ----------
    series_ids : list of str
        Series IDs to map
        
    Returns
    -------
    dict
        Mapping from table number to list of series IDs
    """
    series_list = get_series_list()
    
    table_map = {}
    for series_id in series_ids:
        # Find matching series
        matches = series_list[series_list["series_id"] == series_id]
        
        if len(matches) == 0:
            raise RBADataError(f"Series ID '{series_id}' not found")
        
        # Get table number(s) for this series
        for _, row in matches.iterrows():
            table_no = row["table_no"]
            if table_no not in table_map:
                table_map[table_no] = []
            table_map[table_no].append(series_id)
    
    return table_map


def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse various date string formats used by RBA.
    
    Parameters
    ----------
    date_str : str
        Date string to parse
        
    Returns
    -------
    datetime or None
        Parsed datetime object, or None if parsing fails
    """
    # Common RBA date formats
    formats = [
        "%d-%b-%Y",  # 01-Jan-2020
        "%d %B %Y",  # 01 January 2020
        "%b-%Y",     # Jan-2020
        "%B %Y",     # January 2020
        "%Y-%m-%d",  # 2020-01-01
        "%d/%m/%Y",  # 01/01/2020
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    # Try pandas parser as fallback
    try:
        return pd.to_datetime(date_str)
    except:
        return None


def is_rba_ts_format(df: pd.DataFrame) -> bool:
    """
    Check if a DataFrame appears to be in RBA time series format.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to check
        
    Returns
    -------
    bool
        True if the DataFrame looks like RBA time series data
    """
    if df.empty or df.shape[1] < 2:
        return False
    
    # Check for date-like values in first column
    first_col = df.iloc[:, 0]
    date_count = 0
    
    for val in first_col.dropna().head(20):
        if _is_potential_date(val):
            date_count += 1
    
    # If more than 30% of values look like dates, it's probably time series
    return date_count > len(first_col.dropna().head(20)) * 0.3


def _is_potential_date(value) -> bool:
    """Check if a value could be a date."""
    if pd.isna(value):
        return False
    
    # Check if it's already a datetime
    if isinstance(value, (datetime, pd.Timestamp)):
        return True
    
    # Check string patterns
    str_val = str(value)
    
    # Year patterns
    if re.match(r"^(19|20)\d{2}", str_val):
        return True
    
    # Month names
    months = ["jan", "feb", "mar", "apr", "may", "jun",
              "jul", "aug", "sep", "oct", "nov", "dec"]
    
    if any(month in str_val.lower() for month in months):
        return True
    
    # Quarter patterns
    if re.match(r"^Q[1-4]", str_val, re.IGNORECASE):
        return True
    
    return False


def get_pandas_freq_alias(freq_type: str) -> str:
    """
    Get the appropriate pandas frequency alias based on pandas version.
    
    Handles the change in frequency aliases between pandas < 2.0 and >= 2.0:
    - Quarter end: "Q" -> "QE"
    - Month end: "M" -> "ME"
    
    Parameters
    ----------
    freq_type : str
        The frequency type ("Q" or "M")
        
    Returns
    -------
    str
        The appropriate frequency alias for the current pandas version
    """
    try:
        # Parse version more carefully
        # Handle versions like '1.5.3', '2.0.0', '2.1.0rc0'
        version_str = pd.__version__.split('+')[0]  # Remove any '+' suffixes
        version_str = version_str.split('rc')[0]    # Remove release candidate suffixes
        version_parts = version_str.split('.')[:2]
        pd_version = tuple(int(x) for x in version_parts)
    except (ValueError, AttributeError):
        # If we can't parse the version, assume old pandas
        pd_version = (1, 0)
    
    if freq_type.upper() == "Q":
        return "QE" if pd_version >= (2, 0) else "Q"
    elif freq_type.upper() == "M":
        return "ME" if pd_version >= (2, 0) else "M"
    else:
        return freq_type