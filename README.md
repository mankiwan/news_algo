# Cryptocurrency News Trading Backtest

A comprehensive Python backtesting framework for evaluating cryptocurrency trading strategies based on news events. This system analyzes the impact of news announcements on Bitcoin (BTC) and Ethereum (ETH) prices and backtests a momentum-based trading strategy.

## 📊 Strategy Overview

### Trading Logic
1. **News Event Detection**: Monitor cryptocurrency news announcements
2. **Price Momentum Analysis**: Observe price movement 1 minute after news
3. **Position Taking**: 
   - If price increases in first minute → Take LONG position
   - If price decreases in first minute → Take SHORT position
4. **Exit Strategy**: Close position after 10 minutes

### Key Features
- Support for BTC and ETH trading
- Vectorized operations for high performance
- Comprehensive performance analytics
- Professional visualization suite
- Modular, reusable codebase

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone or download the project**
```bash
cd news_algo
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 📁 Project Structure

```
news_algo/
├── main.py              # Main execution script with user interface
├── backtest.py          # Core backtesting strategy logic
├── performance.py       # Performance metrics calculations
├── plotting.py          # Visualization and charting functions
├── download_data.py     # Binance price data downloader
├── requirements.txt     # Python dependencies
├── news/               # News data directory
│   └── *.xlsx         # Excel files with news data
├── downloads/          # Price data directory
│   └── *.csv          # CSV files with price data
└── results/            # Output directory
    ├── *.csv          # Backtest results
    └── *.png          # Performance charts
```

## 📊 Data Requirements

### Price Data
- **Source**: Binance API (use `download_data.py`)
- **Format**: CSV with columns: `open_time`, `open`, `high`, `low`, `close`, `volume`
- **Frequency**: 1-minute intervals recommended
- **Location**: `downloads/` directory

### News Data
- **Format**: Excel (.xlsx) files
- **Required Columns**:
  - Date column (various formats supported)
  - Time column (optional, for precise timing)
  - Token/Cryptocurrency column (BTC, ETH, Bitcoin, Ethereum)
- **Location**: `news/` directory

## 🏃‍♂️ Running the Backtest

### Step 1: Download Price Data
```bash
python download_data.py
```
Follow the prompts to:
- Select cryptocurrency (BTC/ETH)
- Choose time interval (1m recommended)
- Set date range for historical data

### Step 2: Prepare News Data
- Place your Excel file with news data in the `news/` directory
- Ensure it contains date, time (optional), and token columns

### Step 3: Run Backtest
```bash
python main.py
```

### Interactive Workflow
The system will guide you through:

1. **CSV File Selection**: Choose price data file from `downloads/`
2. **Excel File Selection**: Choose news data file from `news/`
3. **Cryptocurrency Selection**: Choose BTC or ETH
4. **Column Mapping**: Identify date, time, and token columns
5. **Backtest Execution**: Automated strategy execution
6. **Results Display**: Performance metrics and statistics
7. **Visualization**: Optional chart generation

## 📈 Performance Metrics

The system calculates comprehensive performance statistics:

### Return Metrics
- **Total Return**: Cumulative strategy performance
- **Annualized Return**: Yearly extrapolated performance
- **Win Rate**: Percentage of profitable trades
- **Average Win/Loss**: Mean profit and loss per trade

### Risk Metrics
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Volatility**: Annualized standard deviation of returns
- **Sharpe Ratio**: Risk-adjusted return metric
- **Calmar Ratio**: Return vs. maximum drawdown

### Trading Statistics
- **Number of Trades**: Total executed trades
- **Profit Factor**: Ratio of gross profit to gross loss

## 📊 Visualization Suite

### Available Charts
1. **Cumulative Returns**: Strategy performance over time
2. **Drawdown Curve**: Risk exposure visualization
3. **Returns Distribution**: Statistical analysis of trade outcomes
4. **Win/Loss Analysis**: Success rate breakdown
5. **Price Action Analysis**: Market behavior around news events
6. **Performance Summary**: Key metrics dashboard

### Chart Export
- All charts saved to `results/` directory
- High-resolution PNG format (300 DPI)
- Professional styling with seaborn

## 🔧 Configuration

### Supported Date Formats
```
2023-12-25 14:30:00
2023-12-25
12/25/2023 14:30:00
12/25/2023
25/12/2023 14:30:00
25/12/2023
```

### Supported Time Formats
```
14:30:00 (24-hour)
14:30
2:30:00 PM (12-hour)
2:30 PM
```

### Trading Parameters
- **Observation Window**: 1 minute for momentum detection
- **Position Duration**: 10 minutes holding period
- **Price Tolerance**: 2 minutes for price matching
- **Trading Days**: 365 days/year (24/7 crypto markets)

## 🐛 Troubleshooting

### Common Issues

**1. No CSV files found**
- Ensure price data is in `downloads/` directory
- Run `download_data.py` to fetch data from Binance

**2. No Excel files found**
- Place news data files in `news/` directory
- Supported formats: .xlsx, .xls

**3. No valid trades found**
- Check if token column contains BTC/ETH references
- Verify date/time alignment with price data
- Ensure news events fall within price data time range

**4. Import errors**
- Install missing packages: `pip install -r requirements.txt`
- For plotting issues: `pip install matplotlib seaborn`

### Performance Optimization
- Use 1-minute price data for optimal precision
- Limit news data to overlapping time periods with price data
- Close other applications for large dataset processing

## 🔍 Advanced Usage

### Custom Strategy Development
Modify `backtest.py` to implement:
- Different momentum windows
- Alternative position sizing
- Stop-loss mechanisms
- Multi-timeframe analysis

### Additional Cryptocurrencies
Extend support by:
1. Adding new patterns in `execute_backtest_strategy()`
2. Updating price data download script
3. Testing with relevant news data

### Batch Processing
Process multiple files by:
1. Modifying file selection functions
2. Adding loop structures in `main.py`
3. Implementing result aggregation

## 📄 License

This project is for educational and research purposes. Use at your own risk for live trading.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement improvements
4. Add tests and documentation
5. Submit pull request

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Review error messages carefully
3. Ensure data format compliance
4. Verify all dependencies are installed

---

**Disclaimer**: This backtesting framework is for educational purposes only. Past performance does not guarantee future results. Cryptocurrency trading involves substantial risk of loss.