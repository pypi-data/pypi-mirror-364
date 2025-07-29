"""
Functions for tidying RBA data into a consistent format
"""

from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime
from .exceptions import RBADataError
from .utils import parse_date_string, is_rba_ts_format


def tidy_rba(
    filepath: Path,
    table_no: str,
    url: str,
    cur_hist: str = "current"
) -> pd.DataFrame:
    """
    Tidy an RBA Excel file into a standardized DataFrame format.
    
    Parameters
    ----------
    filepath : Path
        Path to the Excel file
    table_no : str
        RBA table number
    url : str
        Source URL of the data
    cur_hist : str
        Whether this is a "current" or "historical" table
        
    Returns
    -------
    pd.DataFrame
        Tidy DataFrame with standardized columns
    """
    # Read Excel file to get sheet names
    xl_file = pd.ExcelFile(filepath)
    sheet_names = xl_file.sheet_names
    
    # Special handling for certain tables
    if table_no.lower() in ["a1.1", "a3"]:
        # These tables have a different structure
        return _tidy_special_table(xl_file, table_no, url, cur_hist)
    
    # Process each sheet
    all_data = []
    for sheet_name in sheet_names:
        # Skip metadata sheets
        if sheet_name.lower() in ["notes", "series breaks"]:
            continue
            
        # Read the sheet
        df = pd.read_excel(xl_file, sheet_name=sheet_name, header=None)
        
        # Check if it's in RBA time series format
        if not is_rba_ts_format(df):
            continue
        
        # Tidy the sheet
        tidy_df = _tidy_normal_sheet(df, sheet_name, table_no, url, cur_hist)
        all_data.append(tidy_df)
    
    # Combine all sheets
    if not all_data:
        raise RBADataError(f"No valid data found in table {table_no}")
    
    result = pd.concat(all_data, ignore_index=True)
    return result


def _tidy_normal_sheet(
    df: pd.DataFrame,
    sheet_name: str,
    table_no: str,
    url: str,
    cur_hist: str
) -> pd.DataFrame:
    """
    Tidy a normal RBA time series sheet.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame from Excel
    sheet_name : str
        Name of the Excel sheet
    table_no : str
        RBA table number
    url : str
        Source URL
    cur_hist : str
        Current or historical indicator
        
    Returns
    -------
    pd.DataFrame
        Tidy DataFrame
    """
    # Find the header rows
    header_row = _find_header_row(df)
    
    # Extract metadata
    metadata = _extract_metadata(df, header_row)
    
    # Extract the data
    data_df = df.iloc[header_row:].reset_index(drop=True)
    
    # Set column names from the first row
    data_df.columns = data_df.iloc[0]
    data_df = data_df.iloc[1:].reset_index(drop=True)
    
    # Get date column (usually first column)
    date_col = data_df.columns[0]
    
    # Melt the DataFrame to long format
    value_vars = [col for col in data_df.columns if col != date_col]
    
    long_df = pd.melt(
        data_df,
        id_vars=[date_col],
        value_vars=value_vars,
        var_name="series",
        value_name="value"
    )
    
    # Rename date column
    long_df = long_df.rename(columns={date_col: "date"})
    
    # Convert date column
    long_df["date"] = pd.to_datetime(long_df["date"], errors="coerce")
    
    # Convert value column to numeric
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
    
    # Remove rows with missing dates or values
    long_df = long_df.dropna(subset=["date", "value"])
    
    # Add metadata columns
    long_df["table_no"] = table_no
    long_df["sheet_name"] = sheet_name
    long_df["table_title"] = metadata.get("title", "")
    long_df["frequency"] = metadata.get("frequency", "")
    long_df["units"] = metadata.get("units", "")
    long_df["source"] = metadata.get("source", "RBA")
    long_df["pub_date"] = metadata.get("pub_date", pd.NaT)
    long_df["series_type"] = metadata.get("series_type", "Original")
    long_df["cur_hist"] = cur_hist
    
    # Extract series IDs from the original header
    series_id_map = _extract_series_ids(df, header_row)
    long_df["series_id"] = long_df["series"].map(series_id_map)
    
    # Add description (same as series name for now)
    long_df["description"] = long_df["series"]
    
    return long_df


def _find_header_row(df: pd.DataFrame) -> int:
    """
    Find the row containing column headers in an RBA Excel sheet.
    
    Usually this is the row that contains "Series ID" or dates.
    """
    for i in range(min(20, len(df))):
        row = df.iloc[i]
        row_str = " ".join([str(x) for x in row if pd.notna(x)])
        
        if "Series ID" in row_str or "series id" in row_str.lower():
            return i + 1  # Data starts after Series ID row
        
        # Check if this row contains dates
        date_count = sum(1 for x in row if _is_date_like(x))
        if date_count > len(row) * 0.3:  # More than 30% are dates
            return i
    
    # Default to row 10 if not found
    return 10


def _is_date_like(value) -> bool:
    """Check if a value looks like a date."""
    if pd.isna(value):
        return False
    
    # Check for datetime objects
    if isinstance(value, (datetime, pd.Timestamp)):
        return True
    
    # Check for date-like strings
    str_val = str(value)
    date_patterns = ["19", "20", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Q1", "Q2", "Q3", "Q4"]
    
    return any(pattern in str_val for pattern in date_patterns)


def _extract_metadata(df: pd.DataFrame, header_row: int) -> Dict[str, str]:
    """
    Extract metadata from the header rows of an RBA Excel sheet.
    """
    metadata = {}
    
    # Look for common metadata patterns in the first few rows
    for i in range(min(header_row, 10)):
        row = df.iloc[i]
        row_text = " ".join([str(x) for x in row if pd.notna(x)])
        
        # Title (usually in first row)
        if i == 0 and row_text:
            metadata["title"] = row_text.strip()
        
        # Frequency
        if "quarterly" in row_text.lower():
            metadata["frequency"] = "Quarterly"
        elif "monthly" in row_text.lower():
            metadata["frequency"] = "Monthly"
        elif "daily" in row_text.lower():
            metadata["frequency"] = "Daily"
        elif "weekly" in row_text.lower():
            metadata["frequency"] = "Weekly"
        elif "annual" in row_text.lower():
            metadata["frequency"] = "Annual"
        
        # Units
        if "per cent" in row_text.lower() or "%" in row_text:
            metadata["units"] = "Per cent"
        elif "$" in row_text:
            if "million" in row_text.lower():
                metadata["units"] = "$ million"
            elif "billion" in row_text.lower():
                metadata["units"] = "$ billion"
            else:
                metadata["units"] = "$"
        
        # Source
        if "source:" in row_text.lower():
            source_start = row_text.lower().find("source:") + 7
            metadata["source"] = row_text[source_start:].strip()
        
        # Publication date
        if "last updated:" in row_text.lower():
            date_start = row_text.lower().find("last updated:") + 13
            date_str = row_text[date_start:].strip()
            try:
                metadata["pub_date"] = pd.to_datetime(date_str)
            except:
                metadata["pub_date"] = pd.NaT
    
    return metadata


def _extract_series_ids(df: pd.DataFrame, header_row: int) -> Dict[str, str]:
    """
    Extract series IDs from the header area of an RBA Excel sheet.
    
    Returns a mapping from series name to series ID.
    """
    series_map = {}
    
    # Look for Series ID row
    for i in range(max(0, header_row - 5), header_row):
        row = df.iloc[i]
        row_str = " ".join([str(x) for x in row if pd.notna(x)])
        
        if "Series ID" in row_str or "series id" in row_str.lower():
            # The series IDs are in this row
            series_names = df.iloc[header_row].values
            series_ids = row.values
            
            for name, sid in zip(series_names, series_ids):
                if pd.notna(name) and pd.notna(sid) and str(sid) != "Series ID":
                    series_map[str(name)] = str(sid)
            
            break
    
    return series_map


def _tidy_special_table(
    xl_file: pd.ExcelFile,
    table_no: str,
    url: str,
    cur_hist: str
) -> pd.DataFrame:
    """
    Handle special table formats that don't follow the standard structure.
    """
    # This would implement special handling for tables like A1.1 and A3
    # For now, we'll raise an informative error
    raise RBADataError(
        f"Table {table_no} has a non-standard format that requires special handling. "
        "This functionality is not yet implemented."
    )