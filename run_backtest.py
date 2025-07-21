#!/usr/bin/env python3
"""
Backtesting Runner
Runs historical backtests to validate the trading strategy.
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.backtest import BacktestEngine
from src.config import config

async def run_backtest():
    """Run comprehensive backtesting"""
    print("🔄 BACKTESTING MODE")
    print("📊 HISTORICAL DATA ANALYSIS")
    print("="*60)
    
    # Get user preferences
    print("\n📋 Backtest Configuration")
    
    # Symbol selection
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT']
    print(f"Available symbols: {', '.join(symbols)}")
    symbol = input(f"Enter symbol (default: BTCUSDT): ").strip().upper()
    if not symbol:
        symbol = 'BTCUSDT'
    
    # Date range
    default_start = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    default_end = datetime.now().strftime('%Y-%m-%d')
    
    start_date = input(f"Start date (YYYY-MM-DD, default: {default_start}): ").strip()
    if not start_date:
        start_date = default_start
    
    end_date = input(f"End date (YYYY-MM-DD, default: {default_end}): ").strip()
    if not end_date:
        end_date = default_end
    
    # Timeframe
    timeframes = ['15m', '1h', '4h', '1d']
    print(f"Available timeframes: {', '.join(timeframes)}")
    timeframe = input(f"Timeframe (default: 15m): ").strip()
    if not timeframe:
        timeframe = '15m'
    
    # Initial balance
    try:
        initial_balance = float(input("Initial balance (default: 10000): ") or "10000")
    except ValueError:
        initial_balance = 10000.0
    
    print(f"\n🎯 Backtest Parameters:")
    print(f"Symbol: {symbol}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Timeframe: {timeframe}")
    print(f"Initial Balance: ${initial_balance:,.2f}")
    
    confirmation = input("\nProceed with backtest? (y/N): ").strip().lower()
    if confirmation != 'y':
        print("❌ Backtest cancelled")
        return
    
    # Initialize backtest engine
    print("\n🚀 Initializing backtest engine...")
    engine = BacktestEngine(initial_balance=initial_balance)
    
    try:
        # Run backtest
        print("⏳ Running backtest... (this may take a few minutes)")
        results = await engine.run_backtest(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe=timeframe
        )
        
        # Display results
        print("\n" + "="*80)
        print("📊 BACKTEST RESULTS")
        print("="*80)
        
        report = engine.generate_backtest_report(results)
        print(report)
        
        # Ask if user wants to save results
        save_results = input("\nSave results to file? (y/N): ").strip().lower()
        if save_results == 'y':
            filename = f"backtest_{symbol}_{start_date}_{end_date}_{timeframe}.txt"
            filepath = os.path.join('backtest_results', filename)
            
            # Create directory if it doesn't exist
            os.makedirs('backtest_results', exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write(f"Backtest Results - {datetime.now()}\n")
                f.write("="*80 + "\n")
                f.write(f"Symbol: {symbol}\n")
                f.write(f"Period: {start_date} to {end_date}\n")
                f.write(f"Timeframe: {timeframe}\n")
                f.write(f"Initial Balance: ${initial_balance:,.2f}\n\n")
                f.write(report)
                f.write("\n\nDetailed Trade Results:\n")
                f.write("-"*40 + "\n")
                
                for i, trade in enumerate(results['trades_detail'], 1):
                    f.write(f"\nTrade {i}:\n")
                    f.write(f"  Type: {trade['type']}\n")
                    f.write(f"  Entry: ${trade['entry_price']:.2f}\n")
                    f.write(f"  Exit: ${trade['exit_price']:.2f}\n")
                    f.write(f"  P&L: ${trade['pnl']:.2f} ({trade['pnl_percent']:.2f}%)\n")
                    f.write(f"  Duration: {trade['duration']}\n")
                    f.write(f"  Exit Reason: {trade['exit_reason']}\n")
            
            print(f"✅ Results saved to: {filepath}")
        
        # Performance summary
        performance = results['performance']
        print(f"\n📈 PERFORMANCE SUMMARY:")
        print(f"Total Return: {results['total_return']:.2f}%")
        print(f"Win Rate: {performance['win_rate']:.1f}%")
        print(f"Profit Factor: {performance['profit_factor']:.2f}")
        print(f"Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {performance['max_drawdown']:.2f}%")
        
        if performance['win_rate'] >= 55 and performance['profit_factor'] >= 1.2:
            print("\n✅ Strategy shows promising results!")
            print("Consider running paper trading to validate in real-time conditions.")
        else:
            print("\n⚠️ Strategy may need optimization.")
            print("Consider adjusting parameters or testing different timeframes.")
        
    except Exception as e:
        print(f"❌ Error during backtest: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_backtest())
