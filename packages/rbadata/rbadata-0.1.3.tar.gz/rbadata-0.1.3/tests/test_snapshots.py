"""
Tests for the snapshots module
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock, mock_open
import requests
from rbadata.snapshots import Snapshots, get_snapshots, get_economic_indicators
from rbadata.exceptions import RBADataError


class TestSnapshots:
    """Test the Snapshots class."""
    
    def test_init(self):
        """Test Snapshots initialization."""
        snapshots = Snapshots()
        
        assert snapshots._cached_data == {}
        assert hasattr(snapshots, 'SNAPSHOT_TYPES')
        assert hasattr(snapshots, 'BASE_URL')
    
    def test_get_snapshot_types(self):
        """Test getting snapshot types."""
        snapshots = Snapshots()
        types = snapshots.get_snapshot_types()
        
        assert isinstance(types, dict)
        assert len(types) == 3
        assert 'economic-indicators' in types
        assert 'economy-composition' in types
        assert 'payments' in types
        
        # Check structure
        for key, info in types.items():
            assert 'name' in info
            assert 'url' in info
            assert 'description' in info
    
    def test_snapshot_types_content(self):
        """Test snapshot types have correct content."""
        snapshots = Snapshots()
        types = snapshots.get_snapshot_types()
        
        # Check economic indicators
        eco_ind = types['economic-indicators']
        assert eco_ind['name'] == 'Key Economic Indicators'
        assert '/economy-snapshot' in eco_ind['url']
        
        # Check economy composition
        eco_comp = types['economy-composition']
        assert eco_comp['name'] == 'Composition of the Australian Economy'
        assert '/economy-composition' in eco_comp['url']
        
        # Check payments
        payments = types['payments']
        assert payments['name'] == 'How Australians Pay'
        assert '/payments-snapshot' in payments['url']
    
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_snapshot_success(self, mock_file, mock_get):
        """Test successful snapshot download."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'PDF content'
        mock_get.return_value = mock_response
        
        snapshots = Snapshots()
        result_path = snapshots.download_snapshot('economic-indicators')
        
        # Verify
        assert isinstance(result_path, Path)
        assert 'economic-indicators' in str(result_path)
        mock_get.assert_called_once()
        assert 'economy-snapshot.pdf' in mock_get.call_args[0][0]
        mock_file().write.assert_called_once_with(b'PDF content')
    
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_snapshot_custom_path(self, mock_file, mock_get):
        """Test downloading snapshot to custom path."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'PDF content'
        mock_get.return_value = mock_response
        
        snapshots = Snapshots()
        custom_path = '/custom/path/snapshot.pdf'
        result_path = snapshots.download_snapshot('payments', output_path=custom_path)
        
        assert str(result_path) == custom_path
        mock_file.assert_called_once_with(Path(custom_path), 'wb')
    
    def test_download_snapshot_invalid_type(self):
        """Test downloading with invalid snapshot type."""
        snapshots = Snapshots()
        
        with pytest.raises(RBADataError, match="Invalid snapshot type"):
            snapshots.download_snapshot('invalid-type')
    
    @patch('requests.get')
    def test_download_snapshot_network_error(self, mock_get):
        """Test handling of network errors during download."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        snapshots = Snapshots()
        
        with pytest.raises(RBADataError, match="Failed to download snapshot"):
            snapshots.download_snapshot('economic-indicators')
    
    @patch('requests.get')
    def test_download_snapshot_http_error(self, mock_get):
        """Test handling of HTTP errors during download."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        snapshots = Snapshots()
        
        with pytest.raises(RBADataError, match="Failed to download snapshot"):
            snapshots.download_snapshot('economic-indicators')
    
    @patch('rbadata.snapshots.Snapshots._scrape_economic_indicators')
    def test_get_economic_indicators(self, mock_scrape):
        """Test getting economic indicators data."""
        # Mock scraped data
        mock_data = pd.DataFrame({
            'indicator': ['GDP Growth', 'Unemployment Rate'],
            'value': [2.5, 4.0],
            'unit': ['% y/y', '%']
        })
        mock_scrape.return_value = mock_data
        
        snapshots = Snapshots()
        result = snapshots.get_economic_indicators()
        
        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result['indicator']) == ['GDP Growth', 'Unemployment Rate']
        mock_scrape.assert_called_once()
        
        # Test caching
        result2 = snapshots.get_economic_indicators()
        assert result2 is result  # Same object from cache
        assert mock_scrape.call_count == 1  # Not called again
    
    @patch('rbadata.snapshots.Snapshots._scrape_economic_indicators')
    def test_get_economic_indicators_refresh(self, mock_scrape):
        """Test refreshing economic indicators data."""
        # Mock different data for each call
        mock_scrape.side_effect = [
            pd.DataFrame({'indicator': ['GDP'], 'value': [2.5]}),
            pd.DataFrame({'indicator': ['GDP'], 'value': [2.6]})
        ]
        
        snapshots = Snapshots()
        result1 = snapshots.get_economic_indicators()
        result2 = snapshots.get_economic_indicators(refresh=True)
        
        assert mock_scrape.call_count == 2
        assert result1['value'].iloc[0] == 2.5
        assert result2['value'].iloc[0] == 2.6
    
    @patch('rbadata.snapshots.Snapshots._scrape_economy_composition')
    def test_get_economy_composition(self, mock_scrape):
        """Test getting economy composition data."""
        # Mock scraped data
        mock_data = pd.DataFrame({
            'sector': ['Services', 'Mining'],
            'share': [70.5, 8.5],
            'unit': ['% of GDP', '% of GDP']
        })
        mock_scrape.return_value = mock_data
        
        snapshots = Snapshots()
        result = snapshots.get_economy_composition()
        
        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result['sector']) == ['Services', 'Mining']
        assert result['share'].sum() == 79.0
        
        # Test caching
        result2 = snapshots.get_economy_composition()
        assert mock_scrape.call_count == 1
    
    @patch('rbadata.snapshots.Snapshots._scrape_payment_methods')
    def test_get_payment_methods(self, mock_scrape):
        """Test getting payment methods data."""
        # Mock scraped data
        mock_data = pd.DataFrame({
            'method': ['Card', 'Cash'],
            'share': [75, 13],
            'transactions': [85, 7]
        })
        mock_scrape.return_value = mock_data
        
        snapshots = Snapshots()
        result = snapshots.get_payment_methods()
        
        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result['method']) == ['Card', 'Cash']
        assert 'share' in result.columns
        assert 'transactions' in result.columns
    
    def test_get_comparison_tool_data(self):
        """Test that comparison tool raises NotImplementedError."""
        snapshots = Snapshots()
        
        with pytest.raises(NotImplementedError, match="JavaScript execution"):
            snapshots.get_comparison_tool_data(
                'economic-indicators',
                ['GDP', 'CPI']
            )
    
    def test_scrape_economic_indicators(self):
        """Test the economic indicators scraper returns valid data."""
        snapshots = Snapshots()
        result = snapshots._scrape_economic_indicators()
        
        # Verify structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'indicator' in result.columns
        assert 'value' in result.columns
        assert 'unit' in result.columns
        assert 'date' in result.columns
        
        # Check some indicators exist
        indicators = result['indicator'].tolist()
        assert 'GDP Growth' in indicators
        assert 'Unemployment Rate' in indicators
        assert 'CPI Inflation' in indicators
        assert 'Cash Rate' in indicators
    
    def test_scrape_economy_composition(self):
        """Test the economy composition scraper returns valid data."""
        snapshots = Snapshots()
        result = snapshots._scrape_economy_composition()
        
        # Verify structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'sector' in result.columns
        assert 'share' in result.columns
        assert 'unit' in result.columns
        
        # Check sectors
        sectors = result['sector'].tolist()
        assert 'Services' in sectors
        assert 'Mining' in sectors
        assert 'Manufacturing' in sectors
        
        # Shares should sum to 100
        total_share = result['share'].sum()
        assert abs(total_share - 100) < 1  # Allow small rounding error
    
    def test_scrape_payment_methods(self):
        """Test the payment methods scraper returns valid data."""
        snapshots = Snapshots()
        result = snapshots._scrape_payment_methods()
        
        # Verify structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'method' in result.columns
        assert 'share' in result.columns
        assert 'transactions' in result.columns
        
        # Check payment methods
        methods = result['method'].tolist()
        assert 'Card' in methods
        assert 'Cash' in methods
        
        # Shares should sum to 100
        total_share = result['share'].sum()
        assert abs(total_share - 100) < 1  # Allow small rounding error


class TestSnapshotsFunctions:
    """Test module-level convenience functions."""
    
    def test_get_snapshots(self):
        """Test get_snapshots function."""
        result = get_snapshots()
        
        assert isinstance(result, Snapshots)
        assert hasattr(result, 'get_economic_indicators')
        assert hasattr(result, 'download_snapshot')
    
    @patch('rbadata.snapshots.Snapshots.get_economic_indicators')
    def test_get_economic_indicators_function(self, mock_get):
        """Test get_economic_indicators convenience function."""
        # Mock return data
        mock_data = pd.DataFrame({
            'indicator': ['Test'],
            'value': [1.0]
        })
        mock_get.return_value = mock_data
        
        result = get_economic_indicators()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        mock_get.assert_called_once()


class TestSnapshotsIntegration:
    """Integration tests for snapshots functionality."""
    
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_all_snapshot_types(self, mock_file, mock_get):
        """Test downloading all snapshot types."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'PDF content'
        mock_get.return_value = mock_response
        
        snapshots = Snapshots()
        
        # Download each type
        for snapshot_type in snapshots.SNAPSHOT_TYPES.keys():
            result = snapshots.download_snapshot(snapshot_type)
            assert isinstance(result, Path)
            assert snapshot_type in str(result)
        
        # Should have made 3 download calls
        assert mock_get.call_count == 3
    
    def test_cached_data_isolation(self):
        """Test that cached data is properly isolated between types."""
        snapshots = Snapshots()
        
        # Mock the scraping methods
        with patch.object(snapshots, '_scrape_economic_indicators') as mock_eco:
            with patch.object(snapshots, '_scrape_economy_composition') as mock_comp:
                with patch.object(snapshots, '_scrape_payment_methods') as mock_pay:
                    # Set different return values
                    mock_eco.return_value = pd.DataFrame({'data': ['eco']})
                    mock_comp.return_value = pd.DataFrame({'data': ['comp']})
                    mock_pay.return_value = pd.DataFrame({'data': ['pay']})
                    
                    # Get each type
                    eco_data = snapshots.get_economic_indicators()
                    comp_data = snapshots.get_economy_composition()
                    pay_data = snapshots.get_payment_methods()
                    
                    # Verify they're different
                    assert eco_data['data'].iloc[0] == 'eco'
                    assert comp_data['data'].iloc[0] == 'comp'
                    assert pay_data['data'].iloc[0] == 'pay'
                    
                    # Verify caching
                    assert len(snapshots._cached_data) == 3