"""
Data Browsing and Discovery Examples for rbadata
==============================================

This example demonstrates how to:
- Browse available RBA tables
- Search for specific data series
- Filter tables by topic
- Understand table metadata
- Find the right data for your analysis
"""

import rbadata
import pandas as pd

def main():
    """Main function demonstrating data browsing features."""
    
    print("rbadata Data Browsing Examples")
    print("=" * 50)
    
    # Example 1: Browse all available tables
    print("\n1. Browsing all available RBA tables")
    print("-" * 50)
    
    # Get a list of all available tables
    # This returns a DataFrame with table information
    all_tables = rbadata.browse_rba_tables()
    
    print(f"Total number of available tables: {len(all_tables)}")
    print("\nTable information columns:")
    print(all_tables.columns.tolist())
    
    # Show first few tables
    print("\nFirst 10 tables:")
    print(all_tables[['no', 'title']].head(10))
    
    # Show tables by type
    print("\nTables by type:")
    print(all_tables['current_or_historical'].value_counts())
    
    
    # Example 2: Search for specific topics
    print("\n\n2. Searching for specific topics")
    print("-" * 50)
    
    # Search for inflation-related tables
    inflation_tables = rbadata.browse_rba_tables("inflation")
    
    print(f"Tables related to 'inflation': {len(inflation_tables)}")
    print("\nInflation tables:")
    for _, table in inflation_tables.iterrows():
        print(f"  {table['no']}: {table['title']}")
    
    # Search for other topics
    topics = ["interest", "exchange", "credit", "labour"]
    for topic in topics:
        tables = rbadata.browse_rba_tables(topic)
        print(f"\nTables containing '{topic}': {len(tables)}")
    
    
    # Example 3: Browse available data series
    print("\n\n3. Browsing data series")
    print("-" * 50)
    
    # Get all available series
    # Note: This might be a large dataset
    all_series = rbadata.browse_rba_series()
    
    print(f"Total number of data series: {len(all_series)}")
    print("\nSeries information columns:")
    print(all_series.columns.tolist())
    
    # Show series from a specific table
    g1_series = rbadata.browse_rba_series(table_no="G1")
    print(f"\nNumber of series in table G1: {len(g1_series)}")
    print("\nSample series from G1:")
    print(g1_series[['series_id', 'series', 'frequency']].head())
    
    
    # Example 4: Search for specific series
    print("\n\n4. Searching for specific data series")
    print("-" * 50)
    
    # Search for unemployment-related series
    unemployment_series = rbadata.browse_rba_series("unemployment")
    
    print(f"Series related to 'unemployment': {len(unemployment_series)}")
    print("\nUnemployment series:")
    for _, series in unemployment_series.head(5).iterrows():
        print(f"  {series['series_id']}: {series['series']}")
        print(f"    Table: {series['table_no']}, Frequency: {series['frequency']}")
    
    
    # Example 5: Find series by characteristics
    print("\n\n5. Finding series by characteristics")
    print("-" * 50)
    
    # Get all series and filter by frequency
    all_series = rbadata.browse_rba_series()
    
    # Find daily series
    daily_series = all_series[all_series['frequency'] == 'Daily']
    print(f"Number of daily series: {len(daily_series)}")
    
    # Find quarterly series
    quarterly_series = all_series[all_series['frequency'] == 'Quarterly']
    print(f"Number of quarterly series: {len(quarterly_series)}")
    
    # Show frequency distribution
    print("\nFrequency distribution of all series:")
    print(all_series['frequency'].value_counts())
    
    
    # Example 6: Understanding table readability
    print("\n\n6. Checking table readability")
    print("-" * 50)
    
    # Not all tables can be read by the package
    # The 'readable' column indicates which ones are supported
    tables = rbadata.browse_rba_tables()
    
    readable_tables = tables[tables['readable'] == True]
    non_readable_tables = tables[tables['readable'] == False]
    
    print(f"Readable tables: {len(readable_tables)}")
    print(f"Non-readable tables: {len(non_readable_tables)}")
    
    if len(non_readable_tables) > 0:
        print("\nExamples of non-readable tables (special formats):")
        print(non_readable_tables[['no', 'title']].head())
    
    
    # Example 7: Refreshing table lists
    print("\n\n7. Refreshing table and series lists")
    print("-" * 50)
    
    # The package caches table and series lists for performance
    # You can force a refresh to get the latest information
    print("Refreshing table list from RBA website...")
    
    # This would scrape the RBA website for the latest tables
    # Note: This might take a few seconds
    try:
        fresh_tables = rbadata.browse_rba_tables(refresh=True)
        print(f"Fresh table list loaded: {len(fresh_tables)} tables")
    except Exception as e:
        print(f"Note: Refresh requires internet connection. Error: {e}")
    
    
    # Example 8: Creating a data catalog
    print("\n\n8. Creating a custom data catalog")
    print("-" * 50)
    
    # You can create your own catalog of frequently used series
    my_series_ids = {
        "GCPIAG": "CPI - All Groups",
        "GLFSURSA": "Unemployment Rate (Seasonally Adjusted)",
        "FIRMMCRT": "Cash Rate Target",
        "GRCPBVG": "GDP Growth",
    }
    
    print("My custom data catalog:")
    for series_id, description in my_series_ids.items():
        # Find the series information
        series_info = all_series[all_series['series_id'] == series_id]
        if not series_info.empty:
            info = series_info.iloc[0]
            print(f"\n{series_id}: {description}")
            print(f"  Official name: {info['series']}")
            print(f"  Table: {info['table_no']}")
            print(f"  Frequency: {info['frequency']}")
            print(f"  Units: {info.get('units', 'N/A')}")
    
    
    # Example 9: Export browse results
    print("\n\n9. Exporting browse results")
    print("-" * 50)
    
    # You can save browse results for offline reference
    output_file = "rba_tables_catalog.csv"
    
    # Get inflation and interest rate tables
    relevant_tables = pd.concat([
        rbadata.browse_rba_tables("inflation"),
        rbadata.browse_rba_tables("interest")
    ]).drop_duplicates()
    
    print(f"Saving {len(relevant_tables)} relevant tables to {output_file}")
    
    # Uncomment to actually save:
    # relevant_tables.to_csv(output_file, index=False)
    # print(f"Saved to {output_file}")
    
    
    print("\n\nData browsing examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()