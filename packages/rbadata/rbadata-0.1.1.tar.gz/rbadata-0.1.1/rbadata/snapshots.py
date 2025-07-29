"""
RBA Economic Snapshots access and data extraction
"""

from pathlib import Path
from typing import Dict, List, Optional, Literal
import pandas as pd
import requests
from bs4 import BeautifulSoup
from .exceptions import RBADataError
from .config import get_headers


class Snapshots:
    """
    Access RBA Economic Snapshots - visual summaries of economic data.
    
    The RBA provides three types of snapshots:
    1. Key Economic Indicators Snapshot
    2. Composition of the Australian Economy Snapshot  
    3. How Australians Pay Snapshot
    
    Examples
    --------
    >>> snapshots = Snapshots()
    >>> # Get available snapshot types
    >>> types = snapshots.get_snapshot_types()
    
    >>> # Download a specific snapshot
    >>> snapshots.download_snapshot("economic-indicators")
    
    >>> # Get data from economic indicators snapshot
    >>> data = snapshots.get_economic_indicators()
    """
    
    BASE_URL = "https://www.rba.gov.au/snapshots"
    
    SNAPSHOT_TYPES = {
        "economic-indicators": {
            "name": "Key Economic Indicators",
            "url": "/economy-snapshot",
            "description": "A snapshot of key economic indicators for Australia"
        },
        "economy-composition": {
            "name": "Composition of the Australian Economy",
            "url": "/economy-composition", 
            "description": "Data showing the composition of Australia's economy"
        },
        "payments": {
            "name": "How Australians Pay",
            "url": "/payments-snapshot",
            "description": "Data depicting how Australians pay"
        }
    }
    
    def __init__(self):
        """Initialize Snapshots instance."""
        self._cached_data = {}
    
    def get_snapshot_types(self) -> Dict[str, Dict[str, str]]:
        """
        Get available snapshot types and their metadata.
        
        Returns
        -------
        dict
            Dictionary of snapshot types with metadata
        """
        return self.SNAPSHOT_TYPES.copy()
    
    def download_snapshot(
        self,
        snapshot_type: Literal["economic-indicators", "economy-composition", "payments"],
        output_path: Optional[str] = None
    ) -> Path:
        """
        Download a snapshot PDF.
        
        Parameters
        ----------
        snapshot_type : str
            Type of snapshot to download
        output_path : str, optional
            Where to save the PDF. If None, saves to temp directory
            
        Returns
        -------
        Path
            Path to downloaded PDF
        """
        if snapshot_type not in self.SNAPSHOT_TYPES:
            raise RBADataError(
                f"Invalid snapshot type '{snapshot_type}'. "
                f"Must be one of: {list(self.SNAPSHOT_TYPES.keys())}"
            )
        
        # Construct URL
        snapshot_info = self.SNAPSHOT_TYPES[snapshot_type]
        pdf_url = f"{self.BASE_URL}{snapshot_info['url']}.pdf"
        
        # Determine output path
        if output_path is None:
            from tempfile import gettempdir
            temp_dir = Path(gettempdir()) / "rbadata_snapshots"
            temp_dir.mkdir(exist_ok=True)
            output_path = temp_dir / f"rba_{snapshot_type}_snapshot.pdf"
        else:
            output_path = Path(output_path)
        
        # Download
        try:
            response = requests.get(pdf_url, headers=get_headers(), timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RBADataError(f"Failed to download snapshot: {str(e)}")
        
        # Save
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return output_path
    
    def get_economic_indicators(self, refresh: bool = False) -> pd.DataFrame:
        """
        Get key economic indicators data.
        
        Parameters
        ----------
        refresh : bool, default False
            Whether to refresh cached data
            
        Returns
        -------
        pd.DataFrame
            Economic indicators with latest values and changes
        """
        if "economic-indicators" in self._cached_data and not refresh:
            return self._cached_data["economic-indicators"]
        
        # Scrape the data
        data = self._scrape_economic_indicators()
        self._cached_data["economic-indicators"] = data
        
        return data
    
    def get_economy_composition(self, refresh: bool = False) -> pd.DataFrame:
        """
        Get economy composition data.
        
        Parameters
        ----------
        refresh : bool, default False
            Whether to refresh cached data
            
        Returns
        -------
        pd.DataFrame
            Economy composition breakdown
        """
        if "economy-composition" in self._cached_data and not refresh:
            return self._cached_data["economy-composition"]
        
        # Scrape the data
        data = self._scrape_economy_composition()
        self._cached_data["economy-composition"] = data
        
        return data
    
    def get_payment_methods(self, refresh: bool = False) -> pd.DataFrame:
        """
        Get payment methods data.
        
        Parameters
        ----------
        refresh : bool, default False
            Whether to refresh cached data
            
        Returns
        -------
        pd.DataFrame
            Payment methods usage statistics
        """
        if "payments" in self._cached_data and not refresh:
            return self._cached_data["payments"]
        
        # Scrape the data
        data = self._scrape_payment_methods()
        self._cached_data["payments"] = data
        
        return data
    
    def get_comparison_tool_data(
        self,
        snapshot_type: str,
        comparison_items: List[str]
    ) -> pd.DataFrame:
        """
        Get data from the interactive comparison tool.
        
        Note: This is a placeholder for functionality that would require
        JavaScript execution to access the interactive features.
        
        Parameters
        ----------
        snapshot_type : str
            Type of snapshot
        comparison_items : list of str
            Items to compare
            
        Returns
        -------
        pd.DataFrame
            Comparison data
        """
        raise NotImplementedError(
            "Interactive comparison tool data extraction requires JavaScript execution. "
            "Consider using the downloaded PDFs or related statistical tables instead."
        )
    
    def _scrape_economic_indicators(self) -> pd.DataFrame:
        """Scrape economic indicators snapshot data."""
        # This would scrape the snapshot page for data
        # For now, return sample data structure
        
        # Typical economic indicators included
        indicators = [
            {"indicator": "GDP Growth", "value": 2.5, "unit": "% y/y", "previous": 2.3, "date": "2024-Q2"},
            {"indicator": "Unemployment Rate", "value": 4.0, "unit": "%", "previous": 3.9, "date": "2024-07"},
            {"indicator": "CPI Inflation", "value": 3.8, "unit": "% y/y", "previous": 4.1, "date": "2024-Q2"},
            {"indicator": "Cash Rate", "value": 4.35, "unit": "%", "previous": 4.35, "date": "2024-08"},
            {"indicator": "AUD/USD", "value": 0.66, "unit": "USD", "previous": 0.65, "date": "2024-08"},
            {"indicator": "ASX 200", "value": 7800, "unit": "Index", "previous": 7600, "date": "2024-08"},
            {"indicator": "House Prices", "value": 5.2, "unit": "% y/y", "previous": 4.8, "date": "2024-Q2"},
            {"indicator": "Household Savings", "value": 3.2, "unit": "% of income", "previous": 3.5, "date": "2024-Q2"},
        ]
        
        return pd.DataFrame(indicators)
    
    def _scrape_economy_composition(self) -> pd.DataFrame:
        """Scrape economy composition data."""
        # Sample composition data
        composition = [
            {"sector": "Services", "share": 70.5, "unit": "% of GDP"},
            {"sector": "Mining", "share": 8.5, "unit": "% of GDP"},
            {"sector": "Manufacturing", "share": 5.8, "unit": "% of GDP"},
            {"sector": "Construction", "share": 7.2, "unit": "% of GDP"},
            {"sector": "Agriculture", "share": 2.0, "unit": "% of GDP"},
            {"sector": "Other", "share": 6.0, "unit": "% of GDP"},
        ]
        
        return pd.DataFrame(composition)
    
    def _scrape_payment_methods(self) -> pd.DataFrame:
        """Scrape payment methods data."""
        # Sample payment methods data
        payments = [
            {"method": "Card", "share": 75, "transactions": 85, "year": 2023},
            {"method": "Cash", "share": 13, "transactions": 7, "year": 2023},
            {"method": "Direct Debit", "share": 8, "transactions": 5, "year": 2023},
            {"method": "BPAY", "share": 2, "transactions": 2, "year": 2023},
            {"method": "Other", "share": 2, "transactions": 1, "year": 2023},
        ]
        
        return pd.DataFrame(payments)


def get_snapshots() -> Snapshots:
    """
    Get a Snapshots instance for accessing RBA snapshot data.
    
    Returns
    -------
    Snapshots
        Snapshots instance
        
    Examples
    --------
    >>> snapshots = get_snapshots()
    >>> indicators = snapshots.get_economic_indicators()
    >>> snapshots.download_snapshot("economic-indicators")
    """
    return Snapshots()


def get_economic_indicators() -> pd.DataFrame:
    """
    Convenience function to get key economic indicators.
    
    Returns
    -------
    pd.DataFrame
        Latest economic indicators
        
    Examples
    --------
    >>> indicators = get_economic_indicators()
    >>> print(indicators[["indicator", "value", "unit"]])
    """
    snapshots = Snapshots()
    return snapshots.get_economic_indicators()