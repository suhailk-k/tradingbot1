"""
Backtesting engine for strategy validation.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import asyncio

from strategy import TradingStrategy
from binance_interface import BinanceInterface
from database import db_manager
from models import Trade, TradeType, TradeStatus, TradingMode

logger = logging.getLogger(__name__)

class BacktestEngine:
    """Backtesting engine for strategy validation"""
    
    def __init__(self, initial_balance: float = 10000):
        """Initialize backtest engine"""
        self.initial_balance = initial_balance
        self.strategy = TradingStrategy()
        self.binance = BinanceInterface(paper_trading=True)
        
        # Backtest state
        self.balance = initial_balance
        self.positions = []
        self.trades = []
        self.equity_curve = []
        
        logger.info(f"Backtest engine initialized with ${initial_balance}")
    
    async def run_backtest(self, symbol: str, start_date: str, end_date: str, 
                          timeframe: str = '15m') -> Dict:
        """Run complete backtest"""
        try:
            logger.info(f"Starting backtest for {symbol} from {start_date} to {end_date}")
            
            # Get historical data
            data = await self._get_backtest_data(symbol, start_date, end_date, timeframe)
            
            if data.empty:
                raise ValueError("No historical data available for backtest period")
            
            # Calculate indicators
            data = self.strategy.calculate_indicators(data)
            
            # Initialize backtest state
            self._reset_backtest_state()
            
            # Run simulation
            results = await self._simulate_trading(data, symbol)
            
            # Calculate performance metrics
            performance = self._calculate_performance_metrics()
            
            # Store results
            backtest_results = {
                'symbol': symbol,
                'period': f"{start_date} to {end_date}",
                'timeframe': timeframe,
                'initial_balance': self.initial_balance,
                'final_balance': self.balance,
                'total_return': ((self.balance - self.initial_balance) / self.initial_balance) * 100,
                'trades': len(self.trades),
                'performance': performance,
                'equity_curve': self.equity_curve,
                'trades_detail': self.trades
            }
            
            logger.info(f"Backtest completed. Total return: {backtest_results['total_return']:.2f}%")
            return backtest_results
            
        except Exception as e:
            logger.error(f"Error in backtest: {e}")
            raise
    
    async def _get_backtest_data(self, symbol: str, start_date: str, 
                               end_date: str, timeframe: str) -> pd.DataFrame:
        """Get historical data for backtesting"""
        try:
            # Convert dates to timestamps
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
            
            # Get data in chunks to handle large date ranges
            all_data = []
            current_start = start_ts
            
            while current_start < end_ts:
                # Calculate chunk end (max 1000 candles per request)
                chunk_data = await self.binance.get_historical_data(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=1000,
                    start_time=current_start
                )
                
                if chunk_data.empty:
                    break
                
                all_data.append(chunk_data)
                
                # Update start time for next chunk
                current_start = int(chunk_data.index[-1].timestamp() * 1000) + 1
                
                # Add small delay to respect rate limits
                await asyncio.sleep(0.1)
            
            if not all_data:
                return pd.DataFrame()
            
            # Combine all data
            data = pd.concat(all_data)
            data = data[~data.index.duplicated(keep='first')]
            data.sort_index(inplace=True)
            
            # Filter by date range
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            data = data[start_dt:end_dt]
            
            logger.info(f"Retrieved {len(data)} candles for backtest")
            return data
            
        except Exception as e:
            logger.error(f"Error getting backtest data: {e}")
            return pd.DataFrame()
    
    def _reset_backtest_state(self):
        """Reset backtest state"""
        self.balance = self.initial_balance
        self.positions = []
        self.trades = []
        self.equity_curve = []
    
    async def _simulate_trading(self, data: pd.DataFrame, symbol: str) -> Dict:
        """Simulate trading on historical data"""
        position_size_pct = 0.1  # 10% of balance per trade
        commission = 0.001  # 0.1% commission
        
        for i in range(len(data)):
            current_data = data.iloc[:i+1]
            
            if len(current_data) < 50:  # Need enough data for indicators
                continue
            
            current_candle = current_data.iloc[-1]
            timestamp = current_candle.name
            price = current_candle['close']
            
            # Update equity curve
            self._update_equity_curve(timestamp, price)
            
            # Generate signal
            signal_data = self.strategy.generate_signal(current_data)
            
            if not self.strategy.validate_signal(signal_data, price):
                continue
            
            signal = signal_data['signal']
            
            # Check if we already have a position
            if self.positions:
                # Manage existing position
                await self._manage_position(current_candle, signal_data)
            else:
                # Open new position if signal is strong enough
                if signal in ['BUY', 'SELL'] and signal_data['strength'] > 60:
                    await self._open_position(symbol, signal, price, timestamp, 
                                            position_size_pct, commission, current_candle)
        
        # Close any remaining positions at the end
        if self.positions:
            final_price = data.iloc[-1]['close']
            final_timestamp = data.index[-1]
            await self._close_position(final_price, final_timestamp, commission, "End of backtest")
        
        return {'status': 'completed'}
    
    async def _open_position(self, symbol: str, signal: str, price: float, 
                           timestamp: pd.Timestamp, position_size_pct: float, 
                           commission: float, candle_data) -> None:
        """Open a new position"""
        if len(self.positions) > 0:  # Only one position at a time
            return
        
        position_value = self.balance * position_size_pct
        quantity = position_value / price
        
        # Calculate stop loss and take profit
        atr = candle_data.get('atr', price * 0.02)  # Use 2% if ATR not available
        stop_loss, take_profit = self.strategy.calculate_stop_loss_take_profit(
            price, signal, atr
        )
        
        # Create position
        position = {
            'symbol': symbol,
            'type': signal.lower(),
            'entry_price': price,
            'quantity': quantity,
            'entry_time': timestamp,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_commission': position_value * commission
        }
        
        self.positions.append(position)
        
        # Deduct commission from balance
        self.balance -= position['entry_commission']
        
        logger.debug(f"Opened {signal} position at ${price:.2f} with quantity {quantity:.6f}")
    
    async def _manage_position(self, candle_data, signal_data) -> None:
        """Manage existing position"""
        if not self.positions:
            return
        
        position = self.positions[0]
        current_price = candle_data['close']
        timestamp = candle_data.name
        
        # Check stop loss
        if position['type'] == 'buy' and current_price <= position['stop_loss']:
            await self._close_position(current_price, timestamp, 0.001, "Stop Loss")
            return
        elif position['type'] == 'sell' and current_price >= position['stop_loss']:
            await self._close_position(current_price, timestamp, 0.001, "Stop Loss")
            return
        
        # Check take profit
        if position['type'] == 'buy' and current_price >= position['take_profit']:
            await self._close_position(current_price, timestamp, 0.001, "Take Profit")
            return
        elif position['type'] == 'sell' and current_price <= position['take_profit']:
            await self._close_position(current_price, timestamp, 0.001, "Take Profit")
            return
        
        # Check for signal reversal
        if signal_data['signal'] != 'HOLD':
            opposite_signal = 'SELL' if position['type'] == 'buy' else 'BUY'
            if signal_data['signal'] == opposite_signal and signal_data['strength'] > 70:
                await self._close_position(current_price, timestamp, 0.001, "Signal Reversal")
                return
    
    async def _close_position(self, exit_price: float, exit_time: pd.Timestamp, 
                            commission: float, reason: str) -> None:
        """Close existing position"""
        if not self.positions:
            return
        
        position = self.positions.pop(0)
        
        # Calculate P&L
        if position['type'] == 'buy':
            pnl = (exit_price - position['entry_price']) * position['quantity']
        else:  # sell
            pnl = (position['entry_price'] - exit_price) * position['quantity']
        
        exit_commission = exit_price * position['quantity'] * commission
        net_pnl = pnl - position['entry_commission'] - exit_commission
        
        # Update balance
        position_value = exit_price * position['quantity']
        self.balance += position_value + net_pnl
        
        # Record trade
        trade = {
            'symbol': position['symbol'],
            'type': position['type'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'quantity': position['quantity'],
            'entry_time': position['entry_time'],
            'exit_time': exit_time,
            'pnl': net_pnl,
            'pnl_percent': (net_pnl / (position['entry_price'] * position['quantity'])) * 100,
            'duration': exit_time - position['entry_time'],
            'exit_reason': reason
        }
        
        self.trades.append(trade)
        
        logger.debug(f"Closed {position['type']} position. P&L: ${net_pnl:.2f} ({reason})")
    
    def _update_equity_curve(self, timestamp: pd.Timestamp, current_price: float):
        """Update equity curve with current portfolio value"""
        portfolio_value = self.balance
        
        # Add unrealized P&L from open positions
        for position in self.positions:
            if position['type'] == 'buy':
                unrealized_pnl = (current_price - position['entry_price']) * position['quantity']
            else:
                unrealized_pnl = (position['entry_price'] - current_price) * position['quantity']
            
            portfolio_value += unrealized_pnl
        
        self.equity_curve.append({
            'timestamp': timestamp,
            'equity': portfolio_value,
            'balance': self.balance,
            'positions': len(self.positions)
        })
    
    def _calculate_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'avg_trade': 0,
                'best_trade': 0,
                'worst_trade': 0
            }
        
        # Basic statistics
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] <= 0]
        
        total_profit = sum(t['pnl'] for t in winning_trades)
        total_loss = abs(sum(t['pnl'] for t in losing_trades))
        
        # Calculate metrics
        win_rate = (len(winning_trades) / len(self.trades)) * 100
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # Returns for Sharpe ratio
        if self.equity_curve:
            returns = []
            for i in range(1, len(self.equity_curve)):
                prev_equity = self.equity_curve[i-1]['equity']
                curr_equity = self.equity_curve[i]['equity']
                returns.append((curr_equity - prev_equity) / prev_equity)
            
            if returns:
                avg_return = np.mean(returns)
                std_return = np.std(returns)
                sharpe_ratio = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        # Maximum drawdown
        max_drawdown = self._calculate_max_drawdown()
        
        return {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_pnl': sum(t['pnl'] for t in self.trades),
            'avg_trade': np.mean([t['pnl'] for t in self.trades]),
            'best_trade': max(t['pnl'] for t in self.trades),
            'worst_trade': min(t['pnl'] for t in self.trades),
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'avg_trade_duration': np.mean([t['duration'].total_seconds() / 3600 for t in self.trades]),  # hours
            'recovery_factor': abs(sum(t['pnl'] for t in self.trades) / max_drawdown) if max_drawdown != 0 else 0
        }
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if not self.equity_curve:
            return 0
        
        peak = self.equity_curve[0]['equity']
        max_drawdown = 0
        
        for point in self.equity_curve:
            if point['equity'] > peak:
                peak = point['equity']
            
            drawdown = (peak - point['equity']) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def generate_backtest_report(self, results: Dict) -> str:
        """Generate human-readable backtest report"""
        performance = results['performance']
        
        report = f"""
        ╔══════════════════════════════════════════════════════════╗
        ║                    BACKTEST REPORT                      ║
        ╠══════════════════════════════════════════════════════════╣
        ║ Symbol: {results['symbol']}                             ║
        ║ Period: {results['period']}                             ║
        ║ Timeframe: {results['timeframe']}                       ║
        ╠══════════════════════════════════════════════════════════╣
        ║                    PERFORMANCE                           ║
        ╠══════════════════════════════════════════════════════════╣
        ║ Initial Balance:     ${results['initial_balance']:,.2f} ║
        ║ Final Balance:       ${results['final_balance']:,.2f}   ║
        ║ Total Return:        {results['total_return']:6.2f}%    ║
        ║ Total P&L:           ${performance['total_pnl']:,.2f}   ║
        ╠══════════════════════════════════════════════════════════╣
        ║                    TRADE STATISTICS                     ║
        ╠══════════════════════════════════════════════════════════╣
        ║ Total Trades:        {performance['total_trades']:6d}   ║
        ║ Winning Trades:      {performance['winning_trades']:6d} ║
        ║ Losing Trades:       {performance['losing_trades']:6d}  ║
        ║ Win Rate:            {performance['win_rate']:6.2f}%    ║
        ║ Profit Factor:       {performance['profit_factor']:6.2f}║
        ║ Average Trade:       ${performance['avg_trade']:6.2f}   ║
        ║ Best Trade:          ${performance['best_trade']:6.2f}  ║
        ║ Worst Trade:         ${performance['worst_trade']:6.2f} ║
        ╠══════════════════════════════════════════════════════════╣
        ║                    RISK METRICS                         ║
        ╠══════════════════════════════════════════════════════════╣
        ║ Sharpe Ratio:        {performance['sharpe_ratio']:6.2f} ║
        ║ Max Drawdown:        {performance['max_drawdown']:6.2f}%║
        ║ Recovery Factor:     {performance['recovery_factor']:6.2f}║
        ║ Avg Trade Duration:  {performance['avg_trade_duration']:6.1f} hrs║
        ╚══════════════════════════════════════════════════════════╝
        """
        
        return report
