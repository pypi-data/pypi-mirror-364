"""
Web scraping functions for RBA data
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from .exceptions import RBADataError


def scrape_table_list() -> pd.DataFrame:
    """
    Scrape the list of available tables from the RBA website.
    
    Returns
    -------
    pd.DataFrame
        DataFrame containing table information
    """
    tables_data = []
    
    # Scrape current tables
    current_tables = _scrape_statistical_tables()
    for table in current_tables:
        table["current_or_historical"] = "current"
        tables_data.append(table)
    
    # Scrape historical tables
    historical_tables = _scrape_historical_tables()
    for table in historical_tables:
        table["current_or_historical"] = "historical"
        tables_data.append(table)
    
    # Add special exchange rate tables
    exchange_tables = _get_exchange_rate_tables()
    tables_data.extend(exchange_tables)
    
    df = pd.DataFrame(tables_data)
    
    # Determine which tables are readable
    df["readable"] = ~df["no"].isin(_get_non_readable_tables())
    
    return df


def _scrape_statistical_tables() -> List[Dict[str, str]]:
    """Scrape current statistical tables from RBA website."""
    url = "https://www.rba.gov.au/statistics/tables/"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RBADataError(f"Failed to fetch RBA tables page: {str(e)}")
    
    soup = BeautifulSoup(response.content, "html.parser")
    tables = []
    
    # Find all table links
    # The structure is typically: <a href="...">Table_No - Title</a>
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        text = link.get_text(strip=True)
        
        # Skip non-table links
        if not href or "xls" not in href:
            continue
        
        # Extract table number and title
        if " – " in text or " - " in text:
            parts = text.replace(" – ", " - ").split(" - ", 1)
            if len(parts) == 2:
                table_no = parts[0].strip()
                title = parts[1].strip()
                
                # Build full URL
                if not href.startswith("http"):
                    href = f"https://www.rba.gov.au{href}"
                
                tables.append({
                    "no": table_no,
                    "title": title,
                    "url": href
                })
    
    return tables


def _scrape_historical_tables() -> List[Dict[str, str]]:
    """Scrape historical data tables from RBA website."""
    url = "https://www.rba.gov.au/statistics/historical-data.html"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RBADataError(f"Failed to fetch RBA historical data page: {str(e)}")
    
    soup = BeautifulSoup(response.content, "html.parser")
    tables = []
    
    # Historical tables have a similar structure
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        text = link.get_text(strip=True)
        
        # Skip non-Excel links
        if not href or "xls" not in href:
            continue
        
        # Extract table info
        if " – " in text or " - " in text:
            parts = text.replace(" – ", " - ").split(" - ", 1)
            if len(parts) == 2:
                table_no = parts[0].strip()
                title = parts[1].strip()
                
                # Build full URL
                if not href.startswith("http"):
                    href = f"https://www.rba.gov.au{href}"
                
                tables.append({
                    "no": table_no,
                    "title": title,
                    "url": href
                })
    
    return tables


def _get_exchange_rate_tables() -> List[Dict[str, str]]:
    """Get special exchange rate tables that don't have standard numbers."""
    base_url = "https://www.rba.gov.au/statistics/historical-data.html#exchange-rates"
    
    exchange_tables = [
        {
            "no": "ex_daily_8386",
            "title": "Exchange Rates – Daily – 1983 to 1986",
            "url": f"{base_url}",
            "current_or_historical": "historical",
            "readable": True
        },
        {
            "no": "ex_daily_8790",
            "title": "Exchange Rates – Daily – 1987 to 1990",
            "url": f"{base_url}",
            "current_or_historical": "historical",
            "readable": True
        },
        {
            "no": "ex_daily_9194",
            "title": "Exchange Rates – Daily – 1991 to 1994",
            "url": f"{base_url}",
            "current_or_historical": "historical",
            "readable": True
        },
        {
            "no": "ex_daily_9598",
            "title": "Exchange Rates – Daily – 1995 to 1998",
            "url": f"{base_url}",
            "current_or_historical": "historical",
            "readable": True
        },
        {
            "no": "ex_daily_9902",
            "title": "Exchange Rates – Daily – 1999 to 2002",
            "url": f"{base_url}",
            "current_or_historical": "historical",
            "readable": True
        },
        {
            "no": "ex_daily_0306",
            "title": "Exchange Rates – Daily – 2003 to 2006",
            "url": f"{base_url}",
            "current_or_historical": "historical",
            "readable": True
        },
        {
            "no": "ex_daily_0709",
            "title": "Exchange Rates – Daily – 2007 to 2009",
            "url": f"{base_url}",
            "current_or_historical": "historical",
            "readable": True
        },
        {
            "no": "ex_daily_1013",
            "title": "Exchange Rates – Daily – 2010 to 2013",
            "url": f"{base_url}",
            "current_or_historical": "historical",
            "readable": True
        },
        {
            "no": "ex_daily_1417",
            "title": "Exchange Rates – Daily – 2014 to 2017",
            "url": f"{base_url}",
            "current_or_historical": "historical",
            "readable": True
        },
        {
            "no": "ex_daily_1822",
            "title": "Exchange Rates – Daily – 2018 to 2022",
            "url": f"{base_url}",
            "current_or_historical": "historical",
            "readable": True
        },
        {
            "no": "ex_daily_23cur",
            "title": "Exchange Rates – Daily – 2023 to Current",
            "url": f"{base_url}",
            "current_or_historical": "historical",
            "readable": True
        },
        {
            "no": "ex_monthly_10cur",
            "title": "Exchange Rates – Monthly – January 2010 to latest complete month of current year",
            "url": f"{base_url}",
            "current_or_historical": "historical",
            "readable": True
        },
        {
            "no": "ex_monthly_6909",
            "title": "Exchange Rates – Monthly – July 1969 to December 2009",
            "url": f"{base_url}",
            "current_or_historical": "historical",
            "readable": True
        }
    ]
    
    return exchange_tables


def _get_non_readable_tables() -> List[str]:
    """Get list of table numbers that cannot be read by the package."""
    return [
        "E3", "E4", "E5", "E6", "E7",  # Distribution tables
        "J1", "J2",  # Individual banks tables
        "F16", "F17",  # Old format tables
    ]