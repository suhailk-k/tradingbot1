"""
Railway.app optimized trading bot runner
"""
import asyncio
import sys
import os
import signal
import threading
import time
from datetime import datetime
from flask import Flask, jsonify

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from trading_bot import TradingBot

# Create Flask app for health checks (Railway requirement)
app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "trading-bot"
    })

@app.route('/')
def index():
    return jsonify({
        "service": "BTC Trading Bot",
        "status": "running",
        "mode": "paper_trading",
        "balance": "$20.00",
        "description": "AI-powered BTC/USDT futures trading bot"
    })

class RailwayTradingBot:
    def __init__(self):
        self.bot = None
        self.running = False
        
    async def start_bot(self):
        """Start the trading bot"""
        print("🚀 Railway Trading Bot Starting...")
        print("="*50)
        
        # Initialize in paper trading mode for safety
        self.bot = TradingBot(paper_trading=True)
        self.running = True
        
        print("✅ Railway Deployment Active")
        print("📊 Paper Trading Mode: ON")
        print("💰 Virtual Balance: $20.00")
        print("🎯 Position Size: $5.00")
        print("🛡️ Risk per Trade: 5%")
        print("⚡ Max Trades/Day: 3")
        print("🌐 Health endpoint: /health")
        
        try:
            await self.bot.start()
        except Exception as e:
            print(f"❌ Bot error: {e}")
            self.running = False
            if self.bot:
                await self.bot.stop()
    
    def start_health_server(self):
        """Start Flask health check server"""
        port = int(os.environ.get("PORT", 8000))
        app.run(host="0.0.0.0", port=port, debug=False)

def signal_handler(signum, frame):
    print("\n🛑 Shutting down gracefully...")
    os._exit(0)

async def main():
    # Handle graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create bot instance
    railway_bot = RailwayTradingBot()
    
    # Start health check server in background thread
    health_thread = threading.Thread(
        target=railway_bot.start_health_server,
        daemon=True
    )
    health_thread.start()
    
    # Start the trading bot
    await railway_bot.start_bot()

if __name__ == "__main__":
    asyncio.run(main())
