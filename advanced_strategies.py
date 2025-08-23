#!/usr/bin/env python3
"""
Advanced Trading Strategies for SPX Options
Enhanced strategies with machine learning predictions and advanced indicators.

Author: olaitanojo
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import talib
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MLPrediction:
    """ML prediction result"""
    signal: int  # -1, 0, 1
    probability: float
    confidence: float
    feature_importance: Dict[str, float]

class AdvancedIndicators:
    """Advanced technical indicators using TA-Lib"""
    
    @staticmethod
    def calculate_all_indicators(data: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive technical indicators"""
        df = data.copy()
        
        # Price-based indicators
        df['SMA_10'] = talib.SMA(df['Close'], 10)
        df['SMA_20'] = talib.SMA(df['Close'], 20)
        df['SMA_50'] = talib.SMA(df['Close'], 50)
        df['SMA_200'] = talib.SMA(df['Close'], 200)
        
        df['EMA_12'] = talib.EMA(df['Close'], 12)
        df['EMA_26'] = talib.EMA(df['Close'], 26)
        df['EMA_50'] = talib.EMA(df['Close'], 50)
        
        # MACD family
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = talib.MACD(df['Close'])
        
        # RSI family
        df['RSI_14'] = talib.RSI(df['Close'], 14)
        df['RSI_21'] = talib.RSI(df['Close'], 21)
        
        # Stochastic
        df['STOCH_K'], df['STOCH_D'] = talib.STOCH(df['High'], df['Low'], df['Close'])
        
        # Williams %R
        df['WILLR'] = talib.WILLR(df['High'], df['Low'], df['Close'])
        
        # Commodity Channel Index
        df['CCI'] = talib.CCI(df['High'], df['Low'], df['Close'])
        
        # Bollinger Bands
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = talib.BBANDS(df['Close'])
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # Average True Range
        df['ATR'] = talib.ATR(df['High'], df['Low'], df['Close'])
        
        # Parabolic SAR
        df['SAR'] = talib.SAR(df['High'], df['Low'])
        
        # Average Directional Index
        df['ADX'] = talib.ADX(df['High'], df['Low'], df['Close'])
        df['PLUS_DI'] = talib.PLUS_DI(df['High'], df['Low'], df['Close'])
        df['MINUS_DI'] = talib.MINUS_DI(df['High'], df['Low'], df['Close'])
        
        # Money Flow Index
        df['MFI'] = talib.MFI(df['High'], df['Low'], df['Close'], df['Volume'])
        
        # On-Balance Volume
        df['OBV'] = talib.OBV(df['Close'], df['Volume'])
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Price momentum
        df['Momentum'] = talib.MOM(df['Close'], 10)
        df['Rate_of_Change'] = talib.ROC(df['Close'], 10)
        
        # Volatility
        df['Volatility'] = df['Close'].pct_change().rolling(20).std() * np.sqrt(252)
        
        return df

class MLEnhancedStrategy:
    """Machine Learning enhanced trading strategy"""
    
    def __init__(self, strategy_name: str = "ML_Enhanced"):
        self.strategy_name = strategy_name
        self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = None
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML model"""
        df = AdvancedIndicators.calculate_all_indicators(data)
        
        # Select features for ML model
        feature_cols = [
            'RSI_14', 'RSI_21', 'MACD', 'MACD_Signal', 'MACD_Hist',
            'STOCH_K', 'STOCH_D', 'WILLR', 'CCI', 'BB_Position', 'BB_Width',
            'ATR', 'ADX', 'PLUS_DI', 'MINUS_DI', 'MFI', 'Volume_Ratio',
            'Momentum', 'Rate_of_Change', 'Volatility'
        ]
        
        # Add price ratios
        df['Price_SMA20_Ratio'] = df['Close'] / df['SMA_20']
        df['Price_SMA50_Ratio'] = df['Close'] / df['SMA_50']
        df['SMA20_SMA50_Ratio'] = df['SMA_20'] / df['SMA_50']
        
        feature_cols.extend(['Price_SMA20_Ratio', 'Price_SMA50_Ratio', 'SMA20_SMA50_Ratio'])
        
        # Add lagged features
        for col in ['RSI_14', 'MACD', 'Volume_Ratio']:
            df[f'{col}_Lag1'] = df[col].shift(1)
            df[f'{col}_Lag2'] = df[col].shift(2)
            feature_cols.extend([f'{col}_Lag1', f'{col}_Lag2'])
        
        self.feature_columns = feature_cols
        return df[feature_cols].dropna()
    
    def create_target(self, data: pd.DataFrame, lookahead: int = 5) -> pd.Series:
        """Create target variable (future returns)"""
        future_returns = data['Close'].shift(-lookahead) / data['Close'] - 1
        
        # Convert to classification labels
        targets = pd.Series(0, index=data.index)  # Hold
        targets[future_returns > 0.005] = 1      # Buy (>0.5% return)
        targets[future_returns < -0.005] = -1    # Sell (<-0.5% return)
        
        return targets
    
    def train_model(self, data: pd.DataFrame, test_size: float = 0.2) -> Dict:
        """Train the ML model"""
        # Prepare features and target
        features_df = self.prepare_features(data)
        targets = self.create_target(data)
        
        # Align features and targets
        common_index = features_df.index.intersection(targets.index)
        X = features_df.loc[common_index]
        y = targets.loc[common_index]
        
        # Remove hold signals for training (focus on buy/sell)
        mask = y != 0
        X = X[mask]
        y = y[mask]
        
        if len(X) < 100:
            return {'success': False, 'message': 'Insufficient training data'}
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Feature importance
        feature_importance = dict(zip(
            self.feature_columns,
            self.model.feature_importances_
        ))
        
        return {
            'success': True,
            'accuracy': accuracy,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'feature_importance': feature_importance,
            'classification_report': classification_report(y_test, y_pred)
        }
    
    def predict_signal(self, data: pd.DataFrame) -> MLPrediction:
        """Predict trading signal using ML model"""
        if not self.is_trained:
            return MLPrediction(0, 0.0, 0.0, {})
        
        features_df = self.prepare_features(data)
        
        if features_df.empty:
            return MLPrediction(0, 0.0, 0.0, {})
        
        # Get latest features
        latest_features = features_df.iloc[-1:].values
        latest_features_scaled = self.scaler.transform(latest_features)
        
        # Make prediction
        prediction = self.model.predict(latest_features_scaled)[0]
        probabilities = self.model.predict_proba(latest_features_scaled)[0]
        
        # Calculate confidence (max probability)
        confidence = max(probabilities)
        probability = probabilities[1] if len(probabilities) > 2 else probabilities[0]
        
        # Feature importance for this prediction
        feature_importance = dict(zip(
            self.feature_columns,
            self.model.feature_importances_
        ))
        
        return MLPrediction(
            signal=int(prediction),
            probability=probability,
            confidence=confidence,
            feature_importance=feature_importance
        )

class AdvancedTradingStrategies:
    """Collection of advanced trading strategies"""
    
    def __init__(self):
        self.ml_strategy = MLEnhancedStrategy()
    
    def mean_reversion_strategy(self, data: pd.DataFrame) -> pd.Series:
        """Advanced mean reversion strategy"""
        df = AdvancedIndicators.calculate_all_indicators(data)
        signals = pd.Series(0, index=df.index)
        
        # Conditions for mean reversion
        oversold = (df['RSI_14'] < 30) & (df['BB_Position'] < 0.05) & (df['WILLR'] < -80)
        overbought = (df['RSI_14'] > 70) & (df['BB_Position'] > 0.95) & (df['WILLR'] > -20)
        
        # Additional confirmation
        volume_spike = df['Volume_Ratio'] > 1.5
        low_volatility = df['BB_Width'] < df['BB_Width'].rolling(50).mean()
        
        signals[oversold & volume_spike] = 1   # Buy
        signals[overbought & volume_spike] = -1 # Sell
        
        return signals
    
    def momentum_breakout_strategy(self, data: pd.DataFrame) -> pd.Series:
        """Momentum breakout strategy with multiple confirmations"""
        df = AdvancedIndicators.calculate_all_indicators(data)
        signals = pd.Series(0, index=df.index)
        
        # Trend conditions
        uptrend = (df['SMA_20'] > df['SMA_50']) & (df['Close'] > df['SMA_20'])
        downtrend = (df['SMA_20'] < df['SMA_50']) & (df['Close'] < df['SMA_20'])
        
        # Momentum conditions
        strong_momentum = df['ADX'] > 25
        bullish_momentum = (df['PLUS_DI'] > df['MINUS_DI']) & (df['MACD'] > df['MACD_Signal'])
        bearish_momentum = (df['PLUS_DI'] < df['MINUS_DI']) & (df['MACD'] < df['MACD_Signal'])
        
        # Volume confirmation
        volume_confirm = df['Volume_Ratio'] > 1.2
        
        # Buy signals
        buy_conditions = uptrend & strong_momentum & bullish_momentum & volume_confirm
        signals[buy_conditions] = 1
        
        # Sell signals
        sell_conditions = downtrend & strong_momentum & bearish_momentum & volume_confirm
        signals[sell_conditions] = -1
        
        return signals
    
    def volatility_breakout_strategy(self, data: pd.DataFrame) -> pd.Series:
        """Volatility breakout strategy"""
        df = AdvancedIndicators.calculate_all_indicators(data)
        signals = pd.Series(0, index=df.index)
        
        # Volatility conditions
        low_vol_period = df['ATR'] < df['ATR'].rolling(20).mean() * 0.8
        vol_expansion = df['BB_Width'] > df['BB_Width'].shift(1) * 1.1
        
        # Price breakout conditions
        upper_break = df['Close'] > df['BB_Upper']
        lower_break = df['Close'] < df['BB_Lower']
        
        # Volume confirmation
        volume_breakout = df['Volume_Ratio'] > 1.5
        
        # Generate signals
        buy_signal = upper_break & vol_expansion & volume_breakout & (df['RSI_14'] < 80)
        sell_signal = lower_break & vol_expansion & volume_breakout & (df['RSI_14'] > 20)
        
        signals[buy_signal] = 1
        signals[sell_signal] = -1
        
        return signals
    
    def ml_ensemble_strategy(self, data: pd.DataFrame) -> Tuple[pd.Series, Dict]:
        """ML ensemble strategy combining multiple signals"""
        if not self.ml_strategy.is_trained:
            training_result = self.ml_strategy.train_model(data)
            if not training_result['success']:
                return pd.Series(0, index=data.index), training_result
        
        # Get individual strategy signals
        mean_rev_signals = self.mean_reversion_strategy(data)
        momentum_signals = self.momentum_breakout_strategy(data)
        vol_signals = self.volatility_breakout_strategy(data)
        
        # Get ML prediction for latest data point
        ml_prediction = self.ml_strategy.predict_signal(data)
        
        # Combine signals using ensemble approach
        ensemble_signals = pd.Series(0, index=data.index)
        
        for i in range(len(data)):
            if i < 50:  # Need enough data for indicators
                continue
                
            signal_votes = [
                mean_rev_signals.iloc[i],
                momentum_signals.iloc[i],
                vol_signals.iloc[i]
            ]
            
            # Add ML signal with higher weight for recent data
            if i == len(data) - 1:  # Latest data point
                signal_votes.extend([ml_prediction.signal] * 2)  # Double weight for ML
            
            # Majority vote
            vote_sum = sum(signal_votes)
            if vote_sum >= 2:
                ensemble_signals.iloc[i] = 1
            elif vote_sum <= -2:
                ensemble_signals.iloc[i] = -1
        
        strategy_info = {
            'ml_prediction': ml_prediction,
            'signal_components': {
                'mean_reversion': mean_rev_signals.iloc[-1] if len(mean_rev_signals) > 0 else 0,
                'momentum': momentum_signals.iloc[-1] if len(momentum_signals) > 0 else 0,
                'volatility': vol_signals.iloc[-1] if len(vol_signals) > 0 else 0,
                'ml_signal': ml_prediction.signal
            }
        }
        
        return ensemble_signals, strategy_info

def main():
    """Test advanced strategies"""
    import yfinance as yf
    
    # Fetch test data
    data = yf.download("SPY", period="2y")
    
    # Initialize advanced strategies
    adv_strategies = AdvancedTradingStrategies()
    
    print("🚀 Testing Advanced Trading Strategies")
    print("=" * 50)
    
    # Test individual strategies
    print("\n📊 Mean Reversion Strategy:")
    mean_rev_signals = adv_strategies.mean_reversion_strategy(data)
    print(f"Total signals: {len(mean_rev_signals[mean_rev_signals != 0])}")
    print(f"Buy signals: {len(mean_rev_signals[mean_rev_signals == 1])}")
    print(f"Sell signals: {len(mean_rev_signals[mean_rev_signals == -1])}")
    
    print("\n📈 Momentum Breakout Strategy:")
    momentum_signals = adv_strategies.momentum_breakout_strategy(data)
    print(f"Total signals: {len(momentum_signals[momentum_signals != 0])}")
    print(f"Buy signals: {len(momentum_signals[momentum_signals == 1])}")
    print(f"Sell signals: {len(momentum_signals[momentum_signals == -1])}")
    
    print("\n⚡ ML Ensemble Strategy:")
    ensemble_signals, strategy_info = adv_strategies.ml_ensemble_strategy(data)
    print(f"Total signals: {len(ensemble_signals[ensemble_signals != 0])}")
    print(f"Buy signals: {len(ensemble_signals[ensemble_signals == 1])}")
    print(f"Sell signals: {len(ensemble_signals[ensemble_signals == -1])}")
    
    ml_pred = strategy_info['ml_prediction']
    print(f"\nLatest ML Prediction:")
    print(f"Signal: {ml_pred.signal}")
    print(f"Confidence: {ml_pred.confidence:.3f}")
    
    print(f"\nSignal Components:")
    for component, signal in strategy_info['signal_components'].items():
        print(f"{component}: {signal}")

if __name__ == "__main__":
    main()
