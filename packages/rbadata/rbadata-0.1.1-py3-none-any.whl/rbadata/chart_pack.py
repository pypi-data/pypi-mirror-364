"""
RBA Chart Pack data extraction and management
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .exceptions import RBADataError
from .config import get_headers
from .download import download_rba


class ChartPack:
    """
    Access and extract data from RBA Chart Pack.
    
    The RBA Chart Pack provides graphical summaries of macroeconomic and 
    financial market trends, released 8 times per year.
    
    Examples
    --------
    >>> cp = ChartPack()
    >>> # Get available chart categories
    >>> categories = cp.get_categories()
    
    >>> # Get charts for a specific category
    >>> inflation_charts = cp.get_charts_by_category("inflation")
    
    >>> # Download the full chart pack PDF
    >>> cp.download_chart_pack("2024-07")
    """
    
    BASE_URL = "https://www.rba.gov.au/chart-pack"
    
    def __init__(self):
        """Initialize ChartPack instance."""
        self._categories = None
        self._charts = None
        self._last_update = None
    
    def get_categories(self, refresh: bool = False) -> List[str]:
        """
        Get available chart categories.
        
        Parameters
        ----------
        refresh : bool, default False
            Whether to refresh the category list from the website
            
        Returns
        -------
        list of str
            Available chart categories
        """
        if self._categories is not None and not refresh:
            return self._categories
        
        self._scrape_chart_pack_page()
        return self._categories
    
    def get_charts_by_category(
        self,
        category: str,
        refresh: bool = False
    ) -> List[Dict[str, str]]:
        """
        Get charts for a specific category.
        
        Parameters
        ----------
        category : str
            Chart category (e.g., "inflation", "growth", "financial-markets")
        refresh : bool, default False
            Whether to refresh the chart data
            
        Returns
        -------
        list of dict
            List of charts with metadata
        """
        if self._charts is None or refresh:
            self._scrape_chart_pack_page()
        
        # Normalize category name
        category_lower = category.lower().replace(" ", "-")
        
        if category_lower not in [c.lower().replace(" ", "-") for c in self._categories]:
            raise RBADataError(f"Category '{category}' not found. Available: {self._categories}")
        
        # Return charts for this category
        return [c for c in self._charts if c["category"].lower().replace(" ", "-") == category_lower]
    
    def get_all_charts(self, refresh: bool = False) -> List[Dict[str, str]]:
        """
        Get all available charts.
        
        Parameters
        ----------
        refresh : bool, default False
            Whether to refresh the chart data
            
        Returns
        -------
        list of dict
            All charts with metadata
        """
        if self._charts is None or refresh:
            self._scrape_chart_pack_page()
        
        return self._charts
    
    def download_chart_pack(
        self,
        date: Optional[Union[str, datetime]] = None,
        output_path: Optional[str] = None
    ) -> Path:
        """
        Download the full Chart Pack PDF.
        
        Parameters
        ----------
        date : str or datetime, optional
            Date of the chart pack to download (e.g., "2024-07")
            If None, downloads the latest available
        output_path : str, optional
            Where to save the PDF. If None, saves to temp directory
            
        Returns
        -------
        Path
            Path to the downloaded PDF
        """
        # Get the PDF URL
        pdf_url = self._get_chart_pack_pdf_url(date)
        
        # Determine output path
        if output_path is None:
            from tempfile import gettempdir
            temp_dir = Path(gettempdir()) / "rbadata_charts"
            temp_dir.mkdir(exist_ok=True)
            
            # Generate filename from URL or date
            if date:
                filename = f"rba_chart_pack_{date}.pdf"
            else:
                filename = "rba_chart_pack_latest.pdf"
            
            output_path = temp_dir / filename
        else:
            output_path = Path(output_path)
        
        # Download the file
        response = requests.get(pdf_url, headers=get_headers(), timeout=30)
        response.raise_for_status()
        
        # Save to file
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return output_path
    
    def get_chart_data(self, chart_id: str) -> pd.DataFrame:
        """
        Extract data from a specific chart.
        
        Note: This is a placeholder for future functionality to extract
        actual data values from charts. Currently, the RBA provides charts
        as images/PDFs without easily accessible data APIs.
        
        Parameters
        ----------
        chart_id : str
            Chart identifier
            
        Returns
        -------
        pd.DataFrame
            Chart data (if available)
        """
        raise NotImplementedError(
            "Direct chart data extraction is not yet implemented. "
            "Consider using the relevant statistical tables instead."
        )
    
    def get_latest_release_date(self) -> datetime:
        """
        Get the date of the latest Chart Pack release.
        
        Returns
        -------
        datetime
            Date of the latest release
        """
        if self._last_update is None:
            self._scrape_chart_pack_page()
        
        return self._last_update
    
    def _scrape_chart_pack_page(self):
        """Scrape the Chart Pack page to get categories and charts."""
        url = f"{self.BASE_URL}/"
        
        try:
            response = requests.get(url, headers=get_headers(), timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RBADataError(f"Failed to access Chart Pack page: {str(e)}")
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract categories from navigation or main content
        categories = []
        charts = []
        
        # Look for chart categories in the navigation
        nav_items = soup.find_all("a", href=re.compile(r"#[\w-]+"))
        for item in nav_items:
            category = item.get_text(strip=True)
            if category and category not in ["Overview", "Download"]:
                categories.append(category)
        
        # Extract individual charts
        # Charts are typically in sections with headings
        sections = soup.find_all(["section", "div"], class_=re.compile(r"chart|graph"))
        
        for section in sections:
            # Try to extract chart information
            title_elem = section.find(["h2", "h3", "h4"])
            if title_elem:
                chart_info = {
                    "title": title_elem.get_text(strip=True),
                    "category": self._guess_category(title_elem.get_text(strip=True)),
                    "id": section.get("id", ""),
                    "url": ""  # Would need to extract if individual chart URLs exist
                }
                charts.append(chart_info)
        
        # Extract release date
        date_pattern = re.compile(r"(\d{1,2}\s+\w+\s+\d{4})")
        date_text = soup.find(string=date_pattern)
        if date_text:
            try:
                self._last_update = pd.to_datetime(date_pattern.search(date_text).group(1))
            except:
                self._last_update = None
        
        # Store results
        self._categories = categories if categories else self._get_default_categories()
        self._charts = charts if charts else self._get_default_charts()
    
    def _get_chart_pack_pdf_url(self, date: Optional[Union[str, datetime]] = None) -> str:
        """Get the URL for the Chart Pack PDF."""
        # If no date specified, get the latest
        if date is None:
            return f"{self.BASE_URL}/pdf/chart-pack.pdf"
        
        # Format date for URL
        if isinstance(date, datetime):
            date_str = date.strftime("%Y%m")
        else:
            # Assume format like "2024-07"
            date_str = date.replace("-", "")
        
        # Construct URL (this is an approximation - actual URL pattern may vary)
        return f"{self.BASE_URL}/pdf/chart-pack-{date_str}.pdf"
    
    def _guess_category(self, title: str) -> str:
        """Guess the category based on chart title."""
        title_lower = title.lower()
        
        # Check more specific patterns first - order matters!
        # Priority order based on test expectations:
        # 1. Housing (most specific - "house prices" shouldn't match "price")
        # 2. Inflation/CPI (specific economic indicator)
        # 3. Credit/Money (before "growth")
        # 4. Exchange rates (before general "rate")
        # 5. World Economy (contains country names)
        # 6. Australian Growth
        # 7. Labour Market
        # 8. Interest Rates (most general - contains "rate")
        
        if any(word in title_lower for word in ["house", "property", "dwelling"]):
            return "Housing"
        elif any(word in title_lower for word in ["inflation", "cpi", "price"]):
            return "Inflation"
        elif any(word in title_lower for word in ["credit", "lending", "debt", "money"]):
            return "Credit and Money"
        elif any(word in title_lower for word in ["exchange", "currency", "dollar"]):
            return "Exchange Rates"
        elif any(word in title_lower for word in ["china", "europe", "global"]):
            return "World Economy"
        elif re.search(r'\bus\b', title_lower):  # Match "US" as a word, not in "USD"
            return "World Economy"
        elif any(word in title_lower for word in ["gdp", "growth", "output"]):
            return "Australian Growth"
        elif any(word in title_lower for word in ["unemployment", "labour", "labor", "employment"]):
            return "Labour Market"
        elif any(word in title_lower for word in ["interest", "rate", "yield", "cash rate"]):
            return "Interest Rates"
        else:
            return "Other"
    
    def _get_default_categories(self) -> List[str]:
        """Return default chart categories based on typical RBA Chart Pack structure."""
        return [
            "World Economy",
            "Australian Growth", 
            "Labour Market",
            "Inflation",
            "Interest Rates",
            "Exchange Rates",
            "Credit and Money",
            "Housing",
            "Financial Markets"
        ]
    
    def _get_default_charts(self) -> List[Dict[str, str]]:
        """Return default chart list based on typical RBA Chart Pack content."""
        return [
            {"title": "GDP Growth - Selected Economies", "category": "World Economy", "id": "gdp-growth", "url": ""},
            {"title": "Unemployment Rates - Selected Economies", "category": "World Economy", "id": "unemployment-global", "url": ""},
            {"title": "Australian GDP Growth", "category": "Australian Growth", "id": "aus-gdp", "url": ""},
            {"title": "Household Consumption", "category": "Australian Growth", "id": "consumption", "url": ""},
            {"title": "Business Investment", "category": "Australian Growth", "id": "investment", "url": ""},
            {"title": "Unemployment Rate", "category": "Labour Market", "id": "unemployment", "url": ""},
            {"title": "Employment Growth", "category": "Labour Market", "id": "employment", "url": ""},
            {"title": "Consumer Price Inflation", "category": "Inflation", "id": "cpi", "url": ""},
            {"title": "Underlying Inflation", "category": "Inflation", "id": "underlying", "url": ""},
            {"title": "Cash Rate", "category": "Interest Rates", "id": "cash-rate", "url": ""},
            {"title": "Australian Dollar", "category": "Exchange Rates", "id": "aud", "url": ""},
            {"title": "Credit Growth", "category": "Credit and Money", "id": "credit", "url": ""},
            {"title": "Housing Prices", "category": "Housing", "id": "house-prices", "url": ""},
        ]


def get_chart_pack() -> ChartPack:
    """
    Get a ChartPack instance for accessing RBA Chart Pack data.
    
    Returns
    -------
    ChartPack
        ChartPack instance
        
    Examples
    --------
    >>> cp = get_chart_pack()
    >>> categories = cp.get_categories()
    >>> cp.download_chart_pack()
    """
    return ChartPack()