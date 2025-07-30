"""
Caching functionality for rbadata with configurable TTL and storage backends.

This module provides caching to reduce redundant downloads and improve performance.
Supports both in-memory and disk-based caching with automatic expiration.
"""

import hashlib
import json
import pickle
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd

from .exceptions import CacheError


class CacheBackend:
    """Abstract base class for cache backends."""

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache with optional TTL in seconds."""
        raise NotImplementedError

    def delete(self, key: str) -> None:
        """Remove value from cache."""
        raise NotImplementedError

    def clear(self) -> None:
        """Clear all cached values."""
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        raise NotImplementedError


class MemoryCache(CacheBackend):
    """
    In-memory cache backend.

    Fast but data is lost when process ends.
    Good for short-lived scripts and testing.
    """

    def __init__(self):
        """Initialize memory cache."""
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from memory cache."""
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Check expiration
        if entry["expires_at"] and time.time() > entry["expires_at"]:
            del self._cache[key]
            return None

        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in memory cache."""
        expires_at = None
        if ttl:
            expires_at = time.time() + ttl

        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": time.time(),
        }

    def delete(self, key: str) -> None:
        """Remove value from memory cache."""
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        if key not in self._cache:
            return False

        entry = self._cache[key]
        if entry["expires_at"] and time.time() > entry["expires_at"]:
            del self._cache[key]
            return False

        return True


class DiskCache(CacheBackend):
    """
    Disk-based cache backend.

    Slower than memory but persists between runs.
    Good for production use with large datasets.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize disk cache.

        Parameters
        ----------
        cache_dir : Path, optional
            Directory for cache files. Defaults to system temp directory.
        """
        if cache_dir is None:
            cache_dir = Path(tempfile.gettempdir()) / "rbadata_cache"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key."""
        # Use hash to avoid filesystem issues with special characters
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def _get_meta_path(self, key: str) -> Path:
        """Get metadata file path for cache key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.meta"

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from disk cache."""
        cache_path = self._get_cache_path(key)
        meta_path = self._get_meta_path(key)

        if not cache_path.exists() or not meta_path.exists():
            return None

        try:
            # Check metadata
            with open(meta_path, "r") as f:
                meta = json.load(f)

            # Check expiration
            if meta.get("expires_at") and time.time() > meta["expires_at"]:
                self.delete(key)
                return None

            # Load cached value
            with open(cache_path, "rb") as f:
                return pickle.load(f)

        except Exception as e:
            raise CacheError(f"Failed to read cache for key {key}: {str(e)}")

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in disk cache."""
        cache_path = self._get_cache_path(key)
        meta_path = self._get_meta_path(key)

        try:
            # Save value
            with open(cache_path, "wb") as f:
                pickle.dump(value, f)

            # Save metadata
            meta = {
                "created_at": time.time(),
                "expires_at": time.time() + ttl if ttl else None,
                "key": key,
            }
            with open(meta_path, "w") as f:
                json.dump(meta, f)

        except Exception as e:
            # Clean up on failure
            cache_path.unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)
            raise CacheError(f"Failed to write cache for key {key}: {str(e)}")

    def delete(self, key: str) -> None:
        """Remove value from disk cache."""
        cache_path = self._get_cache_path(key)
        meta_path = self._get_meta_path(key)

        cache_path.unlink(missing_ok=True)
        meta_path.unlink(missing_ok=True)

    def clear(self) -> None:
        """Clear all cached values."""
        for file in self.cache_dir.glob("*.cache"):
            file.unlink()
        for file in self.cache_dir.glob("*.meta"):
            file.unlink()

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        value = self.get(key)
        return value is not None


class RBACache:
    """
    Main cache interface for rbadata.

    Provides a unified interface for caching RBA data with:
    - Configurable TTL (time-to-live)
    - Multiple backend support
    - Automatic key generation
    - DataFrame serialization
    """

    def __init__(
        self,
        backend: Optional[CacheBackend] = None,
        default_ttl: int = 3600,
        enabled: bool = True,
    ):
        """
        Initialize RBA cache.

        Parameters
        ----------
        backend : CacheBackend, optional
            Cache backend to use. Defaults to MemoryCache.
        default_ttl : int, default 3600
            Default TTL in seconds (1 hour)
        enabled : bool, default True
            Whether caching is enabled
        """
        self.backend = backend or MemoryCache()
        self.default_ttl = default_ttl
        self.enabled = enabled

    def _generate_key(
        self,
        table_no: Optional[str] = None,
        series_id: Optional[Union[str, list]] = None,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        **kwargs,
    ) -> str:
        """Generate cache key from parameters."""
        parts = []

        if table_no:
            parts.append(f"table:{table_no}")

        if series_id:
            if isinstance(series_id, list):
                series_id = ",".join(sorted(series_id))
            parts.append(f"series:{series_id}")

        if start_date:
            parts.append(f"start:{start_date}")

        if end_date:
            parts.append(f"end:{end_date}")

        # Add any additional kwargs
        for k, v in sorted(kwargs.items()):
            parts.append(f"{k}:{v}")

        return "|".join(parts)

    def get_dataframe(
        self,
        table_no: Optional[str] = None,
        series_id: Optional[Union[str, list]] = None,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        **kwargs,
    ) -> Optional[pd.DataFrame]:
        """
        Get cached DataFrame if available.

        Parameters match those of read_rba() function.

        Returns
        -------
        pd.DataFrame or None
            Cached DataFrame if found and valid, None otherwise
        """
        if not self.enabled:
            return None

        key = self._generate_key(table_no, series_id, start_date, end_date, **kwargs)
        value = self.backend.get(key)

        if value is not None and isinstance(value, pd.DataFrame):
            return value.copy()  # Return copy to prevent modification

        return None

    def set_dataframe(
        self,
        df: pd.DataFrame,
        table_no: Optional[str] = None,
        series_id: Optional[Union[str, list]] = None,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        ttl: Optional[int] = None,
        **kwargs,
    ) -> None:
        """
        Cache a DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to cache
        ttl : int, optional
            TTL in seconds. Uses default_ttl if not specified.
        Other parameters match those of read_rba() function.
        """
        if not self.enabled:
            return

        key = self._generate_key(table_no, series_id, start_date, end_date, **kwargs)
        ttl = ttl or self.default_ttl

        self.backend.set(key, df.copy(), ttl)

    def get_csv(self, table_no: str) -> Optional[str]:
        """Get cached CSV content."""
        if not self.enabled:
            return None

        key = f"csv:{table_no}"
        return self.backend.get(key)

    def set_csv(self, table_no: str, content: str, ttl: Optional[int] = None) -> None:
        """Cache CSV content."""
        if not self.enabled:
            return

        key = f"csv:{table_no}"
        ttl = ttl or self.default_ttl
        self.backend.set(key, content, ttl)

    def clear(self) -> None:
        """Clear all cached data."""
        self.backend.clear()

    def enable(self) -> None:
        """Enable caching."""
        self.enabled = True

    def disable(self) -> None:
        """Disable caching."""
        self.enabled = False


# Global cache instance
_global_cache: Optional[RBACache] = None


def get_cache() -> RBACache:
    """
    Get the global cache instance.

    Creates a default cache if none exists.
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = RBACache()
    return _global_cache


def set_cache(cache: RBACache) -> None:
    """Set the global cache instance."""
    global _global_cache
    _global_cache = cache


def configure_cache(
    backend: str = "memory",
    cache_dir: Optional[Union[str, Path]] = None,
    default_ttl: int = 3600,
    enabled: bool = True,
) -> RBACache:
    """
    Configure the global cache.

    Parameters
    ----------
    backend : str, default "memory"
        Cache backend type: "memory" or "disk"
    cache_dir : str or Path, optional
        Directory for disk cache
    default_ttl : int, default 3600
        Default TTL in seconds
    enabled : bool, default True
        Whether caching is enabled

    Returns
    -------
    RBACache
        Configured cache instance
    """
    if backend == "memory":
        backend_obj = MemoryCache()
    elif backend == "disk":
        backend_obj = DiskCache(Path(cache_dir) if cache_dir else None)
    else:
        raise ValueError(f"Unknown cache backend: {backend}")

    cache = RBACache(backend_obj, default_ttl, enabled)
    set_cache(cache)

    return cache
