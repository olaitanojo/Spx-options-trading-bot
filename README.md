# 🚀 SPX Options Trading Bot

[![CI/CD Pipeline](https://github.com/olaitanojo/Spx-options-trading-bot/actions/workflows/ci-cd-pipeline.yml/badge.svg)](https://github.com/olaitanojo/Spx-options-trading-bot/actions/workflows/ci-cd-pipeline.yml)

A sophisticated automated trading system for SPX options with comprehensive backtesting, risk management, and real-time execution capabilities.

🔧 **Enterprise-Grade CI/CD Pipeline Active** - This repository now includes automated testing, security scanning, code quality checks, and deployment capabilities!

## 🎯 Features

- **📊 Advanced Technical Analysis**: MACD, RSI, Bollinger Bands, Moving Averages
- **🔄 Automated Signal Generation**: Multi-factor trading signals based on market conditions
- **⚡ Real-time Market Analysis**: Live SPX and VIX data integration
- **📈 Comprehensive Backtesting**: Historical strategy performance analysis
- **🛡️ Risk Management**: Position sizing, stop-loss, and portfolio risk controls
- **📱 Live Trading Recommendations**: Current market analysis and trade suggestions
- **📋 Detailed Logging**: Complete audit trail of all trading decisions

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/olaitanojo/spx-options-trading-bot.git
   cd spx-options-trading-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the bot**
   ```bash
   python main.py
   ```

## 📊 How It Works

### Technical Indicators Used

- **Moving Averages**: 20-day and 50-day SMA, 12-day and 26-day EMA
- **MACD**: Momentum indicator with signal line and histogram
- **RSI**: Relative Strength Index for overbought/oversold conditions
- **Bollinger Bands**: Volatility-based support and resistance levels
- **VIX Integration**: Market fear gauge for volatility assessment

### Trading Strategy

The bot generates signals based on multiple technical factors:

**Bullish Signals (Buy Calls)**:
- Price above 20-day moving average
- MACD above signal line
- RSI between 30-70 (not extreme)
- Positive price momentum

**Bearish Signals (Buy Puts)**:
- Price below 20-day moving average
- MACD below signal line
- RSI between 30-70 (not extreme)
- Negative price momentum

### Risk Management

- **Position Sizing**: 2% risk per trade
- **Portfolio Risk**: Maximum 10% total portfolio risk
- **Stop Loss**: 50% of option premium
- **Profit Target**: 25% gain target

## 🔧 Configuration

Key parameters can be adjusted in the `TradingStrategy` class:

```python
@dataclass
class TradingStrategy:
    name: str
    max_risk_per_trade: float = 0.02  # 2% of portfolio
    max_portfolio_risk: float = 0.10   # 10% total portfolio risk
    stop_loss_pct: float = 0.50        # 50% stop loss
    profit_target_pct: float = 0.25    # 25% profit target
```

## 📈 Sample Output

```
==================================================
LIVE MARKET ANALYSIS
==================================================
Current SPX Price: $4,567.89
Trading Signal: BUY
RSI: 45.23
MACD: 12.45
VIX Level: 18.76
Price vs 20-day MA: 2.34%

Recommendation:
Consider buying call options | Low VIX suggests low volatility - consider longer-term trades

==================================================
BACKTEST RESULTS (Last 90 Days)
==================================================
Total Trades: 15
Win Rate: 67%
Total P&L: $8,450.00
Return: 8.45%
Final Capital: $108,450.00
```

## 🔍 Key Components

### `SPXOptionsBot` Class
- Main bot controller with data fetching and analysis
- Backtesting engine with historical performance metrics
- Live market analysis and recommendation generation

### `OptionsPosition` Class
- Tracks individual options positions
- Calculates P&L and position status
- Manages entry and exit data

### `TradingStrategy` Class
- Defines risk parameters and trading rules
- Configurable strategy parameters
- Risk management calculations

## ⚠️ Risk Disclaimer

This software is for educational and research purposes only. Trading options involves substantial risk and is not suitable for all investors. Past performance does not guarantee future results. Always consult with a qualified financial advisor before making investment decisions.

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

Created by [olaitanojo](https://github.com/olaitanojo)

---

⭐ **Star this repository if you find it helpful!**
