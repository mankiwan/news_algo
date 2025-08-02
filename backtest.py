import pandas as pd
import numpy as np

def get_prices_at_timestamps(price_df, timestamps, price_column='close'):
    """Get prices at multiple timestamps with +1min and +10min offsets"""
    if price_df is None or len(timestamps) == 0:
        return pd.DataFrame()
    
    # Convert timestamps to numpy array for vectorized operations
    timestamps = np.array(timestamps)
    
    # Calculate offset timestamps
    timestamps_1min = timestamps + 60
    timestamps_10min = timestamps + 600
    
    # Prepare price timestamps for broadcasting
    price_timestamps = price_df['unix_timestamp'].values
    
    # Find closest timestamps using binary search
    def find_closest_prices(target_timestamps, tolerance=120):
        # Find insertion points
        indices = np.searchsorted(price_timestamps, target_timestamps)
        
        # Handle edge cases
        indices = np.clip(indices, 0, len(price_timestamps) - 1)
        
        # Calculate distances to find truly closest
        left_indices = np.maximum(indices - 1, 0)
        right_indices = indices
        
        left_diffs = np.abs(target_timestamps - price_timestamps[left_indices])
        right_diffs = np.abs(target_timestamps - price_timestamps[right_indices])
        
        # Choose closest
        closest_indices = np.where(left_diffs <= right_diffs, left_indices, right_indices)
        
        # Check tolerance
        min_diffs = np.minimum(left_diffs, right_diffs)
        valid_mask = min_diffs <= tolerance
        
        # Get prices
        prices = np.full(len(target_timestamps), np.nan)
        prices[valid_mask] = price_df[price_column].iloc[closest_indices[valid_mask]].values
        
        return prices
    
    # Get prices for all timestamps
    prices_current = find_closest_prices(timestamps)
    prices_1min = find_closest_prices(timestamps_1min)
    prices_10min = find_closest_prices(timestamps_10min)
    
    # Create result DataFrame
    result_df = pd.DataFrame({
        'unix_timestamp': timestamps,
        'price_current': prices_current,
        'price_1min': prices_1min,
        'price_10min': prices_10min
    })
    
    return result_df


def execute_backtest_strategy(price_df, news_df, token_col, selected_crypto):
    """Execute the news trading strategy for selected cryptocurrency"""
    
    # Sort by unix timestamp
    news_df_sorted = news_df.sort_values(by='unix_timestamp').copy()
    print(f"\nData sorted by unix timestamp")
    
    print(f"\nUnique tokens found: {news_df_sorted[token_col].dropna().unique()}")
    
    # Filter for selected cryptocurrency tokens only
    if selected_crypto == "BTC":
        crypto_patterns = ['BTC', 'BITCOIN']
    elif selected_crypto == "ETH":
        crypto_patterns = ['ETH', 'ETHEREUM']
    else:
        print(f"Unsupported cryptocurrency: {selected_crypto}")
        return pd.DataFrame(), []
    
    # Create mask for any of the crypto patterns
    token_mask = news_df_sorted[token_col].astype(str).str.upper().str.contains('|'.join(crypto_patterns), na=False)
    timestamp_mask = news_df_sorted['unix_timestamp'].notna()
    valid_mask = token_mask & timestamp_mask
    
    crypto_news = news_df_sorted[valid_mask].copy()
    
    if len(crypto_news) == 0:
        print(f"No valid {selected_crypto} news events found!")
        return pd.DataFrame(), []
    
    print(f"\nProcessing {len(crypto_news)} {selected_crypto} news events...")
    
    # Sort price data by timestamp for efficient searching
    price_df_sorted = price_df.sort_values('unix_timestamp').copy()
    
    # Get prices for all events at once
    timestamps = crypto_news['unix_timestamp'].values
    price_results = get_prices_at_timestamps(price_df_sorted, timestamps)
    
    # Merge price results with news data
    crypto_news = crypto_news.reset_index(drop=True)
    crypto_news = pd.concat([crypto_news, price_results[['price_current', 'price_1min', 'price_10min']]], axis=1)
    
    # Remove rows with missing price data
    price_mask = crypto_news[['price_current', 'price_1min', 'price_10min']].notna().all(axis=1)
    crypto_news = crypto_news[price_mask].copy()
    
    if len(crypto_news) == 0:
        print("No valid price data found for news events!")
        return pd.DataFrame(), []
    
    print(f"Found price data for {len(crypto_news)} events")
    
    # Calculate 1-minute price change percentage
    crypto_news['price_change_1min'] = (crypto_news['price_1min'] - crypto_news['price_current']) / crypto_news['price_current']
    
    # Determine position: 1 if positive change, -1 if negative
    crypto_news['position'] = np.where(crypto_news['price_change_1min'] > 0, 1, -1)
    
    # Calculate return after 10 minutes
    crypto_news['price_change_10min'] = (crypto_news['price_10min'] - crypto_news['price_current']) / crypto_news['price_current']
    crypto_news['trade_return'] = crypto_news['position'] * crypto_news['price_change_10min']
    
    # Clean up token column
    crypto_news['token'] = crypto_news[token_col].astype(str).str.upper().str.strip()
    
    # Select relevant columns for results
    result_columns = [
        'unix_timestamp', 'token', 'price_current', 'price_1min', 'price_10min',
        'price_change_1min', 'position', 'trade_return'
    ]
    
    results_df = crypto_news[result_columns].copy()
    returns = results_df['trade_return'].tolist()
    
    # Print summary statistics
    print(f"\nStrategy Results Summary:")
    print(f"Total trades: {len(results_df)}")
    print(f"Average return per trade: {np.mean(returns):.4f}")
    print(f"Win rate: {(np.array(returns) > 0).mean():.2%}")
    
    return results_df, returns
    

