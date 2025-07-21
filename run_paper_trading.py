#!/usr/bin/env python3
"""
Paper Trading Runner
Runs the trading bot in paper trading mode for risk-free testing.
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.trading_bot import TradingBot

async def run_paper_trading():
    """Run the strategy in paper trading mode"""
    print("📝 PAPER TRADING MODE")
    print("💡 NO REAL MONEY AT RISK")
    print("="*60)
    
    # Initialize trading bot in paper mode
    print("🚀 Initializing paper trading bot...")
    bot = TradingBot(paper_trading=True)
    
    print("📊 Paper Trading Mode: ON")
    print("💰 Virtual Balance: $10,000")
    print("🎯 Target Win Rate: 60%+")
    print("⚡ Max Trades/Day: 3")
    print("🛡️ Risk per Trade: 1.5%")
    print("📈 Strategy: EMA + ADX + RSI + AI Analysis")
    print("🔄 Testing Environment: Safe")
    
    try:
        # Start the trading bot
        await bot.start()
    except KeyboardInterrupt:
        print("\n🛑 Paper trading stopped by user")
        await bot.stop()
    except Exception as e:
        print(f"❌ Error in paper trading: {e}")
        await bot.stop()
        raise

if __name__ == "__main__":
    asyncio.run(run_paper_trading())
