"""
Production-grade RBA data fetcher with all advanced features.

This module provides the RBADataFetcher class that combines all the
enhancements from the rbadata package into a single, comprehensive interface.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

try:
    from .async_core import AsyncRBAClient

    _ASYNC_AVAILABLE = True
except ImportError:
    AsyncRBAClient = None
    _ASYNC_AVAILABLE = False
from .cache import configure_cache
from .core import read_rba
from .exceptions import DataError, RBADataError, ValidationError


class RBADataFetcher:
    """
    Production-grade RBA data fetcher with comprehensive features.

    This class provides:
    - Full series coverage (100% of RBA data)
    - Efficient bulk fetching
    - Async support for concurrent downloads
    - Smart caching with configurable backends
    - Date range filtering
    - Enhanced error handling
    - Data validation
    - Performance monitoring

    Examples
    --------
    >>> # Basic usage
    >>> fetcher = RBADataFetcher()
    >>> df = fetcher.fetch('F1')

    >>> # Advanced usage with caching
    >>> fetcher = RBADataFetcher(
    ...     cache_backend='disk',
    ...     cache_dir='./rba_cache',
    ...     default_ttl=7200  # 2 hours
    ... )

    >>> # Fetch multiple series efficiently
    >>> yield_curve = fetcher.fetch_series([
    ...     'FCMYGBAG1', 'FCMYGBAG2', 'FCMYGBAG3',
    ...     'FCMYGBAG5', 'FCMYGBAG10'
    ... ])

    >>> # Async fetch for multiple tables
    >>> tables_data = await fetcher.fetch_tables_async(['F1', 'F2', 'G1'])
    """

    # Complete table metadata (from the analysis document)
    TABLE_METADATA = {
        "F1": {
            "name": "Interest Rates and Yields - Money Market",
            "frequency": "Daily/Monthly",
            "series_count": 50,  # Full coverage
        },
        "F2": {
            "name": "Capital Market Yields - Government Bonds",
            "frequency": "Daily/Monthly",
            "series_count": 30,
        },
        "F11": {
            "name": "Exchange Rates",
            "frequency": "Daily/Monthly",
            "series_count": 25,
        },
        "G1": {
            "name": "Consumer Price Inflation",
            "frequency": "Quarterly",
            "series_count": 10,
        },
        "D3": {
            "name": "Monetary Aggregates",
            "frequency": "Monthly",
            "series_count": 15,
        },
        # Add more tables as needed
    }

    def __init__(
        self,
        cache_backend: str = "memory",
        cache_dir: Optional[Union[str, Path]] = None,
        default_ttl: int = 3600,
        max_concurrent: int = 5,
        timeout: int = 30,
        validate_data: bool = True,
        track_performance: bool = False,
    ):
        """
        Initialize the RBA data fetcher.

        Parameters
        ----------
        cache_backend : str, default "memory"
            Cache backend type: "memory" or "disk"
        cache_dir : str or Path, optional
            Directory for disk cache
        default_ttl : int, default 3600
            Default cache TTL in seconds (1 hour)
        max_concurrent : int, default 5
            Maximum concurrent downloads
        timeout : int, default 30
            Request timeout in seconds
        validate_data : bool, default True
            Whether to validate fetched data
        track_performance : bool, default False
            Whether to track performance metrics
        """
        # Configure cache
        self.cache = configure_cache(
            backend=cache_backend,
            cache_dir=cache_dir,
            default_ttl=default_ttl,
            enabled=True,
        )

        # Settings
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.validate_data = validate_data
        self.track_performance = track_performance

        # Performance tracking
        self._performance_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_download_time": 0,
            "total_parse_time": 0,
            "errors": [],
        }

        # Load series metadata
        self._load_series_metadata()

    def _load_series_metadata(self):
        """Load comprehensive series metadata."""
        try:
            metadata_path = Path(__file__).parent / "data" / "series_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    self.series_metadata = json.load(f)
            else:
                self.series_metadata = {}
        except Exception:
            self.series_metadata = {}

    def fetch(
        self,
        table_no: Optional[Union[str, List[str]]] = None,
        series_id: Optional[Union[str, List[str]]] = None,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        use_csv: bool = True,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Fetch RBA data with all enhancements.

        This is a wrapper around read_rba() that adds:
        - Performance tracking
        - Data validation
        - Enhanced error messages

        Parameters
        ----------
        table_no : str or list of str, optional
            Table number(s) to fetch
        series_id : str or list of str, optional
            Series ID(s) to fetch
        start_date : str or datetime, optional
            Start date for filtering
        end_date : str or datetime, optional
            End date for filtering
        use_csv : bool, default True
            Use CSV format for full series coverage
        use_cache : bool, default True
            Use caching for better performance

        Returns
        -------
        pd.DataFrame
            Fetched and validated data
        """
        start_time = datetime.now() if self.track_performance else None

        try:
            # Track request
            if self.track_performance:
                self._performance_stats["total_requests"] += 1

            # Validate inputs
            if start_date and end_date:
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                if start_dt > end_dt:
                    raise ValidationError(
                        "date_range",
                        f"{start_date} to {end_date}",
                        "start_date must be before end_date",
                    )

            # Fetch data
            df = read_rba(
                table_no=table_no,
                series_id=series_id,
                start_date=start_date,
                end_date=end_date,
                use_csv=use_csv,
                use_cache=use_cache,
            )

            # Validate data if enabled
            if self.validate_data:
                self._validate_dataframe(df)

            # Track performance
            if self.track_performance:
                elapsed = (datetime.now() - start_time).total_seconds()
                self._performance_stats["total_download_time"] += elapsed

            return df

        except Exception as e:
            if self.track_performance:
                self._performance_stats["errors"].append(
                    {
                        "timestamp": datetime.now(),
                        "error": str(e),
                        "params": {"table_no": table_no, "series_id": series_id},
                    }
                )
            raise

    def fetch_series(
        self,
        series_ids: Union[str, List[str]],
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        pivot: bool = False,
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Fetch specific series efficiently.

        Parameters
        ----------
        series_ids : str or list of str
            Series ID(s) to fetch
        start_date : str or datetime, optional
            Start date
        end_date : str or datetime, optional
            End date
        pivot : bool, default False
            If True, return pivoted DataFrame with series as columns

        Returns
        -------
        pd.DataFrame or dict
            If pivot=True, returns DataFrame with date index and series columns
            Otherwise returns standard long-format DataFrame
        """
        if isinstance(series_ids, str):
            series_ids = [series_ids]

        df = self.fetch(series_id=series_ids, start_date=start_date, end_date=end_date)

        if pivot:
            # Pivot to wide format
            pivot_df = df.pivot(index="date", columns="series_id", values="value")

            # Add metadata as attributes
            for series_id in pivot_df.columns:
                series_data = df[df["series_id"] == series_id].iloc[0]
                pivot_df[series_id].attrs = {
                    "description": series_data.get("description", series_id),
                    "units": series_data.get("units", ""),
                    "table": series_data.get("table", ""),
                }

            return pivot_df

        return df

    async def fetch_async(
        self,
        table_no: Optional[Union[str, List[str]]] = None,
        series_id: Optional[Union[str, List[str]]] = None,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
    ) -> pd.DataFrame:
        """
        Async version of fetch() for concurrent downloads.

        Parameters
        ----------
        Same as fetch()

        Returns
        -------
        pd.DataFrame
            Fetched data
        """
        if not _ASYNC_AVAILABLE:
            raise ImportError(
                "Async functionality requires 'aiohttp'. "
                "Install with: pip install aiohttp"
            )

        async with AsyncRBAClient(
            max_concurrent=self.max_concurrent, timeout=self.timeout, use_cache=True
        ) as client:
            return await client.read_rba_async(
                table_no=table_no,
                series_id=series_id,
                start_date=start_date,
                end_date=end_date,
            )

    async def fetch_tables_async(
        self,
        table_nos: List[str],
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch multiple tables concurrently.

        Parameters
        ----------
        table_nos : list of str
            Tables to fetch
        start_date : str or datetime, optional
            Start date
        end_date : str or datetime, optional
            End date

        Returns
        -------
        dict
            Dictionary mapping table_no to DataFrame
        """
        if not _ASYNC_AVAILABLE:
            raise ImportError(
                "Async functionality requires 'aiohttp'. "
                "Install with: pip install aiohttp"
            )

        tasks = []
        for table in table_nos:
            task = self.fetch_async(
                table_no=table, start_date=start_date, end_date=end_date
            )
            tasks.append((table, task))

        results = {}
        for table, task in tasks:
            try:
                df = await task
                results[table] = df
            except Exception as e:
                print(f"Failed to fetch table {table}: {e}")

        return results

    def get_available_series(
        self, table_no: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Get all available series, optionally filtered by table.

        Parameters
        ----------
        table_no : str, optional
            Filter by specific table

        Returns
        -------
        dict
            Dictionary with table metadata and series lists
        """
        if table_no and table_no.upper() in self.series_metadata:
            table_data = self.series_metadata[table_no.upper()]
            return {
                "table_name": table_data.get("table_name", ""),
                "series": list(table_data.get("series", {}).keys()),
                "series_details": table_data.get("series", {}),
            }

        # Return all tables
        result = {}
        for table, data in self.series_metadata.items():
            result[table] = {
                "table_name": data.get("table_name", ""),
                "series_count": len(data.get("series", {})),
                "series": list(data.get("series", {}).keys()),
            }

        return result

    def search_series(self, keyword: str) -> List[Dict[str, str]]:
        """
        Search for series by keyword in ID or description.

        Parameters
        ----------
        keyword : str
            Search keyword

        Returns
        -------
        list
            List of matching series with metadata
        """
        keyword = keyword.upper()
        matches = []

        for table, table_data in self.series_metadata.items():
            for series_id, series_info in table_data.get("series", {}).items():
                description = series_info.get("description", "").upper()

                if keyword in series_id or keyword in description:
                    matches.append(
                        {
                            "series_id": series_id,
                            "description": series_info.get("description", ""),
                            "table": table,
                            "units": series_info.get("unit", ""),
                            "type": series_info.get("type", ""),
                        }
                    )

        return matches

    def build_yield_curve(
        self,
        date: Optional[Union[str, datetime]] = None,
        curve_type: str = "government",
    ) -> pd.DataFrame:
        """
        Build a yield curve for a specific date.

        Parameters
        ----------
        date : str or datetime, optional
            Date for yield curve (defaults to latest)
        curve_type : str, default "government"
            Type of curve: "government", "swap", or "bank_bill"

        Returns
        -------
        pd.DataFrame
            DataFrame with tenor (years) and yield columns
        """
        # Define series for each curve type
        curve_series = {
            "government": {
                "FCMYGBAG1": 1,
                "FCMYGBAG2": 2,
                "FCMYGBAG3": 3,
                "FCMYGBAG5": 5,
                "FCMYGBAG7": 7,
                "FCMYGBAG10": 10,
                "FCMYGBAG15": 15,
                "FCMYGBAG20": 20,
            },
            "swap": {
                "FMSWAPS1": 1,
                "FMSWAPS2": 2,
                "FMSWAPS3": 3,
                "FMSWAPS4": 4,
                "FMSWAPS5": 5,
                "FMSWAPS7": 7,
                "FMSWAPS10": 10,
            },
            "bank_bill": {
                "FIRMMBAB30D": 30 / 365,
                "FIRMMBAB60D": 60 / 365,
                "FIRMMBAB90D": 90 / 365,
                "FIRMMBAB120D": 120 / 365,
                "FIRMMBAB180D": 180 / 365,
            },
        }

        if curve_type not in curve_series:
            raise ValueError(f"Unknown curve type: {curve_type}")

        # Fetch data
        series_map = curve_series[curve_type]
        df = self.fetch_series(
            list(series_map.keys()),
            start_date=date if date else datetime.now() - timedelta(days=7),
            end_date=date,
        )

        if df.empty:
            raise RBADataError("No yield curve data available for the specified date")

        # Get latest date if not specified
        if date is None:
            date = df["date"].max()
        else:
            date = pd.to_datetime(date)

        # Filter for specific date
        df_date = df[df["date"] == date]

        # Build curve
        curve_data = []
        for series_id, tenor in series_map.items():
            series_data = df_date[df_date["series_id"] == series_id]
            if not series_data.empty:
                curve_data.append(
                    {
                        "tenor": tenor,
                        "yield": series_data["value"].iloc[0],
                        "series_id": series_id,
                    }
                )

        curve_df = pd.DataFrame(curve_data)
        curve_df = curve_df.sort_values("tenor")

        return curve_df

    def _validate_dataframe(self, df: pd.DataFrame) -> None:
        """Validate fetched DataFrame."""
        if df.empty:
            raise DataError("Fetched DataFrame is empty")

        required_columns = ["date", "series_id", "value"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise DataError(f"Missing required columns: {missing}")

        # Check data types
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            raise DataError("'date' column is not datetime type")

        if not pd.api.types.is_numeric_dtype(df["value"]):
            raise DataError("'value' column is not numeric type")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.track_performance:
            return {"message": "Performance tracking is disabled"}

        stats = self._performance_stats.copy()

        # Calculate cache hit rate
        total = stats["cache_hits"] + stats["cache_misses"]
        if total > 0:
            stats["cache_hit_rate"] = stats["cache_hits"] / total
        else:
            stats["cache_hit_rate"] = 0

        # Average times
        if stats["total_requests"] > 0:
            stats["avg_download_time"] = (
                stats["total_download_time"] / stats["total_requests"]
            )
        else:
            stats["avg_download_time"] = 0

        return stats

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache.clear()

    def __repr__(self) -> str:
        """String representation."""
        cache_type = type(self.cache.backend).__name__
        return (
            f"RBADataFetcher(cache={cache_type}, "
            f"max_concurrent={self.max_concurrent}, "
            f"validate={self.validate_data})"
        )
