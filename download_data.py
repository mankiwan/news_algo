import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time

def get_binance_klines(symbol, interval, start_time, end_time):
    """
    Download kline data from Binance API
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT', 'ETHUSDT')
        interval: Time interval ('1m', '5m', '1h', '1d', etc.)
        start_time: Start time in milliseconds
        end_time: End time in milliseconds
    """
    base_url = 'https://api.binance.com/api/v3/klines'
    
    all_data = []
    current_start = start_time
    
    while current_start < end_time:
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': current_start,
            'endTime': min(current_start + 1000 * 60 * 1000, end_time),  # Max 1000 records per request
            'limit': 1000
        }
        
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            all_data.extend(data)
            current_start = data[-1][6] + 1  # Next start time
            print(f"Downloaded {len(data)} records, total: {len(all_data)}")
            time.sleep(0.1)  # Rate limiting
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break
    
    return all_data

def convert_to_dataframe(kline_data):
    """Convert kline data to pandas DataFrame"""
    columns = [
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ]
    
    df = pd.DataFrame(kline_data, columns=columns)
    
    # Convert to appropriate data types
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    
    for col in ['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']:
        df[col] = df[col].astype(float)
    
    df['number_of_trades'] = df['number_of_trades'].astype(int)
    
    return df

def main():
    print("Binance Data Downloader")
    print("=" * 30)
    
    # Get user input
    symbol = input("Enter trading pair (BTC/ETH): ").upper().strip()
    if symbol in ['BTC', 'BITCOIN']:
        symbol = 'BTCUSDT'
    elif symbol in ['ETH', 'ETHEREUM']:
        symbol = 'ETHUSDT'
    elif not symbol.endswith('USDT'):
        symbol += 'USDT'
    
    # Interval selection
    print("\nAvailable intervals:")
    intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d']
    for i, interval in enumerate(intervals, 1):
        print(f"{i}. {interval}")
    
    interval_choice = input("\nSelect interval (1-12) or enter custom: ").strip()
    if interval_choice.isdigit() and 1 <= int(interval_choice) <= 12:
        interval = intervals[int(interval_choice) - 1]
    else:
        interval = interval_choice
    
    # Date selection
    print("\nDate selection:")
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        
        start_timestamp = int(start_dt.timestamp() * 1000)
        end_timestamp = int(end_dt.timestamp() * 1000)
        
        print(f"\nDownloading {symbol} {interval} data from {start_date} to {end_date}")
        
        # Download data
        kline_data = get_binance_klines(symbol, interval, start_timestamp, end_timestamp)
        
        if kline_data:
            # Convert to DataFrame
            df = convert_to_dataframe(kline_data)
            
            # Save to CSV
            filename = f"downloads/{symbol}_{interval}_{start_date}_to_{end_date}.csv"
            df.to_csv(filename, index=False)
            
            print(f"\nData saved to {filename}")
            print(f"Total records: {len(df)}")
            print(f"Date range: {df['open_time'].min()} to {df['open_time'].max()}")
            
        else:
            print("No data downloaded")
            
    except ValueError as e:
        print(f"Date format error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()