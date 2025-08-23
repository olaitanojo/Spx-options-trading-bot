# 🚀 SPX Options Trading Bot

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![ML](https://img.shields.io/badge/ML-XGBoost%20%7C%20Ensemble-orange.svg)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **A sophisticated, production-ready automated trading system for SPX options featuring advanced ML strategies, comprehensive backtesting, risk management, and real-time execution with institutional-grade monitoring.**

## 🎆 Advanced Features

### 🤖 Machine Learning Strategies (`advanced_strategies.py`)
- **Gradient Boosting Classifier**: ML-enhanced signal prediction with feature importance
- **Ensemble Voting**: Combines multiple strategies (mean reversion, momentum breakout, volatility)
- **Advanced Technical Indicators**: 30+ TA-Lib indicators for sophisticated analysis
- **Feature Engineering**: Comprehensive feature set including volume, volatility, and momentum
- **Model Training**: Real-time model training with backtesting validation
- **Confidence Scoring**: Prediction confidence levels for risk-adjusted position sizing

### 🏢 Production Deployment (Docker)
- **Multi-Service Architecture**: SPX bot, Redis, PostgreSQL, monitoring stack
- **Grafana Dashboards**: Real-time trading performance visualization
- **Prometheus Monitoring**: System metrics, alerts, and health checks
- **Redis Caching**: High-performance data caching and session management
- **PostgreSQL Storage**: Robust data persistence for trades and analytics
- **Health Checks**: Automated service health monitoring and restart policies

### 🛡️ Advanced Risk Management
- **Dynamic Position Sizing**: ML-based position sizing based on market conditions
- **Portfolio Heat Management**: Real-time portfolio risk monitoring
- **Volatility-Adjusted Stops**: Dynamic stop losses based on market volatility
- **Correlation Analysis**: Position correlation tracking for risk diversification
- **Drawdown Protection**: Automatic position reduction during adverse periods

### 📊 Analytics & Monitoring
- **Real-time P&L Tracking**: Live position monitoring with unrealized P&L
- **Performance Attribution**: Trade analysis and performance breakdown
- **Risk Metrics**: VaR, Sharpe ratio, maximum drawdown calculation
- **Market Regime Detection**: Trend vs. range-bound market identification
- **Backtesting Engine**: Walk-forward analysis with out-of-sample testing

## 🎯 Core Features

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

### 🐳 Docker Deployment (Production)

For production deployment with full monitoring stack:

1. **Navigate to deployment directory**
   ```bash
   cd deployment
   ```

2. **Start the full stack**
   ```bash
   docker-compose up -d
   ```

This starts:
- **SPX Trading Bot** (main application)
- **Redis** (data caching)
- **PostgreSQL** (data persistence)
- **Grafana** (dashboards at http://localhost:3000)
- **Prometheus** (metrics collection)

3. **View services status**
   ```bash
   docker-compose ps
   ```

4. **View logs**
   ```bash
   docker-compose logs -f spx-bot
   ```

## 🤖 Advanced ML Usage

### Running ML-Enhanced Strategies

```python
from advanced_strategies import MLTradingStrategy, AdvancedStrategyEnsemble

# Initialize ML strategy
ml_strategy = MLTradingStrategy()

# Fetch and prepare training data
data = ml_strategy.get_market_data("^SPX", period="2y")
features = ml_strategy.calculate_technical_indicators(data)

# Train ML model
ml_strategy.train_model(features)

# Generate ML predictions
predictions = ml_strategy.predict_signals(features.tail(1))
print(f"ML Signal: {predictions['signal']} (Confidence: {predictions['confidence']:.2f})")
```

### Ensemble Strategy Backtesting

```python
# Initialize ensemble of strategies
ensemble = AdvancedStrategyEnsemble()
ensemble.add_strategy('mean_reversion', weight=0.3)
ensemble.add_strategy('momentum_breakout', weight=0.4)
ensemble.add_strategy('volatility_breakout', weight=0.3)

# Backtest ensemble
results = ensemble.backtest(
    start_date='2023-01-01',
    end_date='2024-01-01',
    initial_capital=100000
)

print(f"Ensemble Results:")
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.3f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
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
