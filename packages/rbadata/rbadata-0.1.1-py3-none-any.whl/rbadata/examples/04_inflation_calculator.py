"""
Inflation Calculator Examples
=============================

This example demonstrates how to:
- Calculate inflation-adjusted values
- Calculate inflation rates between periods
- Work with different date formats
- Analyze purchasing power changes
- Create custom inflation analyses
"""

import rbadata
import pandas as pd
from datetime import datetime

def main():
    """Main function demonstrating inflation calculator features."""
    
    print("rbadata Inflation Calculator Examples")
    print("=" * 50)
    
    # Example 1: Basic inflation calculation
    print("\n1. Basic inflation-adjusted value calculation")
    print("-" * 50)
    
    # Calculate what $100 in 2000 is worth in 2023
    original_amount = 100
    from_year = "2000"
    to_year = "2023"
    
    # Using the convenience function
    adjusted_value = rbadata.inflation_calculator(original_amount, from_year, to_year)
    
    print(f"${original_amount} in {from_year} is equivalent to ${adjusted_value:.2f} in {to_year}")
    print(f"That's an increase of {adjusted_value - original_amount:.2f} ({(adjusted_value/original_amount - 1)*100:.1f}%)")
    
    
    # Example 2: Using the InflationCalculator class
    print("\n\n2. Using the InflationCalculator class for multiple calculations")
    print("-" * 50)
    
    # Create calculator instance (loads CPI data once)
    calc = rbadata.InflationCalculator()
    
    # Calculate values for multiple amounts
    amounts = [100, 1000, 10000, 50000]
    print(f"Value of money from 2010 to 2023:")
    print("-" * 40)
    print("2010 Amount  |  2023 Equivalent  |  Change")
    print("-" * 40)
    
    for amount in amounts:
        value_2023 = calc.calculate_value(amount, "2010", "2023")
        change_pct = (value_2023/amount - 1) * 100
        print(f"${amount:>10,}  |  ${value_2023:>14,.2f}  |  {change_pct:>5.1f}%")
    
    
    # Example 3: Calculate inflation rates
    print("\n\n3. Calculating inflation rates")
    print("-" * 50)
    
    # Calculate inflation rate between two periods
    rate_total = calc.calculate_inflation_rate("2020", "2023", annualized=False)
    rate_annual = calc.calculate_inflation_rate("2020", "2023", annualized=True)
    
    print(f"Total inflation 2020-2023: {rate_total:.2f}%")
    print(f"Annualized inflation rate: {rate_annual:.2f}% per year")
    
    # Calculate inflation for different periods
    print("\nInflation rates for various periods:")
    periods = [
        ("2019", "2020", "Pre-pandemic year"),
        ("2020", "2021", "First pandemic year"),
        ("2021", "2022", "Recovery period"),
        ("2022", "2023", "Recent period"),
    ]
    
    for from_year, to_year, description in periods:
        rate = calc.calculate_inflation_rate(from_year, to_year, annualized=True)
        print(f"  {from_year}-{to_year} ({description}): {rate:.2f}%")
    
    
    # Example 4: Working with different date formats
    print("\n\n4. Using different date formats")
    print("-" * 50)
    
    # The calculator accepts various date formats
    date_examples = [
        ("2020", "2023", "Year only"),
        ("2020-Q1", "2023-Q1", "Quarter format"),
        ("2020-03-31", "2023-03-31", "Full date"),
    ]
    
    print("Calculating $1000 value with different date formats:")
    for from_date, to_date, format_desc in date_examples:
        value = calc.calculate_value(1000, from_date, to_date)
        print(f"  {format_desc}: {from_date} to {to_date} = ${value:.2f}")
    
    
    # Example 5: Historical purchasing power analysis
    print("\n\n5. Historical purchasing power analysis")
    print("-" * 50)
    
    # Analyze how purchasing power has changed over decades
    base_amount = 1000
    base_year = 1990
    
    print(f"Purchasing power of ${base_amount} from {base_year}:")
    print("-" * 50)
    print("Year  |  Equivalent Value  |  Cumulative Inflation")
    print("-" * 50)
    
    for year in range(1990, 2024, 5):
        if year == base_year:
            continue
        value = calc.calculate_value(base_amount, str(base_year), str(year))
        total_inflation = (value/base_amount - 1) * 100
        print(f"{year}  |  ${value:>15,.2f}  |  {total_inflation:>18.1f}%")
    
    
    # Example 6: Real wage analysis
    print("\n\n6. Real wage analysis")
    print("-" * 50)
    
    # Analyze if wages have kept up with inflation
    wage_2010 = 50000
    wage_2023 = 75000
    
    # What should the wage be to maintain purchasing power?
    required_wage_2023 = calc.calculate_value(wage_2010, "2010", "2023")
    
    print(f"Wage in 2010: ${wage_2010:,}")
    print(f"Wage in 2023: ${wage_2023:,}")
    print(f"Required wage to maintain 2010 purchasing power: ${required_wage_2023:,.2f}")
    
    if wage_2023 > required_wage_2023:
        gain = wage_2023 - required_wage_2023
        gain_pct = (wage_2023/required_wage_2023 - 1) * 100
        print(f"Real wage GAIN: ${gain:,.2f} ({gain_pct:.1f}% above inflation)")
    else:
        loss = required_wage_2023 - wage_2023
        loss_pct = (1 - wage_2023/required_wage_2023) * 100
        print(f"Real wage LOSS: ${loss:,.2f} ({loss_pct:.1f}% below inflation)")
    
    
    # Example 7: Cost of living comparison
    print("\n\n7. Cost of living comparison")
    print("-" * 50)
    
    # Compare costs across different time periods
    items = [
        ("House", 200000, "2000"),
        ("Car", 20000, "2005"),
        ("University degree", 15000, "1995"),
        ("Coffee", 3.50, "2015"),
    ]
    
    print("Cost comparison in today's dollars (2023):")
    print("-" * 60)
    print(f"{'Item':<20} {'Original Cost':<15} {'Year':<6} {'2023 Equivalent':<15}")
    print("-" * 60)
    
    for item, cost, year in items:
        current_value = calc.calculate_value(cost, year, "2023")
        print(f"{item:<20} ${cost:<14,.2f} {year:<6} ${current_value:<14,.2f}")
    
    
    # Example 8: Investment return vs inflation
    print("\n\n8. Investment returns vs inflation")
    print("-" * 50)
    
    # Compare investment returns with inflation
    investment_amount = 10000
    investment_year = "2015"
    current_year = "2023"
    
    # Calculate required value to beat inflation
    inflation_adjusted = calc.calculate_value(investment_amount, investment_year, current_year)
    
    # Example investment returns
    investment_scenarios = [
        ("Bank savings (2% p.a.)", investment_amount * (1.02 ** 8)),
        ("Bonds (4% p.a.)", investment_amount * (1.04 ** 8)),
        ("Stocks (8% p.a.)", investment_amount * (1.08 ** 8)),
        ("Property (10% p.a.)", investment_amount * (1.10 ** 8)),
    ]
    
    print(f"Initial investment: ${investment_amount:,} in {investment_year}")
    print(f"Value needed to maintain purchasing power in {current_year}: ${inflation_adjusted:,.2f}")
    print("\nInvestment outcomes:")
    
    for scenario, final_value in investment_scenarios:
        real_return = final_value - inflation_adjusted
        real_return_pct = (final_value/inflation_adjusted - 1) * 100
        
        print(f"\n{scenario}:")
        print(f"  Final value: ${final_value:,.2f}")
        if real_return > 0:
            print(f"  Real return: ${real_return:,.2f} ({real_return_pct:.1f}% above inflation)")
        else:
            print(f"  Real loss: ${-real_return:,.2f} ({-real_return_pct:.1f}% below inflation)")
    
    
    # Example 9: Get CPI data directly
    print("\n\n9. Accessing CPI data directly")
    print("-" * 50)
    
    # Get the underlying CPI series
    cpi_series = calc.get_cpi_series(start_date="2020", end_date="2023")
    
    print("Quarterly CPI values:")
    print(cpi_series.tail(8))
    
    # Calculate quarter-on-quarter changes
    qoq_changes = cpi_series.pct_change() * 100
    print("\nQuarter-on-quarter inflation (%):")
    print(qoq_changes.tail(8).round(2))
    
    
    print("\n\nInflation calculator examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()