"""
Data models for the trading bot
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class TradeStatus(str, Enum):
    """Trade status enumeration"""
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class TradeType(str, Enum):
    """Trade type enumeration"""
    LONG = "long"
    SHORT = "short"

class TradingMode(str, Enum):
    """Trading mode enumeration"""
    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"

class Trade(Base):
    """Trade model for database storage"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    trade_type = Column(SQLEnum(TradeType), nullable=False)
    status = Column(SQLEnum(TradeStatus), nullable=False, default=TradeStatus.OPEN)
    trading_mode = Column(SQLEnum(TradingMode), nullable=False)
    
    # Entry details
    entry_price = Column(Float, nullable=False)
    entry_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    quantity = Column(Float, nullable=False)
    
    # Exit details
    exit_price = Column(Float, nullable=True)
    exit_time = Column(DateTime, nullable=True)
    
    # Risk management
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    
    # P&L
    pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)
    
    # Fees
    entry_fee = Column(Float, default=0.0)
    exit_fee = Column(Float, default=0.0)
    
    # Strategy signals
    ema_fast = Column(Float, nullable=True)
    ema_slow = Column(Float, nullable=True)
    adx = Column(Float, nullable=True)
    rsi = Column(Float, nullable=True)
    
    # Additional metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Signal(Base):
    """Trading signal model"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    signal_type = Column(SQLEnum(TradeType), nullable=False)
    strength = Column(Float, nullable=False)  # Signal strength 0-100
    
    # Technical indicators
    ema_fast = Column(Float, nullable=False)
    ema_slow = Column(Float, nullable=False)
    adx = Column(Float, nullable=False)
    rsi = Column(Float, nullable=False)
    volume_ratio = Column(Float, nullable=False)
    
    # Price data
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    # AI analysis
    ai_analysis = Column(Text, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class Portfolio(Base):
    """Portfolio tracking model"""
    __tablename__ = "portfolio"
    
    id = Column(Integer, primary_key=True, index=True)
    trading_mode = Column(SQLEnum(TradingMode), nullable=False)
    
    # Balance tracking
    total_balance = Column(Float, nullable=False)
    available_balance = Column(Float, nullable=False)
    used_margin = Column(Float, default=0.0)
    
    # Performance metrics
    total_pnl = Column(Float, default=0.0)
    total_pnl_percent = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    
    # Risk metrics
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, nullable=True)
    
    # Timestamps
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic models for API
class TradeCreate(BaseModel):
    symbol: str
    trade_type: TradeType
    trading_mode: TradingMode
    entry_price: float
    quantity: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class TradeResponse(BaseModel):
    id: int
    symbol: str
    trade_type: TradeType
    status: TradeStatus
    trading_mode: TradingMode
    entry_price: float
    entry_time: datetime
    quantity: float
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    
    class Config:
        from_attributes = True

class SignalCreate(BaseModel):
    symbol: str
    timeframe: str
    signal_type: TradeType
    strength: float
    ema_fast: float
    ema_slow: float
    adx: float
    rsi: float
    volume_ratio: float
    price: float
    volume: float
    ai_analysis: Optional[str] = None
    ai_confidence: Optional[float] = None

class PortfolioResponse(BaseModel):
    trading_mode: TradingMode
    total_balance: float
    available_balance: float
    used_margin: float
    total_pnl: float
    total_pnl_percent: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    max_drawdown: float
    
    class Config:
        from_attributes = True
