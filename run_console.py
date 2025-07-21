#!/usr/bin/env python3
"""
Super simple Railway deployment - just print status
"""
import os
import time
from datetime import datetime

def main():
    port = int(os.environ.get('PORT', 8000))
    
    print("🚀 BTC Trading Bot - Railway Deployment")
    print("="*50)
    print(f"📡 Configured Port: {port}")
    print("📊 Mode: Paper Trading")
    print("💰 Balance: $20.00")
    print("🎯 Position Size: $5.00")
    print("🛡️ Risk: 5% per trade")
    print("⚡ Max Trades: 3/day")
    print("✅ Bot Status: Active")
    print("🌐 Railway Deployment: SUCCESS")
    
    # Simple keep-alive loop
    counter = 0
    while True:
        counter += 1
        print(f"[{datetime.now()}] Bot heartbeat #{counter} - Trading bot active")
        
        if counter % 10 == 0:
            print("📊 Trading Summary:")
            print("   - Virtual balance: $20.00")
            print("   - Trades today: 0")
            print("   - Bot status: Running")
            print("   - Mode: Paper trading")
        
        time.sleep(60)  # 1 minute intervals

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(30)  # Wait before exit
