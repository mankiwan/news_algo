"""
Strategy parameter optimization module for the news trading backtest system.

This module provides functionality to optimize trading strategy parameters:
- Window: Time period to calculate price percentage for position determination
- Threshold: Time period to hold position before calculating returns

The optimization tests various combinations to find the best performing parameters.
"""

import pandas as pd
import numpy as np
from itertools import product
from backtest import execute_backtest_strategy, filter_crypto_news, get_prices_at_timestamps, calculate_trading_returns
from performance import calculate_performance_metrics


def get_optimization_parameters():
    """Get optimization parameters from user input"""
    print("\n" + "="*60)
    print("STRATEGY PARAMETER OPTIMIZATION")
    print("="*60)
    print("Optimize window (signal) and threshold (exit) timing parameters.")
    print("\nCurrent defaults:")
    print("- Window: 1 minute (time to determine position)")
    print("- Threshold: 10 minutes (time to close position)")
    print("- Constraint: Threshold must be > Window")
    
    # Window parameter options - user can customize range (in minutes)
    print(f"\nWindow parameter range (signal timing):")
    print("Default: 0.5min to 20min in 1min steps (0.5, 1.5, 2.5, ..., 20)")
    
    use_custom = input("Use custom window range? (y/n): ").strip().lower()
    
    if use_custom in ['y', 'yes']:
        try:
            start = float(input("Start window (minutes): "))
            stop = float(input("Stop window (minutes): "))
            step = float(input("Step size (minutes): "))
            window_options = np.arange(start, stop + step, step).tolist()  # Keep in minutes
        except ValueError:
            print("Invalid input, using defaults")
            window_options = np.arange(0.5, 20.5, 1).tolist()  # 0.5min to 20min in 1min steps
    else:
        window_options = np.arange(0.5, 20.5, 1).tolist()  # 0.5min to 20min in 1min steps
    
    print(f"Window range: {len(window_options)} options from {window_options[0]:.1f}min to {window_options[-1]:.1f}min")
    
    # Get window selection
    use_all_windows = input(f"\nUse all {len(window_options)} window options? (y/n): ").strip().lower()
    
    if use_all_windows in ['y', 'yes', '']:
        selected_windows = window_options
    else:
        print("Enter specific window values (in minutes), separated by commas:")
        print(f"Available range: {window_options[0]:.1f} to {window_options[-1]:.1f}")
        try:
            user_windows = input("Windows (minutes): ").strip()
            selected_windows = [float(x.strip()) for x in user_windows.split(',')]
            # Validate that selected windows are in the available range
            selected_windows = [w for w in selected_windows if w in window_options]
            if not selected_windows:
                print("No valid windows selected, using all")
                selected_windows = window_options
        except ValueError:
            print("Invalid input, using all windows")
            selected_windows = window_options
    
    # Threshold parameter options - user can customize range (in minutes)
    print(f"\nThreshold parameter range (exit timing):")
    print("Default: 5min to 60min in 5min steps (5, 10, 15, ..., 60)")
    
    use_custom_threshold = input("Use custom threshold range? (y/n): ").strip().lower()
    
    if use_custom_threshold in ['y', 'yes']:
        try:
            start = float(input("Start threshold (minutes): "))
            stop = float(input("Stop threshold (minutes): "))
            step = float(input("Step size (minutes): "))
            threshold_options = np.arange(start, stop + step, step).tolist()  # Keep in minutes
        except ValueError:
            print("Invalid input, using defaults")
            threshold_options = np.arange(5, 65, 5).tolist()  # 5min to 60min in 5min steps
    else:
        threshold_options = np.arange(5, 65, 5).tolist()  # 5min to 60min in 5min steps
    
    print(f"Threshold range: {len(threshold_options)} options from {threshold_options[0]:.1f}min to {threshold_options[-1]:.1f}min")
    
    # Get threshold selection
    use_all_thresholds = input(f"\nUse all {len(threshold_options)} threshold options? (y/n): ").strip().lower()
    
    if use_all_thresholds in ['y', 'yes', '']:
        selected_thresholds = threshold_options
    else:
        print("Enter specific threshold values (in minutes), separated by commas:")
        print(f"Available range: {threshold_options[0]:.1f} to {threshold_options[-1]:.1f}")
        try:
            user_thresholds = input("Thresholds (minutes): ").strip()
            selected_thresholds = [float(x.strip()) for x in user_thresholds.split(',')]
            # Validate that selected thresholds are in the available range
            selected_thresholds = [t for t in selected_thresholds if t in threshold_options]
            if not selected_thresholds:
                print("No valid thresholds selected, using all")
                selected_thresholds = threshold_options
        except ValueError:
            print("Invalid input, using all thresholds")
            selected_thresholds = threshold_options
    
    # Filter valid combinations (threshold > window)
    valid_combinations = []
    for window, threshold in product(selected_windows, selected_thresholds):
        if threshold > window:
            valid_combinations.append((window, threshold))
    
    if not valid_combinations:
        print("No valid combinations found (threshold must be > window)")
        return None
        
    print(f"\nFound {len(valid_combinations)} valid parameter combinations to test.")
    
    # Optimization metric selection
    print(f"\nOptimization metrics:")
    metrics = [
        ("total_return", "Total Return"),
        ("sharpe_ratio", "Sharpe Ratio"), 
        ("calmar_ratio", "Calmar Ratio"),
        ("win_rate", "Win Rate"),
        ("profit_factor", "Profit Factor")
    ]
    
    for i, (_, name) in enumerate(metrics, 1):
        print(f"{i}. {name}")
    
    while True:
        try:
            choice = input(f"\nSelect optimization metric (1-{len(metrics)}): ").strip()
            metric_idx = int(choice) - 1
            if 0 <= metric_idx < len(metrics):
                optimization_metric = metrics[metric_idx][0]
                metric_name = metrics[metric_idx][1]
                break
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number")
    
    return {
        'combinations': valid_combinations,
        'optimization_metric': optimization_metric,
        'metric_name': metric_name
    }


def run_parameter_optimization_efficient(price_df, news_df, token_col, selected_crypto, trading_costs, optimization_params):
    """Run efficient parameter optimization with pre-processed data and modular functions"""
    
    combinations = optimization_params['combinations']
    optimization_metric = optimization_params['optimization_metric']
    metric_name = optimization_params['metric_name']
    
    print(f"\n" + "="*70)
    print(f"RUNNING VECTORIZED OPTIMIZATION - Optimizing for {metric_name}")
    print("="*70)
    print(f"Testing {len(combinations)} parameter combinations using vectorized operations...")
    
    try:
        # Pre-filter and prepare crypto news once
        crypto_news = filter_crypto_news(news_df, token_col, selected_crypto)
        
        if len(crypto_news) == 0:
            print(f"No valid {selected_crypto} news events found!")
            return None
        
        print(f"Processing {len(crypto_news)} {selected_crypto} news events...")
        
        # Sort price data once
        price_df_sorted = price_df.sort_values('unix_timestamp').copy()
        timestamps = crypto_news['unix_timestamp'].values
        
        # Vectorized optimization: process all combinations at once
        results = []
        
        for i, (window, threshold) in enumerate(combinations, 1):
            # window and threshold are now in minutes
            window_str = f"{window:.1f}min"
            threshold_str = f"{threshold:.1f}min"
            
            # Get prices for this parameter combination
            price_results = get_prices_at_timestamps(price_df_sorted, timestamps, window=window, threshold=threshold)
            
            # Merge with news data
            crypto_news_copy = crypto_news.reset_index(drop=True)
            crypto_news_copy = pd.concat([crypto_news_copy, price_results[['price_current', 'price_window', 'price_threshold']]], axis=1)
            
            # Remove rows with missing price data
            price_mask = crypto_news_copy[['price_current', 'price_window', 'price_threshold']].notna().all(axis=1)
            crypto_news_copy = crypto_news_copy[price_mask].copy()
            
            if len(crypto_news_copy) == 0:
                continue
            
            # Calculate returns using vectorized operations
            crypto_news_copy = calculate_trading_returns(crypto_news_copy, trading_costs)
            returns = crypto_news_copy['trade_return'].tolist()
            
            if returns and len(returns) > 0:
                # Calculate performance metrics
                metrics = calculate_performance_metrics(returns)
                metric_value = metrics.get(optimization_metric, 0)
                
                # Clean up token column
                crypto_news_copy['token'] = crypto_news_copy[token_col].astype(str).str.upper().str.strip()
                
                # Select relevant columns for results
                result_columns = [
                    'unix_timestamp', 'token', 'price_current', 'price_window', 'price_threshold',
                    'price_change_window', 'position', 'trade_return'
                ]
                results_df = crypto_news_copy[result_columns].copy()
                
                results.append({
                    'window': window,
                    'threshold': threshold,
                    'window_str': window_str,
                    'threshold_str': threshold_str,
                    'trades': len(returns),
                    'total_return': metrics.get('total_return', 0),
                    'annualized_return': metrics.get('annualized_return', 0),
                    'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                    'calmar_ratio': metrics.get('calmar_ratio', 0),
                    'max_drawdown': metrics.get('max_drawdown', 0),
                    'win_rate': metrics.get('win_rate', 0),
                    'profit_factor': metrics.get('profit_factor', 0),
                    'optimization_metric': metric_value,
                    'returns': returns,
                    'results_df': results_df
                })
                
                if i <= 5 or i % 10 == 0:  # Show progress for first 5 and every 10th
                    print(f"[{i}/{len(combinations)}] {window_str}/{threshold_str}: {len(returns)} trades, {metric_name}: {metric_value:.4f}")
        
        if not results:
            print("No successful optimization runs!")
            return None
        
        # Sort by optimization metric (descending for most metrics)
        reverse_sort = optimization_metric not in ['max_drawdown']
        results.sort(key=lambda x: x['optimization_metric'], reverse=reverse_sort)
        
        print(f"\n✅ Optimization completed! Found {len(results)} valid parameter combinations.")
        return results
        
    except Exception as e:
        print(f"Error in vectorized optimization: {e}")
        return None


def run_parameter_optimization(price_df, news_df, token_col, selected_crypto, trading_costs, optimization_params):
    """Main optimization function - uses vectorized approach for better performance"""
    
    # Use vectorized optimization for better performance
    results = run_parameter_optimization_efficient(price_df, news_df, token_col, selected_crypto, trading_costs, optimization_params)
    
    # Fallback to individual backtest calls if vectorized approach fails
    if results is None:
        print("Vectorized optimization failed, falling back to individual backtests...")
        results = run_parameter_optimization_fallback(price_df, news_df, token_col, selected_crypto, trading_costs, optimization_params)
    
    return results


def run_parameter_optimization_fallback(price_df, news_df, token_col, selected_crypto, trading_costs, optimization_params):
    """Fallback optimization using individual backtest calls"""
    
    combinations = optimization_params['combinations']
    optimization_metric = optimization_params['optimization_metric']
    metric_name = optimization_params['metric_name']
    
    print(f"Running fallback optimization for {len(combinations)} combinations...")
    
    results = []
    
    for i, (window, threshold) in enumerate(combinations, 1):
        # window and threshold are now in minutes
        window_str = f"{window:.1f}min"
        threshold_str = f"{threshold:.1f}min"
        
        try:
            # Use the unified backtest function with verbose=False for speed
            results_df, returns = execute_backtest_strategy(
                price_df, news_df, token_col, selected_crypto, 
                trading_costs, window, threshold, verbose=False
            )
            
            if returns and len(returns) > 0:
                metrics = calculate_performance_metrics(returns)
                metric_value = metrics.get(optimization_metric, 0)
                
                results.append({
                    'window': window,
                    'threshold': threshold,
                    'window_str': window_str,
                    'threshold_str': threshold_str,
                    'trades': len(returns),
                    'total_return': metrics.get('total_return', 0),
                    'annualized_return': metrics.get('annualized_return', 0),
                    'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                    'calmar_ratio': metrics.get('calmar_ratio', 0),
                    'max_drawdown': metrics.get('max_drawdown', 0),
                    'win_rate': metrics.get('win_rate', 0),
                    'profit_factor': metrics.get('profit_factor', 0),
                    'optimization_metric': metric_value,
                    'returns': returns,
                    'results_df': results_df
                })
                
                if i <= 5 or i % 5 == 0:
                    print(f"[{i}/{len(combinations)}] {window_str}/{threshold_str}: {metric_name}: {metric_value:.4f}")
                
        except Exception as e:
            print(f"Error testing {window_str}/{threshold_str}: {e}")
    
    if not results:
        return None
    
    # Sort by optimization metric
    reverse_sort = optimization_metric not in ['max_drawdown']
    results.sort(key=lambda x: x['optimization_metric'], reverse=reverse_sort)
    
    return results


def display_optimization_results(results, optimization_params):
    """Display optimization results in a formatted table"""
    
    if not results:
        print("No results to display!")
        return None
    
    metric_name = optimization_params['metric_name']
    
    print(f"\n" + "="*90)
    print(f"OPTIMIZATION RESULTS - Ranked by {metric_name}")
    print("="*90)
    
    # Print header
    header = f"{'Rank':<4} {'Window':<8} {'Threshold':<10} {'Trades':<6} {'Total Ret':<9} {'Sharpe':<7} {'Win Rate':<8} {metric_name:<12}"
    print(header)
    print("-" * 90)
    
    # Print top results
    for i, result in enumerate(results[:10], 1):  # Show top 10
        row = (f"{i:<4} {result['window_str']:<8} {result['threshold_str']:<10} "
               f"{result['trades']:<6} {result['total_return']:<9.4f} "
               f"{result['sharpe_ratio']:<7.3f} {result['win_rate']:<8.2%} "
               f"{result['optimization_metric']:<12.4f}")
        print(row)
    
    if len(results) > 10:
        print(f"\n... and {len(results) - 10} more combinations tested")
    
    # Highlight best result
    best = results[0]
    print(f"\n" + "="*50)
    print("BEST PARAMETERS")
    print("="*50)
    print(f"Window: {best['window_str']} ({best['window']}s)")
    print(f"Threshold: {best['threshold_str']} ({best['threshold']}s)")
    print(f"Trades: {best['trades']}")
    print(f"Total Return: {best['total_return']:.4f}")
    print(f"Annualized Return: {best['annualized_return']:.4f}")
    print(f"Sharpe Ratio: {best['sharpe_ratio']:.3f}")
    print(f"Win Rate: {best['win_rate']:.2%}")
    print(f"Max Drawdown: {best['max_drawdown']:.4f}")
    print(f"{metric_name}: {best['optimization_metric']:.4f}")
    
    return best


def save_optimization_results(results, optimization_params):
    """Save optimization results to CSV file"""
    
    if not results:
        return None
    
    # Create results directory
    import os
    from datetime import datetime
    os.makedirs("results", exist_ok=True)
    
    # Convert results to DataFrame
    results_data = []
    for result in results:
        results_data.append({
            'Window_Seconds': result['window'],
            'Threshold_Seconds': result['threshold'], 
            'Window_Display': result['window_str'],
            'Threshold_Display': result['threshold_str'],
            'Trades': result['trades'],
            'Total_Return': result['total_return'],
            'Annualized_Return': result['annualized_return'],
            'Sharpe_Ratio': result['sharpe_ratio'],
            'Calmar_Ratio': result['calmar_ratio'],
            'Max_Drawdown': result['max_drawdown'],
            'Win_Rate': result['win_rate'],
            'Profit_Factor': result['profit_factor'],
            'Optimization_Metric': result['optimization_metric']
        })
    
    results_df = pd.DataFrame(results_data)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metric_name = optimization_params['metric_name'].replace(' ', '_').lower()
    filename = f"results/optimization_{metric_name}_{timestamp}.csv"
    
    results_df.to_csv(filename, index=False)
    print(f"\nOptimization results saved to: {filename}")
    
    return filename


def get_backtest_mode_choice():
    """Get user choice between simple backtest and optimized backtest"""
    print("\n" + "="*50)
    print("BACKTEST MODE SELECTION")
    print("="*50)
    print("Choose your backtesting approach:")
    print("1. Simple Backtest (current default: 1min window, 10min threshold)")
    print("2. Optimized Backtest (test different window/threshold parameters)")
    
    while True:
        try:
            choice = input("\nSelect mode (1 or 2): ").strip()
            if choice == "1":
                return "simple"
            elif choice == "2":
                return "optimized"
            else:
                print("Invalid selection. Please enter 1 or 2.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None