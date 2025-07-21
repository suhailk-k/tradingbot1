"""
Technical analysis strategy implementation.
EMA + ADX + RSI strategy with volume confirmation.
"""

import pandas as pd
import numpy as np
import ta
from typing import Dict, Optional, Tuple
import logging

from config import strategy_config
from models import TradeType

logger = logging.getLogger(__name__)

class TradingStrategy:
    """EMA + ADX + RSI trading strategy"""
    
    def __init__(self):
        """Initialize strategy with configuration"""
        self.ema_fast = strategy_config.EMA_FAST
        self.ema_slow = strategy_config.EMA_SLOW
        self.ema_signal = strategy_config.EMA_SIGNAL
        self.adx_period = strategy_config.ADX_PERIOD
        self.adx_threshold = strategy_config.ADX_THRESHOLD
        self.rsi_period = strategy_config.RSI_PERIOD
        self.rsi_overbought = strategy_config.RSI_OVERBOUGHT
        self.rsi_oversold = strategy_config.RSI_OVERSOLD
        self.volume_ma_period = strategy_config.VOLUME_MA_PERIOD
        self.volume_threshold = strategy_config.VOLUME_THRESHOLD
        
        logger.info("Trading strategy initialized with EMA + ADX + RSI")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        if len(df) < max(self.ema_slow, self.adx_period, self.rsi_period, self.volume_ma_period):
            raise ValueError("Insufficient data for indicator calculation")
        
        # Make a copy to avoid modifying original data
        data = df.copy()
        
        # EMA indicators
        data['ema_fast'] = ta.trend.EMAIndicator(close=data['close'], window=self.ema_fast).ema_indicator()
        data['ema_slow'] = ta.trend.EMAIndicator(close=data['close'], window=self.ema_slow).ema_indicator()
        
        # MACD for signal confirmation
        macd = ta.trend.MACD(close=data['close'], window_fast=self.ema_fast, window_slow=self.ema_slow, window_sign=self.ema_signal)
        data['macd'] = macd.macd()
        data['macd_signal'] = macd.macd_signal()
        data['macd_histogram'] = macd.macd_diff()
        
        # ADX for trend strength
        adx = ta.trend.ADXIndicator(high=data['high'], low=data['low'], close=data['close'], window=self.adx_period)
        data['adx'] = adx.adx()
        data['di_plus'] = adx.adx_pos()
        data['di_minus'] = adx.adx_neg()
        
        # RSI for momentum
        data['rsi'] = ta.momentum.RSIIndicator(close=data['close'], window=self.rsi_period).rsi()
        
        # Volume analysis
        data['volume_ma'] = data['volume'].rolling(window=self.volume_ma_period).mean()
        data['volume_ratio'] = data['volume'] / data['volume_ma']
        
        # Support and Resistance levels
        data['resistance'] = data['high'].rolling(window=20).max()
        data['support'] = data['low'].rolling(window=20).min()
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(close=data['close'], window=20, window_dev=2)
        data['bb_upper'] = bb.bollinger_hband()
        data['bb_lower'] = bb.bollinger_lband()
        data['bb_middle'] = bb.bollinger_mavg()
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['bb_middle']
        
        # Price position within Bollinger Bands
        data['bb_position'] = (data['close'] - data['bb_lower']) / (data['bb_upper'] - data['bb_lower'])
        
        # Stochastic oscillator
        stoch = ta.momentum.StochasticOscillator(high=data['high'], low=data['low'], close=data['close'])
        data['stoch_k'] = stoch.stoch()
        data['stoch_d'] = stoch.stoch_signal()
        
        # Average True Range for volatility
        data['atr'] = ta.volatility.AverageTrueRange(high=data['high'], low=data['low'], close=data['close']).average_true_range()
        
        return data
    
    def generate_signal(self, df: pd.DataFrame) -> Dict:
        """Generate trading signal based on strategy rules"""
        if len(df) < 2:
            return {'signal': 'HOLD', 'strength': 0, 'reasons': ['Insufficient data']}
        
        # Get latest values
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Initialize signal analysis
        signal_score = 0
        reasons = []
        signal_strength = 0
        
        # 1. EMA Trend Analysis
        ema_bullish = current['ema_fast'] > current['ema_slow']
        ema_crossover_bull = (current['ema_fast'] > current['ema_slow'] and 
                             previous['ema_fast'] <= previous['ema_slow'])
        ema_crossover_bear = (current['ema_fast'] < current['ema_slow'] and 
                             previous['ema_fast'] >= previous['ema_slow'])
        
        if ema_crossover_bull:
            signal_score += 25
            reasons.append("EMA bullish crossover")
        elif ema_crossover_bear:
            signal_score -= 25
            reasons.append("EMA bearish crossover")
        elif ema_bullish:
            signal_score += 10
            reasons.append("EMA bullish trend")
        else:
            signal_score -= 10
            reasons.append("EMA bearish trend")
        
        # 2. MACD Analysis
        macd_bullish = current['macd'] > current['macd_signal']
        macd_crossover_bull = (current['macd'] > current['macd_signal'] and 
                              previous['macd'] <= previous['macd_signal'])
        macd_crossover_bear = (current['macd'] < current['macd_signal'] and 
                              previous['macd'] >= previous['macd_signal'])
        
        if macd_crossover_bull:
            signal_score += 20
            reasons.append("MACD bullish crossover")
        elif macd_crossover_bear:
            signal_score -= 20
            reasons.append("MACD bearish crossover")
        elif macd_bullish:
            signal_score += 8
            reasons.append("MACD bullish")
        else:
            signal_score -= 8
            reasons.append("MACD bearish")
        
        # 3. ADX Trend Strength
        strong_trend = current['adx'] > self.adx_threshold
        trend_direction = current['di_plus'] > current['di_minus']
        
        if strong_trend:
            if trend_direction:
                signal_score += 15
                reasons.append(f"Strong uptrend (ADX: {current['adx']:.1f})")
            else:
                signal_score -= 15
                reasons.append(f"Strong downtrend (ADX: {current['adx']:.1f})")
        else:
            signal_score *= 0.7  # Reduce confidence in weak trends
            reasons.append(f"Weak trend (ADX: {current['adx']:.1f})")
        
        # 4. RSI Momentum
        rsi_oversold = current['rsi'] < self.rsi_oversold
        rsi_overbought = current['rsi'] > self.rsi_overbought
        rsi_neutral = self.rsi_oversold <= current['rsi'] <= self.rsi_overbought
        
        if rsi_oversold and signal_score > 0:
            signal_score += 15
            reasons.append(f"RSI oversold bounce ({current['rsi']:.1f})")
        elif rsi_overbought and signal_score < 0:
            signal_score -= 15
            reasons.append(f"RSI overbought reversal ({current['rsi']:.1f})")
        elif rsi_overbought and signal_score > 0:
            signal_score *= 0.5  # Reduce bullish signal strength
            reasons.append(f"RSI overbought warning ({current['rsi']:.1f})")
        elif rsi_oversold and signal_score < 0:
            signal_score *= 0.5  # Reduce bearish signal strength
            reasons.append(f"RSI oversold warning ({current['rsi']:.1f})")
        
        # 5. Volume Confirmation
        high_volume = current['volume_ratio'] > self.volume_threshold
        if high_volume:
            signal_score *= 1.2
            reasons.append(f"High volume confirmation ({current['volume_ratio']:.2f}x)")
        else:
            signal_score *= 0.8
            reasons.append(f"Low volume ({current['volume_ratio']:.2f}x)")
        
        # 6. Bollinger Bands Analysis
        bb_squeeze = current['bb_width'] < 0.1  # Tight bands indicate low volatility
        bb_breakout_up = current['close'] > current['bb_upper']
        bb_breakout_down = current['close'] < current['bb_lower']
        
        if bb_breakout_up and signal_score > 0:
            signal_score += 10
            reasons.append("Bollinger Bands upward breakout")
        elif bb_breakout_down and signal_score < 0:
            signal_score -= 10
            reasons.append("Bollinger Bands downward breakout")
        elif bb_squeeze:
            signal_score *= 0.7  # Reduce signal strength during low volatility
            reasons.append("Low volatility (BB squeeze)")
        
        # 7. Stochastic Oscillator
        stoch_oversold = current['stoch_k'] < 20 and current['stoch_d'] < 20
        stoch_overbought = current['stoch_k'] > 80 and current['stoch_d'] > 80
        stoch_bull_cross = (current['stoch_k'] > current['stoch_d'] and 
                           previous['stoch_k'] <= previous['stoch_d'])
        stoch_bear_cross = (current['stoch_k'] < current['stoch_d'] and 
                           previous['stoch_k'] >= previous['stoch_d'])
        
        if stoch_bull_cross and signal_score > 0:
            signal_score += 8
            reasons.append("Stochastic bullish crossover")
        elif stoch_bear_cross and signal_score < 0:
            signal_score -= 8
            reasons.append("Stochastic bearish crossover")
        
        # Calculate signal strength (0-100)
        signal_strength = min(abs(signal_score), 100)
        
        # Determine final signal
        if signal_score > 30:
            signal = 'BUY'
        elif signal_score < -30:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        # Calculate confidence based on multiple confirmations
        confirmation_count = sum([
            ema_bullish if signal == 'BUY' else not ema_bullish,
            macd_bullish if signal == 'BUY' else not macd_bullish,
            strong_trend,
            high_volume,
            abs(signal_score) > 50
        ])
        
        confidence = (confirmation_count / 5) * 100
        
        return {
            'signal': signal,
            'strength': signal_strength,
            'confidence': confidence,
            'score': signal_score,
            'reasons': reasons,
            'indicators': {
                'ema_fast': current['ema_fast'],
                'ema_slow': current['ema_slow'],
                'macd': current['macd'],
                'macd_signal': current['macd_signal'],
                'adx': current['adx'],
                'rsi': current['rsi'],
                'volume_ratio': current['volume_ratio'],
                'bb_position': current['bb_position'],
                'stoch_k': current['stoch_k'],
                'atr': current['atr']
            }
        }
    
    def calculate_stop_loss_take_profit(self, entry_price: float, signal: str, atr: float) -> Tuple[float, float]:
        """Calculate stop loss and take profit levels"""
        if signal == 'BUY':
            # For long positions
            stop_loss = entry_price * (1 - 0.02)  # 2% stop loss
            take_profit = entry_price * (1 + 0.03)  # 3% take profit
            
            # ATR-based adjustments
            atr_stop = entry_price - (2 * atr)
            atr_tp = entry_price + (3 * atr)
            
            # Use the more conservative option
            stop_loss = max(stop_loss, atr_stop)
            take_profit = min(take_profit, atr_tp)
            
        else:  # SELL
            # For short positions
            stop_loss = entry_price * (1 + 0.02)  # 2% stop loss
            take_profit = entry_price * (1 - 0.03)  # 3% take profit
            
            # ATR-based adjustments
            atr_stop = entry_price + (2 * atr)
            atr_tp = entry_price - (3 * atr)
            
            # Use the more conservative option
            stop_loss = min(stop_loss, atr_stop)
            take_profit = max(take_profit, atr_tp)
        
        return stop_loss, take_profit
    
    def validate_signal(self, signal_data: Dict, current_price: float) -> bool:
        """Validate if signal meets minimum requirements"""
        if signal_data['signal'] == 'HOLD':
            return False
        
        # Minimum strength requirement
        if signal_data['strength'] < 40:
            return False
        
        # Minimum confidence requirement
        if signal_data['confidence'] < 60:
            return False
        
        # Check if ADX shows strong trend
        if signal_data['indicators']['adx'] < self.adx_threshold:
            return False
        
        # Check for extreme RSI levels that might indicate reversal
        rsi = signal_data['indicators']['rsi']
        if signal_data['signal'] == 'BUY' and rsi > 75:
            return False
        if signal_data['signal'] == 'SELL' and rsi < 25:
            return False
        
        return True
    
    def get_strategy_description(self) -> str:
        """Get human-readable strategy description"""
        return f"""
        EMA + ADX + RSI Strategy Configuration:
        
        - EMA Fast: {self.ema_fast} periods
        - EMA Slow: {self.ema_slow} periods
        - ADX Period: {self.adx_period}, Threshold: {self.adx_threshold}
        - RSI Period: {self.rsi_period}, Overbought: {self.rsi_overbought}, Oversold: {self.rsi_oversold}
        - Volume MA: {self.volume_ma_period} periods, Threshold: {self.volume_threshold}x
        
        Entry Conditions:
        - BUY: EMA fast > slow, ADX > {self.adx_threshold}, RSI not overbought, high volume
        - SELL: EMA fast < slow, ADX > {self.adx_threshold}, RSI not oversold, high volume
        
        Risk Management:
        - Stop Loss: 2% or 2x ATR
        - Take Profit: 3% or 3x ATR
        - Position Size: Based on risk per trade
        """
