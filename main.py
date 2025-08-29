#!/usr/bin/env python3
"""
SPX Options Trading Bot
A comprehensive automated trading system for SPX options with backtesting,
risk management, and real-time execution capabilities.

Author: olaitanojo
"""

import logging
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("trading_bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class OptionType(Enum):
    CALL = "call"
    PUT = "put"


class TradeSignal(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class OptionsPosition:
    """Represents an options position"""

    symbol: str
    option_type: OptionType
    strike: float
    expiration: str
    quantity: int
    entry_price: float
    entry_date: datetime
    exit_price: Optional[float] = None
    exit_date: Optional[datetime] = None

    @property
    def is_open(self) -> bool:
        return self.exit_price is None

    @property
    def pnl(self) -> float:
        if self.exit_price is None:
            return 0.0
        return (self.exit_price - self.entry_price) * self.quantity * 100


@dataclass
class TradingStrategy:
    """Base class for trading strategies"""

    name: str
    max_risk_per_trade: float = 0.02  # 2% of portfolio
    max_portfolio_risk: float = 0.10  # 10% total portfolio risk
    stop_loss_pct: float = 0.50  # 50% stop loss
    profit_target_pct: float = 0.25  # 25% profit target


class SPXOptionsBot:
    """
    Enhanced SPX Options Trading Bot with backtesting and real-time capabilities
    """

    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions: List[OptionsPosition] = []
        self.trade_history: List[Dict] = []
        self.spx_data = None
        self.vix_data = None

    def fetch_market_data(self, period: str = "1y") -> None:
        """Fetch SPX and VIX data for analysis"""
        try:
            logger.info("Fetching market data...")

            # Fetch SPX data
            spx = yf.Ticker("^SPX")
            self.spx_data = spx.history(period=period)

            # Fetch VIX data for volatility analysis
            vix = yf.Ticker("^VIX")
            self.vix_data = vix.history(period=period)

            if self.spx_data is not None:
                logger.info(f"Fetched {len(self.spx_data)} SPX data points")
            if self.vix_data is not None:
                logger.info(f"Fetched {len(self.vix_data)} VIX data points")

        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            raise

    def calculate_technical_indicators(self) -> pd.DataFrame:
        """Calculate technical indicators for trading signals"""
        if self.spx_data is None:
            raise ValueError("Market data not loaded. Call fetch_market_data() first.")

        df = self.spx_data.copy()

        # Moving averages
        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df["SMA_50"] = df["Close"].rolling(window=50).mean()
        df["EMA_12"] = df["Close"].ewm(span=12).mean()
        df["EMA_26"] = df["Close"].ewm(span=26).mean()

        # MACD
        df["MACD"] = df["EMA_12"] - df["EMA_26"]
        df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()
        df["MACD_Histogram"] = df["MACD"] - df["MACD_Signal"]

        # RSI
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        df["BB_Middle"] = df["Close"].rolling(window=20).mean()
        bb_std = df["Close"].rolling(window=20).std()
        df["BB_Upper"] = df["BB_Middle"] + (bb_std * 2)
        df["BB_Lower"] = df["BB_Middle"] - (bb_std * 2)

        # Add VIX data
        if self.vix_data is not None:
            df["VIX"] = self.vix_data["Close"]

        return df

    def generate_trading_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate trading signals based on technical analysis"""
        signals = pd.Series(index=data.index, dtype=object)
        signals[:] = TradeSignal.HOLD

        for i in range(50, len(data)):  # Start after moving averages are calculated
            current = data.iloc[i]
            prev = data.iloc[i - 1]

            # Bullish signals
            bullish_conditions = [
                current["Close"] > current["SMA_20"],  # Above 20-day MA
                current["MACD"] > current["MACD_Signal"],  # MACD bullish
                current["RSI"] > 30 and current["RSI"] < 70,  # RSI not extreme
                current["Close"] > prev["Close"],  # Price momentum
            ]

            # Bearish signals
            bearish_conditions = [
                current["Close"] < current["SMA_20"],  # Below 20-day MA
                current["MACD"] < current["MACD_Signal"],  # MACD bearish
                current["RSI"] > 30 and current["RSI"] < 70,  # RSI not extreme
                current["Close"] < prev["Close"],  # Price momentum
            ]

            if sum(bullish_conditions) >= 3:
                signals.iloc[i] = TradeSignal.BUY
            elif sum(bearish_conditions) >= 3:
                signals.iloc[i] = TradeSignal.SELL

        return signals

    def calculate_position_size(
        self, strategy: TradingStrategy, option_price: float
    ) -> int:
        """Calculate position size based on risk management"""
        risk_amount = self.current_capital * strategy.max_risk_per_trade
        contract_value = option_price * 100  # Options are 100 shares per contract
        position_size = int(risk_amount / contract_value)
        return max(1, position_size)  # Minimum 1 contract

    def backtest_strategy(self, start_date: str, end_date: str) -> Dict:
        """Backtest the trading strategy"""
        logger.info(f"Starting backtest from {start_date} to {end_date}")

        # Fetch historical data
        self.fetch_market_data(period="2y")
        data_with_indicators = self.calculate_technical_indicators()
        signals = self.generate_trading_signals(data_with_indicators)

        # Filter data for backtest period
        mask = (data_with_indicators.index >= start_date) & (
            data_with_indicators.index <= end_date
        )
        backtest_data = data_with_indicators[mask]
        backtest_signals = signals[mask]

        strategy = TradingStrategy("SPX Mean Reversion")
        backtest_positions = []

        for date, signal in backtest_signals.items():
            if signal == TradeSignal.BUY:
                # Simulate buying call options
                current_price = backtest_data.loc[date, "Close"]
                strike = current_price * 1.02  # Slightly OTM
                option_price = current_price * 0.03  # Simplified option pricing

                position_size = self.calculate_position_size(strategy, option_price)

                position = OptionsPosition(
                    symbol="SPX",
                    option_type=OptionType.CALL,
                    strike=strike,
                    expiration=(date + timedelta(days=30)).strftime("%Y-%m-%d"),
                    quantity=position_size,
                    entry_price=option_price,
                    entry_date=date,
                )
                backtest_positions.append(position)

            elif signal == TradeSignal.SELL:
                # Simulate buying put options
                current_price = backtest_data.loc[date, "Close"]
                strike = current_price * 0.98  # Slightly OTM
                option_price = current_price * 0.03  # Simplified option pricing

                position_size = self.calculate_position_size(strategy, option_price)

                position = OptionsPosition(
                    symbol="SPX",
                    option_type=OptionType.PUT,
                    strike=strike,
                    expiration=(date + timedelta(days=30)).strftime("%Y-%m-%d"),
                    quantity=position_size,
                    entry_price=option_price,
                    entry_date=date,
                )
                backtest_positions.append(position)

        # Calculate backtest results
        total_trades = len(backtest_positions)
        total_pnl = sum([pos.pnl for pos in backtest_positions if not pos.is_open])
        win_rate = len([pos for pos in backtest_positions if pos.pnl > 0]) / max(
            total_trades, 1
        )

        results = {
            "total_trades": total_trades,
            "total_pnl": total_pnl,
            "win_rate": win_rate,
            "final_capital": self.initial_capital + total_pnl,
            "return_pct": (total_pnl / self.initial_capital) * 100,
            "positions": backtest_positions,
        }

        logger.info(
            f"Backtest completed: {total_trades} trades, {win_rate:.2%} win rate, {results['return_pct']:.2f}% return"
        )
        return results

    def run_live_analysis(self) -> Dict:
        """Run live market analysis and generate current recommendations"""
        logger.info("Running live market analysis...")

        # Fetch current market data
        self.fetch_market_data(period="3mo")
        data_with_indicators = self.calculate_technical_indicators()
        signals = self.generate_trading_signals(data_with_indicators)

        # Get current market conditions
        current_data = data_with_indicators.iloc[-1]
        current_signal = signals.iloc[-1]

        analysis = {
            "current_price": current_data["Close"],
            "signal": current_signal.value,
            "rsi": current_data["RSI"],
            "macd": current_data["MACD"],
            "vix_level": current_data.get("VIX", None),
            "price_vs_sma20": (
                (current_data["Close"] - current_data["SMA_20"])
                / current_data["SMA_20"]
            )
            * 100,
            "recommendation": self._generate_recommendation(
                current_data, current_signal
            ),
        }

        logger.info(
            f"Current signal: {analysis['signal']}, Price: ${analysis['current_price']:.2f}"
        )
        return analysis

    def _generate_recommendation(
        self, current_data: pd.Series, signal: TradeSignal
    ) -> str:
        """Generate trading recommendation based on current analysis"""
        recommendations = []

        if signal == TradeSignal.BUY:
            recommendations.append("Consider buying call options")
            if current_data["RSI"] < 40:
                recommendations.append(
                    "RSI indicates oversold conditions - good for calls"
                )
        elif signal == TradeSignal.SELL:
            recommendations.append("Consider buying put options")
            if current_data["RSI"] > 60:
                recommendations.append(
                    "RSI indicates overbought conditions - good for puts"
                )
        else:
            recommendations.append("No clear signal - consider staying in cash")

        vix_level = current_data.get("VIX", 0)
        if vix_level > 25:
            recommendations.append(
                "High VIX suggests elevated volatility - consider shorter-term trades"
            )
        elif vix_level < 15:
            recommendations.append(
                "Low VIX suggests low volatility - consider longer-term trades"
            )

        return " | ".join(recommendations)


def main():
    """Main function to run the SPX Options Trading Bot"""
    logger.info("Starting SPX Options Trading Bot")

    # Initialize bot
    bot = SPXOptionsBot(initial_capital=100000)

    try:
        # Run live analysis
        live_analysis = bot.run_live_analysis()
        print("\n" + "=" * 50)
        print("LIVE MARKET ANALYSIS")
        print("=" * 50)
        print(f"Current SPX Price: ${live_analysis['current_price']:.2f}")
        print(f"Trading Signal: {live_analysis['signal'].upper()}")
        print(f"RSI: {live_analysis['rsi']:.2f}")
        print(f"MACD: {live_analysis['macd']:.2f}")
        if live_analysis["vix_level"]:
            print(f"VIX Level: {live_analysis['vix_level']:.2f}")
        print(f"Price vs 20-day MA: {live_analysis['price_vs_sma20']:.2f}%")
        print("\nRecommendation:")
        print(live_analysis["recommendation"])

        # Run backtest
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        backtest_results = bot.backtest_strategy(start_date, end_date)
        print("\n" + "=" * 50)
        print("BACKTEST RESULTS (Last 90 Days)")
        print("=" * 50)
        print(f"Total Trades: {backtest_results['total_trades']}")
        print(f"Win Rate: {backtest_results['win_rate']:.2%}")
        print(f"Total P&L: ${backtest_results['total_pnl']:.2f}")
        print(f"Return: {backtest_results['return_pct']:.2f}%")
        print(f"Final Capital: ${backtest_results['final_capital']:.2f}")

    except Exception as e:
        logger.error(f"Error running trading bot: {e}")
        return 1

    logger.info("SPX Options Trading Bot completed successfully")
    return 0


if __name__ == "__main__":
    exit(main())
