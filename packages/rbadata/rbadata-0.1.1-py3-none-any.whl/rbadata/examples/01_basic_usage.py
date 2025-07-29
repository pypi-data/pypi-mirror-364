"""
Basic Usage Examples for rbadata
================================

This example demonstrates the fundamental features of rbadata:
- Reading single tables
- Reading multiple tables
- Reading by series ID
- Understanding the data structure
- Basic data manipulation
"""

import rbadata
import pandas as pd

def main():
    """Main function demonstrating basic rbadata usage."""
    
    print("rbadata Basic Usage Examples")
    print("=" * 50)
    
    # Example 1: Read a single RBA table
    print("\n1. Reading a single table (G1 - Consumer Price Inflation)")
    print("-" * 50)
    
    # Download table G1 which contains CPI data
    # This returns a pandas DataFrame with all series in the table
    cpi_table = rbadata.read_rba(table_no="g1")
    
    # Display basic information about the data
    print(f"Shape of data: {cpi_table.shape}")
    print(f"Date range: {cpi_table['date'].min()} to {cpi_table['date'].max()}")
    print(f"\nColumns in the DataFrame:")
    print(cpi_table.columns.tolist())
    
    # Show first few rows
    print("\nFirst 5 rows:")
    print(cpi_table.head())
    
    # Show unique series in the table
    print(f"\nNumber of unique series: {cpi_table['series_id'].nunique()}")
    print("\nSample series:")
    print(cpi_table['series'].unique()[:5])
    
    
    # Example 2: Read multiple tables at once
    print("\n\n2. Reading multiple tables")
    print("-" * 50)
    
    # You can read multiple tables in a single call
    # This is more efficient than multiple separate calls
    multi_tables = rbadata.read_rba(table_no=["a1", "f1"])
    
    print(f"Total rows from multiple tables: {len(multi_tables)}")
    
    # Show which tables were loaded
    print("\nUnique table titles:")
    for title in multi_tables['table_title'].unique():
        print(f"  - {title}")
    
    
    # Example 3: Read specific series by ID
    print("\n\n3. Reading specific series by ID")
    print("-" * 50)
    
    # If you know the specific series ID you want, you can request it directly
    # GCPIAG is the Consumer Price Index - All Groups
    cpi_series = rbadata.read_rba(series_id="GCPIAG")
    
    print(f"Series: {cpi_series['series'].iloc[0]}")
    print(f"Number of observations: {len(cpi_series)}")
    print(f"Frequency: {cpi_series['frequency'].iloc[0]}")
    print(f"Units: {cpi_series['units'].iloc[0]}")
    
    # Show recent values
    print("\nLast 5 CPI values:")
    print(cpi_series[['date', 'value']].tail())
    
    
    # Example 4: Using the convenience function for series ID
    print("\n\n4. Using read_rba_seriesid convenience function")
    print("-" * 50)
    
    # This is equivalent to read_rba(series_id=...)
    unemployment = rbadata.read_rba_seriesid("GLFSURSA")
    
    print(f"Series: {unemployment['series'].iloc[0]}")
    print(f"Latest unemployment rate: {unemployment['value'].iloc[-1]}%")
    print(f"Date: {unemployment['date'].iloc[-1]}")
    
    
    # Example 5: Reading historical vs current data
    print("\n\n5. Reading historical data")
    print("-" * 50)
    
    # Some tables have both current and historical versions
    # Use cur_hist parameter to specify which one you want
    try:
        # Try to read historical version of table A1
        hist_data = rbadata.read_rba(table_no="a1", cur_hist="historical")
        print(f"Historical data available with {len(hist_data)} rows")
        print(f"Date range: {hist_data['date'].min()} to {hist_data['date'].max()}")
    except Exception as e:
        print(f"Note: {e}")
        print("Not all tables have historical versions")
    
    
    # Example 6: Understanding the data structure
    print("\n\n6. Understanding the data structure")
    print("-" * 50)
    
    # Each row in the DataFrame represents one observation
    # Let's look at the structure in detail
    sample_row = cpi_series.iloc[0]
    
    print("Structure of each row:")
    for col, value in sample_row.items():
        print(f"  {col}: {value} (type: {type(value).__name__})")
    
    
    # Example 7: Basic data filtering and analysis
    print("\n\n7. Basic data filtering and analysis")
    print("-" * 50)
    
    # Filter for recent data (last 2 years)
    recent_cutoff = pd.Timestamp.now() - pd.DateOffset(years=2)
    recent_cpi = cpi_series[cpi_series['date'] >= recent_cutoff]
    
    print(f"CPI observations in last 2 years: {len(recent_cpi)}")
    
    # Calculate year-over-year change
    if len(recent_cpi) >= 4:  # Need at least 4 quarters
        latest_value = recent_cpi['value'].iloc[-1]
        year_ago_value = recent_cpi['value'].iloc[-5]  # 4 quarters ago
        yoy_change = ((latest_value / year_ago_value) - 1) * 100
        print(f"Year-over-year CPI change: {yoy_change:.2f}%")
    
    
    # Example 8: Handling errors
    print("\n\n8. Error handling")
    print("-" * 50)
    
    try:
        # Try to read a non-existent table
        bad_data = rbadata.read_rba(table_no="xyz123")
    except Exception as e:
        print(f"Error caught: {e}")
        print("The package provides clear error messages for invalid inputs")
    
    
    print("\n\nBasic usage examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()