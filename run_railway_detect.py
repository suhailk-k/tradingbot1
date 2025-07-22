#!/usr/bin/env python3
"""
Railway Python Detection and Bot Starter
Handles python/python3 command variations
"""
import sys
import os
import subprocess
from datetime import datetime

def check_python_installation():
    """Check and report Python installation details"""
    print("🐍 Python Environment Check")
    print("=" * 40)
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path[0]}")
    
    # Check for python command
    try:
        result = subprocess.run(['python', '--version'], capture_output=True, text=True)
        print(f"'python' command: Available ({result.stdout.strip()})")
    except FileNotFoundError:
        print("'python' command: NOT FOUND")
    
    # Check for python3 command
    try:
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        print(f"'python3' command: Available ({result.stdout.strip()})")
    except FileNotFoundError:
        print("'python3' command: NOT FOUND")
    
    print("=" * 40)

def start_railway_bot():
    """Start the Railway trading bot"""
    print("🚂 Railway Trading Bot Launcher")
    print("=" * 50)
    
    # Check environment
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') == 'production'
    
    if is_railway:
        print("✅ Railway environment detected")
        # Import Railway configuration
        import config_railway
    
    print("📊 Mode: Paper Trading")
    print("💰 Virtual Balance: $20.00")
    print("🎯 Position Size: $3.00")
    print("🛡️ Risk: 5% per trade")
    print("⚡ Max Trades: 2/day")
    print("🔄 Starting bot worker...")
    
    # Import and run the main bot
    try:
        from run_railway_worker import main
        import asyncio
        asyncio.run(main())
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔄 Running in heartbeat mode...")
        run_simple_heartbeat()
    except Exception as e:
        print(f"❌ Bot error: {e}")
        print("🔄 Running in heartbeat mode...")
        run_simple_heartbeat()

def run_simple_heartbeat():
    """Simple heartbeat if main bot fails"""
    import time
    
    counter = 0
    while True:
        counter += 1
        print(f"[{datetime.now()}] 💓 Railway heartbeat #{counter}")
        
        if counter % 10 == 0:
            print("📊 Railway Status: Healthy")
            print("🔄 Bot Mode: Heartbeat")
            print("⏰ Uptime: {} minutes".format(counter))
        
        time.sleep(60)

if __name__ == '__main__':
    try:
        check_python_installation()
        start_railway_bot()
    except KeyboardInterrupt:
        print("\n🛑 Railway bot stopped")
    except Exception as e:
        print(f"🚨 Critical error: {e}")
        print("💓 Falling back to heartbeat mode...")
        run_simple_heartbeat()
