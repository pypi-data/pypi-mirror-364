"""
rbadata - Download and tidy data from the Reserve Bank of Australia
"""

__version__ = "0.1.0"

from .alerts import RBAAlerts, create_alert

# Async functions (optional - only if aiohttp is available)
try:
    from .async_core import fetch_multiple_series_async, read_rba_async

    _ASYNC_AVAILABLE = True
except ImportError:
    _ASYNC_AVAILABLE = False
    fetch_multiple_series_async = None
    read_rba_async = None

# Browse functions
from .browse import browse_rba_series, browse_rba_tables

# Caching
from .cache import configure_cache, get_cache

# Analysis tools
from .calculator import InflationCalculator, inflation_calculator
from .cash_rate import read_cashrate
from .chart_pack import ChartPack, get_chart_pack

# Core functions
from .core import read_rba, read_rba_seriesid

# Utility functions
from .download import download_rba

# Advanced fetcher
from .fetcher import RBADataFetcher

# Data access functions
from .forecasts import rba_forecasts
from .glossary import Glossary, define, get_glossary

# Additional features
from .snapshots import Snapshots, get_economic_indicators, get_snapshots
from .tidy import tidy_rba

__all__ = [
    # Core functions
    "read_rba",
    "read_rba_seriesid",
    # Browse functions
    "browse_rba_series",
    "browse_rba_tables",
    # Caching
    "configure_cache",
    "get_cache",
    # Data access
    "rba_forecasts",
    "read_cashrate",
    # Analysis tools
    "InflationCalculator",
    "inflation_calculator",
    "ChartPack",
    "get_chart_pack",
    # Advanced fetcher
    "RBADataFetcher",
    # Additional features
    "Snapshots",
    "get_snapshots",
    "get_economic_indicators",
    "RBAAlerts",
    "create_alert",
    "Glossary",
    "get_glossary",
    "define",
    # Utilities
    "download_rba",
    "tidy_rba",
]

# Add async functions if available
if _ASYNC_AVAILABLE:
    __all__.extend(["read_rba_async", "fetch_multiple_series_async"])
