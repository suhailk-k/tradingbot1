"""
Main Tradifrom config import config, strategy_config
from database import DatabaseManager
from models import Trade, Signal, TradeStatus, TradeType, TradingMode
from binance_interface import BinanceInterface
from strategy import TradingStrategy
from ai_analysis import GeminiAI

# Import the global database manager
from database import db_manager Module
Orchestrates all trading operations including signal generation, position management, and execution.
"""

import asyncio
import logging
import signal
import sys
import structlog
from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from config import config, strategy_config
from database import DatabaseManager
from models import Trade, Signal, TradeStatus, TradeType, TradingMode
from binance_interface import BinanceInterface
from strategy import TradingStrategy
from ai_analysis import GeminiAI

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.log_file),
        logging.StreamHandler()
    ]
)

logger = structlog.get_logger(__name__)

class TradingBot:
    """Main trading bot class"""
    
    def __init__(self, paper_trading: bool = True, symbol: str = None):
        """Initialize trading bot"""
        self.paper_trading = paper_trading
        self.symbol = symbol or config.default_symbol
        self.trading_mode = TradingMode.PAPER if paper_trading else TradingMode.LIVE
        self.running = False
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Initialize components
        self.binance = BinanceInterface(paper_trading=paper_trading)
        self.strategy = TradingStrategy()
        self.ai = GeminiAI()
        
        # Trading state
        self.daily_trades = 0
        self.last_trade_date = datetime.now().date()
        self.last_signal_time = None
        self.position_manager = PositionManager(self.binance, self.db_manager)
        
        # Performance tracking
        self.start_time = None
        self.trades_today = 0
        
        logger.info(f"Trading bot initialized", 
                   symbol=self.symbol,
                   mode=self.trading_mode.value,
                   paper_trading=paper_trading)
    
    async def start(self):
        """Start the trading bot"""
        try:
            self.running = True
            self.start_time = datetime.now()
            
            logger.info("🚀 Trading bot starting",
                       symbol=self.symbol,
                       mode=self.trading_mode.value)
            
            # Setup signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Validate configuration
            await self._validate_setup()
            
            # Start trading loop
            await self._trading_loop()
            
        except Exception as e:
            logger.error("Error starting trading bot", error=str(e))
            raise
    
    async def stop(self):
        """Stop the trading bot"""
        logger.info("🛑 Stopping trading bot")
        self.running = False
        
        # Close any open positions if in paper trading
        if self.paper_trading:
            await self.position_manager.close_all_positions("Bot shutdown")
        
        # Generate summary
        logger.info("📊 Session Summary", 
                   trades=self.trades_today,
                   duration=duration)
        
        # Get trading stats
        stats = self.db_manager.get_trading_stats(self.trading_mode)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown")
        asyncio.create_task(self.stop())
    
    async def _validate_setup(self):
        """Validate trading setup and connections"""
        try:
            # Test Binance connection
            account_info = await self.binance.get_account_info()
            logger.info("✅ Binance connection validated",
                       balance=account_info.get('totalWalletBalance', 0))
            
            # Test symbol info
            symbol_info = await self.binance.get_symbol_info(self.symbol)
            logger.info("✅ Symbol info retrieved", symbol=self.symbol)
            
            # Test AI connection
            test_analysis = await self.ai.analyze_market_sentiment(
                self.symbol, 
                {'price': 50000, 'change_24h': 2.5, 'volume': 1000000},
                {'ema_fast': 50000, 'ema_slow': 49800, 'rsi': 55, 'adx': 30}
            )
            logger.info("✅ AI analysis validated")
            
            # Check database
            portfolio = self.db_manager.get_portfolio(self.trading_mode)
            logger.info("✅ Database connection validated")
            
        except Exception as e:
            logger.error("❌ Setup validation failed", error=str(e))
            raise
    
    async def _trading_loop(self):
        """Main trading loop"""
        logger.info("📊 Starting trading loop")
        
        while self.running:
            try:
                # Reset daily trade count
                await self._check_daily_reset()
                
                # Skip trading if daily limit reached
                if self.trades_today >= config.max_trades_per_day:
                    logger.debug("Daily trade limit reached, waiting")
                    await asyncio.sleep(300)  # Wait 5 minutes
                    continue
                
                # Get market data
                market_data = await self._get_market_data()
                
                if market_data is None:
                    await asyncio.sleep(60)  # Wait 1 minute on error
                    continue
                
                # Generate trading signal
                signal_data = await self._analyze_market(market_data)
                
                # Manage existing positions
                await self.position_manager.manage_positions(market_data, signal_data)
                
                # Check for new trading opportunities
                if not await self.position_manager.has_open_positions():
                    await self._evaluate_entry_signal(signal_data, market_data)
                
                # Update portfolio metrics
                await self._update_portfolio_metrics()
                
                # Log current status
                await self._log_status(market_data, signal_data)
                
                # Wait before next iteration
                await asyncio.sleep(30)  # 30 seconds between checks
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error("Error in trading loop", error=str(e))
                await asyncio.sleep(60)  # Wait on error
    
    async def _check_daily_reset(self):
        """Check if it's a new trading day and reset counters"""
        today = datetime.now().date()
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
            logger.info("📅 New trading day started", date=today)
    
    async def _get_market_data(self) -> Optional[Dict]:
        """Get current market data and indicators"""
        try:
            # Get historical data for indicators
            historical_data = await self.binance.get_historical_data(
                symbol=self.symbol,
                timeframe=config.default_timeframe,
                limit=100
            )
            
            if historical_data.empty:
                logger.warning("No historical data available")
                return None
            
            # Calculate technical indicators
            data_with_indicators = self.strategy.calculate_indicators(historical_data)
            
            # Get current price and volume
            current_price = await self.binance.get_current_price(self.symbol)
            
            return {
                'price_data': {
                    'price': current_price,
                    'timestamp': datetime.now(),
                    'symbol': self.symbol
                },
                'historical_data': data_with_indicators,
                'latest_candle': data_with_indicators.iloc[-1],
                'account_info': await self.binance.get_account_info()
            }
            
        except Exception as e:
            logger.error("Error getting market data", error=str(e))
            return None
    
    async def _analyze_market(self, market_data: Dict) -> Dict:
        """Analyze market conditions and generate signals"""
        try:
            # Generate technical signal
            signal_data = self.strategy.generate_signal(market_data['historical_data'])
            
            # Get AI analysis
            ai_analysis = await self.ai.analyze_market_sentiment(
                self.symbol,
                market_data['price_data'],
                signal_data['indicators']
            )
            
            # Validate signal with AI
            if signal_data['signal'] != 'HOLD':
                ai_validation = await self.ai.validate_trading_signal(
                    signal_data,
                    {
                        'trend': 'bullish' if signal_data['indicators']['ema_fast'] > signal_data['indicators']['ema_slow'] else 'bearish',
                        'volatility': signal_data['indicators']['atr'],
                        'volume_profile': signal_data['indicators']['volume_ratio']
                    }
                )
                
                # Adjust signal strength based on AI validation
                if not ai_validation['valid']:
                    signal_data['strength'] *= 0.5
                    signal_data['reasons'].append(f"AI validation concern: {ai_validation['reasoning']}")
            
            # Combine technical and AI analysis
            signal_data['ai_analysis'] = ai_analysis
            signal_data['timestamp'] = datetime.now()
            
            return signal_data
            
        except Exception as e:
            logger.error("Error in market analysis", error=str(e))
            return {
                'signal': 'HOLD',
                'strength': 0,
                'confidence': 0,
                'reasons': ['Analysis error'],
                'indicators': {},
                'timestamp': datetime.now()
            }
    
    async def _evaluate_entry_signal(self, signal_data: Dict, market_data: Dict):
        """Evaluate if we should enter a new position"""
        if signal_data['signal'] == 'HOLD':
            return
        
        # Validate signal meets our criteria
        if not self.strategy.validate_signal(signal_data, market_data['price_data']['price']):
            logger.debug("Signal validation failed", 
                        signal=signal_data['signal'],
                        strength=signal_data['strength'])
            return
        
        # Check if enough time has passed since last signal
        if (self.last_signal_time and 
            datetime.now() - self.last_signal_time < timedelta(minutes=15)):
            logger.debug("Too soon since last signal")
            return
        
        # Calculate position size
        account_info = market_data['account_info']
        available_balance = float(account_info.get('availableBalance', 0))
        
        if available_balance < config.position_size_usd:
            logger.warning("Insufficient balance for new position",
                          available=available_balance,
                          required=config.position_size_usd)
            return
        
        # Execute trade
        await self._execute_trade(signal_data, market_data)
    
    async def _execute_trade(self, signal_data: Dict, market_data: Dict):
        """Execute a trade based on signal"""
        try:
            current_price = market_data['price_data']['price']
            latest_candle = market_data['latest_candle']
            
            # Calculate position size based on risk management
            risk_amount = market_data['account_info']['totalWalletBalance'] * (config.risk_per_trade_percent / 100)
            
            # Calculate stop loss and take profit
            atr = latest_candle.get('atr', current_price * 0.02)
            stop_loss, take_profit = self.strategy.calculate_stop_loss_take_profit(
                current_price, signal_data['signal'], atr
            )
            
            # Calculate position size
            quantity = self.binance.calculate_position_size(
                self.symbol, risk_amount, current_price, stop_loss
            )
            
            if quantity == 0:
                logger.warning("Calculated position size is zero")
                return
            
            # Place order
            side = 'BUY' if signal_data['signal'] == 'BUY' else 'SELL'
            
            order = await self.binance.place_order(
                symbol=self.symbol,
                side=side,
                quantity=quantity,
                order_type='MARKET',
                stop_price=stop_loss,
                take_profit=take_profit
            )
            
            # Record trade in database
            trade_data = {
                'symbol': self.symbol,
                'trade_type': TradeType.LONG if side == 'BUY' else TradeType.SHORT,
                'trading_mode': self.trading_mode,
                'entry_price': float(order.get('avgPrice', current_price)),
                'quantity': quantity,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'ema_fast': signal_data['indicators']['ema_fast'],
                'ema_slow': signal_data['indicators']['ema_slow'],
                'adx': signal_data['indicators']['adx'],
                'rsi': signal_data['indicators']['rsi'],
                'notes': f"Signal strength: {signal_data['strength']}, Reasons: {', '.join(signal_data['reasons'])}"
            }
            
            trade = self.db_manager.create_trade(trade_data)
            
            # Update counters
            self.trades_today += 1
            self.last_signal_time = datetime.now()
            
            logger.info("✅ Trade executed",
                       trade_id=trade['id'],
                       symbol=self.symbol,
                       side=side,
                       quantity=quantity,
                       price=trade_data['entry_price'],
                       strength=signal_data['strength'])
            
        except Exception as e:
            logger.error("Error executing trade", error=str(e))
    
    async def _update_portfolio_metrics(self):
        """Update portfolio performance metrics"""
        try:
            account_info = await self.binance.get_account_info()
            stats = self.db_manager.get_trading_stats(self.trading_mode)
            
            portfolio_data = {
                'total_balance': float(account_info.get('totalWalletBalance', 0)),
                'available_balance': float(account_info.get('availableBalance', 0)),
                'used_margin': float(account_info.get('totalMarginBalance', 0)) - float(account_info.get('availableBalance', 0)),
                'total_pnl': stats['total_pnl'],
                'total_pnl_percent': (stats['total_pnl'] / config.paper_trading_initial_balance) * 100 if self.paper_trading else 0,
                'win_rate': stats['win_rate'],
                'total_trades': stats['total_trades'],
                'winning_trades': stats['winning_trades'],
                'losing_trades': stats['losing_trades']
            }
            
            self.db_manager.update_portfolio(self.trading_mode, portfolio_data)
            
        except Exception as e:
            logger.error("Error updating portfolio metrics", error=str(e))
    
    async def _log_status(self, market_data: Dict, signal_data: Dict):
        """Log current trading status"""
        current_price = market_data['price_data']['price']
        account_info = market_data['account_info']
        
        logger.info("📊 Trading Status",
                   symbol=self.symbol,
                   price=f"${current_price:,.2f}",
                   signal=signal_data['signal'],
                   strength=f"{signal_data['strength']:.1f}%",
                   balance=f"${float(account_info.get('totalWalletBalance', 0)):,.2f}",
                   trades_today=self.trades_today,
                   rsi=f"{signal_data['indicators'].get('rsi', 0):.1f}",
                   adx=f"{signal_data['indicators'].get('adx', 0):.1f}")
    
    async def _generate_session_summary(self):
        """Generate trading session summary"""
        if not self.start_time:
            return
        
        session_duration = datetime.now() - self.start_time
        stats = self.db_manager.get_trading_stats(self.trading_mode)
        
        logger.info("📈 Trading Session Summary",
                   duration=str(session_duration),
                   trades_executed=self.trades_today,
                   total_trades=stats['total_trades'],
                   win_rate=f"{stats['win_rate']:.1f}%",
                   total_pnl=f"${stats['total_pnl']:.2f}")

class PositionManager:
    """Manages open positions and risk"""
    
    def __init__(self, binance_interface: BinanceInterface, database_manager):
        self.binance = binance_interface
        self.db = database_manager
        
    async def has_open_positions(self) -> bool:
        """Check if there are any open positions"""
        open_trades = self.db.get_open_trades(
            TradingMode.PAPER if self.binance.paper_trading else TradingMode.LIVE
        )
        return len(open_trades) > 0
    
    async def manage_positions(self, market_data: Dict, signal_data: Dict):
        """Manage existing positions"""
        trading_mode = TradingMode.PAPER if self.binance.paper_trading else TradingMode.LIVE
        open_trades = self.db.get_open_trades(trading_mode)
        
        for trade in open_trades:
            await self._manage_single_position(trade, market_data, signal_data)
    
    async def _manage_single_position(self, trade: Dict, market_data: Dict, signal_data: Dict):
        """Manage a single position"""
        current_price = market_data['price_data']['price']
        
        # Check stop loss
        if self._should_stop_loss(trade, current_price):
            await self._close_position(trade, current_price, "Stop Loss Hit")
            return
        
        # Check take profit
        if self._should_take_profit(trade, current_price):
            await self._close_position(trade, current_price, "Take Profit Hit")
            return
        
        # Check for signal reversal
        if self._should_reverse_position(trade, signal_data):
            await self._close_position(trade, current_price, "Signal Reversal")
            return
    
    def _should_stop_loss(self, trade: Dict, current_price: float) -> bool:
        """Check if stop loss should be triggered"""
        if not trade.get('stop_loss'):
            return False
        
        if trade['trade_type'] == TradeType.LONG:
            return current_price <= trade['stop_loss']
        else:  # SHORT
            return current_price >= trade['stop_loss']
    
    def _should_take_profit(self, trade: Dict, current_price: float) -> bool:
        """Check if take profit should be triggered"""
        if not trade.get('take_profit'):
            return False
        
        if trade['trade_type'] == TradeType.LONG:
            return current_price >= trade['take_profit']
        else:  # SHORT
            return current_price <= trade['take_profit']
    
    def _should_reverse_position(self, trade: Dict, signal_data: Dict) -> bool:
        """Check if position should be closed due to signal reversal"""
        if signal_data['signal'] == 'HOLD':
            return False
        
        # Strong opposite signal
        if signal_data['strength'] < 70:
            return False
        
        if trade['trade_type'] == TradeType.LONG and signal_data['signal'] == 'SELL':
            return True
        elif trade['trade_type'] == TradeType.SHORT and signal_data['signal'] == 'BUY':
            return True
        
        return False
    
    async def _close_position(self, trade: Dict, exit_price: float, reason: str):
        """Close a position"""
        try:
            # Close position on exchange
            if not self.binance.paper_trading:
                await self.binance.close_position(trade['symbol'])
            
            # Calculate P&L
            entry_price = trade['entry_price']
            quantity = trade['quantity']
            
            if trade['trade_type'] == TradeType.LONG:
                pnl = (exit_price - entry_price) * quantity
            else:  # SHORT
                pnl = (entry_price - exit_price) * quantity
            
            # Update trade in database
            self.db.close_trade(trade['id'], exit_price, pnl)
            
            logger.info("Position closed",
                       trade_id=trade['id'],
                       symbol=trade['symbol'],
                       reason=reason,
                       exit_price=exit_price,
                       pnl=f"${pnl:.2f}")
            
        except Exception as e:
            logger.error("Error closing position", 
                        trade_id=trade.id, 
                        error=str(e))
    
    async def close_all_positions(self, reason: str):
        """Close all open positions"""
        trading_mode = TradingMode.PAPER if self.binance.paper_trading else TradingMode.LIVE
        open_trades = self.db.get_open_trades(trading_mode)
        
        for trade in open_trades:
            try:
                # trade is now a dictionary, not an ORM object
                current_price = await self.binance.get_current_price(trade['symbol'])
                await self._close_position(trade, current_price, reason)
            except Exception as e:
                logger.error("Error closing position during shutdown",
                           trade_id=trade['id'],
                           error=str(e))
