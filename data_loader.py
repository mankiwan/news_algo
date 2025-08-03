"""
Data loading and file selection utilities for the news trading backtest system.

This module handles all file I/O operations including:
- CSV price data loading
- Excel news data loading  
- File selection interfaces
- Date/time parsing and conversion
"""

import os
import glob
import pandas as pd
from datetime import datetime


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
    """Convert date and time columns to unix timestamp"""
    
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
        
        # Process each time value to extract time component
        processed_times = []
        for time_val in time_series:
            if pd.isna(time_val):
                processed_times.append(None)
                continue
                
            time_str = None
            if isinstance(time_val, datetime):
                # Extract time component from datetime object
                time_str = time_val.strftime('%H:%M:%S')
            elif hasattr(time_val, 'hour'):  # datetime.time object
                time_str = f"{time_val.hour:02d}:{time_val.minute:02d}:{time_val.second:02d}"
            else:
                # Try to parse as string
                time_str = str(time_val)
                # Remove any date prefix if it exists (like "1900-01-01 05:39:40")
                if ' ' in time_str and len(time_str) > 8:
                    time_str = time_str.split(' ', 1)[1]  # Take everything after first space
            
            processed_times.append(time_str)
        
        # Now combine dates with processed times
        combined_datetimes = []
        for i, (date_val, time_str) in enumerate(zip(date_dt, processed_times)):
            if pd.isna(date_val) or time_str is None:
                combined_datetimes.append(pd.NaT)
                continue
            
            try:
                # Create combined datetime string
                date_str = date_val.strftime('%Y-%m-%d')
                combined_str = f"{date_str} {time_str}"
                
                # Parse combined datetime
                combined_dt = pd.to_datetime(combined_str, errors='coerce')
                combined_datetimes.append(combined_dt)
                
            except Exception as e:
                print(f"Warning: Could not parse date/time combination for row {i}: {date_val} + {time_str}")
                combined_datetimes.append(date_val)  # Fall back to date only
        
        final_dt = pd.Series(combined_datetimes)
    else:
        final_dt = date_dt
    
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


def select_cryptocurrency():
    """Prompt user to select cryptocurrency for backtesting"""
    print("\nSelect cryptocurrency for backtesting:")
    print("1. BTC (Bitcoin)")
    print("2. ETH (Ethereum)")
    
    while True:
        try:
            choice = input("\nEnter your choice (1 or 2): ").strip()
            if choice == "1":
                return "BTC"
            elif choice == "2":
                return "ETH"
            else:
                print("Invalid selection. Please enter 1 for BTC or 2 for ETH.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None


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