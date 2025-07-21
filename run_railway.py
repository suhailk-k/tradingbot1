"""
Railway.app optimized trading bot runner
"""
import os
import sys
import threading
import time
from datetime import datetime
from flask import Flask, jsonify

# Simple Flask app for Railway health checks
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "healthy",
        "service": "BTC Trading Bot",
        "mode": "paper_trading",
        "balance": "$20.00",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "trading-bot"
    })

@app.route('/status')
def status():
    return jsonify({
        "bot_status": "running",
        "trading_mode": "paper",
        "symbol": "BTCUSDT",
        "position_size": "$5",
        "balance": "$20.00"
    })

def start_simple_bot():
    """Simple bot simulation for Railway"""
    print("🚀 Railway Trading Bot Starting...")
    print("="*50)
    print("✅ Railway Deployment Active")
    print("📊 Paper Trading Mode: ON")
    print("💰 Virtual Balance: $20.00")
    print("🎯 Position Size: $5.00")
    print("🛡️ Risk per Trade: 5%")
    print("⚡ Max Trades/Day: 3")
    print("🌐 Health endpoint: / and /health")
    
    # Keep the bot alive with periodic status updates
    while True:
        try:
            print(f"[{datetime.now()}] Bot heartbeat - Railway deployment active")
            time.sleep(300)  # 5 minutes
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(60)

def main():
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_simple_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask app
    port = int(os.environ.get("PORT", 8000))
    print(f"🌐 Starting web server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
