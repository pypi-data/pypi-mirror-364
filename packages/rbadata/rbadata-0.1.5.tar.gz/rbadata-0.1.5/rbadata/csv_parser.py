"""
Enhanced CSV parser for RBA data with support for all series.

This module provides functionality to parse RBA's CSV format directly,
enabling access to all available series with better performance and
proper encoding handling.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Union

import pandas as pd
import requests

from .cache import get_cache
from .config import get_headers
from .exceptions import DataError, DownloadError, RBADataError, SeriesNotFoundError
from .standardize import standardize_rba_dataframe


def download_rba_csv(table_no: str, use_cache: bool = True) -> str:
    """
    Download RBA CSV data directly from the RBA website.

    Parameters
    ----------
    table_no : str
        RBA table number (e.g., 'f1', 'g1')
    use_cache : bool, default True
        Whether to use cached data if available

    Returns
    -------
    str
        CSV content as string

    Raises
    ------
    RBADataError
        If download fails
    """
    # Check cache first
    if use_cache:
        cache = get_cache()
        cached_content = cache.get_csv(table_no)
        if cached_content is not None:
            return cached_content

    # Construct CSV URL
    base_url = "https://www.rba.gov.au/statistics/tables/csv"
    csv_url = f"{base_url}/{table_no.lower()}-data.csv"

    try:
        # Download with proper encoding
        response = requests.get(csv_url, headers=get_headers(), timeout=30)
        response.raise_for_status()

        # RBA uses Windows-1252 encoding
        response.encoding = "windows-1252"
        content = response.text

        # Cache the content
        if use_cache:
            cache = get_cache()
            cache.set_csv(table_no, content)

        return content

    except requests.exceptions.HTTPError as e:
        raise DownloadError(
            f"Failed to download CSV for table {table_no}",
            url=csv_url,
            status_code=e.response.status_code if e.response else None,
        )
    except requests.exceptions.ConnectionError:
        raise DownloadError(
            f"Network error downloading table {table_no}",
            url=csv_url,
            context={"error_type": "connection_error"},
        )
    except requests.exceptions.Timeout:
        raise DownloadError(
            f"Timeout downloading table {table_no} (30 seconds exceeded)",
            url=csv_url,
            context={"error_type": "timeout"},
        )
    except requests.exceptions.RequestException as e:
        raise DownloadError(
            f"Failed to download CSV for table {table_no}: {str(e)}", url=csv_url
        )


def parse_rba_csv(
    csv_content: str,
    table_no: str,
    series_filter: Optional[List[str]] = None,
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
) -> pd.DataFrame:
    """
    Parse RBA CSV content into a tidy DataFrame.

    This parser handles RBA's specific CSV format which includes:
    - Multiple header rows with metadata
    - Series IDs in the header
    - Date column in various formats
    - 'na' values for missing data

    Parameters
    ----------
    csv_content : str
        CSV content as string
    table_no : str
        RBA table number
    series_filter : list of str, optional
        List of series IDs to filter
    start_date : str or datetime, optional
        Start date for filtering
    end_date : str or datetime, optional
        End date for filtering

    Returns
    -------
    pd.DataFrame
        Tidy DataFrame with columns: date, series_id, value, table, description
    """
    lines = csv_content.strip().split("\n")

    # Find the Series ID header row
    header_idx = _find_series_id_row(lines)
    if header_idx is None:
        raise DataError(
            f"Could not find Series ID header in table {table_no}",
            table_no=table_no,
            context={
                "error_type": "missing_header",
                "lines_checked": min(20, len(lines)),
            },
        )

    # Extract series IDs from header
    series_ids = _extract_series_ids(lines[header_idx])

    # Extract metadata (description, units, etc.)
    metadata = _extract_csv_metadata(lines[:header_idx], series_ids)

    # Parse data rows
    data_rows = []
    for line in lines[header_idx + 1 :]:
        if not line.strip():
            continue

        values = _parse_csv_line(line)
        if len(values) < 2:
            continue

        date_str = values[0].strip()
        if not date_str:
            continue

        try:
            # Parse date
            date = _parse_rba_date(date_str)

            # Process each series value
            for i, series_id in enumerate(series_ids):
                if i + 1 < len(values):
                    value_str = values[i + 1].strip()
                    if value_str and value_str.lower() != "na":
                        try:
                            value = float(value_str)

                            # Apply series filter if specified
                            if series_filter and series_id not in series_filter:
                                continue

                            data_rows.append(
                                {
                                    "date": date,
                                    "series_id": series_id,
                                    "value": value,
                                    "table": table_no.upper(),
                                    "description": metadata.get(series_id, {}).get(
                                        "description", series_id
                                    ),
                                    "units": metadata.get(series_id, {}).get(
                                        "units", ""
                                    ),
                                    "series_type": metadata.get(series_id, {}).get(
                                        "series_type", "Original"
                                    ),
                                }
                            )
                        except ValueError:
                            continue

        except Exception:
            continue

    # Create DataFrame
    df = pd.DataFrame(data_rows)

    if df.empty:
        if series_filter:
            # Check if the requested series exist
            missing_series = [s for s in series_filter if s not in series_ids]
            if missing_series:
                raise SeriesNotFoundError(
                    missing_series, table_no=table_no, available_series=series_ids
                )
        raise DataError(
            f"No valid data found in table {table_no}",
            table_no=table_no,
            context={"series_count": len(series_ids), "date_range": "unknown"},
        )

    # Apply date filtering
    if start_date:
        start_date = pd.to_datetime(start_date)
        df = df[df["date"] >= start_date]

    if end_date:
        end_date = pd.to_datetime(end_date)
        df = df[df["date"] <= end_date]

    # Standardize the DataFrame format
    df = standardize_rba_dataframe(df, source="csv")

    return df


def _find_series_id_row(lines: List[str]) -> Optional[int]:
    """Find the row containing 'Series ID' header."""
    for i, line in enumerate(lines[:20]):  # Check first 20 lines
        if "Series ID" in line:
            return i
    return None


def _extract_series_ids(header_line: str) -> List[str]:
    """Extract series IDs from the header line."""
    # Split by comma and clean up
    parts = header_line.split(",")
    series_ids = []

    for part in parts[1:]:  # Skip first column (Series ID label)
        series_id = part.strip().strip('"')
        if series_id:
            series_ids.append(series_id)

    return series_ids


def _extract_csv_metadata(
    header_lines: List[str], series_ids: List[str]
) -> Dict[str, Dict[str, str]]:
    """Extract metadata from CSV header rows."""
    metadata = {sid: {} for sid in series_ids}

    for line in header_lines:
        if not line.strip():
            continue

        parts = _parse_csv_line(line)
        if not parts:
            continue

        label = parts[0].strip().lower()

        # Extract descriptions
        if "description" in label:
            for i, series_id in enumerate(series_ids):
                if i + 1 < len(parts):
                    desc = parts[i + 1].strip().strip('"')
                    if desc:
                        metadata[series_id]["description"] = desc

        # Extract units
        elif "unit" in label:
            for i, series_id in enumerate(series_ids):
                if i + 1 < len(parts):
                    unit = parts[i + 1].strip().strip('"')
                    if unit:
                        metadata[series_id]["units"] = unit

        # Extract series type
        elif "type" in label or "series type" in label:
            for i, series_id in enumerate(series_ids):
                if i + 1 < len(parts):
                    stype = parts[i + 1].strip().strip('"')
                    if stype:
                        metadata[series_id]["series_type"] = stype

    return metadata


def _parse_csv_line(line: str) -> List[str]:
    """
    Parse a CSV line handling quoted values properly.

    This handles cases where values contain commas within quotes.
    """
    # Use regex to split CSV properly
    pattern = r',(?=(?:[^"]*"[^"]*")*[^"]*$)'
    parts = re.split(pattern, line)

    # Clean up quotes
    cleaned_parts = []
    for part in parts:
        part = part.strip()
        if part.startswith('"') and part.endswith('"'):
            part = part[1:-1]
        cleaned_parts.append(part)

    return cleaned_parts


def _parse_rba_date(date_str: str) -> datetime:
    """
    Parse RBA date formats.

    RBA uses various date formats:
    - Daily: 'dd-mmm-yyyy' (e.g., '01-Jan-2023')
    - Monthly: 'mmm-yyyy' (e.g., 'Jan-2023')
    - Quarterly: 'Qn yyyy' (e.g., 'Q1 2023')
    - Annual: 'yyyy' (e.g., '2023')
    """
    date_str = date_str.strip()

    # Try daily format first
    try:
        return pd.to_datetime(date_str, format="%d-%b-%Y")
    except ValueError:
        pass

    # Try monthly format
    try:
        return pd.to_datetime(date_str, format="%b-%Y")
    except ValueError:
        pass

    # Try quarterly format
    if date_str.startswith("Q"):
        try:
            quarter_match = re.match(r"Q(\d)\s+(\d{4})", date_str)
            if quarter_match:
                quarter = int(quarter_match.group(1))
                year = int(quarter_match.group(2))
                # Convert quarter to month (Q1=1, Q2=4, Q3=7, Q4=10)
                month = (quarter - 1) * 3 + 1
                return pd.to_datetime(f"{year}-{month:02d}-01")
        except ValueError:
            pass

    # Try annual format
    try:
        if len(date_str) == 4 and date_str.isdigit():
            return pd.to_datetime(f"{date_str}-01-01")
    except ValueError:
        pass

    # Fall back to pandas parser
    return pd.to_datetime(date_str, errors="coerce")


def fetch_multiple_series_csv(
    series_ids: List[str],
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
) -> pd.DataFrame:
    """
    Fetch multiple series efficiently using CSV downloads.

    This function groups series by table and downloads each table only once,
    then filters for the requested series.

    Parameters
    ----------
    series_ids : list of str
        List of series IDs to fetch
    start_date : str or datetime, optional
        Start date for filtering
    end_date : str or datetime, optional
        End date for filtering

    Returns
    -------
    pd.DataFrame
        Combined DataFrame with all requested series
    """
    from .utils import tables_from_seriesid

    # Map series to tables
    table_mapping = tables_from_seriesid(series_ids)

    all_data = []

    # Download each table once
    for table_no, table_series in table_mapping.items():
        try:
            # Download CSV
            csv_content = download_rba_csv(table_no)

            # Parse with series filter
            df = parse_rba_csv(
                csv_content,
                table_no,
                series_filter=list(table_series),
                start_date=start_date,
                end_date=end_date,
            )

            all_data.append(df)

        except RBADataError as e:
            # Log error but continue with other tables
            print(f"Warning: Failed to fetch table {table_no}: {str(e)}")
            continue

    if not all_data:
        raise RBADataError("Failed to fetch any data for the requested series")

    # Combine all data
    result = pd.concat(all_data, ignore_index=True)

    # Ensure we only have requested series
    result = result[result["series_id"].isin(series_ids)]

    return result
