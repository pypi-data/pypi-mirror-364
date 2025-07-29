"""
Functions for downloading RBA data files
"""

import os
import time
import tempfile
from pathlib import Path
from typing import Optional
import requests
from .exceptions import RBADataError
from .config import get_download_method, get_headers


def download_rba(url: str, table_no: str) -> Path:
    """
    Download an RBA Excel file to a temporary location.
    
    Parameters
    ----------
    url : str
        URL of the Excel file to download
    table_no : str
        Table number (used for naming the file)
        
    Returns
    -------
    Path
        Path to the downloaded Excel file
        
    Raises
    ------
    RBADataError
        If the download fails after retries
    """
    # Create temporary directory
    temp_dir = Path(tempfile.gettempdir()) / "rbadata_downloads"
    temp_dir.mkdir(exist_ok=True)
    
    # Generate filename
    filename = f"rba_table_{table_no}.xlsx"
    filepath = temp_dir / filename
    
    # Try to download with retry logic
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            response = _download_file(url)
            
            # Save to file
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            return filepath
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Download failed, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise RBADataError(f"Failed to download file after {max_retries} attempts: {str(e)}")


def _download_file(url: str) -> requests.Response:
    """
    Download a file using requests with appropriate headers and timeout.
    
    Parameters
    ----------
    url : str
        URL to download
        
    Returns
    -------
    requests.Response
        Response object containing the downloaded content
    """
    headers = get_headers()
    timeout = 30  # seconds
    
    # Use custom download method if specified
    download_method = get_download_method()
    
    if download_method == "wininet":
        # For corporate networks, we might need special handling
        # For now, we'll use standard requests but this could be extended
        pass
    
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    
    return response


def url_exists(url: str) -> bool:
    """
    Check if a URL exists and is accessible.
    
    Parameters
    ----------
    url : str
        URL to check
        
    Returns
    -------
    bool
        True if the URL exists and returns a successful status code
    """
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False