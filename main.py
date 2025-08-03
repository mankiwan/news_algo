"""
Main execution script for cryptocurrency news trading backtest.

This script orchestrates the complete backtesting workflow:
1. Data loading (price and news data)
2. User input collection
3. Strategy execution
4. Performance analysis
5. Results visualization
"""

import os
from backtest import execute_backtest_strategy
from performance import (
    calculate_performance_metrics, 
    print_performance_report, 
    is_strategy_profitable
)
from plotting import generate_all_plots
from data_loader import (
    select_csv_file,
    select_excel_file, 
    load_price_data,
    load_excel_data,
    convert_to_unix_timestamp,
    select_cryptocurrency,
    get_column_mappings,
    save_results
)


def main():
    """Main function to orchestrate the backtesting process"""
    print("News Algorithm Trading Backtest")
    print("=" * 40)
    
    # Step 1: Select CSV file
    csv_file = select_csv_file()
    if csv_file is None:
        return
    
    # Step 2: Load price data
    price_df = load_price_data(csv_file)
    if price_df is None:
        return
    
    # Step 3: Select Excel file
    excel_file = select_excel_file()
    if excel_file is None:
        return
    
    # Step 4: Load news data  
    print(f"\nLoading news data from Excel file: {os.path.basename(excel_file)}")
    news_df = load_excel_data(excel_file)
    if news_df is None:
        return
    
    # Step 5: Select cryptocurrency
    selected_crypto = select_cryptocurrency()
    if selected_crypto is None:
        return
    
    # Step 6: Get column mappings
    date_col, time_col, token_col = get_column_mappings(news_df)
    if date_col is None or token_col is None:
        return
    
    print(f"Using date column: {date_col}")
    if time_col:
        print(f"Using time column: {time_col}")
    print(f"Using token column: {token_col}")
    print(f"Selected cryptocurrency: {selected_crypto}")
    
    # Step 7: Convert dates and times to unix timestamps
    print("\nConverting dates and times to unix timestamps...")
    time_series = news_df[time_col] if time_col else None
    news_df['unix_timestamp'] = convert_to_unix_timestamp(news_df[date_col], time_series)
    
    # Step 8: Execute backtest strategy
    print("\nExecuting backtest strategy...")
    results_df, returns = execute_backtest_strategy(price_df, news_df, token_col, selected_crypto)
    
    # Step 9: Calculate and display performance metrics
    if returns:
        metrics = calculate_performance_metrics(returns)
        print_performance_report(metrics)
        
        # Assess strategy profitability
        _, assessment = is_strategy_profitable(metrics)
        print(f"\n{assessment}")
        
        # Add metrics to results
        for key, value in metrics.items():
            results_df.attrs[key] = value
    else:
        print("\nNo valid trades found!")
    
    # Step 10: Save results
    save_results(results_df)
    
    # Step 11: Generate plots
    if not results_df.empty:
        plot_choice = input("\nGenerate visualization plots? (y/n): ").strip().lower()
        if plot_choice in ['y', 'yes']:
            try:
                generate_all_plots(results_df, metrics if returns else None)
            except Exception as e:
                print(f"Error generating plots: {e}")
                print("Make sure matplotlib and seaborn are installed: pip install matplotlib seaborn")
    
    return results_df


if __name__ == "__main__":
    results = main()