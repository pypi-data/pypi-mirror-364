"""
Real-World Data Analysis Examples with rbadata
=============================================

This example demonstrates practical economic analysis:
- Monetary policy analysis
- Inflation dynamics
- Labour market trends
- Financial conditions assessment
- Economic forecasting evaluation
- Cross-country comparisons
"""

import rbadata
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Optional visualization
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_style("whitegrid")
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

def main():
    """Main function demonstrating real-world data analysis."""
    
    print("rbadata Real-World Data Analysis Examples")
    print("=" * 50)
    
    # Example 1: Monetary Policy Analysis
    print("\n1. Monetary Policy Analysis")
    print("-" * 50)
    
    monetary_analysis = analyze_monetary_policy()
    
    print("Monetary Policy Summary:")
    for key, value in monetary_analysis.items():
        print(f"  {key}: {value}")
    
    
    # Example 2: Inflation Dynamics
    print("\n\n2. Analyzing Inflation Dynamics")
    print("-" * 50)
    
    inflation_analysis = analyze_inflation_dynamics()
    
    print("Inflation Analysis Results:")
    print(f"  Current inflation: {inflation_analysis['current_rate']:.2f}%")
    print(f"  Average (last 5 years): {inflation_analysis['five_year_avg']:.2f}%")
    print(f"  Volatility: {inflation_analysis['volatility']:.2f}")
    print(f"  Above target periods: {inflation_analysis['above_target_pct']:.1f}%")
    
    
    # Example 3: Labour Market Analysis
    print("\n\n3. Labour Market Trends")
    print("-" * 50)
    
    labour_analysis = analyze_labour_market()
    
    if labour_analysis:
        print("Labour Market Indicators:")
        print(f"  Current unemployment: {labour_analysis['current_unemployment']:.1f}%")
        print(f"  12-month change: {labour_analysis['year_change']:+.1f} pp")
        print(f"  Trend: {labour_analysis['trend']}")
        print(f"  NAIRU estimate: {labour_analysis['nairu_estimate']:.1f}%")
    
    
    # Example 4: Financial Conditions Index
    print("\n\n4. Financial Conditions Assessment")
    print("-" * 50)
    
    fci = calculate_financial_conditions_index()
    
    if fci is not None:
        print("Financial Conditions Index (FCI):")
        print(f"  Current FCI: {fci['current_fci']:.2f}")
        print(f"  Interpretation: {fci['interpretation']}")
        print("\nComponents:")
        for component, value in fci['components'].items():
            print(f"    {component}: {value:.2f}")
    
    
    # Example 5: Taylor Rule Analysis
    print("\n\n5. Taylor Rule Analysis")
    print("-" * 50)
    
    taylor_analysis = analyze_taylor_rule()
    
    if taylor_analysis:
        print("Taylor Rule Results:")
        print(f"  Actual cash rate: {taylor_analysis['actual_rate']:.2f}%")
        print(f"  Taylor rule rate: {taylor_analysis['taylor_rate']:.2f}%")
        print(f"  Deviation: {taylor_analysis['deviation']:+.2f} pp")
        print(f"  Policy stance: {taylor_analysis['stance']}")
    
    
    # Example 6: Economic Forecast Evaluation
    print("\n\n6. Forecast Accuracy Assessment")
    print("-" * 50)
    
    forecast_eval = evaluate_forecast_accuracy()
    
    if forecast_eval:
        print("Forecast Evaluation (1-year ahead):")
        for variable, metrics in forecast_eval.items():
            print(f"\n{variable}:")
            print(f"  Mean Error: {metrics['mean_error']:+.2f}")
            print(f"  Mean Absolute Error: {metrics['mae']:.2f}")
            print(f"  Hit rate: {metrics['hit_rate']:.1f}%")
    
    
    # Example 7: Economic Cycle Dating
    print("\n\n7. Economic Cycle Analysis")
    print("-" * 50)
    
    cycle_analysis = analyze_economic_cycles()
    
    if cycle_analysis:
        print("Economic Cycle Analysis:")
        print(f"  Current phase: {cycle_analysis['current_phase']}")
        print(f"  Phase duration: {cycle_analysis['phase_duration']} quarters")
        print(f"  Output gap estimate: {cycle_analysis['output_gap']:+.1f}%")
        
        if cycle_analysis['turning_points']:
            print("\nRecent turning points:")
            for point in cycle_analysis['turning_points'][-3:]:
                print(f"    {point['date']}: {point['type']}")
    
    
    # Example 8: Cross-Variable Relationships
    print("\n\n8. Economic Relationships Analysis")
    print("-" * 50)
    
    relationships = analyze_economic_relationships()
    
    if relationships:
        print("Key Economic Relationships:")
        for relationship, results in relationships.items():
            print(f"\n{relationship}:")
            print(f"  Correlation: {results['correlation']:.3f}")
            print(f"  Lead/lag: {results['optimal_lag']} quarters")
            print(f"  Relationship: {results['interpretation']}")
    
    
    # Example 9: Policy Rate Decomposition
    print("\n\n9. Policy Rate Decomposition")
    print("-" * 50)
    
    rate_decomposition = decompose_policy_rate()
    
    if rate_decomposition:
        print("Cash Rate Decomposition:")
        print(f"  Current rate: {rate_decomposition['current_rate']:.2f}%")
        print("\nContributions:")
        for factor, contribution in rate_decomposition['contributions'].items():
            print(f"    {factor}: {contribution:+.2f} pp")
        print(f"\n  Neutral rate estimate: {rate_decomposition['neutral_rate']:.2f}%")
    
    
    # Example 10: Economic Dashboard
    print("\n\n10. Economic Dashboard Summary")
    print("-" * 50)
    
    dashboard = create_economic_dashboard_summary()
    
    print("RBA Economic Dashboard")
    print("=" * 60)
    
    # Current conditions
    print("\nCurrent Conditions:")
    for indicator, value in dashboard['current_conditions'].items():
        print(f"  {indicator}: {value}")
    
    # Outlook
    print("\nEconomic Outlook:")
    for metric, forecast in dashboard['outlook'].items():
        print(f"  {metric}: {forecast}")
    
    # Risks
    print("\nKey Risks:")
    for i, risk in enumerate(dashboard['risks'], 1):
        print(f"  {i}. {risk}")
    
    
    print("\n\nReal-world data analysis examples completed!")
    print("=" * 50)


# Analysis functions

def analyze_monetary_policy():
    """Analyze current monetary policy stance."""
    try:
        # Get cash rate
        cash_rate = rbadata.read_rba(series_id="FIRMMCRT")
        current_rate = cash_rate.iloc[-1]['value']
        
        # Get inflation
        inflation = rbadata.read_rba(series_id="GCPIAGSAQP")
        current_inflation = inflation.iloc[-1]['value']
        
        # Calculate real rate
        real_rate = current_rate - current_inflation
        
        # Determine stance
        if real_rate > 2:
            stance = "Restrictive"
        elif real_rate > 0:
            stance = "Moderately tight"
        elif real_rate > -1:
            stance = "Neutral"
        else:
            stance = "Accommodative"
        
        # Recent changes
        rate_3m_ago = cash_rate.iloc[-3]['value'] if len(cash_rate) > 3 else current_rate
        recent_change = current_rate - rate_3m_ago
        
        return {
            'current_rate': f"{current_rate:.2f}%",
            'real_rate': f"{real_rate:.2f}%",
            'stance': stance,
            'recent_change': f"{recent_change:+.2f} pp",
            'current_inflation': f"{current_inflation:.2f}%"
        }
        
    except Exception as e:
        print(f"Error in monetary analysis: {e}")
        return {}


def analyze_inflation_dynamics():
    """Analyze inflation trends and dynamics."""
    try:
        # Get CPI data
        cpi = rbadata.read_rba(series_id="GCPIAGSAQP")
        cpi_ts = cpi.set_index('date')['value']
        
        # Current rate
        current_rate = cpi_ts.iloc[-1]
        
        # Historical analysis
        five_years_ago = pd.Timestamp.now() - pd.DateOffset(years=5)
        recent_cpi = cpi_ts[cpi_ts.index >= five_years_ago]
        
        # Calculate metrics
        five_year_avg = recent_cpi.mean()
        volatility = recent_cpi.std()
        
        # Target analysis (RBA target: 2-3%)
        above_target = (recent_cpi > 3).sum()
        below_target = (recent_cpi < 2).sum()
        in_target = (recent_cpi >= 2) & (recent_cpi <= 3)
        
        above_target_pct = (above_target / len(recent_cpi)) * 100
        
        # Momentum
        three_month_change = cpi_ts.iloc[-1] - cpi_ts.iloc[-3] if len(cpi_ts) > 3 else 0
        
        return {
            'current_rate': current_rate,
            'five_year_avg': five_year_avg,
            'volatility': volatility,
            'above_target_pct': above_target_pct,
            'three_month_momentum': three_month_change,
            'in_target_pct': (in_target.sum() / len(recent_cpi)) * 100
        }
        
    except Exception as e:
        print(f"Error in inflation analysis: {e}")
        return {}


def analyze_labour_market():
    """Analyze labour market conditions."""
    try:
        # Get unemployment rate
        unemployment = rbadata.read_rba(series_id="GLFSURSA")
        unemp_ts = unemployment.set_index('date')['value']
        
        # Current conditions
        current_unemployment = unemp_ts.iloc[-1]
        year_ago = unemp_ts.iloc[-12] if len(unemp_ts) > 12 else current_unemployment
        year_change = current_unemployment - year_ago
        
        # Trend analysis
        recent_trend = unemp_ts.iloc[-6:].diff().mean()
        if recent_trend < -0.1:
            trend = "Improving"
        elif recent_trend > 0.1:
            trend = "Deteriorating"
        else:
            trend = "Stable"
        
        # NAIRU estimate (simplified)
        # In practice, this would use more sophisticated methods
        long_term_avg = unemp_ts.mean()
        nairu_estimate = long_term_avg
        
        # Slack assessment
        if current_unemployment > nairu_estimate + 0.5:
            slack = "Significant slack"
        elif current_unemployment > nairu_estimate:
            slack = "Some slack"
        elif current_unemployment < nairu_estimate - 0.5:
            slack = "Tight conditions"
        else:
            slack = "Near equilibrium"
        
        return {
            'current_unemployment': current_unemployment,
            'year_change': year_change,
            'trend': trend,
            'nairu_estimate': nairu_estimate,
            'slack_assessment': slack
        }
        
    except Exception as e:
        print(f"Error in labour market analysis: {e}")
        return None


def calculate_financial_conditions_index():
    """Calculate a simple Financial Conditions Index."""
    try:
        components = {}
        weights = {
            'cash_rate': -0.3,
            'exchange_rate': -0.2,
            'credit_spread': -0.3,
            'equity_market': 0.2
        }
        
        # Cash rate (normalized)
        cash_rate = rbadata.read_rba(series_id="FIRMMCRT")
        current_cash = cash_rate.iloc[-1]['value']
        historical_avg = cash_rate['value'].mean()
        components['cash_rate'] = (current_cash - historical_avg) / cash_rate['value'].std()
        
        # Exchange rate (TWI - simplified proxy)
        # Higher TWI = stronger AUD = tighter conditions
        try:
            twi = rbadata.read_rba(series_id="FXRTWI")
            current_twi = twi.iloc[-1]['value']
            twi_avg = twi['value'].mean()
            components['exchange_rate'] = (current_twi - twi_avg) / twi['value'].std()
        except:
            components['exchange_rate'] = 0
        
        # Credit spread (simplified - using mortgage rate differential)
        components['credit_spread'] = 0  # Placeholder
        
        # Equity market (simplified)
        components['equity_market'] = 0.5  # Placeholder for positive conditions
        
        # Calculate FCI
        fci = sum(components[k] * weights[k] for k in components)
        
        # Interpretation
        if fci < -1:
            interpretation = "Very tight"
        elif fci < -0.5:
            interpretation = "Tight"
        elif fci < 0.5:
            interpretation = "Neutral"
        elif fci < 1:
            interpretation = "Accommodative"
        else:
            interpretation = "Very accommodative"
        
        return {
            'current_fci': fci,
            'interpretation': interpretation,
            'components': components
        }
        
    except Exception as e:
        print(f"Error calculating FCI: {e}")
        return None


def analyze_taylor_rule():
    """Analyze monetary policy using Taylor Rule."""
    try:
        # Get required data
        cash_rate = rbadata.read_rba(series_id="FIRMMCRT")
        inflation = rbadata.read_rba(series_id="GCPIAGSAQP")
        
        # Current values
        actual_rate = cash_rate.iloc[-1]['value']
        current_inflation = inflation.iloc[-1]['value']
        
        # Taylor rule parameters
        neutral_real_rate = 1.0  # Assumption
        inflation_target = 2.5   # RBA target midpoint
        inflation_weight = 1.5
        output_gap_weight = 0.5
        output_gap = 0  # Simplified - assume zero
        
        # Calculate Taylor rule rate
        taylor_rate = (
            neutral_real_rate + 
            current_inflation + 
            inflation_weight * (current_inflation - inflation_target) +
            output_gap_weight * output_gap
        )
        
        # Compare with actual
        deviation = actual_rate - taylor_rate
        
        # Interpret stance
        if deviation > 1:
            stance = "Much tighter than Taylor rule"
        elif deviation > 0.5:
            stance = "Tighter than Taylor rule"
        elif deviation > -0.5:
            stance = "Consistent with Taylor rule"
        elif deviation > -1:
            stance = "Looser than Taylor rule"
        else:
            stance = "Much looser than Taylor rule"
        
        return {
            'actual_rate': actual_rate,
            'taylor_rate': taylor_rate,
            'deviation': deviation,
            'stance': stance
        }
        
    except Exception as e:
        print(f"Error in Taylor rule analysis: {e}")
        return None


def evaluate_forecast_accuracy():
    """Evaluate RBA forecast accuracy."""
    try:
        # Get historical forecasts
        all_forecasts = rbadata.rba_forecasts()
        
        # Focus on 1-year ahead forecasts
        forecasts = all_forecasts.copy()
        forecasts['horizon_days'] = (forecasts['date'] - forecasts['forecast_date']).dt.days
        one_year = forecasts[(forecasts['horizon_days'] > 300) & (forecasts['horizon_days'] < 400)]
        
        # Get actual data for comparison
        actual_data = {
            'gdp_change': rbadata.read_rba(series_id="GGDPECCPGDP"),
            'cpi_annual': rbadata.read_rba(series_id="GCPIAGSAQP"),
            'unemp_rate': rbadata.read_rba(series_id="GLFSURSA")
        }
        
        results = {}
        
        for variable in ['gdp_change', 'cpi_annual', 'unemp_rate']:
            var_forecasts = one_year[one_year['series'] == variable]
            
            if var_forecasts.empty or variable not in actual_data:
                continue
            
            # Simple accuracy metrics
            errors = []
            for _, forecast in var_forecasts.iterrows():
                # Find matching actual
                actual = actual_data[variable]
                matching = actual[actual['date'] == forecast['date']]
                
                if not matching.empty:
                    error = forecast['value'] - matching.iloc[0]['value']
                    errors.append(error)
            
            if errors:
                results[variable] = {
                    'mean_error': np.mean(errors),
                    'mae': np.mean(np.abs(errors)),
                    'rmse': np.sqrt(np.mean(np.square(errors))),
                    'hit_rate': sum(1 for e in errors if abs(e) < 0.5) / len(errors) * 100
                }
        
        return results
        
    except Exception as e:
        print(f"Error in forecast evaluation: {e}")
        return None


def analyze_economic_cycles():
    """Analyze economic cycles and output gap."""
    try:
        # Get GDP growth
        gdp = rbadata.read_rba(series_id="GGDPECCPGDP")
        gdp_ts = gdp.set_index('date')['value']
        
        # Simple cycle identification
        # Moving average for trend
        trend = gdp_ts.rolling(window=8, center=True).mean()
        cycle = gdp_ts - trend
        
        # Current phase
        recent_growth = gdp_ts.iloc[-4:].mean()
        if recent_growth > 3:
            current_phase = "Expansion"
        elif recent_growth > 2:
            current_phase = "Moderate growth"
        elif recent_growth > 0:
            current_phase = "Slowdown"
        else:
            current_phase = "Contraction"
        
        # Phase duration
        phase_changes = (gdp_ts > gdp_ts.shift(1)).astype(int).diff()
        last_change_idx = phase_changes[phase_changes != 0].index[-1] if any(phase_changes != 0) else gdp_ts.index[0]
        phase_duration = len(gdp_ts[gdp_ts.index > last_change_idx])
        
        # Output gap (simplified)
        potential_growth = 2.5  # Assumption
        output_gap = recent_growth - potential_growth
        
        # Turning points (simplified)
        turning_points = []
        for i in range(2, len(gdp_ts) - 2):
            if gdp_ts.iloc[i] > gdp_ts.iloc[i-1] and gdp_ts.iloc[i] > gdp_ts.iloc[i+1]:
                turning_points.append({
                    'date': gdp_ts.index[i].strftime('%Y-%m'),
                    'type': 'Peak'
                })
            elif gdp_ts.iloc[i] < gdp_ts.iloc[i-1] and gdp_ts.iloc[i] < gdp_ts.iloc[i+1]:
                turning_points.append({
                    'date': gdp_ts.index[i].strftime('%Y-%m'),
                    'type': 'Trough'
                })
        
        return {
            'current_phase': current_phase,
            'phase_duration': phase_duration,
            'output_gap': output_gap,
            'recent_growth': recent_growth,
            'turning_points': turning_points
        }
        
    except Exception as e:
        print(f"Error in cycle analysis: {e}")
        return None


def analyze_economic_relationships():
    """Analyze relationships between key variables."""
    try:
        # Get key series
        series_data = {
            'cash_rate': rbadata.read_rba(series_id="FIRMMCRT"),
            'inflation': rbadata.read_rba(series_id="GCPIAGSAQP"),
            'unemployment': rbadata.read_rba(series_id="GLFSURSA"),
        }
        
        # Convert to aligned time series
        aligned = pd.DataFrame()
        for name, data in series_data.items():
            ts = data.set_index('date')['value']
            aligned[name] = ts
        
        aligned = aligned.dropna()
        
        relationships = {}
        
        # Phillips Curve: Unemployment vs Inflation
        if 'unemployment' in aligned.columns and 'inflation' in aligned.columns:
            corr = aligned['unemployment'].corr(aligned['inflation'])
            
            # Check different lags
            correlations = {}
            for lag in range(-4, 5):
                if lag < 0:
                    corr_lag = aligned['unemployment'].iloc[:lag].corr(
                        aligned['inflation'].iloc[-lag:]
                    )
                elif lag > 0:
                    corr_lag = aligned['unemployment'].iloc[lag:].corr(
                        aligned['inflation'].iloc[:-lag]
                    )
                else:
                    corr_lag = corr
                correlations[lag] = corr_lag
            
            optimal_lag = max(correlations, key=lambda k: abs(correlations[k]))
            
            relationships['Phillips Curve'] = {
                'correlation': corr,
                'optimal_lag': optimal_lag,
                'interpretation': 'Negative relationship' if corr < 0 else 'Positive relationship'
            }
        
        # Taylor Rule: Cash rate vs Inflation
        if 'cash_rate' in aligned.columns and 'inflation' in aligned.columns:
            corr = aligned['cash_rate'].corr(aligned['inflation'])
            
            relationships['Policy Response'] = {
                'correlation': corr,
                'optimal_lag': 0,
                'interpretation': 'Strong positive' if corr > 0.7 else 'Moderate positive' if corr > 0.3 else 'Weak'
            }
        
        return relationships
        
    except Exception as e:
        print(f"Error in relationship analysis: {e}")
        return None


def decompose_policy_rate():
    """Decompose policy rate into contributing factors."""
    try:
        # Get data
        cash_rate = rbadata.read_rba(series_id="FIRMMCRT")
        inflation = rbadata.read_rba(series_id="GCPIAGSAQP")
        
        current_rate = cash_rate.iloc[-1]['value']
        current_inflation = inflation.iloc[-1]['value']
        
        # Simple decomposition
        neutral_real_rate = 1.0
        inflation_target = 2.5
        
        contributions = {
            'Neutral real rate': neutral_real_rate,
            'Expected inflation': inflation_target,
            'Inflation gap': (current_inflation - inflation_target) * 1.5,
            'Output gap': 0,  # Simplified
            'Risk premium': 0.5
        }
        
        # Ensure decomposition adds up
        implied_rate = sum(contributions.values())
        residual = current_rate - implied_rate
        contributions['Other factors'] = residual
        
        return {
            'current_rate': current_rate,
            'neutral_rate': neutral_real_rate + inflation_target,
            'contributions': contributions
        }
        
    except Exception as e:
        print(f"Error in rate decomposition: {e}")
        return None


def create_economic_dashboard_summary():
    """Create a comprehensive economic dashboard."""
    dashboard = {
        'current_conditions': {},
        'outlook': {},
        'risks': []
    }
    
    try:
        # Current conditions
        indicators = rbadata.get_economic_indicators()
        key_indicators = ['GDP Growth', 'Unemployment Rate', 'CPI Inflation', 'Cash Rate']
        
        for indicator in key_indicators:
            matching = indicators[indicators['indicator'] == indicator]
            if not matching.empty:
                value = matching.iloc[0]['value']
                unit = matching.iloc[0]['unit']
                dashboard['current_conditions'][indicator] = f"{value} {unit}"
        
        # Outlook
        latest_forecasts = rbadata.rba_forecasts(all_or_latest="latest")
        
        # Get 1-year ahead forecasts
        one_year_ahead = pd.Timestamp.now() + pd.DateOffset(years=1)
        future_forecasts = latest_forecasts[
            (latest_forecasts['date'] >= one_year_ahead - pd.DateOffset(months=3)) &
            (latest_forecasts['date'] <= one_year_ahead + pd.DateOffset(months=3))
        ]
        
        for series in ['gdp_change', 'cpi_annual', 'unemp_rate']:
            series_forecast = future_forecasts[future_forecasts['series'] == series]
            if not series_forecast.empty:
                value = series_forecast.iloc[0]['value']
                desc = series_forecast.iloc[0]['series_desc']
                dashboard['outlook'][desc] = f"{value:.1f}%"
        
        # Risks
        # Simplified risk assessment based on current conditions
        cash_rate_data = rbadata.read_rba(series_id="FIRMMCRT")
        current_cash_rate = cash_rate_data.iloc[-1]['value']
        
        if current_cash_rate > 4:
            dashboard['risks'].append("Elevated interest rates may constrain growth")
        
        inflation_data = rbadata.read_rba(series_id="GCPIAGSAQP")
        current_inflation = inflation_data.iloc[-1]['value']
        
        if current_inflation > 3:
            dashboard['risks'].append("Inflation remains above target band")
        elif current_inflation < 2:
            dashboard['risks'].append("Inflation below target may signal weak demand")
        
        dashboard['risks'].append("Global economic uncertainty")
        dashboard['risks'].append("Geopolitical tensions")
        
    except Exception as e:
        print(f"Error creating dashboard: {e}")
    
    return dashboard


if __name__ == "__main__":
    main()