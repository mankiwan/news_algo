import pandas as pd
import numpy as np

def get_prices_at_timestamps(price_df, timestamps, price_column='close', window=1, threshold=10):
    """Get prices at multiple timestamps with configurable window and threshold offsets (in minutes)"""
    if price_df is None or len(timestamps) == 0:
        return pd.DataFrame()
    
    # Convert timestamps to numpy array for vectorized operations
    timestamps = np.array(timestamps)
    
    # Calculate offset timestamps using configurable parameters (convert minutes to seconds)
    timestamps_window = timestamps + (window * 60)
    timestamps_threshold = timestamps + (threshold * 60)
    
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
    prices_window = find_closest_prices(timestamps_window)
    prices_threshold = find_closest_prices(timestamps_threshold)
    
    # Create result DataFrame
    result_df = pd.DataFrame({
        'unix_timestamp': timestamps,
        'price_current': prices_current,
        'price_window': prices_window,
        'price_threshold': prices_threshold
    })
    
    return result_df


def filter_crypto_news(news_df, token_col, selected_crypto):
    """Filter news data for selected cryptocurrency"""
    # Sort by unix timestamp
    news_df_sorted = news_df.sort_values(by='unix_timestamp').copy()
    
    # Define crypto patterns
    if selected_crypto == "BTC":
        crypto_patterns = ['BTC', 'BITCOIN']
    elif selected_crypto == "ETH":
        crypto_patterns = ['ETH', 'ETHEREUM']
    else:
        raise ValueError(f"Unsupported cryptocurrency: {selected_crypto}")
    
    # Create mask for any of the crypto patterns
    token_mask = news_df_sorted[token_col].astype(str).str.upper().str.contains('|'.join(crypto_patterns), na=False)
    timestamp_mask = news_df_sorted['unix_timestamp'].notna()
    valid_mask = token_mask & timestamp_mask
    
    return news_df_sorted[valid_mask].copy()


def calculate_trading_returns(crypto_news, trading_costs=None, window_col='price_window', threshold_col='price_threshold'):
    """Calculate trading returns with optional costs"""
    # Calculate window price change percentage (for position determination)
    crypto_news['price_change_window'] = (crypto_news[window_col] - crypto_news['price_current']) / crypto_news['price_current']
    
    # Determine position: 1 if positive change, -1 if negative
    crypto_news['position'] = np.where(crypto_news['price_change_window'] > 0, 1, -1)
    
    # Calculate return after threshold period
    crypto_news['price_change_threshold'] = (crypto_news[threshold_col] - crypto_news['price_current']) / crypto_news['price_current']
    
    # Apply transaction costs and slippage if provided
    if trading_costs is not None:
        transaction_cost = trading_costs.get('transaction_cost', 0)
        slippage = trading_costs.get('slippage', 0)
        total_cost = transaction_cost + slippage
        
        # Calculate gross return first
        gross_return = crypto_news['position'] * crypto_news['price_change_threshold']
        
        # Apply costs: subtract total cost for each trade (entry + exit)
        crypto_news['trade_return'] = gross_return - (2 * total_cost * np.abs(crypto_news['position']))
    else:
        # No costs applied
        crypto_news['trade_return'] = crypto_news['position'] * crypto_news['price_change_threshold']
    
    return crypto_news


def execute_backtest_strategy(price_df, news_df, token_col, selected_crypto, trading_costs=None, window=1, threshold=10, verbose=True):
    """Execute the news trading strategy with configurable parameters (window and threshold in minutes)"""
    
    if verbose:
        print(f"\nData sorted by unix timestamp")
        print(f"\nUnique tokens found: {news_df[token_col].dropna().unique()}")
    
    try:
        # Filter crypto news
        crypto_news = filter_crypto_news(news_df, token_col, selected_crypto)
        
        if len(crypto_news) == 0:
            if verbose:
                print(f"No valid {selected_crypto} news events found!")
            return pd.DataFrame(), []
        
        if verbose:
            print(f"\nProcessing {len(crypto_news)} {selected_crypto} news events...")
        
        # Sort price data by timestamp for efficient searching
        price_df_sorted = price_df.sort_values('unix_timestamp').copy()
        
        # Get prices for all events at once
        timestamps = crypto_news['unix_timestamp'].values
        price_results = get_prices_at_timestamps(price_df_sorted, timestamps, window=window, threshold=threshold)
        
        # Merge price results with news data
        crypto_news = crypto_news.reset_index(drop=True)
        crypto_news = pd.concat([crypto_news, price_results[['price_current', 'price_window', 'price_threshold']]], axis=1)
        
        # Remove rows with missing price data
        price_mask = crypto_news[['price_current', 'price_window', 'price_threshold']].notna().all(axis=1)
        crypto_news = crypto_news[price_mask].copy()
        
        if len(crypto_news) == 0:
            if verbose:
                print("No valid price data found for news events!")
            return pd.DataFrame(), []
        
        if verbose:
            print(f"Found price data for {len(crypto_news)} events")
        
        # Calculate trading returns
        crypto_news = calculate_trading_returns(crypto_news, trading_costs)
        
        # Print cost information if verbose
        if verbose and trading_costs is not None:
            transaction_cost = trading_costs.get('transaction_cost', 0)
            slippage = trading_costs.get('slippage', 0)
            total_cost = transaction_cost + slippage
            print(f"\nApplying trading costs:")
            print(f"- Transaction cost: {transaction_cost*100:.3f}% per trade")
            print(f"- Slippage: {slippage*100:.3f}% per trade")
            print(f"- Total cost per round trip: {2*total_cost*100:.3f}%")
        elif verbose:
            print(f"\nNo trading costs applied (ideal conditions)")
        
        # Clean up token column
        crypto_news['token'] = crypto_news[token_col].astype(str).str.upper().str.strip()
        
        # Select relevant columns for results
        result_columns = [
            'unix_timestamp', 'token', 'price_current', 'price_window', 'price_threshold',
            'price_change_window', 'position', 'trade_return'
        ]
        
        # For backward compatibility, rename columns for default case
        if window == 1 and threshold == 10:
            crypto_news = crypto_news.rename(columns={
                'price_window': 'price_1min',
                'price_threshold': 'price_10min',
                'price_change_window': 'price_change_1min'
            })
            result_columns = [
                'unix_timestamp', 'token', 'price_current', 'price_1min', 'price_10min',
                'price_change_1min', 'position', 'trade_return'
            ]
        
        results_df = crypto_news[result_columns].copy()
        returns = results_df['trade_return'].tolist()
        
        # Print summary statistics if verbose
        if verbose:
            print(f"\nStrategy Results Summary:")
            print(f"Total trades: {len(results_df)}")
            print(f"Average return per trade: {np.mean(returns):.4f}")
            print(f"Win rate: {(np.array(returns) > 0).mean():.2%}")
        
        return results_df, returns
        
    except Exception as e:
        if verbose:
            print(f"Error in backtest execution: {e}")
        return pd.DataFrame(), []


# Alias for backward compatibility - now they use the same optimized function
execute_backtest_strategy_optimized = execute_backtest_strategy


