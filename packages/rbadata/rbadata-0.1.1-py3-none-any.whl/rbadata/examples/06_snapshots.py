"""
RBA Economic Snapshots Examples
================================

This example demonstrates how to:
- Access RBA Economic Snapshots
- Get key economic indicators
- Work with economy composition data
- Analyze payment methods data
- Download snapshot PDFs
"""

import rbadata
import pandas as pd
from pathlib import Path

def main():
    """Main function demonstrating Snapshots functionality."""
    
    print("rbadata Economic Snapshots Examples")
    print("=" * 50)
    
    # Example 1: Access Snapshots
    print("\n1. Accessing RBA Economic Snapshots")
    print("-" * 50)
    
    # Get Snapshots instance
    snapshots = rbadata.get_snapshots()
    
    # Alternative: Create instance directly
    # snapshots = rbadata.Snapshots()
    
    print("Snapshots instance created successfully")
    print("\nRBA provides three types of snapshots:")
    print("  1. Key Economic Indicators")
    print("  2. Composition of the Australian Economy")
    print("  3. How Australians Pay")
    
    
    # Example 2: Get snapshot types
    print("\n\n2. Available snapshot types")
    print("-" * 50)
    
    # Get available snapshot types and metadata
    snapshot_types = snapshots.get_snapshot_types()
    
    print("Available snapshots:")
    for key, info in snapshot_types.items():
        print(f"\n{key}:")
        print(f"  Name: {info['name']}")
        print(f"  Description: {info['description']}")
        print(f"  URL path: {info['url']}")
    
    
    # Example 3: Get economic indicators
    print("\n\n3. Key Economic Indicators Snapshot")
    print("-" * 50)
    
    # Get the latest economic indicators
    indicators = snapshots.get_economic_indicators()
    
    print(f"Number of indicators: {len(indicators)}")
    print("\nKey Economic Indicators:")
    print("-" * 60)
    print(f"{'Indicator':<20} {'Value':<10} {'Unit':<15} {'Previous':<10}")
    print("-" * 60)
    
    for _, row in indicators.iterrows():
        print(f"{row['indicator']:<20} {row['value']:<10} {row['unit']:<15} {row.get('previous', 'N/A'):<10}")
    
    # Using convenience function
    print("\n\nUsing convenience function:")
    quick_indicators = rbadata.get_economic_indicators()
    print(f"Retrieved {len(quick_indicators)} indicators")
    
    
    # Example 4: Analyze economic indicators
    print("\n\n4. Analyzing economic indicators")
    print("-" * 50)
    
    # Calculate changes from previous values
    indicators_with_change = indicators.copy()
    if 'previous' in indicators.columns:
        indicators_with_change['change'] = indicators['value'] - indicators['previous']
        indicators_with_change['change_pct'] = (
            (indicators['value'] / indicators['previous'] - 1) * 100
        ).round(2)
        
        print("Indicators with largest changes:")
        print("-" * 50)
        
        # Sort by absolute percentage change
        indicators_with_change['abs_change_pct'] = indicators_with_change['change_pct'].abs()
        top_changes = indicators_with_change.nlargest(5, 'abs_change_pct')
        
        for _, row in top_changes.iterrows():
            direction = "↑" if row['change'] > 0 else "↓"
            print(f"{row['indicator']}: {row['change_pct']:+.2f}% {direction}")
    
    
    # Example 5: Economy composition
    print("\n\n5. Composition of Australian Economy")
    print("-" * 50)
    
    # Get economy composition data
    composition = snapshots.get_economy_composition()
    
    print("Australian Economy Composition:")
    print("-" * 40)
    print(f"{'Sector':<20} {'Share':<10} {'Unit'}")
    print("-" * 40)
    
    for _, row in composition.iterrows():
        print(f"{row['sector']:<20} {row['share']:<10.1f} {row['unit']}")
    
    # Calculate and display insights
    total_share = composition['share'].sum()
    print(f"\nTotal: {total_share:.1f}%")
    
    # Find dominant sectors
    print("\nDominant sectors (>5% of GDP):")
    major_sectors = composition[composition['share'] > 5].sort_values('share', ascending=False)
    for _, sector in major_sectors.iterrows():
        print(f"  • {sector['sector']}: {sector['share']:.1f}%")
    
    
    # Example 6: Payment methods
    print("\n\n6. How Australians Pay")
    print("-" * 50)
    
    # Get payment methods data
    payments = snapshots.get_payment_methods()
    
    print("Payment Methods Usage:")
    print("-" * 60)
    print(f"{'Method':<15} {'Value Share':<15} {'Transaction Share':<20} {'Year'}")
    print("-" * 60)
    
    for _, row in payments.iterrows():
        print(f"{row['method']:<15} {row['share']:<14}% {row['transactions']:<19}% {row['year']}")
    
    # Analyze payment trends
    if 'share' in payments.columns:
        # Find most and least used methods
        most_used = payments.loc[payments['share'].idxmax()]
        least_used = payments.loc[payments['share'].idxmin()]
        
        print(f"\nMost used payment method: {most_used['method']} ({most_used['share']}% by value)")
        print(f"Least used payment method: {least_used['method']} ({least_used['share']}% by value)")
    
    
    # Example 7: Download snapshot PDFs
    print("\n\n7. Downloading snapshot PDFs")
    print("-" * 50)
    
    # Download economic indicators snapshot
    try:
        pdf_path = snapshots.download_snapshot("economic-indicators")
        print(f"Economic indicators snapshot downloaded to: {pdf_path}")
        print(f"File size: {pdf_path.stat().st_size / 1024:.1f} KB")
    except Exception as e:
        print(f"Download failed: {e}")
    
    # Download all snapshots to a specific directory
    # output_dir = Path("./snapshots")
    # output_dir.mkdir(exist_ok=True)
    # 
    # for snapshot_type in ["economic-indicators", "economy-composition", "payments"]:
    #     try:
    #         pdf_path = snapshots.download_snapshot(
    #             snapshot_type,
    #             output_path=output_dir / f"{snapshot_type}.pdf"
    #         )
    #         print(f"Downloaded: {pdf_path.name}")
    #     except Exception as e:
    #         print(f"Failed to download {snapshot_type}: {e}")
    
    
    # Example 8: Refresh snapshot data
    print("\n\n8. Refreshing snapshot data")
    print("-" * 50)
    
    # Snapshots are cached for performance
    # You can force a refresh to get the latest data
    
    print("Getting fresh economic indicators...")
    fresh_indicators = snapshots.get_economic_indicators(refresh=True)
    print(f"Refreshed {len(fresh_indicators)} indicators")
    
    # Compare with cached data
    cached_indicators = snapshots.get_economic_indicators(refresh=False)
    print(f"Cached version has {len(cached_indicators)} indicators")
    
    
    # Example 9: Create economic dashboard data
    print("\n\n9. Creating economic dashboard data")
    print("-" * 50)
    
    # Combine different snapshots for a comprehensive view
    dashboard_data = {}
    
    # Get all snapshot data
    dashboard_data['indicators'] = snapshots.get_economic_indicators()
    dashboard_data['composition'] = snapshots.get_economy_composition()
    dashboard_data['payments'] = snapshots.get_payment_methods()
    
    print("Dashboard data collected:")
    for key, df in dashboard_data.items():
        print(f"  {key}: {len(df)} rows")
    
    # Create a summary
    print("\nEconomic Summary:")
    print("-" * 50)
    
    # Key indicators
    key_metrics = ['GDP Growth', 'Unemployment Rate', 'CPI Inflation', 'Cash Rate']
    indicators_df = dashboard_data['indicators']
    
    for metric in key_metrics:
        matching = indicators_df[indicators_df['indicator'] == metric]
        if not matching.empty:
            row = matching.iloc[0]
            print(f"{metric}: {row['value']} {row['unit']}")
    
    # Largest economic sector
    if not dashboard_data['composition'].empty:
        largest_sector = dashboard_data['composition'].loc[
            dashboard_data['composition']['share'].idxmax()
        ]
        print(f"\nLargest sector: {largest_sector['sector']} ({largest_sector['share']:.1f}% of GDP)")
    
    # Most popular payment method
    if not dashboard_data['payments'].empty:
        popular_payment = dashboard_data['payments'].loc[
            dashboard_data['payments']['share'].idxmax()
        ]
        print(f"Most used payment: {popular_payment['method']} ({popular_payment['share']}% by value)")
    
    
    # Example 10: Export snapshot data
    print("\n\n10. Exporting snapshot data")
    print("-" * 50)
    
    # Export to various formats for further analysis
    
    # Export to CSV
    output_file = "economic_indicators.csv"
    # indicators.to_csv(output_file, index=False)
    print(f"Would export indicators to {output_file}")
    
    # Export to Excel with multiple sheets
    excel_file = "rba_snapshots.xlsx"
    # with pd.ExcelWriter(excel_file) as writer:
    #     dashboard_data['indicators'].to_excel(writer, sheet_name='Indicators', index=False)
    #     dashboard_data['composition'].to_excel(writer, sheet_name='Composition', index=False)
    #     dashboard_data['payments'].to_excel(writer, sheet_name='Payments', index=False)
    print(f"Would export all snapshots to {excel_file}")
    
    # Create a formatted report
    print("\nSnapshot data can be exported for:")
    print("  • Regular monitoring and reporting")
    print("  • Historical comparison")
    print("  • Integration with BI tools")
    print("  • Custom visualizations")
    
    
    print("\n\nEconomic Snapshots examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()