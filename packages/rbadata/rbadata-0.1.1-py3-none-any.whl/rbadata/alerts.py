"""
RBA statistical release alerts and notifications
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime, time
import pandas as pd
from .exceptions import RBADataError


class RBAAlerts:
    """
    Manage alerts for RBA statistical releases.
    
    This class provides functionality to set up notifications for when
    new RBA data is released. Note: Actual email/SMS functionality would
    require additional configuration and services.
    
    Examples
    --------
    >>> alerts = RBAAlerts()
    >>> # Register for CPI release alerts
    >>> alerts.add_alert(
    ...     table_no="G1",
    ...     name="CPI Alert",
    ...     callback=lambda: print("New CPI data available!")
    ... )
    
    >>> # Check for updates
    >>> alerts.check_for_updates()
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize alerts manager.
        
        Parameters
        ----------
        config_file : str, optional
            Path to alerts configuration file
        """
        self.config_file = config_file or self._get_default_config_path()
        self.alerts = self._load_alerts()
        self._last_check = {}
        self._callbacks = {}
    
    def add_alert(
        self,
        table_no: Optional[str] = None,
        series_id: Optional[str] = None,
        release_type: Optional[str] = None,
        name: Optional[str] = None,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Add a new alert for RBA data releases.
        
        Parameters
        ----------
        table_no : str, optional
            RBA table number to monitor
        series_id : str, optional
            Specific series ID to monitor
        release_type : str, optional
            Type of release (e.g., "chart-pack", "snapshot", "smp")
        name : str, optional
            Friendly name for the alert
        callback : callable, optional
            Function to call when new data is detected
            
        Returns
        -------
        str
            Alert ID
            
        Examples
        --------
        >>> alerts.add_alert(table_no="G1", name="Inflation Data")
        >>> alerts.add_alert(release_type="chart-pack", name="Chart Pack Release")
        """
        # Validate inputs
        if not any([table_no, series_id, release_type]):
            raise RBADataError(
                "Must specify at least one of: table_no, series_id, or release_type"
            )
        
        # Generate alert ID
        alert_id = self._generate_alert_id()
        
        # Create alert configuration
        alert_config = {
            "id": alert_id,
            "name": name or f"Alert {alert_id}",
            "table_no": table_no,
            "series_id": series_id,
            "release_type": release_type,
            "created": datetime.now().isoformat(),
            "enabled": True,
            "last_triggered": None
        }
        
        # Store alert
        self.alerts[alert_id] = alert_config
        
        # Store callback if provided
        if callback:
            self._callbacks[alert_id] = callback
        
        # Save configuration
        self._save_alerts()
        
        return alert_id
    
    def remove_alert(self, alert_id: str):
        """
        Remove an alert.
        
        Parameters
        ----------
        alert_id : str
            ID of the alert to remove
        """
        if alert_id not in self.alerts:
            raise RBADataError(f"Alert '{alert_id}' not found")
        
        del self.alerts[alert_id]
        
        if alert_id in self._callbacks:
            del self._callbacks[alert_id]
        
        self._save_alerts()
    
    def list_alerts(self) -> pd.DataFrame:
        """
        List all configured alerts.
        
        Returns
        -------
        pd.DataFrame
            DataFrame of alert configurations
        """
        if not self.alerts:
            return pd.DataFrame()
        
        return pd.DataFrame.from_dict(self.alerts, orient="index")
    
    def enable_alert(self, alert_id: str):
        """Enable a specific alert."""
        if alert_id not in self.alerts:
            raise RBADataError(f"Alert '{alert_id}' not found")
        
        self.alerts[alert_id]["enabled"] = True
        self._save_alerts()
    
    def disable_alert(self, alert_id: str):
        """Disable a specific alert."""
        if alert_id not in self.alerts:
            raise RBADataError(f"Alert '{alert_id}' not found")
        
        self.alerts[alert_id]["enabled"] = False
        self._save_alerts()
    
    def check_for_updates(self) -> List[Dict[str, str]]:
        """
        Check for new releases and trigger alerts.
        
        Returns
        -------
        list of dict
            List of triggered alerts with details
        """
        triggered = []
        
        for alert_id, config in self.alerts.items():
            if not config["enabled"]:
                continue
            
            # Check if this release has new data
            if self._has_new_release(config):
                # Trigger alert
                self._trigger_alert(alert_id)
                
                triggered.append({
                    "alert_id": alert_id,
                    "name": config["name"],
                    "type": config.get("release_type", "table"),
                    "timestamp": datetime.now().isoformat()
                })
        
        return triggered
    
    def get_release_schedule(self) -> pd.DataFrame:
        """
        Get typical RBA release schedule.
        
        Returns
        -------
        pd.DataFrame
            Release schedule information
        """
        # Typical RBA release schedule
        schedule = [
            {
                "release": "Consumer Price Inflation (G1-G3)",
                "frequency": "Monthly",
                "typical_day": "Last Wednesday",
                "typical_time": "11:30 AM"
            },
            {
                "release": "Statement on Monetary Policy",
                "frequency": "Quarterly",
                "typical_day": "First Friday of Feb, May, Aug, Nov",
                "typical_time": "11:30 AM"
            },
            {
                "release": "Chart Pack",
                "frequency": "8 times per year",
                "typical_day": "Following key data releases",
                "typical_time": "Various"
            },
            {
                "release": "Financial Aggregates",
                "frequency": "Monthly", 
                "typical_day": "Last business day",
                "typical_time": "11:30 AM"
            },
            {
                "release": "Retail Payments",
                "frequency": "Monthly",
                "typical_day": "Around 15th",
                "typical_time": "11:30 AM"
            }
        ]
        
        return pd.DataFrame(schedule)
    
    def set_notification_method(
        self,
        method: str,
        config: Dict[str, str]
    ):
        """
        Configure notification method.
        
        Parameters
        ----------
        method : str
            Notification method ("email", "webhook", "callback")
        config : dict
            Configuration for the notification method
            
        Examples
        --------
        >>> alerts.set_notification_method(
        ...     "webhook",
        ...     {"url": "https://example.com/webhook"}
        ... )
        """
        # This would store notification configuration
        # Actual implementation would depend on notification service
        pass
    
    def _has_new_release(self, alert_config: Dict) -> bool:
        """
        Check if there's a new release for this alert.
        
        In a real implementation, this would:
        1. Check the RBA website for updates
        2. Compare with last known release date
        3. Return True if new data is available
        """
        # Placeholder implementation
        # Would need to actually check RBA website
        return False
    
    def _trigger_alert(self, alert_id: str):
        """Trigger an alert."""
        config = self.alerts[alert_id]
        
        # Update last triggered time
        config["last_triggered"] = datetime.now().isoformat()
        self._save_alerts()
        
        # Call callback if registered
        if alert_id in self._callbacks:
            try:
                self._callbacks[alert_id]()
            except Exception as e:
                print(f"Error in alert callback: {e}")
        
        # Here you would also send email/SMS/webhook notifications
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        from uuid import uuid4
        return str(uuid4())[:8]
    
    def _get_default_config_path(self) -> Path:
        """Get default configuration file path."""
        from pathlib import Path
        config_dir = Path.home() / ".rbadata"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "alerts.json"
    
    def _load_alerts(self) -> Dict:
        """Load alerts from configuration file."""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_alerts(self):
        """Save alerts to configuration file."""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, "w") as f:
            json.dump(self.alerts, f, indent=2)


def create_alert(
    table_no: Optional[str] = None,
    series_id: Optional[str] = None,
    release_type: Optional[str] = None,
    name: Optional[str] = None
) -> str:
    """
    Convenience function to create an RBA data release alert.
    
    Parameters
    ----------
    table_no : str, optional
        RBA table number to monitor
    series_id : str, optional
        Specific series ID to monitor  
    release_type : str, optional
        Type of release (e.g., "chart-pack", "snapshot", "smp")
    name : str, optional
        Friendly name for the alert
        
    Returns
    -------
    str
        Alert ID
        
    Examples
    --------
    >>> # Alert for inflation data
    >>> alert_id = create_alert(table_no="G1", name="CPI Release")
    
    >>> # Alert for Chart Pack
    >>> alert_id = create_alert(release_type="chart-pack", name="Chart Pack")
    """
    alerts = RBAAlerts()
    return alerts.add_alert(
        table_no=table_no,
        series_id=series_id,
        release_type=release_type,
        name=name
    )