#!/usr/bin/env python3
"""
Test script to validate the trading bot setup and functionality
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        from config import config, strategy_config
        print("✅ Config imported")
        
        from models import Trade, Signal, Portfolio, TradingMode, TradeType
        print("✅ Models imported")
        
        from database import db_manager
        print("✅ Database manager imported")
        
        from strategy import TradingStrategy
        print("✅ Trading strategy imported")
        
        from binance_interface import BinanceInterface
        print("✅ Binance interface imported")
        
        from ai_analysis import GeminiAI
        print("✅ AI analysis imported")
        
        from backtest import BacktestEngine
        print("✅ Backtest engine imported")
        
        from trading_bot import TradingBot
        print("✅ Trading bot imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🗄️ Testing database...")
    
    try:
        from database import db_manager
        from models import TradingMode
        
        # Test portfolio creation/update
        portfolio_data = {
            'total_balance': 10000.0,
            'available_balance': 9500.0,
            'total_pnl': 150.0,
            'win_rate': 65.0,
            'total_trades': 10
        }
        
        portfolio = db_manager.update_portfolio(TradingMode.PAPER, portfolio_data)
        print(f"✅ Portfolio updated: ID {portfolio.id}")
        
        # Test portfolio retrieval
        retrieved_portfolio = db_manager.get_portfolio(TradingMode.PAPER)
        if retrieved_portfolio:
            print(f"✅ Portfolio retrieved: Balance ${retrieved_portfolio.total_balance}")
        
        # Test trading stats
        stats = db_manager.get_trading_stats(TradingMode.PAPER)
        print(f"✅ Trading stats retrieved: {stats['total_trades']} trades")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_strategy():
    """Test trading strategy"""
    print("\n📊 Testing trading strategy...")
    
    try:
        import pandas as pd
        import numpy as np
        from strategy import TradingStrategy
        
        strategy = TradingStrategy()
        
        # Create sample data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='15T')
        np.random.seed(42)
        
        # Generate realistic price data
        price_changes = np.random.normal(0, 0.01, 100)
        prices = 50000 * np.exp(np.cumsum(price_changes))
        
        sample_data = pd.DataFrame({
            'open': prices * 0.999,
            'high': prices * 1.001,
            'low': prices * 0.998,
            'close': prices,
            'volume': np.random.uniform(1000, 10000, 100)
        }, index=dates)
        
        # Test indicator calculation
        data_with_indicators = strategy.calculate_indicators(sample_data)
        print(f"✅ Indicators calculated: {len(data_with_indicators.columns)} columns")
        
        # Test signal generation
        signal = strategy.generate_signal(data_with_indicators)
        print(f"✅ Signal generated: {signal['signal']} (strength: {signal['strength']:.1f}%)")
        
        # Test signal validation
        is_valid = strategy.validate_signal(signal, prices[-1])
        print(f"✅ Signal validation: {'Valid' if is_valid else 'Invalid'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Strategy error: {e}")
        return False

def test_configuration():
    """Test configuration settings"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from config import config, strategy_config
        
        # Test basic config access
        print(f"✅ Default symbol: {config.default_symbol}")
        print(f"✅ Position size: ${config.position_size_usd}")
        print(f"✅ Risk per trade: {config.risk_per_trade_percent}%")
        
        # Test strategy config
        print(f"✅ EMA fast: {strategy_config.EMA_FAST}")
        print(f"✅ ADX threshold: {strategy_config.ADX_THRESHOLD}")
        print(f"✅ RSI period: {strategy_config.RSI_PERIOD}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_paper_trading_bot():
    """Test paper trading bot initialization"""
    print("\n🤖 Testing trading bot (paper mode)...")
    
    try:
        from trading_bot import TradingBot
        
        # Initialize bot in paper trading mode
        bot = TradingBot(paper_trading=True)
        print("✅ Paper trading bot initialized")
        
        # Test basic properties
        print(f"✅ Symbol: {bot.symbol}")
        print(f"✅ Trading mode: {bot.trading_mode.value}")
        print(f"✅ Paper trading: {bot.paper_trading}")
        
        # Note: We don't start the bot to avoid API calls during testing
        
        return True
        
    except Exception as e:
        print(f"❌ Trading bot error: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("\n🌍 Testing environment...")
    
    # Check for required files
    required_files = [
        '.env.example',
        'requirements.txt',
        'README.md'
    ]
    
    required_dirs = [
        'src',
        'logs',
        'data',
        'backtest_results'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/ exists")
        else:
            print(f"❌ {directory}/ missing")
            return False
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found (copy from .env.example)")
    
    return True

async def main():
    """Run all tests"""
    print("🧪 Trading Bot Test Suite")
    print("="*50)
    
    tests = [
        ("Environment Setup", test_environment),
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("Strategy", test_strategy),
        ("Paper Trading Bot", test_paper_trading_bot)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                
        except Exception as e:
            print(f"❌ {test_name} FAILED: {e}")
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your trading bot is ready to use.")
        print("\n📝 Next steps:")
        print("1. Configure your .env file with API keys")
        print("2. Run paper trading: python run_paper_trading.py")
        print("3. Run backtests: python run_backtest.py")
        print("4. Launch dashboard: python run_dashboard.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("Make sure you've run 'python setup.py' first.")

if __name__ == "__main__":
    asyncio.run(main())
