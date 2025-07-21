"""
Core configuration module for the trading bot.
Handles environment variables and application settings.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TradingConfig(BaseSettings):
    """Trading configuration settings"""
    
    # Binance API Configuration
    binance_api_key: str = Field(..., env="BINANCE_API_KEY")
    binance_secret_key: str = Field(..., env="BINANCE_SECRET_KEY")
    binance_testnet: bool = Field(True, env="BINANCE_TESTNET")
    
    # Google Gemini API Configuration
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    
    # Trading Configuration
    default_symbol: str = Field("BTCUSDT", env="DEFAULT_SYMBOL")
    default_timeframe: str = Field("15m", env="DEFAULT_TIMEFRAME")
    position_size_usd: float = Field(100.0, env="POSITION_SIZE_USD")
    max_position_size_usd: float = Field(500.0, env="MAX_POSITION_SIZE_USD")
    risk_per_trade_percent: float = Field(1.5, env="RISK_PER_TRADE_PERCENT")
    max_trades_per_day: int = Field(3, env="MAX_TRADES_PER_DAY")
    stop_loss_percent: float = Field(2.0, env="STOP_LOSS_PERCENT")
    take_profit_percent: float = Field(3.0, env="TAKE_PROFIT_PERCENT")
    
    # Database Configuration
    database_url: str = Field("sqlite:///trading_bot.db", env="DATABASE_URL")
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/trading_bot.log", env="LOG_FILE")
    
    # Telegram Notifications (Optional)
    telegram_bot_token: Optional[str] = Field(None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(None, env="TELEGRAM_CHAT_ID")
    
    # Paper Trading
    paper_trading_initial_balance: float = Field(10000.0, env="PAPER_TRADING_INITIAL_BALANCE")
    
    # Backtesting
    backtest_start_date: str = Field("2023-01-01", env="BACKTEST_START_DATE")
    backtest_end_date: str = Field("2024-01-01", env="BACKTEST_END_DATE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

class StrategyConfig:
    """EMA + ADX Strategy Configuration"""
    
    # EMA Parameters
    EMA_FAST = 12
    EMA_SLOW = 26
    EMA_SIGNAL = 9
    
    # ADX Parameters
    ADX_PERIOD = 14
    ADX_THRESHOLD = 25
    
    # RSI Parameters
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    
    # Volume Parameters
    VOLUME_MA_PERIOD = 20
    VOLUME_THRESHOLD = 1.5

# Global configuration instance
config = TradingConfig()
strategy_config = StrategyConfig()
