"""
RBA Data Release Alerts Examples
=================================

This example demonstrates how to:
- Set up alerts for new data releases
- Manage alert configurations
- Monitor specific tables and series
- View RBA release schedules
- Create custom notification workflows
"""

import rbadata
import pandas as pd
from datetime import datetime, time

def main():
    """Main function demonstrating alerts functionality."""
    
    print("rbadata Data Release Alerts Examples")
    print("=" * 50)
    
    # Example 1: Create alerts instance
    print("\n1. Setting up RBA Alerts")
    print("-" * 50)
    
    # Create alerts manager
    alerts = rbadata.RBAAlerts()
    
    print("Alerts manager created successfully")
    print("Alerts are stored in your home directory by default")
    print(f"Config location: ~/.rbadata/alerts.json")
    
    
    # Example 2: Create basic alerts
    print("\n\n2. Creating basic alerts")
    print("-" * 50)
    
    # Alert for CPI data (Table G1)
    alert_id1 = alerts.add_alert(
        table_no="G1",
        name="CPI Data Release"
    )
    print(f"Created alert for CPI data: {alert_id1}")
    
    # Alert for unemployment data
    alert_id2 = alerts.add_alert(
        series_id="GLFSURSA",
        name="Unemployment Rate Update"
    )
    print(f"Created alert for unemployment rate: {alert_id2}")
    
    # Alert for Chart Pack releases
    alert_id3 = alerts.add_alert(
        release_type="chart-pack",
        name="New Chart Pack Available"
    )
    print(f"Created alert for Chart Pack: {alert_id3}")
    
    
    # Example 3: Using convenience function
    print("\n\n3. Using convenience function for alerts")
    print("-" * 50)
    
    # Quick way to create alerts
    quick_alert = rbadata.create_alert(
        table_no="F1",
        name="Interest Rates Update"
    )
    print(f"Quick alert created: {quick_alert}")
    
    
    # Example 4: List all alerts
    print("\n\n4. Managing alerts")
    print("-" * 50)
    
    # Get all configured alerts
    all_alerts = alerts.list_alerts()
    
    if not all_alerts.empty:
        print(f"Total configured alerts: {len(all_alerts)}")
        print("\nConfigured alerts:")
        print("-" * 70)
        print(f"{'Name':<30} {'Type':<15} {'Enabled':<10} {'Created'}")
        print("-" * 70)
        
        for _, alert in all_alerts.iterrows():
            alert_type = "Table" if alert.get('table_no') else "Series" if alert.get('series_id') else "Release"
            created_date = pd.to_datetime(alert['created']).strftime('%Y-%m-%d')
            print(f"{alert['name']:<30} {alert_type:<15} {str(alert['enabled']):<10} {created_date}")
    
    
    # Example 5: Enable/disable alerts
    print("\n\n5. Enabling and disabling alerts")
    print("-" * 50)
    
    if all_alerts.empty:
        print("No alerts configured yet")
    else:
        # Disable the first alert
        first_alert_id = all_alerts.iloc[0]['id']
        alerts.disable_alert(first_alert_id)
        print(f"Disabled alert: {first_alert_id}")
        
        # Re-enable it
        alerts.enable_alert(first_alert_id)
        print(f"Re-enabled alert: {first_alert_id}")
    
    
    # Example 6: RBA release schedule
    print("\n\n6. RBA release schedule")
    print("-" * 50)
    
    # Get typical release schedule
    schedule = alerts.get_release_schedule()
    
    print("RBA Statistical Release Schedule:")
    print("-" * 80)
    print(f"{'Release':<35} {'Frequency':<20} {'Typical Day':<25}")
    print("-" * 80)
    
    for _, release in schedule.iterrows():
        print(f"{release['release']:<35} {release['frequency']:<20} {release['typical_day']:<25}")
    
    print("\nNote: All releases typically occur at 11:30 AM Sydney time")
    
    
    # Example 7: Create alerts with callbacks
    print("\n\n7. Creating alerts with callbacks")
    print("-" * 50)
    
    # Define callback functions
    def on_cpi_release():
        """Function to run when CPI data is released."""
        print("NEW CPI DATA AVAILABLE!")
        # Here you could:
        # - Download the new data automatically
        # - Run analysis scripts
        # - Send notifications
        # - Update dashboards
    
    def on_forecast_release():
        """Function to run when new forecasts are available."""
        print("NEW RBA FORECASTS AVAILABLE!")
        # Could trigger forecast analysis
    
    # Create alert with callback
    callback_alert = alerts.add_alert(
        table_no="G1",
        name="CPI with Auto-Download",
        callback=on_cpi_release
    )
    print(f"Created alert with callback: {callback_alert}")
    
    
    # Example 8: Check for updates
    print("\n\n8. Checking for updates")
    print("-" * 50)
    
    # Check if any alerts have new data
    # Note: This is a demonstration - actual checking would require
    # comparing with RBA website
    print("Checking for new data releases...")
    
    triggered = alerts.check_for_updates()
    
    if triggered:
        print(f"\n{len(triggered)} alerts triggered:")
        for alert in triggered:
            print(f"  - {alert['name']} at {alert['timestamp']}")
    else:
        print("No new releases detected")
    
    
    # Example 9: Create comprehensive monitoring
    print("\n\n9. Comprehensive data monitoring setup")
    print("-" * 50)
    
    # Key economic data to monitor
    monitoring_config = [
        {"table_no": "A1", "name": "RBA Balance Sheet"},
        {"table_no": "A2", "name": "Monetary Policy Changes"},
        {"table_no": "F1", "name": "Interest Rates"},
        {"table_no": "G1", "name": "Consumer Price Inflation"},
        {"table_no": "G3", "name": "Inflation Expectations"},
        {"table_no": "H1", "name": "Labour Force"},
        {"series_id": "FIRMMCRT", "name": "Cash Rate Target"},
        {"release_type": "smp", "name": "Statement on Monetary Policy"},
        {"release_type": "chart-pack", "name": "Chart Pack"},
        {"release_type": "snapshot", "name": "Economic Snapshot"}
    ]
    
    print("Setting up comprehensive monitoring...")
    
    # Create alerts for all key data
    # for config in monitoring_config:
    #     try:
    #         alert_id = alerts.add_alert(**config)
    #         print(f"  ✓ {config['name']}")
    #     except Exception as e:
    #         print(f"  ✗ {config['name']}: {e}")
    
    print("\nWould monitor all key RBA data releases")
    
    
    # Example 10: Export and backup alerts
    print("\n\n10. Exporting alert configurations")
    print("-" * 50)
    
    # Get all alerts for backup
    all_alerts = alerts.list_alerts()
    
    if not all_alerts.empty:
        # Export to CSV
        backup_file = "rba_alerts_backup.csv"
        # all_alerts.to_csv(backup_file, index=False)
        print(f"Would export {len(all_alerts)} alerts to {backup_file}")
        
        # Create summary report
        print("\nAlert Summary:")
        print(f"  Total alerts: {len(all_alerts)}")
        print(f"  Enabled: {sum(all_alerts['enabled'])}")
        print(f"  Disabled: {sum(~all_alerts['enabled'])}")
        
        # Count by type
        table_alerts = sum(all_alerts['table_no'].notna())
        series_alerts = sum(all_alerts['series_id'].notna())
        release_alerts = sum(all_alerts['release_type'].notna())
        
        print(f"\nBy type:")
        print(f"  Table alerts: {table_alerts}")
        print(f"  Series alerts: {series_alerts}")
        print(f"  Release alerts: {release_alerts}")
    
    
    # Clean up example alerts (optional)
    print("\n\nCleaning up example alerts...")
    # for _, alert in all_alerts.iterrows():
    #     alerts.remove_alert(alert['id'])
    print("Example alerts would be removed")
    
    
    print("\n\nData release alerts examples completed!")
    print("=" * 50)
    
    print("\nNote: Actual alert triggering requires:")
    print("  - Regular checking (e.g., cron job)")
    print("  - Comparison with RBA website")
    print("  - Notification service configuration")


if __name__ == "__main__":
    main()