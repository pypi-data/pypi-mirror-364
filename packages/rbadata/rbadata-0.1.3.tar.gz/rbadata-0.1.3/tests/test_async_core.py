"""
Tests for async functionality.
"""

import asyncio
from unittest.mock import Mock, patch, AsyncMock

import pandas as pd
import pytest

try:
    import aiohttp
    from rbadata.async_core import (
        AsyncRBAClient,
        read_rba_async,
        fetch_multiple_series_async,
    )
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    AsyncRBAClient = None
    read_rba_async = None
    fetch_multiple_series_async = None

from rbadata.exceptions import DownloadError, RBADataError


@pytest.mark.skipif(not ASYNC_AVAILABLE, reason="aiohttp not available")
class TestAsyncRBAClient:
    """Test AsyncRBAClient class."""
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with AsyncRBAClient() as client:
            assert client.session is not None
            assert isinstance(client.session, aiohttp.ClientSession)
            
        # Session should be closed after exit
        assert client.session.closed
        
    @pytest.mark.asyncio
    async def test_download_csv_success(self):
        """Test successful CSV download."""
        client = AsyncRBAClient()
        
        # Mock response as an async context manager
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read = AsyncMock(return_value=b"CSV,data\n1,2")
        mock_response.raise_for_status = Mock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        # Mock session
        mock_session = AsyncMock()
        mock_session.get = Mock(return_value=mock_response)
        
        client.session = mock_session
        
        # Execute
        result = await client._download_csv('F1')
        
        # Assert
        assert result == "CSV,data\n1,2"
        assert mock_session.get.called
        
    @pytest.mark.asyncio
    async def test_download_csv_with_retry(self):
        """Test CSV download with retry on failure."""
        client = AsyncRBAClient(max_retries=3, use_cache=False)
        
        # Mock responses - fail twice, then succeed
        error_response = AsyncMock()
        error_response.status = 500
        error_response.raise_for_status = Mock(
            side_effect=aiohttp.ClientResponseError(
                request_info=Mock(),
                history=(),
                status=500
            )
        )
        
        success_response = AsyncMock()
        success_response.status = 200
        success_response.read = AsyncMock(return_value=b"CSV,data")
        success_response.raise_for_status = Mock()
        
        # Create proper async context managers for responses
        error_response.__aenter__ = AsyncMock(return_value=error_response)
        error_response.__aexit__ = AsyncMock(return_value=None)
        
        success_response.__aenter__ = AsyncMock(return_value=success_response)
        success_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = AsyncMock()
        mock_session.get = Mock(
            side_effect=[error_response, error_response, success_response]
        )
        
        client.session = mock_session
        
        # Execute with minimal sleep
        with patch('asyncio.sleep', new_callable=AsyncMock):
            result = await client._download_csv('F1')
            
        # Should succeed after retries  
        assert result == "CSV,data"
        assert mock_session.get.call_count == 3
        
    @pytest.mark.asyncio
    async def test_download_csv_max_retries_exceeded(self):
        """Test CSV download fails after max retries."""
        client = AsyncRBAClient(max_retries=2, use_cache=False)
        
        # Mock failing response
        error_response = AsyncMock()
        error_response.status = 500
        error_response.raise_for_status = Mock(
            side_effect=aiohttp.ClientResponseError(
                request_info=Mock(),
                history=(),
                status=500
            )
        )
        error_response.__aenter__ = AsyncMock(return_value=error_response)
        error_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = AsyncMock()
        mock_session.get = Mock(return_value=error_response)
        
        client.session = mock_session
        
        # Execute
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with pytest.raises(DownloadError) as exc_info:
                await client._download_csv('F1')
                
        assert "Failed to download table F1" in str(exc_info.value)
        assert mock_session.get.call_count == 2
        
    @patch('rbadata.async_core.get_cache')
    @pytest.mark.asyncio
    async def test_download_csv_from_cache(self, mock_cache):
        """Test CSV download uses cache."""
        client = AsyncRBAClient(use_cache=True)
        
        # Mock cache hit
        mock_cache.return_value.get_csv.return_value = "cached,content"
        
        # Execute
        result = await client._download_csv('F1')
        
        # Should return cached content without network call
        assert result == "cached,content"
        assert mock_cache.return_value.get_csv.called
        
    @patch('rbadata.async_core.parse_rba_csv')
    @patch('rbadata.async_core.tables_from_seriesid')
    @pytest.mark.asyncio
    async def test_read_rba_async_with_series(self, mock_tables, mock_parse):
        """Test async read with series IDs."""
        # Setup
        mock_tables.return_value = {'F1': {'TEST1', 'TEST2'}}
        mock_parse.return_value = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=2),
            'series_id': ['TEST1', 'TEST1'],
            'value': [1.0, 2.0]
        })
        
        async with AsyncRBAClient() as client:
            # Mock CSV download
            client._download_csv = AsyncMock(return_value="CSV,content")
            
            # Execute
            result = await client.read_rba_async(series_id=['TEST1', 'TEST2'])
            
        # Assert
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert client._download_csv.called
        
    @pytest.mark.asyncio
    async def test_read_rba_async_validation(self):
        """Test input validation for async read."""
        async with AsyncRBAClient() as client:
            # No table_no or series_id
            with pytest.raises(RBADataError) as exc_info:
                await client.read_rba_async()
                
            assert "Either 'table_no' or 'series_id' must be specified" in str(exc_info.value)
            
            # Both table_no and series_id
            with pytest.raises(RBADataError) as exc_info:
                await client.read_rba_async(table_no='F1', series_id='TEST1')
                
            assert "Only one of" in str(exc_info.value)
            
    @patch('rbadata.async_core.parse_rba_csv')
    @pytest.mark.asyncio
    async def test_concurrent_table_downloads(self, mock_parse):
        """Test concurrent downloading of multiple tables."""
        # Setup
        mock_parse.return_value = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'series_id': ['TEST'],
            'value': [1.0]
        })
        
        async with AsyncRBAClient(max_concurrent=2) as client:
            # Track download calls
            download_calls = []
            
            async def mock_download(table):
                download_calls.append(table)
                await asyncio.sleep(0.1)  # Simulate network delay
                return f"CSV for {table}"
                
            client._download_csv = mock_download
            
            # Execute
            tables = ['F1', 'F2', 'G1', 'D3']
            result = await client.read_rba_async(table_no=tables)
            
        # All tables should be downloaded
        assert set(download_calls) == set(tables)
        assert len(result) == 4  # 4 tables × 1 row each
        
    @patch('rbadata.async_core.parse_rba_csv')
    @patch('rbadata.async_core.tables_from_seriesid')
    @pytest.mark.asyncio
    async def test_fetch_multiple_series_async(self, mock_tables, mock_parse):
        """Test fetching multiple series returns dict."""
        # Setup
        mock_tables.return_value = {
            'F1': {'SERIES1', 'SERIES2'},
            'G1': {'SERIES3'}
        }
        
        # Mock different data for each series
        def parse_side_effect(content, table, **kwargs):
            series_filter = kwargs.get('series_filter', [])
            data = []
            for series in series_filter:
                data.append({
                    'date': pd.Timestamp('2023-01-01'),
                    'series_id': series,
                    'value': float(series[-1]),  # Use last char as value
                    'units': 'Test',
                    'description': f'Description for {series}'
                })
            return pd.DataFrame(data)
            
        mock_parse.side_effect = parse_side_effect
        
        async with AsyncRBAClient() as client:
            client._download_csv = AsyncMock(return_value="CSV,content")
            
            # Execute
            result = await client.fetch_multiple_series_async(
                ['SERIES1', 'SERIES2', 'SERIES3']
            )
            
        # Assert
        assert isinstance(result, dict)
        assert set(result.keys()) == {'SERIES1', 'SERIES2', 'SERIES3'}
        
        # Check each series
        for series_id, df in result.items():
            assert isinstance(df, pd.DataFrame)
            assert 'value' in df.columns
            assert 'units' in df.columns
            assert 'description' in df.columns


@pytest.mark.skipif(not ASYNC_AVAILABLE, reason="aiohttp not available")
class TestAsyncConvenienceFunctions:
    """Test async convenience functions."""
    
    @patch('rbadata.async_core.AsyncRBAClient.read_rba_async')
    @pytest.mark.asyncio
    async def test_read_rba_async_function(self, mock_read):
        """Test read_rba_async convenience function."""
        # Setup
        expected_df = pd.DataFrame({'value': [1, 2, 3]})
        mock_read.return_value = expected_df
        
        # Execute
        result = await read_rba_async(
            table_no='F1',
            start_date='2023-01-01',
            max_concurrent=10
        )
        
        # Assert
        assert result is expected_df
        mock_read.assert_called_once_with(
            table_no='F1',
            series_id=None,
            start_date='2023-01-01',
            end_date=None
        )
        
    @patch('rbadata.async_core.AsyncRBAClient.fetch_multiple_series_async')
    @pytest.mark.asyncio
    async def test_fetch_multiple_series_async_function(self, mock_fetch):
        """Test fetch_multiple_series_async convenience function."""
        # Setup
        expected_result = {
            'TEST1': pd.DataFrame({'value': [1]}),
            'TEST2': pd.DataFrame({'value': [2]})
        }
        mock_fetch.return_value = expected_result
        
        # Execute
        result = await fetch_multiple_series_async(
            ['TEST1', 'TEST2'],
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        
        # Assert
        assert result == expected_result
        mock_fetch.assert_called_once_with(
            series_ids=['TEST1', 'TEST2'],
            start_date='2023-01-01',
            end_date='2023-12-31'
        )


@pytest.mark.skipif(not ASYNC_AVAILABLE, reason="aiohttp not available")
class TestAsyncErrorHandling:
    """Test error handling in async operations."""
    
    @patch('rbadata.async_core.parse_rba_csv')
    @pytest.mark.asyncio
    async def test_partial_table_failures(self, mock_parse):
        """Test handling when some tables fail but others succeed."""
        # Setup
        mock_parse.return_value = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'series_id': ['TEST'],
            'value': [1.0]
        })
        
        async with AsyncRBAClient() as client:
            # Mock downloads - F1 succeeds, F2 fails
            async def mock_download(table):
                if table == 'F2':
                    raise DownloadError(f"Failed to download {table}")
                return f"CSV for {table}"
                
            client._download_csv = mock_download
            
            # Execute
            result = await client.read_rba_async(table_no=['F1', 'F2'])
            
        # Should still return data from F1
        assert len(result) == 1
        assert result['series_id'].iloc[0] == 'TEST'
        
    @pytest.mark.asyncio
    async def test_all_tables_fail(self):
        """Test error when all table downloads fail."""
        async with AsyncRBAClient() as client:
            # Mock all downloads to fail
            client._download_csv = AsyncMock(
                side_effect=DownloadError("Network error")
            )
            
            # Execute
            with pytest.raises(RBADataError) as exc_info:
                await client.read_rba_async(table_no='F1')
                
            assert "Failed to fetch any data" in str(exc_info.value)