"""
Binance exchange interface for futures trading.
Handles all interactions with Binance Futures API.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import ccxt.pro as ccxt
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException

from config import config
from models import TradeType, TradingMode

logger = logging.getLogger(__name__)

class BinanceInterface:
    """Binance Futures trading interface"""
    
    def __init__(self, paper_trading: bool = True):
        """Initialize Binance interface"""
        self.paper_trading = paper_trading
        self.testnet = config.binance_testnet or paper_trading
        
        # Initialize Binance client
        try:
            self.client = Client(
                api_key=config.binance_api_key,
                api_secret=config.binance_secret_key,
                testnet=self.testnet
            )
            
            # Initialize CCXT for advanced features
            self.exchange = ccxt.binance({
                'apiKey': config.binance_api_key,
                'secret': config.binance_secret_key,
                'sandbox': self.testnet,
                'options': {
                    'defaultType': 'future',  # Use futures
                },
            })
            
            # Test connection
            self.client.ping()
            logger.info(f"Binance interface initialized (testnet: {self.testnet})")
            
        except Exception as e:
            logger.error(f"Failed to initialize Binance interface: {e}")
            raise
        
        # Paper trading state
        self.paper_balance = config.paper_trading_initial_balance
        self.paper_positions: Dict[str, Dict] = {}
        
        # Trading limits
        self.daily_trades = 0
        self.last_trade_date = datetime.now().date()
    
    async def get_account_info(self) -> Dict:
        """Get account information"""
        if self.paper_trading:
            return {
                'totalWalletBalance': self.paper_balance,
                'totalUnrealizedProfit': sum(pos.get('unrealizedProfit', 0) for pos in self.paper_positions.values()),
                'availableBalance': self.paper_balance - sum(pos.get('margin', 0) for pos in self.paper_positions.values()),
                'totalMarginBalance': self.paper_balance,
                'canTrade': True
            }
        
        try:
            account = self.client.futures_account()
            return account
        except BinanceAPIException as e:
            logger.error(f"Error getting account info: {e}")
            raise
    
    async def get_symbol_info(self, symbol: str) -> Dict:
        """Get symbol trading information"""
        try:
            exchange_info = self.client.futures_exchange_info()
            symbol_info = next((s for s in exchange_info['symbols'] if s['symbol'] == symbol), None)
            
            if not symbol_info:
                raise ValueError(f"Symbol {symbol} not found")
            
            return symbol_info
        except BinanceAPIException as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            raise
    
    async def get_current_price(self, symbol: str) -> float:
        """Get current price for symbol"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            raise
    
    async def get_historical_data(self, symbol: str, timeframe: str, limit: int = 500, start_time: Optional[str] = None) -> pd.DataFrame:
        """Get historical kline data"""
        try:
            # Convert timeframe to Binance format
            interval_map = {
                '1m': Client.KLINE_INTERVAL_1MINUTE,
                '5m': Client.KLINE_INTERVAL_5MINUTE,
                '15m': Client.KLINE_INTERVAL_15MINUTE,
                '30m': Client.KLINE_INTERVAL_30MINUTE,
                '1h': Client.KLINE_INTERVAL_1HOUR,
                '4h': Client.KLINE_INTERVAL_4HOUR,
                '1d': Client.KLINE_INTERVAL_1DAY,
            }
            
            interval = interval_map.get(timeframe, Client.KLINE_INTERVAL_15MINUTE)
            
            klines = self.client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                startTime=start_time
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            df.set_index('timestamp', inplace=True)
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except BinanceAPIException as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            raise
    
    async def place_order(self, symbol: str, side: str, quantity: float, 
                         order_type: str = 'MARKET', price: Optional[float] = None,
                         stop_price: Optional[float] = None, 
                         take_profit: Optional[float] = None) -> Dict:
        """Place a futures order"""
        
        # Check daily trading limits
        today = datetime.now().date()
        if self.last_trade_date != today:
            self.daily_trades = 0
            self.last_trade_date = today
        
        if self.daily_trades >= config.max_trades_per_day:
            raise Exception(f"Daily trading limit reached: {config.max_trades_per_day}")
        
        if self.paper_trading:
            return await self._place_paper_order(symbol, side, quantity, order_type, price, stop_price, take_profit)
        
        try:
            # Place the main order
            order_params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity,
            }
            
            if order_type == 'LIMIT' and price:
                order_params['price'] = price
                order_params['timeInForce'] = 'GTC'
            
            order = self.client.futures_create_order(**order_params)
            
            # Place stop loss and take profit orders if specified
            if order['status'] == 'FILLED' and (stop_price or take_profit):
                position_side = 'LONG' if side == 'BUY' else 'SHORT'
                
                if stop_price:
                    await self._place_stop_loss(symbol, quantity, stop_price, position_side)
                
                if take_profit:
                    await self._place_take_profit(symbol, quantity, take_profit, position_side)
            
            self.daily_trades += 1
            logger.info(f"Order placed: {order['orderId']} for {symbol}")
            return order
            
        except BinanceAPIException as e:
            logger.error(f"Error placing order for {symbol}: {e}")
            raise
    
    async def _place_paper_order(self, symbol: str, side: str, quantity: float,
                               order_type: str, price: Optional[float],
                               stop_price: Optional[float], take_profit: Optional[float]) -> Dict:
        """Simulate order placement for paper trading"""
        current_price = await self.get_current_price(symbol)
        fill_price = price if order_type == 'LIMIT' and price else current_price
        
        # Calculate order value
        order_value = fill_price * quantity
        
        # Check if sufficient balance
        if order_value > self.paper_balance:
            raise Exception("Insufficient balance for paper trade")
        
        # Create paper order
        order = {
            'orderId': f"paper_{datetime.now().timestamp()}",
            'symbol': symbol,
            'status': 'FILLED',
            'executedQty': quantity,
            'avgPrice': fill_price,
            'side': side,
            'type': order_type,
            'timeInForce': 'GTC' if order_type == 'LIMIT' else None
        }
        
        # Update paper position
        if symbol not in self.paper_positions:
            self.paper_positions[symbol] = {
                'symbol': symbol,
                'positionAmt': 0,
                'entryPrice': 0,
                'markPrice': current_price,
                'unrealizedProfit': 0,
                'margin': 0
            }
        
        position = self.paper_positions[symbol]
        
        if side == 'BUY':
            if position['positionAmt'] < 0:  # Closing short
                close_qty = min(quantity, abs(position['positionAmt']))
                position['positionAmt'] += close_qty
                quantity -= close_qty
            
            if quantity > 0:  # Opening long
                total_value = position['positionAmt'] * position['entryPrice'] + quantity * fill_price
                position['positionAmt'] += quantity
                position['entryPrice'] = total_value / position['positionAmt'] if position['positionAmt'] != 0 else fill_price
        
        else:  # SELL
            if position['positionAmt'] > 0:  # Closing long
                close_qty = min(quantity, position['positionAmt'])
                position['positionAmt'] -= close_qty
                quantity -= close_qty
            
            if quantity > 0:  # Opening short
                total_value = abs(position['positionAmt']) * position['entryPrice'] + quantity * fill_price
                position['positionAmt'] -= quantity
                position['entryPrice'] = total_value / abs(position['positionAmt']) if position['positionAmt'] != 0 else fill_price
        
        # Update margin and unrealized P&L
        position['margin'] = abs(position['positionAmt']) * position['entryPrice'] * 0.1  # 10x leverage
        position['markPrice'] = current_price
        
        if position['positionAmt'] != 0:
            if position['positionAmt'] > 0:  # Long position
                position['unrealizedProfit'] = position['positionAmt'] * (current_price - position['entryPrice'])
            else:  # Short position
                position['unrealizedProfit'] = abs(position['positionAmt']) * (position['entryPrice'] - current_price)
        else:
            position['unrealizedProfit'] = 0
        
        self.daily_trades += 1
        logger.info(f"Paper order placed: {order['orderId']} for {symbol}")
        return order
    
    async def _place_stop_loss(self, symbol: str, quantity: float, stop_price: float, position_side: str):
        """Place stop loss order"""
        try:
            side = 'SELL' if position_side == 'LONG' else 'BUY'
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP_MARKET',
                quantity=quantity,
                stopPrice=stop_price,
                timeInForce='GTC'
            )
            
            logger.info(f"Stop loss placed: {order['orderId']} at {stop_price}")
            return order
            
        except BinanceAPIException as e:
            logger.error(f"Error placing stop loss: {e}")
    
    async def _place_take_profit(self, symbol: str, quantity: float, take_profit_price: float, position_side: str):
        """Place take profit order"""
        try:
            side = 'SELL' if position_side == 'LONG' else 'BUY'
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='TAKE_PROFIT_MARKET',
                quantity=quantity,
                stopPrice=take_profit_price,
                timeInForce='GTC'
            )
            
            logger.info(f"Take profit placed: {order['orderId']} at {take_profit_price}")
            return order
            
        except BinanceAPIException as e:
            logger.error(f"Error placing take profit: {e}")
    
    async def get_position(self, symbol: str) -> Optional[Dict]:
        """Get current position for symbol"""
        if self.paper_trading:
            return self.paper_positions.get(symbol)
        
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            position = next((p for p in positions if float(p['positionAmt']) != 0), None)
            return position
        except BinanceAPIException as e:
            logger.error(f"Error getting position for {symbol}: {e}")
            return None
    
    async def close_position(self, symbol: str) -> Optional[Dict]:
        """Close all positions for symbol"""
        position = await self.get_position(symbol)
        
        if not position or float(position['positionAmt']) == 0:
            return None
        
        try:
            quantity = abs(float(position['positionAmt']))
            side = 'SELL' if float(position['positionAmt']) > 0 else 'BUY'
            
            order = await self.place_order(symbol, side, quantity, 'MARKET')
            logger.info(f"Position closed for {symbol}")
            return order
            
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {e}")
            raise
    
    async def get_open_orders(self, symbol: str) -> List[Dict]:
        """Get all open orders for symbol"""
        if self.paper_trading:
            return []  # Paper trading doesn't track open orders
        
        try:
            orders = self.client.futures_get_open_orders(symbol=symbol)
            return orders
        except BinanceAPIException as e:
            logger.error(f"Error getting open orders for {symbol}: {e}")
            return []
    
    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """Cancel an order"""
        if self.paper_trading:
            return {'orderId': order_id, 'status': 'CANCELED'}
        
        try:
            result = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            logger.info(f"Order cancelled: {order_id}")
            return result
        except BinanceAPIException as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            raise
    
    def calculate_position_size(self, symbol: str, risk_amount: float, entry_price: float, stop_loss_price: float) -> float:
        """Calculate position size based on risk management"""
        risk_per_unit = abs(entry_price - stop_loss_price)
        if risk_per_unit == 0:
            return 0
        
        position_size = risk_amount / risk_per_unit
        
        # Apply maximum position size limit
        max_size = config.max_position_size_usd / entry_price
        return min(position_size, max_size)
    
    async def get_trading_fees(self, symbol: str) -> Dict:
        """Get trading fees for symbol"""
        try:
            if self.paper_trading:
                return {'makerCommission': 0.02, 'takerCommission': 0.04}  # 0.02% maker, 0.04% taker
            
            account = self.client.futures_account()
            return {
                'makerCommission': float(account['feeTier']) * 0.01,  # Convert from basis points
                'takerCommission': float(account['feeTier']) * 0.01
            }
        except Exception as e:
            logger.error(f"Error getting trading fees: {e}")
            return {'makerCommission': 0.02, 'takerCommission': 0.04}
