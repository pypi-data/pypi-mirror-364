"""
Tests for the alerts module
"""

import pytest
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, Mock, MagicMock, mock_open
from rbadata.alerts import RBAAlerts, create_alert
from rbadata.exceptions import RBADataError


class TestRBAAlerts:
    """Test the RBAAlerts class."""
    
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.home')
    @patch('rbadata.alerts.RBAAlerts._load_alerts')
    def test_init_default_config(self, mock_load, mock_home, mock_mkdir):
        """Test initialization with default config path."""
        mock_home.return_value = Path('/mock/home')
        mock_load.return_value = {}
        
        alerts = RBAAlerts()
        
        assert '/mock/home/.rbadata/alerts.json' in str(alerts.config_file)
        assert alerts.alerts == {}
        assert alerts._callbacks == {}
        assert alerts._last_check == {}
    
    @patch('rbadata.alerts.RBAAlerts._load_alerts')
    def test_init_custom_config(self, mock_load):
        """Test initialization with custom config file."""
        mock_load.return_value = {'alert1': {'id': 'alert1'}}
        
        alerts = RBAAlerts(config_file='/custom/path/alerts.json')
        
        assert alerts.config_file == '/custom/path/alerts.json'
        assert 'alert1' in alerts.alerts
    
    @patch('rbadata.alerts.RBAAlerts._save_alerts')
    @patch('rbadata.alerts.RBAAlerts._generate_alert_id')
    def test_add_alert_table(self, mock_gen_id, mock_save):
        """Test adding an alert for a table."""
        mock_gen_id.return_value = 'test123'
        
        alerts = RBAAlerts()
        alert_id = alerts.add_alert(
            table_no='G1',
            name='CPI Alert'
        )
        
        assert alert_id == 'test123'
        assert 'test123' in alerts.alerts
        assert alerts.alerts['test123']['table_no'] == 'G1'
        assert alerts.alerts['test123']['name'] == 'CPI Alert'
        assert alerts.alerts['test123']['enabled'] is True
        mock_save.assert_called_once()
    
    @patch('rbadata.alerts.RBAAlerts._save_alerts')
    @patch('rbadata.alerts.RBAAlerts._generate_alert_id')
    def test_add_alert_series(self, mock_gen_id, mock_save):
        """Test adding an alert for a series."""
        mock_gen_id.return_value = 'test456'
        
        alerts = RBAAlerts()
        alert_id = alerts.add_alert(
            series_id='GCPIAG',
            name='Inflation Series'
        )
        
        assert alert_id == 'test456'
        assert alerts.alerts['test456']['series_id'] == 'GCPIAG'
        assert alerts.alerts['test456']['table_no'] is None
    
    @patch('rbadata.alerts.RBAAlerts._save_alerts')
    @patch('rbadata.alerts.RBAAlerts._generate_alert_id')
    def test_add_alert_release_type(self, mock_gen_id, mock_save):
        """Test adding an alert for a release type."""
        mock_gen_id.return_value = 'test789'
        
        alerts = RBAAlerts()
        alert_id = alerts.add_alert(
            release_type='chart-pack',
            name='Chart Pack Alert'
        )
        
        assert alert_id == 'test789'
        assert alerts.alerts['test789']['release_type'] == 'chart-pack'
    
    def test_add_alert_no_target(self):
        """Test error when no target specified."""
        alerts = RBAAlerts()
        
        with pytest.raises(RBADataError, match="Must specify at least one"):
            alerts.add_alert(name='Invalid Alert')
    
    @patch('rbadata.alerts.RBAAlerts._save_alerts')
    @patch('rbadata.alerts.RBAAlerts._generate_alert_id')
    def test_add_alert_with_callback(self, mock_gen_id, mock_save):
        """Test adding an alert with callback."""
        mock_gen_id.return_value = 'test_cb'
        mock_callback = Mock()
        
        alerts = RBAAlerts()
        alert_id = alerts.add_alert(
            table_no='G1',
            callback=mock_callback
        )
        
        assert alert_id == 'test_cb'
        assert 'test_cb' in alerts._callbacks
        assert alerts._callbacks['test_cb'] == mock_callback
    
    @patch('rbadata.alerts.RBAAlerts._save_alerts')
    def test_remove_alert_success(self, mock_save):
        """Test removing an existing alert."""
        alerts = RBAAlerts()
        alerts.alerts = {'test123': {'id': 'test123'}}
        alerts._callbacks = {'test123': Mock()}
        
        alerts.remove_alert('test123')
        
        assert 'test123' not in alerts.alerts
        assert 'test123' not in alerts._callbacks
        mock_save.assert_called_once()
    
    def test_remove_alert_not_found(self):
        """Test removing non-existent alert."""
        alerts = RBAAlerts()
        
        with pytest.raises(RBADataError, match="Alert 'nonexistent' not found"):
            alerts.remove_alert('nonexistent')
    
    def test_list_alerts_empty(self):
        """Test listing alerts when none exist."""
        alerts = RBAAlerts()
        alerts.alerts = {}
        
        result = alerts.list_alerts()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_list_alerts_with_data(self):
        """Test listing alerts with data."""
        alerts = RBAAlerts()
        alerts.alerts = {
            'alert1': {
                'id': 'alert1',
                'name': 'Test Alert 1',
                'table_no': 'G1',
                'enabled': True
            },
            'alert2': {
                'id': 'alert2',
                'name': 'Test Alert 2',
                'series_id': 'GCPIAG',
                'enabled': False
            }
        }
        
        result = alerts.list_alerts()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'name' in result.columns
        assert 'enabled' in result.columns
        assert set(result.index) == {'alert1', 'alert2'}
    
    @patch('rbadata.alerts.RBAAlerts._save_alerts')
    def test_enable_alert(self, mock_save):
        """Test enabling an alert."""
        alerts = RBAAlerts()
        alerts.alerts = {'test123': {'id': 'test123', 'enabled': False}}
        
        alerts.enable_alert('test123')
        
        assert alerts.alerts['test123']['enabled'] is True
        mock_save.assert_called_once()
    
    def test_enable_alert_not_found(self):
        """Test enabling non-existent alert."""
        alerts = RBAAlerts()
        
        with pytest.raises(RBADataError, match="Alert 'nonexistent' not found"):
            alerts.enable_alert('nonexistent')
    
    @patch('rbadata.alerts.RBAAlerts._save_alerts')
    def test_disable_alert(self, mock_save):
        """Test disabling an alert."""
        alerts = RBAAlerts()
        alerts.alerts = {'test123': {'id': 'test123', 'enabled': True}}
        
        alerts.disable_alert('test123')
        
        assert alerts.alerts['test123']['enabled'] is False
        mock_save.assert_called_once()
    
    @patch('rbadata.alerts.RBAAlerts._trigger_alert')
    @patch('rbadata.alerts.RBAAlerts._has_new_release')
    def test_check_for_updates(self, mock_has_new, mock_trigger):
        """Test checking for updates."""
        alerts = RBAAlerts()
        alerts.alerts = {
            'alert1': {
                'id': 'alert1',
                'name': 'Test Alert 1',
                'enabled': True,
                'release_type': 'table'
            },
            'alert2': {
                'id': 'alert2',
                'name': 'Test Alert 2',
                'enabled': False,
                'release_type': 'series'
            },
            'alert3': {
                'id': 'alert3',
                'name': 'Test Alert 3',
                'enabled': True,
                'release_type': 'chart-pack'
            }
        }
        
        # Only alert1 has new release
        mock_has_new.side_effect = [True, False]
        
        triggered = alerts.check_for_updates()
        
        # Only enabled alerts checked
        assert mock_has_new.call_count == 2
        assert mock_trigger.call_count == 1
        mock_trigger.assert_called_with('alert1')
        
        assert len(triggered) == 1
        assert triggered[0]['alert_id'] == 'alert1'
        assert triggered[0]['name'] == 'Test Alert 1'
        assert triggered[0]['type'] == 'table'
    
    def test_get_release_schedule(self):
        """Test getting release schedule."""
        alerts = RBAAlerts()
        schedule = alerts.get_release_schedule()
        
        assert isinstance(schedule, pd.DataFrame)
        assert len(schedule) > 0
        assert 'release' in schedule.columns
        assert 'frequency' in schedule.columns
        assert 'typical_day' in schedule.columns
        assert 'typical_time' in schedule.columns
        
        # Check specific releases
        releases = schedule['release'].tolist()
        assert any('Consumer Price Inflation' in r for r in releases)
        assert any('Statement on Monetary Policy' in r for r in releases)
        assert any('Chart Pack' in r for r in releases)
    
    def test_set_notification_method(self):
        """Test setting notification method (placeholder)."""
        alerts = RBAAlerts()
        
        # Should not raise
        alerts.set_notification_method(
            'webhook',
            {'url': 'https://example.com/webhook'}
        )
    
    def test_has_new_release(self):
        """Test checking for new release (placeholder)."""
        alerts = RBAAlerts()
        
        # Currently always returns False
        assert alerts._has_new_release({'id': 'test'}) is False
    
    @patch('rbadata.alerts.RBAAlerts._save_alerts')
    def test_trigger_alert(self, mock_save):
        """Test triggering an alert."""
        alerts = RBAAlerts()
        mock_callback = Mock()
        
        alerts.alerts = {
            'test123': {
                'id': 'test123',
                'last_triggered': None
            }
        }
        alerts._callbacks = {'test123': mock_callback}
        
        alerts._trigger_alert('test123')
        
        # Check last_triggered updated
        assert alerts.alerts['test123']['last_triggered'] is not None
        mock_save.assert_called_once()
        mock_callback.assert_called_once()
    
    @patch('rbadata.alerts.RBAAlerts._save_alerts')
    @patch('builtins.print')
    def test_trigger_alert_callback_error(self, mock_print, mock_save):
        """Test triggering alert with callback error."""
        alerts = RBAAlerts()
        
        def bad_callback():
            raise ValueError("Test error")
        
        alerts.alerts = {
            'test123': {
                'id': 'test123',
                'last_triggered': None
            }
        }
        alerts._callbacks = {'test123': bad_callback}
        
        # Should not raise
        alerts._trigger_alert('test123')
        
        # Error should be printed
        mock_print.assert_called_once()
        assert "Error in alert callback" in str(mock_print.call_args)
    
    def test_generate_alert_id(self):
        """Test generating alert ID."""
        alerts = RBAAlerts()
        
        alert_id = alerts._generate_alert_id()
        
        assert isinstance(alert_id, str)
        assert len(alert_id) == 8
    
    @patch('pathlib.Path.home')
    @patch('pathlib.Path.mkdir')
    def test_get_default_config_path(self, mock_mkdir, mock_home):
        """Test getting default config path."""
        mock_home.return_value = Path('/mock/home')
        
        with patch('rbadata.alerts.RBAAlerts._load_alerts', return_value={}):
            alerts = RBAAlerts()
            config_path = alerts._get_default_config_path()
        
        assert str(config_path) == '/mock/home/.rbadata/alerts.json'
    
    @patch('pathlib.Path.exists')
    def test_load_alerts_no_file(self, mock_exists):
        """Test loading alerts when file doesn't exist."""
        mock_exists.return_value = False
        
        alerts = RBAAlerts()
        result = alerts._load_alerts()
        
        assert result == {}
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_alerts_valid_file(self, mock_file, mock_exists):
        """Test loading alerts from valid file."""
        mock_exists.return_value = True
        alert_data = {'alert1': {'id': 'alert1'}}
        mock_file.return_value.read.return_value = json.dumps(alert_data)
        
        alerts = RBAAlerts()
        result = alerts._load_alerts()
        
        assert result == alert_data
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', side_effect=json.JSONDecodeError('test', 'doc', 0))
    def test_load_alerts_invalid_json(self, mock_file, mock_exists):
        """Test loading alerts from invalid JSON file."""
        mock_exists.return_value = True
        
        alerts = RBAAlerts()
        result = alerts._load_alerts()
        
        assert result == {}
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    def test_save_alerts(self, mock_exists, mock_mkdir, mock_file):
        """Test saving alerts to file."""
        mock_exists.return_value = False  # File doesn't exist during init
        alerts = RBAAlerts()
        alerts.config_file = '/test/alerts.json'
        alerts.alerts = {'alert1': {'id': 'alert1'}}
        
        alerts._save_alerts()
        
        # Check file was written with correct mode
        # Find the call with 'w' mode (write mode)
        write_calls = [call for call in mock_file.call_args_list if 'w' in str(call)]
        assert len(write_calls) == 1
        assert Path('/test/alerts.json') == write_calls[0][0][0]
        
        written_data = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        assert 'alert1' in written_data


class TestCreateAlert:
    """Test the create_alert convenience function."""
    
    @patch('rbadata.alerts.RBAAlerts.add_alert')
    def test_create_alert_table(self, mock_add):
        """Test creating alert for table."""
        mock_add.return_value = 'test123'
        
        alert_id = create_alert(
            table_no='G1',
            name='CPI Alert'
        )
        
        assert alert_id == 'test123'
        mock_add.assert_called_once_with(
            table_no='G1',
            series_id=None,
            release_type=None,
            name='CPI Alert'
        )
    
    @patch('rbadata.alerts.RBAAlerts.add_alert')
    def test_create_alert_series(self, mock_add):
        """Test creating alert for series."""
        mock_add.return_value = 'test456'
        
        alert_id = create_alert(
            series_id='GCPIAG',
            name='Inflation Series'
        )
        
        assert alert_id == 'test456'
        mock_add.assert_called_once_with(
            table_no=None,
            series_id='GCPIAG',
            release_type=None,
            name='Inflation Series'
        )
    
    @patch('rbadata.alerts.RBAAlerts.add_alert')
    def test_create_alert_release_type(self, mock_add):
        """Test creating alert for release type."""
        mock_add.return_value = 'test789'
        
        alert_id = create_alert(
            release_type='chart-pack',
            name='Chart Pack'
        )
        
        assert alert_id == 'test789'
        mock_add.assert_called_once_with(
            table_no=None,
            series_id=None,
            release_type='chart-pack',
            name='Chart Pack'
        )