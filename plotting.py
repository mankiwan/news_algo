import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime
import os

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def plot_cumulative_returns(results_df, save_path="results/cumulative_returns.png"):
    """Plot cumulative returns over time"""
    if results_df.empty or 'trade_return' not in results_df.columns:
        print("No trade returns data available for plotting")
        return
    
    # Calculate cumulative returns
    cumulative_returns = (1 + results_df['trade_return']).cumprod()
    
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(cumulative_returns)), cumulative_returns, linewidth=2, label='Strategy')
    plt.axhline(y=1, color='r', linestyle='--', alpha=0.7, label='Breakeven')
    
    plt.title('Cumulative Returns Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Trade Number', fontsize=12)
    plt.ylabel('Cumulative Return', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Cumulative returns plot saved to {save_path}")

def plot_drawdown_curve(results_df, save_path="results/drawdown_curve.png"):
    """Plot drawdown curve"""
    if results_df.empty or 'trade_return' not in results_df.columns:
        print("No trade returns data available for plotting")
        return
    
    # Calculate cumulative returns and drawdowns
    cumulative_returns = (1 + results_df['trade_return']).cumprod()
    running_max = cumulative_returns.expanding().max()
    drawdowns = (cumulative_returns - running_max) / running_max
    
    plt.figure(figsize=(12, 6))
    plt.fill_between(range(len(drawdowns)), drawdowns, 0, alpha=0.7, color='red', label='Drawdown')
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.8)
    
    plt.title('Drawdown Curve', fontsize=16, fontweight='bold')
    plt.xlabel('Trade Number', fontsize=12)
    plt.ylabel('Drawdown (%)', fontsize=12)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1%}'.format(y)))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Drawdown curve plot saved to {save_path}")

def plot_returns_distribution(results_df, save_path="results/returns_distribution.png"):
    """Plot distribution of individual trade returns"""
    if results_df.empty or 'trade_return' not in results_df.columns:
        print("No trade returns data available for plotting")
        return
    
    returns = results_df['trade_return']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Histogram
    ax1.hist(returns, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    ax1.axvline(returns.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {returns.mean():.4f}')
    ax1.axvline(returns.median(), color='green', linestyle='--', linewidth=2, label=f'Median: {returns.median():.4f}')
    ax1.set_title('Distribution of Trade Returns', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Return', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Box plot
    ax2.boxplot(returns, vert=True)
    ax2.set_title('Box Plot of Trade Returns', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Return', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Returns distribution plot saved to {save_path}")

def plot_win_loss_analysis(results_df, save_path="results/win_loss_analysis.png"):
    """Plot win/loss analysis"""
    if results_df.empty or 'trade_return' not in results_df.columns:
        print("No trade returns data available for plotting")
        return
    
    returns = results_df['trade_return']
    wins = returns[returns > 0]
    losses = returns[returns < 0]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Win/Loss pie chart
    labels = ['Wins', 'Losses']
    sizes = [len(wins), len(losses)]
    colors = ['lightgreen', 'lightcoral']
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Win/Loss Ratio', fontsize=14, fontweight='bold')
    
    # Win/Loss histogram
    ax2.hist([wins, losses], bins=20, label=['Wins', 'Losses'], color=['green', 'red'], alpha=0.7)
    ax2.set_title('Win/Loss Distribution', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Return', fontsize=12)
    ax2.set_ylabel('Frequency', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Cumulative wins vs losses
    win_cumsum = wins.cumsum() if len(wins) > 0 else pd.Series([0])
    loss_cumsum = losses.cumsum() if len(losses) > 0 else pd.Series([0])
    
    ax3.plot(range(len(win_cumsum)), win_cumsum, 'g-', label='Cumulative Wins', linewidth=2)
    ax3.plot(range(len(loss_cumsum)), loss_cumsum, 'r-', label='Cumulative Losses', linewidth=2)
    ax3.set_title('Cumulative Wins vs Losses', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Trade Number', fontsize=12)
    ax3.set_ylabel('Cumulative Return', fontsize=12)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Monthly returns (if timestamp available)
    if 'unix_timestamp' in results_df.columns:
        results_df['date'] = pd.to_datetime(results_df['unix_timestamp'], unit='s')
        monthly_returns = results_df.groupby(results_df['date'].dt.to_period('M'))['trade_return'].sum()
        
        monthly_returns.plot(kind='bar', ax=ax4, color=['green' if x > 0 else 'red' for x in monthly_returns])
        ax4.set_title('Monthly Returns', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Month', fontsize=12)
        ax4.set_ylabel('Return', fontsize=12)
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'No timestamp data\nfor monthly analysis', 
                ha='center', va='center', transform=ax4.transAxes, fontsize=12)
        ax4.set_title('Monthly Returns (N/A)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Win/loss analysis plot saved to {save_path}")

def plot_price_action_analysis(results_df, save_path="results/price_action_analysis.png"):
    """Plot price action analysis around news events"""
    if results_df.empty:
        print("No data available for plotting")
        return
    
    required_cols = ['price_current', 'price_1min', 'price_10min', 'price_change_1min', 'position']
    if not all(col in results_df.columns for col in required_cols):
        print("Missing required columns for price action analysis")
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Price changes distribution
    ax1.hist(results_df['price_change_1min'], bins=30, alpha=0.7, color='purple', edgecolor='black')
    ax1.axvline(0, color='red', linestyle='--', linewidth=2, label='No Change')
    ax1.set_title('1-Minute Price Change Distribution', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Price Change (%)', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Position distribution
    position_counts = results_df['position'].value_counts()
    ax2.bar(position_counts.index, position_counts.values, color=['red', 'green'])
    ax2.set_title('Position Distribution', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Position (1=Long, -1=Short)', fontsize=12)
    ax2.set_ylabel('Count', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Price evolution (sample of trades)
    sample_size = min(20, len(results_df))
    sample_indices = np.random.choice(len(results_df), sample_size, replace=False)
    sample_data = results_df.iloc[sample_indices]
    
    for i, (_, row) in enumerate(sample_data.iterrows()):
        prices = [row['price_current'], row['price_1min'], row['price_10min']]
        times = [0, 1, 10]
        color = 'green' if row['trade_return'] > 0 else 'red'
        ax3.plot(times, prices, color=color, alpha=0.6, linewidth=1)
    
    ax3.set_title(f'Price Evolution (Sample of {sample_size} trades)', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Minutes after news', fontsize=12)
    ax3.set_ylabel('Price', fontsize=12)
    ax3.grid(True, alpha=0.3)
    
    # Returns vs price change correlation
    price_change_10min = (results_df['price_10min'] - results_df['price_current']) / results_df['price_current']
    ax4.scatter(results_df['price_change_1min'], price_change_10min, alpha=0.6)
    ax4.set_title('1-Min vs 10-Min Price Changes', fontsize=14, fontweight='bold')
    ax4.set_xlabel('1-Minute Price Change (%)', fontsize=12)
    ax4.set_ylabel('10-Minute Price Change (%)', fontsize=12)
    ax4.grid(True, alpha=0.3)
    
    # Add correlation coefficient
    corr = np.corrcoef(results_df['price_change_1min'], price_change_10min)[0,1]
    ax4.text(0.05, 0.95, f'Correlation: {corr:.3f}', transform=ax4.transAxes, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Price action analysis plot saved to {save_path}")

def plot_performance_summary(metrics, save_path="results/performance_summary.png"):
    """Plot performance metrics summary"""
    if not metrics:
        print("No performance metrics available for plotting")
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Key metrics bar chart
    key_metrics = {
        'Total Return': metrics.get('total_return', 0) * 100,
        'Annualized Return': metrics.get('annualized_return', 0) * 100,
        'Max Drawdown': metrics.get('max_drawdown', 0) * 100,
        'Volatility': metrics.get('volatility', 0) * 100
    }
    
    colors = ['green' if v > 0 else 'red' for v in key_metrics.values()]
    bars = ax1.bar(key_metrics.keys(), key_metrics.values(), color=colors, alpha=0.7)
    ax1.set_title('Key Performance Metrics (%)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Percentage (%)', fontsize=12)
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, key_metrics.values()):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.2f}%', ha='center', va='bottom')
    
    # Risk-Return scatter
    returns = [metrics.get('annualized_return', 0) * 100]
    risks = [metrics.get('volatility', 0) * 100]
    ax2.scatter(risks, returns, s=100, c='blue', alpha=0.7)
    ax2.set_title('Risk-Return Profile', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Volatility (%)', fontsize=12)
    ax2.set_ylabel('Annualized Return (%)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Add strategy label
    ax2.annotate('Strategy', (risks[0], returns[0]), 
                xytext=(10, 10), textcoords='offset points')
    
    # Ratio metrics
    ratios = {
        'Sharpe Ratio': metrics.get('sharpe_ratio', 0),
        'Calmar Ratio': metrics.get('calmar_ratio', 0),
        'Win Rate': metrics.get('win_rate', 0) * 100 if 'win_rate' in metrics else 0,
        'Profit Factor': min(metrics.get('profit_factor', 0), 10)  # Cap at 10 for visualization
    }
    
    ax3.bar(ratios.keys(), ratios.values(), color='skyblue', alpha=0.7)
    ax3.set_title('Performance Ratios', fontsize=14, fontweight='bold')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    
    # Trade statistics
    trade_stats = {
        'Total Trades': metrics.get('num_trades', 0),
        'Win Rate (%)': metrics.get('win_rate', 0) * 100 if 'win_rate' in metrics else 0,
        'Avg Win (%)': metrics.get('avg_win', 0) * 100 if 'avg_win' in metrics else 0,
        'Avg Loss (%)': metrics.get('avg_loss', 0) * 100 if 'avg_loss' in metrics else 0
    }
    
    # Create text summary
    text_summary = "\n".join([f"{k}: {v:.2f}" for k, v in trade_stats.items()])
    ax4.text(0.1, 0.9, text_summary, transform=ax4.transAxes, fontsize=12,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    ax4.set_title('Trading Statistics', fontsize=14, fontweight='bold')
    ax4.axis('off')
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Performance summary plot saved to {save_path}")

def generate_all_plots(results_df, metrics=None):
    """Generate all available plots"""
    print("Generating all visualization plots...")
    print("=" * 50)
    
    # List of available plots
    plots = [
        ("Cumulative Returns", plot_cumulative_returns),
        ("Drawdown Curve", plot_drawdown_curve),
        ("Returns Distribution", plot_returns_distribution),
        ("Win/Loss Analysis", plot_win_loss_analysis),
        ("Price Action Analysis", plot_price_action_analysis),
    ]
    
    # Generate plots
    for plot_name, plot_function in plots:
        try:
            print(f"Generating {plot_name}...")
            plot_function(results_df)
        except Exception as e:
            print(f"Error generating {plot_name}: {e}")
    
    # Generate performance summary if metrics available
    if metrics:
        try:
            print("Generating Performance Summary...")
            plot_performance_summary(metrics)
        except Exception as e:
            print(f"Error generating Performance Summary: {e}")
    
    print("=" * 50)
    print("All plots generated and saved to 'results/' directory")

# Suggested additional plots that could be implemented:
"""
SUGGESTED ADDITIONAL VISUALIZATIONS:

1. **Time-based Analysis**:
   - Returns by hour of day
   - Returns by day of week
   - Seasonal patterns
   - News frequency over time

2. **Market Condition Analysis**:
   - Performance during different volatility regimes
   - Performance vs Bitcoin price trends
   - Correlation with market indices

3. **News Impact Analysis**:
   - Returns by news sentiment (if available)
   - Returns by news category/type
   - News volume vs price impact

4. **Risk Analysis**:
   - Rolling Sharpe ratio
   - Rolling volatility
   - Value at Risk (VaR)
   - Expected Shortfall

5. **Comparative Analysis**:
   - Strategy vs buy-and-hold
   - Strategy vs benchmark indices
   - Multiple strategy comparison

6. **Interactive Plots**:
   - Plotly interactive charts
   - Dashboard with real-time updates
   - Parameter sensitivity analysis

7. **Advanced Analytics**:
   - Rolling correlation analysis
   - Factor attribution
   - Performance attribution
   - Transaction cost analysis
"""