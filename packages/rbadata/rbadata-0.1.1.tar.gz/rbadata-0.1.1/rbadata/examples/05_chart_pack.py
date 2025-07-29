"""
RBA Chart Pack Examples
=======================

This example demonstrates how to:
- Access RBA Chart Pack data
- Browse available chart categories
- Download Chart Pack PDFs
- Work with chart metadata
- Understand Chart Pack structure
"""

import rbadata
from pathlib import Path
import pandas as pd

def main():
    """Main function demonstrating Chart Pack functionality."""
    
    print("rbadata Chart Pack Examples")
    print("=" * 50)
    
    # Example 1: Create Chart Pack instance
    print("\n1. Accessing the RBA Chart Pack")
    print("-" * 50)
    
    # Get Chart Pack instance
    chart_pack = rbadata.get_chart_pack()
    
    # Alternative: Create instance directly
    cp = rbadata.ChartPack()
    
    print("Chart Pack instance created successfully")
    print("The Chart Pack provides graphical summaries of economic data")
    print("Released 8 times per year following key data releases")
    
    
    # Example 2: Get available categories
    print("\n\n2. Browsing Chart Pack categories")
    print("-" * 50)
    
    # Get list of chart categories
    categories = chart_pack.get_categories()
    
    print(f"Number of chart categories: {len(categories)}")
    print("\nAvailable categories:")
    for i, category in enumerate(categories, 1):
        print(f"  {i}. {category}")
    
    
    # Example 3: Get charts by category
    print("\n\n3. Getting charts by category")
    print("-" * 50)
    
    # Get all charts in the inflation category
    inflation_charts = chart_pack.get_charts_by_category("inflation")
    
    print(f"Number of inflation charts: {len(inflation_charts)}")
    print("\nInflation-related charts:")
    for chart in inflation_charts:
        print(f"  - {chart['title']}")
        print(f"    ID: {chart['id']}")
        print(f"    Category: {chart['category']}")
    
    # Try another category
    print("\nWorld Economy charts:")
    world_charts = chart_pack.get_charts_by_category("world economy")
    for chart in world_charts[:5]:  # Show first 5
        print(f"  - {chart['title']}")
    
    
    # Example 4: Get all available charts
    print("\n\n4. Getting all available charts")
    print("-" * 50)
    
    # Get complete list of all charts
    all_charts = chart_pack.get_all_charts()
    
    print(f"Total number of charts: {len(all_charts)}")
    
    # Group charts by category
    charts_df = pd.DataFrame(all_charts)
    if not charts_df.empty:
        category_counts = charts_df['category'].value_counts()
        print("\nCharts per category:")
        for category, count in category_counts.items():
            print(f"  {category}: {count} charts")
    
    
    # Example 5: Download Chart Pack PDF
    print("\n\n5. Downloading Chart Pack PDF")
    print("-" * 50)
    
    # Download the latest Chart Pack
    # Note: This will save to a temporary directory by default
    try:
        pdf_path = chart_pack.download_chart_pack()
        print(f"Chart Pack downloaded to: {pdf_path}")
        print(f"File size: {pdf_path.stat().st_size / 1024 / 1024:.1f} MB")
    except Exception as e:
        print(f"Note: Download requires internet connection. Error: {e}")
    
    # Download to specific location
    # output_dir = Path("./downloads")
    # output_dir.mkdir(exist_ok=True)
    # pdf_path = chart_pack.download_chart_pack(output_path=output_dir / "rba_chart_pack.pdf")
    
    
    # Example 6: Get Chart Pack metadata
    print("\n\n6. Chart Pack metadata")
    print("-" * 50)
    
    # Get the latest release date
    try:
        latest_date = chart_pack.get_latest_release_date()
        print(f"Latest Chart Pack release: {latest_date}")
    except:
        print("Release date information not available")
    
    # Chart Pack is typically released:
    release_schedule = [
        "Following the quarterly Statement on Monetary Policy",
        "After major economic data releases",
        "Approximately 8 times per year",
        "Usually on Tuesdays or Wednesdays"
    ]
    
    print("\nChart Pack release schedule:")
    for item in release_schedule:
        print(f"  • {item}")
    
    
    # Example 7: Search for specific charts
    print("\n\n7. Searching for specific charts")
    print("-" * 50)
    
    # Search for charts by keyword in title
    search_terms = ["GDP", "unemployment", "interest", "exchange"]
    
    all_charts = chart_pack.get_all_charts()
    
    for term in search_terms:
        matching_charts = [
            chart for chart in all_charts
            if term.lower() in chart['title'].lower()
        ]
        print(f"\nCharts containing '{term}': {len(matching_charts)}")
        for chart in matching_charts[:3]:  # Show first 3
            print(f"  - {chart['title']}")
    
    
    # Example 8: Chart Pack structure
    print("\n\n8. Understanding Chart Pack structure")
    print("-" * 50)
    
    # Typical Chart Pack structure
    structure = {
        "Overview": "Economic conditions summary",
        "World Economy": "Global GDP, trade, commodity prices",
        "Australian Growth": "GDP, consumption, investment",
        "Labour Market": "Employment, unemployment, wages",
        "Inflation": "CPI, underlying inflation, expectations",
        "Interest Rates": "Cash rate, bond yields, mortgage rates",
        "Exchange Rates": "AUD/USD, TWI, cross rates",
        "Credit and Money": "Credit growth, money supply",
        "Housing": "Prices, construction, lending",
        "Financial Markets": "Equity markets, volatility"
    }
    
    print("Typical Chart Pack sections:")
    for section, description in structure.items():
        print(f"  {section}: {description}")
    
    
    # Example 9: Working with chart data
    print("\n\n9. Working with chart information")
    print("-" * 50)
    
    # Create a catalog of key economic charts
    key_charts = {
        "gdp-growth": "GDP Growth - Australia",
        "unemployment": "Unemployment Rate",
        "cpi": "Consumer Price Inflation",
        "cash-rate": "Cash Rate",
        "aud": "Australian Dollar",
        "house-prices": "Housing Prices"
    }
    
    print("Key economic indicator charts:")
    all_charts = chart_pack.get_all_charts()
    
    for chart_id, expected_title in key_charts.items():
        # Find matching chart
        matching = [c for c in all_charts if c['id'] == chart_id]
        if matching:
            chart = matching[0]
            print(f"\n{expected_title}:")
            print(f"  Category: {chart['category']}")
            print(f"  Chart ID: {chart['id']}")
        else:
            print(f"\n{expected_title}: Not found with ID '{chart_id}'")
    
    
    # Example 10: Chart Pack vs Statistical Tables
    print("\n\n10. Chart Pack vs Statistical Tables")
    print("-" * 50)
    
    print("Key differences:")
    print("\nChart Pack:")
    print("  • Visual representation of data")
    print("  • Curated selection of key indicators")
    print("  • Published 8 times per year")
    print("  • PDF format with graphs")
    print("  • Good for overview and trends")
    
    print("\nStatistical Tables:")
    print("  • Raw numerical data")
    print("  • Comprehensive coverage")
    print("  • Updated more frequently")
    print("  • Excel format")
    print("  • Good for detailed analysis")
    
    # Note about data extraction
    print("\nNote: The Chart Pack provides visualizations.")
    print("For the underlying data, use the corresponding statistical tables:")
    print("  • GDP data: Table G1")
    print("  • Inflation: Tables G1-G3")
    print("  • Interest rates: Tables F1-F5")
    print("  • Exchange rates: Table F11")
    
    
    print("\n\nChart Pack examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()