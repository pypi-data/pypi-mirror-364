"""
Tests for the chart_pack module
"""

import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, Mock, MagicMock, mock_open
import requests
from bs4 import BeautifulSoup
from rbadata.chart_pack import ChartPack, get_chart_pack
from rbadata.exceptions import RBADataError


class TestChartPack:
    """Test the ChartPack class."""
    
    def test_init(self):
        """Test ChartPack initialization."""
        cp = ChartPack()
        
        assert cp._categories is None
        assert cp._charts is None
        assert cp._last_update is None
        assert hasattr(cp, 'BASE_URL')
    
    @patch('rbadata.chart_pack.ChartPack._scrape_chart_pack_page')
    def test_get_categories(self, mock_scrape):
        """Test getting chart categories."""
        cp = ChartPack()
        cp._categories = ['Inflation', 'Growth', 'Labour Market']
        
        # First call - use cached
        categories = cp.get_categories()
        
        assert categories == ['Inflation', 'Growth', 'Labour Market']
        mock_scrape.assert_not_called()
        
        # Call with refresh
        cp.get_categories(refresh=True)
        mock_scrape.assert_called_once()
    
    @patch('rbadata.chart_pack.ChartPack._scrape_chart_pack_page')
    def test_get_categories_initial_load(self, mock_scrape):
        """Test getting categories when not cached."""
        cp = ChartPack()
        mock_categories = ['World Economy', 'Australian Growth']
        
        # Mock the scraping to set categories
        def set_categories():
            cp._categories = mock_categories
        
        mock_scrape.side_effect = set_categories
        
        categories = cp.get_categories()
        
        assert categories == mock_categories
        mock_scrape.assert_called_once()
    
    @patch('rbadata.chart_pack.ChartPack._scrape_chart_pack_page')
    def test_get_charts_by_category(self, mock_scrape):
        """Test getting charts by category."""
        cp = ChartPack()
        cp._categories = ['Inflation', 'Growth']
        cp._charts = [
            {'title': 'CPI', 'category': 'Inflation', 'id': 'cpi'},
            {'title': 'GDP', 'category': 'Growth', 'id': 'gdp'},
            {'title': 'Underlying', 'category': 'Inflation', 'id': 'underlying'}
        ]
        
        # Get inflation charts
        inflation_charts = cp.get_charts_by_category('Inflation')
        
        assert len(inflation_charts) == 2
        assert all(c['category'] == 'Inflation' for c in inflation_charts)
        mock_scrape.assert_not_called()
    
    @patch('rbadata.chart_pack.ChartPack._scrape_chart_pack_page')
    def test_get_charts_by_category_case_insensitive(self, mock_scrape):
        """Test category matching is case-insensitive."""
        cp = ChartPack()
        cp._categories = ['Labour Market']
        cp._charts = [
            {'title': 'Unemployment', 'category': 'Labour Market', 'id': 'unemp'}
        ]
        
        # Try different cases
        charts1 = cp.get_charts_by_category('Labour Market')
        charts2 = cp.get_charts_by_category('labour market')
        charts3 = cp.get_charts_by_category('LABOUR MARKET')
        
        assert len(charts1) == len(charts2) == len(charts3) == 1
    
    @patch('rbadata.chart_pack.ChartPack._scrape_chart_pack_page')
    def test_get_charts_by_category_invalid(self, mock_scrape):
        """Test error for invalid category."""
        cp = ChartPack()
        cp._categories = ['Inflation', 'Growth']
        cp._charts = []
        
        with pytest.raises(RBADataError, match="Category 'Invalid' not found"):
            cp.get_charts_by_category('Invalid')
    
    @patch('rbadata.chart_pack.ChartPack._scrape_chart_pack_page')
    def test_get_all_charts(self, mock_scrape):
        """Test getting all charts."""
        cp = ChartPack()
        mock_charts = [
            {'title': 'Chart 1', 'category': 'Cat1'},
            {'title': 'Chart 2', 'category': 'Cat2'}
        ]
        cp._charts = mock_charts
        
        charts = cp.get_all_charts()
        
        assert charts == mock_charts
        mock_scrape.assert_not_called()
        
        # Test refresh
        cp.get_all_charts(refresh=True)
        mock_scrape.assert_called_once()
    
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('rbadata.chart_pack.ChartPack._get_chart_pack_pdf_url')
    def test_download_chart_pack_latest(self, mock_get_url, mock_file, mock_get):
        """Test downloading latest chart pack."""
        # Setup mocks
        mock_get_url.return_value = 'https://example.com/chart-pack.pdf'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'PDF content'
        mock_get.return_value = mock_response
        
        cp = ChartPack()
        result = cp.download_chart_pack()
        
        # Verify
        assert isinstance(result, Path)
        assert 'chart_pack_latest.pdf' in str(result)
        mock_get.assert_called_once_with(
            'https://example.com/chart-pack.pdf',
            headers=mock_get.call_args[1]['headers'],
            timeout=30
        )
        mock_file().write.assert_called_once_with(b'PDF content')
    
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_chart_pack_specific_date(self, mock_file, mock_get):
        """Test downloading chart pack for specific date."""
        # Setup mocks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'PDF content'
        mock_get.return_value = mock_response
        
        cp = ChartPack()
        
        # Test with string date
        result = cp.download_chart_pack(date='2024-07')
        
        assert 'chart_pack_2024-07.pdf' in str(result)
        
        # Test with datetime
        result2 = cp.download_chart_pack(date=datetime(2024, 8, 1))
        
        assert 'chart_pack_' in str(result2)
        assert '2024' in str(result2)
    
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_chart_pack_custom_path(self, mock_file, mock_get):
        """Test downloading to custom path."""
        # Setup mocks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'PDF content'
        mock_get.return_value = mock_response
        
        cp = ChartPack()
        custom_path = '/custom/path/chart.pdf'
        result = cp.download_chart_pack(output_path=custom_path)
        
        assert str(result) == custom_path
        mock_file.assert_called_once_with(Path(custom_path), 'wb')
    
    @patch('requests.get')
    def test_download_chart_pack_error(self, mock_get):
        """Test handling download errors."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        cp = ChartPack()
        
        with pytest.raises(requests.RequestException):
            cp.download_chart_pack()
    
    def test_get_chart_data_not_implemented(self):
        """Test that get_chart_data raises NotImplementedError."""
        cp = ChartPack()
        
        with pytest.raises(NotImplementedError, match="not yet implemented"):
            cp.get_chart_data('chart123')
    
    @patch('rbadata.chart_pack.ChartPack._scrape_chart_pack_page')
    def test_get_latest_release_date(self, mock_scrape):
        """Test getting latest release date."""
        cp = ChartPack()
        test_date = datetime(2024, 7, 15)
        cp._last_update = test_date
        
        # Should use cached date
        result = cp.get_latest_release_date()
        
        assert result == test_date
        mock_scrape.assert_not_called()
        
        # Test when not cached
        cp2 = ChartPack()
        cp2.get_latest_release_date()
        mock_scrape.assert_called_once()
    
    @patch('requests.get')
    def test_scrape_chart_pack_page_success(self, mock_get):
        """Test successful page scraping."""
        # Mock HTML response
        html_content = """
        <html>
        <body>
            <nav>
                <a href="#inflation">Inflation</a>
                <a href="#growth">Australian Growth</a>
                <a href="#overview">Overview</a>
            </nav>
            <section id="cpi-chart" class="chart">
                <h3>Consumer Price Inflation</h3>
            </section>
            <section id="gdp-chart" class="chart">
                <h3>GDP Growth</h3>
            </section>
            <p>15 July 2024</p>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode()
        mock_get.return_value = mock_response
        
        cp = ChartPack()
        cp._scrape_chart_pack_page()
        
        # Check categories (Overview should be filtered out)
        assert 'Inflation' in cp._categories
        assert 'Australian Growth' in cp._categories
        assert 'Overview' not in cp._categories
        
        # Check charts
        assert len(cp._charts) >= 2
        chart_titles = [c['title'] for c in cp._charts]
        assert 'Consumer Price Inflation' in chart_titles
        assert 'GDP Growth' in chart_titles
        
        # Check date extraction
        assert cp._last_update is not None
        assert cp._last_update.year == 2024
        assert cp._last_update.month == 7
    
    @patch('requests.get')
    def test_scrape_chart_pack_page_network_error(self, mock_get):
        """Test handling of network errors during scraping."""
        mock_get.side_effect = requests.RequestException("Connection failed")
        
        cp = ChartPack()
        
        with pytest.raises(RBADataError, match="Failed to access Chart Pack page"):
            cp._scrape_chart_pack_page()
    
    @patch('requests.get')
    def test_scrape_chart_pack_page_defaults(self, mock_get):
        """Test scraping falls back to defaults when no data found."""
        # Mock minimal HTML
        html_content = "<html><body><p>Empty page</p></body></html>"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode()
        mock_get.return_value = mock_response
        
        cp = ChartPack()
        cp._scrape_chart_pack_page()
        
        # Should have default categories and charts
        assert len(cp._categories) > 0
        assert 'World Economy' in cp._categories
        assert 'Inflation' in cp._categories
        
        assert len(cp._charts) > 0
        assert any(c['title'] == 'Consumer Price Inflation' for c in cp._charts)
    
    def test_get_chart_pack_pdf_url_latest(self):
        """Test getting PDF URL for latest chart pack."""
        cp = ChartPack()
        url = cp._get_chart_pack_pdf_url()
        
        assert url == f"{cp.BASE_URL}/pdf/chart-pack.pdf"
    
    def test_get_chart_pack_pdf_url_specific_date(self):
        """Test getting PDF URL for specific date."""
        cp = ChartPack()
        
        # Test with string date
        url1 = cp._get_chart_pack_pdf_url('2024-07')
        assert 'chart-pack-202407.pdf' in url1
        
        # Test with datetime
        url2 = cp._get_chart_pack_pdf_url(datetime(2024, 8, 1))
        assert 'chart-pack-202408.pdf' in url2
    
    def test_guess_category(self):
        """Test category guessing from title."""
        cp = ChartPack()
        
        # Test various titles
        assert cp._guess_category("Consumer Price Inflation") == "Inflation"
        assert cp._guess_category("CPI Annual Rate") == "Inflation"
        assert cp._guess_category("GDP Growth Rate") == "Australian Growth"
        assert cp._guess_category("Unemployment Rate") == "Labour Market"
        assert cp._guess_category("Cash Rate Target") == "Interest Rates"
        # Note: "AUD/USD Exchange Rate" contains both "exchange" and "rate", but "exchange" is more specific
        assert cp._guess_category("AUD/USD Exchange Rate") == "Exchange Rates"
        # "Australian Dollar" also maps to Exchange Rates
        assert cp._guess_category("Australian Dollar") == "Exchange Rates"
        assert cp._guess_category("Credit Growth") == "Credit and Money"
        assert cp._guess_category("House Prices") == "Housing"
        assert cp._guess_category("China GDP") == "World Economy"
        # Note: "US Inflation" contains "inflation" so it maps to "Inflation" not "World Economy"  
        assert cp._guess_category("US Inflation") == "Inflation"
        # But "US Economic Activity" without other keywords maps to World Economy
        assert cp._guess_category("US Economic Activity") == "World Economy"
        assert cp._guess_category("Unknown Chart") == "Other"
    
    def test_get_default_categories(self):
        """Test default categories list."""
        cp = ChartPack()
        categories = cp._get_default_categories()
        
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert 'World Economy' in categories
        assert 'Inflation' in categories
        assert 'Labour Market' in categories
        assert 'Interest Rates' in categories
    
    def test_get_default_charts(self):
        """Test default charts list."""
        cp = ChartPack()
        charts = cp._get_default_charts()
        
        assert isinstance(charts, list)
        assert len(charts) > 0
        
        # Check structure
        for chart in charts:
            assert 'title' in chart
            assert 'category' in chart
            assert 'id' in chart
            assert 'url' in chart
        
        # Check some specific charts
        titles = [c['title'] for c in charts]
        assert 'Consumer Price Inflation' in titles
        assert 'Cash Rate' in titles
        assert 'Australian Dollar' in titles


class TestChartPackFunctions:
    """Test module-level convenience functions."""
    
    def test_get_chart_pack(self):
        """Test get_chart_pack function."""
        result = get_chart_pack()
        
        assert isinstance(result, ChartPack)
        assert hasattr(result, 'get_categories')
        assert hasattr(result, 'download_chart_pack')


class TestChartPackIntegration:
    """Integration tests for chart pack functionality."""
    
    @patch('requests.get')
    def test_full_workflow(self, mock_get):
        """Test a complete workflow of using ChartPack."""
        # Mock successful response for scraping
        html_content = """
        <html>
        <body>
            <nav>
                <a href="#inflation">Inflation</a>
                <a href="#growth">Growth</a>
            </nav>
            <section class="chart">
                <h3>CPI Chart</h3>
            </section>
        </body>
        </html>
        """
        
        scrape_response = Mock()
        scrape_response.status_code = 200
        scrape_response.content = html_content.encode()
        
        # Mock PDF download response
        pdf_response = Mock()
        pdf_response.status_code = 200
        pdf_response.content = b'PDF content'
        
        mock_get.side_effect = [scrape_response, pdf_response]
        
        # Create instance and get categories
        cp = ChartPack()
        categories = cp.get_categories()
        
        assert 'Inflation' in categories
        assert 'Growth' in categories
        
        # Get charts
        all_charts = cp.get_all_charts()
        assert len(all_charts) > 0
        
        # Download PDF
        with patch('builtins.open', mock_open()):
            pdf_path = cp.download_chart_pack()
            assert isinstance(pdf_path, Path)