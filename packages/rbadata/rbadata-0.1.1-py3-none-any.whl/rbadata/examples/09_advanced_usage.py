"""
Advanced Usage Examples for rbadata
==================================

This example demonstrates:
- Combining multiple data sources
- Building economic dashboards
- Time series analysis
- Data validation and quality checks
- Performance optimization
- Custom data pipelines
"""

import rbadata
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Optional imports for advanced features
try:
    import matplotlib.pyplot as plt
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("Note: Install matplotlib for visualization examples")

def main():
    """Main function demonstrating advanced rbadata usage."""
    
    print("rbadata Advanced Usage Examples")
    print("=" * 50)
    
    # Example 1: Building an economic dashboard
    print("\n1. Building a comprehensive economic dashboard")
    print("-" * 50)
    
    dashboard_data = build_economic_dashboard()
    
    print("Dashboard data collected:")
    for key, value in dashboard_data.items():
        if isinstance(value, pd.DataFrame):
            print(f"  {key}: {len(value)} rows")
        else:
            print(f"  {key}: {value}")
    
    
    # Example 2: Time series alignment and analysis
    print("\n\n2. Time series alignment and analysis")
    print("-" * 50)
    
    # Get multiple related series
    series_ids = {
        "GCPIAG": "CPI",
        "GLFSURSA": "Unemployment Rate",
        "FIRMMCRT": "Cash Rate",
    }
    
    # Download all series
    print("Downloading multiple series...")
    all_series = {}
    for series_id, name in series_ids.items():
        try:
            data = rbadata.read_rba(series_id=series_id)
            all_series[name] = data[['date', 'value']].set_index('date')['value']
            print(f"  ✓ {name}: {len(data)} observations")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
    
    # Align series to common dates
    if len(all_series) > 1:
        aligned_data = pd.DataFrame(all_series)
        aligned_data = aligned_data.dropna()  # Keep only common dates
        
        print(f"\nAligned data shape: {aligned_data.shape}")
        print(f"Date range: {aligned_data.index.min()} to {aligned_data.index.max()}")
        
        # Calculate correlations
        print("\nCorrelations between series:")
        correlations = aligned_data.corr()
        print(correlations)
    
    
    # Example 3: Data quality checks
    print("\n\n3. Data quality and validation")
    print("-" * 50)
    
    # Download a table for quality checks
    table_data = rbadata.read_rba(table_no="G1")
    
    quality_report = perform_quality_checks(table_data)
    
    print("Data Quality Report:")
    for check, result in quality_report.items():
        status = "✓ PASS" if result['status'] else "✗ FAIL"
        print(f"  {check}: {status}")
        if result['details']:
            print(f"    Details: {result['details']}")
    
    
    # Example 4: Bulk data download with error handling
    print("\n\n4. Bulk data download with error handling")
    print("-" * 50)
    
    # Tables to download
    tables_to_download = ["A1", "F1", "G1", "G3", "H1", "XYZ"]  # XYZ is invalid
    
    downloaded_data = {}
    failed_downloads = []
    
    print("Downloading multiple tables...")
    for table in tables_to_download:
        try:
            data = rbadata.read_rba(table_no=table)
            downloaded_data[table] = data
            print(f"  ✓ {table}: {len(data)} rows")
        except Exception as e:
            failed_downloads.append((table, str(e)))
            print(f"  ✗ {table}: Failed")
    
    print(f"\nSuccessfully downloaded: {len(downloaded_data)}/{len(tables_to_download)} tables")
    if failed_downloads:
        print("Failed downloads:")
        for table, error in failed_downloads:
            print(f"  {table}: {error[:50]}...")
    
    
    # Example 5: Creating derived indicators
    print("\n\n5. Creating derived economic indicators")
    print("-" * 50)
    
    # Calculate real interest rate (Cash Rate - CPI inflation)
    try:
        # Get cash rate
        cash_rate = rbadata.read_rba(series_id="FIRMMCRT")
        cash_rate_ts = cash_rate.set_index('date')['value']
        
        # Get CPI annual change
        cpi_change = rbadata.read_rba(series_id="GCPIAGSAQP")
        cpi_ts = cpi_change.set_index('date')['value']
        
        # Calculate real rate
        real_rate = calculate_real_interest_rate(cash_rate_ts, cpi_ts)
        
        print("Real Interest Rate (last 5 observations):")
        print(real_rate.tail())
        
        # Find periods of negative real rates
        negative_periods = real_rate[real_rate < 0]
        if not negative_periods.empty:
            print(f"\nPeriods with negative real rates: {len(negative_periods)}")
            print(f"Most recent: {negative_periods.index[-1].strftime('%Y-%m')}")
    except Exception as e:
        print(f"Could not calculate real rate: {e}")
    
    
    # Example 6: Custom data pipeline
    print("\n\n6. Custom data processing pipeline")
    print("-" * 50)
    
    # Define a data pipeline
    pipeline_config = {
        'name': 'Quarterly Economic Update',
        'sources': [
            {'type': 'table', 'id': 'G1', 'series': 'GCPIAG'},
            {'type': 'table', 'id': 'H1', 'series': 'GLFSURSA'},
            {'type': 'forecast', 'series': 'gdp_change'},
        ],
        'transformations': [
            'convert_to_quarterly',
            'calculate_yoy_change',
            'add_metadata'
        ]
    }
    
    print(f"Pipeline: {pipeline_config['name']}")
    pipeline_result = run_data_pipeline(pipeline_config)
    
    if pipeline_result:
        print(f"Pipeline output: {len(pipeline_result)} datasets")
    
    
    # Example 7: Historical analysis
    print("\n\n7. Historical economic analysis")
    print("-" * 50)
    
    # Analyze economic cycles using historical data
    try:
        # Get long-term GDP data
        gdp_data = rbadata.read_rba(series_id="GGDPECCPGDP")
        
        # Identify recessions (simplified: negative growth)
        gdp_growth = gdp_data.set_index('date')['value']
        recessions = identify_recessions(gdp_growth)
        
        print(f"Identified {len(recessions)} recession periods")
        if recessions:
            print("\nRecent recessions:")
            for start, end in recessions[-3:]:
                duration = (end - start).days / 30  # Approximate months
                print(f"  {start.strftime('%Y-%m')} to {end.strftime('%Y-%m')} ({duration:.0f} months)")
    except Exception as e:
        print(f"Historical analysis failed: {e}")
    
    
    # Example 8: Multi-source data integration
    print("\n\n8. Integrating multiple data sources")
    print("-" * 50)
    
    # Combine RBA data with other sources
    integrated_data = {
        'rba_tables': {},
        'forecasts': None,
        'snapshots': None,
        'metadata': {}
    }
    
    # Get RBA statistical data
    key_tables = ['G1', 'F1', 'H1']
    for table in key_tables:
        try:
            integrated_data['rba_tables'][table] = rbadata.read_rba(table_no=table)
        except:
            pass
    
    # Get forecasts
    try:
        integrated_data['forecasts'] = rbadata.rba_forecasts(all_or_latest="latest")
    except:
        pass
    
    # Get snapshots
    try:
        integrated_data['snapshots'] = rbadata.get_economic_indicators()
    except:
        pass
    
    # Add metadata
    integrated_data['metadata'] = {
        'download_time': datetime.now(),
        'data_sources': len([k for k in integrated_data.values() if k is not None]),
        'total_observations': sum(len(v) for v in integrated_data['rba_tables'].values())
    }
    
    print("Integrated data summary:")
    print(f"  Tables downloaded: {len(integrated_data['rba_tables'])}")
    print(f"  Total observations: {integrated_data['metadata']['total_observations']}")
    print(f"  Has forecasts: {integrated_data['forecasts'] is not None}")
    print(f"  Has snapshots: {integrated_data['snapshots'] is not None}")
    
    
    # Example 9: Performance optimization
    print("\n\n9. Performance optimization techniques")
    print("-" * 50)
    
    # Technique 1: Batch downloads
    print("Technique 1: Batch downloading")
    start_time = datetime.now()
    
    # Download multiple series at once
    series_list = ["GCPIAG", "GLFSURSA", "FIRMMCRT"]
    batch_data = rbadata.read_rba(series_id=series_list)
    
    batch_time = (datetime.now() - start_time).total_seconds()
    print(f"  Batch download time: {batch_time:.2f} seconds")
    print(f"  Total rows: {len(batch_data)}")
    
    # Technique 2: Caching
    print("\nTechnique 2: Data caching")
    # Create a simple cache
    data_cache = {}
    
    def cached_download(table_no):
        if table_no not in data_cache:
            data_cache[table_no] = rbadata.read_rba(table_no=table_no)
        return data_cache[table_no]
    
    # First call - downloads data
    start_time = datetime.now()
    data1 = cached_download("G1")
    first_call_time = (datetime.now() - start_time).total_seconds()
    
    # Second call - uses cache
    start_time = datetime.now()
    data2 = cached_download("G1")
    second_call_time = (datetime.now() - start_time).total_seconds()
    
    print(f"  First call: {first_call_time:.3f} seconds")
    print(f"  Cached call: {second_call_time:.3f} seconds")
    print(f"  Speedup: {first_call_time/max(second_call_time, 0.001):.0f}x")
    
    
    # Example 10: Export for external analysis
    print("\n\n10. Exporting data for external analysis")
    print("-" * 50)
    
    # Prepare data for export
    export_data = prepare_export_package()
    
    print("Export package prepared:")
    for format_name, details in export_data.items():
        print(f"  {format_name}: {details}")
    
    # Create analysis-ready dataset
    analysis_dataset = create_analysis_dataset()
    
    print("\nAnalysis dataset created:")
    print(f"  Shape: {analysis_dataset.shape}")
    print(f"  Features: {list(analysis_dataset.columns)}")
    print(f"  Date range: {analysis_dataset.index.min()} to {analysis_dataset.index.max()}")
    
    
    print("\n\nAdvanced usage examples completed!")
    print("=" * 50)


# Helper functions for advanced examples

def build_economic_dashboard():
    """Build a comprehensive economic dashboard dataset."""
    dashboard = {}
    
    try:
        # Key indicators
        dashboard['indicators'] = rbadata.get_economic_indicators()
        
        # Latest forecasts
        dashboard['forecasts'] = rbadata.rba_forecasts(all_or_latest="latest")
        
        # Recent data
        dashboard['cpi'] = rbadata.read_rba(series_id="GCPIAG").tail(4)
        dashboard['unemployment'] = rbadata.read_rba(series_id="GLFSURSA").tail(3)
        dashboard['cash_rate'] = rbadata.read_rba(series_id="FIRMMCRT").tail(1)
        
        # Metadata
        dashboard['last_updated'] = datetime.now()
        
    except Exception as e:
        print(f"Dashboard error: {e}")
    
    return dashboard


def perform_quality_checks(data):
    """Perform data quality checks on a DataFrame."""
    checks = {}
    
    # Check 1: Missing values
    missing_count = data.isnull().sum().sum()
    checks['missing_values'] = {
        'status': missing_count == 0,
        'details': f"{missing_count} missing values found"
    }
    
    # Check 2: Date continuity
    if 'date' in data.columns:
        date_diff = data['date'].diff()
        irregular_dates = date_diff[date_diff != date_diff.mode()[0]].count()
        checks['date_continuity'] = {
            'status': irregular_dates <= 1,  # Allow 1 irregularity
            'details': f"{irregular_dates} irregular date intervals"
        }
    
    # Check 3: Duplicate entries
    duplicates = data.duplicated().sum()
    checks['duplicates'] = {
        'status': duplicates == 0,
        'details': f"{duplicates} duplicate rows"
    }
    
    # Check 4: Value ranges
    if 'value' in data.columns:
        numeric_values = pd.to_numeric(data['value'], errors='coerce')
        outliers = ((numeric_values < numeric_values.quantile(0.01)) | 
                   (numeric_values > numeric_values.quantile(0.99))).sum()
        checks['outliers'] = {
            'status': outliers < len(data) * 0.05,  # Less than 5% outliers
            'details': f"{outliers} potential outliers"
        }
    
    return checks


def calculate_real_interest_rate(nominal_rate, inflation_rate):
    """Calculate real interest rate from nominal rate and inflation."""
    # Align the series
    combined = pd.DataFrame({
        'nominal': nominal_rate,
        'inflation': inflation_rate
    }).dropna()
    
    # Fisher equation approximation
    combined['real_rate'] = combined['nominal'] - combined['inflation']
    
    return combined['real_rate']


def identify_recessions(gdp_growth):
    """Identify recession periods from GDP growth data."""
    recessions = []
    in_recession = False
    start_date = None
    
    for date, growth in gdp_growth.items():
        if growth < 0 and not in_recession:
            in_recession = True
            start_date = date
        elif growth >= 0 and in_recession:
            in_recession = False
            if start_date:
                recessions.append((start_date, date))
    
    return recessions


def run_data_pipeline(config):
    """Run a custom data processing pipeline."""
    results = {}
    
    # Extract phase
    for source in config['sources']:
        try:
            if source['type'] == 'table':
                data = rbadata.read_rba(table_no=source['id'])
                if 'series' in source:
                    data = data[data['series_id'] == source['series']]
                results[source['id']] = data
            elif source['type'] == 'forecast':
                data = rbadata.rba_forecasts(all_or_latest="latest")
                if 'series' in source:
                    data = data[data['series'] == source['series']]
                results['forecast_' + source['series']] = data
        except Exception as e:
            print(f"    Pipeline error for {source}: {e}")
    
    # Transform phase would go here
    # Apply transformations as specified in config
    
    return results


def prepare_export_package():
    """Prepare data for export in multiple formats."""
    export_info = {
        'csv': 'Ready for Excel/R/Python analysis',
        'parquet': 'Efficient columnar format for big data',
        'json': 'Web API compatible format',
        'stata': 'For econometric analysis',
        'hdf5': 'For scientific computing'
    }
    
    # In practice, you would actually create these files
    # For example:
    # data.to_csv('rba_data.csv')
    # data.to_parquet('rba_data.parquet')
    # etc.
    
    return export_info


def create_analysis_dataset():
    """Create a dataset ready for econometric analysis."""
    # Create a mock dataset for demonstration
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='Q')
    
    dataset = pd.DataFrame({
        'gdp_growth': np.random.normal(2.5, 1.5, len(dates)),
        'inflation': np.random.normal(2.0, 0.5, len(dates)),
        'unemployment': np.random.normal(5.0, 0.5, len(dates)),
        'cash_rate': np.random.normal(1.5, 0.5, len(dates)),
        'aud_usd': np.random.normal(0.70, 0.05, len(dates))
    }, index=dates)
    
    # Add lagged variables
    dataset['gdp_growth_lag1'] = dataset['gdp_growth'].shift(1)
    dataset['inflation_lag1'] = dataset['inflation'].shift(1)
    
    # Add moving averages
    dataset['inflation_ma4'] = dataset['inflation'].rolling(4).mean()
    
    return dataset.dropna()


if __name__ == "__main__":
    main()