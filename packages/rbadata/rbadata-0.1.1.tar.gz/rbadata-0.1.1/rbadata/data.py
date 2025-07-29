"""
Data management for RBA table and series information
"""

import json
import pandas as pd
from pathlib import Path
from typing import Optional
from .web_scraper import scrape_table_list


# Cache for table and series data
_table_cache = None
_series_cache = None


def get_table_list(refresh: bool = False) -> pd.DataFrame:
    """
    Get the list of available RBA tables.
    
    Parameters
    ----------
    refresh : bool
        Whether to refresh the table list from the RBA website
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing table information
    """
    global _table_cache
    
    if _table_cache is not None and not refresh:
        return _table_cache
    
    # Try to load from package data
    data_file = Path(__file__).parent / "data" / "table_list.json"
    
    if data_file.exists() and not refresh:
        with open(data_file, "r") as f:
            data = json.load(f)
        _table_cache = pd.DataFrame(data)
    else:
        # Scrape from RBA website
        _table_cache = scrape_table_list()
        
        # Save to package data if possible
        try:
            data_file.parent.mkdir(exist_ok=True)
            _table_cache.to_json(data_file, orient="records", indent=2)
        except:
            pass  # Ignore save errors
    
    return _table_cache


def get_series_list(refresh: bool = False) -> pd.DataFrame:
    """
    Get the list of available RBA data series.
    
    Parameters
    ----------
    refresh : bool
        Whether to refresh the series list
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing series information
    """
    global _series_cache
    
    if _series_cache is not None and not refresh:
        return _series_cache
    
    # Try to load from package data
    data_file = Path(__file__).parent / "data" / "series_list.json"
    
    if data_file.exists() and not refresh:
        with open(data_file, "r") as f:
            data = json.load(f)
        _series_cache = pd.DataFrame(data)
    else:
        # Build series list from table data
        _series_cache = _build_series_list()
        
        # Save to package data if possible
        try:
            data_file.parent.mkdir(exist_ok=True)
            _series_cache.to_json(data_file, orient="records", indent=2)
        except:
            pass  # Ignore save errors
    
    return _series_cache


def _build_series_list() -> pd.DataFrame:
    """
    Build a series list by downloading and parsing sample tables.
    
    This is a simplified version - in production, this would be more comprehensive.
    """
    # For now, return a minimal series list
    # In a full implementation, this would download and parse tables to extract series info
    series_data = [
        {
            "series_id": "GCPIAG",
            "series": "Consumer price index; All groups; Australia",
            "table_no": "G1",
            "table_title": "Consumer Price Inflation",
            "frequency": "Quarterly",
            "units": "Index",
            "cur_hist": "current",
            "series_type": "Original",
            "description": "Consumer price index for all groups in Australia"
        },
        {
            "series_id": "GLFSURSA", 
            "series": "Unemployment rate; Australia",
            "table_no": "H3",
            "table_title": "Labour Force",
            "frequency": "Monthly",
            "units": "Per cent",
            "cur_hist": "current", 
            "series_type": "Seasonally adjusted",
            "description": "Unemployment rate for Australia, seasonally adjusted"
        },
        {
            "series_id": "FIRMMCRT",
            "series": "Interbank overnight cash rate",
            "table_no": "F1.1",
            "table_title": "Interest Rates and Yields – Money Market",
            "frequency": "Daily",
            "units": "Per cent per annum",
            "cur_hist": "current",
            "series_type": "Original",
            "description": "RBA target cash rate"
        }
    ]
    
    return pd.DataFrame(series_data)