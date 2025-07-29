"""
rbadata - Download and tidy data from the Reserve Bank of Australia
"""

__version__ = "0.1.0"

from .core import read_rba, read_rba_seriesid
from .browse import browse_rba_series, browse_rba_tables
from .forecasts import rba_forecasts
from .cash_rate import read_cashrate
from .calculator import InflationCalculator, inflation_calculator
from .chart_pack import ChartPack, get_chart_pack
from .snapshots import Snapshots, get_snapshots, get_economic_indicators
from .alerts import RBAAlerts, create_alert
from .glossary import Glossary, get_glossary, define

__all__ = [
    "read_rba",
    "read_rba_seriesid",
    "browse_rba_series",
    "browse_rba_tables",
    "rba_forecasts",
    "read_cashrate",
    "InflationCalculator",
    "inflation_calculator",
    "ChartPack",
    "get_chart_pack",
    "Snapshots",
    "get_snapshots",
    "get_economic_indicators",
    "RBAAlerts",
    "create_alert",
    "Glossary",
    "get_glossary",
    "define",
]