import numpy as np

def calculate_performance_metrics(returns):
    """Calculate comprehensive performance metrics"""
    if len(returns) == 0:
        return {}
    
    # Convert to numpy array for calculations
    returns_array = np.array(returns)
    
    # Basic metrics
    num_trades = len(returns_array)
    total_return = np.prod(1 + returns_array) - 1
    
    # Calculate annualization factor based on per-trade basis
    # Since we don't know the actual time period, use a more conservative approach
    # Assume trades are roughly equally spaced throughout a reasonable time period
    trading_days_per_year = 365
    
    # For annualization, use the number of trades directly as periods
    # This treats each trade as an independent period
    periods_per_year = trading_days_per_year  # Assume roughly 1 trade per day on average
    
    annualized_return = (1 + total_return) ** (periods_per_year / num_trades) - 1 if num_trades > 0 else 0
    
    # Calculate cumulative returns and drawdown
    cumulative_returns = np.cumprod(1 + returns_array)
    running_max = np.maximum.accumulate(cumulative_returns)
    drawdowns = (cumulative_returns - running_max) / running_max
    max_drawdown = np.min(drawdowns)
    
    # Calculate volatility (more conservative approach)
    # Use the standard deviation of returns and annualize based on actual trade frequency
    if num_trades > 1:
        return_std = np.std(returns_array, ddof=1)
        # Annualize volatility assuming trades are roughly equally spaced
        volatility = return_std * np.sqrt(min(num_trades, periods_per_year))
        
        # Calculate Sharpe ratio with proper zero-volatility handling
        if volatility > 1e-8:  # Use small threshold instead of exact zero
            sharpe_ratio = annualized_return / volatility
        else:
            # If volatility is essentially zero, Sharpe ratio is undefined
            sharpe_ratio = 0
    else:
        volatility = 0
        sharpe_ratio = 0
    
    # Calmar ratio
    calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown < 0 else 0
    
    # Calculate win/loss metrics
    win_mask = returns_array > 0
    loss_mask = returns_array < 0
    
    win_rate = np.mean(win_mask)
    avg_win = np.mean(returns_array[win_mask]) if np.any(win_mask) else 0
    avg_loss = np.mean(returns_array[loss_mask]) if np.any(loss_mask) else 0
    
    total_wins = np.sum(returns_array[win_mask]) if np.any(win_mask) else 0
    total_losses = np.sum(returns_array[loss_mask]) if np.any(loss_mask) else 0
    profit_factor = abs(total_wins / total_losses) if total_losses != 0 else np.inf
    
    return {
        'total_return': float(total_return),
        'annualized_return': float(annualized_return),
        'max_drawdown': float(max_drawdown),
        'sharpe_ratio': float(sharpe_ratio),
        'calmar_ratio': float(calmar_ratio),
        'num_trades': int(num_trades),
        'volatility': float(volatility),
        'win_rate': float(win_rate),
        'avg_win': float(avg_win),
        'avg_loss': float(avg_loss),
        'profit_factor': float(profit_factor)
    }

def print_performance_report(metrics):
    """Print a formatted performance report"""
    if not metrics:
        print("\nNo performance metrics to display!")
        return
    
    print("\n" + "="*50)
    print("PERFORMANCE METRICS")
    print("="*50)
    print(f"Total Return: {metrics['total_return']:.4f} ({metrics['total_return']*100:.2f}%)")
    print(f"Annualized Return: {metrics['annualized_return']:.4f} ({metrics['annualized_return']*100:.2f}%)")
    print(f"Maximum Drawdown: {metrics['max_drawdown']:.4f} ({metrics['max_drawdown']*100:.2f}%)")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
    print(f"Calmar Ratio: {metrics['calmar_ratio']:.4f}")
    print(f"Volatility (Annualized): {metrics['volatility']:.4f} ({metrics['volatility']*100:.2f}%)")
    print(f"\nTrading Statistics:")
    print(f"Number of Trades: {metrics['num_trades']}")
    print(f"Win Rate: {metrics['win_rate']:.4f} ({metrics['win_rate']*100:.2f}%)")
    print(f"Average Win: {metrics['avg_win']:.4f} ({metrics['avg_win']*100:.2f}%)")
    print(f"Average Loss: {metrics['avg_loss']:.4f} ({metrics['avg_loss']*100:.2f}%)")
    print(f"Profit Factor: {metrics['profit_factor']:.4f}")

def is_strategy_profitable(metrics):
    """Determine if the strategy is profitable based on key metrics"""
    if not metrics:
        return False, "No metrics available"
    
    criteria = []
    
    # Check if positive returns
    if metrics['total_return'] > 0:
        criteria.append("✓ Positive total return")
    else:
        criteria.append("✗ Negative total return")
    
    # Check Sharpe ratio
    if metrics['sharpe_ratio'] > 1.0:
        criteria.append("✓ Good Sharpe ratio (>1.0)")
    elif metrics['sharpe_ratio'] > 0.5:
        criteria.append("○ Moderate Sharpe ratio (>0.5)")
    else:
        criteria.append("✗ Poor Sharpe ratio (<0.5)")
    
    # Check max drawdown
    if abs(metrics['max_drawdown']) < 0.1:
        criteria.append("✓ Low drawdown (<10%)")
    elif abs(metrics['max_drawdown']) < 0.2:
        criteria.append("○ Moderate drawdown (<20%)")
    else:
        criteria.append("✗ High drawdown (>20%)")
    
    # Check win rate
    if metrics['win_rate'] > 0.6:
        criteria.append("✓ High win rate (>60%)")
    elif metrics['win_rate'] > 0.4:
        criteria.append("○ Moderate win rate (>40%)")
    else:
        criteria.append("✗ Low win rate (<40%)")
    
    print(f"\nStrategy Assessment:")
    for criterion in criteria:
        print(f"  {criterion}")
    
    # Overall assessment
    positive_count = sum(1 for c in criteria if c.startswith("✓"))
    moderate_count = sum(1 for c in criteria if c.startswith("○"))
    
    if positive_count >= 3:
        return True, "Strategy appears profitable"
    elif positive_count + moderate_count >= 3:
        return True, "Strategy shows moderate promise"
    else:
        return False, "Strategy needs improvement"