"""
Tests for caching functionality.
"""

import json
import time
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from rbadata.cache import (
    MemoryCache,
    DiskCache,
    RBACache,
    configure_cache,
    get_cache,
    set_cache,
)
from rbadata.exceptions import CacheError


class TestMemoryCache:
    """Test in-memory cache backend."""
    
    def test_set_and_get(self):
        """Test basic set and get operations."""
        cache = MemoryCache()
        
        # Set value
        cache.set('key1', 'value1')
        
        # Get value
        assert cache.get('key1') == 'value1'
        
    def test_get_missing_key(self):
        """Test getting non-existent key returns None."""
        cache = MemoryCache()
        assert cache.get('missing') is None
        
    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = MemoryCache()
        
        # Set with 0.1 second TTL
        cache.set('key1', 'value1', ttl=0.1)
        
        # Should exist immediately
        assert cache.get('key1') == 'value1'
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be expired
        assert cache.get('key1') is None
        
    def test_delete(self):
        """Test deleting keys."""
        cache = MemoryCache()
        
        cache.set('key1', 'value1')
        assert cache.exists('key1')
        
        cache.delete('key1')
        assert not cache.exists('key1')
        
    def test_clear(self):
        """Test clearing all cache."""
        cache = MemoryCache()
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        cache.clear()
        
        assert not cache.exists('key1')
        assert not cache.exists('key2')
        
    def test_exists_with_expiration(self):
        """Test exists() checks expiration."""
        cache = MemoryCache()
        
        cache.set('key1', 'value1', ttl=0.1)
        assert cache.exists('key1')
        
        time.sleep(0.2)
        assert not cache.exists('key1')


class TestDiskCache:
    """Test disk-based cache backend."""
    
    def test_set_and_get(self):
        """Test basic set and get operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = DiskCache(Path(tmpdir))
            
            # Set value
            cache.set('key1', {'data': [1, 2, 3]})
            
            # Get value
            result = cache.get('key1')
            assert result == {'data': [1, 2, 3]}
            
    def test_cache_persistence(self):
        """Test cache persists across instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # First instance
            cache1 = DiskCache(Path(tmpdir))
            cache1.set('key1', 'persistent_value')
            
            # Second instance
            cache2 = DiskCache(Path(tmpdir))
            assert cache2.get('key1') == 'persistent_value'
            
    def test_ttl_expiration(self):
        """Test TTL expiration for disk cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = DiskCache(Path(tmpdir))
            
            cache.set('key1', 'value1', ttl=0.1)
            assert cache.get('key1') == 'value1'
            
            time.sleep(0.2)
            assert cache.get('key1') is None
            
    def test_delete_and_clear(self):
        """Test delete and clear operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = DiskCache(Path(tmpdir))
            
            cache.set('key1', 'value1')
            cache.set('key2', 'value2')
            
            # Delete one
            cache.delete('key1')
            assert not cache.exists('key1')
            assert cache.exists('key2')
            
            # Clear all
            cache.clear()
            assert not cache.exists('key2')
            
    def test_cache_error_handling(self):
        """Test error handling for disk operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = DiskCache(Path(tmpdir))
            
            # Create a corrupted cache file by writing invalid pickle data
            key = 'test_key'
            cache_path = cache._get_cache_path(key)
            meta_path = cache._get_meta_path(key)
            
            # Create valid metadata
            meta = {'expires_at': None, 'created_at': time.time()}
            with open(meta_path, 'w') as f:
                json.dump(meta, f)
            
            # Create invalid pickle data
            with open(cache_path, 'wb') as f:
                f.write(b'invalid pickle data')
            
            # This should raise CacheError due to invalid pickle
            with pytest.raises(CacheError):
                cache.get('test_key')


class TestRBACache:
    """Test main RBA cache interface."""
    
    def test_dataframe_caching(self):
        """Test caching pandas DataFrames."""
        cache = RBACache()
        
        # Create test DataFrame
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=3),
            'series_id': ['TEST1'] * 3,
            'value': [1.0, 2.0, 3.0]
        })
        
        # Cache DataFrame
        cache.set_dataframe(df, table_no='F1')
        
        # Retrieve DataFrame
        cached_df = cache.get_dataframe(table_no='F1')
        
        assert cached_df is not None
        pd.testing.assert_frame_equal(df, cached_df)
        
    def test_cache_key_generation(self):
        """Test cache key generation from parameters."""
        cache = RBACache()
        
        # Test various parameter combinations
        key1 = cache._generate_key(table_no='F1')
        assert 'table:F1' in key1
        
        key2 = cache._generate_key(series_id=['TEST1', 'TEST2'])
        assert 'series:TEST1,TEST2' in key2
        
        key3 = cache._generate_key(
            table_no='F1',
            start_date='2023-01-01',
            end_date='2023-12-31',
            custom_param='value'
        )
        assert 'table:F1' in key3
        assert 'start:2023-01-01' in key3
        assert 'end:2023-12-31' in key3
        assert 'custom_param:value' in key3
        
    def test_csv_caching(self):
        """Test CSV content caching."""
        cache = RBACache()
        
        csv_content = "Series ID,TEST1\n01-Jan-2023,1.5"
        
        cache.set_csv('F1', csv_content)
        cached = cache.get_csv('F1')
        
        assert cached == csv_content
        
    def test_cache_disabled(self):
        """Test cache when disabled."""
        cache = RBACache(enabled=False)
        
        # Should not cache when disabled
        cache.set_csv('F1', 'content')
        assert cache.get_csv('F1') is None
        
        # Enable and test
        cache.enable()
        cache.set_csv('F1', 'content')
        assert cache.get_csv('F1') == 'content'
        
        # Disable again
        cache.disable()
        assert cache.get_csv('F1') is None
        
    def test_custom_ttl(self):
        """Test custom TTL settings."""
        cache = RBACache(default_ttl=1)  # 1 second default
        
        # Use default TTL
        cache.set_csv('key1', 'value1')
        
        # Use custom TTL
        cache.set_csv('key2', 'value2', ttl=10)  # 10 seconds
        
        # Both should exist initially
        assert cache.get_csv('key1') == 'value1'
        assert cache.get_csv('key2') == 'value2'
        
        # After 1.1 seconds, only key2 should exist
        time.sleep(1.1)
        assert cache.get_csv('key1') is None
        assert cache.get_csv('key2') == 'value2'


class TestCacheConfiguration:
    """Test cache configuration functions."""
    
    def test_configure_memory_cache(self):
        """Test configuring memory cache."""
        cache = configure_cache(
            backend='memory',
            default_ttl=7200,
            enabled=True
        )
        
        assert isinstance(cache.backend, MemoryCache)
        assert cache.default_ttl == 7200
        assert cache.enabled
        
    def test_configure_disk_cache(self):
        """Test configuring disk cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = configure_cache(
                backend='disk',
                cache_dir=tmpdir,
                default_ttl=3600
            )
            
            assert isinstance(cache.backend, DiskCache)
            assert cache.backend.cache_dir == Path(tmpdir)
            
    def test_configure_invalid_backend(self):
        """Test configuring with invalid backend."""
        with pytest.raises(ValueError) as exc_info:
            configure_cache(backend='invalid')
            
        assert "Unknown cache backend" in str(exc_info.value)
        
    def test_global_cache(self):
        """Test global cache instance."""
        # Get default cache
        cache1 = get_cache()
        assert isinstance(cache1, RBACache)
        
        # Should return same instance
        cache2 = get_cache()
        assert cache1 is cache2
        
        # Set new cache
        new_cache = RBACache(default_ttl=9999)
        set_cache(new_cache)
        
        # Get should return new cache
        cache3 = get_cache()
        assert cache3 is new_cache
        assert cache3.default_ttl == 9999


class TestCacheIntegration:
    """Test cache integration with data operations."""
    
    def test_dataframe_copy_behavior(self):
        """Test that cached DataFrames are copied to prevent modification."""
        cache = RBACache()
        
        # Original DataFrame
        df = pd.DataFrame({'value': [1, 2, 3]})
        
        # Cache it
        cache.set_dataframe(df, table_no='TEST')
        
        # Get cached copy
        cached_df = cache.get_dataframe(table_no='TEST')
        
        # Modify cached copy
        cached_df['value'] = [4, 5, 6]
        
        # Original should be unchanged
        assert df['value'].tolist() == [1, 2, 3]
        
        # Re-fetch from cache should be original values
        cached_df2 = cache.get_dataframe(table_no='TEST')
        assert cached_df2['value'].tolist() == [1, 2, 3]