import os
import glob
import pandas as pd
from datetime import datetime
from backtest import execute_backtest_strategy
from performance import (
    calculate_performance_metrics, 
    print_performance_report, 
    is_strategy_profitable
)
from plotting import generate_all_plots

def select_csv_file():
    """Prompt user to select a CSV file from downloads folder"""
    downloads_dir = "downloads"
    
    if not os.path.exists(downloads_dir):
        print(f"Downloads folder '{downloads_dir}' not found!")
        return None
    
    csv_files = glob.glob(os.path.join(downloads_dir, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in '{downloads_dir}' folder!")
        return None
    
    print(f"\nAvailable CSV files in {downloads_dir}:")
    for i, file in enumerate(csv_files, 1):
        print(f"{i}. {os.path.basename(file)}")
    
    while True:
        try:
            choice = input(f"\nSelect a file (1-{len(csv_files)}): ").strip()
            file_idx = int(choice) - 1
            if 0 <= file_idx < len(csv_files):
                return csv_files[file_idx]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def load_price_data(csv_file_path):
    """Load price data from selected CSV file"""
    if not csv_file_path or not os.path.exists(csv_file_path):
        print(f"CSV file not found: {csv_file_path}")
        return None
    
    print(f"Loading price data from: {csv_file_path}")
    
    try:
        df = pd.read_csv(csv_file_path)
        df['open_time'] = pd.to_datetime(df['open_time'])
        df['unix_timestamp'] = df['open_time'].astype(int) // 10**9
        return df
    except Exception as e:
        print(f"Error loading price data: {e}")
        return None

def load_excel_data(filepath):
    """Load and examine Excel file structure"""
    try:
        # Try to read the Excel file
        df = pd.read_excel(filepath)
        print(f"Excel file loaded successfully!")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst few rows:")
        print(df.head())
        return df
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return None

def convert_to_unix_timestamp(date_series, time_series=None):
    """Convert date and time columns to unix timestamp using vectorized operations"""
    
    # Convert to pandas Series if not already
    if not isinstance(date_series, pd.Series):
        date_series = pd.Series(date_series)
    
    # Try to convert date_series to datetime using pandas built-in inference
    try:
        # Use pandas to_datetime without deprecated parameter
        date_dt = pd.to_datetime(date_series, errors='coerce')
    except:
        # Fallback to manual format detection for first few values
        date_formats = [
            "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y %H:%M:%S", 
            "%m/%d/%Y", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"
        ]
        
        date_dt = None
        for fmt in date_formats:
            try:
                date_dt = pd.to_datetime(date_series, format=fmt, errors='coerce')
                if date_dt.notna().sum() > 0:
                    break
            except:
                continue
        
        if date_dt is None:
            date_dt = pd.to_datetime(date_series, errors='coerce')
    
    # Handle time series if provided
    if time_series is not None and not time_series.empty:
        if not isinstance(time_series, pd.Series):
            time_series = pd.Series(time_series)
        
        # Try to parse time series
        time_formats = ["%H:%M:%S", "%H:%M", "%I:%M:%S %p", "%I:%M %p"]
        time_dt = None
        
        for fmt in time_formats:
            try:
                # Create full datetime strings by combining date and time
                valid_dates = date_dt.notna()
                if valid_dates.any():
                    combined_strings = date_dt.dt.strftime('%Y-%m-%d') + ' ' + time_series.astype(str)
                    # Try with specific format first to avoid warnings
                    try:
                        full_format = f"%Y-%m-%d {fmt}"
                        time_dt = pd.to_datetime(combined_strings, format=full_format, errors='coerce')
                    except:
                        # Fallback to general parsing with UTC
                        time_dt = pd.to_datetime(combined_strings, errors='coerce', utc=True)
                        if time_dt.notna().any():
                            # Convert back to local time for consistency
                            time_dt = time_dt.dt.tz_localize(None)
                    
                    if time_dt.notna().sum() > 0:
                        break
            except:
                continue
        
        # If time parsing succeeded, use combined datetime; otherwise use date only
        if time_dt is not None and time_dt.notna().sum() > 0:
            # Use time_dt where available, fall back to date_dt
            final_dt = time_dt.fillna(date_dt)
        else:
            final_dt = date_dt
    else:
        final_dt = date_dt
    
    # Convert to unix timestamps using vectorized operations
    # Convert datetime to unix timestamp (seconds since epoch)
    unix_timestamps = (final_dt - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
    
    # Handle NaT values by replacing with None
    unix_timestamps = unix_timestamps.where(final_dt.notna(), None)
    
    return unix_timestamps.tolist()

def select_excel_file():
    """Prompt user to select an Excel file"""
    news_dir = "news"
    excel_files = glob.glob(os.path.join(news_dir, "*.xlsx")) + glob.glob(os.path.join(news_dir, "*.xls"))
    if not excel_files:
        print(f"No Excel files found in '{news_dir}' directory!")
        return None
    
    if len(excel_files) == 1:
        return excel_files[0]
    
    print(f"\nAvailable Excel files in {news_dir}:")
    for i, file in enumerate(excel_files, 1):
        print(f"{i}. {os.path.basename(file)}")
    
    while True:
        try:
            choice = input(f"\nSelect Excel file (1-{len(excel_files)}): ").strip()
            file_idx = int(choice) - 1
            if 0 <= file_idx < len(excel_files):
                return excel_files[file_idx]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def get_column_mappings(news_df):
    """Get column mappings from user"""
    print("\nPlease identify the key columns:")
    for i, col in enumerate(news_df.columns, 1):
        print(f"{i}. {col}")
    
    # Get column mappings from user
    date_col_idx = input("\nEnter number for DATE column: ").strip()
    time_col_idx = input("Enter number for TIME column (or press Enter if no separate time column): ").strip()
    token_col_idx = input("Enter number for TOKEN column: ").strip()
    
    try:
        date_col = news_df.columns[int(date_col_idx) - 1]
        time_col = news_df.columns[int(time_col_idx) - 1] if time_col_idx else None
        token_col = news_df.columns[int(token_col_idx) - 1]
        return date_col, time_col, token_col
    except (ValueError, IndexError):
        print("Invalid column selection")
        return None, None, None

def save_results(results_df):
    """Save backtest results to CSV"""
    if results_df.empty:
        print("No results to save!")
        return
    
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results/backtest_results_{timestamp}.csv"
    
    results_df.to_csv(output_file, index=False)
    print(f"\nBacktest results saved to {output_file}")
    print(f"Total processed records: {len(results_df)}")
    
    return output_file

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
    print(f"\nLoading Excel file: {os.path.basename(excel_file)}")
    news_df = load_excel_data(excel_file)
    if news_df is None:
        return
    
    # Step 5: Get column mappings
    date_col, time_col, token_col = get_column_mappings(news_df)
    if date_col is None or token_col is None:
        return
    
    print(f"Using date column: {date_col}")
    if time_col:
        print(f"Using time column: {time_col}")
    print(f"Using token column: {token_col}")
    
    # Convert dates and times to unix timestamps
    print("\nConverting dates and times to unix timestamps...")
    time_series = news_df[time_col] if time_col else None
    news_df['unix_timestamp'] = convert_to_unix_timestamp(news_df[date_col], time_series)
    
    # Step 6: Execute backtest strategy
    print("\nExecuting backtest strategy...")
    results_df, returns = execute_backtest_strategy(price_df, news_df, token_col)
    
    # Step 7: Calculate and display performance metrics
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
    
    # Step 8: Save results
    save_results(results_df)
    
    # Step 9: Generate plots
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