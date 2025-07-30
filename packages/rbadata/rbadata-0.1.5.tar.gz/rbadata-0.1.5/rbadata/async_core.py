"""
Async support for rbadata - fetch RBA data asynchronously for better performance.

This module provides async versions of the main data fetching functions,
enabling concurrent downloads and improved performance for bulk operations.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Union

import aiohttp
import pandas as pd

from .cache import get_cache
from .csv_parser import parse_rba_csv
from .exceptions import DownloadError, RBADataError, SeriesNotFoundError
from .utils import tables_from_seriesid


class AsyncRBAClient:
    """
    Asynchronous client for fetching RBA data.

    Provides async methods for downloading and parsing RBA data with:
    - Concurrent table downloads
    - Connection pooling
    - Automatic retries
    - Progress tracking
    """

    def __init__(
        self,
        max_concurrent: int = 5,
        timeout: int = 30,
        max_retries: int = 3,
        use_cache: bool = True,
    ):
        """
        Initialize async RBA client.

        Parameters
        ----------
        max_concurrent : int, default 5
            Maximum concurrent downloads
        timeout : int, default 30
            Request timeout in seconds
        max_retries : int, default 3
            Maximum number of retries for failed requests
        use_cache : bool, default True
            Whether to use caching
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.max_retries = max_retries
        self.use_cache = use_cache
        self.session: Optional[aiohttp.ClientSession] = None
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self):
        """Enter async context."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        if self.session:
            await self.session.close()

    async def _download_csv(self, table_no: str) -> str:
        """
        Download CSV for a single table.

        Parameters
        ----------
        table_no : str
            Table number to download

        Returns
        -------
        str
            CSV content
        """
        # Check cache first
        if self.use_cache:
            cache = get_cache()
            cached = cache.get_csv(table_no)
            if cached:
                return cached

        url = (
            f"https://www.rba.gov.au/statistics/tables/csv/{table_no.lower()}-data.csv"
        )

        async with self._semaphore:  # Limit concurrent requests
            for attempt in range(self.max_retries):
                try:
                    async with self.session.get(url) as response:
                        response.raise_for_status()

                        # Read content with proper encoding
                        content_bytes = await response.read()
                        content = content_bytes.decode("windows-1252")

                        # Cache if enabled
                        if self.use_cache:
                            cache = get_cache()
                            cache.set_csv(table_no, content)

                        return content

                except aiohttp.ClientResponseError as e:
                    if attempt == self.max_retries - 1:
                        raise DownloadError(
                            f"Failed to download table {table_no}",
                            url=url,
                            status_code=e.status,
                        )
                    await asyncio.sleep(2**attempt)  # Exponential backoff

                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise DownloadError(
                            f"Error downloading table {table_no}: {str(e)}", url=url
                        )
                    await asyncio.sleep(2**attempt)

    async def read_rba_async(
        self,
        table_no: Optional[Union[str, List[str]]] = None,
        series_id: Optional[Union[str, List[str]]] = None,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
    ) -> pd.DataFrame:
        """
        Asynchronously download and parse RBA data.

        Parameters
        ----------
        table_no : str or list of str, optional
            Table number(s) to download
        series_id : str or list of str, optional
            Series ID(s) to download
        start_date : str or datetime, optional
            Start date for filtering
        end_date : str or datetime, optional
            End date for filtering

        Returns
        -------
        pd.DataFrame
            Combined data from all requested tables/series
        """
        # Check cache first
        if self.use_cache:
            cache = get_cache()
            cached = cache.get_dataframe(
                table_no=table_no,
                series_id=series_id,
                start_date=start_date,
                end_date=end_date,
                use_csv=True,
            )
            if cached is not None:
                return cached

        # Validate inputs
        if table_no is None and series_id is None:
            raise RBADataError("Either 'table_no' or 'series_id' must be specified")

        if table_no is not None and series_id is not None:
            raise RBADataError(
                "Only one of 'table_no' or 'series_id' should be specified"
            )

        # Handle series_id input
        if series_id is not None:
            if isinstance(series_id, str):
                series_id = [series_id]
            table_mapping = tables_from_seriesid(series_id)
            table_no = list(table_mapping.keys())

        # Ensure table_no is a list
        if isinstance(table_no, str):
            table_no = [table_no]

        # Download all tables concurrently
        tasks = [self._download_csv(table) for table in table_no]
        csv_contents = await asyncio.gather(*tasks, return_exceptions=True)

        # Parse results
        all_data = []
        errors = []

        for table, content in zip(table_no, csv_contents):
            if isinstance(content, Exception):
                errors.append(f"Table {table}: {str(content)}")
                continue

            try:
                df = parse_rba_csv(
                    content,
                    table,
                    series_filter=series_id if series_id else None,
                    start_date=start_date,
                    end_date=end_date,
                )
                all_data.append(df)
            except Exception as e:
                errors.append(f"Table {table} parsing: {str(e)}")

        if not all_data:
            if errors:
                raise RBADataError(
                    f"Failed to fetch any data. Errors: {'; '.join(errors)}"
                )
            else:
                raise RBADataError("No data found for the requested parameters")

        # Combine results
        result = pd.concat(all_data, ignore_index=True)
        result = result.sort_values(["date", "series_id"])

        # Cache result
        if self.use_cache:
            cache = get_cache()
            cache.set_dataframe(
                result,
                table_no=table_no,
                series_id=series_id,
                start_date=start_date,
                end_date=end_date,
                use_csv=True,
            )

        return result

    async def fetch_multiple_series_async(
        self,
        series_ids: List[str],
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch multiple series concurrently.

        Parameters
        ----------
        series_ids : list of str
            Series IDs to fetch
        start_date : str or datetime, optional
            Start date for filtering
        end_date : str or datetime, optional
            End date for filtering

        Returns
        -------
        dict
            Dictionary mapping series_id to DataFrame
        """
        # Group series by table
        table_mapping = tables_from_seriesid(series_ids)

        # Download all tables
        table_list = list(table_mapping.keys())
        tasks = [self._download_csv(table) for table in table_list]
        csv_contents = await asyncio.gather(*tasks, return_exceptions=True)

        # Parse and extract series
        results = {}

        for table, content, series_in_table in zip(
            table_list, csv_contents, table_mapping.values()
        ):
            if isinstance(content, Exception):
                continue

            try:
                df = parse_rba_csv(
                    content,
                    table,
                    series_filter=list(series_in_table),
                    start_date=start_date,
                    end_date=end_date,
                )

                # Split by series
                for series_id in series_in_table:
                    series_df = df[df["series_id"] == series_id].copy()
                    if not series_df.empty:
                        results[series_id] = series_df.set_index("date")[
                            ["value", "units", "description"]
                        ]

            except Exception:
                continue

        # Check for missing series
        missing = [s for s in series_ids if s not in results]
        if missing and not results:
            raise SeriesNotFoundError(missing)

        return results


# Convenience functions


async def read_rba_async(
    table_no: Optional[Union[str, List[str]]] = None,
    series_id: Optional[Union[str, List[str]]] = None,
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
    max_concurrent: int = 5,
    use_cache: bool = True,
) -> pd.DataFrame:
    """
    Async version of read_rba().

    Downloads RBA data asynchronously for better performance when fetching
    multiple tables or large amounts of data.

    Parameters
    ----------
    table_no : str or list of str, optional
        Table number(s) to download
    series_id : str or list of str, optional
        Series ID(s) to download
    start_date : str or datetime, optional
        Start date for filtering
    end_date : str or datetime, optional
        End date for filtering
    max_concurrent : int, default 5
        Maximum concurrent downloads
    use_cache : bool, default True
        Whether to use caching

    Returns
    -------
    pd.DataFrame
        Combined data from all requested tables/series

    Examples
    --------
    >>> # Async fetch multiple tables
    >>> import asyncio
    >>> df = asyncio.run(read_rba_async(table_no=['f1', 'f2', 'g1']))

    >>> # Async fetch with date filter
    >>> df = asyncio.run(read_rba_async(
    ...     series_id=['FIRMMCRTD', 'FCMYGBAG10'],
    ...     start_date='2020-01-01'
    ... ))
    """
    async with AsyncRBAClient(
        max_concurrent=max_concurrent, use_cache=use_cache
    ) as client:
        return await client.read_rba_async(
            table_no=table_no,
            series_id=series_id,
            start_date=start_date,
            end_date=end_date,
        )


async def fetch_multiple_series_async(
    series_ids: List[str],
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
    max_concurrent: int = 5,
    use_cache: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    Fetch multiple series concurrently.

    Parameters
    ----------
    series_ids : list of str
        Series IDs to fetch
    start_date : str or datetime, optional
        Start date for filtering
    end_date : str or datetime, optional
        End date for filtering
    max_concurrent : int, default 5
        Maximum concurrent downloads
    use_cache : bool, default True
        Whether to use caching

    Returns
    -------
    dict
        Dictionary mapping series_id to DataFrame

    Examples
    --------
    >>> # Fetch yield curve data
    >>> import asyncio
    >>> series = ['FCMYGBAG1', 'FCMYGBAG2', 'FCMYGBAG3', 'FCMYGBAG5', 'FCMYGBAG10']
    >>> data = asyncio.run(fetch_multiple_series_async(series))
    """
    async with AsyncRBAClient(
        max_concurrent=max_concurrent, use_cache=use_cache
    ) as client:
        return await client.fetch_multiple_series_async(
            series_ids=series_ids, start_date=start_date, end_date=end_date
        )
