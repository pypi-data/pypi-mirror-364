"""
Configuration and settings for rbadata
"""

import os
from typing import Dict, Optional


def get_download_method() -> Optional[str]:
    """
    Get the download method from environment variable.
    
    This is useful for corporate networks that require special handling.
    
    Returns
    -------
    str or None
        Download method (e.g., "wininet") or None for default
    """
    return os.environ.get("RBADATA_DL_METHOD")


def get_headers() -> Dict[str, str]:
    """
    Get HTTP headers for RBA requests.
    
    Returns
    -------
    dict
        Headers to use for HTTP requests
    """
    return {
        "User-Agent": "rbadata/0.1.0 (Python package for accessing RBA data)",
        "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }