"""
Core functions for reading RBA data
"""

from datetime import datetime
from typing import List, Optional, Union

import pandas as pd

from .cache import get_cache
from .csv_parser import download_rba_csv, fetch_multiple_series_csv, parse_rba_csv
from .download import download_rba
from .exceptions import RBADataError
from .tidy import tidy_rba
from .utils import check_rba_connection, get_rba_urls, tables_from_seriesid


def read_rba(
    table_no: Optional[Union[str, List[str]]] = None,
    series_id: Optional[Union[str, List[str]]] = None,
    cur_hist: str = "current",
    use_csv: bool = True,
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
    use_cache: bool = True,
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
    use_csv : bool, default True
        If True, use CSV format for better performance and full series coverage.
        If False, use Excel format (legacy behavior)
    start_date : str or datetime, optional
        Start date for filtering data (e.g., "2020-01-01" or datetime object)
    end_date : str or datetime, optional
        End date for filtering data (e.g., "2023-12-31" or datetime object)
    use_cache : bool, default True
        If True, use cached data when available to improve performance

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
    # Check cache first
    if use_cache:
        cache = get_cache()
        cached_df = cache.get_dataframe(
            table_no=table_no,
            series_id=series_id,
            start_date=start_date,
            end_date=end_date,
            cur_hist=cur_hist,
            use_csv=use_csv,
        )
        if cached_df is not None:
            return cached_df

    # Check internet connection
    check_rba_connection()

    # Validate inputs
    if table_no is None and series_id is None:
        raise RBADataError("Either 'table_no' or 'series_id' must be specified")

    if table_no is not None and series_id is not None:
        raise RBADataError("Only one of 'table_no' or 'series_id' should be specified")

    # Use CSV method for series_id requests or when use_csv is True
    if use_csv and series_id is not None:
        # Convert series_id to list if string
        if isinstance(series_id, str):
            series_id = [series_id]

        # Use efficient CSV fetching for multiple series
        result = fetch_multiple_series_csv(series_id, start_date, end_date)

        # Cache the result
        if use_cache:
            cache = get_cache()
            cache.set_dataframe(
                result,
                series_id=series_id,
                start_date=start_date,
                end_date=end_date,
                cur_hist=cur_hist,
                use_csv=use_csv,
            )

        return result

    # Handle series_id input for Excel method
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

    # Use CSV method if requested
    if use_csv and cur_hist == "current":
        all_data = []
        for table in table_no:
            try:
                # Download CSV
                csv_content = download_rba_csv(table)

                # Parse CSV
                df = parse_rba_csv(
                    csv_content,
                    table,
                    series_filter=series_id if series_id else None,
                    start_date=start_date,
                    end_date=end_date,
                )

                all_data.append(df)
            except RBADataError as e:
                # Fall back to Excel method if CSV fails
                print(
                    f"CSV download failed for {table}, falling back to Excel: {str(e)}"
                )
                # Continue with Excel method below

        if all_data:
            # Combine all DataFrames
            result = pd.concat(all_data, ignore_index=True)
            result = result.sort_values(["date", "series_id"])

            # Cache the result
            if use_cache:
                cache = get_cache()
                cache.set_dataframe(
                    result,
                    table_no=table_no,
                    series_id=series_id,
                    start_date=start_date,
                    end_date=end_date,
                    cur_hist=cur_hist,
                    use_csv=use_csv,
                )

            return result

    # Excel method (legacy or fallback)
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

        # Apply date filtering
        if start_date:
            df = df[df["date"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["date"] <= pd.to_datetime(end_date)]

        all_data.append(df)

    # Combine all DataFrames
    result = pd.concat(all_data, ignore_index=True)

    # Sort by date
    result = result.sort_values(["date", "series_id"])

    # Cache the result
    if use_cache:
        cache = get_cache()
        cache.set_dataframe(
            result,
            table_no=table_no,
            series_id=series_id,
            start_date=start_date,
            end_date=end_date,
            cur_hist=cur_hist,
            use_csv=use_csv,
        )

    return result


def read_rba_seriesid(
    series_id: Union[str, List[str]],
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
    use_csv: bool = True,
) -> pd.DataFrame:
    """
    Convenience function to download RBA data by series ID.

    This is equivalent to calling read_rba(series_id=series_id).

    Parameters
    ----------
    series_id : str or list of str
        RBA series ID(s) to download
    start_date : str or datetime, optional
        Start date for filtering data
    end_date : str or datetime, optional
        End date for filtering data
    use_csv : bool, default True
        If True, use CSV format for better performance and full series coverage

    Returns
    -------
    pd.DataFrame
        A tidy DataFrame containing the requested RBA data

    Examples
    --------
    >>> df = read_rba_seriesid("GCPIAG")
    >>> df = read_rba_seriesid(["GCPIAG", "GLFSURSA"])
    >>> df = read_rba_seriesid("FIRMMCRTD", start_date="2020-01-01")
    """
    return read_rba(
        series_id=series_id, start_date=start_date, end_date=end_date, use_csv=use_csv
    )
