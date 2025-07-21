#!/usr/bin/env python3
"""
Live Trading Runner
Runs the trading bot with real money - USE WITH EXTREME CAUTION!
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

async def run_live_trading():
    """Run the strategy in live trading mode"""
    print("🚨 LIVE TRADING MODE")
    print("⚠️  REAL MONEY AT RISK ⚠️")
    print("="*60)
    
    # Safety confirmation
    confirmation = input("Type 'START_LIVE_TRADING' to confirm: ")
    if confirmation != "START_LIVE_TRADING":
        print("❌ Live trading cancelled for safety")
        return
    
    # Additional safety check
    print("\n⚠️  FINAL WARNING ⚠️")
    print("This will trade with REAL MONEY on Binance")
    print("Make sure you have:")
    print("✅ Tested the strategy in paper trading")
    print("✅ Set appropriate position sizes")
    print("✅ Configured risk management")
    print("✅ Set up proper API keys")
    
    final_confirmation = input("\nType 'I_UNDERSTAND_THE_RISKS' to proceed: ")
    if final_confirmation != "I_UNDERSTAND_THE_RISKS":
        print("❌ Live trading cancelled for safety")
        return
    
    # Initialize trading bot in live mode
    print("\n🚀 Initializing live trading bot...")
    bot = TradingBot(paper_trading=False)
    
    print("📊 Live Trading Mode: ON")
    print("💰 Using REAL Binance Account")
    print("🎯 Target Win Rate: 60%+")
    print("⚡ Max Trades/Day: 3")
    print("🛡️ Risk per Trade: 1.5%")
    print("📈 Strategy: EMA + ADX + RSI + AI Analysis")
    
    try:
        # Start the trading bot
        await bot.start()
    except KeyboardInterrupt:
        print("\n🛑 Live trading stopped by user")
        await bot.stop()
    except Exception as e:
        print(f"❌ Error in live trading: {e}")
        await bot.stop()
        raise

if __name__ == "__main__":
    # Additional environment checks
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found")
        print("Please copy .env.example to .env and configure your API keys")
        sys.exit(1)
    
    # Check if this is being run accidentally
    if len(sys.argv) < 2 or sys.argv[1] != '--confirmed':
        print("⚠️  This script runs LIVE trading with REAL money!")
        print("If you're sure you want to proceed, run:")
        print(f"python {sys.argv[0]} --confirmed")
        sys.exit(1)
    
    asyncio.run(run_live_trading())
