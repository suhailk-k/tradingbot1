"""
Database manager for the trading bot
"""
import asyncio
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import logging

from models import Base, Trade, Signal, Portfolio, TradeStatus

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database operations for the trading bot"""
    
    def __init__(self, database_url: str = "sqlite:///trading_bot.db"):
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    # Trade operations
    def save_trade(self, trade_data: Dict[str, Any]) -> Trade:
        """Save a trade to database"""
        with self.get_session() as session:
            trade = Trade(**trade_data)
            session.add(trade)
            session.flush()
            session.refresh(trade)
            return trade
    
    def get_trades(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get trades from database"""
        with self.get_session() as session:
            query = session.query(Trade)
            if symbol:
                query = query.filter(Trade.symbol == symbol)
            trades = query.order_by(Trade.timestamp.desc()).limit(limit).all()
            
            # Convert to dictionaries to avoid session issues
            trade_list = []
            for trade in trades:
                trade_dict = {
                    'id': trade.id,
                    'symbol': trade.symbol,
                    'trade_type': trade.trade_type,
                    'status': trade.status,
                    'trading_mode': trade.trading_mode,
                    'entry_price': trade.entry_price,
                    'quantity': trade.quantity,
                    'pnl': trade.pnl,
                    'entry_time': trade.entry_time,
                    'exit_time': trade.exit_time
                }
                trade_list.append(trade_dict)
            
            return trade_list
    
    def get_trade_by_id(self, trade_id: int) -> Optional[Trade]:
        """Get a specific trade by ID"""
        with self.get_session() as session:
            return session.query(Trade).filter(Trade.id == trade_id).first()
    
    # Signal operations
    def save_signal(self, signal_data: Dict[str, Any]) -> Signal:
        """Save a trading signal to database"""
        with self.get_session() as session:
            signal = Signal(**signal_data)
            session.add(signal)
            session.flush()
            session.refresh(signal)
            return signal
    
    def get_signals(self, symbol: Optional[str] = None, limit: int = 100) -> List[Signal]:
        """Get signals from database"""
        with self.get_session() as session:
            query = session.query(Signal)
            if symbol:
                query = query.filter(Signal.symbol == symbol)
            return query.order_by(Signal.timestamp.desc()).limit(limit).all()
    
    def mark_signal_executed(self, signal_id: int) -> bool:
        """Mark a signal as executed"""
        with self.get_session() as session:
            signal = session.query(Signal).filter(Signal.id == signal_id).first()
            if signal:
                signal.executed = True
                return True
            return False
    
    # Portfolio operations
    def update_portfolio(self, portfolio_data: Dict[str, Any]) -> Portfolio:
        """Update portfolio position"""
        with self.get_session() as session:
            # Check if position exists
            existing = session.query(Portfolio).filter(
                Portfolio.symbol == portfolio_data['symbol'],
                Portfolio.is_paper_trade == portfolio_data.get('is_paper_trade', True)
            ).first()
            
            if existing:
                # Update existing position
                for key, value in portfolio_data.items():
                    setattr(existing, key, value)
                existing.last_updated = datetime.utcnow()
                session.flush()
                session.refresh(existing)
                return existing
            else:
                # Create new position
                portfolio = Portfolio(**portfolio_data)
                session.add(portfolio)
                session.flush()
                session.refresh(portfolio)
                return portfolio
    
    def get_portfolio(self, trading_mode, symbol: Optional[str] = None) -> List[Portfolio]:
        """Get portfolio positions"""
        with self.get_session() as session:
            query = session.query(Portfolio).filter(Portfolio.trading_mode == trading_mode)
            if symbol:
                query = query.filter(Portfolio.symbol == symbol)
            return query.all()
    
    def get_portfolio_value(self, trading_mode) -> float:
        """Calculate total portfolio value"""
        with self.get_session() as session:
            portfolio = session.query(Portfolio).filter(Portfolio.trading_mode == trading_mode).first()
            return portfolio.total_balance if portfolio else 0.0
    
    def get_open_trades(self, trading_mode):
        """Get all open trades for a trading mode"""
        with self.get_session() as session:
            trades = session.query(Trade).filter(
                Trade.status == TradeStatus.OPEN
            ).all()
            
            # Convert to dictionaries to avoid session issues
            trade_list = []
            for trade in trades:
                trade_dict = {
                    'id': trade.id,
                    'symbol': trade.symbol,
                    'trade_type': trade.trade_type,
                    'status': trade.status,
                    'trading_mode': trade.trading_mode,
                    'entry_price': trade.entry_price,
                    'quantity': trade.quantity,
                    'stop_loss': trade.stop_loss,
                    'take_profit': trade.take_profit,
                    'entry_time': trade.entry_time
                }
                trade_list.append(trade_dict)
            
            return trade_list
    
    def create_trade(self, trade_data):
        """Create a new trade record"""
        with self.get_session() as session:
            trade = Trade(**trade_data)
            session.add(trade)
            session.flush()
            session.refresh(trade)
            # Create a detached copy to avoid session issues
            trade_id = trade.id
            trade_symbol = trade.symbol
            logger.info(f"Created trade: {trade_id} for {trade_symbol}")
            
            # Return a dictionary instead of the ORM object to avoid session issues
            return {
                'id': trade.id,
                'symbol': trade.symbol,
                'trade_type': trade.trade_type,
                'status': trade.status,
                'trading_mode': trade.trading_mode,
                'entry_price': trade.entry_price,
                'quantity': trade.quantity,
                'stop_loss': trade.stop_loss,
                'take_profit': trade.take_profit
            }
    
    def update_portfolio(self, trading_mode, portfolio_data):
        """Update portfolio record"""
        with self.get_session() as session:
            from datetime import datetime, date
            today = date.today()
            
            portfolio = session.query(Portfolio).filter(
                Portfolio.trading_mode == trading_mode,
                Portfolio.date >= today
            ).first()
            
            if not portfolio:
                portfolio = Portfolio(trading_mode=trading_mode, date=datetime.utcnow())
                session.add(portfolio)
            
            for key, value in portfolio_data.items():
                setattr(portfolio, key, value)
            
            session.flush()
            session.refresh(portfolio)
            return portfolio
    
    def get_trading_stats(self, trading_mode):
        """Get trading statistics"""
        with self.get_session() as session:
            trades = session.query(Trade).filter(
                Trade.trading_mode == trading_mode,
                Trade.status == TradeStatus.CLOSED
            ).all()
            
            if not trades:
                return {
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "total_pnl": 0.0,
                    "win_rate": 0.0
                }
            
            winning_trades = len([t for t in trades if t.pnl and t.pnl > 0])
            losing_trades = len([t for t in trades if t.pnl and t.pnl <= 0])
            total_pnl = sum(t.pnl for t in trades if t.pnl)
            
            return {
                "total_trades": len(trades),
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "total_pnl": total_pnl,
                "win_rate": (winning_trades / len(trades)) * 100 if trades else 0
            }

    # Analytics and reporting
    def get_trade_statistics(self, symbol: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get trading statistics"""
        with self.get_session() as session:
            from datetime import timedelta
            
            start_date = datetime.utcnow() - timedelta(days=days)
            query = session.query(Trade).filter(Trade.timestamp >= start_date)
            
            if symbol:
                query = query.filter(Trade.symbol == symbol)
            
            trades = query.all()
            
            if not trades:
                return {
                    'total_trades': 0,
                    'total_profit_loss': 0.0,
                    'win_rate': 0.0,
                    'avg_profit_per_trade': 0.0
                }
            
            total_pnl = sum(trade.profit_loss for trade in trades)
            winning_trades = len([t for t in trades if t.profit_loss > 0])
            
            return {
                'total_trades': len(trades),
                'total_profit_loss': total_pnl,
                'win_rate': (winning_trades / len(trades)) * 100 if trades else 0,
                'avg_profit_per_trade': total_pnl / len(trades) if trades else 0,
                'winning_trades': winning_trades,
                'losing_trades': len(trades) - winning_trades
            }
    
    def update_trade(self, trade_id: int, update_data: Dict[str, Any]) -> bool:
        """Update a trade record"""
        with self.get_session() as session:
            trade = session.query(Trade).filter(Trade.id == trade_id).first()
            if trade:
                for key, value in update_data.items():
                    setattr(trade, key, value)
                trade.updated_at = datetime.utcnow()
                session.flush()
                logger.info(f"Updated trade {trade_id}: {update_data}")
                return True
            return False

    def close_trade(self, trade_id: int, exit_price: float, pnl: float) -> bool:
        """Close a trade"""
        with self.get_session() as session:
            trade = session.query(Trade).filter(Trade.id == trade_id).first()
            if trade:
                trade.status = TradeStatus.CLOSED
                trade.exit_price = exit_price
                trade.exit_time = datetime.utcnow()
                trade.pnl = pnl
                trade.pnl_percent = (pnl / (trade.entry_price * trade.quantity)) * 100
                trade.updated_at = datetime.utcnow()
                session.flush()
                logger.info(f"Closed trade {trade_id} with P&L: ${pnl:.2f}")
                return True
            return False

    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data from database"""
        with self.get_session() as session:
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Delete old trades
            deleted_trades = session.query(Trade).filter(Trade.timestamp < cutoff_date).delete()
            
            # Delete old signals
            deleted_signals = session.query(Signal).filter(Signal.timestamp < cutoff_date).delete()
            
            logger.info(f"Cleaned up {deleted_trades} trades and {deleted_signals} signals")
            
            return deleted_trades + deleted_signals

# Global database manager instance  
db_manager = DatabaseManager()
