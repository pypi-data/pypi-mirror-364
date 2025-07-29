# rbadata

A Python package to download and tidy data from the Reserve Bank of Australia (RBA).

This package is a Python implementation inspired by the R package `readrba`, providing similar functionality for accessing RBA statistical tables and economic forecasts.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen)](https://github.com/caymandev/rbadata)
[![Tests](https://github.com/caymandev/rbadata/actions/workflows/tests.yml/badge.svg)](https://github.com/caymandev/rbadata/actions/workflows/tests.yml)

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [Examples](#examples)
- [Documentation](#documentation)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
pip install rbadata
```

For development installation:

```bash
git clone https://github.com/caymandev/rbadata.git
cd rbadata
pip install -e ".[dev]"
```

## Quick Start

```python
import rbadata

# Read a single RBA table
cpi_table = rbadata.read_rba(table_no="g1")

# Read multiple tables
data = rbadata.read_rba(table_no=["a1", "g1"])

# Read by series ID
cpi_series = rbadata.read_rba(series_id="GCPIAG")

# Get RBA forecasts
forecasts = rbadata.rba_forecasts()

# Browse available tables and series
tables = rbadata.browse_rba_tables()
series = rbadata.browse_rba_series("inflation")
```

## Advanced Usage

### Inflation Calculator

```python
# Calculate inflation-adjusted values
calc = rbadata.InflationCalculator()

# How much was $100 in 2000 worth in 2023?
value_2023 = calc.calculate_value(100, "2000", "2023")

# Calculate inflation rate
inflation_rate = calc.calculate_inflation_rate("2020", "2023")

# Quick calculation
adjusted_value = rbadata.inflation_calculator(1000, "2010", "2023")
```

### Chart Pack

```python
# Access RBA Chart Pack
chart_pack = rbadata.get_chart_pack()

# Get available categories
categories = chart_pack.get_categories()

# Get charts by category
inflation_charts = chart_pack.get_charts_by_category("inflation")

# Download the full Chart Pack PDF
chart_pack.download_chart_pack()
```

### Economic Snapshots

```python
# Get economic indicators snapshot
indicators = rbadata.get_economic_indicators()

# Access snapshots
snapshots = rbadata.get_snapshots()
snapshots.download_snapshot("economic-indicators")
```

### Glossary

```python
# Look up term definitions
definition = rbadata.define("CPI")

# Search for terms
glossary = rbadata.get_glossary()
inflation_terms = glossary.search("inflation")
```

## Features

### Core Features
- Download current and historical RBA statistical tables
- Access RBA economic forecasts since 1990
- Search and browse available data series
- Automatic data tidying into pandas DataFrames
- Robust error handling and retry logic

### Additional Features
- **Inflation Calculator**: Calculate inflation-adjusted values and inflation rates
- **Chart Pack Access**: Download and explore RBA Chart Pack data
- **Economic Snapshots**: Access key economic indicators and visualizations
- **Statistical Alerts**: Set up notifications for new data releases
- **Glossary**: Look up definitions of economic and financial terms

## Examples

The package includes comprehensive examples demonstrating all features:

1. **Basic Usage** - Core functionality and data reading
2. **Data Browsing** - Searching and discovering available data
3. **Forecasts** - Working with RBA economic forecasts
4. **Inflation Calculator** - Real-world inflation calculations
5. **Chart Pack** - Accessing visual economic summaries
6. **Snapshots** - Quick economic indicators
7. **Alerts** - Setting up data release notifications
8. **Glossary** - Economic terminology reference
9. **Advanced Usage** - Performance optimization and bulk operations
10. **Data Analysis** - Real-world economic analysis examples

See the [examples directory](examples/) for detailed code examples with inline documentation.

## Documentation

### Data Sources

- **Statistical Tables**: Access to all RBA statistical tables (current and historical)
- **Forecasts**: Public RBA forecasts since 1990 from Statement on Monetary Policy
- **Chart Pack**: Visual summaries released 8 times per year
- **Snapshots**: Key economic indicators, economy composition, and payment methods

### Common Use Cases

```python
# Monitor inflation
inflation = rbadata.read_rba(series_id="GCPIAG")
current_cpi = inflation.iloc[-1]['value']

# Track interest rates
cash_rate = rbadata.read_cashrate()
current_rate = cash_rate.iloc[-1]['value']

# Analyze employment
unemployment = rbadata.read_rba(series_id="GLFSURSA")

# Get latest economic forecasts
latest_forecasts = rbadata.rba_forecasts(all_or_latest="latest")
```

## Requirements

- Python 3.9+
- pandas >= 1.3.0
- requests >= 2.25.0
- beautifulsoup4 >= 4.9.0
- openpyxl >= 3.0.0

## Testing

The package includes comprehensive tests with high coverage. To run tests locally:

```bash
# Run tests
pytest tests/

# Run tests with coverage report
pytest tests/ --cov=rbadata --cov-report=term-missing

# Generate coverage badge locally
python scripts/generate_coverage_badge.py --update-readme
```

### Coverage

The project maintains high test coverage (currently 97%). Coverage is automatically tracked via GitHub Actions and reported using Codecov.

To set up Codecov for your fork:
1. Sign up at [codecov.io](https://codecov.io)
2. Add your repository
3. Add the `CODECOV_TOKEN` to your GitHub repository secrets

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

Before submitting:
1. Run the test suite and ensure all tests pass
2. Add tests for any new functionality
3. Ensure code coverage remains high
4. Run linting: `flake8 rbadata/`
5. Format code: `black rbadata/`

## License

MIT License

## Disclaimer

This package is not affiliated with or endorsed by the Reserve Bank of Australia. All data is provided subject to any conditions and restrictions set out on the RBA website.