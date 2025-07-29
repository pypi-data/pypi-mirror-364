"""
RBA Forecasts Examples
======================

This example demonstrates how to:
- Access RBA economic forecasts
- Get historical forecast data since 1990
- Filter forecasts by variable and date
- Analyze forecast accuracy
- Visualize forecast evolution
"""

import rbadata
import pandas as pd
from datetime import datetime

# Optional: For visualization examples
try:
    import matplotlib.pyplot as plt
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("Note: Install matplotlib for visualization examples")

def main():
    """Main function demonstrating RBA forecasts functionality."""
    
    print("rbadata RBA Forecasts Examples")
    print("=" * 50)
    
    # Example 1: Get all RBA forecasts
    print("\n1. Getting all RBA forecasts")
    print("-" * 50)
    
    # This retrieves all public RBA forecasts since 1990
    # Note: This might take a moment as it compiles data from multiple sources
    all_forecasts = rbadata.rba_forecasts()
    
    print(f"Total forecast observations: {len(all_forecasts)}")
    print(f"Date range: {all_forecasts['forecast_date'].min()} to {all_forecasts['forecast_date'].max()}")
    
    # Show available columns
    print("\nForecast data columns:")
    print(all_forecasts.columns.tolist())
    
    # Show available forecast series
    print("\nAvailable forecast series:")
    for series in all_forecasts['series'].unique():
        series_desc = all_forecasts[all_forecasts['series'] == series]['series_desc'].iloc[0]
        print(f"  {series}: {series_desc}")
    
    
    # Example 2: Get only the latest forecasts
    print("\n\n2. Getting latest forecasts only")
    print("-" * 50)
    
    # Get just the most recent set of forecasts
    latest_forecasts = rbadata.rba_forecasts(all_or_latest="latest")
    
    latest_date = latest_forecasts['forecast_date'].iloc[0]
    print(f"Latest forecast date: {latest_date}")
    print(f"Number of forecast points: {len(latest_forecasts)}")
    
    # Show latest forecasts for key variables
    print("\nLatest forecasts summary:")
    for series in ['gdp_change', 'cpi_annual', 'unemp_rate']:
        series_data = latest_forecasts[latest_forecasts['series'] == series]
        if not series_data.empty:
            desc = series_data['series_desc'].iloc[0]
            print(f"\n{desc}:")
            for _, row in series_data.head(4).iterrows():
                print(f"  {row['date'].strftime('%Y-%m')}: {row['value']}%")
    
    
    # Example 3: Filter forecasts by series
    print("\n\n3. Filtering forecasts by series")
    print("-" * 50)
    
    # Get all inflation forecasts
    inflation_forecasts = all_forecasts[all_forecasts['series'] == 'cpi_annual']
    
    print(f"Total inflation forecast observations: {len(inflation_forecasts)}")
    print(f"Number of unique forecast dates: {inflation_forecasts['forecast_date'].nunique()}")
    
    # Show how inflation forecasts have evolved
    print("\nEvolution of inflation forecasts for 2024:")
    target_year = 2024
    forecasts_2024 = inflation_forecasts[
        inflation_forecasts['date'].dt.year == target_year
    ].sort_values('forecast_date')
    
    if not forecasts_2024.empty:
        for _, row in forecasts_2024.tail(5).iterrows():
            print(f"  Forecast made on {row['forecast_date'].strftime('%Y-%m-%d')}: {row['value']}%")
    
    
    # Example 4: Analyze forecast accuracy
    print("\n\n4. Analyzing forecast accuracy")
    print("-" * 50)
    
    # Compare forecasts with actual outcomes
    # First, get actual CPI data
    actual_cpi = rbadata.read_rba(series_id="GCPIAGSAQP")  # CPI annual % change
    
    # Merge forecasts with actuals
    # This is a simplified example - proper analysis would need more careful date matching
    print("Comparing forecasts with actual outcomes...")
    
    # Get forecasts made 1 year ahead
    one_year_ahead = inflation_forecasts.copy()
    one_year_ahead['forecast_horizon_days'] = (
        one_year_ahead['date'] - one_year_ahead['forecast_date']
    ).dt.days
    
    # Filter for approximately 1-year ahead forecasts (300-400 days)
    one_year_forecasts = one_year_ahead[
        (one_year_ahead['forecast_horizon_days'] > 300) & 
        (one_year_ahead['forecast_horizon_days'] < 400)
    ]
    
    print(f"One-year ahead forecasts: {len(one_year_forecasts)}")
    
    
    # Example 5: Track forecast revisions
    print("\n\n5. Tracking forecast revisions")
    print("-" * 50)
    
    # See how forecasts for a specific date have been revised over time
    target_date = pd.Timestamp('2024-12-31')
    
    revisions = all_forecasts[
        (all_forecasts['date'] == target_date) & 
        (all_forecasts['series'] == 'gdp_change')
    ].sort_values('forecast_date')
    
    if not revisions.empty:
        print(f"GDP growth forecasts for {target_date.strftime('%Y-%m')}:")
        print("Forecast Date    |  Forecast Value")
        print("-" * 35)
        for _, row in revisions.iterrows():
            print(f"{row['forecast_date'].strftime('%Y-%m-%d')}      |  {row['value']:.1f}%")
    
    
    # Example 6: Forecast sources
    print("\n\n6. Understanding forecast sources")
    print("-" * 50)
    
    # RBA forecasts come from different sources over time
    print("Forecast sources:")
    print(all_forecasts['source'].value_counts())
    
    # Show date ranges for each source
    print("\nDate ranges by source:")
    for source in all_forecasts['source'].unique():
        source_data = all_forecasts[all_forecasts['source'] == source]
        date_range = f"{source_data['forecast_date'].min()} to {source_data['forecast_date'].max()}"
        print(f"  {source}: {date_range}")
    
    
    # Example 7: Export forecasts for analysis
    print("\n\n7. Exporting forecasts for analysis")
    print("-" * 50)
    
    # Create a pivot table of GDP forecasts
    gdp_forecasts = all_forecasts[all_forecasts['series'] == 'gdp_change'].copy()
    
    # Create year-quarter string for easier pivoting
    gdp_forecasts['target_period'] = (
        gdp_forecasts['date'].dt.year.astype(str) + '-Q' + 
        gdp_forecasts['date'].dt.quarter.astype(str)
    )
    
    # Pivot to have forecast dates as columns
    gdp_pivot = gdp_forecasts.pivot_table(
        index='target_period',
        columns='forecast_date',
        values='value'
    )
    
    print("GDP forecast matrix shape:", gdp_pivot.shape)
    print("\nSample of GDP forecast evolution:")
    print(gdp_pivot.iloc[:5, -5:])  # Last 5 forecasts for first 5 periods
    
    
    # Example 8: Visualization (if matplotlib available)
    if PLOTTING_AVAILABLE:
        print("\n\n8. Visualizing forecast evolution")
        print("-" * 50)
        
        # Plot how inflation forecasts for 2024 have evolved
        target_year = 2024
        inflation_2024 = all_forecasts[
            (all_forecasts['series'] == 'cpi_annual') &
            (all_forecasts['date'].dt.year == target_year)
        ]
        
        if not inflation_2024.empty:
            plt.figure(figsize=(10, 6))
            
            # Group by quarter
            for quarter in [1, 2, 3, 4]:
                quarter_data = inflation_2024[
                    inflation_2024['date'].dt.quarter == quarter
                ]
                if not quarter_data.empty:
                    plt.plot(
                        quarter_data['forecast_date'],
                        quarter_data['value'],
                        marker='o',
                        label=f'Q{quarter} {target_year}'
                    )
            
            plt.xlabel('Forecast Date')
            plt.ylabel('Inflation Forecast (%)')
            plt.title(f'Evolution of {target_year} Inflation Forecasts')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Uncomment to display:
            # plt.show()
            
            print("Visualization created (uncomment plt.show() to display)")
    
    
    print("\n\nRBA forecasts examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()